FROM mcr.microsoft.com/playwright/python:v1.29.0-focal
WORKDIR /app
RUN sed -i 's/deb.debian.org/mirrors.huaweicloud.com/g' /etc/apt/sources.list
RUN sed -i 's|security.debian.org/debian-security|mirrors.huaweicloud.com/debian-security|g' /etc/apt/sources.list
RUN apt update
RUN apt install -y vim
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN playwright install chrome
# 处理时间
ENV TIME_ZONE=Asia/Shanghai
RUN echo "${TIME_ZONE}" > /etc/timezone \
    && ln -sf /usr/share/zoneinfo/${TIME_ZONE} /etc/localtime
COPY . .