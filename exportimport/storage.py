from zope.component import getUtility, queryUtility, queryMultiAdapter

from plone.app.viewletmanager.interfaces import IViewletSettingsStorage

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.utils import XMLAdapterBase

def importViewletSettingsStorage(context):
    """Import viewlet settings."""
    logger = context.getLogger('plone.app.viewletmanager')

    body = context.readDataFile('viewlets.xml')
    if body is None:
        logger.info("Nothing to import")
        return

    storage = getUtility(IViewletSettingsStorage)

    importer = queryMultiAdapter((storage, context), IBody)
    if importer is None:
        logger.warning("Import adapter missing.")
        return

    importer.body = body
    logger.info("Imported.")

def exportViewletSettingsStorage(context):
    """Export viewlet settings."""
    logger = context.getLogger('plone.app.viewletmanager')

    storage = queryUtility(IViewletSettingsStorage)

    if storage is None:
        logger.info("Nothing to export")
        return

    exporter = queryMultiAdapter((storage, context), IBody)
    if exporter is None:
        logger.warning("Export adapter missing.")
        return

    context.writeDataFile('viewlets.xml', exporter.body, exporter.mime_type)
    logger.info("Exported.")


class ViewletSettingsStorageNodeAdapter(XMLAdapterBase):
    __used_for__ = IViewletSettingsStorage

    def _exportNode(self):
        """
        Export the object as a DOM node.
        """
        storage = getUtility(IViewletSettingsStorage)
        output = self._doc.createElement('object')
        for skin in storage._order:
            for name in storage._order[skin]:
                node = self._doc.createElement('order')
                node.setAttribute('skinname', skin)
                node.setAttribute('manager', name)
                for viewlet in storage._order[skin][name]:
                    child = self._doc.createElement('viewlet')
                    child.setAttribute('name', viewlet)
                    node.appendChild(child)
                output.appendChild(node)
        for skin in storage._hidden:
            for name in storage._hidden[skin]:
                node = self._doc.createElement('hidden')
                node.setAttribute('skinname', skin)
                node.setAttribute('manager', name)
                for viewlet in storage._hidden[skin][name]:
                    child = self._doc.createElement('viewlet')
                    child.setAttribute('name', viewlet)
                    node.appendChild(child)
                output.appendChild(node)
        return output

    def _importNode(self, node):
        """
        Import the object from the DOM node.
        """
        storage = getUtility(IViewletSettingsStorage)
        for child in node.childNodes:
            if child.nodeName != 'order' and child.nodeName != 'hidden':
                continue
            skinname = child.getAttribute('skinname')
            manager = child.getAttribute('manager')
            if skinname == '*':
                for skinname in getattr(storage, '_'+child.nodeName).keys():
                    values = []
                    if child.nodeName == 'order':
                        try:
                            values = list(storage._order[skinname][manager])
                        except KeyError:
                            pass
                        values = self._updateValues(values, child)
                        storage.setOrder(manager, skinname, tuple(values))
                    elif child.nodeName == 'hidden':
                        try:
                            values = list(storage._hidden[skinname][manager])
                        except KeyError:
                            pass
                        values = self._updateValues(values, child)
                        storage.setHidden(manager, skinname, tuple(values))
            else:
                values = []
                if child.nodeName == 'order':
                    basename = skinname
                    if child.hasAttribute('based-on'):
                        basename = child.getAttribute('based-on')
                    try:
                        values = list(storage._order[basename][manager])
                    except KeyError:
                        pass
                    for value in values:
                        if value not in values:
                            viewletnode = self._doc.createElement('viewlet')
                            viewletnode.setAttribute('name', value)
                            if values.index(value) == 0:
                                viewletnode.setAttribute('insert-before', '*')
                            else:
                                pos = values[values.index(value)-1]
                                viewletnode.setAttribute('insert-after', pos)
                            child.appendChild(viewletnode)
                    values = self._updateValues(values, child)
                    storage.setOrder(manager, skinname, tuple(values))

                elif child.nodeName == 'hidden':
                    basename = skinname
                    if child.hasAttribute('based-on'):
                        basename = child.getAttribute('based-on')
                    try:
                        values = list(storage._hidden[basename][manager])
                    except KeyError:
                        pass
                    for value in values:
                        if value not in values:
                            viewletnode = self._doc.createElement('viewlet')
                            viewletnode.setAttribute('name', value)
                            if values.index(value) == 0:
                                viewletnode.setAttribute('insert-before', '*')
                            else:
                                pos = values[values.index(value)-1]
                                viewletnode.setAttribute('insert-after', pos)
                            child.appendChild(viewletnode)
                    values = self._updateValues(values, child)
                    storage.setHidden(manager, skinname, tuple(values))

                if child.hasAttribute('make_default'):
                    make_default = self._convertToBoolean(
                                        child.getAttribute('make_default'))
                    if make_default == True:
                        storage.setDefault(manager, skinname)

    def _updateValues(self, values, node):
        for child in node.childNodes:
            if child.nodeName != 'viewlet':
                continue
            viewlet_name = child.getAttribute('name')
            if viewlet_name in values:
                values.remove(viewlet_name)

            if child.hasAttribute('insert-before'):
                insert_before = child.getAttribute('insert-before')
                if insert_before == '*':
                    values.insert(0, viewlet_name)
                    continue
                else:
                    try:
                        index = values.index(insert_before)
                        values.insert(index, viewlet_name)
                        continue
                    except ValueError:
                        pass
            elif child.hasAttribute('insert-after'):
                insert_after = child.getAttribute('insert-after')
                if insert_after == '*':
                    pass
                else:
                    try:
                        index = values.index(insert_after)
                        values.insert(index+1, viewlet_name)
                        continue
                    except ValueError:
                        pass

            if not child.hasAttribute('remove'):
                values.append(viewlet_name)

        return values
