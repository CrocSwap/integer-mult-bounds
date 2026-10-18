#!/usr/bin/env python3
"""Three full-title PR1424 cases only; offline, fail-closed H6 appendix.

Default: exact rational pressure/grid verification, including a rational
binary64 rounding model; no upstream execution or floating nomination.
--source: additionally replay 3 threshold calls and 6 adjacent invoices in
unchanged, hash-authenticated PR606, and check native binary64 comparisons.
Never executes price_h6.py's main program or any structure/Walsh program.
"""
import argparse
import ast
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
TARGET_TEXT = '0.001676855229071321886206381217337893'
TARGET = F(TARGET_TEXT)
SHORT = F('0.001676855229071321')
SCALE = 10**18
# Proposals inherited from original target-independent row certificates.
# Each cell is re-proved; no floating nomination is used to accept it.
SEEDS = {3:(1679672779019,1679656758746),
         5:(1679674364931,1679662527951),
         7:(1679675807199,1679664671449)}
EXPECTED = {3:79617,5:88409,7:79399}
ORIGINAL_CODE = {
 'model.py':'d18c4c589e37de077d29120d7b4688ad6a335cd63d225f93621a2573cd23cd80',
 'source_bindings.py':'f247b8a5ef341737318af2d926808b92d26d90ff6db9abf2f714ba132ff6f335'}
AUTHOR_SHA = 'ed83a457ae9deb1a8e06551404735ad3c6d71153ef4a22ec64f615f8d1a5d92a'
AUTHOR_REV = 'b496aed769dd724cd1ff6b921cade626562be27b'


def require(value, message):
    if not value:
        raise ValueError(message)


def check_bytes(data, expected, name):
    require(hashlib.sha256(data).hexdigest() == expected, 'SHA256 mismatch: '+name)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, 'module loader')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def load_original(root):
    code = []
    for name, sha in sorted(ORIGINAL_CODE.items()):
        data = (root/name).read_bytes()
        check_bytes(data, sha, name)
        code.append(dict(path=name, bytes=len(data), sha256=sha))
    bindings = load_module(root/'source_bindings.py', 'h6_appendix_bindings')
    dependencies = bindings.authenticate()  # bytes only, before upstream import
    model = load_module(root/'model.py', 'h6_appendix_model')
    return model, bindings, code, dependencies


def author_binding():
    path = HERE/'author_source/price_h6.py'
    data = path.read_bytes()
    check_bytes(data, AUTHOR_SHA, 'author price_h6.py')
    tree = ast.parse(data, filename=str(path))  # parse, never import or execute
    values = [ast.literal_eval(node.value) for node in tree.body
              if isinstance(node, ast.Assign) and any(
                  isinstance(t, ast.Name) and t.id == 'TARGETS' for t in node.targets)]
    require(values == [{'#890 as used (rounded)':'0.001661957775',
                       '#890 title (exact)':'0.001661957774647029',
                       '#1424 title (exact)':TARGET_TEXT}], 'author target literal binding')
    return dict(path='author_source/price_h6.py', bytes=len(data), sha256=AUTHOR_SHA,
                revision=AUTHOR_REV, imported_or_executed=False)


def nearest_binary64(x):
    """Exact nearest-even rounding for positive normal binary64 values only."""
    x = F(x)
    require(x > 0, 'binary64 positive domain')
    e = x.numerator.bit_length()-x.denominator.bit_length()
    if x < F(2)**e:
        e -= 1
    require(-1022 <= e <= 1023, 'binary64 normal domain')
    step = F(2)**(e-52)
    y = x/step
    q, r = divmod(y.numerator, y.denominator)
    if 2*r > y.denominator or (2*r == y.denominator and q % 2):
        q += 1
    answer = q*step
    require(answer <= F(2)**1024-F(2)**971, 'binary64 finite rounding')
    require(abs(answer-x) <= step/2, 'binary64 outward error bound')
    return answer


def comparison_record(s):
    require(type(s) is int and 0 < s < 2**53, 'exact integer-to-binary64 range')
    x = F(s,SCALE)
    fx, ft = nearest_binary64(x), nearest_binary64(TARGET)
    return {'scaled_endpoint':s, 'exact_above':x>TARGET,
            'binary64_above':fx>ft, 'binary64_value':str(fx),
            'endpoint_rounding_error':str(fx-x),
            'exact_endpoint_minus_target':str(x-TARGET)}


def compact_invoice(m, L, count, z):
    rec = m.invoice_record(L,count,z)
    return {key:rec[key] for key in (
        'R','z','alpha_grid_cell','alpha_bracket','scaled_kappa_interval',
        'stock','rank_mass','max_child_rank',
        'positive_lower_bracket_margin','positive_upper_bracket_margin')}


