from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.school import SchoolAccount
from app.models.parent import Parent, Student
from app.models.course import CourseCategory, Course, Schedule
from app.models.order import CourseOrder, Booking, LeaveRequest

# 创建蓝图
school_bp = Blueprint('school', __name__)

@school_bp.route('/login', methods=['POST'])
def school_login():
    """学校账户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
    
    account = SchoolAccount.query.filter_by(username=username).first()
    
    if not account or not account.verify_password(password):
        return jsonify({'message': '用户名或密码错误'}), 401
    
    # 创建访问令牌
    access_token = create_access_token(identity=account.id, additional_claims={'role': 'school'})
    
    return jsonify({
        'access_token': access_token,
        'account': account.to_dict()
    }), 200

@school_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_school_profile():
    """获取学校账户信息"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    return jsonify(account.to_dict()), 200

@school_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_school_profile():
    """更新学校账户信息"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    data = request.get_json()
    
    # 更新账户信息
    if 'real_name' in data:
        account.real_name = data['real_name']
    if 'phone' in data:
        account.phone = data['phone']
    
    db.session.commit()
    
    return jsonify({'message': '账户信息更新成功', 'account': account.to_dict()}), 200

@school_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_school_password():
    """修改学校账户密码"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'message': '旧密码和新密码不能为空'}), 400
    
    if not account.verify_password(old_password):
        return jsonify({'message': '旧密码错误'}), 401
    
    account.password = new_password
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'}), 200

@school_bp.route('/parents', methods=['GET'])
@jwt_required()
def get_parents():
    """获取家长列表"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取当前学校的所有家长
    parents = Parent.query.filter_by(school_id=account.school_id).all()
    
    return jsonify([parent.to_dict() for parent in parents]), 200

@school_bp.route('/parents', methods=['POST'])
@jwt_required()
def add_parent():
    """添加家长"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['openid', 'real_name', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} 是必填字段'}), 400
    
    # 检查openid是否已存在
    existing_parent = Parent.query.filter_by(openid=data['openid']).first()
    if existing_parent:
        return jsonify({'message': '该微信账号已关联家长'}), 400
    
    # 创建家长
    parent = Parent(
        school_id=account.school_id,
        openid=data['openid'],
        real_name=data['real_name'],
        phone=data['phone'],
        avatar_url=data.get('avatar_url')
    )
    
    db.session.add(parent)
    db.session.commit()
    
    return jsonify({'message': '家长添加成功', 'parent': parent.to_dict()}), 201

@school_bp.route('/parents/<int:parent_id>', methods=['GET'])
@jwt_required()
def get_parent(parent_id):
    """获取家长详情"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取家长并验证是否属于当前学校
    parent = Parent.query.get_or_404(parent_id)
    if parent.school_id != account.school_id:
        return jsonify({'message': '无权访问该家长信息'}), 403
    
    return jsonify(parent.to_dict()), 200

@school_bp.route('/parents/<int:parent_id>', methods=['PUT'])
@jwt_required()
def update_parent(parent_id):
    """更新家长信息"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取家长并验证是否属于当前学校
    parent = Parent.query.get_or_404(parent_id)
    if parent.school_id != account.school_id:
        return jsonify({'message': '无权修改该家长信息'}), 403
    
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

@school_bp.route('/parents/<int:parent_id>', methods=['DELETE'])
@jwt_required()
def delete_parent(parent_id):
    """删除家长"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取家长并验证是否属于当前学校
    parent = Parent.query.get_or_404(parent_id)
    if parent.school_id != account.school_id:
        return jsonify({'message': '无权删除该家长'}), 403
    
    db.session.delete(parent)
    db.session.commit()
    
    return jsonify({'message': '家长删除成功'}), 200

@school_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    """获取学生列表"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取当前学校的所有学生
    parents = Parent.query.filter_by(school_id=account.school_id).all()
    parent_ids = [parent.id for parent in parents]
    
    students = Student.query.filter(Student.parent_id.in_(parent_ids)).all()
    
    return jsonify([student.to_dict() for student in students]), 200

