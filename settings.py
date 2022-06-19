import os


class Config():
    
    # 获取环境变量---启动容器时需传递环境变量
    MYSQL_HOST = os.environ.get('MYSQL_HOST',default='10.0.0.101')
    MYSQL_HOST_PORT = 3306
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD',default='123456')
    MYSQL_USER = os.getenv('MYSQL_USER',default='root')
    MYSQL_DBNAME = os.getenv('MYSQL_DBNAME',default='minipress')

    REDIS_HOST = os.getenv('REDIS_HOST',default='10.0.0.101')
    REDIS_HOST_PORT = 6379
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD',default='foobaa')
    
    
    ENV = 'development'
    DEBUG = 'True'
    SECRET_KEY = 'lksjhdjhaklioiqwuyeyQWAFDAFAYAGFH2232354fdaopweoierutngnbchgs'
    
    # 禁用/开启表单的 CSRF 保护。默认是开启
    WTF_CSRF_ENABLED = True
    # 默认下启用 CSRF 检查针对所有的视图。 默认值是 True。
    # WTF_CSRF_CHECK_DEFAULT = True
    # 一个随机字符串生成 CSRF 令牌。 默认同 SECRET_KEY 一样。
    WTF_CSRF_SECRET_KEY = 'pplldlkdljdjlwiAKQKFRLGFKGSDPFGK12133523565645445PDPFKAGMKHM<FKSKL'
    # CSRF 令牌过期时间。默认是 3600 秒
    # WTF_CSRF_TIME_LIMIT = 3600
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_HOST_PORT}/{MYSQL_DBNAME}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    
    # redis配置
    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = REDIS_HOST
    CACHE_REDIS_PORT = REDIS_HOST_PORT
    CACHE_REDIS_PASSWORD = REDIS_PASSWORD
    
    # 静态文件夹配置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join(BASE_DIR,'static')
    UPLOAD_DIR = os.path.join(STATIC_DIR,'upload')
    # 图标文件夹
    ICON_DIR = os.path.join(UPLOAD_DIR,'icon')
    # 相册文件夹
    PHOTO_DIR = os.path.join(UPLOAD_DIR,'photo')
    
    
    
class Development(Config):
    # 开发环境配置
    ENV = 'development'
    DEBUG = 'True'


class Production(Config):
    # 生产环境配置
    ENV = 'production'
    DEBUG = 'False'

    