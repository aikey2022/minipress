from exts import db
from modules.base_module import Base
from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SelectField,DateTimeField,HiddenField
from wtforms.validators import DataRequired,Length,InputRequired,ValidationError
from flask import g
from sqlalchemy import and_,or_,not_

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
    # 内容
    content = db.Column(db.Text, nullable=False)
    
    article_type = db.relationship('Article_Type', backref='article')
    user = db.relationship('User', backref='article')
    
    # 是否删除
    isdelete = db.Column(db.Boolean, default=False)
    
    # 点赞量
    thumbs_up = db.Column(db.Integer, default=0)
    
    # 浏览量
    views = db.Column(db.Integer, default=0)
    
    def __str__(self):
        return self.content


class Favorites(Base):
    __tablename__ = "favorites"
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    aid = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    
    user = db.relationship('User', backref='favorites')
    article = db.relationship('Article', backref='favorites')
    

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
        if Article.query.filter(Article.article_title == field.data,Article.uid != g.user.id).first():
            # print("-------------------------------------->>>>>>>验证标题",field.data)
            raise ValidationError('标题已存在')


class ContentForm(FlaskForm):
    content  = TextAreaField('content', validators=[Length(min=10,max=32000,message="文章内容需在10-32000字之间")])


class HiddensForm(FlaskForm):
    hiddens = HiddenField('hiddens')

# ===========================文章类型表单字段 end=======================================================#


class ArticleForm(TitleForm,ContentForm):
    pass


class EditArticleForm(TitleForm,ContentForm,HiddensForm):
    # 验证标题唯一
    def validate_title(self,field):
        if Article.query.filter(and_(Article.article_title == field.data, Article.uid != g.user.id)).first():
            # print("-------------------------------------->>>>>>>验证标题",field.data)
            raise ValidationError('标题已存在')
 
      
class CommentForm(HiddensForm):
    # 评论
    comment  = TextAreaField('comment', validators=[Length(min=10,max=255,message="评论内容在10-255字之间")])

        
        
