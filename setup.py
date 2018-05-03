#!/usr/bin/env python
from setuptools import setup

setup(
    name='classutil-scraper',
    version='1.1',
    description='A python scraper for unsw classutil (http://classutil.unsw.edu.au/)',
    url="https://github.com/anon1mous/classutil-scraper",
    author='Chen Zhou',
    author_email="czhou428420713@gmail.com",
    license='MIT',
    packages=['classutil_scraper'],
    install_requires=[
        'requests',
        'bs4'
    ],
    zip_safe=False
)
