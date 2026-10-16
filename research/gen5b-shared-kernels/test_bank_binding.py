"""Regression controls for stock units and replica/stage factors."""
import copy
import json
from pathlib import Path
import unittest
import bank_binding


class StockBindingTests(unittest.TestCase):
    def pair(self, case='kernel70'):
        root=Path(__file__).resolve().parent/'certificates'/case
        return [json.loads((root/(name+'.json')).read_text()) for name in ('banks','pricing')]
    def test_both_cases(self):
        for case in ('kernel70','kernel72'):
            bank_binding.check(*self.pair(case))
    def test_half_normalized_stock_rejected(self):
        b,p=self.pair();b['unreplicated_stock']='30739/3'
        with self.assertRaises(AssertionError):bank_binding.check(b,p)
    def test_literal_stock_rejected(self):
        b,p=self.pair();b['literal_stock']+=1
        with self.assertRaises(AssertionError):bank_binding.check(b,p)
    def test_stage_factor_rejected(self):
        b,p=self.pair();b['total_banks']//=5
        with self.assertRaises(AssertionError):bank_binding.check(b,p)
    def test_replica_factor_rejected(self):
        b,p=self.pair();b['checked_role_replica_assignments_per_stage']//=60
        with self.assertRaises(AssertionError):bank_binding.check(b,p)
    def test_inventory_demand_rejected(self):
        b,p=self.pair();p['packing']['demand']['23']+=1
        with self.assertRaises(AssertionError):bank_binding.check(b,p)
    def test_paid_rank_mass_rejected(self):
        b,p=self.pair();p['rank_mass']+=1
        with self.assertRaises(AssertionError):bank_binding.check(b,p)
    def test_explicit_wrong_factors_rejected(self):
        with self.assertRaises(AssertionError):bank_binding.check(*self.pair(),replicas=30)

if __name__=='__main__':unittest.main()
