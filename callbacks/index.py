import dash
from dash import html, dcc, callback_context
import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash.dependencies import Input, Output, State
from urllib.parse import unquote
from server import app
from util import get_exif_data
from dash_iconify import DashIconify
import config
import json
from .photos import (
    album_card_style,
    create_image_card,
)


def create_image_metadata(image_data, album_name):
    gutter_item = "0px 40px"
    
    return html.Div(
        [
            html.Div(
                [
                    html.P("相机", className="text_row_gray"),
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "color":"gray"},
                        children=[
                            DashIconify(
                                icon="solar:camera-broken",
                                style={"fontSize": "16px", "marginRight": "5px", "color":"gray"},
                            ),
                            html.P(
                                f"{image_data.get('设备', '未知')}",
                                style={"margin": "0", "fontSize": "14px", "color":"gray"},
                            ),
                        ],
                    ),
                ],
                className="image_meta_item",
                style={"margin": gutter_item},
            ),
            html.Div(
                [
                    html.P("参数", className="text_row_gray"),
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "color":"gray"},
                        children=[
                            DashIconify(
                                icon="fluent-mdl2:focal-point",
                                style={"fontSize": "16px", "marginRight": "5px", "color":"gray"},
                            ),
                            html.P(
                                f"{image_data.get('焦距', '未知')}",
                                style={"margin": "0", "fontSize": "14px", "marginRight": "10px", "color":"gray"},
                            ),
                            DashIconify(
                                icon="ion:aperture-outline",
                                style={"fontSize": "16px", "marginRight": "5px"},
                            ),
                            html.P(
                                f"{image_data.get('光圈', '未知')}",
                                style={"margin": "0", "fontSize": "14px", "marginRight": "10px"},
                            ),
                            DashIconify(
                                icon="material-symbols:shutter-speed-minus-outline",
                                style={"fontSize": "16px", "marginRight": "5px", "color":"gray"},
                            ),
                            html.P(
                                f"{image_data.get('快门速度', '未知')}",
                                style={"margin": "0", "fontSize": "14px", "marginRight": "10px", "color":"gray"},
                            ),
                            DashIconify(
                                icon="carbon:iso-filled",
                                style={"fontSize": "16px", "marginRight": "5px", "color":"gray"},
                            ),
                            html.P(
                                f"{image_data.get('ISO', '未知')}",
                                style={"margin": "0", "fontSize": "14px", "color":"gray"},
                            ),
                        ],
                    ),
                ],
                className="image_meta_item",
                style={"margin": gutter_item},

            ),
            html.Div(
                [
                    html.P("地点", className="text_row_gray"),
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "color":"gray"},
                        children=[
                            DashIconify(
                                icon="fa6-solid:map-location",
                                style={"fontSize": "16px", "marginRight": "5px", "color":"gray"},
                            ),
                            html.P(
                                f"{album_name}",
                                style={"margin": "0", "fontSize": "14px", "color":"gray"},
                            ),
                        ],
                    ),
                ],
                className="image_meta_item",
                style={"margin": gutter_item},
            ),
            html.Div(
                [
                    html.P("镜头", className="text_row_gray"),
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "color":"gray"},
                        children=[
                            DashIconify(
                                icon="arcticons:lensa",
                                style={"fontSize": "16px", "marginRight": "5px", "color":"gray"},
                            ),
                            html.P(
                                f"{image_data.get('镜头', '未知').split('|')[0]}",
                                style={"margin": "0", "fontSize": "14px", "color":"gray"},
                            ),
                        ],
                    ),
                ],
                className="image_meta_item",
                style={"margin": gutter_item},
            ),
        ],
        style={
            "display": "flex",
            "flexWrap": "wrap",
            "alignItems": "center",
            "justifyContent": "center",
            "padding": "10px",
            "background": "rgba(0, 0, 0, 0.0)",
            "borderRadius": "8px"
        },
    )



# 展示精选图片，按时间显示
def display_photos(albums_data):
    all_photos = []

    # 遍历 albums_data，提取所有照片
    for album in albums_data.values():
        all_photos.extend(album["images"])

    # 将照片分配到列中
    num_images = len(all_photos)
    columns = [[] for _ in range(5)]  # 假设每行有 3 列

    for i in range(num_images):
        columns[i % 5].append(all_photos[i])  # 均匀分配到 3 列

    # 返回照片的 HTML 组件
    return fac.AntdRow(
        [
            fac.AntdCol(
                html.Div(
                    [
                        create_image_card(image_url, index=image_url.split("/")[-1])
                        for image_url in column
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                    },  # 垂直排列
                ),
                span=4,  # 每列占据 8/24 的宽度
                style={"marginBottom": "16px", "border": "10px"},  # 每列底部间距
            )
            for column in columns
        ],
        justify="center",
        gutter=[16, 16],  # 设置网格间距
    )


