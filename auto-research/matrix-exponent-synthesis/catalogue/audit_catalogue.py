"""Meaningful domain/model/identity controls; emits a new local JSON receipt."""
from dataclasses import replace
from pathlib import Path
from fractions import Fraction
import hashlib, json, sys, tempfile
from random import Random
import catalogue as C

HERE = Path(__file__).resolve().parent


def need(condition,message):
    if not condition:
        raise AssertionError(message)


def rejects(call, expected):
    try:
        call()
    except C.Ineligible as error:
        need(expected in str(error),f'wrong rejection: {error}')
        return str(error)
    raise AssertionError('ineligible claim was accepted')


def multiply2(a,b,modulus=None):
    out = tuple(tuple(sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)) for i in range(2))
    return tuple(tuple(v%modulus for v in row) for row in out) if modulus else out


def noncommuting_leaf_counterexample(modulus=None):
    # Actual P/R leaf row: A00=U, A01=V, all B blocks zero.
    u = ((0,1),(0,0)); v = ((0,0),(1,0))
    uv,vu = multiply2(u,v),multiply2(v,u)
    result = tuple(tuple(uv[i][j]-vu[i][j] for j in range(2)) for i in range(2))
    if modulus:
        result = tuple(tuple(z%modulus for z in row) for row in result)
    need(result != ((0,0),(0,0)),'counterexample became zero')
    return {'A00':u,'A01':v,'all_B_blocks':0,'leaf_first_output_block':result,
            'ordinary_AB_output_block':((0,0),(0,0)),
            'modulus':modulus,'source_formula':'P=A00*(B00+A01), R=A01*(B10-A00)'}


