from flask import Flask
import settings
from apps.user.user_v1 import user_bp
from exts import db
from flask_wtf import CSRFProtect


# 创建全局csrf保护
csrf = CSRFProtect()

# 创建app
def create_app():
    # 创建app对象
    app = Flask(__name__, static_folder='../static',template_folder='../templates')
    
    # 引入配置
    app.config.from_object(settings.Development)
    
    # 初始化db
    db.init_app(app=app)
    
    # 初始化csrf保护
    csrf.init_app(app=app)
    
    # 注册蓝图
    app.register_blueprint(user_bp)
    
    return app