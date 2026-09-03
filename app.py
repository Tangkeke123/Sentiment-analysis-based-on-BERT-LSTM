import re

from flask import Flask, request, session, redirect, render_template

from view.page import page
from view.user import user

app = Flask(__name__)
app.secret_key = 'python222'
# 注册蓝图
app.register_blueprint(page.pb)
app.register_blueprint(user.ub)


@app.before_request
def before_request():
    """
    鉴权
    :return:
    """
    pat = re.compile(r'^/static')
    if re.search(pat, request.path):
        return
    if request.path == '/user/login':
        return
    if request.path == '/user/register':
        return
    user = session.get('user')
    if user:
        return None
    return redirect('/user/login')


@app.route('/<path:path>')
def catch_all(path):
    """
    404页面
    :param path:
    :return:
    """
    return render_template('/404.html')


if __name__ == '__main__':
    app.run()
