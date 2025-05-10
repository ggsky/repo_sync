import logging
from termcolor import colored

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        # 保留原始消息不变
        original_msg = record.msg
        if record.levelno == logging.DEBUG:
            record.msg = colored(record.msg, 'blue')
        elif record.levelno == logging.INFO:
            record.msg = colored(record.msg, 'green')
        elif record.levelno == logging.WARNING:
            record.msg = colored(record.msg, 'yellow')
        elif record.levelno == logging.ERROR:
            record.msg = colored(record.msg, 'red')
        elif record.levelno == logging.CRITICAL:
            record.msg = colored(record.msg, 'magenta')
        
        # 调用父类格式化方法
        formatted_message = super().format(record)
        
        # 恢复原始消息
        record.msg = original_msg
        
        return formatted_message

# Configure logger
logger = logging.getLogger('repo_sync')
logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler('repo_sync.log')
file_handler.setLevel(logging.INFO)

# Use the custom colored formatter
console_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Add handler to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Export logger
__all__ = ['logger'] 