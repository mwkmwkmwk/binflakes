# coding: utf-8
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='binflakes',
    version='0',
    description='A catalogue of binary special snowflakes',
    long_description=long_description,
    url='https://github.com/koriakin/binflakes',
    author='Marcin Kościelnicki',
    author_email='koriakin@0x04.net',
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='binary parser disassembler',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    package_data={
        'binflakes': [],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
