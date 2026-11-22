#!/usr/bin/env python3
"""Retain earlier public/stock controls and test the last profile's feasible product."""
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from upstream import install
install()
from calibration import FIXED_STOCK, SMALL_GAP, NEAR_RAW, LAST_TICK
from check_product import physical_product, stock_and_public
for profile in (FIXED_STOCK, SMALL_GAP, NEAR_RAW):
    stock_and_public(profile)
row=physical_product(LAST_TICK)
assert row['product']=='-345550037539' and row['shuttles']==138
assert row['H_calls']==157248 and row['stage_body_records']==81**2
print(json.dumps(row,sort_keys=True),flush=True)
print('PASS_LAST_TICK_AND_RETAINED_STOCK_CONTROLS',flush=True)
