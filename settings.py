

class Config():
    ENV = 'development'
    DEBUG = 'True'
    SECRET_KEY = 'lksjhdjhaklioiqwuyeyQWAFDAFAYAGFH2232354fdaopweoierutngnbchgs'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@10.0.0.101:3306/minipress?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    
class Development(Config):
    ENV = 'development'
    DEBUG = 'True'
    

class Production(Config):
    ENV = 'production'
    DEBUG = 'False'