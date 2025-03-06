import os
import json
import oss2
import yaml
from datetime import date
import config

def get_exif_json(bucket):
    oss_exif_data_key = 'gallery/exif_data.json'
    exif_data = bucket.get_object(oss_exif_data_key).read()  # 读取为 bytes
    exif_data_dict = json.loads(exif_data.decode('utf-8'))  # 解码为字符串并转换为字典

    # 检查本地是否存在 exif_data.json 文件
    local_exif_file = config.exif_json_path
    local_exif_data_dict = {}

    if os.path.exists(local_exif_file):
        with open(local_exif_file, 'r', encoding='utf-8') as json_file:
            local_exif_data_dict = json.load(json_file)  # 读取本地数据

    # 更新本地数据
    for key in list(local_exif_data_dict.keys()):
        if key not in exif_data_dict:
            # 如果远程没有该键，而本地有，则删除本地的键
            del local_exif_data_dict[key]
            print(f"删除本地的键: {key}")

    for key in exif_data_dict:
        if key not in local_exif_data_dict:
            # 如果本地没有该键，则将远程的键添加到本地
            local_exif_data_dict[key] = exif_data_dict[key]
            print(f"添加远程的键: {key}")

    # 将更新后的数据写回到本地的 exif_data.json 文件
    with open(local_exif_file, 'w', encoding='utf-8') as json_file:
        json.dump(local_exif_data_dict, json_file, ensure_ascii=False, indent=4)

    print("exif_data.json 文件已更新并保存到本地。")


def update_albums_json_data(bucket,folder='gallery'):
    # 存储相册信息的字典
    albums = {}

    # 列出文件夹中的所有文件
    for obj in oss2.ObjectIterator(bucket, prefix=folder):
        if obj.key.endswith('.webp'):
            # 生成图片链接
            image_url = f"https://{bucket.bucket_name}.{bucket.endpoint.split('//')[1]}/{obj.key}"
            # 获取相册名称（假设相册名称是文件路径的一部分）
            album_name = obj.key.split('/')[1]
            if album_name not in albums:
                albums[album_name] = {'images': []}
            albums[album_name]['images'].append(image_url)
        elif obj.key.endswith('.yaml'):
            # 读取yaml文件
            yaml_content = bucket.get_object(obj.key).read()
            album_info = yaml.safe_load(yaml_content)
            album_name = obj.key.split('/')[1]
            if album_name not in albums:
                albums[album_name] = {'images': []}
            albums[album_name].update(album_info)

    # 将日期对象转换为字符串
    def convert_dates(obj):
        if isinstance(obj, dict):
            return {k: convert_dates(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_dates(i) for i in obj]
        elif isinstance(obj, date):
            return obj.isoformat()  # 转换为ISO格式的字符串
        return obj

    # 转换相册信息中的日期
    albums = convert_dates(albums)

    # 将信息保存到JSON文件中
    with open(config.albums_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(albums, json_file, ensure_ascii=False, indent=4)

    print("相册信息已保存到 albums.json 文件中。")

    # 从 OSS 下载 exif_data.json 保存到本地
    get_exif_json(bucket)



# 调用函数以更新相册数据
if __name__ == "__main__":
    from dotenv import load_dotenv

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
    update_albums_json_data(bucket)
    
    