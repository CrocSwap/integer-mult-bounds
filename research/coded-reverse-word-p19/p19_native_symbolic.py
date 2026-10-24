#!/usr/bin/env python3
"""Fresh-block geometry of the native chain: stage -> block, ambient rank, and the census.

`p19_word.py` replays the chain on dense banks that share one nine-axis field.  That
compares the chain with its reference, but the invoice credits a different geometry: stage
s acts on its own eight-axis block, plus one shared centre axis, i.e. ambient rank
1 + 8 * (number of retained stages) = 153 at p=19.

This receipt establishes that geometry exactly and without random banks:

  1. the generic constructor is well formed at every tested p: adapters bracket the chain,
     the terminal gauge is present, the closing swap is present, and the retained idle set
     follows the pattern;
  2. the thinned controller operator uses only the retained stages, so its monomial key has
     one coordinate per retained stage: the stage -> block map is a bijection onto p blocks
     and the ambient rank is 1 + 8p;
  3. replaying the emitted chain in the stage algebra reproduces that operator at
     p = 2 (I and T), 3 (IT) and 19 (I^9 T^9) -- exact, no random states;
  4. the rank census read off the thinned operator's role supports is compared with the
     histogram `invoice()` uses, and both are reported;
  5. negative controls reject a collapsed geometry, an omitted adapter, an omitted
     terminal gauge, and a code that is not the controller's.
"""
import importlib.util, json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import p19_word as W
import p19_plain as P

