import logging

logger = logging.getLogger(__name__)


class BaseSession:
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
        logger.debug('Creating a new session on instance: %s (%s)', self._instance_id, self._region_name)
        self._response = self._ssm.start_session(**self._session_parameters)
        logger.debug('Received response: %s', self._response)

        self._session_id, self._token_value = self._response['SessionId'], self._response['TokenValue']

    def terminate(self):
        logger.debug('Terminating session: %s', self._session_id)
        response = self._ssm.terminate_session(SessionId=self._session_id)
        logger.debug('Received response: %s', response)
