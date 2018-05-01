#!/usr/bin/env python3
from pathlib import Path
from dotenv import load_dotenv


# 导入环境变量
env_path = Path('.') / '.flaskenv'
if env_path.is_file():
    load_dotenv(dotenv_path=env_path, verbose=True)

env_path = Path('.') / '.env'
if env_path.is_file():
    load_dotenv(dotenv_path=env_path, verbose=True)


import os
from collections import defaultdict

from flask_migrate import Migrate, upgrade

from app import create_app, db
from app.models import (User, Role, Article, Category, Tag,
                        Comment, Rating, Words, WordLocation)


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


@app.cli.command()
def buildindex():
    """Build articles index."""
    WordLocation.index_articles()


if __name__ == '__main__':
    app.run()
