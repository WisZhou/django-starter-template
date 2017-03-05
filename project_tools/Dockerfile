FROM daocloud.io/library/python:2.7.13
ENV PYTHONUNBUFFERED 1
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN mkdir /code
WORKDIR /code
ADD requirements/base.txt /code
RUN pip install -r base.txt -i https://pypi.mirrors.ustc.edu.cn/simple
