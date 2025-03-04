# 基础镜像
FROM python:3.9-slim as builder

# 安装系统依赖（保持不变）
RUN apt-get update && apt-get install -y \
    gcc \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 配置清华镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装Python依赖
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# ------------ 生产镜像 ------------
FROM python:3.9-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 从builder阶段复制已安装的包
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 复制项目文件
WORKDIR /app
COPY . .

# 安装生产依赖
RUN pip install --user uvicorn gunicorn

# 暴露ASGI端口
EXPOSE 8099

# 启动命令（包含WSGI和ASGI双模式）
CMD ["uvicorn", "main:app.server", "--host", "0.0.0.0", "--port", "8050", "--workers", "4"]