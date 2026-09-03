import pandas as pd
from flask import Blueprint, render_template, jsonify, request
# 移除 SnowNLP 导入 ↓
# from snownlp import SnowNLP
from util import dbUtil
from dao import articleDao, commentDao
from util import wordcloudUtil

# ===== 新增：导入模型相关依赖 =====
import torch
import torch.nn as nn
from transformers import BertTokenizer, BertModel
import os

pb = Blueprint('page', __name__, url_prefix='/page', template_folder='templates')


# ===== 新增：模型定义（和你训练时完全一致） =====
class SentimentModel(nn.Module):
    def __init__(self, hidden_size, num_classes, num_layers, dropout, bert_path):
        super(SentimentModel, self).__init__()
        self.bert = BertModel.from_pretrained(bert_path, local_files_only=True)
        self.lstm = nn.LSTM(self.bert.config.hidden_size, hidden_size, num_layers,
                            bidirectional=True, batch_first=True, dropout=dropout)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_size * 2, num_classes)

    def forward(self, x, mask):
        bert_output = self.bert(x, attention_mask=mask)
        lstm_output, _ = self.lstm(bert_output.last_hidden_state)
        pooled_output = lstm_output[:, -1, :]
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        return logits


##模型
MODEL_PATH = r"C:\Users\Yuikai\Desktop\Context\Gra\winter\saved_models\best_model.pth"
BERT_PATH = r"C:\Users\Yuikai\Desktop\Gra\BERT1"
PROJECT_ROOT = r"C:\Users\Yuikai\Desktop\Context\Gra\winter"
FENCI_DIR = os.path.join(PROJECT_ROOT, "fenci")
SPIDER_DIR = os.path.join(PROJECT_ROOT, "spider")

