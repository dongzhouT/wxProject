from datetime import datetime
from app import db

class CourseCategory(db.Model):
    """课程类别模型"""
    __tablename__ = 'course_category'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    courses = db.relationship('Course', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'school_id': self.school_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Course(db.Model):
    """课程模型"""
    __tablename__ = 'course'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('course_category.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_name = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False, comment='课时时长（分钟）')
    price = db.Column(db.Numeric(10, 2))
    max_students = db.Column(db.Integer)
    min_students = db.Column(db.Integer, default=1)
    cover_image = db.Column(db.String(255))
    status = db.Column(db.Enum('active', 'inactive'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    schedules = db.relationship('Schedule', backref='course', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('CourseOrder', backref='course', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'school_id': self.school_id,
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'teacher_name': self.teacher_name,
            'duration': self.duration,
            'price': float(self.price) if self.price else None,
            'max_students': self.max_students,
            'min_students': self.min_students,
            'cover_image': self.cover_image,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Schedule(db.Model):
    """课表安排模型"""
    __tablename__ = 'schedule'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100))
    status = db.Column(db.Enum('upcoming', 'ongoing', 'completed', 'cancelled'), default='upcoming')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    bookings = db.relationship('Booking', backref='schedule', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'location': self.location,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }