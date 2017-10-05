from app import db
import json, os 
from app import ipcalc
from config import UPLOAD_FOLDER_IMG, UPLOAD_FOLDER_FILES
from app import constants as NET_TYPE
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
        if os.path.exists(os.path.join(UPLOAD_FOLDER_IMG,'spares_img', imgname)) else 'images/no_img.jpg'

class devices(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.INTEGER, primary_key=True)
    description = db.Column(db.VARCHAR(300))
    type = db.Column(db.VARCHAR(200))
    comment = db.Column(db.TEXT)
    number = db.Column(db.VARCHAR(30))
    owner = db.Column(db.VARCHAR(300))
    ip = db.Column(db.VARCHAR(300))
    id_network =  db.Column(db.Integer, db.ForeignKey('networks.id'))

    def __init__(self, ip, id_network, owner = None, description = None,
        comment = None,  number = None, type = None):
        self.ip = ip
        self.id_network = id_network
        self.owner = owner
        self.description = description
        self.comment = comment
        self.number = number
        self.type = type

class networks(db.Model):
    __tablename__ = 'networks'
    id = db.Column(db.INTEGER, primary_key=True)
    net = db.Column(db.VARCHAR(300))
    description = db.Column(db.VARCHAR(300))
    name = db.Column(db.VARCHAR(300))
    cidr = db.Column(db.INTEGER)
    devices = db.relationship('devices', backref = 'networks', lazy = 'dynamic')
    servers = db.relationship('servers', backref = 'networks', lazy = 'dynamic')
    net_type = db.Column(db.INTEGER, default = NET_TYPE.DEVICES)

    
    def __repr__(self):
        return self.name

    @property
    def hosts(self):
        return ipcalc.hosts(self)
    @property
    def mask(self): 
        return ".".join([str(octet) for octet in ipcalc.mask(self)])
    @property
    def first_addr(self):
        return ".".join([str(octet) for octet in ipcalc.first_addr(self)])
    @property
    def last_addr(self):
        return ".".join([str(octet) for octet in ipcalc.last_addr(self)])
    @property
    def network(self):
        return ".".join([str(octet) for octet in ipcalc.network(self)])
        

class users(db.Model):
    """docstring for  users"""
    __tablename__ = 'users'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.VARCHAR(200))
    lastname = db.Column(db.VARCHAR(200))
    secondname = db.Column(db.VARCHAR(200))
    notesname = db.Column(db.VARCHAR(50))
    mail = db.Column(db.VARCHAR(200))
    phone = db.Column(db.VARCHAR(100))
    mobile_phone = db.Column(db.VARCHAR(20))
    id_company = db.Column(db.INTEGER, db.ForeignKey('company.id'))
    post = db.Column(db.VARCHAR(200))
    hierarchy = db.Column(db.VARCHAR(300))
    samaccountname = db.Column(db.VARCHAR(50))
    work_object = db.Column(db.VARCHAR(300))
    uniq_code = db.Column(db.VARCHAR(200))
    dismiss = db.Column(db.Boolean, default=False, nullable=False)
    #equipments = db.relationship('equipments', backref = 'users', lazy = 'dynamic')

    def __repr__(self):
        return "{} {} {}".format(self.name, self.secondname, self.lastname)

class company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.VARCHAR(300))
    users = db.relationship('users', backref = 'company', lazy = 'dynamic')
    #equipments = db.relationship('equipments', backref = 'users', lazy = 'dynamic')

class servers(db.Model): 
    __tablename__ = 'servers'
    id = db.Column(db.INTEGER, primary_key=True)
    dnsname = db.Column(db.VARCHAR(300))
    ip = db.Column(db.VARCHAR(300))
    id_network =  db.Column(db.Integer, db.ForeignKey('networks.id'))
    vmhost = db.Column(db.VARCHAR(300))
    description = db.Column(db.VARCHAR(300))
    ssh_port = db.Column(db.VARCHAR(300))
    os = db.Column(db.VARCHAR(300))
    services = db.Column(db.VARCHAR(300))
    ipmi = db.Column(db.VARCHAR(300))
    ipmi_port = db.Column(db.VARCHAR(300))
    external_ip = db.Column(db.VARCHAR(300))


    def __init__(self,  ip, id_network,dnsname = None, os = None, services = None, vmhost = None, 
        description = None, ssh_port = None,  ipmi = None, ipmi_port = None, external_ip = None):
        self.dnsname = dnsname
        self.ip = ip
        self.id_network = id_network
        self.vmhost = vmhost
        self.description = description
        self.ssh_port = ssh_port
        self.os = os
        self.services = services
        self.ipmi = ipmi
        self.ipmi_port = ipmi_port
        self.external_ip = external_ip

    def __repr__(self):
        return "DNS name: {}".format(self.dnsname)

        






        
            
        
        



