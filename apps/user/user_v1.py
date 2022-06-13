from flask import Blueprint,render_template,request,redirect,url_for,flash,session,g,jsonify,make_response,abort
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from exts import db,cache,csrf
from exts.utils.valid_code import image_code
from modules.user_module import *
from modules.article_module import *
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

    # 管理员修改用户前置条件
    if request.path == url_for('user.update'):
        if request.method == 'POST':
            edit_id = request.form.get('hiddens',type=int)
        if request.method == 'GET':
            edit_id = request.form.get('uid',type=int)
        if edit_id:
            g.edituser = User.query.filter(User.id == edit_id).first()
            
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
   
    # 非登陆状态
    return redirect(url_for('article.articles'))



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
        flash('请勿重复注册',category='error')
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
        flash('注册成功', category='info')
        return redirect(url_for('user.register'))
    
    # 默认展示注册页面
    return render_template('user/register.html',form=uform,types=g.types)


@user_bp.route('/login', endpoint="login",methods=['GET', 'POST'])
def user_login():
    
    # 检查重复登录
    uid = session.get('uid')
    if uid and cache.get(str(uid)):
        flash('您已登录',category='error')
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
            cache.set(str(user.id),user.username,timeout=60*60*3)
            g.user = user
            flash("登陆成功^_^", category="info")
            bp_logging.logger.debug('登陆成功')
            return redirect(url_for('article.articles'))
        
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



# 用户管理中心
@user_bp.route('/admin', endpoint="admin",methods=['GET', 'POST'])
@check_login_status
def user_admin():
    uid = g.user.id
    user = User.query.filter(User.id==uid).first()
    if user.is_root == True or user.is_admin == True:
        # 获取当前分页数默认为1 类型为int
        # 当前页码
        current_page = request.args.get('page',1,type=int)
        # 每页条数
        per_page = 10

        # 获取pagination对象
        pagination = User.query.filter(User.is_delete == False).paginate(page=current_page,per_page=per_page)
        
        #========实现显示固定分页数====================

        # 1 需要显示的固定页数长度
        page_control = 5
        
        # 2 计算当前页到尾页的长度
        page_len = pagination.pages - pagination.page
        
        # 3 比较当前页到尾页的长度与设定的长度
        if pagination.pages<page_control:
            # 3.1 总页数小于固定页数长度
            middle_page = range(1,pagination.pages+1)
        elif page_len < page_control<= pagination.pages:
            # 3.2 当前页到尾页全部显示
            middle_page = range(pagination.pages-page_control+1,pagination.pages+1)
        else:
            # 3.3 当前页到设置的长度
            middle_page = range(pagination.page,pagination.page+page_control)

        return render_template('user/admin_user.html',user=g.user,types=g.types,pagination=pagination,middle_page=middle_page)
    
    flash('没有管理权限',category='error')
    return render_template('user/info.html',user=g.user,types=g.types)



# 新增用户
@user_bp.route('/add', endpoint="add",methods=['GET', 'POST'])
@check_login_status
def user_add():
    form = AddUserForm()
    if g.user.is_admin != True and g.user.is_root != True:
        flash('没有权限请联系',category='error')
        return render_template('user/info.html',user=g.user,types=g.types)
    
    if form.validate_on_submit():
        # 获取数据
        username= request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')
            
        # 创建user对象
        adduser = User()
        adduser.username= username
        adduser.password= generate_password_hash(password=password)
        adduser.email= email
        adduser.phone= phone
        
        # 超级管理员可以操作添加root和admin用户 0 regular 1 admin 2 root
        if g.user.is_root == True:
            if role == '1':
                # 授权为管理员
                adduser.is_admin = True
            if role == '2':
                # 授权为超级管理员
                adduser.is_root = True
                
            bp_logging.logger.debug(f'role={role} {type(role)}')
            
        # 提交数据到数据库
        db.session.add(adduser)
        db.session.commit()
        flash('添加用户成功', category='info')
 
    return render_template('user/adduser.html',user=g.user,types=g.types,form=form)



