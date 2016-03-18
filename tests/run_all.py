#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import imp

test_full = imp.load_source('test_full', 'test_full.py')
test_compat = imp.load_source('test_compat', 'test_compat.py')

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(test_full.TestFull())
    suite.addTest(test_compat.TestCompatibility())
    unittest.TextTestRunner(verbosity=2).run(suite)
