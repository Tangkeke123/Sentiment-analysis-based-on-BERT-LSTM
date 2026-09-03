"""
    微博评论信息 数据访问对象
"""
from util import dbUtil


def getAllComment():
    """
    获取所有评论信息
    :return:
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        sql = "SELECT * FROM t_comment WHERE text_raw!=''"
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)


def getTopCommentUser():
    """
    获取TOP前50评论用户名
    :return:
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        sql = "SELECT username,COUNT(username) AS unCount FROM t_comment GROUP BY username ORDER BY unCount DESC LIMIT 0,50"
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)


def getCommentAmount():
    """
    获取7天用户评论量
    :return:
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        sql = "SELECT DATE_FORMAT(created_at,'%Y-%m-%d') AS commentDate,COUNT(text_raw) AS commentTotal FROM t_comment GROUP BY commentDate ORDER BY commentDate DESC LIMIT 0,7"
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)


def getCommentHotWordAmount(hotword):
    """
    获取日期用户热词评论量
    :return:
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        sql = f"SELECT DATE_FORMAT(created_at,'%Y-%m-%d') AS commentDate,COUNT(text_raw) AS commentTotal FROM t_comment WHERE LOCATE('{hotword}',text_raw)>0  GROUP BY commentDate ORDER BY commentDate DESC "
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)


def getCommentByHotWord(hotword):
    """
    根据热词查询评论信息
    :return:
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()
        sql = f"SELECT * FROM t_comment WHERE LOCATE('{hotword}',text_raw)>0"
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        con.rollback()
        return None
    finally:
        dbUtil.closeCon(con)


def getCommentSourceMap():
    """
    获取评论来源地图数据
    :return: [(省份名, 数量), ...]
    """
    con = None
    try:
        con = dbUtil.getCon()
        cursor = con.cursor()

        sql = """
        SELECT source, COUNT(*) as count 
        FROM t_comment 
        WHERE source IS NOT NULL AND source != '' 
        GROUP BY source
        ORDER BY count DESC
        """
        cursor.execute(sql)
        results = cursor.fetchall()

        data = []
        for row in results:
            province = row[0]
            count = row[1]

            if not province:
                continue

            province = str(province).strip()

            # 确保count是整数
            try:
                count_int = int(count)
            except:
                count_int = 0

            # 标准化省份名称
            if not province.endswith("省") and not province.endswith("市") and not province.endswith(
                    "自治区") and not province.endswith("特别行政区"):
                if province in ["北京", "上海", "天津", "重庆"]:
                    province += "市"
                elif province in ["内蒙古", "广西", "西藏", "宁夏", "新疆"]:
                    province += "自治区"
                elif province == "香港":
                    province = "香港特别行政区"
                elif province == "澳门":
                    province = "澳门特别行政区"
                elif province == "台湾":
                    province = "台湾省"
                else:
                    province += "省"

            data.append((province, count_int))

        return data

    except Exception as e:
        print(e)
        if con:
            con.rollback()
        return []
    finally:
        if con:
            dbUtil.closeCon(con)
