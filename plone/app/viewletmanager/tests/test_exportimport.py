from OFS.Folder import Folder

from persistent.dict import PersistentDict
from zope.component import getUtility
from zope.component import getSiteManager
from zope.app.component.hooks import setHooks, setSite

from Products.GenericSetup.tests.common import BaseRegistryTests
from Products.GenericSetup.tests.common import DummyExportContext
from Products.GenericSetup.tests.common import DummyImportContext

from Products.CMFPlone.exportimport.tests.base import BodyAdapterTestCase
from Products.CMFPlone.setuphandlers import PloneGenerator

from marsapp.categories.storage import IMarscatsSettingsStorage
from marsapp.categories.storage import MarscatsSettingsStorage

COMMON_SETUP = {
    'one': {'portal_types': {'my_content': 'cat-one',
                             'other_content': '',
                             },
            },
    'two': {'startup_directory': 'cat-two',},
    }

_MARSCATS_XML = """\
<?xml version="1.0"?>
<object>
 <field name="two" startup_directory="cat-two"/>
 <field name="one">
  <portal_types>
   <portal_type name="my_content" startup_directory="cat-one"/>
   <portal_type name="other_content"/>
  </portal_types>
 </field>
</object>
"""

_EMPTY_EXPORT = """\
<?xml version="1.0"?>
<object />
"""

_CHILD_PURGE_IMPORT = """\
<?xml version="1.0"?>
<object>
 <field name="one" purge="true"/>
</object>
"""

_TYPESCHILD_PURGE_IMPORT = """\
<?xml version="1.0"?>
<object>
 <field name="one">
  <portal_types purge="true"/>
 </field>
</object>
"""


_FRAGMENT1_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order manager="top" skinname="fancy">
  <viewlet name="three" insert-before="two"/>
 </order>
