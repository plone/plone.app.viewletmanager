#
# Exportimport adapter tests
#

#import os, sys
#if __name__ == '__main__':
#    execfile(os.path.join(sys.path[0], 'framework.py'))

from OFS.Folder import Folder

from zope.component import getUtility, queryUtility, queryMultiAdapter
from zope.component import getSiteManager
from zope.app.component.hooks import setHooks, setSite

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.exportimport.tests.base import BodyAdapterTestCase
from Products.CMFPlone.setuphandlers import PloneGenerator

from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.app.viewletmanager.storage import ViewletSettingsStorage

_VIEWLETS_XML = """\
<?xml version="1.0"?>
<object>
 <order manager="plone.top" skinname="Plone Default">
  <viewlet name="plone.searchbox"/>
  <viewlet name="plone.logo"/>
  <viewlet name="plone.global_tabs"/>
 </order>
</object>
"""


class ViewletSettingsStorageXMLAdapterTest(BodyAdapterTestCase):

    def _getTargetClass(self):
        from plone.app.viewletmanager.exportimport.storage \
                    import ViewletSettingsStorageNodeAdapter
        return ViewletSettingsStorageNodeAdapter

    def _populate(self, obj):
        obj.setOrder('plone.top', "Plone Default", ('plone.searchbox',
                                                    'plone.logo',
                                                    'plone.global_tabs'))

    def setUp(self):
        setHooks()
        self.site = Folder('site')
        gen = PloneGenerator()
        gen.enableSite(self.site)
        setSite(self.site)
        sm = getSiteManager()
        sm.registerUtility(ViewletSettingsStorage(), IViewletSettingsStorage)

        self._obj = getUtility(IViewletSettingsStorage)

        self._BODY = _VIEWLETS_XML

    def test_something(self):
        self.assertEqual('toto', 'lulu')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ViewletSettingsStorageXMLAdapterTest))
    return suite

if __name__ == '__main__':
    framework()

