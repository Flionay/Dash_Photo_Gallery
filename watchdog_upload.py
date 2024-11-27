import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image, ExifTags
import oss2
import shutil
from dotenv import load_dotenv
import exifread
import json
import uuid
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
        # 处理图片 并保存EXIF信息
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
        time.sleep(10)
        send_webhook()

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
        # print(remote_path,file_path)
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
                    with open(file_path,'rb') as img:
                        # exif_data = img._getexif()
                        tags = exifread.process_file(img)
                        readable_exif = convert_exif_to_dict(tags)
                        # print(readable_exif)
                        # 按照相册/图片的级别保存EXIF信息
                        relative_path = os.path.relpath(file_path, directory_path)
                        exif_data_dict[relative_path] = readable_exif
                except Exception as e:
                    print(f"无法处理文件 {file_path}: {e}")
                    
    
    try:
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            print(exif_data_dict)
            json.dump(exif_data_dict, json_file, ensure_ascii=False, indent=4)
            print("JSON 文件已保存。")
    except Exception as e:
        print(f"写入 JSON 文件时出错: {e}")




def convert_exif_to_dict(exif_data):   

    # 将分数列表转换为度数
    def parse_gps_coordinate(values, ref):
        degrees = values[0].num / values[0].den
        minutes = values[1].num / values[1].den
        seconds = values[2].num / values[2].den
        coordinate = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ['S', 'W']:
            coordinate = -coordinate
        return coordinate
    
    # 提取需要的 EXIF 信息
    exif_dict = {
        "CameraModel": str(exif_data.get("Image Model", "Unknown")),
        "LensModel": str(exif_data.get("EXIF LensModel", "Unknown")),
        "ExposureTime": str(exif_data.get("EXIF ExposureTime", "Unknown")),
        "FNumber": str(exif_data.get("EXIF FNumber", "Unknown")),
        "ISO": str(exif_data.get("EXIF ISOSpeedRatings", "Unknown")),
        "FocalLength": str(exif_data.get("EXIF FocalLength", "Unknown")),
        "Latitude": None,
        "Longitude": None,
        "DateTime": "未知",
        "Location": "未知"
    }
    # 解析曝光三要素
    if "EXIF ExposureTime" in exif_data:
        exif_dict["ExposureTime"] = str(exif_data["EXIF ExposureTime"])

    if "EXIF FNumber" in exif_data:
        fnumber = exif_data["EXIF FNumber"].values
        exif_dict["FNumber"] = str(fnumber[0].num / fnumber[0].den)

    if "EXIF ISOSpeedRatings" in exif_data:
        exif_dict["ISO"] = str(exif_data["EXIF ISOSpeedRatings"])

    if "EXIF FocalLength" in exif_data:
        focal_length = exif_data["EXIF FocalLength"].values
        exif_dict["FocalLength"] = str(focal_length[0].num / focal_length[0].den)

    # 解析 GPS 信息
    if "GPS GPSLatitude" in exif_data and "GPS GPSLatitudeRef" in exif_data:
        lat_values = exif_data["GPS GPSLatitude"].values
        lat_ref = exif_data["GPS GPSLatitudeRef"].printable
        exif_dict["Latitude"] = parse_gps_coordinate(lat_values, lat_ref)

    if "GPS GPSLongitude" in exif_data and "GPS GPSLongitudeRef" in exif_data:
        lon_values = exif_data["GPS GPSLongitude"].values
        lon_ref = exif_data["GPS GPSLongitudeRef"].printable
        exif_dict["Longitude"] = parse_gps_coordinate(lon_values, lon_ref)

    # 解析时间信息
    if "Image DateTime" in exif_data:
        exif_dict["DateTime"] = str(exif_data["Image DateTime"])
    else:
        exif_dict["DateTime"] = "未知"  # 添加默认值
    
    # print(exif_dict)
    address = parse_location_rg(exif_data=exif_dict)
    if address == "未知":
        address = parse_location_gaode(exif_data=exif_dict)
      
    exif_dict["Location"] = address
    return exif_dict
        
        

def parse_location_gaode(exif_data):
    
    import requests
    # 初始化 Nominatim
    api_key = os.getenv('gaode_key')
    try:
        if "Latitude" in exif_data and "Longitude" in exif_data:
            latitude = exif_data["Latitude"]
            longitude = exif_data["Longitude"]
            api_url = f"https://restapi.amap.com/v3/geocode/regeo?output=json&location={longitude},{latitude}&key={api_key}&radius=500&extensions=all "
            # print(api_url)
            response = requests.get(api_url)
            location = response.json()
            # time.sleep(10)
            # print(location)
            if location:
                return location['regeocode']['addressComponent']['province'][:-1] + " · " + \
                    location['regeocode']['addressComponent']['district'] + "· " + \
                    location['regeocode']['addressComponent']['township']
            else:
                return "未知"
        else:
            return "未知"
    except Exception as e:
        # print(e)
        return "未知"

def parse_location_rg(exif_data):
    from geopy.geocoders import Nominatim

    # 初始化 Nominatim
    geolocator = Nominatim(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36")

    if "Latitude" in exif_data and "Longitude" in exif_data:
        try:
            latitude = exif_data["Latitude"]
            longitude = exif_data["Longitude"]
            location = geolocator.reverse(f"{latitude}, {longitude}")
            
            if location:
                return location.raw['address']['state'][:-1] + " · " + \
                    location.raw['address']['city'] + " · " + \
                    location.raw['address']['suburb']
            else:
                return "未知位置"
        except Exception as e:
            # print(e)
            return "未知"
            
    else:
        return "未知"
    

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
    # # pass
    w = Watcher()
    w.run()
    
    save_exif_to_json("/Users/angyi/Documents/图片/Gallery/青岛", './test.json')