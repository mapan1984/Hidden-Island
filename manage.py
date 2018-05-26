#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv


# 导入环境变量
env_path = Path('.') / '.flaskenv'
if env_path.is_file():
    load_dotenv(dotenv_path=env_path, verbose=True)

env_path = Path('.') / '.env'
if env_path.is_file():
    load_dotenv(dotenv_path=env_path, verbose=True)


from itertools import combinations

from flask.cli import AppGroup
from flask_migrate import Migrate, upgrade

from app import create_app, db, redis
from app.models import (User, Role, Article, Category, Tag,
                        Comment, Rating, Words, WordLocation)
from app.utils.similarity import similarity


app = create_app(os.getenv('FLASK_ENV', 'default'))
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role,
                Article=Article, Category=Category, Tag=Tag,
                Comment=Comment, Rating=Rating,
                Words=Words, WordLocation=WordLocation)


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()

    # create user roles
    Role.insert_roles()

    # create admin user
    User.add_admin()

    # create categores
    Category.insert_categores()


build_cli = AppGroup('build')


@build_cli.command('index')
def build_index():
    """ Build articles searcher engine index. """
    for article in Article.query.all():
        article._build_index()


@build_cli.command('critics')
def build_critics():
    """ Cache all articles rattings. """
    for rating in Rating.query.all():
        username = rating.user.username
        article_name = rating.article.name
        rating_value = rating.value

        # person_prefs.hset(username, article_name, rating_value)

        # item_prefs.hset(article_name, username, rating_value)

        print(f'Cache rattings of {article_name} & {username} := {rating_value}')


@build_cli.command('similarity')
def build_similarity():
    """ Cache all articles similarities. """
    for a, b in combinations(Article.query.all(), 2):
        simi = similarity(a.content, b.content)
        redis.zadd(a.name, simi, b.name)
        redis.zadd(b.name, simi, a.name)
        print(f'Cache similarity of {a.name} & {b.name} := {simi}')


app.cli.add_command(build_cli)


if __name__ == '__main__':
    app.run()
