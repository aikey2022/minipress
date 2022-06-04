from exts import db
from modules.base_module import Base


class Photo(Base):
    __tablename__ = 'photo'
    
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pic_url = db.Column(db.String(255), nullable=False)
    
    
    def __str__(self):
        return self.pic_url