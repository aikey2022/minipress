from modules.base_module import Base
from exts import db
from flask_wtf import FlaskForm
from wtforms import HiddenField,TextAreaField
from wtforms.validators import Length,ValidationError






class MsgAboard(Base):
    __tablename__ = 'msg_aboard'
    
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    msg_content = db.Column(db.Text, nullable=False)
    
    user = db.relationship('User', backref='msg_aboard')
    
    def __str__(self):
        return self.content
    
    
    


# ======留言板form========
class Hidden(FlaskForm):
    hidden = HiddenField('hidden')
    
    
class MsgAboardForm(Hidden):
    msg_content = TextAreaField('msg_content', validators=[Length(min=1, max=255,message='留言内容不能为空')])