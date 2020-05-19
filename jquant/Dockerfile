FROM python:3.8-alpine

# 设置alpine的镜像地址为阿里云的地址

RUN echo "https://mirrors.aliyun.com/alpine/v3.11/main/" > /etc/apk/repositories \
    && echo "https://mirrors.aliyun.com/alpine/v3.11/community/" >> /etc/apk/repositories \
    # 安装依赖包
    && apk update \
    && apk add --no-cache bash \
    # libevent-dev libxml2-dev  libffi libxml2 libxslt libxslt-dev  \
    python3 gcc g++ python3-dev linux-headers libffi-dev openssl-dev make \
    # 由于通过apk安装的pip总是基于python2.7的版本，不符合项目要求，此处使用get-pip.py的方式
    #安装基于python3.6的pip
#    && python3 /get-pip.py \
    # 删除不必要的脚本
#    && cd .. \
#    && rm -f /get-pip.py \
    # 此环境专用做运行django项目，因此移除不必要的工具，减少空间
    #    && pip uninstall -y pip setuptools wheel \
    # 最后清空apk安装时产生的无用文件
    && rm -rf /var/cache/apk/*


RUN echo "http://dl-cdn.alpinelinux.org/alpine/v3.11/main" > /etc/apk/repositories \
    && echo "http://dl-cdn.alpinelinux.org/alpine/v3.11/community" >> /etc/apk/repositories \
    && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xvzf ta-lib-0.4.0-src.tar.gz  \
    && cd ta-lib/ \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && pip install numpy -i https://pypi.doubanio.com/simple/ \
    && pip install TA-Lib==0.4.18 -i https://pypi.doubanio.com/simple/

ADD . /app

WORKDIR /app

RUN cd /app \
    && pip install -r requirements.txt -i https://pypi.doubanio.com/simple/

CMD ["python", "main.py"]