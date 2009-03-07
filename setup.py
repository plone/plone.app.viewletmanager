from setuptools import setup, find_packages
import os

version = '1.2.2'

setup(name='plone.app.viewletmanager',
      version=version,
      description="configurable viewlet manager",
      long_description=open("README.txt").read() + "\n" + \
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Framework :: Plone",
          "Framework :: Zope2",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='',
      author='Florian Schulze',
      author_email='fschulze@jarn.com',
      url='http://pypi.python.org/pypi/plone.app.viewletmanager',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'zope.publisher',
            'zope.testing',
            'Plone',
            'Products.PloneTestCase',
        ]
      ),
      install_requires=[
        'setuptools',
        'zope.component',
        'zope.contentprovider',
        'zope.interface',
        'zope.viewlet',
        'Products.GenericSetup',
      ],
      )
