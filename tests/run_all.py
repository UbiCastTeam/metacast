#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import unittest
import imp

test_full = imp.load_source('test_full', 'test_full.py')
test_compat = imp.load_source('test_compat', 'test_compat.py')


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(test_full.TestFull())
    suite.addTest(test_compat.TestCompatibility())
    success = not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    sys.exit(success)
