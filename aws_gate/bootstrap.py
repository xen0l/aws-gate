import os
import logging
import tempfile
import shutil
import zipfile
import platform
import subprocess
import requests

from aws_gate.exceptions import UnsupportedPlatormError
from aws_gate.config import DEFAULT_GATE_DIR

DEFAULT_GATE_BIN_DIR = os.path.join(DEFAULT_GATE_DIR, 'bin')
PLUGIN_NAME = 'session-manager-plugin'
PLUGIN_INSTALL_PATH = os.path.join(DEFAULT_GATE_BIN_DIR, PLUGIN_NAME)

MAC_PLUGIN_URL = 'https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac/sessionmanager-bundle.zip'


logger = logging.getLogger(__name__)


def _execute(path, args):

    ret = None
    try:
        logger.debug('Executing "{}"'.format(' '.join([path] + args)))
        result = subprocess.run([path] + args, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logger.error('Command "{}" exited with {}'.format(' '.join([path] + args), e.returncode))

    if result.stdout:
        ret = result.stdout.decode()
        ret = ret.rstrip()

    return ret


class Plugin():
    url = None
    download_path = None

    @property
    def is_installed(self):
        logger.debug('Checking if {} exists and is executable'.format(PLUGIN_INSTALL_PATH))
        return shutil.which(PLUGIN_INSTALL_PATH) is None

    def download(self):
        tmp_dir = tempfile.mkdtemp()
        file_name = os.path.split(self.url)[-1]

        self.download_path = os.path.join(tmp_dir, file_name)
        try:
            logger.debug('Downloading session-manager-plugin archive from %s', self.url)
            with requests.get(self.url, stream=True) as req:
                req.raise_for_status()
                with open(self.download_path, 'wb') as f:
                    shutil.copyfileobj(req.raw, f)
                    logger.debug('Download stored at %s', self.download_path)
        except requests.exceptions.HTTPError as e:
            logger.error('HTTP error while downloading %s: %s', self.url, e)

    def install(self):
        raise NotImplementedError

    def extract(self):
        raise NotImplementedError


class MacPlugin(Plugin):
    url = MAC_PLUGIN_URL

    def install(self):
        download_dir = os.path.split(self.download_path)[0]
        plugin_src_path = os.path.join(download_dir, 'sessionmanager-bundle', 'bin', PLUGIN_NAME)
        plugin_dst_path = PLUGIN_INSTALL_PATH

        if not os.path.exists(DEFAULT_GATE_BIN_DIR):
            logger.debug('Creating %s', DEFAULT_GATE_BIN_DIR)
            os.mkdir(DEFAULT_GATE_BIN_DIR)

        with open(plugin_src_path, 'rb') as f_src, open(plugin_dst_path, 'wb') as f_dst:
            logger.debug('Copying %s to %s', plugin_src_path, plugin_dst_path)
            shutil.copyfileobj(f_src, f_dst)

        logger.debug('Setting execution permissions on %s', plugin_dst_path)
        os.chmod(plugin_dst_path, 0o755)

        version = _execute(PLUGIN_INSTALL_PATH, ['--version'])
        print('{} (version {}) installed successfully!'.format(PLUGIN_NAME, version))

    def extract(self):
        if not zipfile.is_zipfile(self.download_path):
            raise ValueError('Invalid macOS session-manager-plugin ZIP file found {}'.format(self.download_path))

        with zipfile.ZipFile(self.download_path, 'r') as zip_file:
            download_dir = os.path.split(self.download_path)[0]
            zip_file.extractall(download_dir)
            logger.debug('Extracted session-manager-plugin archive at %s', download_dir)


def bootstrap(force):
    system = platform.system()
    if system == 'Darwin':
        plugin = MacPlugin()
    else:
        raise UnsupportedPlatormError('Unable to bootstrap session-manager-plugin on {}'.format(system))

    if plugin.is_installed or force:
        plugin.download()
        plugin.extract()
        plugin.install()
