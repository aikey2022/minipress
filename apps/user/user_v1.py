from flask import Blueprint,render_template,request,redirect,url_for,flash,session,g,jsonify,make_response,abort
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from exts import db,cache,csrf
from exts.utils.valid_code import image_code
from modules.user_module import User,UserRegForm,UserLogForm,UserCenterForm
from modules.article_module import Article_Type
import os,time,io,settings
from sqlalchemy import and_
from apps.user.check_login import check_login_status
from exts.utils.logsout import CreateLogging


# 创建蓝图
user_bp = Blueprint('user', __name__, url_prefix='/user')
bp_logging = CreateLogging('user_v1','debug')

@user_bp.before_app_request
def before_user_bp_request():
    # 每个请求都要展示文章分类
    articl_type = Article_Type.query.all()
    g.types = articl_type
    uid = session.get('uid')
    if uid:
       g.user = User.query.filter(User.id == uid).first() 
       # print('-------------------------->>',g.user)
    



@user_bp.route('/',endpoint='index')
@check_login_status
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
    # 检查重复登录
    uid = session.get('uid')
    if uid and cache.get(str(uid)):
        flash('请勿重复注册',category='info')
        return render_template('user/info.html',user=g.user,types=g.types)

    uform = UserRegForm()
    # 数据正确 并且验证csrf通过
    if uform.validate_on_submit():  
        # 获取数据
        username= request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        phone = request.form.get('phone')
        bp_logging.logger.debug(f'username:{username},password:{password},email:{email},phone:{phone}')
        # print('info----------------->>>',username,password,email,phone)
            
        # 创建user对象
        user = User()
        user.username= username
        user.password= generate_password_hash(password=password)
        user.email= email
        user.phone= phone
        
        # 提交数据到数据库
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('user.register'))
    
    # 默认展示注册页面
    return render_template('user/register.html',form=uform,types=g.types)


@user_bp.route('/login', endpoint="login",methods=['GET', 'POST'])
def user_login():
    
    # 检查重复登录
    uid = session.get('uid')
    if uid and cache.get(str(uid)):
        flash('您已登录',category='info')
        return render_template('user/info.html',user=g.user,types=g.types)
    
    form = UserLogForm()
    if form.validate_on_submit():
        # 获取登陆信息
        username = request.form.get('username')
        password = request.form.get('password')
        
        # check_code = request.form.get('check_code')
        
        # 验证登陆信息
        user = User.query.filter(User.username==username).first()
        # 校验密码
        if user:
            check_pwd = check_password_hash(pwhash=user.password,password=password)
        else:
            check_pwd = False
            
        if user and  check_pwd:
            # 验证通过
            # 设置session
            session['uid'] = user.id
            # 设置缓存  uid=username
            cache.set(str(user.id),user.username,timeout=3600)
            g.user = user
            flash("登陆成功^_^", category="info")
            bp_logging.logger.debug('登陆成功')
            return redirect(url_for('user.index'))
        
        # 登录失败
        return render_template('user/login.html',form=form,types=g.types,error="用户名或者密码错误") 
    # 默认展示登陆页面    
    return render_template('user/login.html',form=form,types=g.types)


# 退出登录
@user_bp.route('/logout', endpoint="logout",methods=['GET', 'POST'])
def user_logout():
    # 删除缓存登陆状态 删除key--> uid=username
    cache.delete(str(session.get('uid')))
    # 删除session
    session.clear()
    return redirect(url_for('user.login'))


# 个人中心
@user_bp.route('/center', endpoint="center",methods=['GET', 'POST'])
@check_login_status
def user_center():
    form = UserCenterForm()
    user = g.user
    if form.validate_on_submit():
        if form.image.data:
            # 有图片上传
            filename = secure_filename(form.image.data.filename)
            suffix = filename.rsplit('.',1)[-1]

            # 生成时间戳
            now = time.time()
            # 生成新的图片名称---确保图片唯一
            new_image_name = f'{user.id}{user.username}{now}.{suffix}'
            
            # 保存新头像到本地
            form.image.data.save(settings.Development.ICON_DIR +"/"+ new_image_name)
            
            # 删除旧头像
            if user.icon:
                old_image_name = user.icon.rsplit('/',1)[-1]
                old_icon_path = os.path.join(settings.Development.ICON_DIR,old_image_name)
                if os.path.exists(old_icon_path):
                    try:
                        os.remove(old_icon_path)
                    except Exception as e:
                        print(e)
                    
            # 生成icon图片新的url---相对路径
            icon_url = os.path.join('upload/icon/', new_image_name.replace('\\','/'))
            user.icon = icon_url
        
        # 没有头像上传    
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
    
        # 提交数据库
        db.session.commit()
        flash("修改成功^_^", category="info")
        bp_logging.logger.debug('更新资料成功')
    # 默认返回个人中心页面
    return render_template('user/user_center.html',user=g.user,types=g.types,form=form)