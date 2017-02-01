import os
from flaskext.mysql import MySQL
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
# Случайный ключ, которые будет исползоваться для подписи
# данных, например cookies.
SECRET_KEY = 'YOUR_RANDOM_SECRET_KEY'

#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_DATABASE_URI = 'mysql://root:dthbabrfwbz2@localhost:3306/equipment'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

#парамерты для загрузки изображений
UPLOAD_FOLDER = os.path.join(basedir,'app/static/images')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'bmp'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

