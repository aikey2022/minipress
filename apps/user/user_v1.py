from flask import Blueprint,render_template,request,redirect,url_for,flash,session,g,jsonify
from exts import cache,csrf
from modules.user_module import User,UserForm



user_bp = Blueprint('user', __name__, url_prefix='/user')



@user_bp.route('/')
def user_index():
    return 'user_index'


@user_bp.route('/register', endpoint="register",methods=['GET', 'POST'])
def user_register():
    uform = UserForm()
    # 数据正确 并且验证csrf通过
    if uform.validate_on_submit():  
            print(request.form.get('username'))
            print(request.form.get('password'))
            return '数据提交成功'
        
    return render_template('user/register.html',form=uform)

