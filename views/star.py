# views/rating.py
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from server import app
import feffery_antd_components as fac

import json
import os


def get_exif_star(exif_data,image_url):

        
    image_id = '/'.join(image_url.split('/')[-2:]).split('.')[0]
    for exif_key in exif_data.keys():
        # 去掉 exif_key 的扩展名
        exif_key_without_ext = os.path.splitext(exif_key)[0]
        
        # 比较最后两个部分
        if image_id == exif_key_without_ext:
            star = exif_data[exif_key].get('star',0)
            return float(star)
        
    else:
        return 0


def rating_layout(albums_data):
    
    with open('exif_data.json', 'r', encoding='utf-8') as f:
        exif_data = json.load(f)
        
    image_url_list = []
    for album_name in albums_data.keys():
        album_images = albums_data[album_name]['images']
        image_url_list+=album_images
    
    # 创建行和列布局
    row = fac.AntdRow(
        gutter=16,  # 设置列间距
        justify='center',  # 居中对齐
        children=[
            fac.AntdCol(
                span=5,  # 每列占6个格子，总共4列（24格）
                children=[
                    html.Div(
                        [
                            fac.AntdImage(
                                src=image_url,
                                preview=False,
                                style={"width": "100%", "height": "auto"},
                            ),
                            fac.AntdRate(
                                id={'type': 'rating', 'index': f"{image_url}|{idx}"},  # 使用图片URL作为唯一标识
                                allowHalf=True,
                                value=get_exif_star(exif_data, image_url),  # 获取评分
                                style={"marginTop": "10px","marginBottom": "20px"},
                            ),
                        ],
                        style={"textAlign": "center"},  # 居中对齐
                    )
                ]
            ) for idx, image_url in enumerate(image_url_list)  # 假设每个相册都有一个 "images" 列表
        ]
    )

    return html.Div(children=row)  # 返回包含所有行的Div

