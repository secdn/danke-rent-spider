FROM python:3.7.3
ENV PYTHONUNBUFFERED 1
COPY . /app/
WORKDIR /app
RUN pip install -r requirements.txt \
    && /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo 'Asia/Shanghai' >/etc/timezone
