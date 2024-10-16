import dash
from dash import html, dcc, callback_context
import feffery_antd_components as fac
from dash.dependencies import Input, Output, State
import config
import json
from urllib.parse import unquote
from util import get_exif_data

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# 初始主题
app.layout =html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="theme-status"),  # 用于存储当前主题状态
    dcc.Store(id="albums-data"),  # 用于存储相册数据
    
    html.Div(
        id="main-container",
        children=[

            # 导航栏
            fac.AntdHeader(
                id="navbar",
                style={
                    "backgroundColor": "#f0f2f5",
                    "color": "black",
                    "backgroundImage": "linear-gradient(135deg, #f0f2f5 0%, #ffffff 100%)",
                    "padding": "10px",
                    "display": "flex",
                    "alignItems": "center",
                },
            ),
            # 内容区
            html.Div(id="page-content", style={"padding": "20px", "textAlign": "center"}),
            fac.AntdModal(id="modal-content", style={"maxWidth": "80%", "margin": "auto"}),
            dcc.Interval(
                id="interval-component", interval=60 * 1000, n_intervals=0
            ),  # 每60秒更新一次
        ],
        style={
            "minHeight": "100vh",
            "overflow": "hidden",  # 防止内容溢出
            "display": "flex",  # 使用 flexbox 布局
            "flexDirection": "column",  # 垂直排列
        },
    )
])




# 定时更新 JSON 数据的回调
@app.callback(
    Output("albums-data", "data"),
    Input("interval-component", "n_intervals"),  # 定时器触发
)
def update_albums_data(n):
    with open("albums.json", "r", encoding="utf-8") as f:
        albums_data = json.load(f)
    return albums_data


# 添加一个新的回调来获取当前主题状态
@app.callback(Output("theme-status", "data"), Input("theme-switch", "checked"))
def update_theme_status(is_dark_mode):
    return is_dark_mode


# 回调函数用于切换主题
@app.callback(
    [
        Output("main-container", "style"),
        Output("navbar", "style"),
    ],
    Input("theme-switch", "checked"),
)
def toggle_theme(is_dark_mode):
    if is_dark_mode:
        common_style = {
            "backgroundColor": "#1c1c1e",
            "color": "white",
            "minHeight": "100vh",
            "backgroundImage": "linear-gradient(135deg, #1c1c1e 0%, #2c2c2e 100%)",
        }
        navbar_style = {
            "backgroundColor": "#1c1c1e",
            "color": "white",
            "backgroundImage": "linear-gradient(135deg, #1c1c1e 0%, #2c2c2e 100%)",
        }

    else:
        common_style = {
            "backgroundColor": "#f0f2f5",
            "color": "black",
            "minHeight": "100vh",
            "backgroundImage": "linear-gradient(135deg, #f0f2f5 0%, #ffffff 100%)",
        }
        navbar_style = {
            "backgroundColor": "#f0f2f5",
            "color": "black",
            "backgroundImage": "linear-gradient(135deg, #f0f2f5 0%, #ffffff 100%)",
        }

    return common_style, {
        **navbar_style,
        "padding": "10px",
        "display": "flex",
        "alignItems": "center",
    }


def album_card_style(is_dark_mode):
    if is_dark_mode:
        card_style = {
            "backgroundColor": "rgba(40, 40, 40, 0.9)",  # 更深的背景色
            "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.3)",  # 更柔和的阴影
            "border": "none",  # 去掉边框
            "borderRadius": "8px",
            "color": "white",  # 文字颜色为白色
            "transition": "all 0.3s ease",
        }
    else:
        card_style = {
            "backgroundColor": "rgba(255, 255, 255, 0.4)",  # 原有的背景色
            "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",  # 原有的阴影
            "borderRadius": "8px",
            "color": "black",  # 文字颜色为黑色
            "transition": "all 0.3s ease",
        }

    return card_style


@app.callback([Output("navbar", "children")], [Input("url", "pathname"), Input("theme-status", "data")])
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
                        items=[{"title": "主页", "href": "/"}, {"title": album_name}],
                        style={"marginBottom": "0"},
                    ),
                    fac.AntdSwitch(
                        id="theme-switch",
                        checkedChildren="🌙",
                        unCheckedChildren="☀️",
                        style={"marginLeft": "auto"},
                    ),
                ],
                style={"display": "flex", "alignItems": "center", "width": "100%"},
            )
        ]


@app.callback(
    [Output("modal-content", "children"), Output("modal-content", "visible")],
    [Input({"type": "image-card", "index": dash.dependencies.ALL}, "n_clicks")],
    [
        State("albums-data", "data"),
        State("url", "pathname"),
    ],
)
def show_image_modal(n_clicks_list, albums_data, pathname):
    if not any(n_clicks_list):
        return dash.no_update, False
    print(n_clicks_list)
    # 获取被点击的图片索引
    clicked_index = n_clicks_list.index(max(n_clicks_list))

    album_name = unquote(pathname.strip("/"))
    if album_name in albums_data:
        album = albums_data[album_name]
        image_url = album["images"][clicked_index]
        image_data = get_exif_data(image_url)
        return (
            html.Div(
                [
                    fac.AntdImage(
                        src=image_url,
                        style={"width": "100%", "marginBottom": "20px"},
                        preview=False,
                    ),
                    html.Div(
                        [html.P(f"{key}: {item}") for key, item in image_data.items()],
                        style={"textAlign": "left"},
                    ),
                ]
            ),
            True,
        )

    return dash.no_update, False


# 在布局中使用 html.Div 包围图片
def create_image_card(image_url, index):
    return html.Div(
        fac.AntdImage(
            src=image_url,
            preview=False,
            style={"width": "100%", "marginBottom": "10px"},
        ),
        id={"type": "image-card", "index": index},
        n_clicks=0,
        style={"cursor": "pointer"},
    )


@app.callback(
    Output("page-content", "children"),
    [
        Input("url", "pathname"),
        Input("theme-status", "data"),
        Input("albums-data", "data"),
    ],
)
def display_page(pathname, is_dark_mode, albums_data):
    print('theme',is_dark_mode)
        # 确保在切换 URL 时保持主题状态
    if is_dark_mode is None:
        is_dark_mode = False  # 默认主题为亮色模式

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
                    span=6,
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
        images_per_column = num_images // 3 + (num_images % 3 > 0)  # 每列的图片数量

        # 将图片分为三组
        columns = [
            album["images"][i : i + images_per_column]
            for i in range(0, num_images, images_per_column)
        ]
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
                            span=6,  # 每列占据 8/24 的宽度
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


if __name__ == "__main__":
    app.run_server(debug=True)
