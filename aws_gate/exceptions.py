class Error(Exception):
    pass


class InstanceNotFound(Error):
    pass


class AWSConnectionError(Error):
    pass
