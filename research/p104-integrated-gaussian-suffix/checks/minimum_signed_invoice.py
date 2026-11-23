"""Prove the least complete recurring log2 invoice for the installed reported gain."""
from fractions import Fraction as Q
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
import json,runpy

with redirect_stdout(StringIO()):
    proof=runpy.run_path(str(Path(__file__).with_name('all_stage_caps.py')))
K=Q('.003898222531555482')
ordinary_debit=Q(11204,8192)
gaussian_debit=Q(125645,1048576)
candidate_clock=318291611
worst=proof['compute'](candidate_clock-1,ordinary_debit,gaussian_debit,K)
G,S=worst['minimum_G_to_beat_3_stage'],worst['ordinary_budget_above_this_G']
ranks,ordinary=proof['cubic_bound'](S,ordinary_debit)
assert G==491002 and S==657091 and ranks==(8192,124611,524288)
assert ordinary<K+proof['stop']
assert proof['GAUSSIAN_C']-gaussian_debit/(G-1)<K+proof['stop']
print(json.dumps({'installed_kappa':str(K),'minimum_integer_log2_C':candidate_clock,'resource_model':'declared source tariff, 1–7 terminal heights from 8192 to 524288 and identical fixed prices',
                  'ordinary_raw_shortfall_at_previous_clock':str(K+proof['stop']-ordinary),'preceding':worst},indent=2))
