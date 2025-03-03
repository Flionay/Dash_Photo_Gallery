# 更新日志

## [0.2.0] - 2024-05-20

### 修复
- **导航栏状态同步**  
  修复<mcsymbol name="sync_menu_with_url" filename="navbar.py" path="/Users/angyi/Desktop/前端/photo_gallery/views/navbar.py" startline="36" type="function"></mcsymbol>回调函数，解决页面刷新后菜单选中状态与URL不同步的问题
- **主题切换优先级**  
  在<mcsymbol name="auto_switch_theme" filename="theme.py" path="/Users/angyi/Desktop/前端/photo_gallery/callbacks/theme.py" startline="53" type="function"></mcsymbol>中增加自动模式状态跟踪，确保手动切换主题后禁用时间自动切换逻辑
- **图片加载抖动**  
  通过<mcsymbol name="create_image_card" filename="photos.py" path="/Users/angyi/Desktop/前端/photo_gallery/callbacks/photos.py" startline="7" type="function"></mcsymbol>添加占位容器和CSS containment，消除滚动时布局偏移

### 优化
- **视觉一致性**  
  统一暗黑模式下相册卡片(<mcfile name="photos.py" path="/Users/angyi/Desktop/前端/photo_gallery/callbacks/photos.py"></mcfile>)和模态框(<mcfile name="main.py" path="/Users/angyi/Desktop/前端/photo_gallery/main.py"></mcfile>)的背景透明度
- **交互反馈**  
  重构导航栏菜单hover效果(<mcfile name="common.css" path="/Users/angyi/Desktop/前端/photo_gallery/assets/common.css"></mcfile>)，使用CSS变量管理主题色
- **性能提升**  
  在<mcfolder name="assets" path="/Users/angyi/Desktop/前端/photo_gallery/assets"></mcfolder>assts中添加will-change和backface-visibility优化渲染性能

### 新增
- **状态持久化**  
  新增<mcsymbol name="theme-status" filename="main.py" path="/Users/angyi/Desktop/前端/photo_gallery/main.py" startline="35" type="function"></mcsymbol>存储组件实现主题状态本地缓存
- **错误处理**  
  添加URL监听回调自动重置根路径(<mcfile name="main.py" path="/Users/angyi/Desktop/前端/photo_gallery/main.py"></mcfile>行158-170)