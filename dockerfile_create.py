#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url

source_dir = os.path.abspath(os.curdir)

# 导入环境变量
env_path = os.path.join(source_dir, '.env')
if os.path.isfile(env_path):
    load_dotenv(dotenv_path=env_path, verbose=True)


from config import DockerConfig

# 1. Create the 'Dockerfile' for database
database_url = make_url(DockerConfig.SQLALCHEMY_DATABASE_URI)
backend_name = database_url.get_backend_name()
username = database_url.username
password = database_url.password
database = database_url.database
host = database_url.host
port = database_url.port

if backend_name == 'mysql':
    print('Create MySQL Dockerfile')

    mysql_dockerfile_dir = os.path.join(source_dir, 'dockers', 'mysql')

    if not os.path.isdir(mysql_dockerfile_dir):
        os.makedirs(mysql_dockerfile_dir)

    with open(os.path.join(mysql_dockerfile_dir, 'Dockerfile'), 'w') as mysql_dockerfile:
        mysql_dockerfile.write('FROM mysql/mysql-server:5.7')
        mysql_dockerfile.write('\n')
        mysql_dockerfile.write('\n# Set environment variables')
        mysql_dockerfile.write('\nENV MYSQL_USER {}'.format(username))
        mysql_dockerfile.write('\nENV MYSQL_PASSWORD {}'.format(password))
        mysql_dockerfile.write('\nENV MYSQL_DATABASE {}'.format(database))
        mysql_dockerfile.write('\nRUN rm /etc/my.cnf')
        mysql_dockerfile.write('\nCOPY my.cnf /etc/')
        mysql_dockerfile.write('\n')
elif backend_name == 'postgres':
    print('Create Postgresql Dockerfile')

    postgres_dockerfile_dir = os.path.join(source_dir, 'dockers', 'postgresql')

    if not os.path.isdir(postgres_dockerfile_dir):
        os.makedirs(postgres_dockerfile_dir)

    with open(os.path.join(postgres_dockerfile_dir, 'Dockerfile'), 'w') as postgres_dockerfile:
        postgres_dockerfile.write('FROM postgres:9.6')
        postgres_dockerfile.write('\n')
        postgres_dockerfile.write('\n# Set environment variables')
        postgres_dockerfile.write('\nENV POSTGRES_USER {}'.format(username))
        postgres_dockerfile.write('\nENV POSTGRES_PASSWORD {}'.format(password))
        postgres_dockerfile.write('\nENV POSTGRES_DB {}'.format(database))
        postgres_dockerfile.write('\n')
else:
    print(f'database backend {backend_name} not support')
    exit(1)


# 2. Create the 'Dockerfile' for redis
print('Create Redis Dockerfile')
redis_url = make_url(DockerConfig.REDIS_URL)
password = redis_url.password


redis_dockerfile_dir = os.path.join(source_dir, 'dockers', 'redis')

if not os.path.isdir(redis_dockerfile_dir):
    os.makedirs(redis_dockerfile_dir)

with open(os.path.join(redis_dockerfile_dir, 'Dockerfile'), 'w') as mysql_dockerfile:
    mysql_dockerfile.write('FROM redis:4.0.9')
    mysql_dockerfile.write('\n')
    mysql_dockerfile.write('\n# Set environment variables')
    mysql_dockerfile.write('\nENV REDIS_PASSWORD {}'.format(password))
    mysql_dockerfile.write('\nCMD ["sh", "-c", "exec redis-server --requirepass \\"$REDIS_PASSWORD\\""]')
    mysql_dockerfile.write('\n')
