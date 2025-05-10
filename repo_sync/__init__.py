from .repo_sync import RepoSync
from .version import __version__
from .options import parser_args
import sys

def main(argv=None):
    """Main entry point of the program"""
    try:
        args = parser_args()
        if args.get('version'):
            print(__version__)
            sys.exit(0)
        if args.get('command', '') == '':
            # logging.error("command is empty")
            # argparser.print_help()
            sys.exit(1)
        rs = RepoSync(args)
        rs.run()
    except KeyboardInterrupt:
        sys.exit('\nERROR: Interrupted by user')

# GUI入口预留
