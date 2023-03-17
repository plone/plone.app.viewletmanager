from AccessControl.ZopeGuards import guarded_hasattr
from Acquisition import aq_base
from Acquisition.interfaces import IAcquirer
from logging import getLogger
from operator import itemgetter
from plone.app.viewletmanager.interfaces import IViewletManagementView
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from urllib.parse import parse_qs
from urllib.parse import urlencode
from ZODB.POSException import ConflictError
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import implementer
from zope.interface import providedBy
from zope.viewlet.interfaces import IViewlet
from ZPublisher import Retry


logger = getLogger("plone.app.viewletmanager")


class BaseOrderedViewletManager:
    # Sometimes viewlets raise errors handled elsewhere -- e.g. for
    # embedded ploneformgen forms.
    # See https://github.com/plone/plone.app.viewletmanager/issues/5
    _exceptions_handled_elsewhere = (ConflictError, KeyboardInterrupt, Retry)

    def filter(self, viewlets):
        """Filter the viewlets.

        ``viewlets`` is a list of tuples of the form (name, viewlet).

        This filters the viewlets just like Five, but also filters out
        viewlets by name from the local utility which implements the
        IViewletSettingsStorage interface.
        """
        results = []
        storage = queryUtility(IViewletSettingsStorage)
        if storage is None:
            return results
        skinname = self.context.getCurrentSkinName()
        hidden = frozenset(storage.getHidden(self.__name__, skinname))
        # Only return visible viewlets accessible to the principal
        # We need to wrap each viewlet in its context to make sure that
        # the object has a real context from which to determine owner
        # security.
        # Copied from Five
        for name, viewlet in viewlets:
            if IAcquirer.providedBy(viewlet):
                viewlet = viewlet.__of__(viewlet.context)
            if name not in hidden and guarded_hasattr(viewlet, "render"):
                results.append((name, viewlet))
        return results

    def sort(self, viewlets):
        """Sort the viewlets.

        ``viewlets`` is a list of tuples of the form (name, viewlet).

        This sorts the viewlets by the order looked up from the local utility
        which implements the IViewletSettingsStorage interface. The remaining
        ones are sorted just like Five does it.
        """
        result = []
        storage = queryUtility(IViewletSettingsStorage)
        if storage is None:
            return result
        skinname = self.context.getCurrentSkinName()
        order_by_name = storage.getOrder(self.__name__, skinname)
        # first get the known ones
        name_map = dict(viewlets)
        for name in order_by_name:
            if name in name_map:
                result.append((name, name_map[name]))
                del name_map[name]

        try:
            remaining = sorted(name_map.items(), key=lambda x: aq_base(x[1]))
        except:
            remaining = sorted(name_map.items(), key=itemgetter(0))
        # return both together
        return result + remaining

    def render(self):
        if self.template:
            try:
                return self.template(viewlets=self.viewlets)
            except self._exceptions_handled_elsewhere:
                raise
            except Exception:
                logger.exception(
                    'Error while rendering viewlet-manager "{}" '
                    "using a template".format(self.__name__)
                )
                return f"error while rendering viewlet-manager {self.__name__}\n"
        else:
            html = []
            for viewlet in self.viewlets:
                try:
                    html.append(viewlet.render())
                except self._exceptions_handled_elsewhere:
                    raise
                except Exception:
                    logger.exception(
                        "Error while rendering viewlet-manager={}, "
                        "viewlet={}".format(self.__name__, viewlet.__name__)
                    )
                    html.append(f"error while rendering {viewlet.__name__}\n")
            return "\n".join(html)


class OrderedViewletManager(BaseOrderedViewletManager):
    manager_template = ViewPageTemplateFile("manage-viewletmanager.pt")

    def render(self):
        """See zope.contentprovider.interfaces.IContentProvider"""

        # check whether we are in the manager view
        is_managing = False
        parent = getattr(self, "__parent__", None)
        while parent is not None:
            if IViewletManagementView.providedBy(parent):
                is_managing = True
                break
            parent = getattr(parent, "__parent__", None)

        if is_managing:
            # if we are in the managing view, then fetch all viewlets again
            viewlets = getAdapters(
                (self.context, self.request, self.__parent__, self), IViewlet
            )

            # sort them first
            viewlets = self.sort(viewlets)

            storage = getUtility(IViewletSettingsStorage)
            skinname = self.context.getCurrentSkinName()
            hidden = frozenset(storage.getHidden(self.__name__, skinname))

            # then render the ones which are accessible
            base_url = str(
                getMultiAdapter((self.context, self.request), name="absolute_url")
            )
            query_tmpl = "%s/@@manage-viewlets?%%s" % base_url
            results = []
            for index, (name, viewlet) in enumerate(viewlets):
                if IAcquirer.providedBy(viewlet):
                    viewlet = viewlet.__of__(viewlet.context)
                viewlet_id = f"{self.__name__}:{name}"
                options = {
                    "index": index,
                    "name": name,
                    "hidden": name in hidden,
                    "show_url": query_tmpl % urlencode({"show": viewlet_id}),
                    "hide_url": query_tmpl % urlencode({"hide": viewlet_id}),
                }

                if guarded_hasattr(viewlet, "render"):
                    viewlet.update()
                    options["content"] = viewlet.render()
                else:
                    options["content"] = ""
                if index > 0:
                    prev_viewlet = viewlets[index - 1][0]
                    query = {"move_above": f"{viewlet_id};{prev_viewlet}"}
                    options["up_url"] = query_tmpl % urlencode(query)
                if index < (len(viewlets) - 1):
                    next_viewlet = viewlets[index + 1][0]
                    query = {"move_below": f"{viewlet_id};{next_viewlet}"}
                    options["down_url"] = query_tmpl % urlencode(query)
                results.append(options)

            self.name = self.__name__
            self.normalized_name = self.name.replace(".", "-")
            interface = list(providedBy(self).flattened())[0]
            self.interface = interface.__identifier__

            # and output them
            return self.manager_template(viewlets=results)
        # the rest is standard behaviour from zope.viewlet
        else:
            return BaseOrderedViewletManager.render(self)


