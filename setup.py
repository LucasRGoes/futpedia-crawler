# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


__version__ = '0.1.0'


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


setup(
    name='scrapedia',
    version=__version__,
    description=('A scraper/crawler used for the extraction of historic data'
                 ' from the webpage futpedia.globo.com'),
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Lucas Góes',
    author_email='lucas.rd.goes@gmail.com',
    url='https://github.com/LucasRGoes/scrapedia',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
