from exts import db
from modules.base_module import Base
from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SelectField,DateTimeField,HiddenField
from wtforms.validators import DataRequired,Length,InputRequired,ValidationError,Length
from flask import g
from sqlalchemy import and_,or_,not_




class AboutMe(Base):
    __tablename__ = 'about_me'

    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)

    user = db.relationship('User', backref='about_me')
    
    
    def __str__(self):
        return self.content
    
    
    
# ==================form表单验证====================

class HiddensForm(FlaskForm):
    hidden = HiddenField('hidden')

class AboutMeForm(HiddensForm):
    content = TextAreaField('content', validators=[Length(max=20000)])







