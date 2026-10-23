"""Independent PR306 displayed finite invoice and rational absorption checks.
Upstream programs are only parsed as inert syntax and never executed.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
import ast, hashlib, json

def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(p): return json.loads(p.read_text())
def ceil(q): return -((-q.numerator)//q.denominator)
def serial(x):
    if isinstance(x,Q): return str(x)
    if isinstance(x,dict): return {str(k):serial(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)): return [serial(v) for v in x]
    return x

def compare_finite_ast(old,new):
    a=ast.parse(old); b=ast.parse(new)
    run=next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name=='run')
    extras=[n for n in run.body if isinstance(n,ast.Assert) and any(isinstance(t,ast.Constant) and t.value in ['reorder_transform','reorder2_transform'] for t in ast.walk(n))]
    assert len(extras)==2
    for n in extras: run.body.remove(n)
    assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
    formula='unit+J*high+J*(stock+24)+E*good+E*(128*N**3)+16*m**3+120*T+E+K+1'
    assignment=next(n for n in ast.walk(a) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='coefficient' for t in n.targets))
    assert ast.dump(assignment.value)==ast.dump(ast.parse(formula,mode='eval').body)
    return True

def source_audit(old,new,scalar,manifest,sourcepins):
    pins=manifest['files']
    assert pins['finite_check.py']==sha(new)
    spec=next(r for r in sourcepins['files'] if r['path']=='finite_check.py')
    assert hashlib.sha1(b'blob '+str(len(new)).encode()+b'\0'+new).hexdigest()==spec['git_blob']
    compare_finite_ast(old,new)
    assert sha(scalar.encode())==pins['scalar_check.py']
    assert 'norms[a]+=abs(c)*norms[b];largest=max(largest,norms[a])' in scalar
    return dict(pr305_finite_sha256=sha(old),pr306_finite_sha256=sha(new),pr306_finite_git_blob=spec['git_blob'],
        only_changes_two_reorder_assertions=True,displayed_coefficient_ast_identical=True,
        unchanged_scalar_recurrence_sha256=sha(scalar.encode()),source_execution=False)

def invoice(stock,calls,added,p,prior):
    keys=['scalar_events','literal_unit_additions','physical_R','normalizer_factor_bound','literal_stock','priced_five_stage_calls','conservative_extra_selector_calls']
    assert all(p[k]==prior[k] for k in keys)
    m=120;v=1760;R=p['physical_R'];T=60;N=240;d=m*m
    E=T*calls;weighted=T*(5*(p['scalar_events']+added)+6*v);unit=T*(5*(p['literal_unit_additions']+added)+6*v)
    J=T*(24*v+10*R);good=8*m*m+8;high=16*(d+1)**2
    K=600*((stock-1)+R*120*p['normalizer_factor_bound'])
    terms=dict(unit_additions=unit,high_affine=J*high,low_transposition=J*(stock+24),wrappers=E*good,
        matrix_preparation=E*128*N**3,fixed_matrix=16*m**3,copy_erase=120*T,children=E,selectors=K,constant=1)
    C=sum(terms.values())
    assert C<2**80 and 0<K<2**40 and stock+24<2**80 and 2*m**3*10**16<2**80
    return dict(literal_stock=stock,literal_children=E,gross_added_scalar_events_per_stage=added,
        weighted_additions_upper=weighted,unit_additions_upper=unit,route_families=J,normalizer_factor_bound=815,
        selector_calls_bound=K,coefficient_terms=terms,displayed_finite_coefficient=C,coefficient_bits=C.bit_length(),
        coefficient_cap=2**80,coefficient_cap_strict_gap=2**80-C,source_constants_unchanged=keys,
        omitted_reads_credit=False,primitive_full_constant_instantiated=False)

def bind(r,added,pins,prior_pins,receipt_sha256):
    bill=invoice(r['literal_stock'],r['calls'],added,pins,prior_pins)
    literal_mass=60*r['rank_mass'];assert 120*r['literal_stock']-literal_mass==264000
    c=Q(r['bit_root_bracket']['lower']);hi=Q(r['bit_root_bracket']['upper'])
    tau=1-Q(r['bit_root_bracket']['lower_moment'][1]);delta1=1-Q(literal_mass,120*r['literal_stock'])-Q(32*120*bill['literal_children'],10**16*r['literal_stock'])
    assert 0<c<hi<1 and tau>0 and delta1>0
    chain=list(map(Q,r['assembly']['bootstrap_chain']));assert chain[0]==Q(384599,10**10)
    gaps=[]
    for stage,(prior,a) in enumerate(zip(chain,chain[1:]),1):
        assert a==(1-c)*c+c*prior
        slacks=dict(atom=c-a,borrowing=1-a-c,remainder=1-a-c*(1-prior),stock=1-c)
        delta=min(slacks.values());assert delta>0 and prior<a<c<1-a
        C=bill['displayed_finite_coefficient']; cutoff=max(1,ceil(36/delta**2),ceil(Q(2*(4+(C-1).bit_length()))/delta))
        assert cutoff*delta**2>=36 and cutoff*delta>=2*(4+(C-1).bit_length())
        gaps.append(dict(stage=stage,slacks=slacks,minimum=delta,displayed_coefficient_cutoff_log2=cutoff))
    assert len(gaps)==3
    bill.update(priced_receipt_sha256=receipt_sha256,coarse=c,coarse_decimal=str(float(c)),literal_rank_mass=literal_mass,
        delta_tau_lower=tau,delta_linear=delta1,bootstrap_gap_checks=gaps,
        cutoff_scope='Displayed fixed bill only. Full primitive, wrapper, setup and previous ordinary-level constants remain inherited and uninstantiated.')
    return bill

def run(config):
    old=Path(config['old_source']);new=Path(config['new_source']);pricing=Path(config['pricing_dir']);out=Path(config['output_dir'])
    audit=source_audit((old/'finite_check.py.txt').read_bytes(),(new/'finite_check.py.txt').read_bytes(),
        (old/'cap_sources/scalar_check.py.txt').read_text(),load(new/'MANIFEST.json'),load(Path(config['new_input_manifest'])))
    pins=load(new/'expected/kernel-pins.json');prior_pins=load(old/'expected/kernel-pins.json')
    def priced(name,added):
        path=pricing/name;return bind(load(path),added,pins,prior_pins,sha(path.read_bytes()))
    baseline=priced('baseline-receipt.json',0);candidate=priced('combined156-provisional-receipt.json',5090)

    assert candidate['displayed_finite_coefficient']==90417469526202901
    previous_path=Path(config['prior_case'])
    previous=load(previous_path)
    witness_path=Path(config['witness']); witness=load(witness_path)
    witness_sha=sha(witness_path.read_bytes())
    assert witness_sha==previous['candidate_sha256']=='aaf9eb2f324c05dc534ecb047f70724042d6c0515e6ae9c8440bbcc2ca6f3ba1'
    assert len(witness['entries'])==156 and sum(len(e['donors']) for e in witness['entries'])==2545
    assert baseline['displayed_finite_coefficient']==previous['finite_arithmetic']['baseline_displayed_coefficient']
    assert candidate['displayed_finite_coefficient']==previous['finite_arithmetic']['displayed_finite_coefficient']
    chart=previous['changed_charts']; assert chart['charts']==281 and chart['combined_normalizer_factor_bound']==815
    assert chart['selector_calls_bound']==candidate['selector_calls_bound']
    candidate.update(candidate_sha256=witness_sha,chart_transport=dict(status='CONDITIONAL_PENDING_REORDER_COMPOSITION',
        prior_case156_receipt_sha256=sha(previous_path.read_bytes()),prior_chart_receipt_sha256=previous['changed_chart_receipt_sha256'],
        charts=281,prior_max_chart_factors=chart['max_changed_chart_factors'],normalizer_bound=815,
        required_bridge='All selected first required frames, entrances, residual endpoints and role-bank census remain unchanged. Reordered interior gate frames still require the inherited admissible-chart/compiler contract.'))
    freshchart_path=out/'chart-transport-inputs.json'; freshchart=load(freshchart_path)
    assert freshchart['candidate_sha256']==witness_sha and freshchart['exact_factor_programs_replayed']==281
    candidate['chart_transport'].update(fresh_transport_receipt_sha256=sha(freshchart_path.read_bytes()),exact_inverse_factor_programs_replayed=281,all706_demand_inputs_unchanged=True,baseline306_interior_frame_admission_still_required=True)
    report=dict(status='PASS_DISPLAYED_FINITE_ARITHMETIC_UNDER_CHANGED_PROFILE',source_head='0314371983b8837f01723f5af2c70217f75b01cc',source_audit=audit,
        baseline=baseline,candidate156=candidate,scalar_transport='Algebraic lemma established; concrete moved-interval admission to be supplied by separate bridge.',
        physical_admission=False,all_size_theorem=False,candidate_composition_verified=False)
    out.mkdir(parents=True,exist_ok=True)
    (out/'finite-review.json').write_text(json.dumps(serial(report),indent=2)+'\n')
    print(json.dumps(dict(baseline_coefficient=baseline['displayed_finite_coefficient'],candidate156_coefficient=candidate['displayed_finite_coefficient'],
        baseline_cutoffs=[x['displayed_coefficient_cutoff_log2'] for x in baseline['bootstrap_gap_checks']],
        candidate156_cutoffs=[x['displayed_coefficient_cutoff_log2'] for x in candidate['bootstrap_gap_checks']]),indent=2))
    return serial(report)
if __name__=='__main__':
    import argparse
    if not __debug__: raise RuntimeError('Assertions required')
    parser=argparse.ArgumentParser();parser.add_argument('--config',type=Path,required=True)
    run(load(parser.parse_args().config))
