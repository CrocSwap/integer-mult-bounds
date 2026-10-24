#!/usr/bin/env python3
"""ROOT-GO bounded unit-compatibility screen of the declared r128 placement.

This tests a declared design interface, not a delivered whole outer caller.
No Fourier evaluation, native query, emitted source word, compiler, or floats.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import sys
import check_producer_packet as source

HERE = Path(__file__).resolve().parent
R = 128


def require(ok, label):
    if not ok:
        raise RuntimeError(label)


def product(a,b):
    out = [Q()] * R
    for i,x in enumerate(a):
        if x:
            for j,y in enumerate(b):
                if y:
                    out[(i+j) % R] += x*y*(-1 if i+j >= R else 1)
    return out


def basis(j):
    return [Q(i==j) for i in range(R)]


def apply(matrix, vector):
    return [sum((x*y for x,y in zip(row,vector)),Q()) for row in matrix]


def main():
    before = source.packet_hashes()
    audit_file = HERE/'PRODUCER-PACKET-RESULT.json'
    audit = json.loads(audit_file.read_text())
    require(audit['status'] == 'PASS_SOURCE_PACKET_AUDIT_ONLY', 'source audit must pass first')
    require(audit['packet_hashes_after'] == before, 'source audit is for this exact packet')
    corrected = json.loads((source.PACKET/'CORRECTED-DERIVATION.json').read_text())
    G = [[Q(q) for q in row] for row in corrected['F_actual']]
    rr = [[Q(q) for q in row] for row in json.loads(source.read('R.json'))]
    J = corrected['selected_ports_J']
    low_u = [[rr[k][i]*Q(1-12*(i in J),4) for k in range(8)] for i in range(112)]
    require(source.mm(rr,low_u) == [[Q(2*(i==j)) for j in range(8)] for i in range(8)], 'RU=2I')
    require(G == [[Q(i==j)-sum(low_u[i][k]*rr[k][j] for k in range(1,8))
                   for j in range(112)] for i in range(112)], 'G=I-U D R')
    # D=diag(0,1,...,1), D²=D, so G²=I−2UDR+UD(RU)DR=I.
    # The literal inverse transpose is consequently G^T, in this declared basis.
    normalizers = json.loads(source.read('NORMALIZERS.json'))
    require(len(normalizers['ports']) == 112, 'all112 native normalizers')
    normalizer_words = []
    for port in normalizers['ports']:
        word = port['K_word']
        for event in word:
            require(event[0] in ('P','D'), 'K word must have no shift/global phase/H')
            if event[0] == 'P':
                rows = event[1]
                require(len(rows) == 9, 'native address dimension')
                # Homogeneous binary permutation fixes zero; check invertibility
                # by exact row elimination, without evaluating any native query.
                pivots = {}
                for row in rows:
                    require(0 <= row < 512, 'binary linear row')
                    x = row
                    while x:
                        bit = x.bit_length()-1
                        if bit in pivots:
                            x ^= pivots[bit]
                        else:
                            pivots[bit] = x
                            break
                require(len(pivots) == 9, 'invertible address permutation')
            else:
                require(len(event) == 3 and len(event[1]) == len(event[2]) == 9,
                        'diagonal phase polynomial with no constant')
        normalizer_words.append(word)
    # Every P and D fixes delta0 with phase+1; transpose does too because each
    # is monomial/unitary. Tensor column lifts keep zero and phase+1 for all f.
    U = [[G[i][j] if i<112 and j<112 else Q(i==j)
          for j in range(R)] for i in range(R)]
    V = list(map(list,zip(*U)))
    epsilon, eta = apply(U,basis(0)), apply(V,basis(0))
    # Actual e_P=128 e0 multiplies both epsilon and eta by128. Compare the
    # residual divided by128; ordinary product/r from P cancels independently.
    witness = None
    probes = []
    for j in range(1,R):
        Ua, Va = apply(U,basis(j)), apply(V,basis(j))
        left, right = product(Ua,eta), product(epsilon,Va)
        residual = [a-b for a,b in zip(left,right)]
        probes.append(j)
        if any(residual):
            k = next(k for k,q in enumerate(residual) if q)
            witness = {'input_basis':j,'first_failed_output_coefficient':k,
                       'left_Ua_times_eta':str(left[k]),'right_epsilon_times_Va':str(right[k]),
                       'residual_left_minus_right':str(residual[k]),
                       'all_left_coefficients':[str(q) for q in left],
                       'all_right_coefficients':[str(q) for q in right],
                       'all_residual_coefficients':[str(q) for q in residual],
                       'U_a':[str(q) for q in Ua],'V_a':[str(q) for q in Va]}
            break  # stop at first failed basis; no other placement/mask search
    require(witness is not None, 'unexpected pass of every allowed unit probe')
    # Controls concern the literal product, independently of the candidate.
    require(product(basis(127),basis(1)) == [-q for q in basis(0)], 'negacyclic wrap -1')
    require(product(basis(0),basis(1)) == basis(1), 'ordinary unit')
    ident = [[Q(i==j) for j in range(R)] for i in range(R)]
    require(product(apply(ident,basis(1)),basis(0)) == product(basis(0),apply(ident,basis(1))),
            'identity U=V=I unit gate passes')
    # Two record arrays multiply each record independently: distinct occupied
    # records give two all-zero polynomial records, not a scalar contraction.
    first_record = [basis(127),[Q()]*R]
    second_record = [[Q()]*R,basis(1)]
    require([product(a,b) for a,b in zip(first_record,second_record)] == [[Q()]*R,[Q()]*R],
            'cross-record product is zero')
    correct_output = [q/R for q in product(basis(0),basis(0))]
    wrong_output = [-q for q in correct_output]
    require(correct_output != wrong_output, 'wrong output W=-I rejected for identity maps')
    # G is real, so its transpose and adjoint coincide. Use an explicitly
    # separate complex scalar control: U=i, true U^-T=-i, U^-*=i.
    def cmul(a,b):
        return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
    i, minus_i = (Q(),Q(1)), (Q(),Q(-1))
    require(cmul(i,minus_i) == (Q(1),Q()) and cmul(i,i) == (Q(-1),Q()),
            'complex inverse-transpose versus inverse-adjoint control')
    after = source.packet_hashes()
    result = {'status':'REJECT_DECLARED_PRODUCT_PLACEMENT_BY_EXACT_NECESSARY_UNIT_IDENTITY',
              'source_head':source.HEAD,'packet_hashes_before':before,'packet_hashes_after':after,
              'source_audit_sha256':sha256(audit_file.read_bytes()).hexdigest(),
              'declared_placement':{'r':R,'owner_coefficients':[0,111],
                 'independent_identity_spectator_coefficients':[112,127],
                 'native_address_zero':'record0', 'coefficient_U':'G direct_sum I16',
                 'coefficient_V':'G^T direct_sum I16 after exact involution derivation',
                 'scope':'imposed diagnostic design placement, not derived whole outer caller'},
              'invariant_record_premise':{'normalizer_source_sha256':source.SOURCE_PINS['NORMALIZERS.json'],
                 'all112_K_words_fix_zero_with_phase_plus_one':True,
                 'proof':'homogeneous invertible P and D with no constant; transpose and positive-column lifts preserve delta0'},
              'unit_normalization':'epsilon and eta below are divided by128 relative to e_P=128e0; witness is ordinary negacyclic residual with that common128 removed',
              'epsilon_over128':[str(q) for q in epsilon], 'eta_over128':[str(q) for q in eta],
              'tested_basis_indices':probes,'witness':witness,
              'controls':{'identity_unit_gate':'PASS','negacyclic_y127_times_y':'-1',
                 'different_records':'ZERO_ALL_COEFFICIENTS','wrong_output_W_minus_I':'REJECTED',
                 'complex_transpose_vs_adjoint':'DISTINGUISHED_BY_SEPARATE_SCALAR_i_CONTROL',
                 'candidate_transpose_vs_adjoint':'G_REAL_THE_TWO_COINCIDE',
                 'old_bad_restoration':'retained in PRODUCER-PACKET-RESULT.json with G_squared_00=10'},
              'unit_invertibility':'not needed for rejection once necessary equality fails',
              'search_stopped_at_first_failure':True,'other_placements_tested':False,
              'native_execution':False,'Fourier_E_used':False,'new_kappa':None}
    out = HERE/('DECLARED-PRODUCT-RESULT-OPTIMIZED.json' if sys.flags.optimize else 'DECLARED-PRODUCT-RESULT.json')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'input_basis':witness['input_basis'],
                      'output_coefficient':witness['first_failed_output_coefficient'],
                      'residual':witness['residual_left_minus_right'],'result':str(out)}))


if __name__ == '__main__':
    main()
