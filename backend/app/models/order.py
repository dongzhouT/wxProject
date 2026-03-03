from datetime import datetime
from app import db

class CourseOrder(db.Model):
    """课程订单模型"""
    __tablename__ = 'course_order'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    total_classes = db.Column(db.Integer, nullable=False)
    remaining_classes = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('pending', 'paid', 'cancelled'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    bookings = db.relationship('Booking', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'total_classes': self.total_classes,
            'remaining_classes': self.remaining_classes,
            'amount': float(self.amount) if self.amount else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Booking(db.Model):
    """约课记录模型"""
    __tablename__ = 'booking'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('course_order.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    status = db.Column(db.Enum('booked', 'attended', 'absent', 'cancelled'), default='booked')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    leave_request = db.relationship('LeaveRequest', backref='booking', lazy=True, uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'schedule_id': self.schedule_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class LeaveRequest(db.Model):
    """请假记录模型"""
    __tablename__ = 'leave_request'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    processed_by = db.Column(db.Integer, db.ForeignKey('school_account.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'reason': self.reason,
            'status': self.status,
            'processed_by': self.processed_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }