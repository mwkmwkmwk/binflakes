# coding: utf-8

from codecs import open
from os import path

from setuptools import find_packages, setup

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
        'Programming Language :: Python :: 3.6',
    ],
    keywords='binary parser disassembler',
    packages=find_packages(exclude=[
        'contrib', 'docs', 'docs.*', 'tests', 'tests.*',
    ]),
    install_requires=['attrs>=17.4.0'],
    setup_requires=[
        'docutils',
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pytest-flake8',
        'pytest-sugar',
        # Detects misc bad ideas.
        'flake8-bugbear',
        # Detects shadowing builtins.
        'flake8-builtins',
        # Ensures a trailing comma on multiline lists etc.
        'flake8-commas',
        # Detects things that should be comprehensions.
        'flake8-comprehensions',
        # Detects leftover debugger breakpoints.
        'flake8-debugger',
        # Validates import ordering.
        'flake8-import-order',
        # Detects invalid escape sequences (eg. "\c").
        'flake8-invalid-escape-sequences',
        # Detects leftover print calls.
        'flake8-print',
        # Ensures docstrings are correctly-formatted ReST.
        'flake8-rst-docstrings',
        # Checks PEP8-conforming naming conventions (snake-case, etc.)
        'pep8-naming',
    ],
    package_data={
        'binflakes': [],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
