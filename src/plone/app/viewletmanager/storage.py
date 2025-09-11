from persistent import Persistent
from persistent.mapping import PersistentMapping
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from zope.interface import implementer


@implementer(IViewletSettingsStorage)
class ViewletSettingsStorage(Persistent):
    def __init__(self):
        self._order = PersistentMapping()
        self._hidden = PersistentMapping()
        self._defaults = PersistentMapping()

    def getOrder(self, name, skinname):
        skin = self._order.get(skinname, {})
        order = skin.get(name, ())
        if not order:
            skinname = self.getDefault(name)
            if skinname is not None:
                skin = self._order.get(skinname, {})
                order = skin.get(name, ())
        return order

    def setOrder(self, name, skinname, order):
        skin = self._order.setdefault(skinname, PersistentMapping())
        skin[name] = tuple(order)
        if self.getDefault(name) is None:
            self.setDefault(name, skinname)

    def getHidden(self, name, skinname):
        skin = self._hidden.get(skinname, {})
        hidden = skin.get(name, ())
        if not hidden:
            skinname = self.getDefault(name)
            if skinname is not None:
                skin = self._hidden.get(skinname, {})
                hidden = skin.get(name, ())
        return hidden

    def setHidden(self, name, skinname, hidden):
        skin = self._hidden.setdefault(skinname, PersistentMapping())
        skin[name] = tuple(hidden)

    def getDefault(self, name):
        try:
            return self._defaults.get(name)
        except AttributeError:  # Backward compatibility
            self._defaults = PersistentMapping()
            self.setDefault(name, "Plone Default")
            return self.getDefault(name)

    def setDefault(self, name, skinname):
        try:
            self._defaults[name] = skinname
        except AttributeError:  # Backward compatibility
            self._defaults = PersistentMapping()
            self.setDefault(name, skinname)
