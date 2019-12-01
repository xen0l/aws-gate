import os

DEBUG = "GATE_DEBUG" in os.environ

AWS_DEFAULT_REGION = "eu-west-1"
AWS_DEFAULT_PROFILE = "default"

DEFAULT_OS_USER = "ec2-user"
DEFAULT_SSH_PORT = 22
DEFAULT_KEY_ALGORITHM = "rsa"
DEFAULT_KEY_SIZE = 2048
SUPPORTED_KEY_TYPES = ["rsa", "ed25519"]
KEY_MIN_SIZE = DEFAULT_KEY_SIZE

DEFAULT_LIST_OUTPUT = "human"
DEFAULT_LIST_OUTPUT_FORMATS = ["json", "human", "tsv", "csv"]
DEFAULT_LIST_OUTPUT_FIELDS = (
    "instance_id",
    "instance_name",
    "availability_zone",
    "vpc_id",
    "private_ip_address",
    "public_ip_addess",
    "private_dns_name",
    "public_dns_name",
)
DEFAULT_LIST_HUMAN_FIELDS = (
    "instance_id",
    "instance_name",
    "availability_zone",
    "vpc_id",
    "private_ip_address",
)

DEFAULT_GATE_DIR = os.path.expanduser("~/.aws-gate")
DEFAULT_GATE_CONFIG_PATH = os.path.join(DEFAULT_GATE_DIR, "config")
DEFAULT_GATE_CONFIGD_PATH = os.path.join(DEFAULT_GATE_DIR, "config.d")

PLUGIN_NAME = "session-manager-plugin"
DEFAULT_GATE_BIN_PATH = os.path.join(DEFAULT_GATE_DIR, "bin")
PLUGIN_INSTALL_PATH = os.path.join(DEFAULT_GATE_BIN_PATH, PLUGIN_NAME)

DEFAULT_GATE_KEY_PATH = os.path.join(DEFAULT_GATE_DIR, "key")

SSM_PLUGIN_BASE_URL = "https://s3.amazonaws.com/session-manager-downloads/plugin/latest"
SSM_PLUGIN_PATH = {
    "Darwin": {
        "download": SSM_PLUGIN_BASE_URL + "/mac/sessionmanager-bundle.zip",
        "bundle": os.path.join("sessionmanager-bundle", "bin", PLUGIN_NAME),
    },
    "Linux": {
        "download": SSM_PLUGIN_BASE_URL + "/ubuntu_64bit/session-manager-plugin.deb",
        "bundle": os.path.join(
            "usr", "local", "sessionmanagerplugin", "bin", PLUGIN_NAME
        ),
    },
}
