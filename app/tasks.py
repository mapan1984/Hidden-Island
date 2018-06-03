import time
import random

from app import celery
from app.models import Article


@celery.task
def add_together(a, b):
    return a + b


@celery.task()
def build_index(id):
    """为文章建立索引与相似度缓存"""
    # XXX: jieba分词每次都会重新加载一次
    article = Article.query.get_or_404(id)
    article._build_index()
    article._cache_similar()


@celery.task
def rebuild_index(id):
    """为文章重新建立索引与相似度缓存"""
    # XXX: jieba分词每次都会重新加载一次
    article = Article.query.get_or_404(id)
    article._rebuild_index()
    article._cache_similar()


@celery.task
def delete_index(id):
    """删除文章的索引与相似度缓存"""
    # XXX: jieba分词每次都会重新加载一次
    article = Article.query.get_or_404(id)
    article._delete_index()
    article._delete_cache()


@celery.task(bind=True)
def long_task(self):
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!', 'result': 42}
