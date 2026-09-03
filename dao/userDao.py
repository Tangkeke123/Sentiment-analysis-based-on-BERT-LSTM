"""
    用户数据访问对象
"""
from entity.UserModel import User
from util import dbUtil


def login(user: User):
    """
    登录判断（使用参数化查询防SQL注入）
    :param user: User对象（包含username/password）
    :return: 登录成功返回用户数据元组，失败返回None
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        # 关键：参数化查询，避免字符串拼接
        sql = "SELECT * FROM t_user WHERE username=%s and password=%s"
        cursor.execute(sql, (user.username, user.password))
        return cursor.fetchone()  # 查到返回用户数据，没查到返回None
    except Exception as e:
        print(f"登录查询异常: {e}")
        if con:  # 避免con为None时调用rollback
            con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)


def add(user: User):
    """
    用户注册添加（参数化查询）
    :param user: User对象（包含username/password/createtime）
    :return: 成功返回受影响行数（1），失败返回None
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        # 参数化插入，避免SQL注入
        sql = "INSERT INTO t_user VALUES(null, %s, %s, %s)"
        cursor.execute(sql, (user.username, user.password, user.createtime))
        con.commit()  # 插入操作需要手动提交事务
        return cursor.rowcount  # 返回1表示插入成功
    except Exception as e:
        print(f"用户添加异常: {e}")
        if con:
            con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)


def getByUserName(username):
    """
    根据用户名查询用户信息
    :param username: 用户名
    :return: 查到返回用户列表，失败返回None
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        sql = "SELECT * FROM t_user WHERE username=%s"
        cursor.execute(sql, (username,))  # 单个参数也要传元组（注意逗号）
        return cursor.fetchall()  # 返回所有匹配的用户数据
    except Exception as e:
        print(f"查询用户异常: {e}")
        if con:
            con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)
