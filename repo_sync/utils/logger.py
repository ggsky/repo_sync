import logging
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
        color = self.COLOR_MAP.get(record.levelno, '')
        msg = color + msg + Style.RESET_ALL
        record.message = msg
        return super().format(record)
    
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