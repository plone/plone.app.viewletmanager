from zope.interface import implements

from persistent import Persistent
from persistent.dict import PersistentDict

from plone.app.viewletmanager.interfaces import IViewletSettingsStorage

DEFAULT_SKINKEY = 'default_skin'
DEFAULT_SKINNAME = 'Plone Default'

class ViewletSettingsStorage(Persistent):
    implements(IViewletSettingsStorage)

    def __init__(self):
        self._order = PersistentDict()
        self._hidden = PersistentDict()

    def getOrder(self, name, skinname):
        skin = self._order.get(skinname, {})
        order = skin.get(name, ())
        if not order:
            skin = self._order.get(DEFAULT_SKINKEY, {})
            order = skin.get(name, ())
        if not order:
            skin = self._order.get(DEFAULT_SKINNAME, {})
            order = skin.get(name, ())
        return order

    def setDefaultOrder(self, name, order):
        self.setOrder(name, DEFAULT_SKINKEY, order)

    def setOrder(self, name, skinname, order):
        skin = self._order.setdefault(skinname, PersistentDict())
        skin[name] = tuple(order)
        if not self.getOrder(name, DEFAULT_SKINKEY):
            self.setDefaultOrder(name, order)

    def getHidden(self, name, skinname):
        skin = self._hidden.get(skinname, {})
        order = skin.get(name, ())
        if not order:
            skin = self._hidden.get(DEFAULT_SKINKEY, {})
            order = skin.get(name, ())
        if not order:
            skin = self._hidden.get(DEFAULT_SKINNAME, {})
            order = skin.get(name, ())
        return order

    def setDefaultHidden(self, name, hidden):
        self.setHidden(name, DEFAULT_SKINKEY, hidden)

    def setHidden(self, name, skinname, hidden):
        skin = self._hidden.setdefault(skinname, PersistentDict())
        skin[name] = tuple(hidden)