# 初始化分析器
sentiment_analyzer = None
try:
    # 设备选择
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # 加载tokenizer
    tokenizer = BertTokenizer.from_pretrained(BERT_PATH, local_files_only=True)

    # 初始化模型（消除dropout警告）
    model = SentimentModel(
        hidden_size=128,
        num_classes=2,
        num_layers=1,
        dropout=0.0,  # 单层设为0，无警告
        bert_path=BERT_PATH
    )

    # 加载模型权重
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.to(device)
    model.eval()


    # 定义预测函数
    def predict_sentiment(text):
        """预测文本情感，返回(情感标签, 置信度)"""
        if not text or len(text.strip()) < 2:
            return "中性", 0.0

        encoding = tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)

        with torch.no_grad():
            outputs = model(input_ids, attention_mask)
            probabilities = torch.softmax(outputs, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()

        # 基础情感标签
        base_sentiment = "正面" if predicted_class == 1 else "负面"

        # 补充中性判定（置信度<0.7判定为中性，可调整阈值）
        if confidence < 0.7:
            return "中性", confidence
        return base_sentiment, confidence


    sentiment_analyzer = predict_sentiment
    print(f"[SUCCESS] 情感分析模型加载成功：{MODEL_PATH}")  # 替换特殊字符
except Exception as e:
    print(f"[ERROR] 情感分析模型加载失败：{e}")  # 替换特殊字符
    sentiment_analyzer = None


# ===== 原有代码：home 路由（未修改） =====
@pb.route('/home')
def home():
    """
    进入主页面，获取相应的数据，带到页面去
    :return:
    """
    articleData = articleDao.get7DayArticle()
    xAxis7ArticleData = []
    yAxis7ArticleData = []
    for article in articleData:
        xAxis7ArticleData.append(article[0])
        yAxis7ArticleData.append(article[1])

    # 获取帖子类别数量
    arcTypeData = []
    articleTypeAmountList = articleDao.getArticleTypeAmount()
    for arcType in articleTypeAmountList:
        arcTypeData.append({'value': arcType[1], 'name': arcType[0]})

    # 获取top50评论用户名
    top50CommentUserList = commentDao.getTopCommentUser()
    top50CommentUserNameList = [cu[0] for cu in top50CommentUserList]
    str = ' '.join(top50CommentUserNameList)
    wordcloudUtil.genWordCloudPic(str, 'comment_mask.jpg', 'comment_user_cloud.jpg')

    # 获取7天评论数量
    commentData = []
    commentAmountList = commentDao.getCommentAmount()
    for comment in commentAmountList:
        commentData.append({'value': comment[1], 'name': comment[0]})
    return render_template('index.html',
                           xAxis7ArticleData=xAxis7ArticleData,
                           yAxis7ArticleData=yAxis7ArticleData,
                           arcTypeData=arcTypeData,
                           commentData=commentData)


# ===== 原有代码：homePageData 路由（未修改） =====
@pb.route('homePageData')
def getHomePageData():
    """
    获取主页数据 ajax异步交互 前端每隔5分钟请求一次 实时数据
    :return:
    """
    totalArticle = articleDao.getTotalArticle()
    topAuthor = articleDao.getTopAuthor()
    topRegion = articleDao.getTopRegion()
    topArticles = articleDao.getArticleTopZan()
    return jsonify(totalArticle=totalArticle, topAuthor=topAuthor, topRegion=topRegion, topArticles=topArticles)


# ===== 修改：hotWord 路由（替换 SnowNLP 为自定义模型） =====
@pb.route('hotWord')
def hotWord():
    """
    热词分析统计
    :return:
    """
    hotwordList = []
    # 只读取前100条
    df = pd.read_csv(os.path.join(FENCI_DIR, "comment_fre.csv"), nrows=100)
    for value in df.values:
        hotwordList.append(value[0])
    # 获取请求参数，如果没有获取到，给个默认值 第一个列表数据
    defaultHotWord = request.args.get('word', default=hotwordList[0])
    hotwordNum = 0  # 出现次数
    for value in df.values:
        if defaultHotWord == value[0]:
            hotwordNum = value[1]

    # 情感分析（替换 SnowNLP ↓）
    sentiments = '中性'
    if sentiment_analyzer is not None:
        try:
            sentiments, _ = sentiment_analyzer(defaultHotWord)
        except Exception as e:
            print(f"热词情感分析错误：{e}")
            sentiments = '中性'
    # 原 SnowNLP 逻辑已删除 ↓
    # stc = SnowNLP(defaultHotWord).sentiments
    # if stc > 0.6:
    #     sentiments = '正面'
    # elif stc < 0.2:
    #     sentiments = '负面'
    # else:
    #     sentiments = '中性'

    commentHotWordData = commentDao.getCommentHotWordAmount(defaultHotWord)
    xAxisHotWordData = []
    yAxisHotWordData = []
    for comment in commentHotWordData:
        xAxisHotWordData.append(comment[0])
        yAxisHotWordData.append(comment[1])

    commentList = commentDao.getCommentByHotWord(defaultHotWord)
    return render_template('hotWord.html',
                           hotwordList=hotwordList,
                           defaultHotWord=defaultHotWord,
                           hotwordNum=hotwordNum,
                           sentiments=sentiments,
                           xAxisHotWordData=xAxisHotWordData,
                           yAxisHotWordData=yAxisHotWordData,
                           commentList=commentList)


# ===== 修改：articleData 路由（替换 SnowNLP 为自定义模型） =====
@pb.route('articleData')
def articleData():
    """
    微博舆情分析
    :return:
    """
    articleOldList = articleDao.getAllArticle()
    articleNewList = []
    for article in articleOldList:
        article = list(article)
        # 情感分析（替换 SnowNLP ↓）
        sentiments = '中性'
        if sentiment_analyzer is not None:
            try:
                sentiments, _ = sentiment_analyzer(article[1])
            except Exception as e:
                print(f"文章情感分析错误：{e}")
                sentiments = '中性'

        article.append(sentiments)
        articleNewList.append(article)
    return render_template('articleData.html', articleList=articleNewList)


# ===== 原有代码：articleDataAnalysis 路由（未修改） =====
@pb.route('articleDataAnalysis')
def articleDataAnalysis():
    """
    微博数据分析
    :return:
    """
    arcTypeList = []
    df = pd.read_csv(os.path.join(SPIDER_DIR, "arcType_data.csv"))
    for value in df.values:
        arcTypeList.append(value[0])
    # 获取请求参数，如果没有获取到，给个默认值 第一个列表数据
    defaultArcType = request.args.get('arcType', default=arcTypeList[0])
    articleList = articleDao.getArticleByArcType(defaultArcType)
    xDzData = []  # 点赞x轴数据
    xPlData = []  # 评论x轴数据
    xZfData = []  # 转发x轴数据
    rangeNum = 1000
    rangeNum2 = 100
    for item in range(0, 10):
        xDzData.append(str(rangeNum * item) + '-' + str(rangeNum * (item + 1)))
        xPlData.append(str(rangeNum * item) + '-' + str(rangeNum * (item + 1)))
    for item in range(0, 20):
        xZfData.append(str(rangeNum2 * item) + '-' + str(rangeNum2 * (item + 1)))
    xDzData.append('1万+')
    xPlData.append('1万+')
    xZfData.append('2千+')
    yDzData = [0 for x in range(len(xDzData))]  # 点赞y轴数据
    yPlData = [0 for x in range(len(xPlData))]  # 评论y轴数据
    yZfData = [0 for x in range(len(xZfData))]  # 转发y轴数据
    for article in articleList:
        for item in range(len(xDzData)):
            if int(article[4]) < rangeNum * (item + 1):
                yDzData[item] += 1
                break
            elif int(article[4]) > 10000:
                yDzData[len(xDzData) - 1] += 1
                break
            if int(article[3]) < rangeNum * (item + 1):
                yPlData[item] += 1
                break
            elif int(article[3]) > 10000:
                yPlData[len(xDzData) - 1] += 1
                break

    for article in articleList:
        for item in range(len(xZfData)):
            if int(article[2]) < rangeNum2 * (item + 1):
                yZfData[item] += 1
                break
            elif int(article[2]) > 2000:
                yZfData[len(xZfData) - 1] += 1
                break
    return render_template('articleDataAnalysis.html',
                           arcTypeList=arcTypeList,
                           defaultArcType=defaultArcType,
                           xDzData=xDzData,
                           yDzData=yDzData,
                           xPlData=xPlData,
                           yPlData=yPlData,
                           xZfData=xZfData,
                           yZfData=yZfData)


# ===== 原有代码：commentDataAnalysis 路由（未修改） =====
@pb.route('commentDataAnalysis')
def commentDataAnalysis():
    """
    微博评论数据分析
    :return:
    """
    commentList = commentDao.getAllComment()
    xDzData = []  # 点赞X轴数据
    rangeNum = 5
    for item in range(0, 20):
        xDzData.append(str(rangeNum * item) + '-' + str(rangeNum * (item + 1)))
    xDzData.append('1百+')
    yDzData = [0 for x in range(len(xDzData))]  # 点赞y轴数据
    genderDic = {'男': 0, '女': 0}
    for comment in commentList:
        for item in range(len(xDzData)):
            if int(comment[4]) < rangeNum * (item + 1):
                yDzData[item] += 1
                break
            elif int(comment[4]) > 100:
                yDzData[len(xDzData) - 1] += 1
                break
            if genderDic.get(comment[8], -1) != -1:
                genderDic[comment[8]] += 1
    genderData = [{'name': x[0], 'value': x[1]} for x in genderDic.items()]

    # 只读取前50条数据
    df = pd.read_csv(os.path.join(FENCI_DIR, "comment_fre.csv"), nrows=50)
    hotCommentwordList = [x[0] for x in df.values]
    str2 = ' '.join(hotCommentwordList)
    wordcloudUtil.genWordCloudPic(str2, 'comment_mask.jpg', 'comment_cloud.jpg')
    return render_template('commentDataAnalysis.html',
                           xDzData=xDzData,
                           yDzData=yDzData,
                           genderData=genderData)


# ===== 原有代码：articleCloud 路由（未修改） =====
@pb.route('articleCloud')
def articleCloud():
    """
    微博内容词云图
    :return:
    """
    # 只读取前50条数据
    df = pd.read_csv(os.path.join(FENCI_DIR, "article_fre.csv"), nrows=50)
    hotArticlewordList = [x[0] for x in df.values]
    str2 = ' '.join(hotArticlewordList)
    wordcloudUtil.genWordCloudPic(str2, 'article_mask.jpg', 'article_cloud.jpg')
    return render_template('articleCloud.html')


@pb.route('commentCloud')
def commentCloud():
    """
    微博评论词云图
    :return:
    """
    # 只读取前50条数据
    df = pd.read_csv(os.path.join(FENCI_DIR, "comment_fre.csv"), nrows=50)
    hotCommentwordList = [x[0] for x in df.values]
    str2 = ' '.join(hotCommentwordList)
    wordcloudUtil.genWordCloudPic(str2, 'comment_mask.jpg', 'comment_cloud.jpg')
    return render_template('commentCloud.html')


@pb.route('commentUserCloud')
def commentUserCloud():
    """
    微博评论用户词云图
    :return:
    """
    # 获取top50评论用户名
    top50CommentUserList = commentDao.getTopCommentUser()
    top50CommentUserNameList = [cu[0] for cu in top50CommentUserList]
    str = ' '.join(top50CommentUserNameList)
    wordcloudUtil.genWordCloudPic(str, 'comment_mask.jpg', 'comment_user_cloud.jpg')
    return render_template('commentUserCloud.html')


@pb.route('ipDataAnalysis')
def ipDataAnalysis():
    """
    微博IP分析
    :return:
    """
    # 获取评论来源地图数据
    from dao.commentDao import getCommentSourceMap
    raw_data = getCommentSourceMap()

    if raw_data is None:
        raw_data = []

    # 获取前10个地区的排名
    top_regions = raw_data[:10] if len(raw_data) >= 10 else raw_data

    # 计算总评论数
    total_comments = sum([count for _, count in raw_data]) if raw_data else 0

    # 转换为ECharts需要的数据格式
    map_data = []
    for province, count in raw_data:
        map_data.append({
            'name': str(province).strip(),
            'value': int(count) if count else 0
        })

    # 调试输出
    print(f"IP分析数据统计:")
    print(f"  原始数据条数: {len(raw_data)}")
    print(f"  地图数据条数: {len(map_data)}")
    print(f"  总评论数: {total_comments}")
    if raw_data:
        print(f"  前3条数据: {raw_data[:3]}")

    return render_template('ipDataAnalysis.html',
                           data_count=len(raw_data),
                           top_regions=top_regions,
                           total_comments=total_comments,
                           map_data=map_data)


@pb.route('sentimentAnalysis')
def sentimentAnalysis():
    """
    微博评论舆情分析
    :return:
    """
    from dao.commentDao import getAllComment

    # 检查模型是否加载成功
    if sentiment_analyzer is None:
        return render_template('sentimentAnalysis.html',
                               commentList=[],
                               stats={'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0},
                               error="情感分析模型加载失败，请检查模型路径")

    # 获取所有评论
    commentList = getAllComment()

    if commentList is None:
        commentList = []

    # 情感分析统计
    sentiment_stats = {
        'positive': 0,  # 正面
        'negative': 0,  # 负面
        'neutral': 0,  # 中性
        'total': 0  # 总数
    }

    analyzed_comments = []

    for comment in commentList[:1000]:
        if comment is None or len(comment) < 2:
            continue

        comment_data = list(comment)
        comment_text = str(comment_data[1]).strip() if len(comment_data) > 1 else ""

        if not comment_text:
            continue

        # 情感分析（替换 SnowNLP ↓）
        try:
            sentiment, confidence = sentiment_analyzer(comment_text)

            # 统计情感
            if sentiment == '正面':
                sentiment_stats['positive'] += 1
            elif sentiment == '负面':
                sentiment_stats['negative'] += 1
            else:
                sentiment_stats['neutral'] += 1

            sentiment_stats['total'] += 1
            comment_data.append(sentiment)
            analyzed_comments.append(comment_data)

        except Exception as e:
            print(f"评论情感分析错误: {e}")
            continue

    return render_template('sentimentAnalysis.html',
                           commentList=analyzed_comments,
                           stats=sentiment_stats)

