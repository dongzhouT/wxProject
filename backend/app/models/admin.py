from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Admin(db.Model):
    """管理员模型"""
    __tablename__ = 'admin'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    schools = db.relationship('School', backref='creator', lazy=True)
    
    @property
    def password(self):
        """密码属性（只读）"""
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """设置密码（加密存储）"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }