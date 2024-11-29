# views/login.py
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from server import app
from dotenv import load_dotenv
import os
# 登录页面布局
login_layout = html.Div([
    dcc.Input(id='username', type='text', placeholder='用户名'),
    dcc.Input(id='password', type='password', placeholder='密码'),
    html.Button('登录', id='login-button'),
    html.Div(id='login-output')
])
    
    
@app.callback(
    Output('login-output', 'children'),
    Output('is-logged-in', 'data'),  # 更新登录状态
    Input('login-button', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value')
)
def login(n_clicks, username, password):
    if n_clicks is None:
        return '', False
    
    # 加载 .env 文件中的环境变量
    load_dotenv()

    # 读取密钥
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    if username == username and password == password:  # 替换为实际的管理员密码
        return dcc.Location(pathname='/star', id='redirect'), True  # 登录成功，重定向到评分页面
    else:
        return '用户名或密码错误', False