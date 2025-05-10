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

