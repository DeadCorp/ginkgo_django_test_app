"""
Tests for `parse_sku` utility.
Run:
     python3 -m unittest product.tests.ParseSkuTests
"""

from unittest import TestCase

import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'final.settings')

django.setup()

from product.utils import parse_sku

"""
C_SC_155349
C_SC_155349-A
C_SC_155349$2
C_SC_155349-A$2
C_BB_1013663254#13663254
C_BB_1016846112#16846112-A
C_BB_1012538278#12538278$2
C_BB_1012538278#12538278-A$2
C_SC_prod16660140#354309
A_KM_04648893000P#022V006624735000
A_KM_04648893000P#022V006624735000-A
A_KM_04648893000P#022V006624735000$2
A_KM_04648893000P#022V006624735000-A$2
A_KM_A034049181#SPM14591928110
A_KM_A034049181#SPM14591928110-A
A_KM_A034049181#SPM14591928110$2
A_KM_A034049181#SPM14591928110-A$2
TEST SKU FAIL
C_BB_1013663254#136+63+A254
C_BB_1013663254#8.641+035.0
C_BB_1013663254#1156/1157
ANOTHER_TEST_SKU#FAIL
"""


class ParseSkuTests(TestCase):
    def test_01(self):
        sku = 'C_SC_155349'
        data = parse_sku(sku)
        check = {
            'market': 'C',
            'supplier': 'SC',
            'id': '155349',
            'option': '',
            'letter': None,
            'quantity': 1
        }
        self.assertEqual(data, check)

    def test_02(self):
        sku = 'C_SC_155349-A'
        data = parse_sku(sku)
        check = {
            'market': 'C',
            'supplier': 'SC',
            'id': '155349',
            'option': '',
            'letter': 'A',
            'quantity': 1
        }
        self.assertEqual(data, check)

    def test_03(self):
        sku = 'C_SC_155349$2'
        data = parse_sku(sku)
        check = {
            'market': 'C',
            'supplier': 'SC',
             'id': '155349',
            'option': '',
            'letter': None,
            'quantity': 2
        }
        self.assertEqual(data, check)

    def test_04(self):
        sku = 'C_SC_155349-A$2'
        data = parse_sku(sku)
        check = {
            'market': 'C',
            'supplier': 'SC',
            'id': '155349',
            'option': '',
            'letter': 'A',
            'quantity': 2
        }
        self.assertEqual(data, check)

    def test_05(self):
        sku = 'C_BB_1013663254#13663254'
        data = parse_sku(sku)
        check = {
            'market': 'C',
            'supplier': 'BB',
            'id': '1013663254',
            'option': '13663254',
            'letter': None,
            'quantity': 1
        }
        self.assertEqual(data, check)

    def test_06(self):
        sku = 'C_BB_1016846112#16846112-A'
        data = parse_sku(sku)
        check = {
            'market': 'C',
            'supplier': 'BB',
            'id': '1016846112',
            'option': '16846112',
            'letter': 'A',
            'quantity': 1
        }
        self.assertEqual(data, check)

    def test_07(self):
        sku = 'C_BB_1012538278#12538278$2'
        data = parse_sku(sku)
        check = {
            'market': 'C',
            'supplier': 'BB',
            'id': '1012538278',
            'option': '12538278',
            'letter': None,
            'quantity': 2
        }
        self.assertEqual(data, check)

    def test_08(self):
        sku = 'C_BB_1012538278#12538278-A$2'
        data = parse_sku(sku)
        check = {
            'market': 'C',
            'supplier': 'BB',
            'id': '1012538278',
            'option': '12538278',
            'letter': 'A',
            'quantity': 2
        }
        self.assertEqual(data, check)

    def test_09(self):
        sku = 'C_SC_prod16660140#354309'
        data = parse_sku(sku)
        check = {
            'market': 'C',
            'supplier': 'SC',
            'id': 'prod16660140',
            'option': '354309',
            'letter': None,
            'quantity': 1
        }
        self.assertEqual(data, check)

    def test_10(self):
        sku = 'A_KM_04648893000P#022V006624735000'
        data = parse_sku(sku)
        check = {
            'market': 'A',
            'supplier': 'KM',
            'id': '04648893000P',
            'option': '022V006624735000',
            'letter': None,
            'quantity': 1
        }
        self.assertEqual(data, check)

    def test_11(self):
        sku = 'A_KM_04648893000P#022V006624735000-A'
        data = parse_sku(sku)
        check = {
            'market': 'A',
            'supplier': 'KM',
            'id': '04648893000P',
            'option': '022V006624735000',
            'letter': 'A',
            'quantity': 1
        }
        self.assertEqual(data, check)

    def test_12(self):
        sku = 'A_KM_04648893000P#022V006624735000$2'
        data = parse_sku(sku)
        check = {
            'market': 'A',
            'supplier': 'KM',
            'id': '04648893000P',
            'option': '022V006624735000',
            'letter': None,
            'quantity': 2
        }
        self.assertEqual(data, check)

    def test_13(self):
        sku = 'A_KM_04648893000P#022V006624735000-A$2'
        data = parse_sku(sku)
        check = {
            'market': 'A',
            'supplier': 'KM',
            'id': '04648893000P',
            'option': '022V006624735000',
            'letter': 'A',
            'quantity': 2
        }
        self.assertEqual(data, check)

    def test_14(self):
        sku = 'A_KM_A034049181#SPM14591928110'
        data = parse_sku(sku)
        check = {
            'market': 'A',
            'supplier': 'KM',
            'id': 'A034049181',
            'option': 'SPM14591928110',
            'letter': None,
            'quantity': 1
        }
        self.assertEqual(data, check)

    def test_15(self):
        sku = 'A_KM_A034049181#SPM14591928110-A'
        data = parse_sku(sku)
        check = {
            'market': 'A',
            'supplier': 'KM',
            'id': 'A034049181',
            'option': 'SPM14591928110',
            'letter': 'A',
            'quantity': 1
        }
        self.assertEqual(data, check)

    def test_16(self):
        sku = 'A_KM_A034049181#SPM14591928110$2'
        data = parse_sku(sku)
        check = {
            'market': 'A',
            'supplier': 'KM',
            'id': 'A034049181',
            'option': 'SPM14591928110',
            'letter': None,
            'quantity': 2
        }
        self.assertEqual(data, check)

    def test_17(self):
        sku = 'A_KM_A034049181#SPM14591928110-A$2'
        data = parse_sku(sku)
        check = {
            'market': 'A',
            'supplier': 'KM',
            'id': 'A034049181',
            'option': 'SPM14591928110',
            'letter': 'A',
            'quantity': 2
        }
        self.assertEqual(data, check)

    def test_18(self):
        sku = 'TEST SKU FAIL'

        def data():
            parse_sku(sku)

        self.assertRaises(Exception, data)

    def test_19(self):
        sku = 'C_BB_1013+S663254#136+63+A254-A$2'

        data = parse_sku(sku)
        check = {
            'market': 'C',
            'supplier': 'BB',
            'id': '1013+S663254',
            'option': '136+63+A254',
            'letter': 'A',
            'quantity': 2
        }
        self.assertEqual(data, check)

    def test_20(self):
        sku = 'C_BB_1013663254#8.641+035.0'

        data = parse_sku(sku)
        check = {
            'market': 'C',
            'supplier': 'BB',
            'id': '1013663254',
            'option': '8.641+035.0',
            'letter': None,
            'quantity': 1
        }
        self.assertEqual(data, check)

    def test_21(self):
        sku = 'C_BB_1013663254#1156/1157-A'

        data = parse_sku(sku)
        check = {
            'market': 'C',
            'supplier': 'BB',
            'id': '1013663254',
            'option': '1156/1157',
            'letter': 'A',
            'quantity': 1
        }
        self.assertEqual(data, check)

    def test_22(self):
        sku = 'ANOTHER_TEST_SKU#FAIL'

        def data():
            parse_sku(sku)

        self.assertRaises(Exception, data)

    def test_23(self):
        sku = 'a_as_#144124'

        def data():
            parse_sku(sku)
        self.assertRaises(Exception, data)

