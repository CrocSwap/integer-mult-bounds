#!/usr/bin/env python3
"""Exhaust the complete two-call Q8 alphabet and save its exact receipt."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('q8_core',PACKAGE/'core.py')
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
def main():
    core.load_pins()
    one=core.enumerate_one_call()
    receipt=core.enumerate_two_call()
    core.need(one['alphabet_words']==28*7 and one['target_hits']==0,
              'complete one-call exclusion')
    core.need(receipt['alphabet_words']==28*28*7*7,'complete alphabet count')
    core.need(receipt['target_hits']==0,'unexpected two-call target word')
    direct=core.direct_three()
    core.need(direct==core.target(),'direct three-call positive control')
    out={'schema_version':1,'seed':core.SEED,'track':'bit-mechanisms','task_id':'bit-new-register-model',
         'priority_revision':4,'base_commit':'0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2',
         'selected_record_sha256':'10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32',
         'target':'diag([i],[j],[k])','direct_positive_control_calls':3,
         'one_call_domain':one,
         'two_call_domain':receipt,'direct_output_bytes':list(direct)}
    (PACKAGE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS_Q8_TWO_CALL_EXCLUSION',f"words={receipt['alphabet_words']}",
          f"hits={receipt['target_hits']}",f"min_hamming={receipt['minimum_coefficient_hamming_distance']}",
          f"one_call_hits={one['target_hits']}",f"direct_calls=3",
          f"sha256={receipt['ordered_word_output_sha256']}")
if __name__=='__main__': main()
