from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import basedir

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import views, models

if __name__ == "__main__":
    app.run()
