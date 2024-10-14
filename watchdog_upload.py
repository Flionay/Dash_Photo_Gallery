import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image, ExifTags
import oss2
import shutil


# 阿里云OSS配置
auth = oss2.Auth('LTAI5tQ2j1kpp1YsKBJuC6iJ', 'z49aq2jux9xVhoAWXTxza7xSBILuyQ')
bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'angyi')

class Watcher:
    DIRECTORY_TO_WATCH = "./gallery"

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
                    self.copy_yaml_file(root, file, output_dir)

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


    def upload_to_oss(self, remote_path, file_path):
        print(remote_path,file_path)
        bucket.enable_crc = False
        with open(file_path, 'rb') as fileobj:
            bucket.put_object(remote_path, fileobj)

if __name__ == '__main__':
    w = Watcher()
    w.run()
    

    # # 打开图片
    # from PIL.ExifTags import TAGS
    # with Image.open('/Users/angyi/Desktop/前端/photo_gallery/gallery/苏州/DSC04283.JPG') as img:
    #     # 获取 EXIF 数据
    #     exif_data = img._getexif()
        

            
    #     # 检查并应用EXIF方向信息
    #     try:
    #         for orientation in ExifTags.TAGS.keys():
    #             if ExifTags.TAGS[orientation] == 'Orientation':
    #                 break
    #         exif = img._getexif()
    #         if exif is not None:
    #             orientation = exif.get(orientation, None)
    #             if orientation == 3:
    #                 img = img.rotate(180, expand=True)
    #             elif orientation == 6:
    #                 img = img.rotate(270, expand=True)
    #             elif orientation == 8:
    #                 img = img.rotate(90, expand=True)
    #     except (AttributeError, KeyError, IndexError):
    #         # 如果没有EXIF信息，直接跳过
    #         pass
            
    #     img.save('./test.webp', 'webp', quality=20,exif=img.info.get('exif'))
