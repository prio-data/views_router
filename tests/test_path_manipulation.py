
import unittest
from views_data_router.paths import year_add,year_replace

class TestPathManipulation(unittest.TestCase):
    def test_year_add(self):
        base = lambda y: f"/trf/something/2009/base/priogrid_month.ged_best_ns/{y}/values"
        self.assertEqual(year_add(base(2010),1),base(2011))
        self.assertEqual(year_add(base(2010),-1),base(2009))
        self.assertEqual(year_replace(base(2010),1942),base(1942))
