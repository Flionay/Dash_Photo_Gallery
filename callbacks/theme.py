

import dash
from dash import html, dcc, callback_context
import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash.dependencies import Input, Output, State
from server import app 


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
        "padding-left": "65px",
        "padding-right": "65px",
        "padding-top": "75px",
        
        "display": "flex",
        "alignItems": "center",
    }