import feffery_antd_components as fac
import feffery_utils_components as fuc
import dash
from dash import html,dcc
import config


logo = fac.AntdImage(
                id="logo",
                src=config.LOGO_PATH,
                preview=False,
                style={
                    "height": "60px",
                    "width": "150px",
                    "borderRadius": "20%",
                    "overflow": "hidden",
                    "marginRight": "10px",
                },
            )

options = [
    dcc.Link("精选", href="/", style={"margin": "0 15px", "cursor": "pointer","color": "black"}),
    dcc.Link("随机", href="/random", style={"margin": "0 15px", "cursor": "pointer","color": "black"}),
    dcc.Link("相册", href="/albums", style={"margin": "0 15px", "cursor": "pointer","color": "black"}),
    dcc.Link("地图", href="/map",  style={"margin": "0 15px", "cursor": "pointer", "color": "black"},),
]

theme_switch = fac.AntdSwitch(
    id="theme-switch",
    checked=False,
    checkedChildren="🌙",
    unCheckedChildren="☀️",
    style={"marginLeft": "auto"},
)

def render_navbar():
    navbar = fac.AntdAffix(fac.AntdHeader(
                        html.Div(
                            [logo, *options,theme_switch],
                            style={"display": "flex", "alignItems": "center", "width": "100%"},
                        ),
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
                    offsetTop=0.1,
                    # target='main-container',
                    )
    return navbar

