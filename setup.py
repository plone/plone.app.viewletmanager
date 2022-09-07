# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '4.0.0b1'

long_description = '{0}\n{1}'.format(
    open('README.rst').read(),
    open('CHANGES.rst').read()
)

extras_require = {
    'test': [
        'Products.CMFPlone',
        'plone.app.testing',
        'six',
        'zope.publisher',
    ]
}

install_requires = [
    'Acquisition',
    'Products.GenericSetup',
    'ZODB',
    'Zope',
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
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        'Framework :: Zope',
        'Framework :: Zope :: 5',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords='viewlets',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.org/project/plone.app.viewletmanager',
    license='GPL version 2',
    packages=find_packages(),
    namespace_packages=['plone', 'plone.app', ],
    include_package_data=True,
    zip_safe=False,
    extras_require=extras_require,
    install_requires=install_requires,
)
