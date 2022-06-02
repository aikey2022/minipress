

class Config():
    ENV = 'development'
    DEBUG = 'True'
    
    
class Development(Config):
    ENV = 'development'
    DEBUG = 'True'
    

class Production(Config):
    ENV = 'production'
    DEBUG = 'False'