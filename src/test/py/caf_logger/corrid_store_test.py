from caf_logger.mdal import corrid_store
import unittest
import os
import importlib
import sys

class TestShell(unittest.TestCase):
    def setUp(self):
        importlib.reload(corrid_store)

    def test_corrid_store_init_header(self):
        self.assertEqual(corrid_store.get_corr_id(), "")

        corrid_store.init_headers()
        self.assertNotEqual(corrid_store.get_corr_id(), "")

    def test_corrid_store_set_headers(self):
        self.assertEqual(corrid_store.get_corr_id(), "")

        corrid_store.set_headers(["corrid:corrid1,attr:attr1=2", "attr:attr2:1,attr:attr3"])
        self.assertEqual(corrid_store.get_corr_id(), "corrid1")

        global_attrs = corrid_store.get_attrs()
        self.assertTrue("attr1=2"in global_attrs)
        self.assertTrue("attr2:1"in global_attrs)
        self.assertTrue("attr3"in global_attrs)

        corrid_store.set_headers([])
        self.assertNotEqual(corrid_store.get_corr_id(), "corrid1")
        self.assertNotEqual(corrid_store.get_corr_id(), "")
        global_attrs = corrid_store.get_attrs()
        self.assertEqual(0, len(global_attrs))

    def test_corrid_store_get_headers(self):
        headers = corrid_store.get_headers()
        corr_id = corrid_store.get_corr_id()
        self.assertTrue("corrid:"+corr_id in headers)
        self.assertEqual(1, len(headers))

        corrid_store.set_headers(["corrid:corrid1,attr:attr1=2", "attr:attr2:1,attr:attr3"])
        headers = corrid_store.get_headers()
        self.assertTrue("corrid:corrid1" in headers)
        self.assertTrue("attr:attr1=2" in headers)
        self.assertTrue("attr:attr2:1" in headers)
        self.assertTrue("attr:attr3" in headers)
        
        self.assertEqual(4, len(headers))

if __name__ == '__main__':
    unittest.main()

