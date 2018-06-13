import os

from flask import (request, redirect, url_for, render_template,
                   flash, current_app, jsonify, session)
from flask_login import current_user

from app import db, redis
from config import Config
from app.models import Article, User, Role
from app.decorators import admin_required
from app.admin import admin
from app.admin.forms import EditProfileAdminForm
from app.email import send_email
from app.tasks import add_together, long_task


@admin.route('/')
@admin_required
def index():
    # 获取存在的markdown文件的name集合
    existed_md_articles = {
        md_name.split('.')[0] for md_name in os.listdir(Config.ARTICLES_SOURCE_DIR)
    }
    print(existed_md_articles)
    # 获取已记录markdown文章集合
    loged_md_articles = {
        article for article in Article.query.filter_by(author=current_user).all() if article.name in existed_md_articles
    }
    print(loged_md_articles)
    # 获取未被记录的md文件name的集合
    # FIXME: Markdown文件名对应文章标题？
    not_loged_articles = existed_md_articles - {article.name for article in loged_md_articles}
    print(not_loged_articles)
    return render_template(
        'admin/admin.html',
        loged_md_articles=loged_md_articles,
        not_loged_articles=not_loged_articles
    )


@admin.route('/upload', methods=['POST'])
@admin_required
def upload():
    file = request.files['file']
    if file and Config.allowed_file(file.filename):
        filename = file.filename
        # 保存md文件
        file.save(
            os.path.join(current_app.config['ARTICLES_SOURCE_DIR'], filename)
        )
        # 生成html与数据库记录
        Article.md_render(name=filename.rsplit('.')[0])

        flash("上传 %s 成功" % filename)
    else:
        flash("上传 %s 失败" % filename)
    return redirect(url_for('admin.index'))


@admin.route('/render/<article_name>')
@admin_required
def render(article_name):
    flash(Article.md_render(article_name))
    return redirect(url_for('admin.index'))


@admin.route('/refresh/<article_name>')
@admin_required
def refresh(article_name):
    article = Article.query.filter_by(name=article_name).first()
    return article.md_refresh()


@admin.route('/delete/md/<article_name>')
@admin_required
def delete_md(article_name):
    flash(Article.md_delete(article_name))
    return redirect(url_for('admin.index'))


@admin.route('/delete/html/<article_name>')
@admin_required
def delete_html(article_name):
    article = Article.query.filter_by(name=article_name).first()
    flash(article.delete())
    return redirect(url_for('admin.index'))


@admin.route('/render_all')
@admin_required
def render_all():
    Article.md_render_all()
    flash("Render all articles succeeded")
    return redirect(url_for('admin.index'))


@admin.route('/refresh_all')
@admin_required
def refresh_all():
    Article.md_refresh_all()
    return "Refresh all articles succeeded"


@admin.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_profile(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('个人信息已经成功更新')
        return redirect(url_for('user.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('user/edit.html', form=form, user=user)


@admin.route('/test-error')
@admin_required
def test_error():
    raise Exception("Beds are burning!")


@admin.route('/test-redis')
@admin_required
def test_redis():
    redis.set('test_redis', 'hello')
    flash(redis.get('test_redis'))
    redis.delete('test_redis')
    return redirect(url_for('admin.index'))


@admin.route('/test-email')
@admin_required
def test_email():
    send_email(current_user.email, 'Test email', 'test email server', type_='text/plain')
    flash('一封测试邮件已经发送到您的邮箱')
    return redirect(url_for('admin.index'))


@admin.route('/test-task')
@admin_required
def test_task():
    result = add_together.delay(1, 2)
    flash(f'test task {result.wait()}')
    return redirect(url_for('admin.index'))


@admin.route('/test-tasks', methods=['GET', 'POST'])
@admin_required
def test_tasks():
    if request.method == 'GET':
        return render_template('admin/test-tasks.html', email=session.get('email', ''))

    email = request.form['email']
    session['email'] = email

    if request.form['submit'] == 'Send':
        # send right away
        flash('Sending email to {0}'.format(email))
    else:
        # send in one minute
        flash('An email will be sent to {0} in one minute'.format(email))

    return redirect(url_for('admin.test_tasks'))


@admin.route('/test-tasks/longtask', methods=['POST'])
@admin_required
def test_longtask():
    task = long_task.apply_async()
    return (
        jsonify({}),
        202,
        {'Location': url_for('admin.test_taskstatus', task_id=task.id)}
    )


@admin.route('/test-tasks/status/<task_id>')
@admin_required
def test_taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)
