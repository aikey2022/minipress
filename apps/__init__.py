from flask import Flask
import settings

from apps.user.user_v1 import user_bp
from apps.article.articl_v1 import article_bp
from apps.about.about_v1 import about_bp
from apps.photo.photo_v1 import photo_bp
from apps.msg_abort.msg_v1 import msg_abort_bp

from exts import db,cache,csrf
from modules.user_module import *
from modules.article_module import *
from modules.photo_module import *
from modules.msg_aboard_module import *
from modules.about_module import *



# 创建app
def create_app():
    # 创建app对象
    app = Flask(__name__, static_folder='../static',template_folder='../templates')
    
    # 引入配置
    app.config.from_object(settings.Development)
    # app.config.from_object(settings.Production)
    
    # 初始化db
    db.init_app(app=app)
    
    # 初始化cache
    cache.init_app(app=app)
    
    # 初始化csrf保护
    csrf.init_app(app=app)

    # 注册蓝图
    app.register_blueprint(user_bp)
    app.register_blueprint(article_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(photo_bp)
    app.register_blueprint(msg_abort_bp)
    
    return app