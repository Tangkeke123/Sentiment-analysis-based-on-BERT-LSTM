from datetime import datetime

from flask import Blueprint, request, render_template, jsonify, session, redirect

from dao import userDao
from entity.UserModel import User
from util.md5Util import MD5Utility

ub = Blueprint('user', __name__, url_prefix='/user', template_folder='templates')


@ub.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录
    :return:
    """
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.values.get('username')
        password = request.values.get('password')

        # 空值校验
        if not (username and username.strip()):
            return jsonify(error=True, info='用户名不能为空！')
        if not (password and password.strip()):
            return jsonify(error=True, info='密码不能为空！')

        # 构造用户对象并调用登录方法
        user = User(username, MD5Utility.encrypt(password))
        resultUser = userDao.login(user)

        if resultUser:
            session['user'] = resultUser
            return jsonify(success=True, info='登录成功！')
        else:
            return jsonify(error=True, info='用户名或者密码错误！')


@ub.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册（修复None判断+异常处理）
    :return:
    """
    if request.method == 'GET':
        return render_template('register.html')
    else:
        # 获取前端参数
        username = request.values.get('username')
        password = request.values.get('password')
        password2 = request.values.get('password2')

        # 1. 空值校验（简化写法，更易读）
        if not (username and username.strip()):
            return jsonify(error=True, info='用户名不能为空！')
        if not (password and password.strip()):
            return jsonify(error=True, info='密码不能为空！')
        if not (password2 and password2.strip()):
            return jsonify(error=True, info='确认密码不能为空！')

        # 2. 两次密码一致性校验
        if password != password2:
            return jsonify(error=True, info='确认密码不正确！')

        # 3. 用户名重复校验（关键修复：先判断是否为None，再判断长度）
        user_list = userDao.getByUserName(username)
        if user_list is None:
            # 数据库连接异常
            return jsonify(error=True, info='数据库连接失败，请稍后再试！')
        if len(user_list) > 0:
            # 用户名已存在
            return jsonify(error=True, info='该用户名已经存在！')

        # 4. 执行注册逻辑
        try:
            user = User(username, MD5Utility.encrypt(password))
            user.createtime = datetime.now()
            add_result = userDao.add(user)

            # 处理add方法的返回值（避免None对比）
            if add_result and add_result > 0:
                return jsonify(success=True, info='注册成功！')
            else:
                return jsonify(error=True, info='注册失败，请联系管理员！')
        except Exception as e:
            print(f"注册异常: {e}")
            return jsonify(error=True, info='注册过程出错，请稍后再试！')


@ub.route('/logout')
def logout():
    """
    用户安全退出
    :return:
    """
    session.clear()
    return redirect('/user/login')
