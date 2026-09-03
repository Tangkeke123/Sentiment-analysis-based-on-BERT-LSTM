"""
 微信评论信息分词 词频统计 以及写入到csv
"""
import re

import jieba
import pandas as pd

from dao import commentDao


def outCommentFreToCsv(sorted_wfc_list):
    """
    词频统计后，写入到csv
    :param sorted_wfc_list:
    :return:
    """
    df = pd.DataFrame(sorted_wfc_list, columns=['热词', '数量'])
    df.to_csv('comment_fre.csv', index=False)


def getStopWordList():
    """
    获取停顿词
    :return:
    """
    return [line.strip() for line in open('stopWords.txt', encoding='UTF-8').readlines()]


def cut_comment():
    """
    分词
    :return:
    """
    allCommentStr = " ".join([comment[1].strip() for comment in commentDao.getAllComment()])
    seg_list = jieba.cut(allCommentStr)  # 精准模式分词
    return seg_list


def word_fre_count():
    """
    词频统计 过滤数据 数字单个词以及停顿词
    :return:
    """
    seg_list = cut_comment()
    stopWord_list = getStopWordList()
    # 正则去掉数字，单个字以及停顿词
    new_seg_list = []
    for s in seg_list:
        number = re.search('\d+', s)
        if not number and s not in stopWord_list and len(s) > 1:
            new_seg_list.append(s)

    # 词频统计
    wfc = {}
    for w in set(new_seg_list):
        wfc[w] = new_seg_list.count(w)

    # 排序
    sorted_wfc_list = sorted(wfc.items(), key=lambda x: x[1], reverse=True)
    return sorted_wfc_list


if __name__ == '__main__':
    # print("/".join(cut_comment()))
    # print(getStopWordList())
    outCommentFreToCsv(word_fre_count())
