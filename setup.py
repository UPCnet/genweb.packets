# -*- coding: utf-8 -*-
"""
This module contains the tool of genweb.packets
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('src', 'genweb', 'packets', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n')

tests_require = ['zope.testing']

setup(name='genweb.packets',
      version=version,
      description="Continguts empaquetats",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        ],
      keywords='',
      author='UPCnet Plone Team',
      author_email='plone.team@upcnet.es',
      url='https://github.com/upcnet/genweb.packets',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['genweb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'pyquery'
                        ],
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      test_suite='genweb.packets.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      # setup_requires=["PasteScript"],
      # paster_plugins=["templer.localcommands"],
      )