def make_case(m,L):
    exact = m.boundary_record(L,TARGET)
    R = exact['R']
    require(R == EXPECTED[L], 'claimed full-title threshold falsified')
    left = compact_invoice(m,L,R,SEEDS[L][0])
    right = compact_invoice(m,L,R+1,SEEDS[L][1])
    s = left['scaled_kappa_interval'][0]
    unext = right['scaled_kappa_interval'][1]
    require(F(s,SCALE)>TARGET>F(unext,SCALE), 'strict adjacent scaled endpoints')
    comparisons = [comparison_record(v) for v in (
        s,right['scaled_kappa_interval'][0],unext)]
    require([a['exact_above'] for a in comparisons] == [True,False,False],
            'exact boundary comparisons')
    require([a['binary64_above'] for a in comparisons] == [True,False,False],
            'binary64 boundary comparisons')
    xl,xh = map(F,exact['real_helper_boundary'])
    coarse = m.round_out(xl,xh,10**6)
    return dict(L=L, exact=exact,
                helper_boundary_outward_1e6=[str(x) for x in coarse],
                invoice_at_R=left, invoice_at_R_plus_1=right,
                comparisons_order=['lower(R)','lower(R+1)','upper(R+1)'],
                comparison_evidence=comparisons)


def rounding_control():
    k = TARGET*SCALE
    lower = k.numerator//k.denominator
    require(lower == 1676855229071321, 'scaled target floor')
    require(SHORT*SCALE == lower and lower < k < lower+1,
            'short and full targets have same integer endpoint cutoff')
    s = lower+1
    rec = comparison_record(s)
    require(rec['exact_above'] and not rec['binary64_above'],
            'float/Fraction disagreement control')
    require(nearest_binary64(F(s,SCALE)) == nearest_binary64(TARGET),
            'control fails float strictness by equality')
    require(comparison_record(s+1)['binary64_above'], 'next scaled integer passes float')
    return dict(control='synthetic scaled integer, NOT an added invoice case',
                exact_first_passing_scaled_integer=s,
                binary64_first_passing_scaled_integer=s+1,
                evidence=rec, binary64_target=str(nearest_binary64(TARGET)),
                target_rounding_error=str(nearest_binary64(TARGET)-TARGET))


def build(m, code, deps):
    return dict(schema='h6-full-pr1424-appendix-v1',
        target_id='author_PR1424_full_title', target_decimal=TARGET_TEXT,
        target_fraction=str(TARGET), target_scale=SCALE,
        retained_short_target=str(SHORT), full_minus_short=str(TARGET-SHORT),
        original_code=code, unchanged_PR606_dependencies=deps,
        author_source=author_binding(),
        parameters=dict(n=30960,h=17,hist={'17':256,'15':560},data=[16],
                        hp=[1,7,8,1],virtual=False,bad=False,stages=[3,5,7]),
        cases=[make_case(m,L) for L in (3,5,7)],
        binary64_control=rounding_control(),
        paper_ratio=dict(numerator_printed='0.006945535353',
                         denominator_printed='0.004515128332',
                         exact_ratio=str(F('0.006945535353')/F('0.004515128332')),
                         fully_paid_improvement_certified=False))


def validate(got, expected):
    require(got == expected, 'appendix evidence differs from exact recomputation')


def controls(m,evidence):
    names = []
    def rejected(name,operation):
        try:
            operation()
        except ValueError:
            names.append(name)
        else:
            raise ValueError('Control accepted: '+name)
    for name, mutate in (
        ('short target silently substituted',lambda x:x.update(target_decimal=str(SHORT))),
        ('an extra fourth stage case',lambda x:x['cases'].append(deepcopy(x['cases'][0]))),
        ('one endpoint forged',lambda x:x['cases'][0]['invoice_at_R']['scaled_kappa_interval'].__setitem__(0,0)),
        ('R+1 falsely admitted',lambda x:x['cases'][0]['exact'].__setitem__('R',79618)),
        ('one pressure margin forged',lambda x:x['cases'][0]['exact'].__setitem__('positive_pressure_margin_at_R','0'))):
        bad=deepcopy(evidence); mutate(bad)
        rejected(name,lambda:validate(bad,evidence))
    rejected('wrong positive grid cell',lambda:m.invoice_record(3,79617,SEEDS[3][0]+1))
    rejected('integer pressure tie unresolved',lambda:m.strict_allowance(F(3),F(3)))
    rejected('straddled pressure interval unresolved',lambda:m.strict_allowance(F(299,100),F(301,100)))
    rejected('one author-source byte changed',lambda:check_bytes(
        (HERE/'author_source/price_h6.py').read_bytes()+b' ',AUTHOR_SHA,'mutated copy'))
    rejected('binary64 nonpositive domain',lambda:nearest_binary64(F(0)))
    # Halfway fixtures exercise both parity branches of nearest-even rounding.
    require(nearest_binary64(F(1)+F(1,2**53)) == F(1), 'even tie rounds down')
    require(nearest_binary64(F(1)+F(3,2**53)) == F(1)+F(1,2**51), 'odd tie rounds up')
    return dict(rejected=names, positive=[
        'nearest-even binary64 halfway fixtures',
        'same full-target synthetic integer distinguishes exact from float',
        'three exact adjacent pressure and endpoint certificates'])


