
import dash
from dash import html, dcc, callback_context
import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash.dependencies import Input, Output, State
from server import app 
from util import get_exif_data
from dash_iconify import DashIconify
from urllib.parse import unquote


# 在布局中使用 html.Div 包围图片
def create_image_card(image_url, index):
    return html.Div(
        fuc.FefferyDiv([
                fac.AntdImage(
                    src=image_url,
                    preview=False,
                    style={"width": "100%", "height": "100%", "marginBottom": "0px"},
                ),
                
                fac.AntdRate(
                    id={'type': 'rating', 'index': index},
                    allowHalf=True,
                    defaultValue=2.5,
                    style={
                        "position": "absolute",
                        "bottom": "10px",
                        "right": "10px",
                        "backgroundColor": "rgba(255, 255, 255, 0.3)",
                        "display": "none",  # 默认隐藏
                    },
                # onChange=lambda value: update_rating(value, index)  # 更新评分
                ),
            ],

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
                            "maxHeight": "80vh",  # 设置最大高度为视口高度的80%
                            "borderRadius": "8px",
                            "objectFit": "contain",  # 保持比例，适应容器
                            "display": "block",  # 使图片为块级元素
                            "padding": "20px",  # 自动水平居中
                        },  # 充满宽度，保持比例
                        preview=False,
                    ),
                    html.Div(
                        style={
                            "display": "flex",
                            "justifyContent": "center",
                            "padding": "30px",
                            "background": "rgba(0, 0, 0, 0.0)",
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
                                            DashIconify(
                                                icon="solar:camera-broken",  # 使用 Antd 图标
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
                                ],className="image_meta_item"
                                
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
                                            DashIconify(
                                                icon="fluent-mdl2:focal-point",  # 使用 Antd 图标
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
                                            
                                            DashIconify(
                                                icon="ion:aperture-outline",
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
                                            
                                            DashIconify(
                                                icon="material-symbols:shutter-speed-minus-outline",  # 使用 Antd 图标
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
                                            
                                            DashIconify(
                                                icon="carbon:iso-filled",  # 使用 Antd 图标
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
                                        "地点",  
                                       className="text_row"
                                    ),
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                        },
                                        children=[
                                            DashIconify(
                                                icon="fa6-solid:map-location",  # 使用 Antd 图标
                                                style={
                                                    "fontSize": "16px",
                                                    "marginRight": "5px",
                                                },
                                            ), 
                                            html.P(
                                                f"{album_name}",  # 获取到的设备信息
                                                style={
                                                    "margin": "0",
                                                    "fontSize": "14px",
                                                },
                                            ),
                                        ],
                                    ),
                                ],className="image_meta_item"
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
                                            DashIconify(
                                                icon="arcticons:lensa",  # 使用 Antd 图标
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
                                ],className="image_meta_item"
                            ),
                        ],
                    ),
                ]
            ),
            True
        )

    return dash.no_update, False