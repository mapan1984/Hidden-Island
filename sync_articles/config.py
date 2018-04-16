import os
import base64
from pathlib import Path

ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
AUTH_INFO = f'{ADMIN_EMAIL}:{ADMIN_PASSWORD}'
AUTH_ENCODE_INFO = base64.b64encode(AUTH_INFO.encode('utf-8')).decode('utf-8')
AUTH_HEADER = {'Authorization': f'Basic ${AUTH_ENCODE_INFO}'}
POST_URL = 'https://hidden-island.herokuapp.com/api/sync-article/'
ARTICLES_PATH = Path.home() / 'code/mapan1984/_posts'
