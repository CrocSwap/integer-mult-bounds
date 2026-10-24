"""Independent replay of every all-unit table and accepted assignment.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
No optimizer is run; numerical optimality is not promoted to a theorem.
"""
import ast
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
CORE=HERE.parent
sys.path.insert(0,str(CORE))
import freeze as Z
import realification_census as R
import mixed_gauge as M
import weighted_gauge as W


def pure_functions(path,names):
    """Load only byte-pinned pure functions; do not import discovery's solver."""
    tree=ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    R.need({n.name for n in nodes}==set(names),'Exact named pure helper functions exist')
    namespace={'R':R,'Counter':Counter,'sha256':sha256,'json':json}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),namespace)
    return SimpleNamespace(**{name:namespace[name] for name in names})


def main():
    frozen=R.read(CORE/'FREEZE.json');R.need(Z.audit()==frozen,'Unchanged completed core')
    r=R.read(HERE/'ALL-UNITS.json.gz');related=R.read(HERE/'RELATED.json')
    R.need(r['script_sha256']==sha256((HERE/'all_units.py').read_bytes()).hexdigest(),'Discovery script pin')
    R.need(r['core_freeze_sha256']==sha256((CORE/'FREEZE.json').read_bytes()).hexdigest(),'Exact old source closure')
    R.need(r['related_sha256']==sha256((HERE/'RELATED.json').read_bytes()).hexdigest(),'Exact reviewed related scope')
    for pin in related['files']:R.need(sha256((HERE/pin['copy']).read_bytes()).hexdigest()==pin['sha256'],'Compared source pin')
    P=pure_functions(CORE/'palette_gauge.py',[
        'options','cost_tables','profile','validate_assignment','replay_native_prices','expect_rejection','phase_control'])
    A=pure_functions(HERE/'all_units.py',['options'])
    ce=R.load(CORE/'sources'/R.CE,'all_unit_replay_clifford')
    payload=R.read(CORE/'sources/research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz')
    g=M.graph(payload);cache={}
    terms,counts,metadata=P.cost_tables(ce,g,1,cache,option_provider=A.options)
    R.need(terms==r['terms'] and counts==r['option_counts'] and metadata==r['frame_options'],
           'All serialized tables equal independently rebuilt actual products')
    zero=[0]*g['components'];before=W.net_profile(terms,zero)
    bounds={rank:W.rank_power(rank) for rank in range(10)}
    for case in r['cases']:
        fixed=g['strict_fixed'] if case['boundary']=='strict' else g['base_fixed']
        chosen=case['assignment'];P.validate_assignment(chosen,counts,fixed)
        native=P.replay_native_prices(ce,g,1,terms,chosen,cache,option_provider=A.options)
        R.need(native==case['native_replay'],'Chosen exact native products match receipt')
        paid,helpers=P.profile(terms,chosen)
        R.need(R.counter_data(paid)==case['paid_profile'] and R.counter_data(helpers)==case['helper_profile'],'Complete invoice replay')
        lo,hi=W.gain_bounds(before,W.net_profile(terms,chosen),bounds)
        R.need(str(lo)==case['moment_gain_lower'] and str(hi)==case['moment_gain_upper'],'Rational moment intervals')
        R.need(case['changed_components']==0 and lo==hi==0 and case['local_deficit']==64,'Actual bounded negative candidate')
    bad=zero[:];i=next(i for i in g['base_fixed'] if counts[i]>1);bad[i]=1
    controls=[dict(name='fixed_endpoint_option',**P.expect_rejection(lambda:P.validate_assignment(bad,counts,g['base_fixed']),
                                                                  'An actual fixed endpoint changed'))]
    wrong=[{**e,'costs':[row[:] for row in e['costs']]} for e in terms]
    wrong[0]['costs'][0][0]+=1
    controls.append(dict(name='stored_paid_price',**P.expect_rejection(
        lambda:P.replay_native_prices(ce,g,1,wrong,zero,cache,option_provider=A.options),'Stored price differs from actual native rank')))
    representatives={}
    for f in sorted(set(g['component_frames'].values())):representatives.setdefault(len(g['canonical']['frames'][f]),f)
    literal_checks=0
    for rank,frame in representatives.items():
        basis=tuple(g['canonical']['frames'][frame]);F,square,K=cache[basis]
        info=A.options(ce,g['canonical'],frame,1,cache)
        for mask,columns in zip(info['masks'],info['columns']):
            op=K.adjoint().then(ce.fourier(9,range(rank))).then(ce.cgate(9,mask)).then(K)
            R.need(R.tabcols(op)==columns,'Every sampled literal chart option matches the exact tableau')
            back=op.adjoint().then(op)
            R.need(back.tab==ce.ident(9).tab and back.zero_state()==ce.ident(9).zero_state(),'Actual phase and true adjoint cancellation')
            literal_checks+=1
    controls.append(P.phase_control(ce))
    out=dict(status='PASS_ALL_ACTIVE_UNIT_TABLE_AND_ASSIGNMENT_REPLAY',components=g['components'],
             terms=len(terms),cases=len(r['cases']),literal_representative_checks=literal_checks,
             controls=controls,receipt_sha256=sha256((HERE/'ALL-UNITS.json.gz').read_bytes()).hexdigest(),
             script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),new_kappa=False,
             scope='Exact finite invoice validation only; no rerun or formal certificate of floating MIP optimality.')
    (HERE/'VERIFY.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(out['status'],'components',out['components'],'terms',out['terms'],'cases',out['cases'],'literal checks',literal_checks)


if __name__=='__main__':main()
