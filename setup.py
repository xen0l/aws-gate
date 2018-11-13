import inspect
import os
from setuptools import setup, find_packages

from aws_gate import __version__, __description__

__location__ = os.path.join(
    os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe()))
)


def get_install_requirements(path):
    with open(os.path.join(__location__, path), 'r') as f:
        content = f.read()
        requires = [req for req in content.split('\\n') if req != '']

    return requires


setup(
    name='aws-gate',
    version=__version__,
    description=__description__,
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    author='Adam Stevko',
    author_email='adam.stevko@gmail.com',
    packages=find_packages(),
    url='https://github.com/xen0l/aws-gate',
    install_requires=get_install_requirements('requirements/requirements.txt'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: System :: Systems Administration",
    ],
    scripts=[
        'bin/aws-gate',
    ],
)
