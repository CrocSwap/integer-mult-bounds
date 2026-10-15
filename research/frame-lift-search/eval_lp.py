"""LP optimum of the frame assignment for an arbitrary word (e.g. a reordered word from order_to_word.py).
usage: eval_lp.py WORD.json.gz"""
import gzip, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import frame_lift as L
from frame_exact import interval
from check import chain_terms, chain_weight, lp_bound

word = json.load(gzip.open(sys.argv[1]))
ch, G, orig, lo = chain_terms(word)
dom = [interval(l, g) for l, g in zip(lo, G)]
bound, nv, nr = lp_bound(ch, dom)
print('input chain weight %.6f  LP optimum %.6f' % (chain_weight(ch, orig), bound))
