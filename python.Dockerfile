FROM      python:3.10.4
# 设置 语言支持
ENV       LANG=C.UTF-8
ADD       .   /opt/python/flask/minipress
RUN       echo "Asia/Shanghai" > /etc/timezone
WORKDIR   /opt/python/flask/minipress
VOLUME    /flask/pkg/site-packages:/usr/local/lib/python3.10/site-packages
RUN       pip install pip --upgrade -i https://mirrors.aliyun.com/pypi/simple && \ 
          pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple 
EXPOSE    5000
CMD       ["/bin/sh","-c", "uwsgi --ini uwsgi.ini"]