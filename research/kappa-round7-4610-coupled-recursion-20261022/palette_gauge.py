"""Actual chart-mask palette {0, first unit, last unit, all active axes}.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
MILP proposes finite reference choices; exact costs/moments are replayed.
"""
from collections import Counter,defaultdict
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys
import time
import mixed_gauge as M
import weighted_gauge as W
import realification_census as R

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'.solver/local'))
import highspy
import numpy as np


def options(ce,c,frame,ell,cache):
    basis=tuple(c['frames'][frame]);r=len(basis)
    if basis not in cache:cache[basis]=R.frame_data(ce,basis)
    F,square,K=cache[basis]
    normal=R.tensor_columns(R.tabcols(F),ell)
    active=[9*j+i for j in range(ell) for i in range(r)]
    masks=list(dict.fromkeys([0]+([1<<active[0],1<<active[-1],sum(1<<i for i in active)] if active else [])))
    chart=R.tensor_columns(R.tabcols(K),ell)
    columns=[];paulis=[]
    for mask in masks:
        w=R.action(chart,mask)
        actual=R.transvection(normal,w) if mask else normal
        R.need(R.compose(actual,actual)==tuple(1<<i for i in range(18*ell)),'Palette inverse is symplectically involutive only')
        columns.append(actual);paulis.append(w)
    return dict(masks=masks,columns=columns,pauli_vectors=paulis)


def cost_tables(ce,g,ell,framecache,option_provider=options):
    c=g['canonical'];ops={frame:option_provider(ce,c,frame,ell,framecache) for frame in set(g['component_frames'].values())}
    warps={w['op']:R.Kop(ce,w['G_columns']) for w in c['warps']};kt={}
    terms=[];costcache={}
    for item in g['edges']+g['helpers']:
        helper='role' in item;a,b=item['source_frame'],item['target_frame'];op=item.get('operator',0)
        key=a,b,op
        if key not in costcache:
            if op and op not in kt:
                body=warps[abs(op)] if op>0 else warps[abs(op)].adjoint()
                kt[op]=R.tensor_columns(R.tabcols(body),ell)
            costs=[]
            for source in ops[a]['columns']:
                row=[]
                for target in ops[b]['columns']:
                    product=R.compose(target,R.compose(kt[op],source)) if op else R.compose(target,source)
                    row.append(R.f_rank(ce,product))
                costs.append(row)
            costcache[key]=costs
        costs=costcache[key]
        old=ell*(len(c['frames'][b])-len(c['frames'][a])) if helper else ell*item['old_rank']
        R.need(costs[0][0]==old,'Original native cost in every full palette table')
        terms.append({**item,'kind':'helper' if helper else item['kind'],'costs':costs})
    count=[len(ops[g['component_frames'][i]]['masks']) for i in range(g['components'])]
    metadata={str(f):{k:v for k,v in info.items() if k!='columns'} for f,info in ops.items()}
    return terms,count,metadata


def solve(terms,counts,fixed,weights,seconds):
    fixed=set(fixed);unary=[[0]*count for count in counts];pairs={};constant=0
    for e in terms:
        a,b=e['source'],e['target'];sgn=-1 if e['kind']=='helper' else 1
        costs=[[sgn*weights[r] for r in row] for row in e['costs']]
        if a==b:
            for x in range(counts[a]):unary[a][x]+=costs[x][x]
        elif a in fixed and b in fixed:constant+=costs[0][0]
        elif a in fixed:
            for y in range(counts[b]):unary[b][y]+=costs[0][y]
        elif b in fixed:
            for x in range(counts[a]):unary[a][x]+=costs[x][0]
        else:
            if a>b:a,b=b,a;costs=list(map(list,zip(*costs)))
            if (a,b) not in pairs:pairs[a,b]=[[0]*counts[b] for _ in range(counts[a])]
            for x in range(counts[a]):
                for y in range(counts[b]):pairs[a,b][x][y]+=costs[x][y]
    active=sorted((set(i for pair in pairs for i in pair)|{i for i,row in enumerate(unary) if any(v!=row[0] for v in row)})-fixed)
    h=highspy.Highs()
    for key,v in [('output_flag',False),('threads',1),('time_limit',seconds),('mip_rel_gap',0.0),('mip_abs_gap',1e-10)]:h.setOptionValue(key,v)
    variables={};warm=[]
    for i in active:
        variables[i]=[h.addVariable(lb=0,ub=1,obj=float(value/W.SCALE),type=highspy.HighsVarType.kInteger,name=f'x{i}_{x}') for x,value in enumerate(unary[i])]
        h.addConstr(sum(variables[i])==1);warm.extend([1.0]+[0.0]*(counts[i]-1))
    for (a,b),cost in pairs.items():
        z=[[h.addVariable(lb=0,ub=1,obj=float(cost[x][y]/W.SCALE),name=f'z{a}_{b}_{x}_{y}')
            for y in range(counts[b])] for x in range(counts[a])]
        for x in range(counts[a]):h.addConstr(sum(z[x])==variables[a][x])
        for y in range(counts[b]):h.addConstr(sum(z[x][y] for x in range(counts[a]))==variables[b][y])
        warm.extend(float(x==y==0) for x in range(counts[a]) for y in range(counts[b]))
    h.setSolution(len(warm),np.arange(len(warm),dtype=np.int32),np.array(warm,dtype=np.float64))
    h.run();info=h.getInfo();values=h.getSolution().col_value
    assignment=[0]*len(counts)
    for i,vs in variables.items():
        selected=[x for x,v in enumerate(vs) if values[v.index]>.5]
        R.need(len(selected)==1,'One exact discrete palette choice per component')
        assignment[i]=selected[0]
    R.need(all(assignment[i]==0 for i in fixed),'Actual fixed ownership and main endpoints')
    integer=constant+sum(unary[i][assignment[i]] for i in active)+sum(cost[assignment[a]][assignment[b]] for (a,b),cost in pairs.items())
    # Unary rows excluded from the model are constant across all their options.
    integer+=sum(row[0] for i,row in enumerate(unary) if i not in active)
    exact=sum((-1 if e['kind']=='helper' else 1)*weights[e['costs'][assignment[e['source']]][assignment[e['target']]]] for e in terms)
    R.need(integer==exact,'Exact aggregate and original-term objective agreement')
    return assignment,dict(status=str(h.getModelStatus()),nodes=info.mip_node_count,gap=info.mip_gap,
                           objective=info.objective_function_value,dual_bound=info.mip_dual_bound,
                           onehot_components=len(active),pair_transport_tables=len(pairs),variables=h.getNumCol(),
                           constraints=h.getNumRow(),exact_quantized_objective=exact)


