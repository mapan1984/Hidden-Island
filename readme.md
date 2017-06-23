# My personal blog

### 预设环境变量

1. `FLASK_CONFIG`: 决定以何种模式运行，可选`development`, `testing`, `production`, `heroku`, `default`，默认值为`default`
2. `ADMIN_EMAIL`: 管理员的email，用于管理员登陆和管理员接收网站状态变化，网站初始时自动注册
3. `ADMIN_PASSWORD`: 管理员的password，用于管理员登陆，网站初始时自动注册
4. `MAIL_USERNAME`: 网站的email，用于向管理员以及用户发送邮件
5. `MAIL_PASSWORD`: 网站email密码，用于登陆为`MAIL_USERNAME`提供服务的email服务器
6. `SECRET_KEY`: 用户注册及提交表单时使用的加密key

### 文章

有两种发布文章的方式：

### 1. 利用网站给出的Markdown编辑器在线发布

有发布文章权限的用户可在网站的写作页面发布文章。与上一种方式不同，以此发布的文章为`name`赋值为`title`。

### 2. 上传文章的Markdown格式的文章到文章目录(只有管理员可用)

项目根目录下`./articles`为文章目录，保存Markdown格式的文章。

在`./articles`下的文章，其`name`为去后缀的文件名(为了找到源文件进行操作)，`title`在文章中以[特定格式](https://hidden-island.herokuapp.com/write-article)给定。

### 特性

- [x] 可以以Markdown的格式保存文章到文章目录，数据库中只存储文章信息，本地编辑，通过Git或网站接口的方式上传Markdown文件来发布文章
- [x] 可以通过网站提供的Markdown编辑器编写文章
- [x] 多用户博客，用户也可以为作者
- [x] 管理页面可以进行文章的增加、删除与更新等操作
- [x] 通过目录与标签对文章进行分类
- [ ] 支持按关键字查询相关文章
- [ ] 支持用户评论系统