def replay_source(m,bindings,evidence):
    require(sys.float_info.radix == 2 and sys.float_info.mant_dig == 53 and
            sys.float_info.rounds == 1, 'native binary64 nearest rounding required')
    b = bindings.import_banked()
    for case in evidence['cases']:
        L = case['L']; R = case['exact']['R']
        base = b.base(m.N,m.H,m.HIST,L,m.DATA)
        unit,q,pad = b.helper(base,m.HP,False)
        local = m.row(L)
        require(base['terms'] == local['terms'][:-len(unit)] and
                (unit,q,pad) == (local['unit'],local['q'],local['p']), 'source skeleton')
        result = b.threshold(m.N,m.H,m.HIST,L,m.DATA,m.HP,TARGET,False,False)
        require(result['max_helpers'] == R, 'source threshold differs')
        for key in ('invoice_at_R','invoice_at_R_plus_1'):
            rec=case[key]
            inv=b.invoice(m.N,m.H,m.HIST,L,m.DATA,m.HP,rec['R'],False)
            require(inv['nominal_kappa_interval_scaled_1e18']==rec['scaled_kappa_interval'],
                    'source adjacent endpoints differ')
            require(inv['stock']==rec['stock'] and inv['deficit']==local['D'] and
                    inv['stock_replication_factor']==q and inv['helper_pad']==pad and
                    inv['max_child']==rec['max_child_rank'], 'source invoice packing')
        for rec in case['comparison_evidence']:
            s=rec['scaled_endpoint']
            require((s/1e18>float(TARGET_TEXT)) == rec['binary64_above'], 'native float comparison')
            require(F.from_float(s/1e18)==F(rec['binary64_value']), 'native quotient rounding')
    ctrl=evidence['binary64_control']; s=ctrl['exact_first_passing_scaled_integer']
    require(F.from_float(float(TARGET_TEXT))==F(ctrl['binary64_target']), 'native target rounding')
    require(F(s)>TARGET*SCALE and not s/1e18>float(TARGET_TEXT), 'native disagreement control')
    bindings.authenticate()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original',type=Path,default=HERE.parent/'h6_banked_invoice_audit')
    parser.add_argument('--evidence',type=Path,default=HERE/'APPENDIX_EVIDENCE.json')
    parser.add_argument('--source',action='store_true')
    parser.add_argument('--output',type=Path,help='Write new evidence, never overwrite')
    parser.add_argument('--controls-output',type=Path,help='Write new control receipt, never overwrite')
    args=parser.parse_args()
    m,bindings,code,deps=load_original(args.original.resolve())
    evidence=build(m,code,deps)
    if args.output:
        with args.output.open('x',encoding='utf-8',newline='\n') as f:
            json.dump(evidence,f,sort_keys=True,indent=2); f.write('\n')
    else:
        validate(json.loads(args.evidence.read_text()),evidence)
    result=controls(m,evidence)
    if args.controls_output:
        with args.controls_output.open('x',encoding='utf-8',newline='\n') as f:
            json.dump(result,f,sort_keys=True,indent=2); f.write('\n')
    if args.source:
        replay_source(m,bindings,evidence)
    for case in evidence['cases']:
        print('PASS full PR1424 L=%d R=%d: lower(R)>target>upper(R+1); exact pressure signs' %
              (case['L'],case['exact']['R']))
    print('PASS %d rejection controls and %d positive controls' %
          (len(result['rejected']),len(result['positive'])))
    print('PASS Fraction and binary64 agree at all three boundaries, but differ at synthetic s=1676855229071322')
    print('PASS source mode: 3 threshold calls, 6 invoices, native rounding checks' if args.source
          else 'PASS rational mode: no upstream execution or floating nomination')
    require(author_binding()==evidence['author_source'], 'author source changed')
    require(bindings.authenticate()==deps,'original dependency bytes changed')

if __name__ == '__main__':
    main()
