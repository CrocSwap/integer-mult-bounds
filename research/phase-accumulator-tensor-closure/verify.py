#!/usr/bin/env python3
"""Read-only exact replay, including recursive maps and failure controls.

Gareth Davidson (bitplane), with substantial OpenAI Codex assistance.
Apache-2.0. Checks remain active under optimized Python.
"""
import argparse
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import (Op, accumulator_word, apply, c_word, check_columns,
                   columnwise_bank_word, denominator_budget, inverse_word,
                   q_word, q_walsh_word, rank_binary, reference_c_column, reference_open_column,
                   reference_q_column, require, v2, word_digest)
from invoice import audit_charge, charge

HERE = Path(__file__).resolve().parent


def sum_xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def factor_binary(rows, f):
    """M=L^T R: original independent rows and their exact combinations."""
    basis = []
    for row in rows:
        if rank_binary(basis+[row]) > len(basis):
            basis.append(row)
    combinations = {0:0}
    for i, row in enumerate(basis):
        combinations.update({value ^ row: mask | (1 << i) for value, mask in list(combinations.items())})
    left = [0]*len(basis)
    for j, row in enumerate(rows):
        mask = combinations[row]
        for i in range(len(basis)):
            left[i] |= ((mask >> i) & 1) << j
    require(all(rows[j] == sum_xor(basis[i] for i in range(len(basis)) if (left[i] >> j) & 1)
                for j in range(f)), 'rank factorization failed')
    return left, basis


def binary_apply(rows, value):
    return sum(((row & value).bit_count() % 2) << i for i, row in enumerate(rows))


def representation_checks():
    census = []
    total_pairs = 0
    for f in (1,2,3):
        counts = Counter()
        for code in range(1 << (f*f)):
            rows = [(code >> (j*f)) & ((1 << f)-1) for j in range(f)]
            left, right = factor_binary(rows, f)
            rank = len(left)
            counts[rank] += 1
            d = 1 << rank
            for u in range(1 << f):
                zu = binary_apply(left, u)
                for v in range(1 << f):
                    xv = binary_apply(right, v)
                    required_phase = (u & binary_apply(rows, v)).bit_count() % 2
                    require((zu & xv).bit_count() % 2 == required_phase, 'wrong commutator form')
                    for initial in range(d):
                        c, sign = initial, 1
                        for _ in range(2):
                            if (zu & c).bit_count() % 2:
                                sign = -sign
                            c ^= xv
                        require(c == initial and sign == (-1 if required_phase else 1), 'bank not returned')
                    total_pairs += 1
            for multiplicity in (1,2,3):
                require(v2(multiplicity*d) >= rank, 'direct-sum multiplicity lost divisibility')
        census.append({'columns':f, 'forms':1 << (f*f), 'rank_histogram':dict(sorted(counts.items()))})
    rows3 = [tuple((code >> (3*j)) & 7 for j in range(3)) for code in range(512)]
    low = [rows for rows in rows3 if rank_binary(rows) <= 1]
    require(len(low) == 50, 'unexpected one-bit-bank form count')
    for a in low:
        for b in low:
            combined = tuple(x ^ y for x,y in zip(a,b))
            require(rank_binary(combined) <= 2 and combined != (1,2,4), 'two one-bit rounds computed rank three')
    sharp = []
    for f in range(1,17):
        for bank_bits in range(1,5):
            batches = (f+bank_bits-1)//bank_bits
            forms = []
            for start in range(0,f,bank_bits):
                forms.append(tuple((1 << j) if start <= j < min(f,start+bank_bits) else 0 for j in range(f)))
            require(all(rank_binary(m) <= bank_bits for m in forms), 'block bank too small')
            require(tuple(sum_xor(m[j] for m in forms) for j in range(f)) == tuple(1 << j for j in range(f)),
                    'partition did not compute the dot product')
            require((batches-1)*bank_bits < f <= batches*bank_bits, 'batch count not sharp')
            sharp.append([f,1 << bank_bits,batches])
    return {'binary_form_census':census, 'source_label_pairs':total_pairs,
            'two_round_one_bit_bank_pairs':len(low)**2, 'sharp_partition_cases':sharp,
            'proved_scope':'Separable exact representations of the additive binary label groups; scalar commutator phase on every bank coordinate.'}


