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
from Products.CMFCore.testing import ExportImportZCMLLayer

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.exportimport.tests.base import BodyAdapterTestCase
from Products.CMFPlone.setuphandlers import PloneGenerator

from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.app.viewletmanager.storage import ViewletSettingsStorage

_VIEWLETS_XML = """\
<?xml version="1.0"?>
<object>
 <order manager="plone.top" skinname="One">
  <viewlet name="plone.searchbox"/>
  <viewlet name="plone.logo"/>
  <viewlet name="plone.global_tabs"/>
 </order>
 <hidden manager="plone.top" skinname="Two">
  <viewlet name="plone.logo"/>
 </hidden>
</object>
"""

_EMPTY_EXPORT = """\
<?xml version="1.0"?>
<object />
"""

_EMPTY_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order manager="plone.top" skinname="One" />
 <order manager="plone.top" skinname="Two" />
</object>
"""

_EMPTY_NOPURGE_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order manager="plone.top" skinname="One" purge="False" />
 <order manager="plone.top" skinname="Two" purge="False" />
</object>
"""

_FRAGMENT1IMPORT = """\
<?xml version="1.0"?>
<object>
 <order manager="plone.top" skinname="Three" make_default="True">
  <viewlet name="plone.logo"/>
  <viewlet name="plone.searchbox"/>
  <viewlet name="plone.global_tabs"/>
 </order>
 <hidden manager="plone.top" skinname="Three" make_default="True">
  <viewlet name="plone.global_tabs"/>
 </hidden>
</object>
"""

class Layer:
    @classmethod
    def setUp(cls):
        from zope.component import provideAdapter
        
        from plone.app.viewletmanager.exportimport.storage import ViewletSettingsStorageNodeAdapter
        from Products.GenericSetup.interfaces import IBody
        from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
        from Products.GenericSetup.interfaces import ISetupEnviron
        
        provideAdapter(factory=ViewletSettingsStorageNodeAdapter, 
            adapts=(IViewletSettingsStorage, ISetupEnviron),
            provides=IBody)

class ViewletSettingsStorageXMLAdapterTests(BodyAdapterTestCase):
    
    layer = Layer

    def _getTargetClass(self):
        from plone.app.viewletmanager.exportimport.storage \
                    import ViewletSettingsStorageNodeAdapter
        return ViewletSettingsStorageNodeAdapter

    def _populate(self, obj):
        obj.setOrder('plone.top', 'One', ('plone.searchbox',
                                                    'plone.logo',
                                                    'plone.global_tabs'))
        obj.setHidden('plone.top', 'Two', ('plone.logo',))

    def _verifyImport(self, obj):
        orderdict = {u'plone.top': (u'plone.searchbox', u'plone.logo', u'plone.global_tabs')}
        hiddendict = {u'plone.top': (u'plone.logo',)}
        self.assertEqual(type(obj._order), PersistentDict)
        self.failUnless('One' in obj._order.keys())
        self.assertEqual(type(obj._order['One']), PersistentDict)
        self.assertEqual(dict(obj._order['One']), orderdict)
        self.failUnless('default_skin' in obj._order.keys())
        self.assertEqual(type(obj._order['default_skin']), PersistentDict)
        self.assertEqual(dict(obj._order['default_skin']), orderdict)
        self.assertEqual(type(obj._hidden), PersistentDict)
        self.failUnless('Two' in obj._hidden.keys())
        self.assertEqual(type(obj._hidden['Two']), PersistentDict)
        self.assertEqual(dict(obj._hidden['Two']), hiddendict)
        self.failIf('default_skin' in obj._hidden.keys())

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
    
    layer = Layer

    def _initSite(self, populate=False):
        self.root.site = Folder(id='site')
        site = self.root.site

        sm = getSiteManager(site)
        sm.registerUtility(ViewletSettingsStorage(), IViewletSettingsStorage)
        self.storage = getUtility(IViewletSettingsStorage)

        if populate:
            self.storage.setOrder('plone.top', 'One', ('plone.searchbox',
                                                       'plone.logo',
                                                       'plone.global_tabs'))
            self.storage.setHidden('plone.top', 'Two', ('plone.logo',))

        return site

class exportViewletSettingsStorageTests(_ViewletSettingsStorageSetup):

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


