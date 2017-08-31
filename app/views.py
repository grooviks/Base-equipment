from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import AddSpareForm, SearchForm
from app.models import spares
from flask import jsonify
from werkzeug import secure_filename
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
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
        #загружаем изображение в директорию, если его хотели загрузить
        if form.image.data:
            print(type(form.image.data))
            print(upload_image(form.image.data, str(spare.id)))
        flash('Оборудование добавлено!!! ', 'success')
        return redirect(url_for('index'))
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
        else:
            flash('Ошибка редактирования!!! ', 'danger')
        return redirect(url_for('spare', id = spare.id))
    return render_template('spare.html',
                            spare = spare, 
                           form = form)

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
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_image(file,id):
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