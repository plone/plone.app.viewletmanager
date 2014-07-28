# -*- coding: utf-8 -*-
from plone.app.viewletmanager.testing import optionflags

import doctest
import unittest


doc_tests = [
    'storage.rst',
    'manager.rst',
]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite(
            'tests/{0}'.format(doc_file),
            package='plone.app.viewletmanager',
            optionflags=optionflags
        )
        for doc_file in doc_tests
    ])

    return suite
