from datetime import datetime
from app import db

class Parent(db.Model):
    """家长模型"""
    __tablename__ = 'parent'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    openid = db.Column(db.String(100), unique=True, nullable=False)
    real_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    avatar_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    students = db.relationship('Student', backref='parent', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('CourseOrder', backref='parent', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'school_id': self.school_id,
            'openid': self.openid,
            'real_name': self.real_name,
            'phone': self.phone,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Student(db.Model):
    """学生模型"""
    __tablename__ = 'student'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Enum('male', 'female'), default='male')
    birthdate = db.Column(db.Date)
    avatar_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    orders = db.relationship('CourseOrder', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'name': self.name,
            'gender': self.gender,
            'birthdate': self.birthdate.isoformat() if self.birthdate else None,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }