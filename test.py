import pymysql
from pyecharts import options as opts
from pyecharts.charts import Map
from pyecharts.globals import ThemeType


# ---------------------- 1. 数据库连接与数据查询 ----------------------
def get_source_data():
    """从数据库读取source字段并统计各省份数据量"""
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': 'db_weibo3',
        'charset': 'utf8mb4'
    }

    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()

        # 查询source字段并统计各地区数量
        sql = "SELECT source, COUNT(*) as count FROM t_comment WHERE source IS NOT NULL AND source != '' GROUP BY source"
        cursor.execute(sql)
        results = cursor.fetchall()

        data = []
        for row in results:
            province = row[0]
            count = row[1]

            if not province:
                continue

            province = str(province).strip()

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

            data.append((province, count))

        data.sort(key=lambda x: x[1], reverse=True)
        return data

    except Exception as e:
        print(f"数据库查询失败：{e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()


# ---------------------- 2. 生成地理分级设色地图 ----------------------
def generate_province_map():
    # 获取数据库数据
    data = get_source_data()

    if not data:
        print("无有效数据，无法生成地图")
        return

    print(f"共获取到 {len(data)} 个省份的数据")
    for province, count in data[:10]:
        print(f"{province}: {count}条评论")

    # 创建Map实例
    map_chart = Map(
        init_opts=opts.InitOpts(
            theme=ThemeType.LIGHT,
            width="1200px",
            height="800px"
        )
    )

    # 添加数据
    map_chart.add(
        series_name="评论来源数量",
        data_pair=data,
        maptype="china",
        is_roam=True,
        label_opts=opts.LabelOpts(is_show=True)  # 正确的位置设置标签
    )

    # 设置全局选项 - 确保这里没有label_opts
    map_chart.set_global_opts(
        title_opts=opts.TitleOpts(
            title="评论来源分布（按省份）",
            subtitle="数据来源：db_weibo3.t_comment",
            pos_left="center"
        ),
        visualmap_opts=opts.VisualMapOpts(
            is_show=True,
            type_="color",
            min_=min([d[1] for d in data]),
            max_=max([d[1] for d in data]),
            range_color=["#009900", "#FFFF00", "#FF9900", "#FF0000"],
            pos_left="left",
            pos_bottom="5%"
        )
        # 注意：这里没有label_opts参数！
    )

    # 生成HTML文件
    output_file = "province_comment_map.html"
    map_chart.render(output_file)
    print(f"\n地图已生成，文件名为：{output_file}")
    print(f"请用浏览器打开查看地图")


# 执行主函数
if __name__ == "__main__":
    generate_province_map()
