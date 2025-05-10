from .repo_sync import RepoSync
from .version import __version__
from .options import parser_args
from .utils.logger import logger
import sys

def main(argv=None):
    """Main entry point of the program"""
    try:
        args = parser_args()
        if args.get('version'):
            logger.info(__version__)
            sys.exit(0)
        if args.get('command', '') == '':
            # logging.error("command is empty")
            # argparser.print_help()
            sys.exit(1)
        rs = RepoSync(args)
        rs.run()
    except KeyboardInterrupt:
        logger.error('ERROR: Interrupted by user')
        sys.exit(1)

# GUI入口
def gui_main():
    """GUI entry point of the program"""
    try:
        from .gui_main import main as gui_main_func
        gui_main_func()
    except ImportError as e:
        print(f"GUI dependencies not installed: {e}")
        print("Please install PyQt5 and pywin32 with: pip install PyQt5 pywin32")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting GUI: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
