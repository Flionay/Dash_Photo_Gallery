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

@app.callback(
    [
        Output("theme-switch", "checked"),
        Output("auto-theme-enabled", "data")  # 新增自动主题状态存储
    ],
    [
        Input("client-time", "modified_timestamp"),
        Input("theme-switch", "checked")
    ],
    [
        State("client-time", "data"),
        State("auto-theme-enabled", "data")  # 获取当前自动模式状态
    ]
)
def auto_switch_theme(ts, manual_checked, client_time, auto_enabled):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
        
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    print(client_time)
    
    if trigger_id == "client-time":
        if auto_enabled:  # 仅在自动模式启用时生效
            hour = int(client_time.split(':')[0])
            return (hour >= 18 or hour < 6), True
        return dash.no_update, dash.no_update
    elif trigger_id == "theme-switch":
        # 当用户手动切换时，关闭自动模式
        return manual_checked, False
        
    return dash.no_update, dash.no_update