def eigenvector_failure(word, f):
    """Cross-column character u=e0, v=e1 must have positive dot phase."""
    bits = 2*f+1
    grid = 1 << (denominator_budget(word)+bits+2)
    n = 1 << bits
    real = [grid*(-1 if ((j & 1) ^ ((j >> (f+1)) & 1)) else 1) if j < (1 << (2*f)) else 0
            for j in range(n)]
    imag = [0]*n
    before = real.copy()
    apply(word, real, imag)
    require(real == [-v for v in before] and not any(imag), 'cross-column counterexample changed')
    return {'columns':f,'u':1,'v':2,'initial_bank':0,'required_phase':1,'observed_phase':-1,
            'nonzero_input_cells':1 << (2*f), 'word_sha256':word_digest(word)}


def rejects(word, bits, ref):
    try:
        check_columns(word, bits, ref)
    except ValueError:
        return True
    return False


def controls():
    checked = {}
    refq=lambda c,g:reference_q_column(6,(0,1),(2,3),c,g)
    w=accumulator_word(2)
    checked['producer_without_consumer']=rejects(accumulator_word(2,half=True),6,refq)
    checked['omitted_last_return']=rejects(w[:-1],6,refq)
    bad=w.copy()
    k=[i for i,op in enumerate(bad) if op.kind=='xor' and op.b==(2,3)][-1]
    op=bad[k];bad[k]=Op('xor',op.a,(3,2))
    checked['changed_consumer_source']=rejects(bad,6,refq)
    w=q_word((0,1),(2,3))
    checked['missing_inverse_scale']=rejects([op for op in w if not(op.kind=='scale_b' and op.power<0)],4,
                                             lambda c,g:reference_q_column(4,(0,1),(2,3),c,g))
    w=c_word(range(3),1)
    checked['missing_endpoint_sign']=rejects([op for op in w if op.kind!='translate'],3,
                                              lambda c,g:reference_c_column(3,(0,1,2),c,g))
    checked['wrong_chart_direction']=rejects(list(reversed(w[:4]))+w[4:],3,
                                             lambda c,g:reference_c_column(3,(0,1,2),c,g))
    inv=charge(w,3);inv['execution_counts']['data_head_cell_steps']-=1
    try:
        audit_charge(w,3,inv)
    except ValueError:
        checked['missing_head_movement']=True
    inv=charge(w,3);inv['native_C_children'][1]-=1
    try:
        audit_charge(w,3,inv)
    except ValueError:
        checked['missing_recursive_child']=True
    inv=charge(w,3);inv['native_child_operand_cells'][0]['cells']//=2
    try:
        audit_charge(w,3,inv)
    except ValueError:
        correct=Fraction(1,3)+Fraction(2,3)*1
        undercharged=Fraction(1,3)+Fraction(2,3)*Fraction(1,2)
        checked['half_volume_child_false_gain']=(correct==1 and undercharged<1)
    # A valid two-lane Pauli pair plus one untouched lane is NOT a three-lane
    # representation of the same nonzero scalar commutator phase.
    def pair_returns_minus_identity(d):
        for initial in range(d):
            c, sign=initial,1
            for _ in range(2):
                if c==1:
                    sign=-sign
                if c<2:
                    c^=1
            if c!=initial or sign!=-1:
                return False
        return True
    checked['odd_bank_for_nonzero_form']=(pair_returns_minus_identity(2) and not pair_returns_minus_identity(3))
    require(len(checked)==10 and all(checked.values()), 'a negative control failed')
    return checked


