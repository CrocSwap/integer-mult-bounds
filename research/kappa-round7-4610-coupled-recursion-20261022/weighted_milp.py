"""Scoped HiGHS search and exact candidate replay for the weighted graph.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
The floating solver proposes assignments; rational intervals assess gains.
"""
from collections import Counter,defaultdict
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys
import time
import weighted_gauge as W
import mixed_gauge as M

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'.solver/local'))
import highspy
import numpy as np


def solve(terms,n,fixed,seconds):
    fixed=set(fixed);unary=[0]*n;pairs=defaultdict(int);constant=0
    for e in terms:
        a,b=e['source'],e['target'];sgn=-1 if e['kind']=='helper' else 1
        v00,v01,v10,v11=[sgn*v for row in e['costs'] for v in row]
        constant+=v00
        if a==b:unary[a]+=v11-v00
        else:
            unary[a]+=v10-v00;unary[b]+=v01-v00
            pairs[tuple(sorted((a,b)))]+=v11-v10-v01+v00
    pairs={ab:w for ab,w in pairs.items() if w and not(fixed&set(ab))}
    involved=set(i for i,u in enumerate(unary) if u and i not in fixed)|{i for ab in pairs for i in ab}
    h=highspy.Highs()
    for key,v in [('output_flag',False),('threads',1),('time_limit',seconds),('mip_rel_gap',0.0),('mip_abs_gap',1e-11)]:h.setOptionValue(key,v)
    x={i:h.addVariable(lb=0,ub=1,obj=float(unary[i]/W.SCALE),type=highspy.HighsVarType.kInteger,name='x'+str(i)) for i in sorted(involved)}
    for (a,b),weight in sorted(pairs.items()):
        y=h.addVariable(lb=0,ub=1,obj=float(weight/W.SCALE),name='y'+str(a)+'_'+str(b))
        h.addConstr(y<=x[a]);h.addConstr(y<=x[b]);h.addConstr(y>=x[a]+x[b]-1)
    count=h.getNumCol()
    h.setSolution(count,np.arange(count,dtype=np.int32),np.zeros(count,dtype=np.float64))
    h.run();status=h.getModelStatus();info=h.getInfo();solution=h.getSolution()
    modes=[0]*n
    for i,var in x.items():
        v=solution.col_value[var.index]
        M.R.need(abs(v-round(v))<1e-6,'Integral proposed gauge')
        modes[i]=int(round(v))
    M.R.need(all(modes[i]==0 for i in fixed),'Pinned gauges remain old')
    linear=sum(unary[i]*modes[i] for i in range(n))+sum(w*modes[a]*modes[b] for (a,b),w in pairs.items())
    M.R.need(M.value(terms,modes)==constant+linear,'Exact binary product replay')
    return modes,dict(status=str(status),solver_objective_change=info.objective_function_value,
                      solver_dual_bound=info.mip_dual_bound,solver_gap=info.mip_gap,
                      mip_nodes=info.mip_node_count,active_gauge_variables=len(x),product_variables=len(pairs),
                      exact_quantized_objective_change=linear,quantized_scale=W.SCALE,
                      floating_status_is_not_mathematical_optimality_certificate=True)


def main():
    began=time.monotonic();graph=M.R.read(HERE/'MIXED-GAUGE.json.gz')
    setup=M.R.read(HERE/'WEIGHTED-GAUGE.json.gz')
    M.R.need(setup['graph_sha256']==sha256((HERE/'MIXED-GAUGE.json.gz').read_bytes()).hexdigest(),'Weighted setup binds actual graph')
    bounds={int(r):tuple(map(W.Q,ab)) for r,ab in setup['rank_power_bounds'].items()}
    weights={r:int((a+b)*W.SCALE/2+W.Q(1,2)) for r,(a,b) in bounds.items()}
    rows=[]
    for data in graph['results']:
        terms=[{**e,'costs':[[weights[r] for r in row] for row in e['costs']]} for e in data['terms']]
        cases=[]
        for boundary,fixed in [('strict',graph['strict_fixed']),('helper_free_optimistic',graph['base_fixed'])]:
            modes,solver=solve(terms,graph['components'],fixed,120)
            before=W.net_profile(data['terms'],[0]*graph['components']);after=W.net_profile(data['terms'],modes)
            lower,upper=W.gain_bounds(before,after,bounds)
            delta={str(r):after[r]-before[r] for r in sorted(set(before)|set(after)) if after[r]!=before[r]}
            profile={kind:Counter() for kind in ['helper','paid']}
            for e in data['terms']:
                r=e['costs'][modes[e['source']]][modes[e['target']]]
                profile['helper' if e['kind']=='helper' else 'paid'][r]+=1
            row=dict(boundary=boundary,solver=solver,modes=modes,changed_components=sum(modes),
                     moment_gain_lower=str(lower),moment_gain_upper=str(upper),genuine_positive_finite_moment=lower>0,
                     net_profile_delta=delta,local_deficit=sum(r*v for r,v in after.items())-1792*data['ell'],
                     paid_profile={str(r):v for r,v in sorted(profile['paid'].items())},
                     helper_profile={str(r):v for r,v in sorted(profile['helper'].items())})
            cases.append(row)
            print('PASS_WEIGHTED_MILP_CANDIDATE_REPLAY',data['ell'],boundary,solver['status'],
                  'changed',sum(modes),'gain',float(lower),float(upper),'delta',delta,
                  'elapsed',round(time.monotonic()-began,2),flush=True)
        rows.append(dict(ell=data['ell'],cases=cases))
    binaries=sorted((HERE/'.solver/local/highspy').glob('*.pyd'))
    output=dict(status='PASS_WEIGHTED_MILP_AND_EXACT_ASSIGNMENT_REPLAY',kappa=str(W.KAPPA),results=rows,
                solver=dict(name='HiGHS',version=highspy.Highs().version(),numpy_version=np.__version__,
                            binaries={p.name:sha256(p.read_bytes()).hexdigest() for p in binaries}),
                graph_sha256=sha256((HERE/'MIXED-GAUGE.json.gz').read_bytes()).hexdigest(),
                setup_sha256=sha256((HERE/'WEIGHTED-GAUGE.json.gz').read_bytes()).hexdigest(),
                script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),seconds=time.monotonic()-began,
                new_kappa=False,
                scope='Finite actual-reference rank assignment search; integer products and candidate rank profiles replay exactly, and signed moment gains use certified rational intervals. Solver optimality is floating evidence. Positive rank assignments still require complete physical/phase/helper/recursive admission.')
    (HERE/'WEIGHTED-MILP.json.gz').write_bytes(gzip.compress(json.dumps(output,sort_keys=True,separators=(',',':')).encode(),mtime=0))


if __name__=='__main__':main()