class importViewletSettingsStorageTests(_ViewletSettingsStorageSetup):

    _VIEWLETS_XML = _VIEWLETS_XML
    _EMPTY_IMPORT = _EMPTY_IMPORT
    _EMPTY_NOPURGE_IMPORT = _EMPTY_NOPURGE_IMPORT
    _FRAGMENT1IMPORT = _FRAGMENT1IMPORT

    def test_empty_default_purge(self):
        from plone.app.viewletmanager.exportimport.storage import importViewletSettingsStorage

        site = self._initSite(populate=True)
        utility = getUtility(IViewletSettingsStorage)

        self.assertEqual(len(utility._order['One']['plone.top']), 3)
        self.failIf('default_skin' in utility._hidden.keys())

        context = DummyImportContext(site)
        context._files['viewlets.xml'] = self._EMPTY_IMPORT
        importViewletSettingsStorage(context)

        self.assertEqual(len(utility._order['One']['plone.top']), 0)
        self.failIf('default_skin' in utility._hidden.keys())

    def test_empty_explicit_purge(self):
        from plone.app.viewletmanager.exportimport.storage import importViewletSettingsStorage

        site = self._initSite(populate=True)
        utility = getUtility(IViewletSettingsStorage)

        self.assertEqual(len(utility._order['One']['plone.top']), 3)
        self.failIf('default_skin' in utility._hidden.keys())

        # XXX (davconvent): not sure the True param is even taken care of
        context = DummyImportContext(site, True)
        context._files['viewlets.xml'] = self._EMPTY_IMPORT
        importViewletSettingsStorage(context)

        self.assertEqual(len(utility._order['One']['plone.top']), 0)
        self.failIf('default_skin' in utility._hidden.keys())

    def test_empty_skip_purge(self):
        # XXX (davconvent): We'll need to take care of this case later on
        return
        from plone.app.viewletmanager.exportimport.storage import importViewletSettingsStorage

        site = self._initSite(populate=True)
        utility = getUtility(IViewletSettingsStorage)

        self.assertEqual(len(utility._order['One']['plone.top']), 3)
        self.failIf('default_skin' in utility._hidden.keys())

        # XXX (davconvent): not sure the False param is even taken care of
#        context = DummyImportContext(site, False)
#        context._files['viewlets.xml'] = self._EMPTY_IMPORT
        context = DummyImportContext(site)
        context._files['viewlets.xml'] = self._EMPTY_NOPURGE_IMPORT
        importViewletSettingsStorage(context)

        self.assertEqual(len(utility._order['One']['plone.top']), 3)
        self.failIf('default_skin' in utility._hidden.keys())

    def test_make_default(self):
        from plone.app.viewletmanager.exportimport.storage import importViewletSettingsStorage

        site = self._initSite(populate=True)
        utility = getUtility(IViewletSettingsStorage)

        self.assertEqual(utility.getOrder('plone.top', 'Another Skin'),
                    ('plone.searchbox', 'plone.logo', 'plone.global_tabs'))
        self.assertEqual(utility.getHidden('plone.top', 'Another Skin'), ())

        context = DummyImportContext(site, False)
        context._files['viewlets.xml'] = self._FRAGMENT1IMPORT
        importViewletSettingsStorage(context)

        self.assertEqual(utility.getOrder('plone.top', 'Another Skin'),
                    ('plone.logo', 'plone.searchbox', 'plone.global_tabs'))
        self.assertEqual(utility.getHidden('plone.top', 'Another Skin'),
                                                    ('plone.global_tabs',))

    def test_z_keep_default(self):
        #z if from having that test called last
        from plone.app.viewletmanager.exportimport.storage import importViewletSettingsStorage

        site = self._initSite(populate=True)
        utility = getUtility(IViewletSettingsStorage)

        self.assertEqual(utility.getOrder('plone.top', 'Another Skin'),
                    ('plone.logo', 'plone.searchbox', 'plone.global_tabs'))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ViewletSettingsStorageXMLAdapterTests))
    suite.addTest(makeSuite(exportViewletSettingsStorageTests))
    suite.addTest(makeSuite(importViewletSettingsStorageTests))
    return suite

if __name__ == '__main__':
    framework()

