# -*- coding: utf-8 -*-
from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite

import zope.component.testing


def tearDown(test):
    zope.component.testing.tearDown(test)


def test_suite():
    from unittest import TestSuite
    suite = TestSuite()
    suite.addTests((
        DocFileSuite(
            'storage.rst',
            tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
        ),
        DocFileSuite(
            'manager.rst',
            tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
        ),
    ))
    return suite
