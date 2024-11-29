import exifread
import json
from datetime import datetime
from watchdog_upload import convert_exif_to_dict


        
def save_exif_to_json(image_path, json_path):
    with open(image_path, 'rb') as image_file:
        tags = exifread.process_file(image_file)
        for k,v in tags.items():
            print(k,v)
            
        exif_dict = convert_exif_to_dict(tags)
        print(exif_dict)
        # with open(json_path, 'w', encoding='utf-8') as json_file:
        #     json.dump(exif_dict, json_file, ensure_ascii=False, indent=4)




import reverse_geocoder as rg
 
if __name__ == '__main__' :
    
    with open('exif_data.json', 'r', encoding='utf-8') as f:
        exif_data = json.load(f)
        
        
    with open('albums.json', 'r', encoding='utf-8') as f:
        albums_data = json.load(f)
        
    #按照exif_data的图片顺序 返回ablum的images顺序
    # albums_data = sorted(albums_data.values(), key=lambda x: [exif_data[image_url].get('star',0) for image_url in x['images']])
    # print(albums_data)
    image_url_list = []
    for album_name in albums_data.keys():
        album_images = albums_data[album_name]['images']
        image_url_list+=album_images
    print(image_url_list)