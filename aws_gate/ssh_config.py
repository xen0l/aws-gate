import logging
from collections import OrderedDict

from aws_gate.constants import (
    AWS_DEFAULT_PROFILE,
    AWS_DEFAULT_REGION,
    DEFAULT_SSH_PORT,
    DEFAULT_OS_USER,
    DEFAULT_GATE_DIR,
)
from aws_gate.decorators import valid_aws_region, valid_aws_profile

logger = logging.getLogger(__name__)

@valid_aws_profile
@valid_aws_region
def ssh_config(
    profile_name=AWS_DEFAULT_PROFILE,
    region_name=AWS_DEFAULT_REGION,
    user=DEFAULT_OS_USER,
    port=DEFAULT_SSH_PORT,
):
    PROXY_COMMAND = [
        r"""sh -c "aws-gate ssh-proxy -l {} -p `echo %h | sed -Ee 's/^(.*)\.(.*)\.(.*)$/\\3/g'`""".format(user),
        r"""-r `echo %h | sed -Ee 's/^(.*)\.(.*)\.(.*)$/\\2/g'`""",
        r'''`echo %h | sed -Ee 's/^(.*)\.(.*)\.(.*)$/\\1/g'`"''',
    ]
    config = OrderedDict(
        {
            "Host": "*.{}.{}".format(region_name, profile_name),
            "IdentityFile": "{}/%h".format(DEFAULT_GATE_DIR),
            "IdentitiesOnly": "yes",
            "User": user,
            "Port": port,
            "ProxyCommand": " ".join(PROXY_COMMAND),
        }
    )
    for k, v in config.items():
        print("{} {}".format(k, v))
    print()
