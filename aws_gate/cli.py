import os
import sys
import logging
import argparse

from aws_gate import __version__, __description__
from aws_gate.session import session
from aws_gate.utils import is_existing_profile

DEBUG = 'GATE_DEBUG' in os.environ


logger = logging.getLogger(__name__)


def main():

    if 'AWS_PROFILE' in os.environ:
        default_profile = os.environ['AWS_PROFILE']
    else:
        default_profile = 'default'

    if 'AWS_DEFAULT_REGION' in os.environ:
        default_region = os.environ['AWS_DEFAULT_REGION']
    else:
        default_region = 'eu-west-1'

    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-v', '--verbose', help='increase output verbosity',
                        action='store_true')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand', metavar='{session}')

    # 'session' subcommand
    session_parser = subparsers.add_parser('session', help='Open new session on instance and connect to it')
    session_parser.add_argument('-p', '--profile', help='AWS profile to use', default=default_profile)
    session_parser.add_argument('-r', '--region', help='AWS region to use', default=default_region)
    session_parser.add_argument('instance_name', help='Instance we wish to open session to')

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    if not DEBUG:
        sys.excepthook = lambda exc_type, exc_value, traceback: logger.error(exc_value)

    log_level = logging.ERROR
    log_format = '%(message)s'

    # We want to silence dependencies
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    logging.getLogger('boto3').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)

    if args.verbose:
        log_level = logging.INFO

    if DEBUG:
        log_level = logging.DEBUG
        log_format = '%(asctime)s - %(name)-16s - %(levelname)-5s - %(message)s'

    logging.basicConfig(level=log_level, stream=sys.stderr, format=log_format)

    if not is_existing_profile(args.profile):
        raise ValueError('Invalid profile provided: {}'.format(args.profile))

    if args.subcommand == 'session':
        session(instance_name=args.instance_name, region_name=args.region, profile_name=args.profile)


if __name__ == '__main__':
    main()
