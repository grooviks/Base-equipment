from app import db
import json, os 
from config import UPLOAD_FOLDER
#from sqlalchemy.dialects.mysql import INTEGER

def to_json(inst, cls):
    """
    Jsonify the sql alchemy query result.
    """
    convert = dict()
    # add your coversions for things like datetime's
    # and what-not that aren't serializable.
    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.type in convert.keys() and v is not None:
            try:
                d[c.name] = convert[c.type](v)
            except:
                d[c.name] = "Error:  Failed to covert using ", str(convert[c.type])
        elif v is None:
            d[c.name] = str()
        else:
            d[c.name] = v
    return json.dumps(d)

class spares(db.Model):
    '''  migrate.versioning api не поддерживает sqlalchemy.dialects.mysql'''
    __tablename__ = 'spares'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.VARCHAR(300))
    type = db.Column(db.VARCHAR(200))
    comment = db.Column(db.TEXT)
    count = db.Column(db.INTEGER)
    location = db.Column(db.VARCHAR(300))
    barcode = db.Column(db.INTEGER)

    def __repr__(self):
        return self.name
    #добавил для вывода в JSON но не уверен что это понадобится, так как были косяки с ним при возврате в jquery
    @property
    def json(self):
        return to_json(self, self.__class__)

    @property
    def img(self): 
        imgname = str(self.id) + '.jpeg' 
        return os.path.join('images/spares_img',imgname) \
        if os.path.exists(os.path.join(UPLOAD_FOLDER,'spares_img', imgname)) else 'images/no_img.jpg'


class devices(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.INTEGER, primary_key=True)
    description = db.Column(db.VARCHAR(300))
    type = db.Column(db.VARCHAR(200))
    comment = db.Column(db.TEXT)
    number = db.Column(db.INTEGER)
    owner = db.Column(db.VARCHAR(300))
    ip = db.Column(db.VARCHAR(300))
    id_network =  db.Column(db.Integer, db.ForeignKey('networks.id'))



class networks(db.Model):
    __tablename__ = 'networks'
    id = db.Column(db.INTEGER, primary_key=True)
    description = db.Column(db.VARCHAR(300))
    name = db.Column(db.VARCHAR(300))
    mask = db.Column(db.INTEGER)
    devices = db.relationship('devices', backref = 'networks', lazy = 'dynamic')

        
            
        
        



