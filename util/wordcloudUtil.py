import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
from wordcloud import WordCloud


# def genWordCloudPic(str, maskImg, outImg):
#     """
#     生成云图
#     :param str: 词云 空格隔开
#     :param maskImg: 形状模版图片
#     :param outImg: 输出的词云图文件名
#     :return:
#     """
#     img = Image.open('./static/' + maskImg)  # 形状模版图片
#     img_arr = np.array(img)  # 转成图片数组对象
#     wc = WordCloud(
#         width=2000,
#         height=1000,
#         scale=4,
#         background_color='white',
#         colormap='Blues',
#         font_path='STHUPO.TTF',
#         mask=img_arr
#     )
#     wc.generate_from_text(str)
#
#     # 绘制图片
#     plt.imshow(wc)
#
#     # 不显示坐标轴
#     plt.axis('off')
#
#     plt.savefig('./static/' + outImg, dpi=500)
def genWordCloudPic(str, maskImg, outImg):
    """
    生成云图（矩形，不使用蒙版）
    :param str: 词云 空格隔开
    :param maskImg: 形状模版图片（已不使用，可保留参数但忽略）
    :param outImg: 输出的词云图文件名
    :return:
    """
    wc = WordCloud(
        width=2000,
        height=1000,
        scale=4,  # 实际图片尺寸 = width*scale × height*scale = 8000×4000
        background_color='white',
        colormap='Blues',
        font_path='STHUPO.TTF'
        # 去掉 mask 参数
    )
    wc.generate_from_text(str)
    wc.to_file('./static/' + outImg)  # 直接保存，避免 matplotlib 缩放
