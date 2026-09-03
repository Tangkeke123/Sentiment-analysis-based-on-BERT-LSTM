"""
    微博帖子数据访问对象
"""
from util import dbUtil


def getArticleByArcType(arcType):
    """
    根据微博类别查询微博帖子信息
    :return:
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        sql = f"SELECT * FROM t_article where articleType='{arcType}'"
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)


def getAllArticle():
    """
    查询所有帖子信息
    :return:
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        sql = "SELECT * FROM t_article"
        cursor.execute(sql)
        result = cursor.fetchall()
        return result if result else []
    except Exception as e:
        print(f"获取所有文章错误: {e}")
        if con:
            con.rollback()
        return []  # ← 改为返回空列表而不是 None
    finally:
        if con:
            dbUtil.closeCon(con)


def getTotalArticle():
    """
    获取帖子总数
    :return:
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        sql = "SELECT count(*) FROM t_article"
        cursor.execute(sql)
        return cursor.fetchone()[0]
    except Exception as e:
        print(e)
        con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)


def getTopAuthor():
    """
    获取点赞最高微博作者
    :return:
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        sql = "SELECT authorName FROM t_article ORDER BY attitudes_count DESC LIMIT 0,1"
        cursor.execute(sql)
        return cursor.fetchone()[0]
    except Exception as e:
        print(e)
        con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)


def getTopRegion():
    """
    获取最高点赞城市
    :return:
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        sql = "SELECT region_name,SUM(attitudes_count) AS ac FROM t_article WHERE region_name!='' GROUP BY region_name ORDER BY ac DESC LIMIT 0,1"
        cursor.execute(sql)
        return cursor.fetchone()[0]
    except Exception as e:
        print(e)
        con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)


def getArticleTopZan():
    """
    获取点赞最高的6条帖子
    :return:
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        sql = "SELECT text_raw,attitudes_count FROM t_article ORDER BY attitudes_count DESC LIMIT 0,6"
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)


def get7DayArticle():
    """
    获取最近7天微博帖子数量
    :return:
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        sql = "SELECT DATE_FORMAT(created_at,'%Y-%m-%d') AS articleDate,COUNT(text_raw) AS articleTotal FROM t_article GROUP BY articleDate ORDER BY articleDate DESC LIMIT 0,7"
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)


def getArticleTypeAmount():
    """
    获取帖子类别数量
    :return:
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        sql = "SELECT articleType,COUNT(articleType) FROM t_article GROUP BY articleType"
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)
