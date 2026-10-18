#!/usr/bin/env python3
"""Exactly twelve H6 cases; original PR606 import plus exact reconstruction.

No network, dependencies, geometry files, run(), source_check(), stage scan,
virtual helpers, bad-branch pricing, or author-supplement main program.
The only floating computation is upstream/reconstructed nomination; every
scientific sign and alpha grid cell is independently rationally certified.
"""
import argparse
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fractions import Fraction as F
import model as m
from source_bindings import authenticate, import_banked, REVISION


def source_controls(b):
    """Negative fixtures at an existing stage, not extra comparison cases."""
    def reject(name, operation, fragment):
        try:
            operation()
        except ValueError as exc:
            m.require(fragment in str(exc), 'wrong exception for source control: '+name)
        else:
            raise ValueError('source guard accepted: '+name)
        print('PASS SOURCE CONTROL '+name, flush=True)
    reject('incomplete data path',
           lambda:b.base(m.N,m.H,m.HIST,3,[15]), 'each data chain spans h-1')
    r=b.base(m.N,m.H,m.HIST,3,m.DATA)
    reject('ordinary helper with residual width 16',
           lambda:b.helper(r,[1,7,8],False), 'ordinary helper runs from zero to full')
    reject('helper exceeding ambient width',
           lambda:b.helper(r,[1,7,8,2],False), 'positive helper residual')
    saved=b.c.nominate
    try:
        # Deliberately wrong positive proposal. Only a function object in this
        # temporary process is replaced; no original file bytes are modified.
        b.c.nominate=lambda row: 0.019
        reject('bad floating nomination cannot certify a root',
               lambda:b.invoice(m.N,m.H,m.HIST,3,m.DATA,m.HP,80558,False),
               'Certified root bracket')
    finally:
        b.c.nominate=saved


def build():
    sources = authenticate()
    b = import_banked()
    m.require(b.c.FRONTIER == F(1612719427075359, 10**18),
              'historical PR592 constant changed')
    cases = []
    for name, target, quoted in m.TARGETS:
        m.require(target != b.c.FRONTIER, 'historical default is not a case')
        for k, L in enumerate((3, 5, 7)):
            native_base = b.base(m.N, m.H, m.HIST, L, m.DATA)
            unit, q, pad = b.helper(native_base, m.HP, False)
            local_base = m.row(L)
            m.require(native_base['terms'] == local_base['terms'][:-len(unit)],
                      'base terms differ from source')
            m.require((unit, q, pad) ==
                      (local_base['unit'], local_base['q'], local_base['p']),
                      'unit helper terms differ from source')
            for field, local in [('m','m'), ('deficit','D'), ('stock','W'), ('cap','cap')]:
                m.require(native_base[field] == local_base[local], 'base field '+field)
            exact = m.boundary_record(L, target)
            R = exact['R']
            threshold = b.threshold(m.N, m.H, m.HIST, L, m.DATA, m.HP,
                                    target, virtual=False, bad=False)
            m.require(threshold['max_helpers'] == R, 'source threshold mismatch')
            if quoted is not None:
                m.require(R == quoted[k], 'quoted author threshold falsified')
            invoices = []
            for count in (R, R+1):
                upstream = b.invoice(m.N, m.H, m.HIST, L, m.DATA, m.HP,
                                     count, virtual=False)
                endpoints, al, ah = m.invoice(L, count)
                z0 = al*10**15+2
                m.require(z0.denominator == 1, 'alpha index not integral')
                rec = m.invoice_record(L, count, int(z0))
                m.require(endpoints == rec['scaled_kappa_interval'] ==
                          upstream['nominal_kappa_interval_scaled_1e18'],
                          'source/reconstruction interval mismatch')
                m.require(upstream['stock'] == rec['stock'], 'invoice stock mismatch')
                m.require(upstream['stock_replication_factor'] == q and
                          upstream['helper_pad'] == pad and
                          upstream['max_child'] == rec['max_child_rank'],
                          'invoice packing fields mismatch')
                invoices.append(rec)
            m.require(F(invoices[0]['scaled_kappa_interval'][0], m.SCALE) > target,
                      'R fails lower endpoint criterion')
            m.require(F(invoices[1]['scaled_kappa_interval'][1], m.SCALE) < target,
                      'R+1 not excluded by upper endpoint')
            cases.append({
                'target_id': name, 'target': str(target), 'L': L,
                'quoted_R': None if quoted is None else quoted[k],
                'exact': exact, 'source_threshold': threshold,
                'invoice_at_R': invoices[0], 'invoice_at_R_plus_1': invoices[1],
            })
            print(f"PASS {name:17s} L={L} R={R} lower(R)>target>upper(R+1)", flush=True)
    m.require(len(cases) == 12, 'exactly twelve cases')
    source_controls(b)
    authenticate()  # Imported source files must still have their original bytes.
    return {
        'schema': 'h6-banked-twelve-case-audit-v1',
        'retained_source_revision': REVISION,
        'source_files': sources,
        'parameters': {'n': m.N, 'h': m.H, 'hist': {'17':256,'15':560},
                       'data':m.DATA, 'hp':m.HP, 'virtual':False, 'bad':False,
                       'stages':[3,5,7], 'scale':m.SCALE},
        'excluded_historical_default': str(b.c.FRONTIER),
        'skeletons': [m.skeleton_record(L) for L in (3,5,7)],
        'cases': cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        help='Write a NEW evidence JSON; existing files are never overwritten')
    args = parser.parse_args()
    evidence = build()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(evidence, stream, sort_keys=True, indent=2)
            stream.write('\n')
        print('WROTE new evidence JSON')
    else:
        expected = json.loads((Path(__file__).resolve().parent/'EVIDENCE.json').read_text())
        m.require(evidence == expected, 'replayed evidence differs from canonical evidence')
        print('PASS exact replay equals canonical EVIDENCE.json')

if __name__ == '__main__':
    main()
