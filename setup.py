from pathlib import Path
from setuptools import find_packages
from setuptools import setup


version = "4.0.4"

long_description = (
    f"{Path('README.rst').read_text()}\n{Path('CHANGES.rst').read_text()}"
)

extras_require = {
    "test": [
        "Products.CMFPlone",
        "plone.app.testing",
        "plone.testing",
        "zope.publisher",
    ]
}

install_requires = [
    "Products.GenericSetup",
    "Products.CMFCore",
    "Zope",
    "persistent",
    "setuptools",
    "zope.contentprovider",
    "zope.viewlet",
]

setup(
    name="plone.app.viewletmanager",
    version=version,
    description="Configurable viewlet manager",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Zope",
        "Framework :: Zope :: 5",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="viewlets",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/plone.app.viewletmanager",
    license="GPL version 2",
    packages=find_packages(),
    python_requires=">=3.8",
    namespace_packages=[
        "plone",
        "plone.app",
    ],
    include_package_data=True,
    zip_safe=False,
    extras_require=extras_require,
    install_requires=install_requires,
)
