# pylint: disable=all

from setuptools import setup, find_packages
from subprocess import check_output


setup(
    name="r_distribution",
    version="v1.0.0",
    packages=find_packages(exclude='test'),
    scripts=[
        "bin/thickness_rotation.py",
    ],

    install_requires=[
        'numpy',
        'h5py',
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