def replay():
    fixtures={}
    for f in (1,2):
        fixtures[f'open_P_f{f}']=(accumulator_word(f,half=True),3*f,
                                 lambda c,g,f=f:reference_open_column(f,c,g))
        ref=lambda c,g,f=f:reference_q_column(3*f,tuple(range(f)),tuple(range(f,2*f)),c,g)
        fixtures[f'tensor_bank_f{f}']=(accumulator_word(f),3*f,ref)
        fixtures[f'substituted_bank_f{f}']=(columnwise_bank_word(f),3*f,ref)
        fixtures[f'shared_bank_closed_children_f{f}']=(columnwise_bank_word(f,shared=True,close_each=True),2*f+1,
                      lambda c,g,f=f:reference_q_column(2*f+1,tuple(range(f)),tuple(range(f,2*f)),c,g))
        fixtures[f'shared_bank_reverse_consumer_f{f}']=(columnwise_bank_word(f,shared=True,reverse_consumer=True),2*f+1,
                      lambda c,g,f=f:reference_q_column(2*f+1,tuple(range(f)),tuple(range(f,2*f)),c,g))
        fixtures[f'Q_f{f}']=(q_word(range(f),range(f,2*f)),2*f,
                      lambda c,g,f=f:reference_q_column(2*f,tuple(range(f)),tuple(range(f,2*f)),c,g))
        fixtures[f'Q_f{f}_with_bank_spectators']=(q_word(range(f),range(f,2*f)),3*f,ref)
        fixtures[f'Q_f{f}_one_wide_C']=(q_walsh_word(range(f),range(f,2*f)),3*f,ref)
        for label,depth in [('direct',0),('typed',1)]:
            fixtures[f'C_{3*f}_{label}']=(c_word(range(3*f),depth),3*f,
                      lambda c,g,f=f:reference_c_column(3*f,tuple(range(3*f)),c,g))
    fixtures['C_9_two_levels']=(c_word(range(9),2),9,lambda c,g:reference_c_column(9,tuple(range(9)),c,g))
    fixtures['Q_f3_substituted']=(q_word(range(3),range(3,6),1),6,
                                lambda c,g:reference_q_column(6,(0,1,2),(3,4,5),c,g))
    fixtures['tensor_bank_f3_nested_basis']=(accumulator_word(3,depth=1),9,
                                lambda c,g:reference_q_column(9,(0,1,2),(3,4,5),c,g))
    checks={}
    for name,(word,bits,ref) in fixtures.items():
        checkpoints=({len(word)//2-1:lambda c,g:reference_open_column(3,c,g)}
                     if name=='tensor_bank_f3_nested_basis' else None)
        result=check_columns(word,bits,ref,checkpoints=checkpoints)
        invoice=charge(word,bits);audit_charge(word,bits,invoice)
        result['invoice']=invoice
        result['program']=[op.record() for op in word]
        checks[name]=result
    word,bits,_=fixtures['C_9_two_levels']
    inverse=inverse_word(word)
    def cref_inverse(column,grid):
        r,i=reference_c_column(9,tuple(range(9)),column,grid)
        return r,[-v for v in i]
    inverse_check=check_columns(inverse,bits,cref_inverse)
    inverse_invoice=charge(inverse,bits);audit_charge(inverse,bits,inverse_invoice)
    inverse_check['invoice']=inverse_invoice
    require(checks['C_9_two_levels']['invoice']['native_C_children']=={1:9}, 'two-level child inventory changed')
    require(checks['C_3_typed']['invoice']['native_C_children']=={1:3}, 'one-level child inventory changed')
    require(checks['tensor_bank_f3_nested_basis']['invoice']['native_C_children']=={1:12},
            'nested live-bank child inventory changed')
    require(checks['C_9_two_levels']['column_support_minmax']==[512,512], 'C9 support changed')
    require(checks['Q_f2_with_bank_spectators']['column_support_minmax']==[16,16], 'Q support changed')
    return {'status':'PASS_PHASE_ACCUMULATOR_TENSOR_CLOSURE_NO_CONTRACTION',
            'fixtures':checks,'literal_inverse_C9':inverse_check,
            'aggregate_failure':eigenvector_failure(accumulator_word(2,aggregate=True),2),
            'shared_producer_failure':eigenvector_failure(columnwise_bank_word(2,shared=True),2),
            'representations':representation_checks(),'negative_controls':controls(),
            'support_screen':{'C_n_minimum_total_C_axis_width':'n',
                              'Q_f_minimum_total_C_axis_width':'2*f',
                              'scope':'Products of C_k on fixed full-volume arrays and arbitrary monomial maps; exact whole-array endpoint, including all bank coordinates.'},
            'moment':{'types':['C_n','Q_(n/2)'],
                      'matrix_at_zero_saving':[['1/3','2/3'],['1','0']],
                      'positive_fixed_vector':['1','1'],
                      'eliminated_Q_one_level':'3^a',
                      'eliminated_Q_two_levels':'9^a',
                      'strict_contraction_for_a_ge_0':False,
                      'scope':'Displayed C/Q realization only; no universal native lower bound.'},
            'new_kappa':False,'evidence_status':'Author checked, same AI-assisted author for both implementations; not independent human review.'}


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--emit',action='store_true',help='print freshly derived evidence; do not modify files')
    args=ap.parse_args()
    result=replay()
    if args.emit:
        print(json.dumps(result,indent=2,sort_keys=True))
        return
    expected=json.loads((HERE/'RESULT.json').read_text())
    require(canonical(result)==canonical(expected),'receipt differs from complete recomputation')
    print(f'PASS_PHASE_ACCUMULATOR_TENSOR_CLOSURE fixtures={len(result["fixtures"])} C9_columns=512 two_level_children=9 controls=10 no_contraction no_new_kappa')


if __name__=='__main__':
    main()
