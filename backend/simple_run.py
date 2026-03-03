from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# 内存存储
users = {
    'admin': {'username': 'admin', 'password': 'admin123', 'role': 'admin'}
}

# 模拟数据
courses = [
    {'id': 1, 'name': '钢琴课', 'category': '音乐', 'price': 100},
    {'id': 2, 'name': '绘画课', 'category': '美术', 'price': 80},
    {'id': 3, 'name': '舞蹈课', 'category': '舞蹈', 'price': 90}
]

# 登录接口
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in users and users[username]['password'] == password:
        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': 'mock-token',
                'userInfo': users[username]
            }
        })
    else:
        return jsonify({
            'code': 401,
            'message': '用户名或密码错误'
        })

# 获取课程列表
@app.route('/api/school/courses', methods=['GET'])
def get_courses():
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': courses
    })

# 健康检查
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'code': 200,
        'message': '服务正常'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)