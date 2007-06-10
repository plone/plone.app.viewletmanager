from zope.interface import implements

from persistent import Persistent
from persistent.dict import PersistentDict

from plone.app.viewletmanager.interfaces import IViewletSettingsStorage

DEFAULT_SKINNAME = 'default_skin'

class ViewletSettingsStorage(Persistent):
    implements(IViewletSettingsStorage)

    def __init__(self):
        self._order = PersistentDict()
        self._hidden = PersistentDict()

    def getOrder(self, name, skinname):
        skin = self._order.get(skinname, {})
        default_skin = self._order.get(DEFAULT_SKINNAME, {})
        return skin.get(name, ()) or default_skin.get(name, ())

    def setDefaultOrder(self, name, order):
        self.setOrder(name, DEFAULT_SKINNAME, order)

    def setOrder(self, name, skinname, order):
        skin = self._order.setdefault(skinname, PersistentDict())
        skin[name] = tuple(order)
        if not self.getOrder(name, DEFAULT_SKINNAME):
            self.setDefaultOrder(name, order)

    def getHidden(self, name, skinname):
        skin = self._hidden.get(skinname, {})
        default_skin = self._hidden.get(DEFAULT_SKINNAME, {})
        return skin.get(name, ()) or default_skin.get(name, ())

    def setDefaultHidden(self, name, hidden):
        self.setHidden(name, DEFAULT_SKINNAME, hidden)

    def setHidden(self, name, skinname, hidden):
        skin = self._hidden.setdefault(skinname, PersistentDict())
        skin[name] = tuple(hidden)
