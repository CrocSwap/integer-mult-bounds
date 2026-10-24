#!/usr/bin/env python3
"""Settle the target-frame definition: row frames versus column closure.

The invoice builds its target histogram from a frame convention:

    two full outputs (the initial pair);
    for each stage i, two roles whose frame is the prefix up to i when the pattern is I
    and the suffix from i when it is T;
    rank = 1 + 8 * |frame intersect the retained stages|;
    role multiplicity 112.

The controller word has two candidate quantities that could correspond to it:

    row frame      -- the retained stages appearing in a role's OWN output content;
    column closure -- the retained stages that can reach a role from anywhere in the word.

After the reversed bridge sweep almost every role is reachable from everything, so the
column closure is expected to be much wider and is not a target notion.  This receipt
measures both against the invoice exactly, per rank, with call totals and rank mass, and
states which one the invoice uses.  It does not price anything.
"""
import importlib.util, json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import p19_word as W

def need(ok, why):
    if not ok: raise ValueError(why)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def main():
    mod = load('c4940_rowframe', ROOT/'research/coded-reverse-controller/verify.py')
    p, pat = 19, 'I'*9+'T'*9
    thick = frozenset(range(1, 2*p, 2))
    co, _ = mod.controller(p, mod.keep_of(p, pat), {s: Q(1) for s in range(2*p+1)})
    th = mod.thin(co, thick)

    rows = {i: set() for i in range(2*p)}
    cols = {j: set() for j in range(2*p)}
    for term, m in th.items():
        sel = {s for s, bit in enumerate(term[1:]) if bit}
        for i in range(2*p):
            if any(m[i][j] for j in range(2*p)): rows[i] |= sel
            for j in range(2*p):
                if m[i][j]: cols[j] |= sel
    def hist(sup):
        per_role = Counter(1 + 8*len(S & thick) for S in sup.values())
        return per_role, {r: 112*v for r, v in sorted(per_role.items())}
    rows_roles, row_T = hist(rows)
    cols_roles, col_T = hist(cols)

    T_raw, D_raw = W.invoice(p, pat, thick, {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40})
    T_total = Counter()
    for k, v in T_raw.items(): T_total[int(k)] += v
    helper = Counter({r: p*n for r, n in W.H.items()})
    invoiced_main = Counter(T_total)
    for r, n in helper.items(): invoiced_main[r] -= n
    invoiced_main = Counter({r: v for r, v in invoiced_main.items() if v})

    def mass(h): return sum(int(r)*v for r, v in h.items())
    def calls(h): return sum(h.values())
    diff_row = {r: row_T.get(r, 0) - invoiced_main.get(r, 0)
                for r in sorted(set(row_T) | set(invoiced_main))}
    diff_col = {r: col_T.get(r, 0) - invoiced_main.get(r, 0)
                for r in sorted(set(col_T) | set(invoiced_main))}

    print('row frames per rank   :', dict(sorted(rows_roles.items())))
    print('row-frame T           :', row_T)
    print('column-closure T      :', col_T)
    print('invoiced main T       :', dict(sorted(invoiced_main.items())))
    print()
    print('row  == invoiced      :', row_T == invoiced_main)
    print('col  == invoiced      :', col_T == invoiced_main)
    print('row  mass %d calls %d' % (mass(row_T), calls(row_T)))
    print('col  mass %d calls %d' % (mass(col_T), calls(col_T)))
    print('inv  mass %d calls %d' % (mass(invoiced_main), calls(invoiced_main)))
    print('row  diff by rank     :', diff_row)
    print('col  diff by rank     :', diff_col)

    receipt = {
        'status': 'PASS_ROW_FRAME_CENSUS' if row_T == invoiced_main else 'FINDING_ROW_FRAME_MISMATCH',
        'derived_row_T': row_T, 'derived_column_closure_T': col_T,
        'invoiced_main_T': dict(sorted(invoiced_main.items())),
        'invoiced_T_total': dict(sorted(T_total.items())),
        'row_equals_invoiced': row_T == invoiced_main,
        'column_closure_equals_invoiced': col_T == invoiced_main,
        'row_difference_by_rank': diff_row, 'column_difference_by_rank': diff_col,
        'mass': {'row': mass(row_T), 'column_closure': mass(col_T), 'invoiced': mass(invoiced_main)},
        'calls': {'row': calls(row_T), 'column_closure': calls(col_T), 'invoiced': calls(invoiced_main)},
        'frame_convention': ('invoice: two full outputs, prefix frame for each I stage, suffix frame for each T '
                             'stage, rank 1 + 8|frame intersect thick|, multiplicity 112'),
        'not_priced_here': 'the column closure is measured for contrast only and enters no price'}
    (HERE/'P19_ROWFRAME.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': receipt['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
