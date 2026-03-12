# 基于 Django 的学生管理系统

这是一个面向网页端的学生管理系统，基于 Django 构建，适合课程设计、教学演示和基础后台管理场景。

项目提供管理员注册与登录、学生信息新增、编辑、删除、详情查看、条件筛选、分页排序以及首页统计面板等功能，帮助用户完成学生档案的日常维护。

## 功能特性

- 管理员注册、登录、退出
- 学生信息增删改查
- 按学号、姓名、班级筛选
- 学生列表分页与排序
- 首页班级分布可视化统计
- 桌面端界面优化与统一样式

## 技术栈

- Python
- Django
- SQLite
- HTML + CSS

## 运行方式

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
python manage.py migrate
python manage.py runserver
```

访问本地地址后即可使用系统。
