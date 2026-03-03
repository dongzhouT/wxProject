# 兴趣班管理微信小程序

## 项目简介

这是一个用于兴趣班信息管理的微信小程序系统，支持管理员、学校方和家长三种角色，实现了课程管理、学生管理、约课、请假等功能。

### 主要功能

1. **管理员功能**
   - 创建/管理学校账户
   - 系统配置
   - 数据统计

2. **学校方功能**
   - 管理家长账户
   - 课程管理（添加/编辑课表）
   - 消课操作
   - 学生出勤管理

3. **家长功能**
   - 查看课表
   - 请假申请
   - 约课
   - 查看剩余课程数
   - 接收通知

## 技术栈

- **前端**：微信小程序原生开发（WXML、WXSS、JavaScript）
- **后端**：Python Flask
- **数据库**：MySQL

## 项目结构

```
interest_class_manager/
├── backend/              # 后端代码
│   ├── app/              # 应用主目录
│   │   ├── api/          # API路由
│   │   ├── models/       # 数据模型
│   │   └── __init__.py   # 应用初始化
│   ├── config.py         # 配置文件
│   └── requirements.txt  # 依赖包列表
├── frontend/             # 前端代码
│   ├── pages/            # 页面
│   │   ├── admin/        # 管理员页面
│   │   ├── school/       # 学校方页面
│   │   ├── parent/       # 家长页面
│   │   └── common/       # 公共页面
│   ├── components/       # 组件
│   ├── utils/            # 工具函数
│   ├── services/         # 服务
│   ├── assets/           # 资源文件
│   ├── app.js            # 应用入口
│   ├── app.json          # 应用配置
│   └── app.wxss          # 全局样式
└── README.md             # 项目说明
```

## 快速开始

### 后端部署

1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

2. 配置数据库
```bash
# 修改config.py中的数据库配置
SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/dbname'
```

3. 运行应用
```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

### 前端开发

1. 下载并安装微信开发者工具
2. 导入frontend目录
3. 在app.js中配置API地址
```javascript
globalData: {
  baseUrl: 'https://your-api-domain.com/api' // 替换为实际的API地址
}
```
4. 编译并运行

## 数据库设计

系统包含以下主要数据表：
- admin: 管理员表
- school: 学校表
- school_account: 学校账户表
- parent: 家长表
- student: 学生表
- course_category: 课程类别表
- course: 课程表
- schedule: 课表安排表
- course_order: 课程订单表
- booking: 约课记录表
- leave_request: 请假记录表

详细的数据库结构请参考backend/app/models目录下的模型定义。

## API文档

系统提供了完整的RESTful API，包括：
- 管理员API: /api/admin/*
- 学校方API: /api/school/*
- 家长API: /api/parent/*

详细的API接口请参考backend/app/api目录下的路由定义。

## 注意事项

1. 本项目为演示版本，实际部署时请修改以下配置：
   - 数据库连接信息
   - JWT密钥
   - API地址

2. 家长登录需要配置微信小程序的AppID和AppSecret，并在后端实现微信登录验证。

3. 建议在生产环境中使用HTTPS协议。

## 许可证

MIT