from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from datetime import timedelta

# 初始化数据库
db = SQLAlchemy()
# 初始化JWT
jwt = JWTManager()

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 配置应用
    app.config.from_object('config.Config')
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # 注册蓝图
    from app.api.admin import admin_bp
    from app.api.school import school_bp
    from app.api.parent import parent_bp
    
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(school_bp, url_prefix='/api/school')
    app.register_blueprint(parent_bp, url_prefix='/api/parent')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 添加默认管理员账户（如果不存在）
    from app.models.admin import Admin
    if not Admin.query.first():
        admin = Admin(username='admin', password='admin123')
        db.session.add(admin)
        db.session.commit()
    
    return app