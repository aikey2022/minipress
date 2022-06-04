from modules.base_module import Base
from exts import db


class MsgAboard(Base):
    __tablename__ = 'msg_aboard'
    
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    msg_content = db.Column(db.Text, nullable=False)
    
    user = db.relationship('User', backref='msg_aboard')
    
    def __str__(self):
        return self.content