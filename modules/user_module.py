from exts import db,cache
from datetime import datetime
from modules.base_module import Base
from flask import session,g
from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,PasswordField,FileField,EmailField,HiddenField
from wtforms.validators import DataRequired,Length,InputRequired,EqualTo,Regexp,ValidationError
import re
from werkzeug.security import generate_password_hash,check_password_hash
from flask_wtf.file import FileField, FileAllowed, FileRequired,FileSize


class User(Base):
    __tablename__ = 'user'

    username = db.Column(db.String(50), nullable=False,unique=True)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(50), nullable=False,unique=True)
    phone = db.Column(db.String(11), nullable=False,unique=True)
    is_delete = db.Column(db.Boolean, default=False)
    is_root = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    allow_login = db.Column(db.Boolean, default=True)
    active_time = db.Column(db.DateTime)
    login_time = db.Column(db.DateTime)
    icon = db.Column(db.String(255))
    
    def __str__(self):
        return str(self.id)



# #=======================================================基础表单字段 start =======================================================#
class UsernameForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(),InputRequired(message="必须输入用户名"),Length(min=6,max=20,message='用户名长度在6-20个字符'),])
    def validate_username(self,field):
        if re.search('^[0-9_]',field.data):
            raise ValidationError(message='用户名不能以数字或者下划线开头')
        
        if User.query.filter(User.username == field.data).first():
            raise ValidationError(message='用户名已存在')
        
        # if field.data.lower() in [ User.username.lower() for user in User.query.all() ]:
        #     raise ValidationError(message='用户名已存在')
        
        if re.search(' ',field.data):
            raise ValidationError(message='用户名不能含有空格')


class PassWordForm(FlaskForm):
    password = PasswordField('password', validators=[DataRequired(),InputRequired(message="必须输入密码"),Length(min=6,max=16,message='密码长度在6-16个字符'),])


class EmailForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired(),InputRequired(message="必须输入邮箱"),Length(min=7,max=50,message='邮箱长度在6-50个字符'),])
    def validate_email(self,field):
        if User.query.filter(User.email == field.data).first():
            raise ValidationError(message='邮箱已存在')


class PhoneForm(FlaskForm):
    phone = StringField('phone', validators=[DataRequired(),InputRequired(message="必须输入11位手机号"),Length(min=11,max=11,message='请输入11位手机号'),Regexp('^1[356789][0-9]{9}$',message='手机号格式不正确')])
    def validate_phone(self,field):
        if User.query.filter(User.phone == field.data).first():
            raise ValidationError(message='手机号已存在')    


class CheckCodeForm(FlaskForm):
    check_code = StringField('check_code', validators=[DataRequired(),InputRequired(message="必须输入验证码"),Length(min=4,max=4,message='验证码长度为4位')])

    def validate_check_code(self,field):
        code_key = session.get('code_key')
        # 验证过期
        if not cache.get(code_key):
            raise ValidationError(message='验证码已过期')
        
        #  验证码错误
        if cache.get(code_key).lower() != field.data.lower():
            raise ValidationError(message='验证码错误')  

class ImageUpLoad(FlaskForm):
    image = FileField('iconimg', validators=[FileAllowed(['jpg','png','jpeg','gif'],message='只能上传jpg,png,jpeg,gif格式的图片'),FileSize(max_size=1024*1024*10,min_size=0,message='图片大小必须为1M以内')])
    
class HiddenForm(FlaskForm):
    hiddens = HiddenField('hiddens')
             
# #=======================================================基础表单字段 end =======================================================#

# 验证注册表单
class UserRegForm(UsernameForm,PassWordForm,EmailForm,PhoneForm,CheckCodeForm):
    repassword = PasswordField('repassword', validators=[DataRequired(),InputRequired(message="必须输入确认密码"),EqualTo('password',message='两次密码不一致')])
 

#  验证登录表单
class UserLogForm(UsernameForm,PassWordForm,CheckCodeForm):
    def validate_username(self,field):
        if re.search('^[0-9_]',field.data):
            raise ValidationError(message='用户名不能以数字或者下划线开头')
        
        if re.search(' ',field.data):
            raise ValidationError(message='用户名不能含有空格')


#  用户中心表单
class UserCenterForm(UsernameForm,EmailForm,PhoneForm,ImageUpLoad):
    
    def validate_username(self,field):
        if re.search('^[0-9_]',field.data):
            raise ValidationError(message='用户名不能以数字或者下划线开头')

        if re.search(' ',field.data):
            raise ValidationError(message='用户名不能含有空格')
        
        # 仅用户名发生变化时验证唯一       
        if g.user.username != field.data:
            if User.query.filter(User.username == field.data).first():
                raise ValidationError(message='用户名已存在')

        
    def validate_email(self,field):
        # 仅当邮箱发生变化时验证唯一
        if g.user.email != field.data:
            if User.query.filter(User.email == field.data).first():
                raise ValidationError(message='邮箱已存在')
    
    def validate_phone(self,field):
        # 仅当手机号发生变化时验证唯一
        if g.user.phone != field.data:
            if User.query.filter(User.phone == field.data).first():
                raise ValidationError(message='手机号已存在')
            

# 用户修改密码表单
class ModiyPassForm(PassWordForm):
    newpasswd = PasswordField('newpasswd', validators=[DataRequired(),InputRequired(message="必须输入新密码"),Length(min=6,max=16,message='密码长度在6-16个字符'),])
    repasswd = PasswordField('repasswd', validators=[DataRequired(),InputRequired(message="必须输入确认密码"),EqualTo('newpasswd',message='两次密码不一致')])
    
    # 校验原密码
    def validate_password(self,field):
        if not check_password_hash(g.user.password,field.data):
            raise ValidationError(message='原密码错误')


# 管理员新增用户表单
class AddUserForm(UsernameForm,PassWordForm,EmailForm,PhoneForm):
    repassword = PasswordField('repassword', validators=[DataRequired(),InputRequired(message="必须输入确认密码"),EqualTo('password',message='两次密码不一致')])


# 管理员编辑用户表单
class EditUserForm(UsernameForm,EmailForm,PhoneForm,HiddenForm):
    def validate_username(self,field):
        if re.search('^[0-9_]',field.data):
            raise ValidationError(message='用户名不能以数字或者下划线开头')

        if re.search(' ',field.data):
            raise ValidationError(message='用户名不能含有空格')
        
        # 仅用户名发生变化时验证唯一       
        if g.edituser.username != field.data:
            if User.query.filter(User.username == field.data).first():
                raise ValidationError(message='用户名已存在')

        
    def validate_email(self,field):
        # 仅当邮箱发生变化时验证唯一
        if g.edituser.email != field.data:
            if User.query.filter(User.email == field.data).first():
                raise ValidationError(message='邮箱已存在')
    
    def validate_phone(self,field):
        # 仅当手机号发生变化时验证唯一
        if g.edituser.phone != field.data:
            if User.query.filter(User.phone == field.data).first():
                raise ValidationError(message='手机号已存在')
            
            
# 管理员修改用户密码
class EditUserPassForm(PassWordForm,HiddenForm):
    repasswd = PasswordField('repasswd', validators=[DataRequired(),InputRequired(message="必须输入确认密码"),EqualTo('password',message='两次密码不一致')])