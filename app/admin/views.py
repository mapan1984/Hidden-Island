from flask import render_template

from . import admin


@admin.route('/admin')
def admin():
    return render_template('admin.html')
