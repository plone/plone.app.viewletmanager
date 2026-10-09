Introduction
============

by Florian Schulze <fschulze@jarn.com>.

This component expects you to register storage.ViewletSettingsStorage as a
local utility providing IViewletSettingsStorage (CMFPlone does this). The
viewlet manager in manager.OrderedViewletManager can then get the filter and
order settings. These settings can be configured by 3rd party products and
TTW to customize the viewlets per skin.

Additional viewlets
===================

A manager renders more than the viewlets registered for it. Subscription
adapters for ``(context, request, view, manager)`` providing
``interfaces.IAdditionalViewlets`` contribute ``(name, viewlet)`` pairs through
their ``viewlets()`` method. This lets an add-on decide at runtime which
manager shows a viewlet, for example from configuration stored in the
database. Contributed viewlets are ordered, hidden and managed like registered
ones. A registered viewlet wins over a contributed one of the same name.
