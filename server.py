import dash
import os
import oss2

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    prevent_initial_callbacks = True
   
)

# 设置网页title
app.title = 'AngYi\'s Gallery'

server = app.server


#  当oss更新时，更新相册数据和EXIF数据到本地json文件
@server.route('/webhook', methods=['POST'])
def webhook():
    # 处理 webhook 请求
    print("收到 webhook 请求，开始更新相册和 EXIF 数据。")
    
    from dotenv import load_dotenv
    from read_oss import update_albums_json_data

    # 加载 .env 文件中的环境变量
    load_dotenv()

    # 读取密钥
    oss_access_key = os.getenv('OSS_ACCESS_KEY')
    oss_secret_key = os.getenv('OSS_SECRET_KEY')
    oss_endpoint = os.getenv('OSS_ENDPOINT')
    oss_bucket = os.getenv('OSS_BUCKET')

    # 阿里云OSS配置
    auth = oss2.Auth(oss_access_key, oss_secret_key)
    bucket = oss2.Bucket(auth, oss_endpoint, oss_bucket)
    update_albums_json_data(bucket)  # albums.json & exif_data.json
    
    return "Webhook received", 200
