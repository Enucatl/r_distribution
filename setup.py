# pylint: disable=all

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from get_git_version.version import get_git_version
from subprocess import check_output


setup(
    name="r_distribution",
    version=get_git_version(),
    packages=find_packages(exclude='test'),
    scripts=[
        "bin/thickness_rotation.py",
    ],

    install_requires=[
        'numpy==1.8.0',
        'h5py==2.2.1',
        'matplotlib==1.3.1',
    ],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },

    # metadata for upload to PyPI
    author="TOMCAT DPC group",
    author_email="",
    description="Analyse ratio of absorption and dark field",
    license="GNU GPL 3",
    keywords="",
    # project home page, if any
    url="https://bitbucket.org/enucatl/r_distribution",
    # could also include long_description, download_url, classifiers, etc.
)
