import dash
from dash import html, dcc, callback_context
import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash.dependencies import Input, Output, State
import config
import json
from urllib.parse import unquote
from util import get_exif_data

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# 初始主题
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="theme-status"),
        dcc.Store(id="albums-data"),
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
                        # "backgroundColor": "rgba(255, 255, 255, 0.0)",
                    },
                    maskStyle={
                        "backdropFilter": "blur(10px)",  # 设置毛玻璃效果
                        # "backgroundColor": "rgba(255, 255, 255, 0.5)",  # 半透明背景
                    },
                    width="80vw",
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


# 修改卡片样式
def album_card_style(is_dark_mode):
    if is_dark_mode:
        card_style = {
            "backgroundColor": "rgba(40, 40, 40, 0.9)",
            "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.2)",  # 更柔和的阴影
            "border": "none",
            "borderRadius": "12px",  # 更圆的边角
            "color": "white",
            "transition": "all 0.3s ease",
        }
    else:
        card_style = {
            "backgroundColor": "rgba(255, 255, 255, 0.9)",  # 更清新的背景色
            "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.1)",  # 更柔和的阴影
            "borderRadius": "12px",
            "color": "black",
            "transition": "all 0.3s ease",
        }

    return card_style


@app.callback(
    [Output("navbar", "children")],
    [Input("url", "pathname"), Input("theme-status", "data")],
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
    [Output("modal-content", "children"), Output("modal-content", "visible"),Output("interval-component","disabled")],
    [Input({"type": "image-card", "index": dash.dependencies.ALL}, "n_clicks")],
    [
        State("albums-data", "data"),
        State("url", "pathname"),
    ],
)
def show_image_modal(n_clicks_list, albums_data, pathname):
    if not any(n_clicks_list):
        return dash.no_update, False, False
    ctx = callback_context
    # if not ctx.triggered:
    #     return dash.no_update, False

    # 解析 prop_id
    prop_id = ctx.triggered[0]["prop_id"]
    # 获取被点击的图片索引
    # print(prop_id[:-9])
    clicked_image_name = eval(prop_id[:-9])["index"]  # 获取 index 的值
    print(clicked_image_name)
    album_name = unquote(pathname.strip("/"))
    if album_name in albums_data:
        album = albums_data[album_name]
        for image_u in album["images"]:
            if clicked_image_name in image_u:
                print(image_u)
                image_url = image_u
        # image_url = [image_u for image_u in album["images"] if clicked_image_name in image_u][0] # 获取被点击的图片地址
        image_data = get_exif_data(image_url)
        return (
            html.Div(
                [
                    fac.AntdImage(
                        src=image_url,
                        style={
                            "width": "100%",
                            "height": "auto",
                            "borderRadius": "8px",
                        },  # 充满宽度，保持比例
                        preview=False,
                    ),
                    html.Div(
                        style={
                            "display": "flex",
                            "justifyContent": "space-between",
                            "padding": "30px",
                            # "background": "rgba(255, 255, 255, 0.0)",
                            "borderRadius": "8px",
                            # "boxShadow": "0 2px 10px rgba(0, 0, 0, 0.1)",
                        },
                        children=[
                            html.Div(
                                [
                                    html.P(
                                        "相机",  # 第一排放两个字“相机”
                                       className="text_row"
                                    ),
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                        },
                                        children=[
                                            fac.AntdIcon(
                                                icon="antd-camera",  # 使用 Antd 图标
                                                style={
                                                    "fontSize": "16px",
                                                    "marginRight": "5px",
                                                },
                                            ), 
                                            html.P(
                                                f"{image_data.get('设备', '未知')}",  # 获取到的设备信息
                                                style={
                                                    "margin": "0",
                                                    "fontSize": "14px",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                                
                            ),
                            html.Div(
                                [
                                    html.P(
                                        "参数", 
                                       className="text_row"
                                    ),
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                        },
                                        children=[
                                            fac.AntdIcon(
                                                icon="pi-eye",  # 使用 Antd 图标
                                                style={
                                                    "fontSize": "16px",
                                                    "marginRight": "5px",
                                                },
                                            ), 
                                            html.P(
                                                f"{image_data.get('焦距', '未知')}",  # 获取到的设备信息
                                                style={
                                                    "margin": "0",
                                                    "fontSize": "14px",
                                                    "marginRight": "10px"
                                                },
                                            ),
                                            
                                            fac.AntdIcon(
                                                icon="pi-crosshair",  # 使用 Antd 图标
                                                style={
                                                    "fontSize": "16px",
                                                    "marginRight": "5px",
                                                },
                                            ), 
                                            html.P(
                                                f"{image_data.get('光圈', '未知')}",  # 获取到的设备信息
                                                style={
                                                    "margin": "0",
                                                    "fontSize": "14px",
                                                    "marginRight": "10px"
                                                },
                                            ),
                                            
                                            fac.AntdIcon(
                                                icon="md-restore",  # 使用 Antd 图标
                                                style={
                                                    "fontSize": "16px",
                                                    "marginRight": "5px",
                                                },
                                            ), 
                                            html.P(
                                                f"{image_data.get('快门速度', '未知')}",  # 获取到的设备信息
                                                style={
                                                    "margin": "0",
                                                    "fontSize": "14px",
                                                    "marginRight": "10px"
                                                },
                                            ),
                                            
                                               fac.AntdIcon(
                                                icon="md-restore",  # 使用 Antd 图标
                                                style={
                                                    "fontSize": "16px",
                                                    "marginRight": "5px",
                                                },
                                            ), 
                                            html.P(
                                                f"{image_data.get('ISO', '未知')}",  # 获取到的设备信息
                                                style={
                                                    "margin": "0",
                                                    "fontSize": "14px",
                                                    "marginRight": "10px"
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                                className="image_meta_item",
                            ),
                            html.Div(
                                [
                                html.P(
                                        "地点",  # 第一排放两个字“相机”
                                       className="text_row"
                                    ),
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                        },
                                        children=[
                                            fac.AntdIcon(
                                                icon="pi-map-pin",  # 使用 Antd 图标
                                                style={
                                                    "fontSize": "16px",
                                                    "marginRight": "5px",
                                                },
                                            ), 
                                            html.P(
                                                f"{image_data.get('地点', '未知')}",  # 获取到的设备信息
                                                style={
                                                    "margin": "0",
                                                    "fontSize": "14px",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                              [
                                html.P(
                                        "镜头",  # 第一排放两个字“相机”
                                       className="text_row"
                                    ),
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                        },
                                        children=[
                                            fac.AntdIcon(
                                                icon="pi-map-pin",  # 使用 Antd 图标
                                                style={
                                                    "fontSize": "16px",
                                                    "marginRight": "5px",
                                                },
                                            ), 
                                            html.P(
                                                f"{image_data.get('镜头', '未知').split('|')[0]}",  # 获取到的设备信息
                                                style={
                                                    "margin": "0",
                                                    "fontSize": "14px",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ]
            ),
            True,True
        )

    return dash.no_update, False, False


# 在布局中使用 html.Div 包围图片
def create_image_card(image_url, index):
    return html.Div(
        fuc.FefferyDiv(
            fac.AntdImage(
                src=image_url,
                preview=False,
                style={"width": "100%", "height": "100%", "marginBottom": "0px"},
            ),
            className={
                "&:hover": {
                    "transform": "scale(1.02)",  # /* 鼠标悬停时放大 5% */
                    "box-shadow": "0 4px 15px rgba(0, 0, 0, 0.5)",  # /* 添加阴影效果 */
                }
            },
            style={"position": "relative"},
        ),
        id={"type": "image-card", "index": index},
        n_clicks=0,
        style={
            "cursor": "pointer",
            "transition": "transform 0.5s cubic-bezier(0.25, 0.1, 0.25, 1), box-shadow 0.5s cubic-bezier(0.25, 0.1, 0.25, 1)",  # 使用自定义缓动函数
            "marginBottom": "20px",
        },
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
    print("theme", is_dark_mode)
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

        # # 处理余数
        # if remainder == 1:
        #     columns[1].append(album["images"][-1])  # 余数为1，最后一张放到第二列
        # elif remainder == 2:
        #     columns[1].append(album["images"][-1])  # 最后一张放到第二列
        #     columns[0].append(album["images"][-2])  # 倒数第二张放到第一列

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


if __name__ == "__main__":
    app.run_server(debug=True)
