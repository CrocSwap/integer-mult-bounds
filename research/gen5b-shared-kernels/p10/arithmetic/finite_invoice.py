"""Original finite ring/recipe invoice formula, pinned PR320 m100/N200 contract.
The caller supplies measured inventory and scalar counts. No admission is inferred.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import hashlib,json
import reproduce_p10 as b

def bill(stock,calls,local_weighted,local_units,R=8223,chart_max=400):
    m=100;N=2*m;d=m*m;T=60;v=960;h=20
    E=T*calls;J=T*(24*v+10*R);normalizer=chart_max+(m-1)+m
    weighted=T*(5*local_weighted+6*v);unit=T*(5*local_units+6*v)
    K=2*5*T*((stock-1)+R*m*normalizer)
    terms=dict(unit_expanded_additions=unit,high_affine_factors=J*16*(d+1)**2,
        low_transpositions=J*(stock+h),generic_wrappers=E*(8*m*m+8),
        matrix_preparation=E*128*N**3,global_matrix_preparation=16*m**3,
        copy_erase_episodes=5*h*T,paid_child_overhead=E,bank_selectors=K,constant=1)
    return dict(m=m,N=N,d=d,replicas=T,h=h,v=v,R=R,stock=stock,literal_paid_children=E,
        local_weighted_additions=local_weighted,local_unit_additions=local_units,
        weighted_additions=weighted,route_families=J,chart_factor_bound=chart_max,
        normalizer_factor_bound=normalizer,coefficient_terms=terms,coefficient=sum(terms.values()),
        fallback_per_child=32*m*m,fallback_generic_count=6*N*(N-1)+3*N+6*(N-1),
        internal_row_coefficient=d+1,external_complex_row_coefficient=20161)


def run():
    finite=b.read('finite_check.py');bank=b.read('bank_check.py');pins=b.pins()
    path=b.HERE/'candidate15-pricing.json';raw=path.read_bytes();candidate=json.loads(raw)
    baseline=bill(pins['literal_stock'],pins['banked_calls'],pins['weighted_scalar_events'],pins['literal_unit_additions'])
    assert baseline['coefficient']==pins['finite_coefficient']==25419835642718201
    assert baseline['coefficient_terms']['bank_selectors']==pins['extra_selector_calls']
    assert baseline['normalizer_factor_bound']==pins['normalizer_factor_bound']==599
    gross_adds=80;charge=bill(candidate['literal_stock'],candidate['banked_calls'],pins['weighted_scalar_events']+gross_adds,pins['literal_unit_additions']+gross_adds)
    assert charge['coefficient']<2**80 and 0<charge['coefficient_terms']['bank_selectors']<2**40
    assert charge['fallback_generic_count']<charge['fallback_per_child']
    delta={k:v-baseline['coefficient_terms'][k] for k,v in charge['coefficient_terms'].items()}
    assert delta['unit_expanded_additions']==60*5*80==24000
    payload=64*pins['forward_max_row_l1']**3*pins['inverse_max_row_l1']**2
    return dict(status='CONDITIONAL_INVOICE_NOT_PHYSICAL_FINITE_ADMISSION',source_head=b.HEAD,physical_admission=False,
        candidate_input=dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)),
        gross_added_unit_ADDs_per_local_stage=80,gross_added_unit_ADDs_all_replicas_and_stages=24000,
        removed_read_credit=0,baseline=baseline,candidate_conditional=charge,
        coefficient_term_deltas=delta,coefficient_delta=charge['coefficient']-baseline['coefficient'],
        inherited_payload_envelope=dict(forward_row_l1=pins['forward_max_row_l1'],inverse_row_l1=pins['inverse_max_row_l1'],payload_bound=payload,payload_bits=payload.bit_length(),required_strict_upper='2^104',validated_for_candidate=False),
        pending_obligations=[
            'All 80 added scalar operations have unit expansion cost at most one each; any larger/rational coefficient requires its actual expansion bill.',
            'All changed entrance/residual charts are nonsingular, exact, correctly embedded, with factor numerators and denominators below 2^80.',
            'Candidate maximum chart factor count is at most 400, hence the retained normalizer factor bound599 applies; otherwise recompute the selector term.',
            'Forward and inverse literal row-norm maxima remain within31433 and966260, or a replacement certified payload envelope below2^104 is supplied. No candidate norm replay is claimed here.',
            'Fresh physical chronology, operand source spans, frame nesting, all-column scalar replays, completion discharge and role-to-bank address binding are supplied.',
            'Prime-factor obligations, selector/routing/row-reserve/precision/recovery hypotheses and the retained common weighted chart/compiler interfaces remain conditional.'
        ],scope='Concrete arithmetic of the pinned finite formula with a conservative gross ADD overcharge. No physical finite admission follows until pending bounds and bridge obligations are checked.')
