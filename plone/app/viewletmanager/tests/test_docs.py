from plone.app.viewletmanager.testing import optionflags

import doctest
import re
import six
import unittest


doc_tests = [
    'storage.rst',
    'manager.rst',
]


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        want = re.sub("u'(.*?)'", "'\\1'", want)
        got = re.sub(
            'zope.interface.interfaces.ComponentLookupError',
            'ComponentLookupError',
            got,
        )
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite(
            f'tests/{doc_file}',
            package='plone.app.viewletmanager',
            optionflags=optionflags,
            checker=Py23DocChecker(),
        )
        for doc_file in doc_tests
    ])

    return suite
