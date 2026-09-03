# 基于深度学习的微博舆情分析系统

基于 Flask、MySQL、BERT/LSTM 和词云可视化的微博舆情分析系统，支持微博文章、评论、热词、评论来源及情感分析。

## 主要功能

- 用户注册、登录和权限控制
- 微博文章、评论数据展示
- 热词统计与词云生成
- 文章类型、评论及 IP 来源分析
- BERT + BiLSTM 二分类情感分析
- 爬虫数据抓取及 MySQL 持久化

## 安装依赖

```powershell
cd "C:\Users\Yuikai\Desktop\Context\Gra\winter"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 路径配置

项目根目录绝对路径：

```text
C:\Users\Yuikai\Desktop\Context\Gra\winter
```

BERT 基础模型默认路径：

```text
C:\Users\Yuikai\Desktop\Gra\BERT1
```

`best_model.pth` 已删除，因为原文件约 394 MB，超过 GitHub 普通文件 100 MB 的限制。缺少该权重时，应用仍可启动，但情感分析功能会提示模型未加载。若要启用情感分析，请将模型权重放回：

```text
C:\Users\Yuikai\Desktop\Context\Gra\winter\saved_models\best_model.pth
```

数据库默认配置为 `localhost:3306/db_weibo3`，用户名为 `root`。生产环境请修改 `util/dbUtil.py` 和 `spider/main.py`，不要提交真实密码。

## 启动项目

```powershell
cd "C:\Users\Yuikai\Desktop\Context\Gra\winter"
python app.py
```

访问：<http://127.0.0.1:5000/user/login>

## 分词处理

```powershell
python fenci\articleFenci.py
python fenci\commentFenci.py
```

## Git 推送

```powershell
git add .
git commit -m "完善 README 和路径配置"
git push -u origin main
```
