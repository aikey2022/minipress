from exts import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(50), nullable=False,unique=True)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False,unique=True)
    phone = db.Column(db.String(11), nullable=False,unique=True)
    is_delete = db.Column(db.Boolean, default=False)
    is_root = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    allow_login = db.Column(db.Boolean, default=False)
    reg_time = db.Column(db.DateTime, default=datetime.now)
    active_time = db.Column(db.DateTime)
    login_time = db.Column(db.DateTime)
    
    def __str__(self):
        return self.username
    