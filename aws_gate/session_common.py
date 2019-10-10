import json
import logging

from aws_gate.utils import execute_plugin

logger = logging.getLogger(__name__)


class BaseSession:
    _instance_id = None
    _ssm = None
    _region_name = None
    _profile_name = None

    _response = None
    _session_id = None
    _token_value = None

    _session_parameters = {}

    def __enter__(self):
        # create and establish session
        self.create()
        return self

    def __exit__(self, *args):
        # terminate session
        self.terminate()

    def create(self):
        logger.debug(
            "Creating a new session on instance: %s (%s)",
            self._instance_id,
            self._region_name,
        )
        self._response = self._ssm.start_session(**self._session_parameters)
        logger.debug("Received response: %s", self._response)

        self._session_id, self._token_value = (
            self._response["SessionId"],
            self._response["TokenValue"],
        )

    def terminate(self):
        logger.debug("Terminating session: %s", self._session_id)
        response = self._ssm.terminate_session(SessionId=self._session_id)
        logger.debug("Received response: %s", response)

    def open(self):
        execute_plugin(
            [
                json.dumps(self._response),
                self._region_name,
                "StartSession",
                self._profile_name,
                json.dumps(self._session_parameters),
                self._ssm.meta.endpoint_url,
            ]
        )
