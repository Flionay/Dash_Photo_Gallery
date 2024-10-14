import oss2
import yaml
import json
from datetime import date

# 初始化OSS客户端
auth = oss2.Auth('LTAI5tQ2j1kpp1YsKBJuC6iJ', 'z49aq2jux9xVhoAWXTxza7xSBILuyQ')
bucket = oss2.Bucket(auth, 'oss-cn-beijing.aliyuncs.com', 'angyi')

# 指定要列出的文件夹
folder = 'gallery'

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
with open('albums.json', 'w', encoding='utf-8') as json_file:
    json.dump(albums, json_file, ensure_ascii=False, indent=4)

print("相册信息已保存到albums.json文件中。")
