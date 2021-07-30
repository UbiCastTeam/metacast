#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
MetaCast - Compatibility test, import and export in older formats.
'''
from io import BytesIO
import os
import unittest

from metacast.io import load_xml, dump_xml, load_json, dump_json, load_js, dump_js


class TestCompatibility(unittest.TestCase):

    def test_full(self):
        base_path = os.path.dirname(__file__)
        tests = [
            (load_xml, dump_xml, ['sample_1.xml', 'sample_2.xml', 'sample_3.xml']),
            (load_json, dump_json, ['sample_1.json', 'sample_2.json', 'sample_3.json']),
            (load_js, dump_js, ['sample_1.js', 'sample_2.js', 'sample_3.js']),
        ]
        try:
            expected_type = unicode  # python 2 backward compatibility
        except NameError:
            expected_type = str
        for load_fct, dump_fct, files in tests:
            for name in files:
                path = os.path.join(base_path, name)
                with open(path, 'rb') as fileobj:
                    mc = load_fct(fileobj)
                buf = BytesIO()
                dump_fct(mc, buf)
                result = buf.getvalue()
                self.assertIsInstance(result.decode('utf-8'), expected_type)


if __name__ == '__main__':
    unittest.main()
