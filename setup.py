from setuptools import setup, find_packages
import sys, os

version = '1.0rc1'

setup(name='plone.app.viewletmanager',
      version=version,
      description="configurable viewlet manager",
      long_description="""\
A viewlet manager which allows configuration of the filtering and ordering
per skin.
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Florian Schulze',
      author_email='fschulze@plonesolutions.com',
      url='https://svn.plone.org/svn/plone/plone.app.viewletmanager',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
