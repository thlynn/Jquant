FROM python:3.8.2

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install && \
  pip install numpy -i https://pypi.doubanio.com/simple/

ADD . /app

WORKDIR /app

RUN  cd /app && \
  pip install -r requirements.txt -i https://pypi.doubanio.com/simple/

CMD ["python", "main.py"]