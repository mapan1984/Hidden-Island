# My personal blog

使用`flask`开发的博客。

有关设置、部署及功能见[wiki](https://github.com/mapan1984/Hidden-Island/wiki)。

## 功能

- [x] 方便的文章发布方式
- [x] 通过目录、标签、发布日期对文章进行分类
- [x] 支持按关键字查询相关文章
- [x] 支持用户评论与评分
- [x] 相关文章推荐
- [x] 使用Docker进行部署
- [x] celery后台任务

## 依赖服务

* 数据库：MySQL 或者 PostgreSQL
* 文章相似度存储/Celery 队列：Redis

## 配置/环境变量

利用 `.flaskenv` 和 `.env` 2 个文件管理项目依赖的环境变量

### flask

见 `.flaskenv` 文件：
1. `FLASK_APP`
2. `FLASK_ENV`: 决定以何种模式运行，可选 development, testing, production, heroku, docker, 默认值 production 模式
3. `SECRET_KEY`

### 邮件

见 `.env` 文件：
* `ADMIN_EMAIL`：管理员邮件地址，注册用
* `ADMIN_PASSWORD`：管理员邮件密码，注册用

* `MAIL_SENDER`：网站的邮件地址，用于向用户及管理员发送邮件
* `SENDGRID_API_KEY`: SendGrid's api key，利用 SendGrid 提供的邮件服务

### 数据库

不同类型数据库 url 示例如下：
1. `postgresql://${USERNAME}:${PASSWORD}@${HOST}:5432/${DATABASE}`
2. `mysql+pymysql://${USERNAME}:${PASSWORD}@{HOST}/${DATABASE}`

见 `.env` 文件，需要配置的环境变量如下：
* `DATABASE_URL`: (可选)网站 production, heroku, docker 模式下数据库地址
* `DEV_DATABASE_URL`：(可选)网站 development 模式下数据库地址
* `TEST_DATABASE_URL`：(可选)网站 testing 模式下数据库地址

### Redis

项目直接使用 redis 服务，同时 celery 任务队列也依赖 redis，目前配置是使用同一个 redis 服务，不同用途使用不同的 database

redis url 示例：`redis://:{PASSWORD}@{HOST}:6379/${DATABASE}`

见 `.env` 文件，需要配置的环境变量如下：
* `REDIS_URL`: 直接使用的 redis 服务地址
* `CELERY_BROKER_URL`: celery 使用
* `CELERY_RESULT_BACKEND`：celery 使用，存储任务状态已经结果

## 本地开发

### 使用 docker 运行依赖服务

配置好需要的环境变量后，运行 `dockerfile_create.py` 创建相关 Dockerfile

    $ python dockerfile_create.py

利用生成的 Dockerfile 构建并运行 docker 容器：

PostgreSQL:

    $ cd dockers/postgresql
    $ docker build . -t hidden_island_postgres
    $ docker run -d -p 5432:5432 --name hidden_island_postgres hidden_island_postgres

    $ docker exec -it hidden_island_postgres /bin/bash

    #  psql -U mapan -d hiddenislandblog -W


Redis:

    $ cd dockers/redis
    $ docker build . -t hidden_island_redis
    $ docker run -d -p 6379:6379 --name hidden_island_redis hidden_island_redis

### 运行

生成虚拟环境，下载依赖：

    $ python -m venv .venv
    $ . .venv/bin/activate
    $ pip install -r requirements/dev.txt

构建需要的数据库内容：

    $ flask deploy
    $ flask build index
    $ flask build similarity

运行任务队列：

    $ celery worker -A celery_worker.celery --loglevel=info

运行服务：

    $ flask run

## 部署

### docker compose

1. 将 `.flaskenv` 中 `FLASK_ENV` 的值改为 `docker`
2. 配置 `.env` 文件：
    1. 此模式下使用的数据库 url 是 `DATABASE_URL`
    2. 需要注意 `DATABASE_URL` 中的数据库连接 IP (`HOST`) 为 `mysql` 或者 `postgres`，`REDIS_HOST` 为 `redis`，见 `docker-compose.yml`
3. ./dockerfile_create.py
4. docker-compose build
5. docker-compose up -d
