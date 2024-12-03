import time
import os
from PIL import Image, ExifTags
import shutil
from dotenv import load_dotenv
import exifread
import json
from fractions import Fraction
from loguru import logger 
# 加载 .env 文件中的环境变量
load_dotenv()

class ImageProcessor:
    def __init__(self, directory_path):
        self.directory_path = directory_path
        self.output_dir = "./output/"
        # 清空 output 文件夹
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)  # 删除文件夹及其内容
            
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def process_images(self):
        logger.info("开始parse exif信息")
        self.save_exif_to_json()
        logger.info("保存EXIF信息到JSON文件")
        for root, _, files in os.walk(self.directory_path):
            for file in files:
                if file.endswith(('.png', '.jpg', '.jpeg', '.JPG')):
                    logger.info(f"开始处理图片: {file}")
                    file_path = os.path.join(root, file)
                    output_file = os.path.join(self.output_dir, os.path.relpath(file_path, self.directory_path)).rsplit('.', 1)[0] + '.webp'
                    output_file_dir = os.path.dirname(output_file)

                    if not os.path.exists(output_file_dir):
                        os.makedirs(output_file_dir)

                    self.process_image(file_path, output_file)
                    pass
                elif file.endswith('.yaml'):
                    self.copy_yaml_file(root, file, self.output_dir)
                    
    def copy_yaml_file(self, root, file, output_dir):
        file_path = os.path.join(root, file)
        output_file = os.path.join(output_dir, os.path.relpath(file_path, self.directory_path))
        output_file_dir = os.path.dirname(output_file)

        if not os.path.exists(output_file_dir):
            os.makedirs(output_file_dir)
        shutil.copy2(file_path, output_file)
        

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
                pass

            img.save(output_file, 'webp', quality=20, exif=img.info.get('exif'))
            add_watermark(output_file, output_file)

    def save_exif_to_json(self):
        exif_data_dict = {}
        for root, _, files in os.walk(self.directory_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.JPG')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as img:
                            tags = exifread.process_file(img)
                            readable_exif = convert_exif_to_dict(tags)
                            relative_path = os.path.relpath(file_path, self.directory_path)
                            exif_data_dict[relative_path] = readable_exif
                            logger.info(f"处理 {file_path} EXIF信息成功")
                    except Exception as e:
                        print(f"无法处理文件 {file_path}: {e}")

        json_file_path = os.path.join(self.output_dir, 'exif_data.json')
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(exif_data_dict, json_file, ensure_ascii=False, indent=4)
            print("JSON 文件已保存。")




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
            
            

import subprocess

def upload_to_oss(src_folder, bucket_name, endpoint, access_key_id, access_key_secret):
    endpoint = 'oss-cn-beijing.aliyuncs.com'
    command = [
        'ossutil', 'sync','-f', '--delete','-u', src_folder,
        f'oss://{bucket_name}/gallery/',
        '-e', endpoint,
        '-i', access_key_id,
        '-k', access_key_secret,
        '--region', "cn-beijing"
        
    ]
    print(command)
    
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("上传成功:", result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("上传失败:", e.stderr.decode())      
              
            
def send_webhook():
    import requests
    webhook_url = os.getenv('WEBHOOK_URL')  # 替换为您的 Dash 应用地址
    try:
        response = requests.post(webhook_url)
        if response.status_code == 200:
            print("Webhook 请求成功，Dash 应用已更新。")
        else:
            print(f"Webhook 请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"发送 webhook 请求时出错: {e}")


if __name__ == '__main__':
    
    
    directory_to_process = os.getenv('watch_dir')
    while True:
        if 'run.txt' in os.listdir(directory_to_process):
            print(f"开始处理目录: {directory_to_process}")
            # loguru 日志文件
            logger.add(os.path.join(directory_to_process, 'running_log.txt'), level='INFO')

            processor = ImageProcessor(directory_to_process)
            processor.process_images()
            
             # 删除 running_log 日志 表示图片处理完
            os.remove(os.path.join(directory_to_process, 'running_log.txt'))
            upload_to_oss(src_folder='./output/', bucket_name=os.getenv('OSS_BUCKET'), 
                        endpoint=os.getenv('OSS_ENDPOINT'), access_key_id=os.getenv('OSS_ACCESS_KEY'), 
                        access_key_secret=os.getenv('OSS_SECRET_KEY'))
            send_webhook()
            
            # 删除 run.txt 表示上传完
            os.remove(os.path.join(directory_to_process, 'run.txt'))
            
        else:
            time.sleep(1)
            print('.', end='', flush=True)
        
