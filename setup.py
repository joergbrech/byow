"""
Don't use this file directly or via pip. This file
is used by conda-build which handles the dependencies.
"""

import os
from setuptools import setup, find_packages


def read(f_name):
    return open(os.path.join(os.path.dirname(__file__), f_name)).read()


setup(
    name="byow",
    version="0.0.1",
    author="Jan Kleinert",
    author_email="jan@kleinert-bonn.de",
    description="A simple CAD tool for a freestanding DIY climbing wall",
    license="MIT",
    url="https://github.com/joergbrech/climbing-wall",
    packages=find_packages(),
    long_description=read('README.md'),
    entry_points={
        'console_scripts': ['byow=byow.gui:gui'],
    }
)
