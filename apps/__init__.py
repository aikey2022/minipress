from flask import Flask
import settings
from apps.user.user_v1 import user_bp


# 创建app
def create_app():
    # 创建app对象
    app = Flask(__name__, static_folder='../static',template_folder='../templates')
    
    # 引入配置
    app.config.from_object(settings.Development)
    
    # 注册蓝图
    app.register_blueprint(user_bp)
    
    return app