#!/usr/bin/env python3
"""Native chart-change maps of the word: every distinct (initial, final) frame pair of a MOVE or of a helper is lowered to a native Clifford recipe and compared, as an exact signed map with global phase, with the expected map (native.py, unchanged from the #6833 package, with retained/native/native_verify.py).
usage: native_maps.py WORD.json.gz     (prints the counts; ends PASS_NATIVE_MAPS). native.py counts the 192 second-plane mains with the helpers, as it does for every word of this line: normalizers = 2 * (public - 208)."""
import gzip, json, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import native as N
w = json.load(gzip.open(sys.argv[1], 'rt')); r = N.native(w)
print({k: r[k] for k in ('distinct_maps', 'main_adapters', 'helper_normalizers', 'helpers', 'wrong_phase_rejected')})
assert r['wrong_phase_rejected'] and r['main_adapters'] == 208 and r['distinct_maps'] == 3185 and r['helper_normalizers'] == 2 * sum(r['helpers'].values()) == 2 * (w['public'] - 208)
print('PASS_NATIVE_MAPS')
