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
            {'id': 1, 'name': '钢琴课', 'category': '音乐', 'price': 100, 'school_id': 1, 'schedule': ['周一', '周三', '周五'], 'teacher': '张老师', 'time': '09:00-10:00', 'max_students': 5, 'current_students': 2},
            {'id': 2, 'name': '绘画课', 'category': '美术', 'price': 80, 'school_id': 1, 'schedule': ['周二', '周四'], 'teacher': '李老师', 'time': '14:00-15:00', 'max_students': 8, 'current_students': 3},
            {'id': 3, 'name': '舞蹈课', 'category': '舞蹈', 'price': 90, 'school_id': 1, 'schedule': ['周六', '周日'], 'teacher': '王老师', 'time': '16:00-17:00', 'max_students': 10, 'current_students': 8}
        ]
        # 学生数据
        self.students = []
        # 订单数据
        self.orders = []

# 初始化模拟数据库
db = MockDB()

class MyHandler(http.server.BaseHTTPRequestHandler):
    def get_parameter(self, name):
        import urllib.parse
        if '?' in self.path:
            query_string = self.path.split('?')[1]
            params = urllib.parse.parse_qs(query_string)
            if name in params:
                return params[name][0]
        return None
    
    def do_GET(self):
        print(f"GET 请求路径: {self.path}")
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
        # 获取课程详情
        elif self.path.startswith('/api/school/courses/'):
            # 提取课程ID
            parts = self.path.split('/')
            if len(parts) > 4:
                course_id = int(parts[-1])
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
        # 获取课程列表
        elif self.path == '/api/school/courses' or self.path.startswith('/api/school/courses?'):
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
        # 获取学校家长列表
        elif self.path == '/api/school/parents' or self.path.startswith('/api/school/parents?'):
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
        # 获取订单详情
        elif self.path.startswith('/api/school/orders/'):
            order_id = self.path.split('/')[-1]
            # 在所有家长中查找订单
            found_order = None
            for parent in db.parents:
                if 'orders' in parent:
                    for order in parent['orders']:
                        if order['order_id'] == order_id:
                            found_order = order
                            break
                    if found_order:
                        break
            
            if found_order:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '获取订单详情成功',
                    'data': found_order
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 404,
                    'message': '订单不存在'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        # 获取学校家长详情
        elif self.path.startswith('/api/school/parents/'):
            parent_id = int(self.path.split('/')[-1])
            # 获取家长详情
            parent = next((p for p in db.parents if p['id'] == parent_id), None)
            if parent:
                # 确保家长有orders属性
                if 'orders' not in parent:
                    parent['orders'] = []
                
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
        # 家长端API
        elif self.path == '/api/parent/schedule':
            # 获取家长课表
            date = self.get_parameter('date')
            # 模拟数据
            schedule = [
                {'time': '09:00-10:00', 'courseName': '钢琴课', 'teacherName': '张老师', 'status': '已确认'},
                {'time': '14:00-15:00', 'courseName': '绘画课', 'teacherName': '李老师'}
            ]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 200,
                'message': '获取课表成功',
                'data': schedule
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif self.path == '/api/parent/courses':
            # 获取家长课程列表
            # 模拟数据
            courses = [
                {'id': 1, 'name': '钢琴课'},
                {'id': 2, 'name': '绘画课'},
                {'id': 3, 'name': '舞蹈课'}
            ]
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
        elif self.path == '/api/parent/leave' and self.command == 'POST':
            # 提交请假申请
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # 模拟处理
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 200,
                'message': '请假申请提交成功'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif self.path == '/api/parent/booking':
            if self.command == 'GET':
                # 获取可预约课程列表
                # 从课程数据中获取，计算剩余名额
                booking_courses = []
                for course in db.courses:
                    remaining = course.get('max_students', 10) - course.get('current_students', 0)
                    if remaining > 0:
                        booking_courses.append({
                            'id': course['id'],
                            'name': course['name'],
                            'time': course.get('time', '待定'),
                            'teacher': course.get('teacher', '待定'),
                            'remaining': remaining
                        })
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '获取可预约课程成功',
                    'data': booking_courses
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            elif self.command == 'POST':
                # 提交预约
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                course_id = data.get('course_id')
                # 查找课程并更新当前预约人数
                course_found = False
                for course in db.courses:
                    if course['id'] == course_id:
                        course_found = True
                        max_students = course.get('max_students', 10)
                        current_students = course.get('current_students', 0)
                        if current_students < max_students:
                            course['current_students'] = current_students + 1
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            response = {
                                'code': 200,
                                'message': '预约成功'
                            }
                            self.wfile.write(json.dumps(response).encode('utf-8'))
                        else:
                            self.send_response(400)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            response = {
                                'code': 400,
                                'message': '课程名额已满'
                            }
                            self.wfile.write(json.dumps(response).encode('utf-8'))
                        break
                if not course_found:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 404,
                        'message': '课程不存在'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
        elif self.path == '/api/parent/course-count':
            # 获取剩余课程
            # 模拟数据
            courses = [
                {'id': 1, 'name': '钢琴课', 'total': 20, 'remaining': 15},
                {'id': 2, 'name': '绘画课', 'total': 15, 'remaining': 10},
                {'id': 3, 'name': '舞蹈课', 'total': 10, 'remaining': 8}
            ]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 200,
                'message': '获取剩余课程成功',
                'data': courses
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif self.path == '/api/parent/notifications':
            # 获取通知
            # 模拟数据
            notifications = [
                {'id': 1, 'time': '2026-03-01 10:00', 'content': '您的孩子今天的钢琴课已完成', 'read': True},
                {'id': 2, 'time': '2026-03-02 14:00', 'content': '下周课程安排已更新', 'read': False},
                {'id': 3, 'time': '2026-03-03 09:00', 'content': '请及时确认本周的课程安排', 'read': False}
            ]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 200,
                'message': '获取通知成功',
                'data': notifications
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
        # 学校创建家长
        elif self.path == '/api/school/parents':
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
            
            # 检查是否需要创建订单
            if data.get('create_order', False):
                import time
                # 生成唯一订单号（时间戳）
                order_id = 'ORD' + str(int(time.time() * 1000))
                
                # 创建订单
                new_order = {
                    'id': 1,
                    'order_id': order_id,
                    'created_at': time.strftime('%Y-%m-%d', time.localtime()),
                    'type': data.get('order_type', '课时包'),
                    'status': data.get('order_status', '已支付'),
                    'amount': data.get('order_amount', 0),
                    'lesson_packages': []
                }
                
                # 添加课时包
                if data.get('lesson_count'):
                    new_order['lesson_packages'].append({
                        'id': 1,
                        'course_name': data.get('course_name', '通用课程'),
                        'total_lessons': data.get('lesson_count', 0),
                        'remaining_lessons': data.get('lesson_count', 0)
                    })
                
                new_parent['orders'].append(new_order)
            
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
        
        # 学校家长管理（更新和删除）
        elif self.path.startswith('/api/school/parents/'):
            parts = self.path.split('/')
            print(f"路径: {self.path}")
            print(f"parts: {parts}")
            print(f"parts长度: {len(parts)}")
            
            # 检查是否是添加订单的请求
            if len(parts) == 6 and parts[5] == 'orders' and self.command == 'POST':
                parent_id = int(parts[-2])
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # 查找家长
                parent = next((p for p in db.parents if p['id'] == parent_id), None)
                if parent:
                    # 确保家长有orders数组
                    if 'orders' not in parent:
                        parent['orders'] = []
                    
                    # 创建新订单
                    new_order = {
                        'id': len(parent['orders']) + 1,
                        'order_id': 'ORD' + str(parent_id) + str(len(parent['orders']) + 1).zfill(3),
                        'created_at': '2026-03-03',  # 实际应用中应该使用当前日期
                        'type': data.get('type', '课时包'),
                        'status': data.get('status', '已支付'),
                        'amount': data.get('amount', 0),
                        'lesson_packages': data.get('lesson_packages', [])
                    }
                    
                    parent['orders'].append(new_order)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '添加订单成功',
                        'data': new_order
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
            else:
                # 其他请求（PUT 和 DELETE）
                parent_id = int(parts[-1])
                if self.command == 'PUT':
                    # 更新家长
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))
                    
                    parent = next((p for p in db.parents if p['id'] == parent_id), None)
                    if parent:
                        # 移除订单相关参数，单独处理
                        create_order = data.pop('create_order', False)
                        order_amount = data.pop('order_amount', None)
                        lesson_count = data.pop('lesson_count', None)
                        course_name = data.pop('course_name', None)
                        
                        # 更新家长基本信息
                        parent.update(data)
                        
                        # 处理订单更新
                        if create_order:
                            import time
                            # 如果家长没有订单，创建新订单
                            if not parent.get('orders'):
                                parent['orders'] = []
                            
                            # 如果已有订单，更新第一个订单
                            if parent['orders']:
                                order = parent['orders'][0]
                                if order_amount is not None:
                                    order['amount'] = order_amount
                                if lesson_count:
                                    if not order.get('lesson_packages'):
                                        order['lesson_packages'] = []
                                    if order['lesson_packages']:
                                        lesson_package = order['lesson_packages'][0]
                                        lesson_package['total_lessons'] = lesson_count
                                        lesson_package['remaining_lessons'] = lesson_count
                                        if course_name:
                                            lesson_package['course_name'] = course_name
                                    else:
                                        # 创建新的课时包
                                        order['lesson_packages'].append({
                                            'id': 1,
                                            'course_name': course_name or '通用课程',
                                            'total_lessons': lesson_count,
                                            'remaining_lessons': lesson_count
                                        })
                            else:
                                # 创建新订单
                                order_id = 'ORD' + str(int(time.time() * 1000))
                                new_order = {
                                    'id': 1,
                                    'order_id': order_id,
                                    'created_at': time.strftime('%Y-%m-%d', time.localtime()),
                                    'type': '课时包',
                                    'status': '已支付',
                                    'amount': order_amount or 0,
                                    'lesson_packages': []
                                }
                                if lesson_count:
                                    new_order['lesson_packages'].append({
                                        'id': 1,
                                        'course_name': course_name or '通用课程',
                                        'total_lessons': lesson_count,
                                        'remaining_lessons': lesson_count
                                    })
                                parent['orders'].append(new_order)
                        
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
        
        # 订单管理接口
        elif self.path.startswith('/api/school/orders/'):
            order_id = self.path.split('/')[-1]
            
            if self.command == 'GET':
                # 获取订单详情
                # 在所有家长中查找订单
                found_order = None
                for parent in db.parents:
                    if 'orders' in parent:
                        for order in parent['orders']:
                            if order['order_id'] == order_id:
                                found_order = order
                                break
                        if found_order:
                            break
                
                if found_order:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '获取订单详情成功',
                        'data': found_order
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 404,
                        'message': '订单不存在'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
            elif self.command == 'PUT':
                # 更新订单
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # 在所有家长中查找订单
                found_order = None
                for parent in db.parents:
                    if 'orders' in parent:
                        for order in parent['orders']:
                            if order['order_id'] == order_id:
                                found_order = order
                                break
                        if found_order:
                            break
                
                if found_order:
                    # 更新订单信息
                    found_order.update({
                        'type': data.get('type', found_order.get('type')),
                        'status': data.get('status', found_order.get('status')),
                        'amount': data.get('amount', found_order.get('amount')),
                        'lesson_packages': data.get('lesson_packages', found_order.get('lesson_packages'))
                    })
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '更新订单成功',
                        'data': found_order
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 404,
                        'message': '订单不存在'
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
                    'price': data.get('price'),
                    'description': data.get('description'),
                    'schedule': data.get('schedule', []),
                    'teacher': data.get('teacher', '待定'),
                    'time': data.get('time', '待定'),
                    'max_students': data.get('max_students', 10),
                    'current_students': 0
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
        
        # 学校课程更新和删除
        elif self.path.startswith('/api/school/courses/'):
            try:
                course_id = int(self.path.split('/')[-1])
            except ValueError:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 404,
                    'message': '课程不存在'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
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
        # 更新订单信息（学校）
        if self.path.startswith('/api/school/orders/'):
            order_id = self.path.split('/')[-1]
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # 在所有家长中查找订单
            found_order = None
            for parent in db.parents:
                if 'orders' in parent:
                    for order in parent['orders']:
                        if order['order_id'] == order_id:
                            found_order = order
                            break
                    if found_order:
                        break
            
            if found_order:
                # 更新订单信息
                found_order.update({
                    'type': data.get('type', found_order.get('type')),
                    'status': data.get('status', found_order.get('status')),
                    'amount': data.get('amount', found_order.get('amount')),
                    'lesson_packages': data.get('lesson_packages', found_order.get('lesson_packages'))
                })
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '更新订单成功',
                    'data': found_order
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 404,
                    'message': '订单不存在'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        # 更新学校账户信息（管理员）
        elif self.path.startswith('/api/admin/accounts/'):
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
    
    def do_PUT(self):
        # 学校课程更新
        if self.path.startswith('/api/school/courses/'):
            try:
                course_id = int(self.path.split('/')[-1])
            except ValueError:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 404,
                    'message': '课程不存在'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
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
        # 学校课程删除
        if self.path.startswith('/api/school/courses/'):
            try:
                course_id = int(self.path.split('/')[-1])
            except ValueError:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 404,
                    'message': '课程不存在'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
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

with socketserver.TCPServer(('127.0.0.1', PORT), MyHandler) as httpd:
    print(f"服务器运行在 http://127.0.0.1:{PORT}")
    httpd.serve_forever()