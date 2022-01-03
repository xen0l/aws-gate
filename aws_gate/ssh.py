import json
import logging
import shlex

from aws_gate.constants import (
    AWS_DEFAULT_PROFILE,
    AWS_DEFAULT_REGION,
    DEFAULT_OS_USER,
    DEFAULT_SSH_PORT,
    DEFAULT_KEY_ALGORITHM,
    DEFAULT_KEY_SIZE,
    PLUGIN_INSTALL_PATH,
    DEBUG,
    DEFAULT_GATE_KEY_PATH,
)
from aws_gate.decorators import (
    plugin_version,
    plugin_required,
    valid_aws_profile,
    valid_aws_region,
)
from aws_gate.query import query_instance
from aws_gate.session_common import BaseSession
from aws_gate.ssh_common import SshKey, SshKeyUploader
from aws_gate.utils import (
    get_aws_client,
    get_aws_resource,
    fetch_instance_details_from_config,
    get_instance_details,
    execute,
)

logger = logging.getLogger(__name__)


class SshSession(BaseSession):
    def __init__(
        self,
        instance_id,
        ssm=None,
        region_name=AWS_DEFAULT_REGION,
        profile_name=AWS_DEFAULT_PROFILE,
        port=DEFAULT_SSH_PORT,
        user=DEFAULT_OS_USER,
        command=None,
        local_forward=None,
        remote_forward=None,
        dynamic_forward=None,
    ):
        self._instance_id = instance_id
        self._region_name = region_name
        self._profile_name = profile_name if profile_name is not None else ""
        self._ssm = ssm
        self._port = port
        self._user = user
        self._command = command
        self._local_forward = local_forward
        self._remote_forward = remote_forward
        self._dynamic_forward = dynamic_forward

        self._ssh_cmd = None

        self._session_parameters = {
            "Target": self._instance_id,
            "DocumentName": "AWS-StartSSHSession",
            "Parameters": {"portNumber": [str(self._port)]},
        }

    def _build_ssh_command(self):
        cmd = [
            "ssh",
            "-l",
            self._user,
            "-p",
            str(self._port),
            "-F",
            "/dev/null",
            "-i",
            DEFAULT_GATE_KEY_PATH,
        ]

        if self._local_forward or self._remote_forward or self._dynamic_forward:
            cmd.append("-N")

        if self._local_forward:
            cmd.extend(["-L", self._local_forward])

        if self._remote_forward:
            cmd.extend(["-R", self._remote_forward])

        if self._dynamic_forward:
            cmd.extend(["-D", self._dynamic_forward])

        if DEBUG:
            cmd.append("-vv")
        else:
            cmd.append("-q")

        proxy_command_args = [
            PLUGIN_INSTALL_PATH,
            json.dumps(self._response),
            self._region_name,
            "StartSession",
            self._profile_name,
            json.dumps(self._session_parameters),
            self._ssm.meta.endpoint_url,
        ]
        proxy_command = " ".join(shlex.quote(i) for i in proxy_command_args)

        ssh_options = [
            "IdentitiesOnly=yes",
            "UserKnownHostsFile=/dev/null",
            "StrictHostKeyChecking=no",
            f"ProxyCommand={proxy_command}",
        ]

        for ssh_option in ssh_options:
            cmd.append("-o")
            cmd.append(ssh_option)

        cmd.append(self._instance_id)

        if self._command:
            cmd.append("--")
            cmd.extend(self._command)

        return cmd

    def open(self):
        self._ssh_cmd = self._build_ssh_command()

        return execute(self._ssh_cmd[0], self._ssh_cmd[1:])


@plugin_required
@plugin_version("1.1.23.0")
@valid_aws_profile
@valid_aws_region
def ssh(
    config,
    instance_name,
    user=DEFAULT_OS_USER,
    port=DEFAULT_SSH_PORT,
    key_type=DEFAULT_KEY_ALGORITHM,
    key_size=DEFAULT_KEY_SIZE,
    profile_name=AWS_DEFAULT_PROFILE,
    region_name=AWS_DEFAULT_REGION,
    command=None,
    local_forward=None,
    remote_forward=None,
    dynamic_forward=None,
):
    instance, profile, region = fetch_instance_details_from_config(
        config, instance_name, profile_name, region_name
    )

    ssm = get_aws_client("ssm", region_name=region, profile_name=profile)
    ec2 = get_aws_resource("ec2", region_name=region, profile_name=profile)
    ec2_ic = get_aws_client(
        "ec2-instance-connect", region_name=region, profile_name=profile
    )

    instance_id = query_instance(name=instance, ec2=ec2)
    if instance_id is None:
        raise ValueError(f"No instance could be found for name: {instance}")

    az = get_instance_details(instance_id=instance_id, ec2=ec2)["availability_zone"]

    logger.info(
        "Opening SSH session on instance %s (%s) via profile %s",
        instance_id,
        region,
        profile,
    )
    if local_forward:  # pragma: no cover
        logger.info("SSH session will do a local port forwarding: %s", local_forward)
    if remote_forward:  # pragma: no cover
        logger.info("SSH session will do a remote port forwarding: %s", remote_forward)
    if dynamic_forward:  # pragma: no cover
        logger.info(
            "SSH session will do a dynamic port forwarding: %s", dynamic_forward
        )
    with SshKey(key_type=key_type, key_size=key_size) as ssh_key:
        with SshKeyUploader(
            instance_id=instance_id, az=az, user=user, ssh_key=ssh_key, ec2_ic=ec2_ic
        ):
            with SshSession(
                instance_id,
                region_name=region,
                profile_name=profile,
                ssm=ssm,
                port=port,
                user=user,
                command=command,
                local_forward=local_forward,
                remote_forward=remote_forward,
                dynamic_forward=dynamic_forward,
            ) as ssh_session:
                ssh_session.open()