def profile(terms,assignment):
    paid=Counter();helpers=Counter()
    for e in terms:
        rank=e['costs'][assignment[e['source']]][assignment[e['target']]]
        (helpers if e['kind']=='helper' else paid)[rank]+=1
    return paid,helpers


def validate_assignment(assignment,counts,fixed):
    R.need(len(assignment)==len(counts),'Exactly one option per contact component')
    R.need(all(type(x) is int and 0<=x<count for x,count in zip(assignment,counts)),
           'Every assigned option belongs to its actual frame domain')
    R.need(all(assignment[i]==0 for i in fixed),'Owned/main endpoint choice is fixed')


def replay_native_prices(ce,g,ell,terms,assignment,framecache,option_provider=options):
    """Rebuild selected native products instead of trusting serialized tables."""
    c=g['canonical'];ops={frame:option_provider(ce,c,frame,ell,framecache)
                         for frame in set(g['component_frames'].values())}
    bodies={w['op']:R.Kop(ce,w['G_columns']) for w in c['warps']}
    cache={};chosen=[]
    for e in terms:
        a,b=e['source_frame'],e['target_frame'];x,y=assignment[e['source']],assignment[e['target']]
        op=e.get('operator',0);key=a,b,x,y,op
        if key not in cache:
            left,right=ops[a]['columns'][x],ops[b]['columns'][y]
            if op:
                body=bodies[abs(op)] if op>0 else bodies[abs(op)].adjoint()
                middle=R.tensor_columns(R.tabcols(body),ell)
                relative=R.compose(right,R.compose(middle,left))
            else:relative=R.compose(right,left)
            cache[key]=R.f_rank(ce,relative)
        rank=cache[key]
        R.need(rank==e['costs'][x][y],'Chosen native Fourier rank must equal serialized price')
        chosen.append(rank)
    return dict(terms=len(chosen),distinct_native_products=len(cache),
                selected_rank_sha256=sha256(json.dumps(chosen,separators=(',',':')).encode()).hexdigest())


def expect_rejection(call,message):
    try:call()
    except ValueError:return dict(rejected=True,reason=message)
    raise ValueError('Negative control was accepted: '+message)


def phase_control(ce):
    # Full frame, first-unit mask: A^2 is translation by axes1,...,8.
    A=ce.fourier(9).then(ce.cgate(9,1))
    correct=A.adjoint().then(A);wrong=A.then(A)
    R.need(correct.tab==ce.ident(9).tab and correct.zero_state()==ce.ident(9).zero_state(),'Actual adjoint roundtrip')
    R.need(wrong.tab!=correct.tab and wrong.zero_state()!=correct.zero_state(),'Wrong literal inverse is semantically rejected')
    return dict(name='using_symplectic_involution_as_literal_inverse',rejected=True,
                reason='A^2 is nontrivial Pauli translation, while A^dagger A is identity; both have symplectic identity.',
                wrong_zero_output_address=next(i for i,x in enumerate(wrong.zero_state()[0]) if x!=(0,0)))