@school_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """获取课程类别列表"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取当前学校的所有课程类别
    categories = CourseCategory.query.filter_by(school_id=account.school_id).all()
    
    return jsonify([category.to_dict() for category in categories]), 200

@school_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    """创建课程类别"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    data = request.get_json()
    
    # 验证必填字段
    if 'name' not in data:
        return jsonify({'message': '类别名称是必填字段'}), 400
    
    # 创建课程类别
    category = CourseCategory(
        school_id=account.school_id,
        name=data['name'],
        description=data.get('description')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({'message': '课程类别创建成功', 'category': category.to_dict()}), 201

@school_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """更新课程类别"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取课程类别并验证是否属于当前学校
    category = CourseCategory.query.get_or_404(category_id)
    if category.school_id != account.school_id:
        return jsonify({'message': '无权修改该课程类别'}), 403
    
    data = request.get_json()
    
    # 更新课程类别
    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    
    db.session.commit()
    
    return jsonify({'message': '课程类别更新成功', 'category': category.to_dict()}), 200

@school_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """删除课程类别"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取课程类别并验证是否属于当前学校
    category = CourseCategory.query.get_or_404(category_id)
    if category.school_id != account.school_id:
        return jsonify({'message': '无权删除该课程类别'}), 403
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': '课程类别删除成功'}), 200

@school_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    """获取课程列表"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取当前学校的所有课程
    courses = Course.query.filter_by(school_id=account.school_id).all()
    
    return jsonify([course.to_dict() for course in courses]), 200

@school_bp.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    """创建课程"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['category_id', 'name', 'teacher_name', 'duration']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} 是必填字段'}), 400
    
    # 验证课程类别是否存在且属于当前学校
    category = CourseCategory.query.get_or_404(data['category_id'])
    if category.school_id != account.school_id:
        return jsonify({'message': '所选课程类别无效'}), 400
    
    # 创建课程
    course = Course(
        school_id=account.school_id,
        category_id=data['category_id'],
        name=data['name'],
        description=data.get('description'),
        teacher_name=data['teacher_name'],
        duration=data['duration'],
        price=data.get('price'),
        max_students=data.get('max_students'),
        min_students=data.get('min_students', 1),
        cover_image=data.get('cover_image'),
        status=data.get('status', 'active')
    )
    
    db.session.add(course)
    db.session.commit()
    
    return jsonify({'message': '课程创建成功', 'course': course.to_dict()}), 201

@school_bp.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    """获取课程详情"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取课程并验证是否属于当前学校
    course = Course.query.get_or_404(course_id)
    if course.school_id != account.school_id:
        return jsonify({'message': '无权访问该课程'}), 403
    
    return jsonify(course.to_dict()), 200

@school_bp.route('/courses/<int:course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    """更新课程信息"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取课程并验证是否属于当前学校
    course = Course.query.get_or_404(course_id)
    if course.school_id != account.school_id:
        return jsonify({'message': '无权修改该课程'}), 403
    
    data = request.get_json()
    
    # 更新课程信息
    if 'category_id' in data:
        # 验证课程类别是否存在且属于当前学校
        category = CourseCategory.query.get_or_404(data['category_id'])
        if category.school_id != account.school_id:
            return jsonify({'message': '所选课程类别无效'}), 400
        course.category_id = data['category_id']
    if 'name' in data:
        course.name = data['name']
    if 'description' in data:
        course.description = data['description']
    if 'teacher_name' in data:
        course.teacher_name = data['teacher_name']
    if 'duration' in data:
        course.duration = data['duration']
    if 'price' in data:
        course.price = data['price']
    if 'max_students' in data:
        course.max_students = data['max_students']
    if 'min_students' in data:
        course.min_students = data['min_students']
    if 'cover_image' in data:
        course.cover_image = data['cover_image']
    if 'status' in data:
        course.status = data['status']
    
    db.session.commit()
    
    return jsonify({'message': '课程信息更新成功', 'course': course.to_dict()}), 200

@school_bp.route('/courses/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    """删除课程"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取课程并验证是否属于当前学校
    course = Course.query.get_or_404(course_id)
    if course.school_id != account.school_id:
        return jsonify({'message': '无权删除该课程'}), 403
    
    db.session.delete(course)
    db.session.commit()
    
    return jsonify({'message': '课程删除成功'}), 200

@school_bp.route('/schedules', methods=['GET'])
@jwt_required()
def get_schedules():
    """获取课表列表"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取当前学校的所有课程
    courses = Course.query.filter_by(school_id=account.school_id).all()
    course_ids = [course.id for course in courses]
    
    # 获取这些课程的所有课表
    schedules = Schedule.query.filter(Schedule.course_id.in_(course_ids)).all()
    
    return jsonify([schedule.to_dict() for schedule in schedules]), 200

@school_bp.route('/schedules', methods=['POST'])
@jwt_required()
def create_schedule():
    """创建课表"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['course_id', 'start_time', 'end_time']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} 是必填字段'}), 400
    
    # 验证课程是否存在且属于当前学校
    course = Course.query.get_or_404(data['course_id'])
    if course.school_id != account.school_id:
        return jsonify({'message': '所选课程无效'}), 400
    
    # 创建课表
    schedule = Schedule(
        course_id=data['course_id'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        location=data.get('location'),
        status=data.get('status', 'upcoming')
    )
    
    db.session.add(schedule)
    db.session.commit()
    
    return jsonify({'message': '课表创建成功', 'schedule': schedule.to_dict()}), 201

@school_bp.route('/schedules/<int:schedule_id>', methods=['PUT'])
@jwt_required()
def update_schedule(schedule_id):
    """更新课表信息"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取课表并验证是否属于当前学校
    schedule = Schedule.query.get_or_404(schedule_id)
    course = Course.query.get_or_404(schedule.course_id)
    if course.school_id != account.school_id:
        return jsonify({'message': '无权修改该课表'}), 403
    
    data = request.get_json()
    
    # 更新课表信息
    if 'start_time' in data:
        schedule.start_time = data['start_time']
    if 'end_time' in data:
        schedule.end_time = data['end_time']
    if 'location' in data:
        schedule.location = data['location']
    if 'status' in data:
        schedule.status = data['status']
    
    db.session.commit()
    
    return jsonify({'message': '课表信息更新成功', 'schedule': schedule.to_dict()}), 200

@school_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
def delete_schedule(schedule_id):
    """删除课表"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取课表并验证是否属于当前学校
    schedule = Schedule.query.get_or_404(schedule_id)
    course = Course.query.get_or_404(schedule.course_id)
    if course.school_id != account.school_id:
        return jsonify({'message': '无权删除该课表'}), 403
    
    db.session.delete(schedule)
    db.session.commit()
    
    return jsonify({'message': '课表删除成功'}), 200

@school_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_bookings():
    """获取约课列表"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取当前学校的所有课程
    courses = Course.query.filter_by(school_id=account.school_id).all()
    course_ids = [course.id for course in courses]
    
    # 获取这些课程的所有订单
    orders = CourseOrder.query.filter(CourseOrder.course_id.in_(course_ids)).all()
    order_ids = [order.id for order in orders]
    
    # 获取这些订单的所有约课记录
    bookings = Booking.query.filter(Booking.order_id.in_(order_ids)).all()
    
    return jsonify([booking.to_dict() for booking in bookings]), 200

@school_bp.route('/bookings/<int:booking_id>/status', methods=['PUT'])
@jwt_required()
def update_booking_status(booking_id):
    """更新约课状态（消课操作）"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取约课记录并验证是否属于当前学校
    booking = Booking.query.get_or_404(booking_id)
    order = CourseOrder.query.get_or_404(booking.order_id)
    course = Course.query.get_or_404(order.course_id)
    if course.school_id != account.school_id:
        return jsonify({'message': '无权修改该约课记录'}), 403
    
    data = request.get_json()
    
    # 验证状态值
    if 'status' not in data:
        return jsonify({'message': '状态是必填字段'}), 400
    
    if data['status'] not in ['booked', 'attended', 'absent', 'cancelled']:
        return jsonify({'message': '无效的状态值'}), 400
    
    # 如果状态变为'attended'，则减少剩余课程数
    if data['status'] == 'attended' and booking.status != 'attended':
        order.remaining_classes -= 1
        if order.remaining_classes < 0:
            order.remaining_classes = 0
    
    # 更新约课状态
    booking.status = data['status']
    
    db.session.commit()
    
    return jsonify({'message': '约课状态更新成功', 'booking': booking.to_dict()}), 200

@school_bp.route('/leave-requests', methods=['GET'])
@jwt_required()
def get_leave_requests():
    """获取请假列表"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取当前学校的所有课程
    courses = Course.query.filter_by(school_id=account.school_id).all()
    course_ids = [course.id for course in courses]
    
    # 获取这些课程的所有订单
    orders = CourseOrder.query.filter(CourseOrder.course_id.in_(course_ids)).all()
    order_ids = [order.id for order in orders]
    
    # 获取这些订单的所有约课记录
    bookings = Booking.query.filter(Booking.order_id.in_(order_ids)).all()
    booking_ids = [booking.id for booking in bookings]
    
    # 获取这些约课记录的所有请假申请
    leave_requests = LeaveRequest.query.filter(LeaveRequest.booking_id.in_(booking_ids)).all()
    
    return jsonify([leave_request.to_dict() for leave_request in leave_requests]), 200

@school_bp.route('/leave-requests/<int:request_id>/process', methods=['PUT'])
@jwt_required()
def process_leave_request(request_id):
    """处理请假申请"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取请假申请并验证是否属于当前学校
    leave_request = LeaveRequest.query.get_or_404(request_id)
    booking = Booking.query.get_or_404(leave_request.booking_id)
    order = CourseOrder.query.get_or_404(booking.order_id)
    course = Course.query.get_or_404(order.course_id)
    if course.school_id != account.school_id:
        return jsonify({'message': '无权处理该请假申请'}), 403
    
    data = request.get_json()
    
    # 验证状态值
    if 'status' not in data:
        return jsonify({'message': '状态是必填字段'}), 400
    
    if data['status'] not in ['approved', 'rejected']:
        return jsonify({'message': '无效的状态值'}), 400
    
    # 更新请假状态
    leave_request.status = data['status']
    leave_request.processed_by = account_id
    
    # 如果请假被批准，则更新约课状态为'cancelled'
    if data['status'] == 'approved':
        booking.status = 'cancelled'
    
    db.session.commit()
    
    return jsonify({'message': '请假申请处理成功', 'leave_request': leave_request.to_dict()}), 200

@school_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """获取订单列表"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取当前学校的所有课程
    courses = Course.query.filter_by(school_id=account.school_id).all()
    course_ids = [course.id for course in courses]
    
    # 获取这些课程的所有订单
    orders = CourseOrder.query.filter(CourseOrder.course_id.in_(course_ids)).all()
    
    return jsonify([order.to_dict() for order in orders]), 200

@school_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """获取订单详情"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取订单并验证是否属于当前学校
    order = CourseOrder.query.get_or_404(order_id)
    course = Course.query.get_or_404(order.course_id)
    if course.school_id != account.school_id:
        return jsonify({'message': '无权访问该订单'}), 403
    
    return jsonify(order.to_dict()), 200

@school_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """更新订单状态"""
    account_id = get_jwt_identity()
    account = SchoolAccount.query.get_or_404(account_id)
    
    # 获取订单并验证是否属于当前学校
    order = CourseOrder.query.get_or_404(order_id)
    course = Course.query.get_or_404(order.course_id)
    if course.school_id != account.school_id:
        return jsonify({'message': '无权修改该订单'}), 403
    
    data = request.get_json()
    
    # 验证状态值
    if 'status' not in data:
        return jsonify({'message': '状态是必填字段'}), 400
    
    if data['status'] not in ['pending', 'paid', 'cancelled']:
        return jsonify({'message': '无效的状态值'}), 400
    
    # 更新订单状态
    order.status = data['status']
    
    db.session.commit()
    
    return jsonify({'message': '订单状态更新成功', 'order': order.to_dict()}), 200