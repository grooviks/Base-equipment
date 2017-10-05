from flask import render_template, flash, redirect, url_for, request, json
from app import app, db, ipcalc, excel
from app.forms import AddSpareForm, SearchForm, AddNetworkForm, DeviceForm, ServerForm
from app.models import spares, networks, devices, users, company, servers
from flask import jsonify
from werkzeug import secure_filename
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER_IMG, UPLOAD_FOLDER_FILES
import os
from PIL import Image

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/add_spares', methods = ['GET', 'POST'])
def add_spares():
    form = AddSpareForm()
    if form.validate_on_submit():
        #spare_name = Spares.name.filter(form.name.data)
        spare = spares(name = form.name.data,
                       type = form.type.data,
                       comment = form.comment.data,
                       count = form.count.data,
                       location = form.location.data, 
                       barcode = form.barcode.data )
        db.session.add(spare)
        db.session.commit()
        #загружаем изображение в директорию, если его хотели добавить
        if form.image.data:
            print(type(form.image.data))
            print(upload_image(form.image.data, str(spare.id)))
        flash('Оборудование добавлено!!! ', 'success')
        return redirect(url_for('index'))
    elif request.method == 'POST':        
        flash('Не заполнены обязательные поля!!! ', 'warning')
    return render_template('add_spares.html',
                            form = form)

@app.route('/all_spares', methods = ['GET', 'POST'])
def all_spares():
    all_spares = spares.query.all()
    #получаем множество типов расходников, чтобы выводить их сортированными
    types = {spare.type for spare in all_spares}
    return render_template('all_spares.html',
                           spares = all_spares,
                           types = types)

@app.route('/spare/<id>', methods = ['GET', 'POST'])
def spare(id):
    spare = spares.query.filter_by(id = id).first()
    if spare == None:
        flash('Оборудование не найдено!', 'warning')
        return redirect(url_for('index'))
    form = AddSpareForm(obj=spare)
    if form.validate_on_submit():
        if (request.form['submit'] == 'Сохранить'):
            spare.name = form.name.data
            spare.type = form.type.data
            spare.comment = form.comment.data
            spare.count = form.count.data
            spare.location = form.location.data
            spare.barcode = form.barcode.data 
            if form.image.data:
                upload_image(form.image.data, str(spare.id))
            db.session.commit()
            flash('Изменения сохранены!!! ', 'success')
        elif (request.form['submit'] == 'Удалить'):
            db.session.delete(spare)
            db.session.commit()
            flash('Удалено!!! ', 'success')
            return redirect(url_for('all_spares'))
        else:
            flash('Ошибка редактирования!!! ', 'danger')
        return redirect(url_for('spare', id = spare.id))
    elif request.method == 'POST':        
        flash('Не заполнены обязательные поля!!! ', 'warning')
    return render_template('spare.html',
                            spare = spare, 
                           form = form);

@app.route('/autocomplete',methods=['GET', 'POST'])
def autocomplete():
    search = request.args.get('q')
    query = spares.query.filter(spares.name.like('%' + str(search) + '%'))
    results = [x.name for x in query.all()]
    return jsonify(matching_results=results)

#переделать в одну функцию с autocomple
@app.route('/autocomplete_users',methods=['GET', 'POST'])
def autocomplete_users():
    search = request.args.get('q')
    query = users.query.filter(users.lastname.like('%' + str(search) + '%')).all()
    results = ["{} {} {}".format(x.lastname, x.name, x.secondname) for x in query]
    return jsonify(matching_results=results)

#@app.route('/search',methods = ['GET', 'POST'])
def search(content):
    form = DeviceForm()
    #ПЕРЕПИСАТЬ! делаем запрос по каждому полю и добавляем в результирующий список
    results = devices.query.filter(devices.number.like('%' + str(content) + '%')).order_by("id").all()
    results.extend(devices.query.filter(devices.owner.like('%' + str(content) + '%')).order_by("id").all())
    results.extend(devices.query.filter(devices.description.like('%' + str(content) + '%')).order_by("id").all())
    #отбираем подсети только которые нашлись в поиске , чтобы вывод был красивым
    all_networks = {network for network in networks.query.all() for dev in results if dev.id_network == network.id}
    if len(results) == 0: 
        flash('Ничего не найдено', 'warning')
    return render_template('search_dev_result.html',
                    results = results,
                    form = form, 
                    networks = all_networks)

def allowed_file(filename):
    '''проверка имени и расширения файла'''
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_image(file,id):
    '''загрузка изображения, возвращает путь к файлу'''
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER_IMG,filename)
        file.save(filepath)
        im = Image.open(filepath)
        filepath = os.path.join(UPLOAD_FOLDER_IMG,'spares_img',id +'.jpeg')
        im.save(filepath)
        os.remove(os.path.join(UPLOAD_FOLDER_IMG,filename))
        return filepath
    return None

def add_ip_in_db(network): 
    ''' заполняем бд devices записями с IP новой подсети'''
    for ip in ipcalc.range_ip(network): 
        try: 
            if network.net_type: 
                device = servers(ip = ip,
                id_network = network.id)
                print(device.ip)
            else: 
                device = devices(ip = ip,
                id_network = network.id
                )
            db.session.add(device) 
        except: 
            return False
    try:
        db.session.commit() 
    except: 
        return False
    return True

