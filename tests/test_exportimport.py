from OFS.Folder import Folder

from persistent.dict import PersistentDict
from zope.component import getUtility
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

COMMON_SETUP_ORDER = {
    'basic': {'top': ('one',)},
    'fancy': {'top': ('two', 'three', 'one')},
    }

COMMON_SETUP_HIDDEN = {
    'light': {'top': ('one',)},
    }

_VIEWLETS_XML = """\
<?xml version="1.0"?>
<object>
 <order manager="top" skinname="fancy">
  <viewlet name="two"/>
  <viewlet name="three"/>
  <viewlet name="one"/>
 </order>
 <order manager="top" skinname="basic">
  <viewlet name="one"/>
 </order>
 <hidden manager="top" skinname="light">
  <viewlet name="one"/>
 </hidden>
</object>
"""

_EMPTY_EXPORT = """\
<?xml version="1.0"?>
<object />
"""

_FRAGMENT1_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order skinname="*">
  <viewlet name="three" insert-before="two"/>
 </order>
</object>
"""

_FRAGMENT2_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order skinname="*">
  <viewlet name="four" insert-after="three"/>
 </order>
</object>
"""

_FRAGMENT3_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order skinname="*">
  <viewlet name="three" insert-before="*"/>
  <viewlet name="four" insert-after="*"/>
 </order>
</object>
"""

_FRAGMENT4_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order skinname="*">
  <viewlet name="three" remove="1"/>
 </order>
</object>
"""

_FRAGMENT5_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order name="existing" based-on="basic">
 </order>
 <order name="new" based-on="basic">
  <viewlet name="two" insert-before="three"/>
 </order>
 <order name="wrongbase" based-on="invalid_base_id">
  <viewlet name="two" insert-before="three"/>
 </order>
</object>"""

_FRAGMENT6_IMPORT = """\
<?xml version="1.0"?>
 <order name="basic">
  <viewlet name="one"/>
 </order>
 <order name="fancy" remove="True"/>
 <order name="invalid" remove="True"/>
