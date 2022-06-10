from exts import db
from modules.base_module import Base
from flask_wtf import FlaskForm
from wtforms import FileField, HiddenField
from wtforms.validators import ValidationError
from flask_wtf.file import FileRequired, FileAllowed,FileSize

class Photo(Base):
    __tablename__ = 'photo'
    
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pic_url = db.Column(db.String(255), nullable=False)
    
    
    def __str__(self):
        return self.pic_url
    
    
# 相册上传form

class Hidden(FlaskForm):
    hidden = HiddenField('hidden')
    
    
class PhotoForm(Hidden):
    file = FileField('file',validators=[FileRequired(message="必须存在文件"),FileSize(max_size=1024*1024*10,message='图片大小不能超过10MB'),FileAllowed(['jpg','png','jpeg','gif'], '只能上传20MB以内图片')])
    
    
    

