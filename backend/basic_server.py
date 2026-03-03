import http.server
import socketserver
import json

PORT = 5001

# 模拟数据库
class MockDB:
    def __init__(self):
        # 管理员数据
        self.admins = [
            {'id': 1, 'username': 'admin', 'password': 'admin123', 'role': 'admin'}
        ]
        # 学校数据
        self.schools = [
            {'id': 1, 'name': '示例学校', 'contact_person': '张老师', 'contact_phone': '13800138000', 'account_limit': 3}
        ]
        # 学校账户数据
        self.school_accounts = [
            {'id': 1, 'school_id': 1, 'username': 'school', 'wechat_name': '李老师', 'password': 'school123', 'real_name': '李老师', 'phone': '13800138000', 'role': 'admin'}
        ]
        # 家长数据
        self.parents = [
            {'id': 1, 'openid': 'openid1', 'nickname': '家长1', 'phones': ['13800138001'], 'role': 'parent'},
            {'id': 2, 'openid': 'openid2', 'nickname': '家长2', 'phones': ['13800138002'], 'role': 'parent'},
            {'id': 3, 'openid': 'openid3', 'nickname': '家长3', 'phones': ['13800138003'], 'role': 'parent'}
        ]
        # 课程数据
        self.courses = [
            {'id': 1, 'name': '钢琴课', 'category': '音乐', 'price': 100, 'school_id': 1},
            {'id': 2, 'name': '绘画课', 'category': '美术', 'price': 80, 'school_id': 1},
            {'id': 3, 'name': '舞蹈课', 'category': '舞蹈', 'price': 90, 'school_id': 1}
        ]
        # 学生数据
        self.students = []
        # 订单数据
        self.orders = []

