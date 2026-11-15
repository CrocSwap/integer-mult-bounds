#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One-command validation of an edited P104 native word against its base (our NETCAUX validate wrapper, made
self-contained).  Standard library only.

Steps (each PASS/FAIL, summary table at the end; exit 0 iff every step passed):
  1 accx      accx.py BASE NEW (randomised-exact replay with exact re-checks, legality, owned rules, pricekit kappa)
  2 lossless  lossless.py law DUAL on NEW: no CLEAR destroys information
  3 official  when run inside an integer-mult-bounds checkout: the repository's own invoice tools
              scripts/compare_recursive_invoices.py (BASE invoice -> NEW invoice) and
              scripts/evaluate_recursive_power.py (NEW vs the empty invoice at r^(1-C)) at C just below and just above
              NEW's certified kappa enclosure; requires new_cost_lower below and new_cost_higher above.
              Skipped (not failed) outside a checkout.
usage: python3 validate.py BASE NEW [--caller CALLER.json[.gz]] [--allow-owned-reframe] [--repo ROOT]
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import accx  # noqa: E402
import lossless  # noqa: E402
import pricekit as pk  # noqa: E402


def invoice_json(inv, boundary='complete signed #7113 caller application with 17 native calls'):
    def num(v):
        v = Fraction(v)
        return int(v) if v.denominator == 1 else str(v)
    return {'schema': 'integer-mult-recursive-invoice/v1',
            'contract': {'model': 'mixed-target-unnormalized-power-v1',
                         'rank_semantics': 'H_r costs r^(1-C); debit surrendered productive fields',
                         'ambient_rank': 145, 'boundary': boundary},
            'paid': {str(k): num(inv['P'][k]) for k in sorted(inv['P']) if inv['P'][k]},
            'targets': {str(k): num(inv['T'][k]) for k in sorted(inv['T']) if inv['T'][k]}}


def official(root, caller, B, W, kappa, out=print):
    root = Path(root)
    if not (root / 'scripts' / 'compare_recursive_invoices.py').exists():
        return None, 'skipped (no repository checkout at %s)' % root
    C = pk.load(caller); ci = pk.caller_invoice(C)
    invB = pk.invoice(ci, pk.native_from_word(B)); invW = pk.invoice(ci, pk.native_from_word(W))
    with tempfile.TemporaryDirectory() as d:
        pb, pw, pz = (Path(d) / x for x in ('base.json', 'new.json', 'zero.json'))
        pb.write_text(json.dumps(invoice_json(invB))); pw.write_text(json.dumps(invoice_json(invW)))
        pz.write_text(json.dumps(invoice_json(dict(T={}, P={}))))

        def tool(name, *args):
            p = subprocess.run([sys.executable, '-I', '-B', str(root / 'scripts' / name), *map(str, args)],
                               capture_output=True, text=True, timeout=300, cwd=root)
            if p.returncode:
                raise RuntimeError('%s failed: %s' % (name, (p.stderr or p.stdout)[-400:]))
            return json.loads(p.stdout)
        rep = tool('compare_recursive_invoices.py', pb, pw)
        out('  compare_recursive_invoices base -> new: %s, paid delta %s, target delta %s'
            % (rep['classification'], rep.get('delta_paid'), rep.get('delta_targets')))
        lo = Decimal(str(kappa['lo'])[:15]); hi = lo + Decimal('1e-13')
        res = {}
        for c in (lo, hi):
            r = tool('evaluate_recursive_power.py', pz, pw, '--exponent', str(1 - c), '--bits', 256)
            res[c] = r['classification']
            out('  evaluate_recursive_power at C = %s: %s' % (c, r['classification']))
    good = res[lo] == 'new_cost_lower' and res[hi] == 'new_cost_higher'
    return good, 'compare: %s; crossing in (%s, %s)' % (rep['classification'], lo, hi)


def main(argv):
    args = list(argv); caller = accx.DEFAULT_CALLER; reframe = False; root = HERE.parents[1]
    if '--allow-owned-reframe' in args:
        args.remove('--allow-owned-reframe'); reframe = True
    for flag in ('--caller', '--repo'):
        if flag in args:
            i = args.index(flag); val = args[i + 1]; del args[i:i + 2]
            if flag == '--caller':
                caller = val
            else:
                root = Path(val)
    if len(args) != 2:
        print(__doc__); return 2
    B = pk.load(args[0]); W = pk.load(args[1]); rows = []
    t = time.time()
    try:
        r = accx.check(B, W, caller, reframe); rows.append(('accx', True, '%.1fs' % (time.time() - t), 'ALL CHECKS PASS'))
    except accx.Fail as ex:
        rows.append(('accx', False, '%.1fs' % (time.time() - t), str(ex))); r = None
    t = time.time(); loss = lossless.dual_scan(W)[0]
    rows.append(('lossless', not loss, '%.1fs' % (time.time() - t), '%d lossy CLEARs' % len(loss)))
    if r is not None:
        t = time.time()
        try:
            good, note = official(root, caller, B, W, r['kappa_new'])
        except Exception as ex:   # a tool error is a failure, not a skip
            good, note = False, str(ex)
        if good is not None:
            rows.append(('official', good, '%.1fs' % (time.time() - t), note))
        else:
            print('  official tools ' + note)
    print('\n=== validate summary for %s' % args[1])
    for name, good, dt, note in rows:
        print('  %-10s %-5s %8s  %s' % (name, 'PASS' if good else 'FAIL', dt, note))
    allok = all(x[1] for x in rows)
    print('  OVERALL', 'PASS' if allok else 'FAIL')
    return 0 if allok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
