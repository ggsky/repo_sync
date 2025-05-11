import logging
import yaml
import os
from repo_sync.utils.frozen_dir import get_app_path
from colorama import Fore, Style
import colorama
import re
colorama.init()

def parse_size(size_str):
    """Convert human readable size string to bytes"""
    if isinstance(size_str, (int, float)):
        return int(size_str)
    
    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 * 1024,
        'GB': 1024 * 1024 * 1024,
        'TB': 1024 * 1024 * 1024 * 1024
    }
    
    # Extract number and unit
    match = re.match(r'^(\d+)\s*([A-Za-z]+)?$', str(size_str).strip())
    if not match:
        return 100 * 1024 * 1024  # Default to 100MB if parsing fails
    
    number, unit = match.groups()
    unit = unit.upper() if unit else 'B'
    
    # Convert to bytes
    return int(float(number) * units.get(unit, 1))

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
    config_path = os.path.join(get_app_path(), 'config.yml')
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
        maxBytes=parse_size(log_config.get('max_size', '100MB')),  # Parse human-readable size
        backupCount=int(log_config.get('max_backups', 3))
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