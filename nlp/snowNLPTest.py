from snownlp import SnowNLP

if __name__ == '__main__':
    pos_text = "这家餐厅环境优雅，菜品新鲜！"
    neg_text = "服务差，价格贵，再也不来了。"
    pos_score = SnowNLP(pos_text).sentiments
    neg_score = SnowNLP(neg_text).sentiments
    print(pos_score)
    print(neg_score)
