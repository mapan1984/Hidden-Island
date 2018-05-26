#!/usr/bin/env python
import os
from pathlib import Path
from dotenv import load_dotenv

# 导入环境变量
print('CELERY: load env')
env_path = Path('.') / '.flaskenv'
if env_path.is_file():
    load_dotenv(dotenv_path=env_path, verbose=True)

env_path = Path('.') / '.env'
if env_path.is_file():
    load_dotenv(dotenv_path=env_path, verbose=True)


from app import celery, create_app


app = create_app(os.getenv('FLASK_ENV') or 'default')
app.app_context().push()
