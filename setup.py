import inspect
import os

from setuptools import setup, find_packages

from aws_gate import __version__, __description__, __author__, __author_email__, __url__

__location__ = os.path.join(
    os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe()))
)


def get_install_requirements(path):
    with open(os.path.join(__location__, path), "r") as f:
        content = f.read()
        requires = [req for req in content.split("\\n") if req != ""]

    return requires


NAME = "aws-gate"
PROJECT_URLS = {
    "Bug Tracker": "https://github.com/xen0l/aws-gate/issues",
    "Source Code": "https://github.com/xen0l/aws-gate",
}
CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Topic :: System :: Systems Administration",
]
INSTALL_REQUIRES = get_install_requirements("requirements/requirements.txt")
EXTRA_REQUIRES = {
    "tests": get_install_requirements("requirements/requirements_dev.txt")
}
SCRIPTS = ["bin/aws-gate"]

setup(
    name=NAME,
    version=__version__,
    description=__description__,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url=__url__,
    project_urls=PROJECT_URLS,
    author=__author__,
    author_email=__author_email__,
    packages=find_packages(),
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRA_REQUIRES,
    include_package_data=True,
    scripts=SCRIPTS,
)
