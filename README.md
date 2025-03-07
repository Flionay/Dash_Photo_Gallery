# 📷 Dash Photo Gallery

**基于Dash框架构建的现代化个人摄影画廊**  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 功能特性
- **自动监控**：定时监控文件目录，自动处理新增或修改的图片。
   - 处理图片，避免重复处理。
   - 将压缩后的 WebP 文件上传至 OSS，并生成相应的 YAML 文件以描述相册信息（包括日期和经纬度）。
- **智能展示** - 自动解析EXIF信息（GPS、拍摄时间、设备型号）
- **主题切换** - 支持亮/暗模式无缝切换
- **交互体验** - 支持图片评分、点赞、地图定位等交互功能
- **自动同步** - Webhook触发OSS元数据同步机制


![demo](https://angyi.oss-cn-beijing.aliyuncs.com/uPic/2024/gallery.png)


## 设计方案

作为一个摄影爱好者，希望有一个自己的网页端照片展览。

我相信每一个摄影爱好者肯定有一个比较大的存储设备，文件形态的相册管理着自己的本地相册库

本项目的宗旨就是，从这个文件库，尽量无感的生成一个网页端的照片展览。尽量减少人工运维和实现高度的自定义处理，具有一定的可移植性。

我们的宗旨是，摄影，只需要关注于摄影本身，至于从本地文件到网页显示的过程，希望能够全自动化。

我们要做的就是拍照，修图，存档。 
![技术路线](https://angyi.oss-cn-beijing.aliyuncs.com/elog-docs-images/0fc0fae11d1cc14bf89493b37e19258a.png)

## 🚀 快速部署
### Docker 部署（推荐）
有环境的可以从当前仓库的packages中下载镜像，当然也可以自己编译。
```bash
docker run -d \
  -p 8089:8089 \
  -v /your/local/data:/app/data \
  -v /your/local/.env:/app/.env \
  angyi123/photo_gallery:v1.0  #arm版本的
```

- 访问应用：
   打开浏览器并访问 `http://127.0.0.1:8089`。


- 管理员可以给照片评分：
   访问 `http://127.0.0.1:8089/star`。 登录后可以给照片评分（账号密码在.env文件设置）。

### 源码部署
```bash

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/dash-photo-gallery.git
cd dash-photo-gallery

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境
cp env_example .env
vim .env  # 填写实际配置

# 4. 启动应用
python main.py  # 开发模式
gunicorn main:application -w 4 -b 0.0.0.0:8089  # 生产模式
```

- 访问应用：
打开浏览器并访问 `http://127.0.0.1:8089`。


- 管理员可以给照片评分：
   访问 `http://127.0.0.1:8089/star`。 登录后可以给照片评分（账号密码在.env文件设置）。

## 📂 目录结构
```
├── data/               # 动态数据存储
├── assets/             # 静态资源
├── callbacks/          # Dash回调逻辑
├── views/              # 页面组件
├── local_image_process # 本地图片处理脚本
│
├── Dockerfile          # 容器构建配置
├── main.py             # 应用入口
├── server.py           # Flask服务端
└── requirements.txt    # Python依赖
```

##  📝 使用指南
### 管理员功能
1. 访问 /star 路径进行图片评分
2. 使用.env中配置的账号密码登录
3. 评分数据实时同步至 exif_data.json
### OSS同步机制
通过配置WEBHOOK_URL，当OSS存储更新时：

1. 自动触发元数据同步
2. 更新本地albums.json和exif_data.json
3. 前端界面实时刷新

## 📄 许可证
本项目采用 MIT 许可证，详情请查看 [LICENSE](LICENSE) 文件。


## 📬 联系方式
如有任何问题或建议，请联系：
- 邮箱：angyi_jq@163.com
- GitHub：[Flionay](https://github.com/flionay)