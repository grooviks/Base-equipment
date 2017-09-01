#from flask_wtf import FlaskForm
from flask_wtf import Form
#import FlaskForm
from wtforms import StringField, BooleanField, SelectField, TextAreaField, IntegerField, FileField
from wtforms.validators import DataRequired, optional, length, NumberRange
from wtforms.widgets import TextArea, Input

masks_list = [
#('255.0.0.0/8', '8'), 
#('255.128.0.0 /9','9'),
#('255.192.0.0 /10', '10'),
#('255.224.0.0 /11','11'),
#('255.240.0.0 /12','12'),
#('255.248.0.0 /13','13'),
#('255.252.0.0 /14','14'),
#('255.254.0.0 /15', '15'),
#('255.255.0.0 /16', '16'),
#('255.255.128.0 /17','17'),
#('255.255.192.0 /18', '18'),
#('255.255.224.0 /19', '19'),
#('255.255.240.0 /20', '20'),
#('255.255.248.0 /21', '21'),
#('255.255.252.0 /22', '22'),
('23', '255.255.254.0 /23'),
('24', '255.255.255.0 /24',),
('25', '255.255.255.128 /25'),
('26', '255.255.255.192 /26'),
('27', '255.255.255.224 /27'),
('28', '255.255.255.240 /28'),
('29', '255.255.255.248 /29'),
('30', '255.255.255.252 /30'),
('31', '255.255.255.254 /31')]

types_spares_list = [
('keyboards', 'Keyboards'),
('mouses', 'Mouses'),
('unknown', 'Unknown'),
('audio','Audio'),
('camers','Cameras')
('switches', 'Switches')
('others', 'Others')
]

types_equip_list = [
('routers', 'Router'),
('pc', 'PC'),
('nettop','Nettop'),
('server', 'Server'),
('ipcam', 'IP Camera')
]

class AddSpareForm(Form):
    # Required — это валидатор, функция, которая может быть прикреплена к полю,
    # для выполнения валидации данных отправленных пользователем.
    # Валидатор Required просто проверяет, что поле не было отправлено пустым.
    #NumberRange(min=0) - минимальное значение поля 0
    #validators=[optional(), length(max=600)] - количество символов 600

    name = StringField('name', validators= [DataRequired()])
    type = SelectField(choices = types_list)
    #ограничим длинну
    comment = StringField('comment', widget=TextArea(), validators=[optional(), length(max=600)])
    count = IntegerField('count', widget=Input(input_type='number'), validators=[NumberRange(min=0, message='Только положительные числа'),DataRequired() ])
    location = StringField('location', validators= [DataRequired()])
    image = FileField('image_file')
    barcode = IntegerField('barcode') 



class SearchForm(Form):
    search = StringField('search', validators = [DataRequired()])


class AddNetworkForm(Form):
    name = StringField('name', validators= [DataRequired()])
    mask = SelectField(choices=masks_list)
    #ограничим длинну
    description = StringField('description', widget=TextArea(), validators=[optional(), length(max=600)])
    net = StringField('net', validators= [DataRequired()])

class AddDevicesForm(Form):
    name = StringField('name', validators= [DataRequired()])
    mask = SelectField(choices=masks_list)
    #ограничим длинну
    description = StringField('description', widget=TextArea(), validators=[optional(), length(max=600)])
    net = StringField('net', validators= [DataRequired()])
