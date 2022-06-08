from exts import db
from modules.base_module import Base
from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SelectField,DateTimeField,HiddenField
from wtforms.validators import DataRequired,Length,InputRequired,ValidationError
from flask import g


class Article_Type(Base):
    __tablename__ = 'article_type'
    type_name = db.Column(db.String(50), nullable=False,unique=True)
    isdelete = db.Column(db.Boolean, default=False)
    
    def __str__(self):
        return self.type_name

    
class Article(Base):
    __tablename__ = 'article'
    article_title = db.Column(db.String(100), nullable=False)
    
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('article_type.id'), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    
    article_type = db.relationship('Article_Type', backref='article')
    user = db.relationship('User', backref='article')
    
    isdelete = db.Column(db.Boolean, default=False)
    
    def __str__(self):
        return self.content

    
class Comments(Base):
    __tablename__ = 'comments'
    
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    art_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    com_content = db.Column(db.Text, nullable=False)
    
    user = db.relationship('User', backref='comments')
    article = db.relationship('Article', backref='comments')
    
    isdelete = db.Column(db.Boolean, default=False)
    
    def  __str__(self):
        return self.content
    
    
# ===========================文章类型表单字段 start=======================================================#
class TitleForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(),InputRequired(message="必须输入文章标题"),Length(min=3,max=100,message="文章标题不能超过100个字符")])
    # 验证标题唯一
    def validate_title(self,field):
        if Article.query.filter(Article.article_title == field.data).first():
            print("-------------------------------------->>>>>>>验证标题",field.data)
            raise ValidationError('标题已存在')


class ContentForm(FlaskForm):
    content  = TextAreaField('content', validators=[Length(max=32000,message="文章内容不能超过32000个字符")])
    def validate_content(self,field):
        if len(field.data) < 10:
            raise ValidationError("文章内容不能少于10个字符")


class HiddensForm(FlaskForm):
    hiddens = HiddenField('hiddens')

# ===========================文章类型表单字段 end=======================================================#

class ArticleForm(TitleForm,ContentForm):
    pass

class EditArticleForm(TitleForm,ContentForm,HiddensForm):
    pass