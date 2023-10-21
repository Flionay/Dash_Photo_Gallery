from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import requests
from io import BytesIO
import requests  # 导入 requests 库
import datetime
from fractions import Fraction  

def get_exif_data(image_url):
    print("输入的url",image_url)
    # 假设远程 JSON 文件的 URL 是固定的
    json_url = "https://angyi.oss-cn-beijing.aliyuncs.com/gallery/exif_data.json"  # 替换为实际的 JSON 文件 URL
    try:
        response = requests.get(json_url)
        response.raise_for_status()  # 检查请求是否成功
        exif_data = response.json()  # 解析 JSON 数据

        # 根据 image_url 获取对应的 EXIF 数据
        position = '/'.join(image_url.split('/')[-2:]).split('.')[0]  # 只提取文件名，不添加扩展名
        
        # 假设 JSON 数据的结构是一个字典，键是图片 URL，值是对应的 EXIF 数据
        parsed_exif = {}
        for key,value in exif_data.items():
            if key.startswith(position):
                parsed_exif = value

            
        # print("匹配的图片",position,"匹配到的EXIF数据",parsed_exif)
        #parsed_exif = {key: value for key, value in exif_data.items() if key.startswith(position)}  
        if not parsed_exif:  # 如果没有找到匹配的 EXIF 数据，返回空字典
            return {}
        # print(parsed_exif)
        current_year = datetime.datetime.now().year 
        # 提取所需的 EXIF 信息
        image_info = {
            "设备": parsed_exif.get("Model", "未知设备"),  # 设备型号
            "光圈": "F/"+parsed_exif.get("FNumber", "未知"),  # 光圈
            "快门速度":format_shutter_speed(parsed_exif.get("ExposureTime", "未知")),  # 快门速度
            "焦距": parsed_exif.get("FocalLength", "未知"),  # 焦距
            "ISO": parsed_exif.get("ISOSpeedRatings", "未知"),  # ISO
            "拍摄时间": parsed_exif.get("DateTimeOriginal", parsed_exif.get("DateTime", "未知")),  # 拍摄时间
            # "位置": parsed_exif.get("GPSInfo", {}).get(GPSTAGS.get(2, "未知"), "未知") if "GPSInfo" in parsed_exif else "未知",  # 位置
            "版权": parsed_exif.get("Copyright", f"© {current_year} Angyi. 保留所有权利。"),  # 版权信息
            "镜头": parsed_exif.get("LensModel", "未知"),  # 镜头型号
        }
        print(image_info)
        return image_info

    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return {}  # 返回空字典以防止程序崩溃

def format_shutter_speed(exposure_time):
    if exposure_time == "未知":
        return "未知"
    
    try:
        # 将小数转换为分数
        shutter_speed_fraction = Fraction(float(exposure_time)).limit_denominator()
        
        # 如果分母为1，表示快门速度为整数，直接返回整数
        if shutter_speed_fraction.denominator == 1:
            return str(shutter_speed_fraction.numerator)
        else:
            return f"1/{shutter_speed_fraction.denominator}"  # 转换为 "1/n" 格式
    except Exception as e:
        print(f"处理快门速度时出错: {e}")
        return "未知"

def get_exif_datat(image_url):
    try:
        # 从 URL 下载图片
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))

        # 获取 EXIF 数据
        exif_data = image._getexif()
        if not exif_data:
            return None

        # 解析 EXIF 数据
        parsed_exif = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            parsed_exif[tag] = value

        # 提取所需的 EXIF 信息
        image_info = {
            "device": parsed_exif.get("Model", "未知设备"),
            "aperture": parsed_exif.get("FNumber", "未知"),
            "shutter_speed": parsed_exif.get("ExposureTime", "未知"),
            "focal_length": parsed_exif.get("FocalLength", "未知"),
            "iso": parsed_exif.get("ISOSpeedRatings", "未知"),
            "date_time": parsed_exif.get("DateTime", "未知"),
            "location": parsed_exif.get("GPSInfo", {}).get(GPSTAGS.get(2, "未知"), "未知") if "GPSInfo" in parsed_exif else "未知",
            "copyright": parsed_exif.get("Copyright", "未知"),
        }

        return image_info

    except Exception as e:
        print(f"获取 EXIF 数据时出错: {e}")
        return None


if __name__ == "__main__":
    import ast

    # 原始数据
    exif_data = { 'GPSInfo': "{0: b'\\x02\\x03\\x00\\x00', 5: b'\\x00', 8: '', 9: '', 10: ''}" }

    # 解析 GPSInfo
    # gps_info_str = exif_data['GPSInfo']
    # gps_info_dict = ast.literal_eval(gps_info_str)

    # # 输出解析后的字典
    # print(gps_info_dict.get(2).decode())
    info = get_exif_data("https://angyi.oss-cn-beijing.aliyuncs.com/gallery/北京/IMG_3003.webp")
    print(info)