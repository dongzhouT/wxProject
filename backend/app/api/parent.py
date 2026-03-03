from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.parent import Parent, Student
from app.models.course import Course, Schedule
from app.models.order import CourseOrder, Booking, LeaveRequest
from datetime import datetime

# 创建蓝图
parent_bp = Blueprint('parent', __name__)

@parent_bp.route('/login', methods=['POST'])
def parent_login():
    """微信登录"""
    data = request.get_json()
    openid = data.get('openid')
    
    if not openid:
        return jsonify({'message': 'openid不能为空'}), 400
    
    # 查找家长
    parent = Parent.query.filter_by(openid=openid).first()
    
    if not parent:
        return jsonify({'message': '未找到该微信账号关联的家长信息'}), 404
    
    # 创建访问令牌
    access_token = create_access_token(identity=parent.id, additional_claims={'role': 'parent'})
    
    return jsonify({
        'access_token': access_token,
        'parent': parent.to_dict()
    }), 200

@parent_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_parent_profile():
    """获取家长信息"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    return jsonify(parent.to_dict()), 200

@parent_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_parent_profile():
    """更新家长信息"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    data = request.get_json()
    
    # 更新家长信息
    if 'real_name' in data:
        parent.real_name = data['real_name']
    if 'phone' in data:
        parent.phone = data['phone']
    if 'avatar_url' in data:
        parent.avatar_url = data['avatar_url']
    
    db.session.commit()
    
    return jsonify({'message': '家长信息更新成功', 'parent': parent.to_dict()}), 200

@parent_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    """获取学生列表"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    # 获取当前家长的所有学生
    students = Student.query.filter_by(parent_id=parent_id).all()
    
    return jsonify([student.to_dict() for student in students]), 200

@parent_bp.route('/students', methods=['POST'])
@jwt_required()
def add_student():
    """添加学生"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    data = request.get_json()
    
    # 验证必填字段
    if 'name' not in data:
        return jsonify({'message': '学生姓名是必填字段'}), 400
    
    # 创建学生
    student = Student(
        parent_id=parent_id,
        name=data['name'],
        gender=data.get('gender', 'male'),
        birthdate=data.get('birthdate'),
        avatar_url=data.get('avatar_url')
    )
    
    db.session.add(student)
    db.session.commit()
    
    return jsonify({'message': '学生添加成功', 'student': student.to_dict()}), 201

