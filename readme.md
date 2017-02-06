# My personal blog

## Config

1. `FLASK_CONFIG`: 决定以何种模式运行，可选`development`, `testing`, `production`, `heroku`, `default`，默认值为`default`
2. `ADMIN_EMAIL`: 
3. `ADMIN_PASSWORD`
4. `MAIL_USERNAME`
5. `MAIL_PASSWORD`
6. `SECRET_KEY`

## Problems encoutered

[ ] 由于刚开始`./migrations/versions`目录是空的，部署到heroku时git不会将其上传，所以部署命令`python manage.py deploy`会失败
[x] `current_user`的属性由什么决定，似乎不是`models.py`中的`User`类决定的? `current_user`的属性时类属性，而不是对象属性