def del_ip_in_db(network): 
    ''' удаляем из таблицы Devices или Servers записи приндлежащие подсети '''

    if network.net_type: 
        devices_list = servers.query.filter_by(networks = network).all()
    else:
        devices_list = devices.query.filter_by(networks = network).all()
    try: 
        for device in devices_list: 
            db.session.delete(device)
    except: 
        return False
    try:
        db.session.commit()
    except:
        return False
    return True

def del_network(id_network): 
    ''' удаляем из таблцы networks подсеть по id '''
    network = networks.query.filter_by(id = id_network).first()
    print(network.id)
    if del_ip_in_db(network): 
        db.session.delete(network)
        db.session.commit()
        return True
    return False

def create_network(network): 
    ''' создаем подсеть и генерируем список ip адресов '''
    #если вписали не начало подсети а какой-нить ip , то берем всё равно подсеть 
    network.net = network.network
    db.session.add(network) 
    db.session.commit() 
    if add_ip_in_db(network): 
        print('Подсеть создана')
        return True
    else:
        return False    



@app.route('/network_views/<types>', methods = ['GET', 'POST'])
def network_views(types):
    s_form = SearchForm()
    if types == 'servers': 
        all_networks = networks.query.filter_by(net_type = 1).all()
    elif types == 'objects':
        all_networks = networks.query.filter_by(net_type = 0).all()
    else: 
        all_networks = networks.query.all()
    if request.method == 'POST' :
        for key, val in request.form.items():
            if val == 'Удалить': 
                del_network(key)
                return redirect(url_for('network_views', types = types))
            #elif val == 'Редактировать':
            #    return redirect(url_for('network', id=key)) 
            elif key == 'search': 
                return search(s_form.search.data)
            else:
                flash('Неизвестный запрос', 'warning')
    return render_template('networks.html',
                           networks = all_networks, 
                           form = s_form)


@app.route('/add_network', methods = ['GET', 'POST'])
def add_network():
    form = AddNetworkForm()
    if form.validate_on_submit():
        if ipcalc.check_ip(form.net.data): 
            netw = networks(name = form.name.data,
            description = form.description.data,
            cidr = form.cidr.data,
            net = form.net.data, 
            net_type = form.select_types.data)
            if create_network(netw): 
                flash('Подсеть добавлена!!! ', 'success')
                return redirect(url_for('network_views', types = 'all'))
            else: 
                flash('Таблица IP адресов не создана!! ', 'danger')
                 
        else: 
            flash('Введен некоректный адрес подсети!!! ', 'warning')
    elif request.method == 'POST':        
        flash('Не заполнены обязательные поля!!! ', 'warning')
    return render_template('add_network.html',
                            form = form)


@app.route('/network/<id>', methods = ['GET', 'POST'])
def network(id):
    network = networks.query.filter_by(id = id).first()
    if network.net_type: 
        servers_list = servers.query.filter_by(id_network = id).all()
        form = ServerForm()
        return render_template('servers.html',
                            network = network, 
                            servers = servers_list,
                            form = form
                            )
    else : 
        form = DeviceForm()
        devices_list = devices.query.filter_by(id_network = id).all()
        return render_template('network.html',
                            network = network, 
                            devices = devices_list,
                            form = form
                            )


@app.route('/all_company', methods = ['GET', 'POST'])
def all_company():
    comps_list = company.query.all()
    users_list = users.query.all()
    return render_template('all_company.html',
                            comps = comps_list, 
                            users = users_list
                           )


@app.route('/company/<id>', methods = ['GET', 'POST'])
def t_company(id):
    #form = DeviceForm()
    comp = company.query.filter_by(id = id).first()
    users_list = users.query.filter_by(id_company = id).all()
    return render_template('company.html',
                            comp = comp, 
                            users = users_list
                            )

@app.route('/edit_device', methods = ['GET', 'POST'])
def edit_device():
    ''' получает POST запросом id оборудования в БД , меняемое свойство и значение его 
        проверяет изменилось ли оно , если да то записываем в БД '''
 
    dev_id = request.form['id'][4:]
    dev_property = request.form['name']
    value = request.form['value']

    #каждый раз при запросе лазить в БД чтобы определить тип сети не комильфо, надо переделать
    if networks.query.filter_by(id = request.referrer.split('/')[-1]).first().net_type : 
        device = servers.query.filter_by(id = dev_id).first()
    else: 
        device = devices.query.filter_by(id = dev_id).first()
    if getattr(device, dev_property) != value:
        setattr(device, dev_property, value)
        db.session.commit()
        return json.dumps({'resp' : 'change ok'})
    return json.dumps({'resp': 'not change'})

@app.route('/excel_import', methods = ['GET', 'POST'])
def excel_import():
    file_path = os.path.join(UPLOAD_FOLDER_FILES,'seti.xlsx')
    if excel.excel_parcing(file_path): 
        return redirect(url_for('all_networks'))
    else: 
        return render_template('import_excel.html')

@app.context_processor
def company_list(): 
    '''Список компаний в которых больше 3х человек для отображения в меню'''
    return {"company_list":[comp for comp in company.query.all() \
        if len(users.query.filter_by(company = comp).all()) > 3 \
        and comp.name is not None ]}

@app.route('/network_on_type/<types>', methods = ['GET', 'POST'])
def network_on_type(types):
    s_form = SearchForm()
   


