import dash
from dash import html, dcc, callback_context
import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash.dependencies import Input, Output, State
import config
import json

from util import get_exif_data
from dash_iconify import DashIconify
from server import app

import dash
from callbacks.index import *
from callbacks.photos import *
from callbacks.theme import *

with open("albums.json", "r", encoding="utf-8") as f:
    albums_data = json.load(f)

# 初始主题
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="theme-status", storage_type='local'),
        dcc.Store(id="albums-data",data=albums_data),
        html.Div(
            id="main-container",
            children=[
                # 导航栏
                fac.AntdHeader(
                    id="navbar",
                    style={
                        "backgroundColor": "#ffffff",  # 使用白色背景
                        "color": "#333333",  # 深色文本
                        "padding": "20px 40px",  # 增加内边距
                        "boxShadow": "0 2px 10px rgba(0, 0, 0, 0.1)",  # 添加阴影
                        "display": "flex",
                        "alignItems": "center",
                    },
                ),
                # 内容区
                html.Div(
                    id="page-content", style={"padding": "40px", "textAlign": "center"}
                ),
                fac.AntdModal(
                    id="modal-content",
                    style={
                        "maxWidth": "90%",
                        "margin": "auto",
                        "padding": "0px",
                        "backgroundColor": "rgba(0, 0, 0, 0.0)",

                    },
                    maskStyle={
                        "backdropFilter": "blur(10px)",  # 设置毛玻璃效果
                        # "backgroundColor": "rgba(255, 255, 255, 0.5)",  # 半透明背景
                    },
                    width="60vw",
                    centered=True,
                ),
                dcc.Interval(
                    id="interval-component", interval=60 * 1000, n_intervals=0
                ),
            ],
            style={
                "minHeight": "100vh",
                "overflow": "hidden",
                "display": "flex",
                "flexDirection": "column",
                "backgroundColor": "#f9f9f9",  # 背景色
            },
        ),
    ]
)

# 定时更新 JSON 数据的回调
@app.callback(
    Output("albums-data", "data"),
    Input("interval-component", "n_intervals"),  # 定时器触发
)
def update_albums_data(n):
    print("定时触发")
    with open("albums.json", "r", encoding="utf-8") as f:
        albums_data = json.load(f)
    return albums_data


if __name__ == "__main__":
    app.run_server(debug=True)

