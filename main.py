import dash
from dash import html, dcc, callback_context
import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash.dependencies import Input, Output, State
import config
import json
import oss2
import os
from flask import request
from util import get_exif_data
from dash_iconify import DashIconify
from server import app

import dash
from callbacks.index import *
from callbacks.photos import *
from callbacks.theme import *
from callbacks.star import *
from views.navbar import render_navbar

with open("albums.json", "r", encoding="utf-8") as f:
    albums_data = json.load(f)


from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 初始主题
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="theme-status", storage_type='local'),
        dcc.Store(id="albums-data",data=albums_data),
        dcc.Store(id="is-logged-in",data=False,storage_type='local'),
        dcc.Store(id="image_modal"),
        html.Div(
            id="rating-output",
        ),
        html.Div(
            id="like-output",
        ),
        
        html.Div(
            id="main-container",
            children=[
                # 导航栏
                render_navbar(),
                # 内容区
                html.Div(
                    id="page-content", style={"padding": "40px", "textAlign": "center"}
                ),
                fac.AntdModal(
                    id="modal-content",
                    style={
                        "maxWidth": "95%",
                        # "width": "90vw",
                        "margin": "auto",
                        "padding": "0px",
                        "backgroundColor": "rgba(0, 0, 0, 0.0)",

                    },
                    maskStyle={
                        "backdropFilter": "blur(10px)",  # 设置毛玻璃效果
                        # "backgroundColor": "rgba(255, 255, 255, 0.5)",  # 半透明背景
                    },
                    width="85vw",
                    centered=True,
                ),
                # dcc.Interval(
                #     id="interval-component", interval=60 * 1000, n_intervals=0
                # ),
            ],
            style={
                "minHeight": "100vh",
                "overflow": "hidden",
                "display": "flex",
                "flexDirection": "column",
                "backgroundColor": "#f9f9f9",  # 背景色
            },
        ),
    ],
    id="main-layout",
)

# 定时更新 JSON 数据的回调
@app.callback(
    Output("albums-data", "data"),
    Input("url", "pathname"),  # 用户刷新页面时触发
)
def update_app_albums_data(pathname):
    print("用户刷新触发")
    with open("albums.json", "r", encoding="utf-8") as f:
        albums_data = json.load(f)
    return albums_data






if __name__ == "__main__":
    app.run_server(debug=False)