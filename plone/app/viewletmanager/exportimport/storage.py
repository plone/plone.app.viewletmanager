from persistent.dict import PersistentDict
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
        for nodename in ('order', 'hidden'):
            skins = getattr(storage, '_'+nodename)
            for skin in skins:
                for name in skins[skin]:
                    node = self._doc.createElement(nodename)
                    node.setAttribute('skinname', skin)
                    node.setAttribute('manager', name)
                    for viewlet in skins[skin][name]:
                        child = self._doc.createElement('viewlet')
                        child.setAttribute('name', viewlet)
                        node.appendChild(child)
                    output.appendChild(node)
        return output

    def _importNode(self, node):
        """
        Import the object from the DOM node.
        """
        storage = self.context
        purge = self.environ.shouldPurge()
        if node.getAttribute('purge'):
            purge = self._convertToBoolean(node.getAttribute('purge'))
        if purge:
            self._purgeDicts()
        for child in node.childNodes:
            nodename = child.nodeName
            if nodename not in ('order', 'hidden'):
                continue
            purgeChild = False
            if child.getAttribute('purge'):
                purgeChild = self._convertToBoolean(
                                                  child.getAttribute('purge'))
            skinname = child.getAttribute('skinname')
            manager = child.getAttribute('manager')
            skins = getattr(storage, '_'+nodename)
            if skinname == '*':
                for skinname in skins:
                    values = []
                    if not purgeChild:
                        try:
                            values = list(skins[skinname][manager])
                        except KeyError:
                            pass
                    values = self._updateValues(values, child)
                    if nodename == 'order':
                        storage.setOrder(manager, skinname, tuple(values))
                    elif nodename == 'hidden':
                        storage.setHidden(manager, skinname, tuple(values))

            else:
                values = []
                if not purgeChild:
                    basename = skinname
                    if child.hasAttribute('based-on'):
                        basename = child.getAttribute('based-on')
                    try:
                        values = list(skins[basename][manager])
                    except KeyError:
                        pass
                    if skinname in skins and child.hasAttribute('based-on'):
                        try:
                            oldvalues = list(skins[skinname][manager])
                        except KeyError:
                            pass
                        for value in oldvalues:
                            if value not in values:
                                viewlet = self._doc.createElement('viewlet')
                                viewlet.setAttribute('name', value)
                                if oldvalues.index(value) == 0:
                                    viewlet.setAttribute('insert-before', '*')
                                else:
                                    pos = oldvalues[oldvalues.index(value)-1]
                                    viewlet.setAttribute('insert-after', pos)
                                child.appendChild(viewlet)
                values = self._updateValues(values, child)
                if nodename == 'order':
                    storage.setOrder(manager, skinname, tuple(values))
                elif nodename == 'hidden':
                    storage.setHidden(manager, skinname, tuple(values))

                if child.hasAttribute('make_default'):
                    make_default = self._convertToBoolean(
                                        child.getAttribute('make_default'))
                    if make_default == True:
                        storage.setDefault(manager, skinname)

    def _purgeDicts(self):
        storage = self.context
        for key in storage._order:
            storage._order[key].clear()
        for key in storage._hidden:
            storage._hidden[key].clear()

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
        