from zope.interface import implements

from persistent import Persistent
from persistent.dict import PersistentDict

from plone.app.viewletmanager.interfaces import IViewletSettingsStorage


class ViewletSettingsStorage(Persistent):
    implements(IViewletSettingsStorage)

    def __init__(self):
        self._order = PersistentDict()
        self._hidden = PersistentDict()

    def getOrder(self, name, skinname):
        skin = self._order.get(skinname, {})
        return skin.get(name, ())

    def setOrder(self, name, skinname, order):
        skin = self._order.setdefault(skinname, PersistentDict())
        skin[name] = tuple(order)

    def getHidden(self, name, skinname):
        skin = self._hidden.get(skinname, {})
        return skin.get(name, ())

    def setHidden(self, name, skinname, hidden):
        skin = self._hidden.setdefault(skinname, PersistentDict())
        skin[name] = tuple(hidden)
