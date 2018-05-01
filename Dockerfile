# 该image文件继承官方的python image
FROM python:3.6.4

# 工作环境变量
ENV FLASK_APP manage:app
ENV FLASK_ENV docker

# Create the user to be used in this container
RUN groupadd flasky && useradd -m -g flasky -s /bin/bash flasky

# 指定工作路径为/home/flasky/web
RUN mkdir -p /home/flasky/web
WORKDIR /home/flasky/web
RUN chown -R flasky:flasky /home/flasky
RUN chmod -R 731 /home/flasky

# 解决字符乱码
#ENV LANG en_US.UTF-8
#ENV LANGUAGE en_US:en
#ENV LC_ALL en_US.UTF-8

# 下载Python依赖
COPY requirements requirements
# RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements/docker.txt

# 拷贝源码
COPY app app
COPY migrations migrations
COPY articles articles
COPY manage.py config.py boot.sh .env .flaskenv ./
RUN chmod +x boot.sh

USER flasky

# Run-time configuration
#EXPOSE 5000
#ENTRYPOINT ["./boot.sh"]
