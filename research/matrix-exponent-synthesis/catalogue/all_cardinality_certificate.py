"""Fixed-a feasibility-slack assignment across ALL matching cardinalities.

For a fixed axis graph, R=R0-K, W=W0-rep*K. Complete-profile slack A-mW
changes by rep*sum[Delta F + m-F_h-F_(m-2h)]. Private dummies cost zero.
This certifies the quantized additive slack objective, not a ratio optimum,
global graph optimum, kappa theorem, or physical validity of a new candidate.
"""
from pathlib import Path
from fractions import Fraction as Q
import json, sys, time
import assignment_certificate as A

HERE=Path(__file__).resolve().parent


def verify(I,selected,u,v):
    rows=A.all_rows(I);nd,nc=I['nd'],I['nc']
    A.need(len(u)==nd and len(v)==nc and len(selected)==nd,'certificate shape')
    A.need(all(type(x)is int for x in u+v+selected),'integer certificate')
    A.need(len(set(selected))==nd and all(x<=0 for x in v),'injectivity/price sign')
    primal=0;constraints=0;used=set(selected)
    for i,row in enumerate(rows):
        costs=dict(row);A.need(selected[i] in costs,'illegal real/private dummy edge')
        primal+=costs[selected[i]]
        A.need(u[i]+v[selected[i]]==costs[selected[i]],'selected edge not tight')
        for j,c in row:A.need(u[i]+v[j]<=c,'dual inequality');constraints+=1
    A.need(all(v[j]==0 for j in range(nc) if j not in used),'unused price')
    dual=sum(u)+sum(v);A.need(primal==dual,'nonzero duality gap')
    return {'primal':primal,'dual':dual,'gap':0,'edge_inequalities':constraints,
            'selected_real_edges':sum(j<I['nu'] for j in selected),
            'cardinality_forced':False}


def run(edge_path,a,m=575,scale=10**12,supplied=None):
    I=A.parse_instance(edge_path,a,m,scale);h=I['h']
    lh,uh=A.power_weight_bounds(h,m,a);lr,ur=A.power_weight_bounds(m-2*h,m,a)
    clo,chi=m-uh-ur,m-lh-lr
    for e in I['edges']:
        e['lower']+=clo;e['upper']+=chi
        middle=(e['lower']+e['upper'])/2*scale
        e['q']=middle.numerator//middle.denominator
    minimum=min(0,min(e['q'] for e in I['edges']));offset=-minimum
    for e in I['edges']:e['cost']=e['q']+offset
    I['penalty']=offset # PRIVATE DUMMY ORIGINAL COST ZERO, same row offset.
    if supplied is None:
        selected=A.discover(I);u,v,relaxations=A.dual_potentials(I,selected)
    else:
        selected=supplied['selected_columns'];u=supplied['row_potentials'];v=supplied['column_potentials'];relaxations=0
    checked=verify(I,selected,u,v)
    lookup={(e['row'],e['column']):e for e in I['edges']}
    chosen=[lookup[i,col] for i,col in enumerate(selected) if col<I['nu']]
    quantized=checked['primal']-I['nd']*offset
    error_low=min([Q()]+[e['lower']-Q(e['q'],scale) for e in I['edges']])
    true_lower=Q(quantized,scale)+I['nd']*error_low
    chosen_lo=sum((e['lower'] for e in chosen),Q());chosen_hi=sum((e['upper'] for e in chosen),Q())
    regret=chosen_hi-true_lower;A.need(regret>=0,'reversed regret')
    return {'status':'all_cardinality_quantized_slack_optimum_certified',
        'edge_file_name':Path(edge_path).name,'edge_sha256':A.sha(edge_path),
        'exact_saving':str(a),'parent_width':m,'whole_axis_width':h,'scale':scale,
        'objective':'sum_e [Delta F_e + m - F_h - F_(m-2h)], F_t=t*exp(a*ln(m/t))',
        'complete_slack_identity':'(A-mW)=(A0-mW0)+axis_repeat*objective',
        'dummy_raw_cost':0,'uniform_every_row_offset':offset,
        'checked':checked,'selected_quantized_objective':quantized,
        'selected_true_objective_lower':str(chosen_lo),'selected_true_objective_upper':str(chosen_hi),
        'all_cardinality_true_objective_lower_bound':str(true_lower),
        'true_objective_regret_upper':str(regret),'regret_display':float(regret),
        'selected_columns':selected,'row_potentials':u,'column_potentials':v,
        'selected_carrier_pairs':[[e['donor'],e['use']] for e in chosen],
        'constraint_relaxations':relaxations,
        'scope':'fixed graph/fixed a feasibility slack over all cardinalities; not ratio, global graph or kappa optimality',
        'candidate_not_installed_or_submitted':True,
        'requires_complete_profile_and_physical_replay_before_new_witness':True}


if __name__=='__main__':
    path=HERE/'inputs/matching/h25-selected-edges.txt'
    if len(sys.argv)>1 and sys.argv[1]=='--verify':
        cert_path=Path(sys.argv[2]) if len(sys.argv)>2 else HERE/'all-cardinality-h25-certificate.json'
        c=json.loads(cert_path.read_text());A.need(A.sha(path)==c['edge_sha256'],'edge source hash mismatch')
        result=run(path,Q(c['exact_saving']),c['parent_width'],c['scale'],supplied=c)
        for key in result:
            if key!='constraint_relaxations':A.need(result[key]==c[key],f'certificate replay mismatch: {key}')
        print(json.dumps({'status':'independent_stdlib_all_cardinality_replay_passed',
            'checked':result['checked'],'regret_display':result['regret_display'],
            'certificate_sha256':A.sha(cert_path)},indent=2));sys.exit(0)
    result=run(path,Q('5155151733/125000000000000'))
    dest=HERE/'all-cardinality-h25-certificate.json'
    with dest.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:result[k] for k in ('status','exact_saving','checked','selected_quantized_objective',
        'regret_display','scope')},indent=2))
