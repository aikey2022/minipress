from exts import db
from modules.base_module import Base



class Article_Type(Base):
    __tablename__ = 'article_type'
    type_name = db.Column(db.String(50), nullable=False,unique=True)
    
    def __str__(self):
        return self.type_name

    
class Article(Base):
    __tablename__ = 'article'
    
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('article_type.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    article_type = db.relationship('Article_Type', backref='article')
    user = db.relationship('User', backref='article')
    
    def __str__(self):
        return self.content

    
class Comments(Base):
    __tablename__ = 'comments'
    
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    art_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    com_content = db.Column(db.Text, nullable=False)
    
    user = db.relationship('User', backref='comments')
    article = db.relationship('Article', backref='comments')
    
    def  __str__(self):
        return self.content