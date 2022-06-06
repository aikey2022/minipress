# 使用日志
import logging
import os
import re
from logging.handlers import TimedRotatingFileHandler 



# 自定义日志类
class CreateLogging():

    def __init__(self, log_name='', loglevel='error'):
        # 1.实例化 Logging类
        self.logger = logging.getLogger(f'INTEL{log_name}')
        
        # 2. 设置根路径
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 3. 检查日志文件根路径
        self.check_root_dir()
        
        # 4. 设置日志等级 file_name既是文件名也是日志级别
        self.set_log_level(loglevel)
        
        # 5. 设置日志格式    %(asctime)s | %(levelname)s| %(pathname)s | %(filename)s | [funcName:%(funcName)s] [line:%(lineno)d] [进程ID:%(process)d] [线程ID:%(thread)d] [线程名:%(threadName)s] %(message)s
        self.formatter = logging.Formatter(
            f'{log_name} %(asctime)s %(levelname)s funcName:%(funcName)s line:%(lineno)d 进程ID:%(process)d 线程ID:%(thread)d %(message)s')
        
        # 6 日志操作 日志保留30天，每周一自动切割
        file_handler = TimedRotatingFileHandler(filename=f'{self.base_dir}/logs/{loglevel}.log', when='w0',backupCount=30)
        
        # 7 日志文件前缀
        file_handler.suffix = "%Y-%m-%d.log"
        
        # extMatch是编译好正则表达式，用于匹配日志文件名后缀
        # 需要注意的是suffix和extMatch一定要匹配的上，如果不匹配，过期日志不会被删除。
        file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
        
        # 打印日志
        console = logging.StreamHandler()
        console.setFormatter(self.formatter)
        file_handler.setFormatter(self.formatter)
        
        # 添加处理程序，可以在一个logger添加多个handler
        self.logger.addHandler(console)
        self.logger.addHandler(file_handler)

    def set_log_level(self, log_level):

        if log_level == 'error':
            #  设置日志级别为logging.ERROR
            self.logger.setLevel(logging.ERROR)
        elif log_level == 'debug':
            # 设置日志级别为logging.DEBUG
            self.logger.setLevel(logging.DEBUG)
        else:
            # 设置日志级别为logging.INFO
            self.logger.setLevel(logging.INFO)

    def check_root_dir(self):
        path = f'{self.base_dir}/logs'
        # 检查是是否存在日志文件夹
        if not os.path.exists(path):
            os.makedirs(path)
