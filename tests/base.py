"""Base class for integration tests, based on PloneTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

# Set up a Plone site - note that the portlets branch of CMFPlone applies
# a portlets profile.
setupPloneSite()

class TestCase(PloneTestCase):
    pass

class FunctionalTestCase(FunctionalTestCase):
    pass