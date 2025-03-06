from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import requests
from io import BytesIO
import requests  # 导入 requests 库
import datetime
from fractions import Fraction  
import json
import os
import numpy as np
import config

root_path = os.path.dirname(os.path.abspath(__file__))

def  get_exif_data(image_url):
    # print("输入的url",image_url)
    # 本地 JSON 文件的路径
    json_file_path = config.exif_json_path # 替换为实际的本地 JSON 文件路径
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            exif_data = json.load(json_file)  # 解析 JSON 数据

        # 根据 image_url 获取对应的 EXIF 数据
        position = '/'.join(image_url.split('/')[-2:]).split('.')[0]  # 只提取文件名，不添加扩展名
        
        # 假设 JSON 数据的结构是一个字典，键是图片 URL，值是对应的 EXIF 数据
        parsed_exif = {}
        image_idx = None
        for key,value in exif_data.items():
            if key.startswith(position):
                parsed_exif = value
                image_idx = key

            
        # print("匹配的图片",position,"匹配到的EXIF数据",parsed_exif)
        #parsed_exif = {key: value for key, value in exif_data.items() if key.startswith(position)}  
        if not parsed_exif:  # 如果没有找到匹配的 EXIF 数据，返回空字典
            return {}
        # print(parsed_exif)
        current_year = datetime.datetime.now().year 
        # 提取所需的 EXIF 信息
        image_info = {
            "设备": parsed_exif.get("CameraModel", "未知设备"),  # 设备型号
            "光圈": "F/" + parsed_exif.get("FNumber", "未知"),  # 光圈
            "快门速度": parsed_exif.get("ExposureTime", "未知"),  # 快门速度
            "焦距": parsed_exif.get("FocalLength", "未知"),  # 焦距
            "ISO": parsed_exif.get("ISO", "未知"),  # ISO
            "时间": parse_datetime(parsed_exif.get("DateTime", "未知")),  # 拍摄时间
            "位置": parsed_exif.get("Location", "未知"),
            "版权": parsed_exif.get("Copyright", f"© {current_year} Angyi. 保留所有权利。"),  # 版权信息
            "镜头": parsed_exif.get("LensModel", "未知"),  # 镜头型号
            "Longitude": parsed_exif.get("Longitude", None),
            "Latitude": parsed_exif.get("Latitude", None),
            "star": parsed_exif.get("star", 0),
            "likes": parsed_exif.get("likes", np.random.randint(90, 401)),
            'image_idx': image_idx
        }
        # print(image_info)
        return image_info

    except FileNotFoundError:
        print(f"文件未找到: {json_file_path}")
        return {}  # 返回空字典以防止程序崩溃
    except json.JSONDecodeError:
        print("解析 JSON 数据时出错")
        return {}  # 返回空字典以防止程序崩溃
    except Exception as e:
        print(f"发生错误: {e}")
        return {}  # 返回空字典以防止程序崩溃

def parse_datetime(date_str):
    """将日期字符串解析为年月日时格式"""
    if date_str == "未知":
        return "未知"
    try:
        # 假设输入格式为 "YYYY:MM:DD HH:MM:SS"
        dt = datetime.datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
        # print(dt)   
        return dt.strftime("%Y年%m月%d日 %H时")  # 返回格式为 "YYYY年MM月DD日 HH时"
    except ValueError:
        return "未知"  # 如果解析失败，返回"未知"

def format_coordinate(value):
    return "{:.2f}".format(value) if value != "未知" else "未知"

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



if __name__ == "__main__":
    import ast

    # 原始数据
    exif_data = { 'GPSInfo': "{0: b'\\x02\\x03\\x00\\x00', 5: b'\\x00', 8: '', 9: '', 10: ''}" }

    # 解析 GPSInfo
    # gps_info_str = exif_data['GPSInfo']
    # gps_info_dict = ast.literal_eval(gps_info_str)

    # # 输出解析后的字典
    # print(gps_info_dict.get(2).decode())
    info = get_exif_data("https://angyi.oss-cn-beijing.aliyuncs.com/gallery/东方明珠/DSC04080.webp")
    print(info)