# 展示随机图片
def display_photos_random(albums_data):

    def get_album_name(image_url):
        for album_name, album in albums_data.items():
            if image_url in album["images"]:
                return album_name

    import random  # 导入随机模块

    # 提取所有图片
    all_photos = []
    for album in albums_data.values():
        all_photos.extend(album["images"])

    # all_photos = all_photos[:5]
    random.shuffle(all_photos)  # 随机打乱图片顺序

    return (
        fac.AntdSpace(
            [
                fuc.FefferyLazyLoad(
                    html.Div(
                        fac.AntdSpace(
                            [
                                fac.AntdImage(
                                    src=photo,
                                    style={
                                        "width": "100%",
                                        "maxHeight": "95vh",  # 设置最大高度为视口高度的80%
                                        # "borderRadius": "2px",    
                                        "objectFit": "contain",  # 保持比例，适应容器
                                        "display": "block",  # 使图片为块级元素
                                        "padding": "0px",  # 自动水平居中
                                         "boxShadow": "0 4px 18px rgba(0, 0, 0, 0.2)"
                                    },  # 充满宽度，保持比例
                                    preview=False,
                                ),
                                html.Div(create_image_metadata(
                                    get_exif_data(photo), get_album_name(photo)
                                ),style={"margin":"0px 0px 10px 0px","width": "100%"}),  
                            ],
                            direction="vertical",
                        ),
                        # style={"boxShadow": "0 4px 18px rgba(0, 0, 0, 0.2)",},  
                    ),
                    height=1050,
                    throttle=50,  # 节流防抖延时，单位：毫秒
                )
                for photo in all_photos[:5]
            ],
            direction="vertical",
        ),
    )


# 展示相册
def display_photos_albums(albums_data, is_dark_mode):
    card_style = album_card_style(is_dark_mode=is_dark_mode)
    columns = [[] for _ in range(4)]  # 假设每行有 5 列

    # 将相册分配到列中
    for i, (album_name, album) in enumerate(albums_data.items()):
        columns[i % 4].append(
            dcc.Link(
                [
                    fac.AntdCard(
                        fac.AntdCardMeta(
                            title=album["title"],
                            style={"textAlign": "center"},
                        ),
                        coverImg={
                            "alt": "demo picture",
                            "src": album["images"][0],
                        },
                        hoverable=True,
                        style={
                            **card_style,
                            "margin": "10px",
                            "display": "inline-block",
                        },
                        headStyle={"display": "none"},
                    )
                ],
                href=f"/{album_name}",
            )
        )

    return fac.AntdRow(
        [
            fac.AntdCol(
                html.Div(
                    column,
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                    },
                ),
                span=5,
                style={"marginBottom": "16px"},
            )
            for column in columns
        ],
        justify="center",
    )


def display_photos_in_album(albums_data, pathname):
    album_name = unquote(pathname.strip("/"))
    album = albums_data[album_name]
    # 计算每列的图片数量
    num_images = len(album["images"])
    images_per_column = num_images // 3  # 每列的基本图片数量
    remainder = num_images % 3  # 余数
    print(remainder)
    # 初始化列
    columns = [[] for _ in range(3)]

    # 将图片分配到列中
    for i in range(num_images):
        columns[i % 3].append(album["images"][i])  # 均匀分配

    return html.Div(
        [
            html.H2(album["title"], style={"textAlign": "center"}),
            html.P(
                album["desc"],
                style={"textAlign": "center", "marginBottom": "40px"},
            ),
            fac.AntdRow(
                [
                    fac.AntdCol(
                        html.Div(
                            [
                                create_image_card(
                                    image_url, index=image_url.split("/")[-1]
                                )
                                for image_url in column
                            ],
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "alignItems": "center",
                            },  # 垂直排列
                        ),
                        span=8,  # 每列占据 8/24 的宽度
                        style={"marginBottom": "16px"},  # 每列底部间距
                    )
                    for column in columns
                ],
                justify="center",
                gutter=[16, 16],  # 设置网格间距
            ),
        ]
    )


# 根据url显示不同页面
@app.callback(
    Output("page-content", "children", allow_duplicate=True),
    [
        Input("url", "pathname"),
        Input("albums-data", "data"),
        Input("theme-status", "data"),
    ],
)
def display_page(
    pathname,
    albums_data,
    is_dark_mode,
):

    if pathname == "/": #按照评分 显示精选图片
        return display_photos_random(albums_data)

    elif pathname == "/albums":
        return display_photos_albums(albums_data, is_dark_mode)

    elif pathname == "/random":
        return display_photos(albums_data) #所有图片预览

    elif unquote(pathname.strip("/")) in albums_data:
        return display_photos_in_album(albums_data, pathname)
    else:
        return html.Div(
            [
                html.H2("404 - Page Not Found", style={"textAlign": "center"}),
                html.P(
                    "The page you are looking for does not exist.",
                    style={"textAlign": "center"},
                ),
            ]
        )
