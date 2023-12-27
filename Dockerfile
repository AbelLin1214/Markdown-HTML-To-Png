FROM mcr.microsoft.com/playwright/python:v1.39.0

# ubuntu换源
RUN rm -f /etc/apt/sources.list
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse" >> /etc/apt/sources.list

WORKDIR /app
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
RUN pip install .
