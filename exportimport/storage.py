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
            values = []
            for value in child.childNodes:
                if value.nodeName == 'viewlet':
                    values.append(value.getAttribute('name'))
            if child.nodeName == 'order':
                storage.setOrder(manager, skinname, tuple(values))
            elif child.nodeName == 'hidden':
                storage.setHidden(manager, skinname, tuple(values))
