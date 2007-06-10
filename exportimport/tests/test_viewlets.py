#
# Exportimport adapter tests
# Got inspiration from tests in CMFCore/exportimport/tests
#

#import os, sys
#if __name__ == '__main__':
#    execfile(os.path.join(sys.path[0], 'framework.py'))

from OFS.Folder import Folder

from persistent.dict import PersistentDict
from zope.component import getUtility, queryUtility, queryMultiAdapter
from zope.component import getSiteManager
from zope.app.component.hooks import setHooks, setSite

from Products.GenericSetup.tests.common import BaseRegistryTests
from Products.GenericSetup.tests.common import DummyExportContext
from Products.GenericSetup.tests.common import DummyImportContext

from Products.CMFCore.interfaces import ISkinsTool
from Products.CMFCore.exportimport.tests.test_skins import DummySkinsTool
from Products.CMFCore.exportimport.tests.test_skins import DummySite
#from Products.CMFCore.testing import ExportImportZCMLLayer

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.exportimport.tests.base import BodyAdapterTestCase
from Products.CMFPlone.setuphandlers import PloneGenerator

from Products.PloneTestCase.layer import PloneSite

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
 <hidden manager="plone.top" skinname="Plone Default">
  <viewlet name="plone.logo"/>
 </hidden>
</object>
"""

_EMPTY_EXPORT = """\
<?xml version="1.0"?>
<object />
"""

class ViewletSettingsStorageXMLAdapterTests(BodyAdapterTestCase):

    def _getTargetClass(self):
        from plone.app.viewletmanager.exportimport.storage \
                    import ViewletSettingsStorageNodeAdapter
        return ViewletSettingsStorageNodeAdapter

    def _populate(self, obj):
        obj.setOrder('plone.top', "Plone Default", ('plone.searchbox',
                                                    'plone.logo',
                                                    'plone.global_tabs'))
        obj.setHidden('plone.top', "Plone Default", ('plone.logo',))

    def _verifyImport(self, obj):
        orderdict = {u'plone.top': (u'plone.searchbox', u'plone.logo', u'plone.global_tabs')}
        hiddendict = {u'plone.top': (u'plone.logo',)}
        self.assertEqual(type(obj._order), PersistentDict)
        self.failUnless('Plone Default' in obj._order.keys())
        self.assertEqual(type(obj._order['Plone Default']), PersistentDict)
        self.assertEqual(dict(obj._order['Plone Default']), orderdict)
        self.failUnless('default_skin' in obj._order.keys())
        self.assertEqual(type(obj._order['default_skin']), PersistentDict)
        self.assertEqual(dict(obj._order['default_skin']), orderdict)
        self.assertEqual(type(obj._hidden), PersistentDict)
        self.failUnless('Plone Default' in obj._hidden.keys())
        self.assertEqual(type(obj._hidden['Plone Default']), PersistentDict)
        self.assertEqual(dict(obj._hidden['Plone Default']), hiddendict)
        self.failUnless('default_skin' in obj._hidden.keys())
        self.assertEqual(type(obj._hidden['default_skin']), PersistentDict)
        self.assertEqual(dict(obj._hidden['default_skin']), hiddendict)

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


class _ViewletSettingsStorageSetup(BaseRegistryTests):

    def _initSite(self, populate=False):
        self.root.site = Folder(id='site')
        site = self.root.site

        sm = getSiteManager(site)
#        sm.registerUtility(site.portal_skins, ISkinsTool)
        sm.registerUtility(ViewletSettingsStorage(), IViewletSettingsStorage)
        self.storage = getUtility(IViewletSettingsStorage)

        if populate:
            self.storage.setOrder('plone.top', 'Plone Default',
                                                    ('plone.searchbox',
                                                     'plone.logo',
                                                     'plone.global_tabs'))
            self.storage.setHidden('plone.top', "Plone Default",
                                                    ('plone.logo',))

        return site

class ViewletSettingsStorageTests(_ViewletSettingsStorageSetup):

    layer = PloneSite

    def test_empty(self):
        from plone.app.viewletmanager.exportimport.storage import exportViewletSettingsStorage

        site = self._initSite()
        context = DummyExportContext(site)
        exportViewletSettingsStorage(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'viewlets.xml')
        self._compareDOM(text, _EMPTY_EXPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_normal(self):
        from plone.app.viewletmanager.exportimport.storage import exportViewletSettingsStorage

        site = self._initSite(populate=True)
        context = DummyExportContext(site)
        exportViewletSettingsStorage(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'viewlets.xml')
        self._compareDOM(text, _VIEWLETS_XML)
        self.assertEqual(content_type, 'text/xml')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ViewletSettingsStorageXMLAdapterTests))
    suite.addTest(makeSuite(ViewletSettingsStorageTests))
    return suite

if __name__ == '__main__':
    framework()

