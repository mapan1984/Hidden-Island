---
title: blog config
date: Tue Jan 31 16:42:24 CST 2017
category: code
tag: flask
---

### 预设环境变量

1. `FLASK_CONFIG`: 决定以何种模式运行，可选`development`, `testing`, `production`, `heroku`, `default`，默认值为`default`
2. `ADMIN_EMAIL`: 管理员的email，用于管理员登陆和管理员接收网站状态变化，网站初始时自动注册
3. `ADMIN_PASSWORD`: 管理员的password，用于管理员登陆，网站初始时自动注册
4. `MAIL_USERNAME`: 网站的email，用于向管理员以及用户发送邮件
5. `MAIL_PASSWORD`: 网站email密码，用于登陆为`MAIL_USERNAME`提供服务的email服务器
6. `SECRET_KEY`: 用户注册及提交表单时使用的加密key

### 文章目录

项目根目录下`./articles`为文章目录，保存Markdown格式的文章；生成的HTML格式的文章保存在`./app/templates/articles`中。
