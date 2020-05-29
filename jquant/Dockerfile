FROM python:3.8-alpine

# 设置alpine的镜像地址为阿里云的地址

RUN echo "https://mirrors.aliyun.com/alpine/v3.11/main/" > /etc/apk/repositories \
    && echo "https://mirrors.aliyun.com/alpine/v3.11/community/" >> /etc/apk/repositories \
    # 安装依赖包
    && apk update \
    && apk add --no-cache bash \
    python3 gcc g++ python3-dev linux-headers libffi-dev openssl-dev make \
    && rm -rf /var/cache/apk/* \
    && echo "http://dl-cdn.alpinelinux.org/alpine/v3.11/main" > /etc/apk/repositories \
    && echo "http://dl-cdn.alpinelinux.org/alpine/v3.11/community" >> /etc/apk/repositories \
    && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xvzf ta-lib-0.4.0-src.tar.gz  \
    && cd ta-lib/ \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && pip install numpy -i https://pypi.doubanio.com/simple/ \
    && pip install TA-Lib==0.4.18 -i https://pypi.doubanio.com/simple/ \
    && pip install pandas==1.0.3 -i https://pypi.doubanio.com/simple/

ADD . /app
WORKDIR /app

RUN cd /app \
    && pip install -r requirements.txt -i https://pypi.doubanio.com/simple/

CMD ["python", "main.py"]