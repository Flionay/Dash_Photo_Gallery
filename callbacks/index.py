
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


[
    fac.AntdFloatButton(
        id='float-button-basic-event', description='点我', type='primary'
    ),
    fac.AntdText(id='float-button-basic-event-output'),
]

@app.callback(
    Output('float-button-basic-event-output', 'children'),
    Input('float-button-basic-event', 'nClicks'),
    prevent_initial_call=True,
)
def float_button_basic_event(nClicks):
    return f'nClicks: {nClicks}'



# 切换网页，改变navbar
@app.callback(
    [Output("navbar", "children")],
    [Input("url", "pathname"),],
    State("theme-status", "data")
)
def update_navbar(pathname, is_dark_mode):
    if pathname == "/":
        return [
            html.Div(
                [
                    fac.AntdImage(
                        src=config.LOGO_PATH,
                        preview=False,
                        style={
                            "height": "30px",
                            "width": "30px",
                            "borderRadius": "50%",
                            "overflow": "hidden",
                            "marginRight": "10px",
                        },
                    ),
                    html.Span("Photo Gallery", style={"fontSize": "20px"}),
                    fac.AntdSwitch(
                        id="theme-switch",
                        checked=is_dark_mode,
                        checkedChildren="🌙",
                        unCheckedChildren="☀️",
                        style={"marginLeft": "auto"},
                    ),
                ],
                style={"display": "flex", "alignItems": "center", "width": "100%"},
            )
        ]
    else:
        album_name = unquote(pathname.strip("/"))
        return [
            html.Div(
                [
                    fac.AntdBreadcrumb(
                        items=[{"title": "主页", "href": "/",}, {"title": album_name}],
                        style={"marginBottom": "0","fontSize":"18px","color": "white" if is_dark_mode else "black"},
                    ),
                    fac.AntdSwitch(
                        id="theme-switch",
                        checked=is_dark_mode,
                        checkedChildren="🌙",
                        unCheckedChildren="☀️",
                        style={"marginLeft": "auto"},
                    ),
                ],
                style={"display": "flex", "alignItems": "center", "width": "100%"},
            )
        ]



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
    
    card_style = album_card_style(is_dark_mode=is_dark_mode)

    if pathname == "/":
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

    elif unquote(pathname.strip("/")) in albums_data:
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