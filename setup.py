from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='habranalyzer',
    version='1.0',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "pymorphy2",
    ],
    entry_points={
        'console_scripts':
            ['habranalyzer = habranalyzer.core:main']
    }
)
