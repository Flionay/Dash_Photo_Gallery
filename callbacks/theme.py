import dash
from dash import html, dcc, callback_context
import feffery_antd_components as fac
from dash.dependencies import Input, Output, State
from server import app 
import config
import feffery_utils_components as fuc


# 添加一个新的回调来获取当前主题状态
@app.callback(Output("theme-status", "data"), Input("theme-switch", "checked"))
def update_theme_status(is_dark_mode):
    return is_dark_mode

# 回调函数用于切换主题
@app.callback(
    [
        Output("main-container", "style"),
        Output("navbar", "style",allow_duplicate=True),
        Output("logo", "src"),
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
        }
        logo_src = config.LOGO_PATH_LIGHT
        
    else:
        common_style = {
            "backgroundColor": "#f0f2f5",
            "color": "black",
            "minHeight": "100vh",
            "backgroundImage": "linear-gradient(135deg, #f0f2f5 0%, #ffffff 85%)",
        }
        navbar_style = {
            "backgroundColor": "#f0f2f5",
            "color": "black",
        }
        logo_src = config.LOGO_PATH
 
    return common_style, {
        **navbar_style,
        "padding": "20px 40px",
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "space-between",
    }, logo_src

