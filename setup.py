#!/usr/bin/env python

from setuptools import setup, find_packages

with open('readme.rst') as readme:
    long_desc = readme.read()

setup(
    name='ucsc_bed',
    version='0.1.0',
    description='A bioinformatics library that provides a CLI and API for creating a BED file out of the UCSC refseq genes list',
    long_description=long_desc,
    url='https://github.com/MelbourneGenomics/UcscBed',
    author='Michael Milton',
    author_email='michael.r.milton@gmail.com',
    license='GPLv3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    keywords='bioinformatics ucsc bed',
    packages=find_packages(),
    install_requires=['pandas'],
    entry_points={
        'console_scripts': [
            'ucsc_bed=ucsc_bed:main'
        ]
    }
)
