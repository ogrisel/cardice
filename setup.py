#! /usr/bin/env python
#
# Copyright (C) 2013 Olivier Grisel <olivier.grisel@ensta.org>

description = """Cloud compute cluster configuration tool"""

import sys
import os
import shutil
from distutils.command.clean import clean as Clean


DISTNAME = 'cardice'
DESCRIPTION = 'Cloud compute cluster configuration tool'
#LONG_DESCRIPTION = open('README.rst').read()
MAINTAINER = 'Olivier Grisel'
MAINTAINER_EMAIL = 'olivier.grisel@ensta.org'
URL = 'http://github.com/ogrisel/cardice'
LICENSE = 'MIT'
DOWNLOAD_URL = 'http://pypi.python.org/pypi/cardice'


import cardice
VERSION = cardice.__version__


try:
    from setuptools import setup
    extra_setuptools_args = dict(
        zip_safe=False,
        include_package_data=True,
    )
except ImportError:
    from distutils.core import setup
    extra_setuptools_args = dict()


class CleanCommand(Clean):
    description = "Remove generated files in the source tree"

    def run(self):
        Clean.run(self)
        if os.path.exists('build'):
            shutil.rmtree('build')
        for dirpath, dirnames, filenames in os.walk('cardice'):
            for filename in filenames:
                if (filename.endswith('.so') or filename.endswith('.pyd')
                             or filename.endswith('.dll')
                             or filename.endswith('.pyc')):
                    os.unlink(os.path.join(dirpath, filename))


def setup_package():
    setup(
        name=DISTNAME,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        license=LICENSE,
        url=URL,
        version=VERSION,
        download_url=DOWNLOAD_URL,
        #long_description=LONG_DESCRIPTION,
        packages=['cardice'],
        scripts=['scripts/cardice'],
        classifiers=[
            'Intended Audience :: Science/Research',
            'Intended Audience :: Developers',
            'License :: OSI Approved',
            'Programming Language :: Python',
            'Topic :: Software Development',
            'Topic :: Scientific/Engineering',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Operating System :: Unix',
            'Operating System :: MacOS',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
        ],
        cmdclass={'clean': CleanCommand},
        **extra_setuptools_args)

if __name__ == "__main__":
    setup_package()
