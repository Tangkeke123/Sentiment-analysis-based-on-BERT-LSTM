"""
    将已有的CSV文件（article_data.csv、comment_data.csv）持久化到数据库
"""
import os
import traceback
import pandas as pd
from sqlalchemy import create_engine
import pymysql


# 创建数据库（如果不存在）
def create_db_if_not_exist():
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS db_weibo3 DEFAULT CHARSET utf8mb4")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print('创建数据库异常：', e)
        traceback.print_exc()


create_db_if_not_exist()
engine = create_engine('mysql+pymysql://root:123456@localhost:3306/db_weibo3?charset=utf8mb4')


def dataClean():
    """数据清洗函数（可根据需要实现具体逻辑）"""
    pass


def saveToDb():
    """
    持久化到数据库：合并 CSV 与数据库旧数据，去重后存入，最后删除 CSV 文件
    """
    try:
        # 尝试读取数据库现有表，合并去重
        oldArticleDb = pd.read_sql('select * from t_article', engine)
        newArticleCsv = pd.read_csv('article_data.csv')
        concatArticlePd = pd.concat([newArticleCsv, oldArticleDb])
        resultArticlePd = concatArticlePd.drop_duplicates(subset='id', keep='last')
        resultArticlePd.to_sql('t_article', con=engine, if_exists='replace', index=False)

        oldCommentDb = pd.read_sql('select * from t_comment', engine)
        newCommentCsv = pd.read_csv('comment_data.csv')
        concatCommentPd = pd.concat([newCommentCsv, oldCommentDb])
        resultCommentPd = concatCommentPd.drop_duplicates(subset='id', keep='last')
        resultCommentPd.to_sql('t_comment', con=engine, if_exists='replace', index=False)
    except Exception as e:
        # 如果表不存在，直接写入 CSV 数据（自动创建表）
        if "Table 'db_weibo3.t_article' doesn't exist" in str(e):
            print("提示：首次运行，数据库表不存在，直接写入 CSV 数据创建表")
        else:
            print('异常：', e)
            traceback.print_exc()
        # 直接写入 CSV 数据
        newArticleCsv = pd.read_csv('article_data.csv')
        newCommentCsv = pd.read_csv('comment_data.csv')
        newArticleCsv.to_sql('t_article', con=engine, if_exists='replace', index=False)
        newCommentCsv.to_sql('t_comment', con=engine, if_exists='replace', index=False)

    # 删除已处理的 CSV 文件（可根据需要保留）
    os.remove('article_data.csv')
    os.remove('comment_data.csv')


if __name__ == '__main__':
    print("=" * 50)
    print("开始将现有CSV数据存入数据库")
    print("=" * 50)

    print("\n[步骤1] 数据清洗...")
    dataClean()
    print("[完成] 数据清洗结束\n")

    print("[步骤2] 数据持久化到数据库...")
    saveToDb()
    print("[完成] 数据持久化结束\n")

    print("=" * 50)
    print("数据入库完成！")
    print("=" * 50)
