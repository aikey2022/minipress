from flask import Blueprint,render_template,request,redirect,url_for,flash,session,g,jsonify,make_response
from exts import db,cache,csrf
from exts.utils.valid_code import image_code
from modules.user_module import User,UserForm
import time,io

# 创建蓝图
user_bp = Blueprint('user', __name__, url_prefix='/user')



@user_bp.route('/')
def user_index():
    return 'user_index'


@user_bp.route('/imgcode',endpoint='imgcode')
def valid_code():
    # 生成验证码
    image,code = image_code()
    # 获取时间戳
    time_code = time.time()
    code_key = f'{time_code}_{code}'
    # 保存验证码redis键值到session
    session['code_key'] = code_key
    # 保存验证码到redis缓存
    cache.set(code_key,code,timeout=180)
    
    # 将验证码返回给前端
    # 创建一个缓冲区
    buffer = io.BytesIO()
    # 将图片保存在到缓冲区
    image.save(buffer,'jpeg')
    # 获取缓冲区的二进制图片
    b_img = buffer.getvalue()
    
    # 构建二进制图片的响应对象和响应头
    response = make_response(b_img)
    response.headers['Content-Type'] = 'image/jpeg'
    return  response


@user_bp.route('/register', endpoint="register",methods=['GET', 'POST'])
def user_register():
    uform = UserForm()
    # 数据正确 并且验证csrf通过
    if uform.validate_on_submit():  
        # 获取数据
        username= request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        phone = request.form.get('phone')
        # print('info----------------->>>',username,password,email,phone)
            
        # 创建user对象
        user = User()
        user.username= username
        user.password= password
        user.email= email
        user.phone= phone
        
        # 提交数据到数据库
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('user.register'))
    
    # 默认展示注册页面
    return render_template('user/register.html',form=uform)

