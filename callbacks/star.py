import dash
from dash import Output, Input, State, ctx
import json
from server import app
import feffery_antd_components as fac
import os

def update_exif_with_ratings(button_id, ratings, albums_data):
    # 读取现有的 exif_data.json 文件
    with open('exif_data.json', 'r', encoding='utf-8') as f:
        exif_data = json.load(f)

    flag = False
    # 获取对应的图片 URL
    print(button_id)
    image_url = button_id['index'].split('|')[0]
    idx = int(button_id['index'].split('|')[1])
    # 提取 URL 的最后两个部分
    image_id = '/'.join(image_url.split('/')[-2:])  # 获取最后两个部分
    image_id_without_ext = os.path.splitext(image_id)[0]  # 去掉文件扩展名

    # 检查图片 ID 是否在 exif_data 中
    for exif_key in exif_data.keys():
        # 去掉 exif_key 的扩展名
        exif_key_without_ext = os.path.splitext(exif_key)[0]
        
        # 比较最后两个部分
        if image_id_without_ext == exif_key_without_ext:
            exif_data[exif_key]['star'] = ratings[idx]  # 添加 star 字段
            info = f"更新 {exif_key} 的评分为 {ratings[idx]}"
            flag = True
            break
    else:
        info = f"未找到图片 {image_id} 在 exif_data.json 中"
        flag = False
    # 将更新后的数据写回到 exif_data.json 文件
    with open('exif_data.json', 'w', encoding='utf-8') as f:
        json.dump(exif_data, f, ensure_ascii=False, indent=4)
        
    return info,flag

# 在评分更新逻辑中调用
@app.callback(
    Output('rating-output', 'children'),  # 假设有一个输出区域显示评分结果
    Input({'type': 'rating', 'index': dash.dependencies.ALL}, 'value'),
    State('albums-data', 'data'),
)
def update_rating(ratings, albums_data):
    print(ratings)
    button_id = ctx.triggered_id if ctx.triggered_id else None
    if ratings is None:
        return dash.no_update
    
    # 更新 exif_data.json 文件
    info,flag = update_exif_with_ratings(button_id, ratings, albums_data)
    if flag:
        return fac.AntdNotification(
            message='更新成功',
            description=info,
            duration=2.5,
            type='success',
        )
    else:
        return fac.AntdNotification(
            message='更新失败',
            description=info,
            duration=2.5,
            type='error',
        )