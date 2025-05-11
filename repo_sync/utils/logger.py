import logging
import yaml
import os
from colorama import Fore, Style
import colorama
colorama.init()

class ColoredFormatter(logging.Formatter):
    COLOR_MAP = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA
    }
    def format(self, record):
        msg = record.getMessage()
        original_msg = record.msg
        color = self.COLOR_MAP.get(record.levelno, '')
        msg = color + msg + Style.RESET_ALL
        record.msg = msg
        formatted_message = super().format(record)
        # 恢复原始消息
        record.msg = original_msg
        
        return formatted_message

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_logger():
    config = load_config()
    log_config = config.get('log', {})
    
    # Configure logger
    logger = logging.getLogger('repo_sync')
    logger.setLevel(getattr(logging, log_config.get('level', 'INFO').upper()))
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_config.get('console_formatter', {}).get('level', 'INFO').upper()))
    
    # Create file handler with rotation
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_config.get('file', 'repo_sync.log'),
        maxBytes=log_config.get('max_size', 100 * 1024 * 1024),  # Default 100MB
        backupCount=log_config.get('max_backups', 3)
    )
    file_handler.setLevel(getattr(logging, log_config.get('file_formatter', {}).get('level', 'INFO').upper()))
    
    # Use the custom colored formatter for console
    console_formatter = ColoredFormatter(log_config.get('console_formatter', {}).get('format', '%(asctime)s - %(levelname)s - %(message)s'))
    console_handler.setFormatter(console_formatter)
    
    # Use standard formatter for file
    file_formatter = logging.Formatter(log_config.get('file_formatter', {}).get('format', '%(asctime)s - %(levelname)s - %(message)s'))
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Initialize logger
logger = setup_logger()

# Export logger
__all__ = ['logger'] 