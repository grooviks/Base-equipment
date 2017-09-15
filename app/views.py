from flask import render_template, flash, redirect, url_for, request, json
from app import app, db
from app.forms import AddSpareForm, SearchForm, AddNetworkForm, DeviceForm
from app.models import spares, networks, devices
from flask import jsonify
from werkzeug import secure_filename
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
import os
from PIL import Image
from app import ipcalc

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

#@app.route('/search',methods = ['GET', 'POST'])
#def search():
#    form = SearchForm(request.form)
#    return render_template('search.html',
#                    form=form)

def allowed_file(filename):
    '''проверка имени и расширения файла'''
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_image(file,id):
    '''загрузка изображения, возвращает путь к файлу'''
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER,filename)
        file.save(filepath)
        im = Image.open(filepath)
        filepath = os.path.join(UPLOAD_FOLDER,'spares_img',id +'.jpeg')
        im.save(filepath)
        os.remove(os.path.join(UPLOAD_FOLDER,filename))
        return filepath
    return None

def add_ip_in_db(network): 
    ''' заполняем бд devices записями с IP новой подсети'''
    for ip in ipcalc.range_ip(network): 
        try: 
            device = devices(description = None,
            type = None,
            comment = None,
            number = None, 
            owner = None,
            ip = ip,
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

        

def del_ip_in_db(id_network): 
    ''' удаляем из БД Devices записи приндлежащие подсети '''
    devices_list = devices.query.filter_by(id_network = id_network).all()
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
    ''' удаляем из БД networks подсеть по id '''
    network = networks.query.filter_by(id = id_network).first()
    if del_ip_in_db(id_network): 
        db.session.delete(network)
        db.session.commit()
        return True
    return False



@app.route('/all_networks', methods = ['GET', 'POST'])
def all_networks():
    all_networks = networks.query.all()
    if request.method == 'POST' :
        for key, val in request.form.items():
            if val == 'Удалить': 
                del_network(key)
                return redirect(url_for('all_networks'))
            #elif val == 'Редактировать':
            #    return redirect(url_for('network', id=key)) 
            else:
                flash('Неизвестный запрос', 'warning')
    return render_template('networks.html',
                           networks = all_networks)



@app.route('/add_network', methods = ['GET', 'POST'])
def add_network():
    form = AddNetworkForm()
    if form.validate_on_submit():
        #spare_name = Spares.name.filter(form.name.data)
        if ipcalc.check_ip(form.net.data): 
            netw = networks(name = form.name.data,
            description = form.description.data,
            cidr = form.cidr.data,
            net = form.net.data)
            #если вписали не начало подсети а какой-нить ip , то берем всё равно подсеть 
            netw.net = netw.network
            db.session.add(netw) 
            db.session.commit() 
            flash('Подсеть добавлена!!! ', 'success')
            if add_ip_in_db(netw): 
                return redirect(url_for('all_networks'))
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

    form = DeviceForm()
    network = networks.query.filter_by(id = id).first()
    devices_list = devices.query.filter_by(id_network = id).all()
    return render_template('network.html',
                            network = network, 
                            devices = devices_list,
                            form = form
                            )


@app.route('/edit_device', methods = ['GET', 'POST'])
def edit_device():
    ''' получает POST запросом id оборудования в БД , меняемое свойство и значение его 
        проверяет изменилось ли оно , если да то записываем в БД '''
    dev_id = request.form['id'][4:]
    dev_property = request.form['name']
    value = request.form['value']
    print(dev_id, dev_property, value)
    device = devices.query.filter_by(id = dev_id).first()
    if getattr(device, dev_property) != value:
        setattr(device, dev_property, value)
        db.session.commit()
        print(device.number)
        return json.dumps({'resp' : 'change ok'})
    print( device.type, device.owner)
    return json.dumps({'resp': 'not change'})