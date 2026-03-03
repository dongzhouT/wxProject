from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class School(db.Model):
    """学校模型"""
    __tablename__ = 'school'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(50), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255))
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    accounts = db.relationship('SchoolAccount', backref='school', lazy=True, cascade='all, delete-orphan')
    parents = db.relationship('Parent', backref='school', lazy=True, cascade='all, delete-orphan')
    course_categories = db.relationship('CourseCategory', backref='school', lazy=True, cascade='all, delete-orphan')
    courses = db.relationship('Course', backref='school', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'address': self.address,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SchoolAccount(db.Model):
    """学校账户模型"""
    __tablename__ = 'school_account'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.Enum('principal', 'teacher', 'staff'), default='staff')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    leave_requests = db.relationship('LeaveRequest', backref='processor', lazy=True)
    
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
            'school_id': self.school_id,
            'username': self.username,
            'real_name': self.real_name,
            'phone': self.phone,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }