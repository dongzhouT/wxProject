import http.server
import socketserver
import json
import urllib.parse
import sqlite3
import os
import time

PORT = 5001

# SQLite数据库操作类
class SQLiteDB:
    def __init__(self):
        self.db_file = 'interest_class_manager.db'
        self.init_db()
    
    def init_db(self):
        # 检查数据库文件是否存在
        db_exists = os.path.exists(self.db_file)
        
        # 连接数据库
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # 创建表结构
        # 管理员表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
        ''')
        
        # 学校表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS schools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact_person TEXT,
            contact_phone TEXT,
            account_limit INTEGER
        )
        ''')
        
        # 学校账户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS school_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_id INTEGER,
            username TEXT,
            wechat_name TEXT,
            password TEXT,
            real_name TEXT,
            phone TEXT,
            role TEXT,
            FOREIGN KEY (school_id) REFERENCES schools (id)
        )
        ''')
        
        # 家长表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS parents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            openid TEXT,
            nickname TEXT,
            phones TEXT,
            role TEXT,
            remark TEXT
        )
        ''')
        
        # 课程表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            price REAL,
            school_id INTEGER,
            schedule TEXT,
            teacher TEXT,
            time TEXT,
            max_students INTEGER,
            current_students INTEGER,
            FOREIGN KEY (school_id) REFERENCES schools (id)
        )
        ''')
        
        # 学生表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            parent_id INTEGER,
            FOREIGN KEY (parent_id) REFERENCES parents (id)
        )
        ''')
        
        # 订单表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            parent_id INTEGER,
            amount REAL,
            type TEXT,
            status TEXT,
            created_at TEXT,
            FOREIGN KEY (parent_id) REFERENCES parents (id)
        )
        ''')
        
        # 课时包表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS lesson_packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            course_name TEXT,
            total_lessons INTEGER,
            remaining_lessons INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
        ''')
        
        # 初始化数据
        if not db_exists:
            # 插入管理员数据
            cursor.execute('INSERT INTO admins (username, password, role) VALUES (?, ?, ?)', ('admin', 'admin123', 'admin'))
            
            # 插入学校数据
            cursor.execute('INSERT INTO schools (name, contact_person, contact_phone, account_limit) VALUES (?, ?, ?, ?)', 
                         ('示例学校', '张老师', '13800138000', 3))
            
            # 插入学校账户数据
            cursor.execute('INSERT INTO school_accounts (school_id, username, wechat_name, password, real_name, phone, role) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                         (1, 'school', '李老师', 'school123', '李老师', '13800138000', 'admin'))
            
            # 插入家长数据
            cursor.execute('INSERT INTO parents (openid, nickname, phones, role) VALUES (?, ?, ?, ?)', 
                         ('openid1', '家长1', '["13800138001"]', 'parent'))
            cursor.execute('INSERT INTO parents (openid, nickname, phones, role) VALUES (?, ?, ?, ?)', 
                         ('openid2', '家长2', '["13800138002"]', 'parent'))
            cursor.execute('INSERT INTO parents (openid, nickname, phones, role) VALUES (?, ?, ?, ?)', 
                         ('openid3', '家长3', '["13800138003"]', 'parent'))
            
            # 插入课程数据
            cursor.execute('INSERT INTO courses (name, category, price, school_id, schedule, teacher, time, max_students, current_students) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                         ('钢琴课', '音乐', 100, 1, '["周一", "周三", "周五"]', '张老师', '09:00-10:00', 5, 2))
            cursor.execute('INSERT INTO courses (name, category, price, school_id, schedule, teacher, time, max_students, current_students) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                         ('绘画课', '美术', 80, 1, '["周二", "周四"]', '李老师', '14:00-15:00', 8, 3))
            cursor.execute('INSERT INTO courses (name, category, price, school_id, schedule, teacher, time, max_students, current_students) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                         ('舞蹈课', '舞蹈', 90, 1, '["周六", "周日"]', '王老师', '16:00-17:00', 10, 8))
        
        # 提交并关闭连接
        conn.commit()
        conn.close()
    
    # 通用查询方法
    def query(self, sql, params=()):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchall()
        conn.close()
        return result
    
    # 通用执行方法
    def execute(self, sql, params=()):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id
    
    # 管理员相关方法
    def get_admin(self, username, password):
        admins = self.query('SELECT * FROM admins WHERE username = ? AND password = ?', (username, password))
        if admins:
            admin = admins[0]
            return {
                'id': admin['id'],
                'username': admin['username'],
                'password': admin['password'],
                'role': admin['role']
            }
        return None
    
    # 学校相关方法
    def get_schools(self):
        schools = self.query('SELECT * FROM schools')
        result = []
        for school in schools:
            result.append({
                'id': school['id'],
                'name': school['name'],
                'contact_person': school['contact_person'],
                'contact_phone': school['contact_phone'],
                'account_limit': school['account_limit']
            })
        return result
    
    def get_school(self, school_id):
        schools = self.query('SELECT * FROM schools WHERE id = ?', (school_id,))
        if schools:
            school = schools[0]
            return {
                'id': school['id'],
                'name': school['name'],
                'contact_person': school['contact_person'],
                'contact_phone': school['contact_phone'],
                'account_limit': school['account_limit']
            }
        return None
    
    def create_school(self, data):
        school_id = self.execute(
            'INSERT INTO schools (name, contact_person, contact_phone, account_limit) VALUES (?, ?, ?, ?)',
            (data.get('name'), data.get('contact_person'), data.get('contact_phone'), data.get('account_limit', 3))
        )
        return self.get_school(school_id)
    
    def update_school(self, school_id, data):
        self.execute(
            'UPDATE schools SET name = ?, contact_person = ?, contact_phone = ?, account_limit = ? WHERE id = ?',
            (data.get('name'), data.get('contact_person'), data.get('contact_phone'), data.get('account_limit', 3), school_id)
        )
        return self.get_school(school_id)
    
    # 学校账户相关方法
    def get_school_accounts(self):
        accounts = self.query('SELECT * FROM school_accounts')
        result = []
        for account in accounts:
            result.append({
                'id': account['id'],
                'school_id': account['school_id'],
                'username': account['username'],
                'wechat_name': account['wechat_name'],
                'password': account['password'],
                'real_name': account['real_name'],
                'phone': account['phone'],
                'role': account['role']
            })
        return result
    
    def get_school_account_by_phone(self, phone):
        accounts = self.query('SELECT * FROM school_accounts WHERE phone = ?', (phone,))
        if accounts:
            account = accounts[0]
            result = {
                'id': account['id'],
                'school_id': account['school_id'],
                'username': account['username'],
                'wechat_name': account['wechat_name'],
                'password': account['password'],
                'real_name': account['real_name'],
                'phone': account['phone'],
                'role': account['role']
            }
            # 获取学校信息
            school = self.get_school(account['school_id'])
            if school:
                result['school_name'] = school['name']
            return result
        return None
    
    def get_school_account_by_username(self, username, password):
        accounts = self.query('SELECT * FROM school_accounts WHERE username = ? AND password = ?', (username, password))
        if accounts:
            account = accounts[0]
            result = {
                'id': account['id'],
                'school_id': account['school_id'],
                'username': account['username'],
                'wechat_name': account['wechat_name'],
                'password': account['password'],
                'real_name': account['real_name'],
                'phone': account['phone'],
                'role': account['role']
            }
            # 获取学校信息
            school = self.get_school(account['school_id'])
            if school:
                result['school_name'] = school['name']
            return result
        return None
    
    # 家长相关方法
    def get_parents(self):
        parents = self.query('SELECT * FROM parents')
        result = []
        for parent in parents:
            parent_data = {
                'id': parent['id'],
                'openid': parent['openid'],
                'nickname': parent['nickname'],
                'phones': json.loads(parent['phones']) if parent['phones'] else [],
                'role': parent['role'],
                'remark': parent['remark']
            }
            # 添加订单数
            orders = self.query('SELECT * FROM orders WHERE parent_id = ?', (parent['id'],))
            parent_data['order_count'] = len(orders)
            result.append(parent_data)
        return result
    
    def get_parent(self, parent_id):
        parents = self.query('SELECT * FROM parents WHERE id = ?', (parent_id,))
        if parents:
            parent = parents[0]
            parent_data = {
                'id': parent['id'],
                'openid': parent['openid'],
                'nickname': parent['nickname'],
                'phones': json.loads(parent['phones']) if parent['phones'] else [],
                'role': parent['role'],
                'remark': parent['remark'],
                'orders': []
            }
            # 获取订单
            orders = self.query('SELECT * FROM orders WHERE parent_id = ?', (parent['id'],))
            for order in orders:
                order_data = {
                    'id': order['id'],
                    'order_id': order['order_id'],
                    'created_at': order['created_at'],
                    'type': order['type'],
                    'status': order['status'],
                    'amount': order['amount'],
                    'lesson_packages': []
                }
                # 获取课时包
                lesson_packages = self.query('SELECT * FROM lesson_packages WHERE order_id = ?', (order['id'],))
                for lp in lesson_packages:
                    order_data['lesson_packages'].append({
                        'id': lp['id'],
                        'course_name': lp['course_name'],
                        'total_lessons': lp['total_lessons'],
                        'remaining_lessons': lp['remaining_lessons']
                    })
                parent_data['orders'].append(order_data)
            return parent_data
        return None
    
    def get_parent_by_openid(self, openid):
        parents = self.query('SELECT * FROM parents WHERE openid = ?', (openid,))
        if parents:
            parent = parents[0]
            return {
                'id': parent['id'],
                'openid': parent['openid'],
                'nickname': parent['nickname'],
                'phones': json.loads(parent['phones']) if parent['phones'] else [],
                'role': parent['role']
            }
        return None
    
    def create_parent(self, data):
        phones = json.dumps(data.get('phones', []))
        parent_id = self.execute(
            'INSERT INTO parents (nickname, phones, remark, role) VALUES (?, ?, ?, ?)',
            (data.get('nickname'), phones, data.get('remark'), 'parent')
        )
        return self.get_parent(parent_id)
    
    def update_parent(self, parent_id, data):
        phones = json.dumps(data.get('phones', []))
        self.execute(
            'UPDATE parents SET nickname = ?, phones = ?, remark = ? WHERE id = ?',
            (data.get('nickname'), phones, data.get('remark'), parent_id)
        )
        return self.get_parent(parent_id)
    
    def delete_parent(self, parent_id):
        # 删除相关的课时包
        orders = self.query('SELECT id FROM orders WHERE parent_id = ?', (parent_id,))
        for order in orders:
            self.execute('DELETE FROM lesson_packages WHERE order_id = ?', (order['id'],))
        # 删除相关的订单
        self.execute('DELETE FROM orders WHERE parent_id = ?', (parent_id,))
        # 删除家长
        self.execute('DELETE FROM parents WHERE id = ?', (parent_id,))
        return True
    
    # 订单相关方法
    def create_order(self, parent_id, data):
        order_id = 'ORD' + str(int(time.time() * 1000))
        created_at = time.strftime('%Y-%m-%d', time.localtime())
        order_id_db = self.execute(
            'INSERT INTO orders (order_id, parent_id, amount, type, status, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            (order_id, parent_id, data.get('amount', 0), data.get('type', '课时包'), data.get('status', '已支付'), created_at)
        )
        
        # 创建课时包
        for lp in data.get('lesson_packages', []):
            self.execute(
                'INSERT INTO lesson_packages (order_id, course_name, total_lessons, remaining_lessons) VALUES (?, ?, ?, ?)',
                (order_id_db, lp.get('course_name'), lp.get('total_lessons'), lp.get('remaining_lessons'))
            )
        
        # 获取完整订单信息
        order = self.query('SELECT * FROM orders WHERE id = ?', (order_id_db,))[0]
        order_data = {
            'id': order['id'],
            'order_id': order['order_id'],
            'created_at': order['created_at'],
            'type': order['type'],
            'status': order['status'],
            'amount': order['amount'],
            'lesson_packages': []
        }
        lesson_packages = self.query('SELECT * FROM lesson_packages WHERE order_id = ?', (order_id_db,))
        for lp in lesson_packages:
            order_data['lesson_packages'].append({
                'id': lp['id'],
                'course_name': lp['course_name'],
                'total_lessons': lp['total_lessons'],
                'remaining_lessons': lp['remaining_lessons']
            })
        return order_data
    
    def get_order(self, order_id):
        orders = self.query('SELECT * FROM orders WHERE order_id = ?', (order_id,))
        if orders:
            order = orders[0]
            order_data = {
                'id': order['id'],
                'order_id': order['order_id'],
                'created_at': order['created_at'],
                'type': order['type'],
                'status': order['status'],
                'amount': order['amount'],
                'lesson_packages': []
            }
            lesson_packages = self.query('SELECT * FROM lesson_packages WHERE order_id = ?', (order['id'],))
            for lp in lesson_packages:
                order_data['lesson_packages'].append({
                    'id': lp['id'],
                    'course_name': lp['course_name'],
                    'total_lessons': lp['total_lessons'],
                    'remaining_lessons': lp['remaining_lessons']
                })
            return order_data
        return None
    
    def update_order(self, order_id, data):
        order = self.query('SELECT * FROM orders WHERE order_id = ?', (order_id,))
        if order:
            order_id_db = order[0]['id']
            self.execute(
                'UPDATE orders SET type = ?, status = ?, amount = ? WHERE id = ?',
                (data.get('type'), data.get('status'), data.get('amount'), order_id_db)
            )
            
            # 更新课时包
            self.execute('DELETE FROM lesson_packages WHERE order_id = ?', (order_id_db,))
            for lp in data.get('lesson_packages', []):
                self.execute(
                    'INSERT INTO lesson_packages (order_id, course_name, total_lessons, remaining_lessons) VALUES (?, ?, ?, ?)',
                    (order_id_db, lp.get('course_name'), lp.get('total_lessons'), lp.get('remaining_lessons'))
                )
            return self.get_order(order_id)
        return None
    
    # 课程相关方法
    def get_courses(self):
        courses = self.query('SELECT * FROM courses')
        result = []
        for course in courses:
            result.append({
                'id': course['id'],
                'name': course['name'],
                'category': course['category'],
                'price': course['price'],
                'school_id': course['school_id'],
                'schedule': json.loads(course['schedule']) if course['schedule'] else [],
                'teacher': course['teacher'],
                'time': course['time'],
                'max_students': course['max_students'],
                'current_students': course['current_students']
            })
        return result
    
    def get_course(self, course_id):
        courses = self.query('SELECT * FROM courses WHERE id = ?', (course_id,))
        if courses:
            course = courses[0]
            return {
                'id': course['id'],
                'name': course['name'],
                'category': course['category'],
                'price': course['price'],
                'school_id': course['school_id'],
                'schedule': json.loads(course['schedule']) if course['schedule'] else [],
                'teacher': course['teacher'],
                'time': course['time'],
                'max_students': course['max_students'],
                'current_students': course['current_students']
            }
        return None
    
    def create_course(self, data):
        schedule = json.dumps(data.get('schedule', []))
        course_id = self.execute(
            'INSERT INTO courses (name, category, price, school_id, schedule, teacher, time, max_students, current_students) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (data.get('name'), data.get('category'), data.get('price'), 1, schedule, data.get('teacher', '待定'), data.get('time', '待定'), data.get('max_students', 10), 0)
        )
        return self.get_course(course_id)
    
    def update_course(self, course_id, data):
        schedule = json.dumps(data.get('schedule', []))
        self.execute(
            'UPDATE courses SET name = ?, category = ?, price = ?, schedule = ?, teacher = ?, time = ?, max_students = ? WHERE id = ?',
            (data.get('name'), data.get('category'), data.get('price'), schedule, data.get('teacher', '待定'), data.get('time', '待定'), data.get('max_students', 10), course_id)
        )
        return self.get_course(course_id)
    
    def delete_course(self, course_id):
        self.execute('DELETE FROM courses WHERE id = ?', (course_id,))
        return True
    
    def update_course_students(self, course_id, increment=True):
        course = self.get_course(course_id)
        if course:
            current = course['current_students']
            if increment:
                new_count = current + 1
            else:
                new_count = max(0, current - 1)
            self.execute('UPDATE courses SET current_students = ? WHERE id = ?', (new_count, course_id))
            return True
        return False

# 初始化SQLite数据库
db = SQLiteDB()

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
                try:
                    course_id = int(parts[-1])
                    # 获取课程详情
                    course = db.get_course(course_id)
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
        # 获取课程列表
        elif self.path == '/api/school/courses' or self.path.startswith('/api/school/courses?'):
            search = self.get_parameter('search')
            
            # 获取课程列表
            courses = db.get_courses()
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
            
            # 获取家长列表
            parents = db.get_parents()
            if search:
                parents = [p for p in parents if search in p.get('nickname', '') or any(search in phone for phone in p.get('phones', []))]
            
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
            # 获取订单详情
            order = db.get_order(order_id)
            if order:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '获取订单详情成功',
                    'data': order
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
            parts = self.path.split('/')
            if len(parts) > 4:
                try:
                    parent_id = int(parts[-1])
                    # 获取家长详情
                    parent = db.get_parent(parent_id)
                    if parent:
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
                except ValueError:
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
                'data': db.get_schools()
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
                'data': db.get_school_accounts()
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
                    'school_count': len(db.get_schools()),
                    'account_count': len(db.get_school_accounts()),
                    'parent_count': len(db.get_parents()),
                    'student_count': 0,  # 暂时返回0
                    'course_count': len(db.get_courses()),
                    'order_count': 0  # 暂时返回0
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
        elif self.path == '/api/parent/booking':
            if self.command == 'GET':
                # 获取可预约课程列表
                # 从课程数据中获取，计算剩余名额
                booking_courses = []
                for course in db.get_courses():
                    remaining = course.get('max_students', 10) - course.get('current_students', 0)
                    # 构建完整的上课时间信息
                    schedule = course.get('schedule', [])
                    time = course.get('time', '待定')
                    full_schedule = []
                    for day in schedule:
                        full_schedule.append(f"{day} {time}")
                    
                    booking_courses.append({
                        'id': course['id'],
                        'name': course['name'],
                        'schedule': full_schedule,
                        'time': time,
                        'teacher': course.get('teacher', '待定'),
                        'remaining': remaining,
                        'max_students': course.get('max_students', 10),
                        'current_students': course.get('current_students', 0)
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
            admin = db.get_admin(username, password)
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
        # 管理员创建学校
        elif self.path == '/api/admin/schools' and self.command == 'POST':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # 创建学校
            new_school = db.create_school({
                'name': data.get('name'),
                'contact_person': data.get('contact_person'),
                'contact_phone': data.get('contact_phone'),
                'account_limit': data.get('account_limit', 3)
            })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'code': 200,
                'message': '创建学校成功',
                'data': new_school
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
                account = db.get_school_account_by_phone(phone)
                if account:
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
                account = db.get_school_account_by_username(username, password)
                if account:
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
                parent = db.get_parent_by_openid(code)
                if not parent:
                    # 创建新家长
                    new_parent = db.create_parent({
                        'nickname': f'家长{len(db.get_parents()) + 1}',
                        'phones': [phone],
                        'remark': ''
                    })
                    # 更新openid
                    conn = sqlite3.connect(db.db_file)
                    cursor = conn.cursor()
                    cursor.execute('UPDATE parents SET openid = ? WHERE id = ?', (code, new_parent['id']))
                    conn.commit()
                    conn.close()
                    parent = db.get_parent(new_parent['id'])
                else:
                    # 更新家长手机号
                    conn = sqlite3.connect(db.db_file)
                    cursor = conn.cursor()
                    phones = json.dumps([phone])
                    cursor.execute('UPDATE parents SET phones = ? WHERE id = ?', (phones, parent['id']))
                    conn.commit()
                    conn.close()
                    parent = db.get_parent(parent['id'])
                
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
            
            # 创建家长
            new_parent = db.create_parent({
                'nickname': data.get('nickname'),
                'phones': data.get('phones', []),
                'remark': data.get('remark')
            })
            
            # 检查是否需要创建订单
            if data.get('create_order', False):
                # 创建订单
                order_data = {
                    'amount': data.get('order_amount', 0),
                    'type': data.get('order_type', '课时包'),
                    'status': data.get('order_status', '已支付'),
                    'lesson_packages': []
                }
                
                # 添加课时包
                if data.get('lesson_count'):
                    order_data['lesson_packages'].append({
                        'course_name': data.get('course_name', '通用课程'),
                        'total_lessons': data.get('lesson_count', 0),
                        'remaining_lessons': data.get('lesson_count', 0)
                    })
                
                db.create_order(new_parent['id'], order_data)
                # 重新获取家长信息，包含订单
                new_parent = db.get_parent(new_parent['id'])
            
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
        # 学校创建课程
        elif self.path == '/api/school/courses':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # 创建课程
            new_course = db.create_course({
                'name': data.get('name'),
                'category': data.get('category'),
                'price': data.get('price'),
                'schedule': data.get('schedule', []),
                'teacher': data.get('teacher', '待定'),
                'time': data.get('time', '待定'),
                'max_students': data.get('max_students', 10)
            })
            
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
        # 学校家长管理（更新和删除）
        elif self.path.startswith('/api/school/parents/'):
            parts = self.path.split('/')
            print(f"路径: {self.path}")
            print(f"parts: {parts}")
            print(f"parts长度: {len(parts)}")
            
            # 检查是否是添加订单的请求
            if len(parts) == 6 and parts[5] == 'orders' and self.command == 'POST':
                try:
                    parent_id = int(parts[-2])
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))
                    
                    # 创建订单
                    new_order = db.create_order(parent_id, {
                        'amount': data.get('amount', 0),
                        'type': data.get('type', '课时包'),
                        'status': data.get('status', '已支付'),
                        'lesson_packages': data.get('lesson_packages', [])
                    })
                    
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
                except ValueError:
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
                try:
                    parent_id = int(parts[-1])
                    if self.command == 'PUT':
                        # 更新家长
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)
                        data = json.loads(post_data.decode('utf-8'))
                        
                        # 移除订单相关参数，单独处理
                        create_order = data.pop('create_order', False)
                        order_amount = data.pop('order_amount', None)
                        lesson_count = data.pop('lesson_count', None)
                        course_name = data.pop('course_name', None)
                        
                        # 更新家长基本信息
                        parent = db.update_parent(parent_id, data)
                        
                        # 处理订单更新
                        if create_order:
                            # 如果家长没有订单，创建新订单
                            if not parent.get('orders'):
                                order_data = {
                                    'amount': order_amount or 0,
                                    'type': '课时包',
                                    'status': '已支付',
                                    'lesson_packages': []
                                }
                                if lesson_count:
                                    order_data['lesson_packages'].append({
                                        'course_name': course_name or '通用课程',
                                        'total_lessons': lesson_count,
                                        'remaining_lessons': lesson_count
                                    })
                                db.create_order(parent_id, order_data)
                            else:
                                # 如果已有订单，更新第一个订单
                                order = parent['orders'][0]
                                order_data = {
                                    'type': order.get('type', '课时包'),
                                    'status': order.get('status', '已支付'),
                                    'amount': order_amount if order_amount is not None else order.get('amount', 0),
                                    'lesson_packages': []
                                }
                                if lesson_count:
                                    order_data['lesson_packages'].append({
                                        'course_name': course_name or '通用课程',
                                        'total_lessons': lesson_count,
                                        'remaining_lessons': lesson_count
                                    })
                                db.update_order(order['order_id'], order_data)
                            # 重新获取家长信息，包含订单
                            parent = db.get_parent(parent_id)
                        
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
                    elif self.command == 'DELETE':
                        # 删除家长
                        db.delete_parent(parent_id)
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        response = {
                            'code': 200,
                            'message': '删除家长成功'
                        }
                        self.wfile.write(json.dumps(response).encode('utf-8'))
                except ValueError:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 404,
                        'message': '家长不存在'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
        # 订单管理接口
        elif self.path.startswith('/api/school/orders/'):
            order_id = self.path.split('/')[-1]
            
            if self.command == 'PUT':
                # 更新订单
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # 更新订单
                updated_order = db.update_order(order_id, {
                    'type': data.get('type'),
                    'status': data.get('status'),
                    'amount': data.get('amount'),
                    'lesson_packages': data.get('lesson_packages', [])
                })
                
                if updated_order:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '更新订单成功',
                        'data': updated_order
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
        # 家长提交请假申请
        elif self.path == '/api/parent/leave':
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
        # 家长提交预约
        elif self.path == '/api/parent/booking' and self.command == 'POST':
            # 提交预约
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            course_id = data.get('course_id')
            # 查找课程并更新当前预约人数
            course = db.get_course(course_id)
            if course:
                max_students = course.get('max_students', 10)
                current_students = course.get('current_students', 0)
                if current_students < max_students:
                    # 更新课程的当前学生数
                    db.update_course_students(course_id, True)
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
        # 家长取消预约
        elif self.path == '/api/parent/booking/cancel' and self.command == 'POST':
            # 取消预约
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            course_id = data.get('course_id')
            # 查找课程并更新当前预约人数
            course = db.get_course(course_id)
            if course:
                current_students = course.get('current_students', 0)
                if current_students > 0:
                    # 更新课程的当前学生数
                    db.update_course_students(course_id, False)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '取消预约成功'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 400,
                        'message': '没有可取消的预约'
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
    
    def do_PUT(self):
        # 管理员更新学校信息
        if self.path.startswith('/api/admin/schools/'):
            try:
                school_id = int(self.path.split('/')[-1])
                # 更新学校
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # 更新学校
                updated_school = db.update_school(school_id, {
                    'name': data.get('name'),
                    'contact_person': data.get('contact_person'),
                    'contact_phone': data.get('contact_phone'),
                    'account_limit': data.get('account_limit', 3)
                })
                
                if updated_school:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '更新学校成功',
                        'data': updated_school
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
            except ValueError:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 404,
                    'message': '学校不存在'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        # 学校课程更新
        elif self.path.startswith('/api/school/courses/'):
            try:
                course_id = int(self.path.split('/')[-1])
                # 更新课程
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # 更新课程
                updated_course = db.update_course(course_id, {
                    'name': data.get('name'),
                    'category': data.get('category'),
                    'price': data.get('price'),
                    'schedule': data.get('schedule', []),
                    'teacher': data.get('teacher', '待定'),
                    'time': data.get('time', '待定'),
                    'max_students': data.get('max_students', 10)
                })
                
                if updated_course:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        'code': 200,
                        'message': '更新课程成功',
                        'data': updated_course
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
                # 删除课程
                db.delete_course(course_id)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'code': 200,
                    'message': '删除课程成功'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
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