# 初始化模拟数据库
db = MockDB()

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # 健康检查
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 200,
                'message': '服务正常'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        # 获取课程列表
        elif self.path == '/api/school/courses':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 200,
                'message': '获取成功',
                'data': db.courses
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        # 获取学校列表（管理员）
        elif self.path == '/api/admin/schools':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 200,
                'message': '获取成功',
                'data': db.schools
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        # 获取学校账户列表（管理员）
        elif self.path == '/api/admin/accounts':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 200,
                'message': '获取成功',
                'data': db.school_accounts
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        # 获取系统概览数据（管理员）
        elif self.path == '/api/admin/dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 200,
                'message': '获取成功',
                'data': {
                    'school_count': len(db.schools),
                    'account_count': len(db.school_accounts),
                    'parent_count': len(db.parents),
                    'student_count': len(db.students),
                    'course_count': len(db.courses),
                    'order_count': len(db.orders)
                }
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 404,
                'message': '接口不存在'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_POST(self):
        # 管理员登录接口
        if self.path == '/api/admin/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            username = data.get('username')
            password = data.get('password')
            
            # 验证管理员登录
            admin = next((a for a in db.admins if a['username'] == username and a['password'] == password), None)
            if admin:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '登录成功',
                    'data': {
                        'token': 'mock-token',
                        'userInfo': admin
                    }
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 401,
                    'message': '用户名或密码错误'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        # 学校登录接口
        elif self.path == '/api/school/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            phone = data.get('phone')
            username = data.get('username')
            password = data.get('password')
            
            if phone:
                # 手机号登录，只允许管理员维护的学校账号登录
                print(f"学校登录尝试，手机号: {phone}")
                account = next((a for a in db.school_accounts if a['phone'] == phone), None)
                if account:
                    # 获取学校信息
                    school = next((s for s in db.schools if s['id'] == account['school_id']), None)
                    if school:
                        account['school_name'] = school['name']
                    
                    print(f"学校登录成功，用户: {account['real_name']}, 手机号: {phone}")
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '登录成功',
                        'data': {
                            'token': 'mock-token',
                            'userInfo': account
                        }
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    print(f"学校登录失败，手机号不存在: {phone}")
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 401,
                        'message': '手机号不存在，请到管理员处申请账号'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
            elif username and password:
                # 传统账号密码登录（保留兼容性）
                account = next((a for a in db.school_accounts if a['username'] == username and a['password'] == password), None)
                if account:
                    # 获取学校信息
                    school = next((s for s in db.schools if s['id'] == account['school_id']), None)
                    if school:
                        account['school_name'] = school['name']
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '登录成功',
                        'data': {
                            'token': 'mock-token',
                            'userInfo': account
                        }
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    # 模拟学校登录，使用任意用户名密码
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '登录成功',
                        'data': {
                            'token': 'mock-token',
                            'userInfo': {'username': username, 'role': 'school'}
                        }
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 401,
                    'message': '请输入手机号'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        # 家长登录接口
        elif self.path == '/api/parent/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            code = data.get('code')
            phone = data.get('phone', '未提供')
            
            # 模拟微信登录，使用任意code
            if code:
                print(f"家长登录尝试，code: {code}, 手机号: {phone}")
                # 检查是否已存在该家长
                parent = next((p for p in db.parents if p['openid'] == code), None)
                if not parent:
                    # 创建新家长
                    parent = {
                        'id': len(db.parents) + 1,
                        'openid': code,
                        'nickname': f'家长{len(db.parents) + 1}',
                        'phone': phone,
                        'role': 'parent'
                    }
                    db.parents.append(parent)
                else:
                    # 更新家长手机号
                    parent['phone'] = phone
                
                print(f"家长登录成功，用户: {parent['nickname']}, 手机号: {phone}")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '登录成功',
                    'data': {
                        'token': 'mock-token',
                        'userInfo': parent
                    }
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                print(f"家长登录失败，code为空")
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 401,
                    'message': '登录失败'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        # 学校获取家长列表
        elif self.path == '/api/school/parents':
            if self.command == 'GET':
                search = self.get_parameter('search')
                
                # 模拟家长数据
                parents = db.parents
                if search:
                    parents = [p for p in parents if search in p.get('nickname', '') or any(search in phone for phone in p.get('phones', []))]
                
                # 为每个家长添加订单数
                for parent in parents:
                    parent['order_count'] = len(parent.get('orders', []))
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '获取家长列表成功',
                    'data': parents
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            elif self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # 模拟创建家长
                new_parent = {
                    'id': len(db.parents) + 1,
                    'nickname': data.get('nickname'),
                    'phones': data.get('phones', []),
                    'remark': data.get('remark'),
                    'orders': []
                }
                db.parents.append(new_parent)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '创建家长成功',
                    'data': new_parent
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        # 学校家长详情和管理
        elif self.path.startswith('/api/school/parents/'):
            parent_id = int(self.path.split('/')[-1])
            if self.command == 'GET':
                # 获取家长详情
                parent = next((p for p in db.parents if p['id'] == parent_id), None)
                if parent:
                    # 模拟订单和课时包数据
                    if not parent.get('orders'):
                        parent['orders'] = [
                            {
                                'id': 1,
                                'order_id': 'ORD' + str(parent_id) + '001',
                                'created_at': '2026-03-01',
                                'status': '已支付',
                                'amount': 1000,
                                'lesson_packages': [
                                    {
                                        'id': 1,
                                        'course_name': '数学兴趣班',
                                        'total_lessons': 20,
                                        'remaining_lessons': 15
                                    }
                                ]
                            }
                        ]
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '获取家长详情成功',
                        'data': parent
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 404,
                        'message': '家长不存在'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
            elif self.command == 'PUT':
                # 更新家长
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                parent = next((p for p in db.parents if p['id'] == parent_id), None)
                if parent:
                    parent.update(data)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '更新家长成功',
                        'data': parent
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 404,
                        'message': '家长不存在'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
            elif self.command == 'DELETE':
                # 删除家长
                db.parents = [p for p in db.parents if p['id'] != parent_id]
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '删除家长成功'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        # 学校获取课程列表
        elif self.path == '/api/school/courses':
            if self.command == 'GET':
                search = self.get_parameter('search')
                
                # 模拟课程数据
                courses = db.courses
                if search:
                    courses = [c for c in courses if search in c.get('name', '')]
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '获取课程列表成功',
                    'data': courses
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            elif self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # 模拟创建课程
                new_course = {
                    'id': len(db.courses) + 1,
                    'name': data.get('name'),
                    'category': data.get('category'),
                    'price': data.get('price'),
                    'description': data.get('description')
                }
                db.courses.append(new_course)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '创建课程成功',
                    'data': new_course
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        # 学校课程详情和删除
        elif self.path.startswith('/api/school/courses/'):
            course_id = int(self.path.split('/')[-1])
            if self.command == 'GET':
                # 获取课程详情
                course = next((c for c in db.courses if c['id'] == course_id), None)
                if course:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '获取课程详情成功',
                        'data': course
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 404,
                        'message': '课程不存在'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
            elif self.command == 'PUT':
                # 更新课程
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                course = next((c for c in db.courses if c['id'] == course_id), None)
                if course:
                    course.update(data)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '更新课程成功',
                        'data': course
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 404,
                        'message': '课程不存在'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
            elif self.command == 'DELETE':
                # 删除课程
                db.courses = [c for c in db.courses if c['id'] != course_id]
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '删除课程成功'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        # 学校出勤管理
        elif self.path == '/api/school/attendance':
            if self.command == 'GET':
                course_id = self.get_parameter('courseId')
                date = self.get_parameter('date')
                
                # 模拟出勤数据
                attendance_list = [
                    {'id': 1, 'student_id': 'S001', 'student_name': '张三', 'status': '出勤'},
                    {'id': 2, 'student_id': 'S002', 'student_name': '李四', 'status': '出勤'},
                    {'id': 3, 'student_id': 'S003', 'student_name': '王五', 'status': '缺勤'}
                ]
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '获取出勤记录成功',
                    'data': attendance_list
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            elif self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # 模拟保存出勤记录
                print(f"保存出勤记录: {data}")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '保存出勤记录成功'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        # 学校获取学生列表
        elif self.path == '/api/school/students':
            if self.command == 'GET':
                # 模拟学生数据
                students = [
                    {'id': 1, 'name': '张三', 'student_id': 'S001'},
                    {'id': 2, 'name': '李四', 'student_id': 'S002'},
                    {'id': 3, 'name': '王五', 'student_id': 'S003'}
                ]
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '获取学生列表成功',
                    'data': students
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        # 学校消课操作
        elif self.path == '/api/school/consume':
            if self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # 模拟消课操作
                print(f"消课操作: {data}")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '消课成功'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        # 创建学校（管理员）
        elif self.path == '/api/admin/schools':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # 创建新学校
            new_school = {
                'id': len(db.schools) + 1,
                'name': data.get('name', '新学校'),
                'contact_person': data.get('contact_person', '联系人'),
                'contact_phone': data.get('contact_phone', '13800138000'),
                'address': data.get('address', ''),
                'description': data.get('description', ''),
                'account_limit': data.get('account_limit', 3)
            }
            db.schools.append(new_school)
            
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 201,
                'message': '学校创建成功',
                'data': new_school
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        # 创建学校账户（管理员）
        elif self.path == '/api/admin/accounts':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # 创建新学校账户
            new_account = {
                'id': len(db.school_accounts) + 1,
                'school_id': data.get('school_id', 1),
                'username': data.get('username', data.get('wechat_name', 'new_account')),
                'wechat_name': data.get('wechat_name', data.get('username', 'new_account')),
                'password': data.get('password', '123456'),
                'real_name': data.get('real_name', '姓名'),
                'phone': data.get('phone', '13800138000'),
                'role': data.get('role', 'staff')
            }
            db.school_accounts.append(new_account)
            
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 201,
                'message': '学校账户创建成功',
                'data': new_account
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 404,
                'message': '接口不存在'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
    def do_PUT(self):
        # 更新学校账户信息（管理员）
        if self.path.startswith('/api/admin/accounts/'):
            try:
                account_id = int(self.path.split('/')[-1])
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # 查找账户
                account = next((a for a in db.school_accounts if a['id'] == account_id), None)
                if account:
                    # 更新账户信息
                    if 'username' in data:
                        account['username'] = data['username']
                    if 'wechat_name' in data:
                        account['wechat_name'] = data['wechat_name']
                    if 'password' in data:
                        account['password'] = data['password']
                    if 'real_name' in data:
                        account['real_name'] = data['real_name']
                    if 'phone' in data:
                        account['phone'] = data['phone']
                    if 'role' in data:
                        account['role'] = data['role']
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '学校账户信息更新成功',
                        'data': account
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 404,
                        'message': '学校账户不存在'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 400,
                    'message': '请求参数错误'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        # 更新学校信息（管理员）
        elif self.path.startswith('/api/admin/schools/'):
            try:
                school_id = int(self.path.split('/')[-1])
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # 查找学校
                school = next((s for s in db.schools if s['id'] == school_id), None)
                if school:
                    # 更新学校信息
                    if 'name' in data:
                        school['name'] = data['name']
                    if 'contact_person' in data:
                        school['contact_person'] = data['contact_person']
                    if 'contact_phone' in data:
                        school['contact_phone'] = data['contact_phone']
                    if 'address' in data:
                        school['address'] = data['address']
                    if 'description' in data:
                        school['description'] = data['description']
                    if 'account_limit' in data:
                        school['account_limit'] = data['account_limit']
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '学校信息更新成功',
                        'data': school
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 404,
                        'message': '学校不存在'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 400,
                    'message': '请求参数错误'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 404,
                'message': '接口不存在'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_DELETE(self):
        # 删除学校（管理员）
        if self.path.startswith('/api/admin/schools/'):
            try:
                school_id = int(self.path.split('/')[-1])
                
                # 查找并删除学校
                school_index = next((i for i, s in enumerate(db.schools) if s['id'] == school_id), -1)
                if school_index != -1:
                    db.schools.pop(school_index)
                    
                    # 同时删除相关的学校账户
                    db.school_accounts = [a for a in db.school_accounts if a['school_id'] != school_id]
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '学校删除成功'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 404,
                        'message': '学校不存在'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 400,
                    'message': '请求参数错误'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        # 删除学校账户（管理员）
        elif self.path.startswith('/api/admin/accounts/'):
            try:
                account_id = int(self.path.split('/')[-1])
                
                # 查找并删除学校账户
                account_index = next((i for i, a in enumerate(db.school_accounts) if a['id'] == account_id), -1)
                if account_index != -1:
                    db.school_accounts.pop(account_index)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '学校账户删除成功'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 404,
                        'message': '学校账户不存在'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 400,
                    'message': '请求参数错误'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 404,
                'message': '接口不存在'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

with socketserver.TCPServer(('127.0.0.1', PORT), MyHandler) as httpd:
    print(f"服务器运行在 http://127.0.0.1:{PORT}")
    httpd.serve_forever()