@parent_bp.route('/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    """获取学生详情"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    # 获取学生并验证是否属于当前家长
    student = Student.query.get_or_404(student_id)
    if student.parent_id != parent_id:
        return jsonify({'message': '无权访问该学生信息'}), 403
    
    return jsonify(student.to_dict()), 200

@parent_bp.route('/students/<int:student_id>', methods=['PUT'])
@jwt_required()
def update_student(student_id):
    """更新学生信息"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    # 获取学生并验证是否属于当前家长
    student = Student.query.get_or_404(student_id)
    if student.parent_id != parent_id:
        return jsonify({'message': '无权修改该学生信息'}), 403
    
    data = request.get_json()
    
    # 更新学生信息
    if 'name' in data:
        student.name = data['name']
    if 'gender' in data:
        student.gender = data['gender']
    if 'birthdate' in data:
        student.birthdate = data['birthdate']
    if 'avatar_url' in data:
        student.avatar_url = data['avatar_url']
    
    db.session.commit()
    
    return jsonify({'message': '学生信息更新成功', 'student': student.to_dict()}), 200

@parent_bp.route('/students/<int:student_id>', methods=['DELETE'])
@jwt_required()
def delete_student(student_id):
    """删除学生"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    # 获取学生并验证是否属于当前家长
    student = Student.query.get_or_404(student_id)
    if student.parent_id != parent_id:
        return jsonify({'message': '无权删除该学生'}), 403
    
    db.session.delete(student)
    db.session.commit()
    
    return jsonify({'message': '学生删除成功'}), 200

@parent_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    """获取课程列表"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    # 获取当前学校的所有课程
    courses = Course.query.filter_by(school_id=parent.school_id, status='active').all()
    
    return jsonify([course.to_dict() for course in courses]), 200

@parent_bp.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    """获取课程详情"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    # 获取课程并验证是否属于当前学校
    course = Course.query.get_or_404(course_id)
    if course.school_id != parent.school_id:
        return jsonify({'message': '无权访问该课程'}), 403
    
    return jsonify(course.to_dict()), 200

@parent_bp.route('/schedules', methods=['GET'])
@jwt_required()
def get_available_schedules():
    """获取可约课表列表"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    # 获取当前学校的所有课程
    courses = Course.query.filter_by(school_id=parent.school_id, status='active').all()
    course_ids = [course.id for course in courses]
    
    # 获取这些课程的所有未开始且未取消的课表
    now = datetime.utcnow()
    schedules = Schedule.query.filter(
        Schedule.course_id.in_(course_ids),
        Schedule.start_time > now,
        Schedule.status == 'upcoming'
    ).all()
    
    return jsonify([schedule.to_dict() for schedule in schedules]), 200

@parent_bp.route('/schedules/my', methods=['GET'])
@jwt_required()
def get_my_schedules():
    """获取已约课表列表"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    # 获取当前家长的所有订单
    orders = CourseOrder.query.filter_by(parent_id=parent_id).all()
    order_ids = [order.id for order in orders]
    
    # 获取这些订单的所有已约课记录
    bookings = Booking.query.filter(Booking.order_id.in_(order_ids)).all()
    booking_ids = [booking.id for booking in bookings]
    
    # 获取这些约课记录的所有课表
    schedules = []
    for booking in bookings:
        schedule = Schedule.query.get(booking.schedule_id)
        if schedule:
            schedule_dict = schedule.to_dict()
            schedule_dict['booking_id'] = booking.id
            schedule_dict['booking_status'] = booking.status
            schedules.append(schedule_dict)
    
    return jsonify(schedules), 200

@parent_bp.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    """约课"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['order_id', 'schedule_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} 是必填字段'}), 400
    
    # 验证订单是否存在且属于当前家长
    order = CourseOrder.query.get_or_404(data['order_id'])
    if order.parent_id != parent_id:
        return jsonify({'message': '所选订单无效'}), 400
    
    # 验证订单是否有剩余课程
    if order.remaining_classes <= 0:
        return jsonify({'message': '该订单已无剩余课程'}), 400
    
    # 验证课表是否存在且属于当前学校
    schedule = Schedule.query.get_or_404(data['schedule_id'])
    course = Course.query.get_or_404(schedule.course_id)
    if course.school_id != parent.school_id:
        return jsonify({'message': '所选课表无效'}), 400
    
    # 验证课表是否可约
    if schedule.status != 'upcoming':
        return jsonify({'message': '该课表不可约'}), 400
    
    if schedule.start_time <= datetime.utcnow():
        return jsonify({'message': '该课表已开始或已结束'}), 400
    
    # 验证是否已经约过该课表
    existing_booking = Booking.query.filter_by(
        order_id=data['order_id'],
        schedule_id=data['schedule_id']
    ).first()
    if existing_booking:
        return jsonify({'message': '已经约过该课表'}), 400
    
    # 创建约课记录
    booking = Booking(
        order_id=data['order_id'],
        schedule_id=data['schedule_id']
    )
    
    db.session.add(booking)
    db.session.commit()
    
    return jsonify({'message': '约课成功', 'booking': booking.to_dict()}), 201

@parent_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_bookings():
    """获取约课列表"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    # 获取当前家长的所有订单
    orders = CourseOrder.query.filter_by(parent_id=parent_id).all()
    order_ids = [order.id for order in orders]
    
    # 获取这些订单的所有约课记录
    bookings = Booking.query.filter(Booking.order_id.in_(order_ids)).all()
    
    # 构建详细的约课信息
    booking_details = []
    for booking in bookings:
        booking_dict = booking.to_dict()
        
        # 添加订单信息
        order = CourseOrder.query.get(booking.order_id)
        if order:
            booking_dict['order'] = order.to_dict()
        
        # 添加课表信息
        schedule = Schedule.query.get(booking.schedule_id)
        if schedule:
            booking_dict['schedule'] = schedule.to_dict()
            
            # 添加课程信息
            course = Course.query.get(schedule.course_id)
            if course:
                booking_dict['course'] = course.to_dict()
        
        # 添加请假信息
        leave_request = LeaveRequest.query.filter_by(booking_id=booking.id).first()
        if leave_request:
            booking_dict['leave_request'] = leave_request.to_dict()
        
        booking_details.append(booking_dict)
    
    return jsonify(booking_details), 200

@parent_bp.route('/bookings/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def cancel_booking(booking_id):
    """取消约课"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    # 获取约课记录并验证是否属于当前家长
    booking = Booking.query.get_or_404(booking_id)
    order = CourseOrder.query.get_or_404(booking.order_id)
    if order.parent_id != parent_id:
        return jsonify({'message': '无权取消该约课'}), 403
    
    # 验证是否可以取消
    schedule = Schedule.query.get_or_404(booking.schedule_id)
    if schedule.start_time <= datetime.utcnow():
        return jsonify({'message': '该课表已开始或已结束，无法取消'}), 400
    
    # 检查是否已有请假记录
    leave_request = LeaveRequest.query.filter_by(booking_id=booking_id).first()
    if leave_request:
        return jsonify({'message': '该约课已有请假记录，请通过请假流程处理'}), 400
    
    # 更新约课状态
    booking.status = 'cancelled'
    
    db.session.commit()
    
    return jsonify({'message': '约课取消成功'}), 200

@parent_bp.route('/leave-requests', methods=['POST'])
@jwt_required()
def create_leave_request():
    """提交请假申请"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['booking_id', 'reason']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} 是必填字段'}), 400
    
    # 验证约课记录是否存在且属于当前家长
    booking = Booking.query.get_or_404(data['booking_id'])
    order = CourseOrder.query.get_or_404(booking.order_id)
    if order.parent_id != parent_id:
        return jsonify({'message': '所选约课记录无效'}), 400
    
    # 验证是否可以请假
    schedule = Schedule.query.get_or_404(booking.schedule_id)
    if schedule.start_time <= datetime.utcnow():
        return jsonify({'message': '该课表已开始或已结束，无法请假'}), 400
    
    if booking.status != 'booked':
        return jsonify({'message': '该约课记录状态不允许请假'}), 400
    
    # 检查是否已有请假记录
    existing_request = LeaveRequest.query.filter_by(booking_id=data['booking_id']).first()
    if existing_request:
        return jsonify({'message': '该约课已有请假记录'}), 400
    
    # 创建请假记录
    leave_request = LeaveRequest(
        booking_id=data['booking_id'],
        reason=data['reason']
    )
    
    db.session.add(leave_request)
    db.session.commit()
    
    return jsonify({'message': '请假申请提交成功', 'leave_request': leave_request.to_dict()}), 201

@parent_bp.route('/leave-requests', methods=['GET'])
@jwt_required()
def get_leave_requests():
    """获取请假列表"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    # 获取当前家长的所有订单
    orders = CourseOrder.query.filter_by(parent_id=parent_id).all()
    order_ids = [order.id for order in orders]
    
    # 获取这些订单的所有约课记录
    bookings = Booking.query.filter(Booking.order_id.in_(order_ids)).all()
    booking_ids = [booking.id for booking in bookings]
    
    # 获取这些约课记录的所有请假申请
    leave_requests = LeaveRequest.query.filter(LeaveRequest.booking_id.in_(booking_ids)).all()
    
    # 构建详细的请假信息
    request_details = []
    for request in leave_requests:
        request_dict = request.to_dict()
        
        # 添加约课信息
        booking = Booking.query.get(request.booking_id)
        if booking:
            request_dict['booking'] = booking.to_dict()
            
            # 添加课表信息
            schedule = Schedule.query.get(booking.schedule_id)
            if schedule:
                request_dict['schedule'] = schedule.to_dict()
                
                # 添加课程信息
                course = Course.query.get(schedule.course_id)
                if course:
                    request_dict['course'] = course.to_dict()
        
        request_details.append(request_dict)
    
    return jsonify(request_details), 200

@parent_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """获取订单列表"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    # 获取当前家长的所有订单
    orders = CourseOrder.query.filter_by(parent_id=parent_id).all()
    
    # 构建详细的订单信息
    order_details = []
    for order in orders:
        order_dict = order.to_dict()
        
        # 添加课程信息
        course = Course.query.get(order.course_id)
        if course:
            order_dict['course'] = course.to_dict()
        
        # 添加学生信息
        student = Student.query.get(order.student_id)
        if student:
            order_dict['student'] = student.to_dict()
        
        order_details.append(order_dict)
    
    return jsonify(order_details), 200

@parent_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """获取订单详情"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    # 获取订单并验证是否属于当前家长
    order = CourseOrder.query.get_or_404(order_id)
    if order.parent_id != parent_id:
        return jsonify({'message': '无权访问该订单'}), 403
    
    # 构建详细的订单信息
    order_dict = order.to_dict()
    
    # 添加课程信息
    course = Course.query.get(order.course_id)
    if course:
        order_dict['course'] = course.to_dict()
    
    # 添加学生信息
    student = Student.query.get(order.student_id)
    if student:
        order_dict['student'] = student.to_dict()
    
    # 添加约课记录
    bookings = Booking.query.filter_by(order_id=order_id).all()
    order_dict['bookings'] = [booking.to_dict() for booking in bookings]
    
    return jsonify(order_dict), 200

@parent_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    """创建订单（模拟支付）"""
    parent_id = get_jwt_identity()
    parent = Parent.query.get_or_404(parent_id)
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['student_id', 'course_id', 'total_classes', 'amount']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} 是必填字段'}), 400
    
    # 验证学生是否存在且属于当前家长
    student = Student.query.get_or_404(data['student_id'])
    if student.parent_id != parent_id:
        return jsonify({'message': '所选学生无效'}), 400
    
    # 验证课程是否存在且属于当前学校
    course = Course.query.get_or_404(data['course_id'])
    if course.school_id != parent.school_id:
        return jsonify({'message': '所选课程无效'}), 400
    
    # 验证课程状态
    if course.status != 'active':
        return jsonify({'message': '该课程已下架'}), 400
    
    # 创建订单
    order = CourseOrder(
        parent_id=parent_id,
        student_id=data['student_id'],
        course_id=data['course_id'],
        total_classes=data['total_classes'],
        remaining_classes=data['total_classes'],
        amount=data['amount'],
        status='paid'  # 模拟支付成功
    )
    
    db.session.add(order)
    db.session.commit()
    
    return jsonify({'message': '订单创建成功', 'order': order.to_dict()}), 201