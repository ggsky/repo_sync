from .repo_sync import RepoSync
from .version import __version__
from .options import parser_args, only_combine_conf
from .utils.logger import logger
import sys

def main(argv=None):
    """Main entry point of the program"""
    try:
        # 如果argv是字典类型，直接使用这些参数
        if isinstance(argv, dict):
            args= only_combine_conf(argv)
        else:
            args = parser_args(argv)
            
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

