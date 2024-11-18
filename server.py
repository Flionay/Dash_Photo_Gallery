import dash

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    prevent_initial_callbacks = True
   
)

# 设置网页title
app.title = 'Photo Gallery'

server = app.server