#!/usr/bin/env python3
import os
from dotenv import load_dotenv


source_dir = os.path.abspath(os.curdir)

# 导入环境变量
env_path = os.path.join(source_dir, '.env')
if os.path.isfile(env_path):
    load_dotenv(dotenv_path=env_path, verbose=True)


from config import DockerConfig


docker_file = 'Dockerfile'

mysql_dockerfile_dir = os.path.join(source_dir, 'mysql')
redis_dockerfile_dir = os.path.join(source_dir, 'redis')
postgres_dockerfile_dir = os.path.join(source_dir, 'postgresql')


# Before creating files, check that the destination directory exists
# if not os.path.isdir(mysql_dockerfile_dir):
#     os.makedirs(mysql_dockerfile_dir)
if not os.path.isdir(redis_dockerfile_dir):
    os.makedirs(redis_dockerfile_dir)
if not os.path.isdir(postgres_dockerfile_dir):
    os.makedirs(postgres_dockerfile_dir)


# Create the 'Dockerfile' for initializing the Postgres Docker image
# print('Create MySQL Dockerfile')
# with open(os.path.join(mysql_dockerfile_dir, docker_file), 'w') as mysql_dockerfile:
#     mysql_dockerfile.write('FROM mysql/mysql-server:5.7')
#     mysql_dockerfile.write('\n')
#     mysql_dockerfile.write('\n# Set environment variables')
#     mysql_dockerfile.write('\nENV MYSQL_USER {}'.format(DockerConfig.MYSQL_USER))
#     mysql_dockerfile.write('\nENV MYSQL_PASSWORD {}'.format(DockerConfig.MYSQL_PASSWORD))
#     mysql_dockerfile.write('\nENV MYSQL_DATABASE {}'.format(DockerConfig.MYSQL_DATABASE))
#     mysql_dockerfile.write('\nRUN rm /etc/my.cnf')
#     mysql_dockerfile.write('\nCOPY my.cnf /etc/')
#     mysql_dockerfile.write('\n')

print('Create Postgresql Dockerfile')
with open(os.path.join(postgres_dockerfile_dir, docker_file), 'w') as postgres_dockerfile:
    postgres_dockerfile.write('FROM postgres:9.6')
    postgres_dockerfile.write('\n')
    postgres_dockerfile.write('\n# Set environment variables')
    postgres_dockerfile.write('\nENV POSTGRES_USER {}'.format(DockerConfig.POSTGRES_USER))
    postgres_dockerfile.write('\nENV POSTGRES_PASSWORD {}'.format(DockerConfig.POSTGRES_PASSWORD))
    postgres_dockerfile.write('\nENV POSTGRES_DB {}'.format(DockerConfig.POSTGRES_DB))
    postgres_dockerfile.write('\n')

print('Create Redis Dockerfile')
with open(os.path.join(redis_dockerfile_dir, docker_file), 'w') as mysql_dockerfile:
    mysql_dockerfile.write('FROM redis:4.0.9')
    mysql_dockerfile.write('\n')
    mysql_dockerfile.write('\n# Set environment variables')
    mysql_dockerfile.write('\nENV REDIS_PASSWORD {}'.format(DockerConfig.REDIS_PASSWORD))
    mysql_dockerfile.write('\nCMD ["sh", "-c", "exec redis-server --requirepass \\"$REDIS_PASSWORD\\""]')
    mysql_dockerfile.write('\n')
