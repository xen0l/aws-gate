import os

DEBUG = 'GATE_DEBUG' in os.environ

AWS_DEFAULT_REGION = 'eu-west-1'

DEFAULT_GATE_DIR = os.path.expanduser('~/.aws-gate')
DEFAULT_GATE_CONFIG_PATH = os.path.join(DEFAULT_GATE_DIR, 'config')
DEFAULT_GATE_CONFIGD_PATH = os.path.join(DEFAULT_GATE_DIR, 'config.d')

PLUGIN_NAME = 'session-manager-plugin'
DEFAULT_GATE_BIN_PATH = os.path.join(DEFAULT_GATE_DIR, 'bin')
PLUGIN_INSTALL_PATH = os.path.join(DEFAULT_GATE_BIN_PATH, PLUGIN_NAME)

DEFAULT_GATE_KEY_PATH = os.path.join(DEFAULT_GATE_DIR, 'key')

MAC_PLUGIN_URL = 'https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac/sessionmanager-bundle.zip'

SUPPORTED_KEY_TYPES = ['rsa', 'ed25519']
KEY_MIN_SIZE = 2048
