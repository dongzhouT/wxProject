from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.admin import Admin
from app.models.school import School, SchoolAccount

# 创建蓝图
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
    
    admin = Admin.query.filter_by(username=username).first()
    
    if not admin or not admin.verify_password(password):
        return jsonify({'message': '用户名或密码错误'}), 401
    
    # 创建访问令牌
    access_token = create_access_token(identity=admin.id, additional_claims={'role': 'admin'})
    
    return jsonify({
        'access_token': access_token,
        'admin': admin.to_dict()
    }), 200

@admin_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_admin_profile():
    """获取管理员信息"""
    admin_id = get_jwt_identity()
    admin = Admin.query.get_or_404(admin_id)
    
    return jsonify(admin.to_dict()), 200

@admin_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_admin_profile():
    """更新管理员信息"""
    admin_id = get_jwt_identity()
    admin = Admin.query.get_or_404(admin_id)
    
    data = request.get_json()
    
    # 更新管理员信息
    if 'username' in data:
        admin.username = data['username']
    
    db.session.commit()
    
    return jsonify({'message': '管理员信息更新成功', 'admin': admin.to_dict()}), 200

@admin_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_admin_password():
    """修改管理员密码"""
    admin_id = get_jwt_identity()
    admin = Admin.query.get_or_404(admin_id)
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'message': '旧密码和新密码不能为空'}), 400
    
    if not admin.verify_password(old_password):
        return jsonify({'message': '旧密码错误'}), 401
    
    admin.password = new_password
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'}), 200

@admin_bp.route('/schools', methods=['GET'])
@jwt_required()
def get_schools():
    """获取学校列表"""
    schools = School.query.all()
    return jsonify([school.to_dict() for school in schools]), 200

@admin_bp.route('/schools', methods=['POST'])
@jwt_required()
def create_school():
    """创建学校"""
    admin_id = get_jwt_identity()
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['name', 'contact_person', 'contact_phone']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} 是必填字段'}), 400
    
    # 创建学校
    school = School(
        name=data['name'],
        contact_person=data['contact_person'],
        contact_phone=data['contact_phone'],
        address=data.get('address'),
        description=data.get('description'),
        created_by=admin_id
    )
    
    db.session.add(school)
    db.session.commit()
    
    return jsonify({'message': '学校创建成功', 'school': school.to_dict()}), 201

@admin_bp.route('/schools/<int:school_id>', methods=['GET'])
@jwt_required()
def get_school(school_id):
    """获取学校详情"""
    school = School.query.get_or_404(school_id)
    return jsonify(school.to_dict()), 200

@admin_bp.route('/schools/<int:school_id>', methods=['PUT'])
@jwt_required()
def update_school(school_id):
    """更新学校信息"""
    school = School.query.get_or_404(school_id)
    
    data = request.get_json()
    
    # 更新学校信息
    if 'name' in data:
        school.name = data['name']
    if 'contact_person' in data:
        school.contact_person = data['contact_person']
    if 'contact_phone' in data:
        school.contact_phone = data['contact_phone']
    if 'address' in data:
        school.address = data['address']
    if 'description' in data:
        school.description = data['description']
    
    db.session.commit()
    
    return jsonify({'message': '学校信息更新成功', 'school': school.to_dict()}), 200

@admin_bp.route('/schools/<int:school_id>', methods=['DELETE'])
@jwt_required()
def delete_school(school_id):
    """删除学校"""
    school = School.query.get_or_404(school_id)
    
    db.session.delete(school)
    db.session.commit()
    
    return jsonify({'message': '学校删除成功'}), 200

@admin_bp.route('/schools/<int:school_id>/accounts', methods=['GET'])
@jwt_required()
def get_school_accounts(school_id):
    """获取学校账户列表"""
    # 验证学校是否存在
    school = School.query.get_or_404(school_id)
    
    accounts = SchoolAccount.query.filter_by(school_id=school_id).all()
    return jsonify([account.to_dict() for account in accounts]), 200

@admin_bp.route('/schools/<int:school_id>/accounts', methods=['POST'])
@jwt_required()
def create_school_account(school_id):
    """创建学校账户"""
    # 验证学校是否存在
    school = School.query.get_or_404(school_id)
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['username', 'password', 'real_name', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} 是必填字段'}), 400
    
    # 检查用户名是否已存在
    existing_account = SchoolAccount.query.filter_by(username=data['username']).first()
    if existing_account:
        return jsonify({'message': '用户名已存在'}), 400
    
    # 创建学校账户
    account = SchoolAccount(
        school_id=school_id,
        username=data['username'],
        password=data['password'],
        real_name=data['real_name'],
        phone=data['phone'],
        role=data.get('role', 'staff')
    )
    
    db.session.add(account)
    db.session.commit()
    
    return jsonify({'message': '学校账户创建成功', 'account': account.to_dict()}), 201

@admin_bp.route('/accounts/<int:account_id>', methods=['PUT'])
@jwt_required()
def update_school_account(account_id):
    """更新学校账户"""
    account = SchoolAccount.query.get_or_404(account_id)
    
    data = request.get_json()
    
    # 更新账户信息
    if 'username' in data:
        # 检查新用户名是否已被其他账户使用
        existing_account = SchoolAccount.query.filter(SchoolAccount.username == data['username'], SchoolAccount.id != account_id).first()
        if existing_account:
            return jsonify({'message': '用户名已存在'}), 400
        account.username = data['username']
    if 'real_name' in data:
        account.real_name = data['real_name']
    if 'phone' in data:
        account.phone = data['phone']
    if 'role' in data:
        account.role = data['role']
    if 'password' in data:
        account.password = data['password']
    
    db.session.commit()
    
    return jsonify({'message': '学校账户更新成功', 'account': account.to_dict()}), 200

@admin_bp.route('/accounts/<int:account_id>', methods=['DELETE'])
@jwt_required()
def delete_school_account(account_id):
    """删除学校账户"""
    account = SchoolAccount.query.get_or_404(account_id)
    
    db.session.delete(account)
    db.session.commit()
    
    return jsonify({'message': '学校账户删除成功'}), 200

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """获取系统概览数据"""
    # 统计学校数量
    school_count = School.query.count()
    
    # 统计学校账户数量
    account_count = SchoolAccount.query.count()
    
    # 统计家长数量
    from app.models.parent import Parent
    parent_count = Parent.query.count()
    
    # 统计学生数量
    from app.models.parent import Student
    student_count = Student.query.count()
    
    # 统计课程数量
    from app.models.course import Course
    course_count = Course.query.count()
    
    # 统计订单数量
    from app.models.order import CourseOrder
    order_count = CourseOrder.query.count()
    
    return jsonify({
        'school_count': school_count,
        'account_count': account_count,
        'parent_count': parent_count,
        'student_count': student_count,
        'course_count': course_count,
        'order_count': order_count
    }), 200