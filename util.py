from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import requests
from io import BytesIO

def get_exif_data(image_url):
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