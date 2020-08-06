import unittest
import json
import re
from base64 import b64encode
from app import create_app, db
from app.models import User, Role, Article, Comment


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_404(self):
        response = self.client.get(
            '/api/wrong_url/',
            headers=self.get_api_headers('email', 'password')
        )
        self.assertEqual(response.status_code, 404)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['error'], 'not found')

    def test_no_auth(self):
        response = self.client.get(
            '/api/articles/',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_bad_auth(self):
        # 添加一个用户
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='john@example.com', password='cat', confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        # 用错误的密码获取文章
        response = self.client.get(
            '/api/articles/',
            headers=self.get_api_headers('john@example.com', 'dog')
        )
        self.assertEqual(response.status_code, 401)

    def test_token_auth(self):
        # 增加一个普通用户
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='john@example.com', password='cat', confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        # 用错误的token获取文章
        response = self.client.get(
            '/api/articles/',
            headers=self.get_api_headers('bad-token', '')
        )
        self.assertEqual(response.status_code, 401)

        # 获得一个正确的token
        response = self.client.get(
            '/api/tokens/',
            headers=self.get_api_headers('john@example.com', 'cat')
        )
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # 用正确的token获取文章
        response = self.client.get(
            '/api/articles/',
            headers=self.get_api_headers(token, '')
        )
        self.assertEqual(response.status_code, 200)

    def test_anonymous(self):
        # 用游客身份获取文章
        response = self.client.get(
            '/api/articles/',
            headers=self.get_api_headers('', '')
        )
        self.assertEqual(response.status_code, 401)

    def test_unconfirmed_account(self):
        # 增加一个未认证用户
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='john@example.com', password='cat', confirmed=False,
                 role=r)
        db.session.add(u)
        db.session.commit()

        # 用未认证用户获得文章
        response = self.client.get(
            '/api/articles/',
            headers=self.get_api_headers('john@example.com', 'cat'))
        self.assertEqual(response.status_code, 403)

    def test_articles(self):
        # 增加一个作者
        a = Role.query.filter_by(name='Author').first()
        self.assertIsNotNone(a)
        u = User(email='john@example.com', password='cat', confirmed=True, role=a)
        db.session.add(u)
        db.session.commit()

        # 写一篇空文章
        response = self.client.post(
            '/api/articles/',
            headers=self.get_api_headers('john@example.com', 'cat'),
            data=json.dumps({
                'title': 'title',
                'body': '',
            })
        )
        self.assertEqual(response.status_code, 412)

        # 写一篇正确的文章
        response = self.client.post(
            '/api/articles/',
            headers=self.get_api_headers('john@example.com', 'cat'),
            data=json.dumps({
                'title': 'title',
                'body': 'body of the *blog* article',
                'category': 'test',
                'tags': ['test'],
            })
        )
        self.assertEqual(response.status_code, 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # 获取新增加的文章
        response = self.client.get(
            url,
            headers=self.get_api_headers('john@example.com', 'cat')
        )
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['url'], url)
        self.assertEqual(json_response['body'], 'body of the *blog* article')
        self.assertEqual(json_response['body_html'],
                         '<p>body of the <em>blog</em> article</p>')
        json_article = json_response

        # 获得该用户的所有文章
        response = self.client.get(
            '/api/users/{}/articles/'.format(u.id),
            headers=self.get_api_headers('john@example.com', 'cat')
        )
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('articles'))
        self.assertEqual(json_response.get('count', 0), 1)
        self.assertEqual(json_response['articles'][0], json_article)

        # get the article from the user as a follower
        # response = self.client.get(
        #     '/api/users/{}/timeline/'.format(u.id),
        #     headers=self.get_api_headers('john@example.com', 'cat')
        # )
        # self.assertEqual(response.status_code, 200)
        # json_response = json.loads(response.get_data(as_text=True))
        # self.assertIsNotNone(json_response.get('articles'))
        # self.assertEqual(json_response.get('count', 0), 1)
        # self.assertEqual(json_response['articles'][0], json_article)

        # 编辑文章
        response = self.client.put(
            url,
            headers=self.get_api_headers('john@example.com', 'cat'),
            data=json.dumps({
                'title': 'title',
                'body': 'updated body',
                'category': 'test',
                'tags': ['test'],
            })
        )
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['url'], url)
        self.assertEqual(json_response['body'], 'updated body')
        self.assertEqual(json_response['body_html'], '<p>updated body</p>')

    def test_users(self):
        # 增加两个普通用户
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u1 = User(
            email='john@example.com',
            username='john',
            password='cat',
            confirmed=True,
            role=r
        )
        u2 = User(
            email='susan@example.com',
            username='susan',
            password='dog',
            confirmed=True,
            role=r
        )
        db.session.add_all([u1, u2])
        db.session.commit()

        # 获取用户
        response = self.client.get(
            '/api/users/{}'.format(u1.id),
            headers=self.get_api_headers('susan@example.com', 'dog')
        )
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['username'], 'john')
        response = self.client.get(
            '/api/users/{}'.format(u2.id),
            headers=self.get_api_headers('susan@example.com', 'dog')
        )
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['username'], 'susan')

    def test_comments(self):
        # 增加一个普通用户
        u = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(u)
        u1 = User(
            email='john@example.com',
            username='john',
            password='cat',
            confirmed=True,
            role=u
        )
        # 增加一个作者
        a = Role.query.filter_by(name='Author').first()
        self.assertIsNotNone(a)
        a2 = User(
            email='susan@example.com',
            username='susan',
            password='dog',
            confirmed=True,
            role=a
        )
        db.session.add_all([u1, a2])
        db.session.commit()

        # 以用户a2为作者，增加新文章
        article = Article(name='title', body='body of the article', author=a2)
        db.session.add(article)
        db.session.commit()

        # 写一条新评论
        response = self.client.post(
            '/api/articles/{}/comments/'.format(article.id),
            headers=self.get_api_headers('john@example.com', 'cat'),
            data=json.dumps({'body': 'Good [article](http://example.com)!'})
        )
        self.assertEqual(response.status_code, 201)
        json_response = json.loads(response.get_data(as_text=True))
        url = response.headers.get('Location')
        self.assertIsNotNone(url)
        self.assertEqual(json_response['body'],
                         'Good [article](http://example.com)!')
        self.assertEqual(
            re.sub('<.*?>', '', json_response['body_html']), 'Good article!')

        # 获取这条新的评论
        response = self.client.get(
            url,
            headers=self.get_api_headers('john@example.com', 'cat')
        )
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['url'], url)
        self.assertEqual(json_response['body'],
                         'Good [article](http://example.com)!')

        # 增加另一个评论
        comment = Comment(body='Thank you!', author=a2, article=article)
        db.session.add(comment)
        db.session.commit()

        # 获取文章的新增的这两个评论
        response = self.client.get(
            '/api/articles/{}/comments/'.format(article.id),
            headers=self.get_api_headers('susan@example.com', 'dog')
        )
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('comments'))
        self.assertEqual(json_response.get('count', 0), 2)

        # 获取文章的全部评论
        response = self.client.get(
            '/api/articles/{}/comments/'.format(article.id),
            headers=self.get_api_headers('susan@example.com', 'dog')
        )
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('comments'))
        self.assertEqual(json_response.get('count', 0), 2)
