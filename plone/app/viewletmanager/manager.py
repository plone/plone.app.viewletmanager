from zope.interface import implements
from zope.component import getUtility, getAdapters

from zope.viewlet.interfaces import IViewlet

from Acquisition import aq_base
from AccessControl.ZopeGuards import guarded_hasattr
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.app.viewletmanager.interfaces import IViewletManagementView


class OrderedViewletManager(object):
    manager_template = ViewPageTemplateFile('manage-viewletmanager.pt')

    def filter(self, viewlets):
        """Filter the viewlets.
    
        ``viewlets`` is a list of tuples of the form (name, viewlet).

        This filters the viewlets just like Five, but also filters out
        viewlets by name from the local utility which implements the
        IViewletSettingsStorage interface.
        """
        storage = getUtility(IViewletSettingsStorage)
        skinname = self.context.getCurrentSkinName()
        hidden = storage.getHidden(self.__name__, skinname)
        results = []
        # Only return visible viewlets accessible to the principal
        # We need to wrap each viewlet in its context to make sure that
        # the object has a real context from which to determine owner
        # security.
        # Copied from Five
        for name, viewlet in viewlets:
            viewlet = viewlet.__of__(viewlet.context)
            if name not in hidden and guarded_hasattr(viewlet, 'render'):
                results.append((name, viewlet))
        return results

    def sort(self, viewlets):
        """Sort the viewlets.

        ``viewlets`` is a list of tuples of the form (name, viewlet).

        This sorts the viewlets by the order looked up from the local utility
        which implements the IViewletSettingsStorage interface. The remaining
        ones are sorted just like Five does it.
        """

        storage = getUtility(IViewletSettingsStorage)
        skinname = self.context.getCurrentSkinName()
        order_by_name = storage.getOrder(self.__name__, skinname)
        # first get the known ones
        name_map = dict(viewlets)
        result = []
        for name in order_by_name:
            if name in name_map:
                result.append((name, name_map[name]))
                del name_map[name]

        # then sort the remaining ones
        # Copied from Five
        remaining = sorted(name_map.items(),
                           lambda x, y: cmp(aq_base(x[1]), aq_base(y[1])))

        # return both together
        return result + remaining

    def render(self):
        """See zope.contentprovider.interfaces.IContentProvider"""

        # check whether we are in the manager view
        is_managing = False
        parent = getattr(self, '__parent__', None)
        while parent is not None:
            if IViewletManagementView.providedBy(parent):
                is_managing = True
                break
            parent = getattr(parent, '__parent__', None)

        if is_managing:
            # if we are in the managing view, then fetch all viewlets again
            viewlets = getAdapters(
                (self.context, self.request, self.__parent__, self),
                IViewlet)

            # sort them first
            viewlets = self.sort(viewlets)

            # then render the ones which are accessible
            results = []
            for name, viewlet in viewlets:
                viewlet = viewlet.__of__(viewlet.context)
                if guarded_hasattr(viewlet, 'render'):
                    viewlet.update()
                    results.append({'name': name,
                                    'content': viewlet.render()})
                else:
                    results.append({'name': name,
                                    'content': ""})

            self.name = self.__name__
            # and output them
            return self.manager_template(viewlets=results)
        # the rest is standard behaviour from zope.viewlet
        elif self.template:
            return self.template(viewlets=self.viewlets)
        else:
            return u'\n'.join([viewlet.render() for viewlet in self.viewlets])


class ManageViewlets(BrowserView):
    implements(IViewletManagementView)
