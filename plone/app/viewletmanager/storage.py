from zope.interface import implements

from persistent import Persistent

from plone.app.viewletmanager.interfaces import IViewletSettingsStorage


class ViewletSettingsStorage(Persistent):
    def getOrder(self, name, skinname):
        if name == "plone.portaltop":
            return ('plone.header',
                     'plone.personal_bar',
                     'plone.app.i18n.locales.languageselector',
                     'plone.path_bar',
                    )
        elif name == "plone.portalheader":
            return ('plone.skip_links',
                     'plone.site_actions',
                     'plone.searchbox',
                     'plone.logo',
                     'plone.global_sections',
                    )
        else:
            return ()

    def getHidden(self, name, skinname):
        return ()