@implementer(IViewletManagementView)
class ManageViewlets(BrowserView):
    def show(self, manager, viewlet):
        storage = getUtility(IViewletSettingsStorage)
        skinname = self.context.getCurrentSkinName()
        hidden = storage.getHidden(manager, skinname)
        if viewlet in hidden:
            hidden = tuple(x for x in hidden if x != viewlet)
            storage.setHidden(manager, skinname, hidden)

    def hide(self, manager, viewlet):
        storage = getUtility(IViewletSettingsStorage)
        skinname = self.context.getCurrentSkinName()
        hidden = storage.getHidden(manager, skinname)
        if viewlet not in hidden:
            hidden = hidden + (viewlet,)
            storage.setHidden(manager, skinname, hidden)

    def _getOrder(self, manager_name):
        storage = getUtility(IViewletSettingsStorage)
        skinname = self.context.getCurrentSkinName()
        manager = queryMultiAdapter(
            (self.context, self.request, self), IContentProvider, manager_name
        )
        viewlets = getAdapters(
            (manager.context, manager.request, manager.__parent__, manager), IViewlet
        )
        order_by_name = storage.getOrder(manager_name, skinname)
        # first get the known ones
        name_map = dict(viewlets)
        result = []
        for name in order_by_name:
            if name in name_map:
                result.append((name, name_map[name]))
                del name_map[name]

        # then sort the remaining ones
        # Copied from Five
        try:
            remaining = sorted(name_map.items(), key=lambda x: aq_base(x[1]))
        except:
            remaining = sorted(name_map.items(), key=itemgetter(0))

        return [x[0] for x in result + remaining]

    def moveAbove(self, manager, viewlet, dest):
        storage = getUtility(IViewletSettingsStorage)
        skinname = self.context.getCurrentSkinName()
        order = self._getOrder(manager)
        viewlet_index = order.index(viewlet)
        del order[viewlet_index]
        dest_index = order.index(dest)
        order.insert(dest_index, viewlet)
        storage.setOrder(manager, skinname, order)

    def moveBelow(self, manager, viewlet, dest):
        storage = getUtility(IViewletSettingsStorage)
        skinname = self.context.getCurrentSkinName()
        order = self._getOrder(manager)
        viewlet_index = order.index(viewlet)
        del order[viewlet_index]
        dest_index = order.index(dest)
        order.insert(dest_index + 1, viewlet)
        storage.setOrder(manager, skinname, order)

    def __call__(self):
        base_url = "%s/@@manage-viewlets" % str(
            getMultiAdapter((self.context, self.request), name="absolute_url")
        )
        qs = self.request.get("QUERY_STRING", None)
        if qs is not None:
            query = parse_qs(qs)
            if "show" in query:
                for name in query["show"]:
                    manager, viewlet = name.split(":")
                    self.show(manager, viewlet)
                    self.request.response.redirect(base_url)
                    return ""
            if "hide" in query:
                for name in query["hide"]:
                    manager, viewlet = name.split(":")
                    self.hide(manager, viewlet)
                    self.request.response.redirect(base_url)
                    return ""
            if "move_above" in query:
                for name in query["move_above"]:
                    manager, viewlets = name.split(":")
                    viewlet, dest = viewlets.split(";")
                    self.moveAbove(manager, viewlet, dest)
                    self.request.response.redirect(base_url)
                    return ""
            if "move_below" in query:
                for name in query["move_below"]:
                    manager, viewlets = name.split(":")
                    viewlet, dest = viewlets.split(";")
                    self.moveBelow(manager, viewlet, dest)
                    self.request.response.redirect(base_url)
                    return ""
        return self.index()