</object>
"""

_FRAGMENT7_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order manager="top" skinname="added" make_default="True">
  <viewlet name="one"/>
  <viewlet name="two"/>
  <viewlet name="three"/>
 </order>
 <hidden manager="top" skinname="added" make_default="True">
  <viewlet name="one"/>
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
        obj.setOrder('top', 'fancy', ('two', 'three', 'one'))
        obj.setOrder('top', 'basic', ('one',))
        obj.setHidden('top', 'light', ('one',))

    def _verifyImport(self, obj):
        fancydict = {'top': ('two', 'three', 'one')}
        hiddendict = {'top': ('one',)}
        self.assertEqual(type(obj._order), PersistentDict)
        self.failUnless('fancy' in obj._order.keys())
        self.assertEqual(type(obj._order['fancy']), PersistentDict)
        self.assertEqual(dict(obj._order['fancy']), fancydict)
        self.failUnless('default_skin' in obj._order.keys())
        self.assertEqual(type(obj._order['default_skin']), PersistentDict)
        self.assertEqual(dict(obj._order['default_skin']), fancydict)
        self.assertEqual(type(obj._hidden), PersistentDict)
        self.failUnless('light' in obj._hidden.keys())
        self.assertEqual(type(obj._hidden['light']), PersistentDict)
        self.assertEqual(dict(obj._hidden['light']), hiddendict)
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

    def setUp(self):
        BaseRegistryTests.setUp(self)
        self.root.site = Folder(id='site')
        self.site = self.root.site

        sm = getSiteManager(self.site)
        sm.registerUtility(ViewletSettingsStorage(), IViewletSettingsStorage)
        self.storage = getUtility(IViewletSettingsStorage)

    def _populateSite(self, order={}, hidden={}):
        storage = self.storage
        for skinname in order.keys():
            for manager in order[skinname].keys():
                self.storage.setOrder(manager, skinname,
                                            order[skinname][manager])

        for skinname in hidden.keys():
            for manager in hidden[skinname].keys():
                self.storage.setHidden(manager, skinname,
                                            hidden[skinname][manager])

    def tearDown(self):
        sm = getSiteManager(self.site)
        sm.unregisterUtility(provided=IViewletSettingsStorage)
        BaseRegistryTests.tearDown(self)


class exportViewletSettingsStorageTests(_ViewletSettingsStorageSetup):

    def test_empty(self):
        from plone.app.viewletmanager.exportimport.storage import exportViewletSettingsStorage

        context = DummyExportContext(self.site)
        exportViewletSettingsStorage(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'viewlets.xml')
        self._compareDOM(text, _EMPTY_EXPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_normal(self):
        from plone.app.viewletmanager.exportimport.storage import exportViewletSettingsStorage

        _ORDER = COMMON_SETUP_ORDER
        _HIDDEN = COMMON_SETUP_HIDDEN
        self._populateSite(order=_ORDER, hidden=_HIDDEN)
        
        context = DummyExportContext(self.site)
        exportViewletSettingsStorage(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'viewlets.xml')
        self._compareDOM(text, _VIEWLETS_XML)
        self.assertEqual(content_type, 'text/xml')


class importViewletSettingsStorageTests(_ViewletSettingsStorageSetup):

    _VIEWLETS_XML = _VIEWLETS_XML
    _EMPTY_EXPORT = _EMPTY_EXPORT
    _FRAGMENT7_IMPORT = _FRAGMENT7_IMPORT

    def test_default_no_purge(self):
        from plone.app.viewletmanager.exportimport.storage import importViewletSettingsStorage

        _ORDER = COMMON_SETUP_ORDER
        _HIDDEN = COMMON_SETUP_HIDDEN
        self._populateSite(order=_ORDER, hidden=_HIDDEN)

        site = self.site
        utility = self.storage

        self.assertEqual(len(utility.getOrder('top', 'fancy')), 3)
        self.assertEqual(len(utility.getOrder('top', 'basic')), 1)
        self.assertEqual(len(utility.getHidden('top', 'light')), 1)
        self.failUnless('default_skin' in utility._order.keys())
        self.assertEqual(len(utility.getOrder('top', 'undefined')), 3)
        self.failIf('default_skin' in utility._hidden.keys())

        context = DummyImportContext(site)
        context._files['viewlets.xml'] = self._EMPTY_EXPORT
        importViewletSettingsStorage(context)

        self.assertEqual(len(utility.getOrder('top', 'fancy')), 3)
        self.assertEqual(len(utility.getOrder('top', 'basic')), 1)
        self.assertEqual(len(utility.getHidden('top', 'light')), 1)
        self.failUnless('default_skin' in utility._order.keys())
        self.assertEqual(len(utility.getOrder('top', 'undefined')), 3)
        self.failIf('default_skin' in utility._hidden.keys())

    def test_normal(self):
        from plone.app.viewletmanager.exportimport.storage import importViewletSettingsStorage

        site = self.site
        utility = self.storage
        self.assertEqual(len(utility._order.keys()), 0)
        self.assertEqual(len(utility._hidden.keys()), 0)

        context = DummyImportContext(site)
        context._files['viewlets.xml'] = self._VIEWLETS_XML
        importViewletSettingsStorage(context)

        self.assertEqual(utility.getOrder('top', 'fancy'), ('three', 'two', 'one'))
        self.assertEqual(utility.getOrder('top', 'basic'), ('one',))
        self.assertEqual(utility.getHidden('top', 'light'), ('one',))

    def test_make_default(self):
        from plone.app.viewletmanager.exportimport.storage import importViewletSettingsStorage

        _ORDER = COMMON_SETUP_ORDER
        _HIDDEN = COMMON_SETUP_HIDDEN
        self._populateSite(order=_ORDER, hidden=_HIDDEN)
        self.assertEqual(len(utility._order.keys()), 3)
        self.assertEqual(len(utility._hidden.keys()), 3)

        site = self.site
        utility = self.storage

        self.assertEqual(utility.getOrder('top', 'undefined'),
                    ('two', 'three', 'one'))
        self.assertEqual(utility.getHidden('top', 'undefined'), ())

        context = DummyImportContext(site, False)
        context._files['viewlets.xml'] = self._FRAGMENT7_IMPORT
        importViewletSettingsStorage(context)

        self.assertEqual(utility.getOrder('top', 'undefined'),
                    ('one', 'two', 'three'))
        self.assertEqual(utility.getHidden('top', 'undefined'),
                                                    ('one',))

    def test_z_means_last(self):
        from plone.app.viewletmanager.exportimport.storage import importViewletSettingsStorage

        site = self.site
        utility = self.storage
        # Make sure we have nothing in the utility
        self.assertEqual(len(utility._order.keys()), 0)
        self.assertEqual(len(utility._hidden.keys()), 0)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ViewletSettingsStorageXMLAdapterTests))
    suite.addTest(makeSuite(exportViewletSettingsStorageTests))
    suite.addTest(makeSuite(importViewletSettingsStorageTests))
    return suite

if __name__ == '__main__':
    framework()

