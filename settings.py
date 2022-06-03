

class Config():
    ENV = 'development'
    DEBUG = 'True'
    SECRET_KEY = 'lksjhdjhaklioiqwuyeyQWAFDAFAYAGFH2232354fdaopweoierutngnbchgs'
    
    
class Development(Config):
    ENV = 'development'
    DEBUG = 'True'
    

class Production(Config):
    ENV = 'production'
    DEBUG = 'False'