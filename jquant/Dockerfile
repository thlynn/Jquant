FROM 9fevrier/python-ta-lib-pandas

ADD . /app
WORKDIR /app

RUN cd /app \
    && pip install -r requirements.txt -i https://pypi.doubanio.com/simple/

CMD ["python", "main.py"]