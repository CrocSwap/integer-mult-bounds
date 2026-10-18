"""c8: the cited scope result is present in this repository tree: research/complex-rank8-decoder-rigidity (PR #1212, merged) states Theorem 1.
This is a CITATION check (the text is there, pinned by sha256 in SOURCES.json); it does not re-prove Theorem 1.  Without the sibling directory: SKIP."""
import os, re, sys
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); f = os.path.join(os.path.dirname(PKG), 'complex-rank8-decoder-rigidity', 'PROOF.md')
if not os.path.isfile(f): print('SKIP c8  research/complex-rank8-decoder-rigidity not found next to this package'); sys.exit(0)
t = open(f, encoding='utf-8').read()
ok = '**Theorem 1 (rigidity).**' in t and 'rank at most 8' in t and 'D (2 G_L) D^{-1}' in t and 'no odd entry of K vanishes' in t
print(('PASS' if ok else 'FAIL') + ' c8  cited: #1212 PROOF.md states Theorem 1 (rank <= 8, K_ii = 4, K_ij = 0 on orthogonal pairs  =>  K = D (2G) D^-1) for P112')
sys.exit(0 if ok else 1)
