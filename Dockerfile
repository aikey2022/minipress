FROM      python:3.10.4
ADD       .   /opt/python/flask/minipress
VOLUME    /flask/pkg/site-packages:/usr/local/lib/python3.10/site-packages
RUN       mkdir ~/.pip/ && echo "Asia/Shanghai" /etc/timezone
COPY      pip.conf      ~/.pip/
WORKDIR   /opt/python/flask/minipress
RUN       pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
EXPOSE    5000
CMD       ["/bin/sh","-c", "uwsgi --ini uwsgi.ini"]