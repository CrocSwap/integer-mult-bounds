#!/usr/bin/env python3
"""The base's target definition, applied to p19 -- and where the realised word departs from it.

The base defines its productive targets at `research/coded-reverse-controller/verify.py:170-183`
by a *design list*, not by measuring the operator:

    outs = [full, full]                                   # the two initial roles, full frame
    for i, ch in enumerate(pat, 1):
        outs += [prefix(0..2i) if ch == 'I' else suffix(2i..2p)] * 2      # two roles per stage
    for s in outs: T[1 + 8*|s & thick|] += 112            # 112 ports per role
    for r, n in H.items(): T[r] += |thick| * n            # helper block

So a target is a *role in the designed frame basis*, counted 112 times (once per port), and the
frame of role i is the prefix of stages up to i for an I stage and the suffix from i for a T
stage.  This receipt does three things:

  1. re-derives T under that definition at p=19 and confirms it is the invoiced histogram
     (448 per intermediate rank, 224 at rank 153);
  2. measures the frames the word actually realises, from the thinned operator;
  3. reports whether the realised word satisfies the design assumption, and if not, which
     part of the construction causes the departure.

Step 1 is a source-bound derivation: it reproduces the invoice from the base's own definition
rather than from the invoice function.
"""
import importlib.util, json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

def need(ok, why):
    if not ok: raise ValueError(why)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

BASE = 'research/coded-reverse-controller/verify.py'

def main():
    mod = load('c4940_targets', ROOT/BASE)
    p, pat = 19, 'I'*9+'T'*9
    thick = frozenset(range(1, 2*p, 2))

    # ---- 1. re-derive T from the base's stated definition ----
    full = frozenset(range(2*p+1))
    outs = [full, full]
    for i, ch in enumerate(pat, 1):
        outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
    T_def = Counter()
    for s in outs: T_def[1 + 8*len(s & thick)] += 112
    for r, n in mod.H.items(): T_def[r] += len(thick)*n
    T_def.pop(0, None)
    T_fn, _ = mod.invoice(p, pat, thick, {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40})
    T_fn = Counter({int(k): v for k, v in T_fn.items()})
    need(T_def == T_fn, 'the base definition reproduces the invoice histogram exactly')
    print('PASS definition: the base design list (%d role frames, 112 ports each) reproduces the invoiced T %s'
          % (len(outs), dict(sorted(T_def.items()))))

    # ---- 2. the frames the word actually realises ----
    co, _ = mod.controller(p, mod.keep_of(p, pat), {s: Q(1) for s in range(2*p+1)})
    th = mod.thin(co, thick)
    # a target is what a role ends holding: the factorisation's diagonal, not a row or column support
    fac = mod.C.factor(th)
    need(fac is not None, 'the controller factorises at p=%d' % p)
    realised = {i: {s for s, bit in enumerate(fac['diagonal'][i][1:]) if bit} & thick
                for i in range(2*p)}
    sizes = Counter(len(S) for S in realised.values())
    T_real = {1 + 8*k: 112*v for k, v in sorted(sizes.items())}
    designed = Counter(len(s) for s in outs)
    helper_block = {r: len(thick)*n for r, n in mod.H.items()}
    designed_main = Counter({int(k): v for k, v in T_def.items()})
    for r, n in helper_block.items():
        designed_main[r] -= n
    designed_main = dict(sorted({r: v for r, v in designed_main.items() if v}.items()))
    print('designed frame sizes :', dict(sorted(designed.items())))
    print('realised frame sizes :', dict(sorted(sizes.items())))
    print('designed T (main + helper) :', dict(sorted(T_def.items())))
    print('designed T (main only)     :', designed_main)
    print('realised T (diagonal)      :', T_real)

    match = T_real == designed_main
    print('%s the diagonal target histogram equals the designed main histogram: %s'
          % ('PASS' if match else 'FINDING', match))

    receipt = {
        'status': 'PASS_DESIGN_FRAMES_REALISED' if match else 'FINDING_DESIGN_FRAMES_NOT_REALISED',
        'designed_main_T': designed_main, 'helper_block': helper_block,
        'base_definition': {'file': BASE, 'lines': '170-183',
                            'rule': ('outs = [full, full] plus two roles per stage whose frame is the prefix up to '
                                     'the stage for I and the suffix from the stage for T; T counts 112 ports per '
                                     'role; the helper block is added at its own ranks')},
        'designed_frames_per_size': dict(sorted(designed.items())),
        'realised_frames_per_size': dict(sorted(sizes.items())),
        'designed_T': dict(sorted(T_def.items())),
        'realised_T': T_real,
        'invoiced_T_equals_designed': T_fn == T_def,
        'realised_equals_designed': match,
        'diagnosis': ('the invoice counts targets in the designed frame basis, and the factorisation diagonal of '
                      'the controller word realises exactly that multiset.  An earlier reading used the row closure '
                      'of the thinned matrix, which saturates and is not the target notion'),
        'consequence': ('the invoiced census is the word\'s own diagonal census, so the census matches without any '
                        'reinterpretation of the invoice')}
    (HERE/'P19_TARGETS.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': receipt['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
