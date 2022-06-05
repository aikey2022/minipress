from operator import and_
from flask import Blueprint,render_template,request,redirect,url_for,flash,session,g,jsonify,make_response,abort
from exts import db,cache,csrf
from exts.utils.valid_code import image_code
from modules.user_module import User,UserRegForm,UserLogForm
from modules.article_module import Article_Type
import time,io

# 创建蓝图
user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.before_app_request
def before_user_bp_request():
    # 每个请求都要展示文章分类
    articl_type = Article_Type.query.all()
    g.types = articl_type



@user_bp.route('/',endpoint='index')
def user_index():
    # 根据缓存查询用户登陆状态
    if cache.get(str(session.get('uid'))):
        g.user = User.query.filter(User.id == session.get('uid')).first()
        # 登陆状态
        if g.user:
            return render_template('user/index.html',types=g.types,user=g.user)
    
    # 非登陆状态
    return render_template('user/index.html',types=g.types)



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
    uform = UserRegForm()
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


@user_bp.route('/login', endpoint="login",methods=['GET', 'POST'])
def user_login():
    form = UserLogForm()
    if form.validate_on_submit():
        # 获取登陆信息
        username = request.form.get('username')
        password = request.form.get('password')
        # check_code = request.form.get('check_code')
        
        # 验证登陆信息
        user = User.query.filter(and_(User.username==username,User.password==password)).first()
        if user:
            # 验证通过
            # 设置session
            session['uid'] = user.id
            # 设置缓存  uid=username
            cache.set(str(user.id),user.username,timeout=3600)
            g.user = user
            flash("登陆成功^_^", category="info")
            return redirect(url_for('user.index'))
        
        # 登录失败
        return render_template('user/login.html',form=form,types=g.types,error="用户名或者密码错误") 
    # 默认展示登陆页面    
    return render_template('user/login.html',form=form)


# 退出登录
@user_bp.route('/logout', endpoint="logout",methods=['GET', 'POST'])
def user_logout():
    # 删除缓存登陆状态 删除key--> uid=username
    cache.delete(str(session.get('uid')))
    # 删除session
    session.clear()
    return redirect(url_for('user.login'))