# 删除用户
@user_bp.route('/delete', endpoint="delete",methods=['GET', 'POST'])
@check_login_status
def user_delete():
    # 判断操作权限
    if g.user.is_root == False and g.user.is_admin == False:
        flash('没有权限,请联系管理员',category='error')
        return jsonify(code=400,msg='无权限;请联系管理员')
    
    uid = request.args.get('uid',int)
    deluser = User.query.filter(User.id==uid).first()
    if not uid or not deluser:
        return jsonify(code=400,msg="用户不存在")
    
    if g.user.id == uid:
        return jsonify(code=400,msg='非法操作')

    # root权限操作
    if g.user.is_root == True:
        deluser.is_delete = True
        db.session.commit()
        # 清除登录状态
        cache.delete(str(deluser.id))
        return jsonify(code=200,msg='用户删除成功'),200
    
    # admin权限操作
    if g.user.is_admin == True and (deluser.is_root == False and deluser.is_admin == False):
        deluser.is_delete = True
        db.session.commit()
        # 清除登录状态
        cache.delete(str(deluser.id))
        return jsonify(code=200,msg='用户删除成功'),200
    
    # return jsonify(code=400,msg='无权限;请联系管理员')


# 编辑用户
@user_bp.route('/update', endpoint="update",methods=['GET', 'POST'])
@check_login_status
def user_update():
    # 判断操作权限
    if g.user.is_root == False and g.user.is_admin == False:
        flash('没有权限,请联系管理员',category='error')
        return render_template('user/info.html',user=g.user,types=g.types) 
    
    form = EditUserForm()
    
    # GET请求
    if request.method == 'GET':
        uid = request.args.get('uid',type=int)
        bp_logging.logger.debug(f'uid={uid} {type(uid)}')
        edituser = User.query.filter(User.id == uid).first()
        if not uid or not edituser:
            flash('非法操作,无法编辑',category='error')
            return render_template('user/info.html',user=g.user,types=g.types)
        
        form.username.data = edituser.username
        form.email.data = edituser.email
        form.phone.data = edituser.phone
        form.hiddens.data = uid

        return  render_template('user/update_user.html',user=g.user,types=g.types,form=form,edituser=edituser)
    
    # POST请求
    if form.validate_on_submit():
        # 验证通过
        edit_uid = request.form.get('hiddens',type=int)   # 获取表单隐藏的uid,验证使用
        edituser = User.query.filter(User.id == edit_uid).first()   # 获取用户对象
        if not edit_uid or not edituser:
            flash('非法操作,修改无效',category='error')
            return render_template('user/info.html',user=g.user,types=g.types)

        edituser.username = request.form.get('username')
        edituser.email = request.form.get('email')
        edituser.phone = request.form.get('phone')
        
        # 编辑权限---仅超级管理员可以编辑权限
        if g.user.is_root == True:
            new_role = request.form.get('role',0,type=int)   # 默认为普通用户
            if new_role == 1:
                edituser.is_admin = True
                edituser.is_root = False
            if new_role == 2:
                edituser.is_root = True
                edituser.is_admin = False

        # 是否允许登录
        new_allow = request.form.get('allow_login',1,type=int)  # 默认允许登录
        if new_allow == 0:
            edituser.allow_login = False
            
        db.session.commit()
        
        flash('编辑用户成功',category='info')
        return  render_template('user/update_user.html',user=g.user,types=g.types,form=form,edituser=edituser)
    
    edit_uid = request.form.get('hiddens',type=int)   # 获取表单隐藏的uid,验证使用
    edituser = User.query.filter(User.id == edit_uid).first()   # 获取用户对象
    form.hiddens.data = edit_uid
    return  render_template('user/update_user.html',user=g.user,types=g.types,form=form,edituser=edituser)
