from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_wtf import CSRFProtect

# 创建全局csrf保护
csrf = CSRFProtect()

db = SQLAlchemy()

cache = Cache()