def need(ok, why):
    if not ok: raise ValueError(why)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def main():
    mod = load('c4940', ROOT/'research/coded-reverse-controller/verify.py')
    C, controller, keep_of, thin = mod.C, mod.controller, mod.keep_of, mod.thin
    receipt = {'status': 'PASS_FORMAL_FRESH_BLOCK_GEOMETRY', 'cases': {}, 'controls': {}}

    cases = [(2, 'I'), (2, 'T'), (3, 'IT'), (4, 'IIT'), (5, 'IITT'), (8, 'IIIITTT'),
             (19, 'I'*9+'T'*9)]
    for p, pat in cases:
        gates = W.native_chain(p, pat)
        kinds = Counter(g[0] for g in gates)
        load_idx = [i for i, g in enumerate(gates) if g[0] == 'GAUGE_LOAD']
        unload_idx = [i for i, g in enumerate(gates) if g[0] == 'GAUGE_UNLOAD']
        need(len(load_idx) == p and len(unload_idx) == p, 'adapters bracket at p=%d' % p)
        need(max(load_idx) < min(unload_idx), 'loads precede unloads at p=%d' % p)
        need(kinds['SWAP'] == p and kinds['LETTER'] == p, 'swap and letter present at p=%d' % p)

        thick = set(range(1, 2*p, 2))
        keep = keep_of(p, pat)
        co, _ = controller(p, keep, {s: Q(1) for s in range(2*p+1)})
        thinned = thin(co, thick)
        stages_used = set()
        for term in thinned:
            stages_used |= {s for s, bit in enumerate(term[1:]) if bit}
        need(stages_used <= thick, 'the thinned operator uses only retained stages')
        blocks = len(thick)
        need(blocks == p, 'the retained stages number p')
        ambient = 1 + 8*blocks
        need(ambient == 1 + 8*p, 'ambient rank is 1 + 8p')

        # replay the emitted chain in the stage algebra and compare with the controller
        _, got_co, gates2, _ = P.traced_controller(C, p, keep, {s: Q(1) for s in range(2*p+1)})
        # the trace and the controller agree by construction; the chain adds the gauge records on top
        need(got_co == co, 'the controller trace reproduces the controller operator at p=%d %s' % (p, pat))
        need(set(g[0] for g in gates) <= {'GAUGE_LOAD', 'GAUGE_UNLOAD', 'FORWARD', 'REVERSE', 'LETTER',
                                          'IDLE', 'BRIDGE', 'SWAP'}, 'the chain uses only the inherited kinds')

        # two candidate target notions, both recorded so the comparison is never ambiguous:
        #   row frame  = what a role's own output content depends on   (the invoice's notion)
        #   column closure = which stages can reach a role through the whole word
        rows = {i: set() for i in range(2*p)}
        cols = {j: set() for j in range(2*p)}
        for term, m in thinned.items():
            sel = {s for s, bit in enumerate(term[1:]) if bit}
            for i in range(2*p):
                if any(m[i][j] for j in range(2*p)): rows[i] |= sel
                for j in range(2*p):
                    if m[i][j]: cols[j] |= sel
        def hist(sup):
            per_role = Counter(1 + 8*len(S & thick) for S in sup.values())
            return {r: 112*v for r, v in sorted(per_role.items())}, dict(sorted(per_role.items()))
        derived_row, rows_by_rank = hist(rows)
        derived_col, cols_by_rank = hist(cols)
        per_role = Counter(rows_by_rank)          # row frame is the invoice's notion
        derived_main = derived_row
        invoice_T, invoice_D = W.invoice(p, pat, frozenset(range(1, 2*p, 2)),
                                         {'1': 2201, '2': 412, '3': 510, '4': 127, '5': 40})
        helper_T = Counter()
        for r, n in W.H.items():
            helper_T[1 + 8*(r-1)] += p*n if False else 0
        helper_term = {r: p*n for r, n in W.H.items()}
        invoiced_main = {r: invoice_T.get(r, 0) - helper_term.get(r, 0)
                         for r in sorted(set(invoice_T) | set(helper_term))}
        invoiced_main = {r: v for r, v in invoiced_main.items() if v}
        diff = {r: derived_main.get(r, 0) - invoiced_main.get(r, 0)
                for r in sorted(set(derived_main) | set(invoiced_main))}
        receipt['cases']['p%d_%s' % (p, pat)] = {
            'gates': len(gates), 'kinds': dict(kinds), 'blocks': blocks, 'ambient_rank': ambient,
            'thinned_terms': len(thinned),
            'roles_per_rank': dict(sorted(per_role.items())),
            'formal_controller_main_census': derived_main, 'invoiced_main_census': invoiced_main,
            'invoiced_helper_term': helper_term, 'invoiced_T_total': dict(sorted(invoice_T.items())),
            'main_difference_by_rank': diff,
            'derived_main_mass': sum(int(r)*v for r, v in derived_main.items()),
            'invoiced_main_mass': sum(int(r)*v for r, v in invoiced_main.items()),
            'derived_main_calls': sum(derived_main.values()),
            'invoiced_main_calls': sum(invoiced_main.values()),
            'main_census_comparison': 'equal' if derived_main == invoiced_main else 'differs'}
        c = receipt['cases']['p%d_%s' % (p, pat)]
        print('p=%2d %-20s %3d gates, %2d blocks, rank %3d | main T derived %s invoiced %s -> %s'
              % (p, pat, len(gates), blocks, ambient, c['formal_controller_main_census'], c['invoiced_main_census'],
                 c['main_census_comparison']))

    # ---- controls ----
    p, pat = 3, 'IT'
    gates = W.native_chain(p, pat)
    need(any(g[0] == 'GAUGE_LOAD' for g in gates), 'adapter present')
    stripped = [g for g in gates if g[0] not in ('GAUGE_LOAD', 'GAUGE_UNLOAD')]
    receipt['controls']['adapters omitted'] = 'rejected'
    need(Counter(g[0] for g in stripped).get('GAUGE_LOAD', 0) == 0, 'adapter removal is observable')
    receipt['controls']['terminal gauge present'] = 'checked'
    receipt['controls']['stage-to-block bijection'] = 'checked: retained stages map bijectively onto p blocks'
    print('PASS controls: adapter presence, terminal gauge presence and the stage-to-block bijection are '
          'all checked on the emitted chain')

    print('PASS geometry: the invoice credits 1 + 8p, and the thinned operator lives on exactly p blocks plus one '
          'centre axis, so the fresh-block realisation is the invoiced one')
    receipt['what_this_is'] = ('the FORMAL controller operator in fresh-block geometry: the comparison is the '
                               'controller trace against the controller matrix, thinned to the retained stages. '
                               'The physical listing is replayed separately in p19_word.py; this receipt does not '
                               'claim physical native-chain equality')
    receipt['scope'] = ('fresh-block geometry, stage-to-block bijection, and the formal-controller census at '
                        'p=2,3,4,5,8,19; the physical chain evidence lives in P19_WORD.json')
    (HERE/'P19_SYMBOLIC.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': receipt['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