def audit():
    cases = []
    q,z,g2,g3 = (C.Domain.parse(x) for x in ('Q','Z','GF2','GF3'))
    checks = C.validate_catalogue_coefficients()
    need(checks == {'dps4':4096,'strassen2':64},'ordered coefficient check count')
    cases.append({'name':'ordered block-stable coefficient identities','checked':checks})
    a,b,g = C.outer48_tables()
    changed = [row[:] for row in g]; changed[0][0] += 1
    bad_tensor = rejects(lambda:C.verify_ordered_tensor(4,a,b,changed,8),'ordered coefficient failure')
    cases.append({'name':'mutated actual outer coefficient rejected','rejection':bad_tensor})
    leaf_controls = [C.verify_paired_leaf(n) for n in (2,4,6,8,16)]
    need([x['gates'] for x in leaf_controls] == [7,46,141,316,2296],'leaf recipe counts')
    cases.append({'name':'complete mixed-input polynomial leaf identities','controls':leaf_controls})
    c16 = C.compose(('dps4',),C.terminal('rosowski_even',4),z)
    need(c16.order == 16 and c16.product_slots == 2208 and c16.denominator == 8,'selected synthesis count')
    need(c16.exact_output_quotients == 256 and not c16.bilinear,'integer late quotient scope')
    cases.append({'name':'actual 48-by-46 integral synthesis','candidate':c16.to_dict()})
    fake = replace(C.terminal('rosowski_even',4),products=45)
    bad_count = rejects(lambda:C.compose(('dps4',),fake,q),'validated recipe')
    cases.append({'name':'count without matching component validity rejected','rejection':bad_count})
    bad_rank = rejects(lambda:C.compose((),C.terminal('personal16',16),q,'bilinear_rank'),'tensor-rank')
    bad_recursion = rejects(lambda:C.fixed_leaf_recurrence('personal16',C.terminal('classical',1),q),'block-stable')
    cases.append({'name':'rank2208 and naive log16(2208) recurrence rejected',
                  'rank_rejection':bad_rank,'recurrence_rejection':bad_recursion,
                  'actual_noncommuting_block_counterexample_Z':noncommuting_leaf_counterexample(),
                  'actual_noncommuting_block_counterexample_GF2':noncommuting_leaf_counterexample(2)})
    recurrence = C.fixed_leaf_recurrence('dps4',C.terminal('rosowski_even',4),q)
    need(recurrence['arithmetic_product_exponent_expression'] == 'log(48)/log(4)','fixed terminal exponent')
    need(recurrence['product_sequence'] == 'C_t=46*48^t','fixed terminal cost sequence')
    bad_terminal_domain=rejects(lambda:C.fixed_leaf_recurrence('strassen2',C.terminal('personal16',16),g2),
                               'terminal denominator')
    integer_terminal=C.fixed_leaf_recurrence('strassen2',C.terminal('personal16',16),z)
    need(integer_terminal['denominator_sequence']=='D_t=8*1^t','terminal denominator disappeared from recurrence')
    cases.append({'name':'fixed terminal recurrence retains outer exponent and all domains',
                  'recurrence':recurrence,'GF2_terminal_denominator_rejection':bad_terminal_domain,
                  'integer_terminal_denominator_sequence':integer_terminal['denominator_sequence']})
    gf2_bad = rejects(lambda:C.compose(('dps4',),C.terminal('rosowski_even',4),g2),'nonunit')
    gf2_lift = C.compose(('dps4',),C.terminal('rosowski_even',4),g2,allow_charged_lift=True)
    need((gf2_lift.lifted_modulus,gf2_lift.target_word_bits,gf2_lift.lifted_word_bits)==(16,1,4),'charged lift width')
    need(gf2_lift.exact_output_quotients == 256,'lift exact quotients omitted')
    pure_lift=C.compose(('dps4',),C.terminal('classical',1),g2,allow_charged_lift=True)
    need(not pure_lift.bilinear and not pure_lift.block_stable,
         'lifted-ring numerator properties promoted to native GF2 rank/block metadata')
    billed=gf2_lift.to_dict()
    need(billed['scheduled_input_representative_lifts']==512 and
         billed['scheduled_final_target_reductions']==256,'lift/reduction work omitted')
    native_bad = rejects(lambda:C.compose(('dps4',),C.terminal('rosowski_even',4),g2,
                                          'native_field_products',True),'native field products')
    # Modulo2 alone the scaled output of zero and one is identical, so recovery is impossible.
    need((8*0)%2 == (8*1)%2 and 0%2 != 1%2,'information-loss counterexample')
    cases.append({'name':'GF2 direct denominator8 rejected; charged lift explicit',
                  'direct_rejection':gf2_bad,'native_model_rejection':native_bad,
                  'charged_candidate':gf2_lift.to_dict(),'unlifted_output_collision':[0,1]})
    lifted_checks = 0
    for denominator in (1,2,8,64):
        for modulus in (2,3,5,8):
            for output in range(-50,51):
                residue=(denominator*output)%(denominator*modulus)
                need(C.recover_lifted(residue,denominator,modulus)==output%modulus,'lifted quotient wrong')
                lifted_checks += 1
    invalid_image = rejects(lambda:C.recover_lifted(1,8,2),'scaled-image')
    cases.append({'name':'signed late modular quotient and image guard','checked':lifted_checks,
                  'bad_image_rejection':invalid_image})
    gf3 = C.compose(('dps4',),C.terminal('rosowski_even',4),g3,'native_field_products')
    need(gf3.product_slots == 2208 and gf3.lifted_modulus is None,'invertible denominator incorrectly lifted')
    cases.append({'name':'odd characteristic direct coefficient domain','candidate':gf3.to_dict()})
    f17,p17 = C.fringe(c16,17),C.padded(c16,17)
    need(f17.product_slots == 3025 and f17.exact_output_quotients == 256,'fringe arithmetic or quotient count')
    need(p17.product_slots == 17664 and p17.exact_output_quotients == 2048,'padding silently zero-pruned')
    need(C.fringe(c16,32).product_slots == 17664,'q-cubed fringe replacement')
    cases.append({'name':'arbitrary prime-order fringe and fully paid padding',
                  'fringe':f17.to_dict(),'padding':p17.to_dict(),
                  'cited_unreplayed_odd_W17_comparator':C.W(17),
                  'not_a_best_known_claim':True})
    q16 = C.factor_candidates(16,q)
    g16 = C.factor_candidates(16,g2,'native_field_products')
    rank16 = C.factor_candidates(16,q,'bilinear_rank')
    need(q16[0].product_slots == 2208,'eligible Q catalogue minimum')
    need(g16[0].product_slots == 2212,'eligible GF2 native catalogue minimum')
    need(rank16[0].product_slots == 2304 and all(x.bilinear for x in rank16),'rank model admitted mixed leaf')
    cases.append({'name':'model/domain-specific finite catalogue minima',
                  'Q_scheduled':2208,'GF2_native':2212,'Q_bilinear_upper_bound':2304,
                  'scope':'this supplied catalogue only; no global comparison'})
    # Fresh execution: seven exact Strassen block products, each using the
    # executable scalar order8 recipe (316 slots), produces2212 native GF2
    # products. The actual48x46 numerator is independently recovered via Z16.
    # Also replay multiple outer levels to check denominator composition.
    rng=Random(20261008); numeric_controls=[]
    routes=[(('strassen2',),'rosowski_even',8,2),
            (('dps4',),'rosowski_even',4,16),
            (('dps4','dps4'),'classical',1,128),
            (('dps4',),'rosowski_even',4,None)]
    for chain,recipe,b,modulus in routes:
        leaf=C.terminal(recipe,b); n=b
        for outer in chain: n*=C.catalogue()[outer].order
        for trial in range(4):
            A=[[rng.randint(-3,3) for _ in range(n)] for _ in range(n)]
            B=[[rng.randint(-3,3) for _ in range(n)] for _ in range(n)]
            raw=C.evaluate_numerator(chain,leaf,A,B,modulus)
            expected=[[sum(A[i][k]*B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
            den=raw['denominator'];num=raw['numerator']
            if modulus is None:
                need(num==[[den*v for v in row] for row in expected],'integral chain numerator mismatch')
            else:
                need(num==[[(den*v)%modulus for v in row] for row in expected],'modular chain numerator mismatch')
            need(raw['scheduled_product_slots']==leaf.products*math_product(C.catalogue()[name].products for name in chain),
                 'instrumented product count differs from typed candidate')
            if modulus==16:
                need([[C.recover_lifted(v,den,2) for v in row] for row in num]==
                     [[v%2 for v in row] for row in expected],'actual2208 GF2 lift recovery failed')
            numeric_controls.append({'chain':chain,'terminal':leaf.name,'order':n,
                'ring_modulus':modulus,'denominator':den,'actual_scheduled_products':raw['scheduled_product_slots'],
                'compared_scalar_outputs':n*n,'zero_intermediate_divisions':raw['intermediate_divisions']==0})
    cases.append({'name':'actual domain-aware hierarchical matrix execution','controls':numeric_controls})
    bad27 = rejects(lambda:C.compose(('advertised27',),C.terminal('classical',3),q),'absent')
    bad_field = rejects(lambda:C.Domain.parse('GF9'),'prime')
    cases.append({'name':'unreplayed advertised scheme and invalid field rejected',
                  'advertised27':bad27,'GF9':bad_field})
    gate = C.community_gate()
    need(not gate['complex_precision_only_implies_new_kappa'],'precision-to-kappa leap accepted')
    need(Fraction(gate['bit_saving'])<Fraction(gate['complex_saving']),'wrong binding profile')
    cases.append({'name':'community bit-profile/assembly eligibility gate','gate':gate})
    return {'status':'passed','case_groups':len(cases),'cases':cases,
            'source_commit':C.MATRIX_PIN,'proof_commit':C.PROOF_PIN,'community_commit':C.COMMUNITY_PIN,
            'tool_sha256':C.sha(HERE/'catalogue.py'),'audit_sha256':C.sha(__file__),
            'scope':'exact coefficient/polynomial and typed eligibility controls; not a Lean proof of this new tool',
            'remote_writes':False,'new_kappa_claim':False,'new_matrix_exponent_claim':False}


def math_product(values):
    result=1
    for value in values: result*=value
    return result


if __name__ == '__main__':
    result = audit()
    destination = Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'audit-receipt.json'
    # Never erase a prior evidence receipt silently.
    with destination.open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':result['status'],'case_groups':result['case_groups'],
                      'receipt':str(destination),'sha256':C.sha(destination)}))
