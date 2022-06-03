from flask import Blueprint
from modules.user_module import User



user_bp = Blueprint('user', __name__, url_prefix='/user')



@user_bp.route('/')
def user_index():
    return 'welcome to user index page'