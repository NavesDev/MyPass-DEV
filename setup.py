from setuptools import setup, find_packages

setup(
    name='mypass',
    version='0.1.0',
    packages=find_packages(), 
    entry_points={
        'console_scripts': [
            'mypass = script.cli:app',
        ],
    },
)