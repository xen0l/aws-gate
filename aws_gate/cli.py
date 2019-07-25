import os
import sys
import logging
import argparse

from marshmallow import ValidationError
from yaml.scanner import ScannerError

from aws_gate import __version__, __description__
from aws_gate.config import load_config_from_files
from aws_gate.bootstrap import bootstrap
from aws_gate.session import session
from aws_gate.list import list_instances
from aws_gate.utils import get_default_region

DEBUG = 'GATE_DEBUG' in os.environ

AWS_DEFAULT_REGION = 'eu-west-1'

logger = logging.getLogger(__name__)


def _get_profile(args, config, default):
    profile = None
    if 'profile' in args:
        profile = args.profile
    return profile or config.default_profile or default


def _get_region(args, config, default):
    region = None
    if 'region' in args:
        region = args.region
    return region or config.default_region or default


def parse_arguments():

    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-v', '--verbose', help='increase output verbosity',
                        action='store_true')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand', metavar='{bootstrap, session, list}')

    # 'bootstrap' subcommand
    bootstrap_parser = subparsers.add_parser('bootstrap', help='Download and install session-manager-plugin')
    bootstrap_parser.add_argument('-f', '--force', action='store_true', help='Forces bootstrap operation')

    # 'session' subcommand
    session_parser = subparsers.add_parser('session', help='Open new session on instance and connect to it')
    session_parser.add_argument('-p', '--profile', help='AWS profile to use')
    session_parser.add_argument('-r', '--region', help='AWS region to use')
    session_parser.add_argument('instance_name', help='Instance we wish to open session to')

    # 'list' subcommand
    ls_parser = subparsers.add_parser('list', aliases=['ls'], help='List available instances')
    ls_parser.add_argument('-p', '--profile', help='AWS profile to use')
    ls_parser.add_argument('-r', '--region', help='AWS region to use')

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    return args


def main():

    # We want to provide default values in cases they are not configured in ~/.aws/config or availabe as
    # environment variables
    default_region = get_default_region()
    if default_region is None:
        default_region = AWS_DEFAULT_REGION

    # We try to obtain default profile from the environment or use 'default' to save call to boto3.
    # boto3 will also return 'default': https://github.com/boto/boto3/blob/develop/boto3/session.py#L93
    default_profile = os.environ.get('AWS_PROFILE') or 'default'

    args = parse_arguments()

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

    try:
        config = load_config_from_files()
    except (ValidationError, ScannerError) as e:
        raise ValueError('Invalid configuration provided: {}'.format(e.message))

    profile = _get_profile(args=args, config=config, default=default_profile)
    region = _get_region(args=args, config=config, default=default_region)

    if args.subcommand == 'bootstrap':
        bootstrap(force=args.force)
    if args.subcommand == 'session':
        session(config=config, instance_name=args.instance_name, region_name=region, profile_name=profile)
    if args.subcommand in ['ls', 'list']:
        list_instances(region_name=args.region, profile_name=args.profile)


if __name__ == '__main__':
    main()
