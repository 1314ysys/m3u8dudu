# 构建 amd64 平台镜像
FROM python:3.9-alpine3.14 AS builder-amd64

# 添加 DNS 地址和腾讯云软件源，并设置默认的 DNS 地址
RUN echo 'http://mirrors.cloud.tencent.com/alpine/v3.14/main' > /etc/apk/repositories && \
    echo 'http://mirrors.cloud.tencent.com/alpine/v3.14/community' >> /etc/apk/repositories && \
    apk update

# 将当前目录下的所有文件复制到容器中的 /app 目录
COPY . /app
WORKDIR /app

# 安装 FFmpeg 和其他依赖项
RUN apk add --no-cache ffmpeg && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# 暴露 5000 端口
EXPOSE 5000

# 启动 Flask 应用程序，并指定配置文件
CMD ["python", "app.py", "--config", "/app/config/config.ini"]


# 构建 arm64 平台镜像
FROM python:3.9-alpine3.14 AS builder-arm64

# 添加 DNS 地址和腾讯云软件源，并设置默认的 DNS 地址
RUN echo 'http://mirrors.cloud.tencent.com/alpine/v3.14/main' > /etc/apk/repositories && \
    echo 'http://mirrors.cloud.tencent.com/alpine/v3.14/community' >> /etc/apk/repositories && \
    apk update

# 将当前目录下的所有文件复制到容器中的 /app 目录
COPY . /app
WORKDIR /app

# 安装 FFmpeg 和其他依赖项
RUN apk add --no-cache ffmpeg && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# 暴露 5000 端口
EXPOSE 5000

# 启动 Flask 应用程序，并指定配置文件
CMD ["python", "app.py", "--config", "/app/config/config.ini"]