# 构建阶段
FROM alpine:3.18 as builder

# 安装系统依赖
RUN apk add --no-cache \
    python3=3.9.18-r0 \
    py3-pip \
    gcc \
    musl-dev \
    libc-dev \
    libstdc++ \
    libgl1

# 配置清华镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装Python依赖
COPY requirements.txt .
RUN python3 -m pip install --user --no-cache-dir -r requirements.txt

# ------------ 生产镜像 ------------
FROM alpine:3.18

# 安装运行时依赖
RUN apk add --no-cache \
    python3=3.9.18-r0 \
    libstdc++

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/root/.local/bin:$PATH"

# 从构建阶段复制依赖
COPY --from=builder /root/.local /root/.local

WORKDIR /app
COPY app ./app
COPY main.py .

# 暴露端口
EXPOSE 8050

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8050", "--workers", "4"]