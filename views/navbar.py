import feffery_antd_components as fac
import dash
from dash import html, dcc
import config
from dash_iconify import DashIconify
from server import app

logo = fac.AntdImage(
    id="logo",
    src=config.LOGO_PATH,
    preview=False,
    style={
        "height": "60px",
        "width": "165px",
        "borderRadius": "20%",
        "overflow": "hidden",
        "marginRight": "10px",
    },
)

# 使用 AntdMenu 组件
menu_items = [
    {
        'component': 'Item',
        'props': {
            'key': 'home',
            'title': '精选',
            'href': '/',
        },
    },
    {
        'component': 'Item',
        'props': {
            'key': 'random',
            'title': '随览',
            'href': '/random',
        },
    },
    {
        'component': 'Item',
        'props': {
            'key': 'albums',
            'title': '相册',
            'href': '/albums',
        },
    },
    {
        'component': 'Item',
        'props': {
            'key': 'map',
            'title': '地图',
            'href': '/map',
        },
    },
]

theme_switch = fac.AntdSwitch(
    id="theme-switch",
    checked=False,
    checkedChildren="🌙",
    unCheckedChildren="☀️",
    # style={"marginLeft": "15px"}
)

# 新增客户端时间监听组件
time_sync = dcc.Interval(
    id='time-sync',
    interval=60*1000,  # 每分钟同步一次
    n_intervals=0
)
def render_navbar():
    return fac.AntdAffix(
        fac.AntdHeader(
            html.Div(
                [
                    logo,
                    fac.AntdMenu(
                        id='navbar-menu',
                        mode='horizontal',
                        menuItems=menu_items,
                        defaultSelectedKey = 'home',
                        style={"flex": 1, "margin": "0 15px","borderBottom":"none"},
                    ),
                    theme_switch,
                    html.A(
                        DashIconify(id="github-icon", icon="logos:github-icon", style={"fontSize": "24px", "color": "gray"}),
                        href="https://github.com/Flionay/Dash_Photo_Gallery",  # 替换为你的 GitHub 地址
                        target="_blank",  # 在新标签页中打开
                        style={"textDecoration": "none", "marginLeft": "17px","display": "flex", "color": "gray"},
                    ),
                    time_sync,
                ],
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
    )
    return navbar



