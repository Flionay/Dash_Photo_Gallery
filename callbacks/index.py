
import dash
from dash import html, dcc, callback_context
import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash.dependencies import Input, Output, State
from urllib.parse import unquote
from server import app 
import config
import json
from .photos import album_card_style,create_image_card


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
                style={"marginBottom": "16px","border": "10px"},  # 每列底部间距
            )
            for column in columns
        ],
        justify="center",
        gutter=[16, 16],  # 设置网格间距
    )

# 展示随机图片
def display_photos_random(photos):
    return html.Div([create_image_card(photo, index=i) for i, photo in enumerate(photos)])


# 展示相册
def display_photos_albums(albums_data, is_dark_mode):
    card_style = album_card_style(is_dark_mode=is_dark_mode)
    return fac.AntdRow(
            [
                fac.AntdCol(
                    dcc.Link(
                        [
                            fac.AntdCard(
                                fac.AntdCardMeta(
                                    # description=album['desc'],
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
                    ),
                    span=8,
                    style={"marginBottom": "16px"},
                )
                for album_name, album in albums_data.items()
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
    Output("page-content", "children",allow_duplicate=True),
    [
        Input("url", "pathname"),
        # 
        Input("albums-data", "data"),
        Input("theme-status", "data"),
    ],
#    State("theme-status", "data"),
)
def display_page(pathname, albums_data, is_dark_mode,):
    
    if pathname == "/":
        return display_photos(albums_data)
    
        
    elif pathname == "/albums":
        return display_photos_albums(albums_data, is_dark_mode)

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