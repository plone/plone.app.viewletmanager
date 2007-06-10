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
 <order manager="plone.top" skinname="Plone Default">
  <viewlet name="plone.searchbox"/>
  <viewlet name="plone.logo"/>
  <viewlet name="plone.global_tabs"/>
 </order>
</object>
"""

_EMPTY_EXPORT = """\
<?xml version="1.0"?>
<object name="portal_skins" meta_type="Dummy Skins Tool" allow_any="False"
   cookie_persistence="False" default_skin="default_skin"
   request_varname="request_varname"/>
"""

_NORMAL_EXPORT = """\
<?xml version="1.0"?>
<object name="portal_skins" meta_type="Dummy Skins Tool" allow_any="True"
   cookie_persistence="True" default_skin="basic" request_varname="skin_var">
 <object name="one" meta_type="Filesystem Directory View"
    directory="Products.CMFCore.exportimport.tests:one"/>
 <object name="three" meta_type="Filesystem Directory View"
    directory="Products.CMFCore.exportimport.tests:three"/>
 <object name="two" meta_type="Filesystem Directory View"
    directory="Products.CMFCore.exportimport.tests:two"/>
 <skin-path name="basic">
  <layer name="one"/>
 </skin-path>
 <skin-path name="fancy">
  <layer name="three"/>
  <layer name="two"/>
  <layer name="one"/>
 </skin-path>
</object>
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


class _SkinsSetup(BaseRegistryTests):

    def _initSite(self, selections={}, ids=()):
        from Products.CMFCore.DirectoryView import DirectoryView

        site = DummySite()
        fsdvs = [ (id, DirectoryView(id, 'CMFCore/exportimport/tests/%s' %
                                         id)) for id in ids ]
        site._setObject('portal_skins', DummySkinsTool(selections, fsdvs))

        sm = getSiteManager(site)
        sm.registerUtility(site.portal_skins, ISkinsTool)
        sm.registerUtility(ViewletSettingsStorage(), IViewletSettingsStorage)
        self.storage = getUtility(IViewletSettingsStorage)
        self.storage.setOrder('plone.top', 'Plone Default', ('plone.searchbox',
                                                             'plone.logo',
                                                             'plone.global_tabs'))

        site.REQUEST = 'exists'
        return site

class ViewletSettingsStorageTests(_SkinsSetup):

    layer = ExportImportZCMLLayer

    def test_empty(self):
        from plone.app.viewletmanager.exportimport.storage import exportViewletSettingsStorage

        site = self._initSite()
        print getUtility(IViewletSettingsStorage).getOrder('plone.top', 'Plone Default')
        context = DummyExportContext(site)
        exportViewletSettingsStorage(context)

        print context._wrote
#        self.assertEqual(len(context._wrote), 0)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'viewlets.xml')
        self._compareDOM(text, _EMPTY_EXPORT)
        self.assertEqual(content_type, 'text/xml')

#    def test_normal(self):
#        from Products.CMFCore.exportimport.skins import exportSkinsTool
#
#        _IDS = ('one', 'two', 'three')
#        _PATHS = {'basic': 'one', 'fancy': 'three, two, one'}
#
#        site = self._initSite(selections=_PATHS, ids=_IDS)
#        tool = site.portal_skins
#        tool.default_skin = 'basic'
#        tool.request_varname = 'skin_var'
#        tool.allow_any = True
#        tool.cookie_persistence = True
#
#        context = DummyExportContext(site)
#        exportSkinsTool(context)
#
#        self.assertEqual(len(context._wrote), 1)
#        filename, text, content_type = context._wrote[0]
#        self.assertEqual(filename, 'skins.xml')
#        self._compareDOM(text, _NORMAL_EXPORT)
#        self.assertEqual(content_type, 'text/xml')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ViewletSettingsStorageXMLAdapterTests))
    suite.addTest(makeSuite(ViewletSettingsStorageTests))
    return suite

if __name__ == '__main__':
    framework()

