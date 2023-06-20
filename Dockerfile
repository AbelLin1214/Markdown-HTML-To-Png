FROM python:3.10-slim-buster AS python

FROM mcr.microsoft.com/playwright/python:v1.31.0-focal

# 从python:3.10-slim-buster中复制Python版本
COPY --from=python /usr/local/bin/python /usr/local/bin/python
COPY --from=python /usr/local/lib/libpython3.10.so.1.0 /usr/local/lib/
COPY --from=python /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=python /usr/local/bin/pip3.10 /usr/local/bin/pip
COPY --from=python /usr/local/bin/pip /usr/local/bin
# 从python:3.10-slim-buster中复制libffi.so.7, 用于解决playwright镜像中libffi.so.6的问题（numpy依赖libffi.so.6）
COPY --from=python /usr/lib/x86_64-linux-gnu/libffi.so.6 /usr/lib/x86_64-linux-gnu/libffi.so.6
# playwright镜像中的python版本为3.8，在更新python版本后，需要将3.8的dist-packages目录添加到3.10的pth文件中
RUN echo "/usr/local/lib/python3.8/dist-packages/" >> /usr/local/lib/python3.10/site-packages/my.pth

# 设置Python 3.10为默认版本
RUN update-alternatives --install /usr/bin/python python /usr/local/bin/python 1
RUN update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip 1
RUN ln -s /usr/local/lib/libpython3.10.so.1.0 /usr/lib/

# # 在ubuntu 20.0.4以上，libffi.so.6被升级为libffi.so.7，需要手动创建软链接
# # 完美的解决方案是重新安装libffi6，并重新编译python，但这样花费的时间太长
# # 为了节省时间，直接创建软链接。或许会有一些问题，但目前没有发现
# RUN ln -s /usr/path/to/libffi.so.7 /usr/path/to/libffi.so.6

WORKDIR /app
RUN sed -i "s/archive.ubuntu.com/mirrors.aliyun.com/g" /etc/apt/sources.list
RUN sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list
RUN apt update
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# python3.8与python3.10的greenlet版本不兼容, 需要手动更新greenlet
RUN pip install -U greenlet
COPY requirements.txt .
RUN pip install -r requirements.txt
# 处理时间
ENV TIME_ZONE=Asia/Shanghai
RUN echo "${TIME_ZONE}" > /etc/timezone \
    && ln -sf /usr/share/zoneinfo/${TIME_ZONE} /etc/localtime
COPY . .
