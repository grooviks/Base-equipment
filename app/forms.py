from flask_wtf import Form
from wtforms import StringField, BooleanField, SelectField, TextAreaField, IntegerField, FileField
from wtforms.validators import DataRequired, optional, length, NumberRange
from wtforms.widgets import TextArea, Input

class AddSpareForm(Form):
    # Required — это валидатор, функция, которая может быть прикреплена к полю,
    # для выполнения валидации данных отправленных пользователем.
    # Валидатор Required просто проверяет, что поле не было отправлено пустым.
    #NumberRange(min=0) - минимальное значение поля 0
    #validators=[optional(), length(max=600)] - количество символов 600

    name = StringField('name', validators= [DataRequired()])
    type = SelectField(choices=[('keyboard', 'Keyboard'), ('mouse', 'Mouse'), ('understand', 'Understand') ])
    #ограничим длинну
    comment = StringField('comment', widget=TextArea(), validators=[optional(), length(max=600)])
    count = IntegerField('count', widget=Input(input_type='number'), validators=[NumberRange(min=0, message='Только положительные числа'),DataRequired() ])
    location = StringField('location', validators= [DataRequired()])
    image = FileField('image_file')
    barcode = IntegerField('barcode') 



class SearchForm(Form):
    search = StringField('search', validators = [DataRequired()])

