Changelog
=========


2.0.11 (2018-01-30)
-------------------

Bug fixes:

- Add Python 2 / 3 compatibility [jensens]


2.0.10 (2016-08-10)
-------------------

Fixes:

- Use zope.interface decorator.
  [gforcada]

- Correctly log exception if viewlet rendering failed.
  [jensens]


2.0.9 (2015-09-07)
------------------

- Fix manage-viewlets for Plone 5
  [pbauer]

2.0.8 (2015-04-29)
------------------

- Rename ``_uncatched_errors`` to ``_exceptions_handled_elsewhere``
  [jean]


2.0.7 (2015-03-13)
------------------

- flake8 fixes and general cleanup.
  [gforcada]

- Sort skins and viewletmanagers on exports to create stable exports.
  This fixes: https://github.com/plone/plone.app.viewletmanager/issues/7
  [gforcada]


2.0.6 (2014-07-10)
------------------

- Use the ``!important`` directive for the ``.hide`` and ``.show`` CSS
  declarations on the ``@@manage-viewlets`` view. Twitter Bootstrap is using
  ``!important`` on these class names too, which made the viewlet management
  view unusable.
  [thet]


2.0.5 (2014-02-23)
------------------

- Do not catch conflict errors and keywordinterrupt in viewlet manager.
  We can programmatically setup the exceptions that are not caught.
  [thomasdesvenain]

- If render fails, be more verbose about the exception to know where and how it
  happens in the stack. [kiorky]

- refactor JS in template.
  [petschki]


2.0.4 (2013-08-13)
------------------

- Handle exception during viewlet rendering process: log the exception and
  display an error message. [toutpt]


2.0.3 (2012-12-15)
------------------

- Hiding viewlets for ``skinname="*"`` was not working properly.
  Closes http://dev.plone.org/plone/ticket/10903
  [garbas, WouterVH]

- Add ``plone.app.vocabularies`` as dependency to get the list of existing skins.
  [WouterVH]

- Add MANIFEST.in.
  [WouterVH]


2.0.2 - 2011-01-11
------------------

- Depend on ``Products.CMFPlone`` instead of ``Plone``.
  [elro]

- Explicitly unregister IViewletSettingsStorage utility to prevent test bleed.
  [esteele, cah190]


2.0.1 - 2010-07-18
------------------

- Update license to GPL version 2 only.
  [hannosch]


2.0 - 2010-07-15
----------------

- Silence `Nothing to import / export.` log messages.
  [hannosch]


2.0b5 - 2010-06-03
------------------

- Removed duplicated class statement in manage-viewlets.pt for compatibility
  with Chameleon.
  [pilz]

2.0b4 - 2010-05-01
------------------

- Implement IViewView so viewlets registered to this interface can be managed.
  [elro]

- Use Unicode up/down arrows in @@manage-viewlets.
  [esteele]


2.0b3 - 2010-03-03
------------------

- Provide some basic styling for @@manage-viewlets. Remove the use of
  .portletHeader and .portletItem styles and define everything inline.
  Closes http://dev.plone.org/plone/ticket/10006
  Closes http://dev.plone.org/plone/ticket/10178
  [esteele]

- Push @@manage-viewlets css into style_slot instead of css_slot.
  [esteele]


2.0b2 - 2010-02-17
------------------

- Updated manage-viewlets.pt to the recent markup conventions.
  References http://dev.plone.org/plone/ticket/9981
  [spliter]


2.0b1 - 2009-12-27
------------------

- Use the new zope.site package.
  [hannosch]


2.0a2 - 2009-12-16
------------------

- Protect forced Acquisition wrapping by an interface check on IAcquirer. This
  closes http://dev.plone.org/plone/ticket/9862.
  [hannosch]


2.0a1 - 2009-11-14
------------------

- Added translations for Show/Hide labels in @@manage-portlets view:
  label_show_item and label_hide_item. These msgids are shared with
  @@manage-viewlets view to show/hide viewlets. This closes
  http://dev.plone.org/plone/ticket/9733
  [naro]

- Use JS calls to handle show/hide/move actions instead of forcing a page
  reload. Will fall back to old method if JavaScript is not available.
  [esteele]


1.2.2 - 2009-03-07
------------------

- Specified package dependencies.
  [hannosch]

- Made the manager code more tolerant and not fail when no storage is found.
  [hannosch]

- Made the @@manage-viewlets screen use the 'managedPortlet' CSS class instead
  of 'portlet', so it's more usable with a custom theme.  This closes
  http://dev.plone.org/plone/ticket/8391.
  [davisagli]


1.2.1 - 2008-07-07
------------------

- Fixed bogus AttributeError masking the real ExpatError on syntax errors in
  viewlets.xml. (See test in r21161.)
  [davisagli]


1.2 - 2008-03-09
----------------

- Separated the base functionality and the parts necessary for TTW
  customization into two classes, so we can use this manager in the html
  head.
  [fschulze]

- Fix a syntax error in the export/import code
  [wichert]

- Add a HISTORY.txt file
  [wichert]


1.0 - 2007-08-16
----------------

- Initial release
