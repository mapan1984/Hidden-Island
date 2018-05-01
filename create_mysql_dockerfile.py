import os
from dotenv import load_dotenv


source_dir = os.path.abspath(os.curdir)

# 导入环境变量
env_path = os.path.join(source_dir, '.env')
if os.path.isfile(env_path):
    load_dotenv(dotenv_path=env_path, verbose=True)


from config import DockerConfig


# Postgres Initialization Files
docker_file = 'Dockerfile'
destination_dir = os.path.join(source_dir, 'mysql')


# Before creating files, check that the destination directory exists
if not os.path.isdir(destination_dir):
    os.makedirs(destination_dir)


# Create the 'Dockerfile' for initializing the Postgres Docker image
with open(os.path.join(destination_dir, docker_file), 'w') as mysql_dockerfile:
    mysql_dockerfile.write('FROM mysql/mysql-server:5.7')
    mysql_dockerfile.write('\n')
    mysql_dockerfile.write('\n# Set environment variables')
    mysql_dockerfile.write('\nENV MYSQL_USER {}'.format(DockerConfig.MYSQL_USER))
    mysql_dockerfile.write('\nENV MYSQL_PASSWORD {}'.format(DockerConfig.MYSQL_PASSWORD))
    mysql_dockerfile.write('\nENV MYSQL_DATABASE {}'.format(DockerConfig.MYSQL_DATABASE))
    mysql_dockerfile.write('\nRUN rm /etc/my.cnf')
    mysql_dockerfile.write('\nCOPY my.cnf /etc/')
    mysql_dockerfile.write('\n')