</object>
"""

class Layer:
    @classmethod
    def setUp(cls):
        from zope.component import provideAdapter
        
        from marsapp.categories.exportimport.storage import MarscatsSettingsStorageNodeAdapter
        from Products.GenericSetup.interfaces import IBody
        from marsapp.categories.storage import IMarscatsSettingsStorage
        from Products.GenericSetup.interfaces import ISetupEnviron
        
        provideAdapter(factory=MarscatsSettingsStorageNodeAdapter, 
            adapts=(IMarscatsSettingsStorage, ISetupEnviron),
            provides=IBody)

class MarscatsSettingsStorageXMLAdapterTests(BodyAdapterTestCase):
    
    layer = Layer

    def _getTargetClass(self):
        from marsapp.categories.exportimport.storage \
                    import MarscatsSettingsStorageNodeAdapter
        return MarscatsSettingsStorageNodeAdapter

    def _populate(self, obj):
        obj.setStartupDir('one', 'cat-one', 'my_content')
        obj.setStartupDir('one', '', 'other_content')
        obj.setStartupDir('two', 'cat-two')
        
    def _verifyImport(self, obj):
        one = {'portal_types': {'my_content': 'cat-one',
                                'other_content': ''},
               }
        two = {'startup_directory': 'cat-two'}
        self.assertEqual(type(obj._fields), PersistentDict)
        self.failUnless('one' in obj._fields)
        self.assertEqual(type(obj._fields['one']), PersistentDict)
        self.failUnless('portal_types' in obj._fields['one'])
        self.assertEqual(type(obj._fields['one']['portal_types']),
                         PersistentDict)
        self.failUnless('my_content' in obj._fields['one']['portal_types'])
        self.failUnless('other_content' in obj._fields['one']['portal_types'])
        self.assertEqual(obj._fields['one'], one)
        self.failUnless('two' in obj._fields)
        self.assertEqual(type(obj._fields['two']), PersistentDict)
        self.failUnless('portal_types' not in obj._fields['two'])
        self.failUnless('startup_directory' in obj._fields['two'])
        self.assertEqual(obj._fields['two'], two)

    def setUp(self):
        setHooks()
        self.site = Folder('site')
        gen = PloneGenerator()
        gen.enableSite(self.site)
        setSite(self.site)
        sm = getSiteManager()
        sm.registerUtility(MarscatsSettingsStorage(),
                           IMarscatsSettingsStorage)

        self._obj = getUtility(IMarscatsSettingsStorage)

        self._BODY = _MARSCATS_XML

class _MarscatsSettingsStorageSetup(BaseRegistryTests):

    layer = Layer

    def setUp(self):
        BaseRegistryTests.setUp(self)
        setHooks()
        self.root.site = Folder(id='site')
        self.site = self.root.site
        gen = PloneGenerator()
        gen.enableSite(self.site)
        setSite(self.site)
        sm = getSiteManager(self.site)
        sm.registerUtility(MarscatsSettingsStorage(), IMarscatsSettingsStorage)
        self.storage = getUtility(IMarscatsSettingsStorage)

    def _populateSite(self, fields={}):
        storage = self.storage
        for fieldname in fields.keys():
            field = fields[fieldname]
            if field.has_key('startup_directory'):
                storage.setStartupDir(fieldname, field['startup_directory'])
            if field.has_key('portal_types'):
                for typename in field['portal_types']:
                    storage.setStartupDir(fieldname,
                                          field['portal_types'][typename],
                                          typename)

class exportMarscatsSettingsStorageTests(_MarscatsSettingsStorageSetup):

    def test_empty(self):
        from marsapp.categories.exportimport.storage import \
                                                exportMarscatsSettingsStorage

        context = DummyExportContext(self.site)
        exportMarscatsSettingsStorage(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'marscats.xml')
        self._compareDOM(text, _EMPTY_EXPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_normal(self):
        from marsapp.categories.exportimport.storage import \
                                                exportMarscatsSettingsStorage

        self._populateSite(fields=COMMON_SETUP)

        context = DummyExportContext(self.site)
        exportMarscatsSettingsStorage(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'marscats.xml')
        self._compareDOM(text, _MARSCATS_XML)
        self.assertEqual(content_type, 'text/xml')


class importMarscatsSettingsStorageTests(_MarscatsSettingsStorageSetup):

    _MARSCATS_XML               = _MARSCATS_XML
    _EMPTY_EXPORT               = _EMPTY_EXPORT
    _CHILD_PURGE_IMPORT         = _CHILD_PURGE_IMPORT
    _TYPESCHILD_PURGE_IMPORT    = _TYPESCHILD_PURGE_IMPORT

    def test_empty_default_purge(self):
        from marsapp.categories.exportimport.storage import \
                                                importMarscatsSettingsStorage

        _FIELDS = COMMON_SETUP
        self._populateSite(fields=_FIELDS)

        self.assertEqual(len(self.storage._fields), 2)
        self.assertEqual(len(self.storage._fields['one']), 1)
        self.assertEqual(len(self.storage._fields['two']), 1)

        context = DummyImportContext(self.site)
        context._files['marscats.xml'] = self._EMPTY_EXPORT
        importMarscatsSettingsStorage(context)

        self.assertEqual(len(self.storage._fields), 0)

    def test_empty_explicit_purge(self):
        from marsapp.categories.exportimport.storage import \
                                                importMarscatsSettingsStorage

        _FIELDS = COMMON_SETUP
        self._populateSite(fields=_FIELDS)

        context = DummyImportContext(self.site, True)
        context._files['marscats.xml'] = self._EMPTY_EXPORT
        importMarscatsSettingsStorage(context)

        self.assertEqual(len(self.storage._fields), 0)


    def test_empty_skip_purge(self):
        from marsapp.categories.exportimport.storage import \
                                                importMarscatsSettingsStorage

        _FIELDS = COMMON_SETUP
        self._populateSite(fields=_FIELDS)

        context = DummyImportContext(self.site, False)
        context._files['marscats.xml'] = self._EMPTY_EXPORT
        importMarscatsSettingsStorage(context)

        self.assertEqual(len(self.storage._fields), 2)
        self.assertEqual(len(self.storage._fields['one']), 1)
        self.assertEqual(len(self.storage._fields['two']), 1)

    def test_specific_child_purge(self):
        from marsapp.categories.exportimport.storage import \
                                                importMarscatsSettingsStorage

        _FIELDS = COMMON_SETUP
        self._populateSite(fields=_FIELDS)

        context = DummyImportContext(self.site, False)
        context._files['marscats.xml'] = self._CHILD_PURGE_IMPORT
        importMarscatsSettingsStorage(context)

        self.assertEqual(len(self.storage._fields), 2)
        self.assertEqual(len(self.storage._fields['one']), 0)
        self.assertEqual(len(self.storage._fields['two']), 1)


    def test_specific_typeschild_purge(self):
        from marsapp.categories.exportimport.storage import \
                                                importMarscatsSettingsStorage

        _FIELDS = COMMON_SETUP
        self._populateSite(fields=_FIELDS)

        self.assertEqual(len(self.storage._fields['one']['portal_types']), 2)

        context = DummyImportContext(self.site, False)
        context._files['marscats.xml'] = self._TYPESCHILD_PURGE_IMPORT
        importMarscatsSettingsStorage(context)

        self.assertEqual(len(self.storage._fields), 2)
        self.assertEqual(len(self.storage._fields['one']), 1)
        self.assertEqual(len(self.storage._fields['one']['portal_types']), 0)
        self.assertEqual(len(self.storage._fields['two']), 1)


    def test_normal(self):
        from marsapp.categories.exportimport.storage import \
                                                importMarscatsSettingsStorage

        self.assertEqual(len(self.storage._fields), 0)

        context = DummyImportContext(self.site, False)
        context._files['marscats.xml'] = self._MARSCATS_XML
        importMarscatsSettingsStorage(context)

        self.assertEqual(len(self.storage._fields), 2)
        self.assertEqual(len(self.storage._fields['one']), 1)
        self.assertEqual(len(self.storage._fields['two']), 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(MarscatsSettingsStorageXMLAdapterTests))
    suite.addTest(makeSuite(exportMarscatsSettingsStorageTests))
    suite.addTest(makeSuite(importMarscatsSettingsStorageTests))
    return suite

if __name__ == '__main__':
    framework()

