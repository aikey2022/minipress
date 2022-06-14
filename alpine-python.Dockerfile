FROM   python:3.10.4-alpine

# 设置 语言支持
ENV   LANG=C.UTF-8

ADD    .   /opt/python/flask/minipress
RUN    mkdir ~/.pip/ && \ 
       echo "Asia/Shanghai" /etc/timezone && \  
       # 配置apk包加速镜像为阿里云
       sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/' /etc/apk/repositories && \ 
       apk update && \ 
       # 安装基本开发工具
       apk add --no-cache zlib-dev bzip2-dev pcre-dev openssl-dev ncurses-dev sqlite-dev readline-dev tk-dev && \
       # 安装编译工具
       apk add --no-cache gcc g++ make cmake   linux-headers && \       
       rm -rf /tmp/*  && \
       rm -rf /var/cache/apk/*

COPY     pip.conf  ~/.pip/

# 配置 应用工作目录
WORKDIR  /opt/python/flask/minipress

VOLUME  /flask/pkg/site-packages:/usr/local/lib/python3.10/site-packages
# 安装 项目依赖包
RUN      pip install --upgrade pip && \ 
         pip install setuptools && \ 
         pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 配置 对外端口
EXPOSE   5000

# 设置启动时预期的命令参数
CMD      ["sh","-c", "uwsgi --ini uwsgi.ini"]