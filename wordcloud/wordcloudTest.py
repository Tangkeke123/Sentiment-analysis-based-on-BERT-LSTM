import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
from wordcloud import WordCloud


def genWordCloudPic(str, maskImg, outImg):
    """
    生成云图
    :param str: 词云 空格隔开
    :param maskImg: 形状模板图片
    :param outImg: 输出的词云图片文件名
    :return:
    """
    img = Image.open(maskImg)
    img_arr = np.array(img)  # 转成图片数组对象
    wc = WordCloud(
        width=800,
        height=600,
        background_color='white',
        colormap='Blues',
        font_path='STHUPO.TTF',
        mask=img_arr
    )
    wc.generate_from_text(str)

    # 绘制图片
    plt.imshow(wc)

    # 不显示坐标轴
    plt.axis('off')

    plt.savefig(outImg, dpi=500)


if __name__ == '__main__':
    text = "牛掰2 牛逼 大佬 我去 张三 卡卡 嘿嘿 哈哈 生成 商城 气死我了 不去 就不要 好滴 骄傲 好的 大战 发展 求生 共存 火了 刘安 伙计 火鸡 打火机"
    genWordCloudPic(text, 'comment_mask.jpg', 'wordcloud_test2.jpg')
