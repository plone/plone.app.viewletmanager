Introduction
============

by Florian Schulze <fschulze@jarn.com>.

This component expects you to register storage.ViewletSettingsStorage as a
local utility providing IViewletSettingsStorage (CMFPlone does this). The
viewlet manager in manager.OrderedViewletManager can then get the filter and
order settings. These settings can be configured by 3rd party products and
TTW to customize the viewlets per skin.