def chart_control(ce,g,cache):
    # Every palette option of one actual frame per rank is built literally;
    # exact Pauli signs are retained in the circuit and its true adjoint.
    c=g['canonical'];representatives={}
    for frame in sorted(set(g['component_frames'].values())):
        representatives.setdefault(len(c['frames'][frame]),frame)
    checks=0
    for frame in representatives.values():
        basis=tuple(c['frames'][frame]);r=len(basis)
        if basis not in cache:cache[basis]=R.frame_data(ce,basis)
        F,square,K=cache[basis];info=options(ce,c,frame,1,cache)
        for mask,columns in zip(info['masks'],info['columns']):
            A=K.adjoint().then(ce.fourier(9,range(r))).then(ce.cgate(9,mask)).then(K)
            R.need(R.tabcols(A)==columns,'Literal actual chart circuit matches rank-only symplectic columns')
            identity=A.adjoint().then(A)
            R.need(identity.tab==ce.ident(9).tab and identity.zero_state()==ce.ident(9).zero_state(),
                   'Literal actual chart circuit uses the actual adjoint and global phase')
            checks+=1
    return dict(name='literal_chart_circuit_representatives',ranks=sorted(representatives),checks=checks,
                passed=True,scope='One actual frame per represented rank, ell=1; no 27-axis state-vector claim.')


def main():
    began=time.monotonic();pins=R.read(HERE/'SOURCES.json')
    for row in pins['files']:R.need(sha256((HERE/row['copy']).read_bytes()).hexdigest()==row['sha256'],'Pinned actual input')
    ce=R.load(HERE/'sources'/R.CE,'palette_actual_clifford')
    payload=R.read(HERE/'sources/research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz')
    g=M.graph(payload);cache={};rows=[]
    for ell in (1,3):
        terms,counts,metadata=cost_tables(ce,g,ell,cache)
        bounds={r:W.rank_power(r) for r in range(9*ell+1)}
        weights={r:int((a+b)*W.SCALE/2+W.Q(1,2)) for r,(a,b) in bounds.items()}
        before=W.net_profile(terms,[0]*g['components']);cases=[]
        for boundary,fixed in [('strict',g['strict_fixed']),('helper_free_optimistic',g['base_fixed'])]:
            assignment,solver=solve(terms,counts,fixed,weights,120)
            validate_assignment(assignment,counts,fixed)
            native_replay=replay_native_prices(ce,g,ell,terms,assignment,cache)
            after=W.net_profile(terms,assignment);lo,hi=W.gain_bounds(before,after,bounds)
            paid,helpers=profile(terms,assignment)
            row=dict(boundary=boundary,solver=solver,assignment=assignment,changed_components=sum(x!=0 for x in assignment),
                     moment_gain_lower=str(lo),moment_gain_upper=str(hi),genuine_positive_finite_moment=lo>0,
                     local_deficit=R.mass(paid)-R.mass(helpers)-1792*ell,
                     paid_profile=R.counter_data(paid),helper_profile=R.counter_data(helpers),
                     net_profile_delta={str(r):after[r]-before[r] for r in sorted(set(before)|set(after)) if after[r]!=before[r]},
                     native_replay=native_replay)
            cases.append(row)
            print('PASS_PALETTE_CANDIDATE_REPLAY',ell,boundary,solver['status'],'changed',row['changed_components'],
                  'gain',float(lo),float(hi),'deficit',row['local_deficit'],'elapsed',round(time.monotonic()-began,2),flush=True)
        rows.append(dict(ell=ell,option_counts=counts,frame_options=metadata,terms=terms,cases=cases))
    controls=[phase_control(ce),chart_control(ce,g,cache)]
    # Ownership is an explicit hard constraint, not an objective surcharge.
    zero=[0]*g['components'];bad=zero[:]
    fixed_with_choice=next(i for i in g['base_fixed'] if counts[i]>1)
    bad[fixed_with_choice]=1
    controls.append(dict(name='owned_or_main_fixed_choice_mutation',component=fixed_with_choice,
                         **expect_rejection(lambda:validate_assignment(bad,counts,g['base_fixed']),
                                            'Nonzero option at a fixed actual endpoint')))
    wrong=[{**e,'costs':[row[:] for row in e['costs']]} for e in terms]
    wrong[0]['costs'][0][0]+=1
    controls.append(dict(name='chosen_native_price_mutation',event=wrong[0].get('event'),
                         **expect_rejection(lambda:replay_native_prices(ce,g,ell,wrong,zero,cache),
                                            'One stored paid price disagrees with rebuilt actual product')))
    result=dict(status='PASS_ACTUAL_FOUR_MASK_PALETTE_SEARCH_AND_ASSIGNMENT_REPLAY',kappa=str(W.KAPPA),
                source_manifest_sha256=sha256((HERE/'SOURCES.json').read_bytes()).hexdigest(),
                script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                helper_script_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in [HERE/'mixed_gauge.py',HERE/'weighted_gauge.py',HERE/'realification_census.py']},
                results=rows,controls=controls,new_kappa=False,
                solver='HiGHS 1.15.1 floating MIP status is scoped evidence, not a mathematical optimality certificate.',
                scope='Actual changed frame choices with complete paid/warp ranks and helper endpoint rewards. Positive finite weighted rank evidence is not an admitted recursive supplier; exact absolute-phase lowering, restored reservations and all-f residual job types still require integration.',
                seconds=time.monotonic()-began)
    (HERE/'PALETTE-GAUGE.json.gz').write_bytes(gzip.compress(json.dumps(result,sort_keys=True,separators=(',',':')).encode(),mtime=0))


if __name__=='__main__':main()
