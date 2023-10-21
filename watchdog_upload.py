import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image, ExifTags
import oss2
import shutil
from dotenv import load_dotenv
import json

# 加载 .env 文件中的环境变量
load_dotenv()

# 读取密钥
oss_access_key = os.getenv('OSS_ACCESS_KEY')
oss_secret_key = os.getenv('OSS_SECRET_KEY')
oss_endpoint = os.getenv('OSS_ENDPOINT')
oss_bucket = os.getenv('OSS_BUCKET')
# 阿里云OSS配置
auth = oss2.Auth(oss_access_key,oss_secret_key)
bucket = oss2.Bucket(auth, oss_endpoint, oss_bucket)

class Watcher:
    DIRECTORY_TO_WATCH = os.getenv('watch_dir')

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(900)  # 每15分钟检查一次
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return None
        elif event.event_type in ('created', 'modified'):
            self.process(Watcher.DIRECTORY_TO_WATCH)

    def process(self, directory_path):
        # 处理图片
        output_dir = "./output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        save_exif_to_json(directory_path, os.path.join(output_dir,'exif_data.json'))
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(('.png', '.jpg', '.jpeg', '.JPG')):
                    file_path = os.path.join(root, file)
                    output_file = os.path.join(output_dir, os.path.relpath(file_path, directory_path)).rsplit('.', 1)[0] + '.webp'
                    output_file_dir = os.path.dirname(output_file)
                    
                    if not os.path.exists(output_file_dir):
                        os.makedirs(output_file_dir)

                    # 检查是否已经存在同名的webp文件
                    if not os.path.exists(output_file):
                        self.process_image(file_path, output_file)
                        # 上传到阿里云OSS
                        remote_path = 'gallery/' + os.path.basename(os.path.dirname(output_file)) + '/' + os.path.basename(output_file)
                        self.upload_to_oss(remote_path, output_file)
                elif file.endswith('.yaml'):
                    pass
                    self.copy_yaml_file(root, file, output_dir)
        self.upload_to_oss('gallery/exif_data.json',"output/exif_data.json")

    def copy_yaml_file(self, root, file, output_dir):
        file_path = os.path.join(root, file)
        output_file = os.path.join(output_dir, os.path.relpath(file_path, Watcher.DIRECTORY_TO_WATCH))
        output_file_dir = os.path.dirname(output_file)

        if not os.path.exists(output_file_dir):
            os.makedirs(output_file_dir)

        shutil.copy2(file_path, output_file)
        
        # 上传到阿里云OSS
        remote_path = 'gallery/' + os.path.basename(os.path.dirname(output_file)) + '/' + os.path.basename(output_file)
        self.upload_to_oss(remote_path, output_file)



    def process_image(self, file_path, output_file):
        with Image.open(file_path) as img:
            # 检查并应用EXIF方向信息
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = img._getexif()
                if exif is not None:
                    orientation = exif.get(orientation, None)
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError):
                # 如果没有EXIF信息，直接跳过
                pass

            img.save(output_file, 'webp', quality=20, exif=img.info.get('exif'))
        add_watermark(output_file, output_file)
        
    def upload_to_oss(self, remote_path, file_path):
        print(remote_path,file_path)
        bucket.enable_crc = False
        with open(file_path, 'rb') as fileobj:
            bucket.put_object(remote_path, fileobj)

from fractions import Fraction


def convert_exif_value(value):
    """将EXIF值转换为可序列化的格式"""
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')  # 转换为字符串
    elif isinstance(value, (int, float)):
        return value  # 直接返回数值
    elif isinstance(value, Fraction):
        return float(value)  # 将IFDRational转换为浮点数
    return str(value)  # 其他类型转换为字符串

def save_exif_to_json(directory_path, json_file_path):
    exif_data_dict = {}

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.JPG')):
                file_path = os.path.join(root, file)
                try:
                    with Image.open(file_path) as img:
                        exif_data = img._getexif()
                        if exif_data is not None:
                            # 将EXIF信息转换为可读格式
                            readable_exif = {}
                            for tag_id, value in exif_data.items():
                                tag = ExifTags.TAGS.get(tag_id, tag_id)
                                converted_value = convert_exif_value(value)  # 转换值
                                # 过滤掉长度超过100的键和值
                                if len(tag) <= 100 and len(str(converted_value)) <= 100:
                                    readable_exif[tag] = converted_value  # 仅在长度合适时添加
                            # 按照相册/图片的级别保存EXIF信息
                            relative_path = os.path.relpath(file_path, directory_path)
                            exif_data_dict[relative_path] = readable_exif
                except Exception as e:
                    print(f"无法处理文件 {file_path}: {e}")

    # 将EXIF信息保存到JSON文件
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(exif_data_dict, json_file, ensure_ascii=False, indent=4)



def add_watermark(input_image_path, output_image_path, watermark_path='sy.png', opacity=0.8):
    # 打开输入图片和水印图片
    with Image.open(input_image_path) as base_image:
        # 读取EXIF信息
        exif_data = base_image.info.get('exif')
        with Image.open(watermark_path) as watermark:
            watermark = watermark.convert("RGBA")
            alpha = watermark.split()[3]
            alpha = alpha.point(lambda p: p * opacity)  # 设置不透明度
            watermark.putalpha(alpha)
            # 获取水印的尺寸
            watermark_width, watermark_height = watermark.size
            # watermark = watermark.resize((int(watermark_width*1.3), int(watermark_height*1.3)), Image.ANTIALIAS)
            
            # 计算水印的位置（左下角）
            position = (15, base_image.height - watermark_height-20)
            
            # 创建一个可以在上面绘制的图像
            base_image.paste(watermark, position, watermark)
            
            # 保存叠加后的图片
            base_image.save(output_image_path, exif=exif_data)
            
            

def send_webhook():
    import requests
    webhook_url = "http://localhost:8050/webhook"  # 替换为您的 Dash 应用地址
    try:
        response = requests.post(webhook_url)
        if response.status_code == 200:
            print("Webhook 请求成功，Dash 应用已更新。")
        else:
            print(f"Webhook 请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"发送 webhook 请求时出错: {e}")


if __name__ == '__main__':
    # add_watermark('output/上海/DSC03640.webp', 'output_image.jpg')
    # pass
    w = Watcher()
    w.run()
    