# 构建阶段
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/tiangolo/uvicorn-gunicorn:python3.11-slim AS builder  

# 配置清华镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装Python依赖
COPY requirements.txt .
RUN python3 -m pip install --user --no-cache-dir -r requirements.txt

# ------------ 生产镜像 ------------
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/tiangolo/uvicorn-gunicorn:python3.11-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/root/.local/bin:$PATH"

# 从构建阶段复制依赖
COPY --from=builder /root/.local /root/.local
# 新增数据目录
RUN mkdir -p /app/data

# 设置数据目录为挂载点
VOLUME ["/app/data"]

# 调整文件复制顺序
WORKDIR /app
COPY . .  

# 暴露端口
EXPOSE 8089

# 启动命令
CMD ["gunicorn", "main:server", "--host", "0.0.0.0", "--port", "8089", "--workers", "4"]

