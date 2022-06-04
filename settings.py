

class Config():
    ENV = 'development'
    DEBUG = 'True'
    SECRET_KEY = 'lksjhdjhaklioiqwuyeyQWAFDAFAYAGFH2232354fdaopweoierutngnbchgs'
    
    # 禁用/开启表单的 CSRF 保护。默认是开启
    WTF_CSRF_ENABLED = True
    # 默认下启用 CSRF 检查针对所有的视图。 默认值是 True。
    WTF_CSRF_CHECK_DEFAULT = True
    # 一个随机字符串生成 CSRF 令牌。 默认同 SECRET_KEY 一样。
    WTF_CSRF_SECRET_KEY = 'pplldlkdljdjlwiAKQKFRLGFKGSDPFGK12133523565645445PDPFKAGMKHM<FKSKL'
    # CSRF 令牌过期时间。默认是 3600 秒
    # WTF_CSRF_TIME_LIMIT = 3600
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@10.0.0.101:3306/minipress?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    
    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = '10.0.0.101'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_PASSWORD = 'foobaa'
    
    
class Development(Config):
    ENV = 'development'
    DEBUG = 'True'
    

class Production(Config):
    ENV = 'production'
    DEBUG = 'False'