# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '2.0.11'

long_description = '{0}\n{1}'.format(
    open('README.rst').read(),
    open('CHANGES.rst').read()
)

extras_require = {
    'test': [
        'Products.CMFPlone',
        'plone.app.testing',
        'zope.publisher',
    ]
}

install_requires = [
    'Acquisition',
    'Products.GenericSetup',
    'ZODB3',
    'Zope2',
    'plone.app.vocabularies',
    'setuptools',
    'zope.component',
    'zope.contentprovider',
    'zope.interface',
    'zope.site',
    'zope.viewlet',
]

setup(
    name='plone.app.viewletmanager',
    version=version,
    description='Configurable viewlet manager',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Plone',
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        'Framework :: Zope2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        "Programming Language :: Python :: 2.7",
    ],
    keywords='',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.python.org/pypi/plone.app.viewletmanager',
    license='GPL version 2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone', 'plone.app', ],
    include_package_data=True,
    zip_safe=False,
    extras_require=extras_require,
    install_requires=install_requires,
)
