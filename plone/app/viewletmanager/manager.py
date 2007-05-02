from zope.component import getUtility

from Acquisition import aq_base
from AccessControl.ZopeGuards import guarded_hasattr

from plone.app.viewletmanager.interfaces import IViewletSettingsStorage

class OrderedViewletManager(object):

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
