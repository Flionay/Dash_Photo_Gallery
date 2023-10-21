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
    
    from geopy.geocoders import Nominatim

    # 初始化 Nominatim
    geolocator = Nominatim(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36")


        #     "Latitude": 36.676766666666666,
        # "Longitude": 117.0223,
    # # vv = (36.6767, 117.0223)
    # # loc = rg.search ( vv )
    # # print(loc)
    # # city=loc[0]['name']#城市
    # # county=loc[0]['admin2']#郡
    # # state=loc[0]['admin1']#州
    # # country=loc[0]['cc']#国家
    # print(location.raw['address']['state'][:-1] + ", " + 
    #   location.raw['address']['city'] + ", " + 
    #   location.raw['address']['suburb'])
    
    image_file = open('/Users/angyi/Documents/图片/Gallery/青岛/IMG_1419.jpeg', 'rb')
    tags = exifread.process_file(image_file)
  
    exif_dict = convert_exif_to_dict(tags)
    print(exif_dict)
    from watchdog_upload import parse_location_gaode,parse_location_rg
    
    
    # exif_dict = {
    #     "Latitude": 36.676766666666666,
    #     "Longitude": 117.0223,
    #     "DateTime": "2021:09:13 18:36:06",
    #     "Location": "山东 · 市南区· 八大关街道"
    # }
    print(parse_location_rg(exif_dict))
    res = parse_location_gaode(exif_data=exif_dict) 
    print(res)

# # 使用示例
# image_path = '/Users/angyi/Documents/图片/Gallery/青岛/IMG_1100.jpeg'
# json_path = 'exif_data.json'
# save_exif_to_json(image_path, json_path)
    from util import parse_datetime
    print(parse_datetime("2024:04:04 18:00:28"))