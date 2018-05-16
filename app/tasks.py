import time
from itertools import combinations

from app import celery, redis
from app.models import Article
from app.utils.similarity import similarity


@celery.task
def add_together(a, b):
    return a + b


@celery.task
def rebuild_index(article):
    while True:
        time.sleep(5)
        print(article)
        if article.id:
            article._rebuild_index()
            break
        else:
            print("[Article Rebuild Index] Retry in 5 secs...")
    return article.id


@celery.task()
def build_sim_index():
    for a, b in combinations(Article.query.all()):
        simi = similarity(a.content, b.content)
        redis.zadd(a.name, simi, b.name)
        redis.zadd(b.name, simi, a.name)
