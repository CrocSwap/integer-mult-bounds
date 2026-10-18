#!/usr/bin/env python3
"""Rational-only verification of the twelve-case H6 certificate.

Does not import upstream PR606 code or execute floating nomination. Four source
files are hash-checked as bytes. Every alpha grid cell, pressure sign, interval,
stock identity, and target binding is independently recomputed using Fraction.
Negative fixtures are synthetic controls, not additional scientific cases.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as m
from source_bindings import authenticate, check_bytes, FILES, HERE, REVISION


def validate_case(case, expected_id, target, L, quoted):
    m.require(case['target_id'] == expected_id and case['L'] == L,
              'case identity/stage binding')
    m.require(case['target'] == str(target), 'exact target binding')
    m.require(case['quoted_R'] == quoted, 'quoted threshold attribution')
    exact = m.boundary_record(L, target)
    m.require(case['exact'] == exact, 'exact boundary evidence differs')
    R = exact['R']
    r = m.row(L)
    threshold = {
        'stages':L, 'm':r['m'], 'deficit':r['D'], 'max_helpers':R,
        'helpers_per_port':str(F(R,m.N)), 'helpers_per_bank':r['q'],
        'pad_rank':r['p'], 'total_stock_at_max':str(r['W']+F(L*R,r['q'])),
        'data_path':m.DATA, 'helper_path':m.HP,
        'virtual_entrance_dimension':0, 'bad_envelope':False,
    }
    m.require(case['source_threshold'] == threshold, 'source threshold fields')
    for key, count in [('invoice_at_R', R), ('invoice_at_R_plus_1', R+1)]:
        recorded = case[key]
        m.require(type(recorded['z']) is int, 'integer alpha grid index')
        expected = m.invoice_record(L, count, recorded['z'])
        m.require(recorded == expected, 'invoice certificate differs')
    low_R = case['invoice_at_R']['scaled_kappa_interval'][0]
    upper_next = case['invoice_at_R_plus_1']['scaled_kappa_interval'][1]
    m.require(F(low_R,m.SCALE) > target > F(upper_next,m.SCALE),
              'strict scaled endpoint separation')
    m.require(set(case) == {'target_id','target','L','quoted_R','exact',
                           'source_threshold','invoice_at_R','invoice_at_R_plus_1'},
              'unexpected/missing case fields')


def validate(evidence):
    m.require(evidence['schema'] == 'h6-banked-twelve-case-audit-v1', 'schema')
    m.require(evidence['retained_source_revision'] == REVISION, 'source revision')
    m.require(evidence['source_files'] == authenticate(), 'source manifest')
    m.require(evidence['parameters'] == {
        'n':m.N,'h':m.H,'hist':{'17':256,'15':560},'data':m.DATA,'hp':m.HP,
        'virtual':False,'bad':False,'stages':[3,5,7],'scale':m.SCALE},
        'frozen parameter bindings')
    m.require(evidence['excluded_historical_default'] ==
              str(F(1612719427075359,10**18)), 'historical default binding')
    m.require(evidence['skeletons'] == [m.skeleton_record(L) for L in (3,5,7)],
              'rank-mass skeletons')
    m.require(len(evidence['cases']) == 12, 'exact twelve-case coverage')
    j = 0
    for name,target,quoted in m.TARGETS:
        for k,L in enumerate((3,5,7)):
            validate_case(evidence['cases'][j], name,target,L,
                          None if quoted is None else quoted[k])
            j += 1
    m.require(set(evidence) == {'schema','retained_source_revision','source_files',
        'parameters','excluded_historical_default','skeletons','cases'},
        'unexpected/missing top-level evidence fields')


def controls(evidence):
    result = []
    def rejected(name, operation):
        try:
            operation()
        except ValueError:
            result.append({'control':name,'result':'REJECTED as required'})
        else:
            raise ValueError('Negative control was accepted: '+name)

    path = next(iter(FILES))
    original = (HERE/'vendor'/path).read_bytes()
    rejected('one-byte source mutation before import',
             lambda: check_bytes(bytes([original[0]^1])+original[1:], FILES[path],path))
    r = m.row(3,80558)
    without_pad = deepcopy(r)
    without_pad['terms'].pop()
    rejected('helper children without paid pad', lambda:m.validate_mass_cap(without_pad))
    stock_only = deepcopy(r)
    stock_only['W'] += F(r['L'],r['q'])
    rejected('one extra banked stock share without children',
             lambda:m.validate_mass_cap(stock_only))
    children_only = deepcopy(r)
    children_only['terms'] += r['unit']
    rejected('one helper of children without stock',lambda:m.validate_mass_cap(children_only))
    bad_cap = deepcopy(r)
    mass,_ = bad_cap['terms'][0]
    bad_cap['terms'][0] = (mass,F(r['m'],r['cap']+1))
    rejected('over-cap child with unchanged total mass',lambda:m.validate_mass_cap(bad_cap))

    cases = evidence['cases']
    def case_test(case, index):
        name,target,quoted = m.TARGETS[index//3]
        L = (3,5,7)[index%3]
        validate_case(case,name,target,L,None if quoted is None else quoted[index%3])
    fake = deepcopy(cases[3]); fake['target']=str(m.TARGETS[0][1])
    rejected('rounded PR890 silently substituted for retained target',
             lambda:case_test(fake,3))
    fake = deepcopy(cases[6]); fake['target']=str(F(1612719427075359,10**18))
    rejected('historical FRONTIER silently substituted for selected target',
             lambda:case_test(fake,6))
    fake = deepcopy(cases[0]); fake['exact']['R']+=1
    rejected('R+1 falsely relabeled as admissible maximum',lambda:case_test(fake,0))
    fake = deepcopy(cases[0]); fake['invoice_at_R']['scaled_kappa_interval'][0]+=1
    rejected('one-unit forged lower scaled endpoint',lambda:case_test(fake,0))
    fake = deepcopy(cases[0]); fake['invoice_at_R']['z']+=1
    rejected('wrong exact alpha grid cell',lambda:case_test(fake,0))
    incomplete = deepcopy(evidence); incomplete['cases'].pop()
    rejected('omitted twelfth scientific case',lambda:validate(incomplete))
    rejected('extra stage L=9',lambda:m.row(9))
    rejected('exact strict-boundary tie is not resolved by floor',
             lambda:m.strict_allowance(F(3),F(3)))
    rejected('interval crossing integer is left unresolved',
             lambda:m.strict_allowance(F(299,100),F(301,100)))
    rejected('invalid logarithm range',lambda:m.ln_bounds(F(1,2)))
    rejected('invalid exponential range',lambda:m.exp_bounds(F(0),F(1)))

    # A concrete same-row control that separates semantics. This is NOT a
    # thirteenth comparison target: it tests equality at an output endpoint.
    example = cases[0]
    count = example['exact']['R']
    s = example['invoice_at_R']['scaled_kappa_interval'][0]
    synthetic_t = F(s,m.SCALE)
    exact_pressure = m.pressure(m.row(3,count),synthetic_t/(1-synthetic_t))
    m.require(not F(s,m.SCALE)>synthetic_t, 'rounded-lower equality must fail strict test')
    m.require(exact_pressure[1]<m.row(3,count)['D'], 'true root is strictly above endpoint')
    result.append({'control':'rounded lower endpoint equality versus exact pressure',
                   'result':'DISTINCT: invoice strict test false, true-root test true',
                   'synthetic_target':str(synthetic_t)})
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence',type=Path,nargs='?',default=HERE/'EVIDENCE.json')
    parser.add_argument('--controls-output',type=Path,
                        help='Write NEW deterministic controls JSON; never overwrite')
    args=parser.parse_args()
    evidence=json.loads(args.evidence.read_text())
    validate(evidence)
    print('PASS all 12 cases, 24 exact alpha cells and outward invoice brackets')
    print('PASS all 12 R/R+1 pressure signs and strict scaled endpoint separations')
    result=controls(evidence)
    for entry in result:
        print('PASS CONTROL '+entry['control']+': '+entry['result'])
    if args.controls_output:
        with args.controls_output.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(result,stream,sort_keys=True,indent=2);stream.write('\n')
    print('PASS rational-only certificate verification; no upstream execution or float nomination')

if __name__=='__main__':
    main()
