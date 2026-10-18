#!/usr/bin/env python3
"""Joint CP-SAT search over every legal idle-axis transfer from the T740 initial fill."""
import argparse, gzip, importlib.util, json, time
from collections import Counter, defaultdict
from decimal import Decimal, localcontext, ROUND_FLOOR
from fractions import Fraction as F
from pathlib import Path
from ortools.sat.python import cp_model

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ARCHIVE=ROOT/'research/source-archives/t740-joint-axis-pr3200'
PHASES=ROOT/'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json'
SCALE=10**14

def load_json(path):
    b=Path(path).read_bytes()
    return json.loads(gzip.decompress(b) if b[:2]==b'\x1f\x8b' else b)
def dot(a,b): return (a&b).bit_count()&1

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seconds',type=float,default=120,help='CP-SAT wall-time limit')
    ap.add_argument('--workers',type=int,default=8,help='CP-SAT workers; multiple workers may vary by run')
    ap.add_argument('--seed',type=int,default=0)
    ap.add_argument('--output-dir',type=Path,default=Path('/tmp/t740-joint-axis-search'))
    args=ap.parse_args()
    if not (0 < args.seconds <= 3600) or args.workers < 1: raise SystemExit('invalid search limits')
    t0=time.time()
    spec=importlib.util.spec_from_file_location('pr3200_verify',ARCHIVE/'verify.py')
    verify=importlib.util.module_from_spec(spec); spec.loader.exec_module(verify)
    verify.PKG=ARCHIVE; verify.PHASES=PHASES; verify.BITCERT=ROOT/'research/r438-native-rehost/CERTIFICATE.json'
    phases=json.loads(PHASES.read_text()); rec={r['port']:r for r in phases['recipes']}
    bins=load_json(ARCHIVE/'BINS.json.gz'); base_moves=load_json(ARCHIVE/'MOVES.json.gz')['moves']; result=load_json(ARCHIVE/'RESULT.json')
    verify.BIT=verify.check_bit()
    base_final=verify.audit(rec,bins,base_moves)
    base_prof=Counter({r:n*9*verify.T for r,n in verify.LOCAL.items()}); base_prof.update(base_final)
    verify.run(rec,bins,base_moves,result)
    assert {str(k):v for k,v in sorted(base_prof.items())}==result['profile']
    caps={(p,c):int(ch['rank']) for p,rr in rec.items() for c,ch in enumerate(rr['idle_children'])}
    axes_rec={(p,c):[int(v) for v in ch['orthogonal_axes']] for p,rr in rec.items() for c,ch in enumerate(rr['idle_children'])}
    tr={(p,c):int(ch['translation_after']) for p,rr in rec.items() for c,ch in enumerate(rr['idle_children'])}
    trans={p:[int(s[k]) for s in rc['stage_alignment'] for k in ('entry_Y','exit_Y','entry_X','exit_X')]+[int(rc['terminal_Y_translation'])] for p,rc in rec.items()}
    def legal(v,p,c,d,dax):
        return all(dot(v,x)==0 for x in dax) and all(dot(v,x)==0 for x in trans[p]) and dot(v,tr[p,c])==0 and dot(v,tr[p,d])==0
    groups_by_key=defaultdict(list)
    for rep,p,kids in bins['groups']:
        groups_by_key[(p,tuple(map(tuple,kids)))].append(rep)
    move_by_group=defaultdict(list)
    for rep,p,c,d,v in base_moves: move_by_group[(rep,p)].append((c,d,v))
    base_by_key={}
    for key,reps in groups_by_key.items(): base_by_key[key]=move_by_group[(reps[0],key[0])]
    with localcontext() as ctx:
        ctx.prec=90
        root0=F(result['complex_root'][0]); pstar=Decimal(root0.numerator)/Decimal(root0.denominator)
        costs=[0]
        for r in range(1,52):
            y=Decimal(73)/Decimal(r)
            g=Decimal(r)*((y.ln()*pstar).exp()-Decimal(1))
            costs.append(int((g*SCALE).to_integral_value(rounding=ROUND_FLOOR)))
    model=cp_model.CpModel(); objective=[]; vars_by_key={}; states=[]
    candidate_count=conflicts=0; base_score=0; objective_upper=0
    for si,((p,kids),reps) in enumerate(sorted(groups_by_key.items())):
        freq=len(reps); state={c:{'used':u,'rank':caps[p,c]-u,'axes':axes_rec[p,c][u:caps[p,c]]} for c,u in kids}
        cands=[]
        for c,s in state.items():
            if not s['axes']: continue
            for d,t in state.items():
                if d==c or t['used']!=0 or t['rank']>=51: continue
                for v in s['axes']:
                    if legal(v,p,c,d,t['axes']): cands.append((c,d,v))
        candset=set(cands); baseline=base_by_key[(p,kids)]
        if not set(baseline).issubset(candset):
            raise ValueError(f'baseline move absent from initial candidate universe: {p,kids}')
        # Certify baseline feasibility in the same one-shot role/orthogonality domain.
        out_axes=set(); recv_axes=defaultdict(list); sources=set(); receivers=set()
        for c,d,v in baseline:
            if (c,v) in out_axes or c in receivers or d in sources: raise ValueError('baseline role/source conflict')
            out_axes.add((c,v)); sources.add(c); receivers.add(d); recv_axes[d].append(v)
        if any(dot(a,b) for vv in recv_axes.values() for i,a in enumerate(vv) for b in vv[i+1:]): raise ValueError('baseline incoming axes conflict')
        candidate_count+=len(cands)
        initial_rank={c:s['rank'] for c,s in state.items()}
        bo=Counter(c for c,d,v in baseline); bi=Counter(d for c,d,v in baseline)
        base_score+=freq*sum(costs[initial_rank[c]-bo[c]+bi[c]] for c in state)
        objective_upper+=freq*len(state)*max(costs)
        xs=[]; by_axis=defaultdict(list); by_recv=defaultdict(list); outgoing=defaultdict(list); incoming=defaultdict(list)
        for mi,(c,d,v) in enumerate(cands):
            x=model.NewBoolVar(f'x{si}_{mi}'); xs.append(x); by_axis[c,v].append(x); by_recv[d].append((x,v)); outgoing[c].append(x); incoming[d].append(x)
        for vv in by_axis.values():
            if len(vv)>1: model.Add(sum(vv)<=1)
        for d,items in by_recv.items():
            for i in range(len(items)):
                xi,vi=items[i]
                for j in range(i+1,len(items)):
                    xj,vj=items[j]
                    if dot(vi,vj): model.Add(xi+xj<=1); conflicts+=1
        for c,_ in kids:
            outs=outgoing[c]; ins=incoming[c]
            if outs:
                oa=model.NewBoolVar(f'out{si}_{c}'); model.Add(sum(outs)>=oa); model.Add(sum(outs)<=len(outs)*oa)
                model.AddHint(oa,int(bool(bo[c])))
            else: oa=None
            if ins:
                ia=model.NewBoolVar(f'in{si}_{c}'); model.Add(sum(ins)>=ia); model.Add(sum(ins)<=len(ins)*ia)
                model.AddHint(ia,int(bool(bi[c])))
            else: ia=None
            if oa is not None and ia is not None: model.Add(oa+ia<=1)
            fin=model.NewIntVar(0,51,f'rank{si}_{c}')
            model.Add(fin==initial_rank[c]-(sum(outs) if outs else 0)+(sum(ins) if ins else 0))
            cv=model.NewIntVar(0,max(costs),f'cost{si}_{c}'); model.AddElement(fin,costs,cv)
            final_hint=initial_rank[c]-bo[c]+bi[c]
            model.AddHint(fin,final_hint); model.AddHint(cv,costs[final_hint])
            objective.append(freq*cv)
        chosen=set(baseline)
        for x,edge in zip(xs,cands): model.AddHint(x,int(edge in chosen))
        vars_by_key[(p,kids)]=(cands,xs)
        states.append((p,kids,reps,initial_rank,baseline))
    if objective_upper >= 2**63: raise ValueError(f'int64 objective upper bound {objective_upper}')
    model.Minimize(sum(objective))
    validation=model.Validate()
    if validation: raise ValueError('invalid CP-SAT model: '+validation)
    build_seconds=time.time()-t0
    print(json.dumps({'phase':'built','patterns':len(states),'groups':len(bins['groups']),'variables':candidate_count,'incompatibilities':conflicts,'objective_upper_bound':objective_upper,'scale':SCALE,'build_seconds':round(build_seconds,2)},sort_keys=True),flush=True)
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=args.seconds; solver.parameters.num_search_workers=args.workers; solver.parameters.random_seed=args.seed
    solver.parameters.log_search_progress=True; solver.parameters.log_to_stdout=False
    ts=time.time(); status=solver.Solve(model); solve_seconds=time.time()-ts
    status_name=solver.StatusName(status)
    if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE): raise RuntimeError(status_name)
    selected_by_key={k:[edge for edge,x in zip(cands,xs) if solver.Value(x)] for k,(cands,xs) in vars_by_key.items()}
    candidate_stream=[]
    for p,kids,reps,rank,baseline in states:
        for rep in reps:
            candidate_stream.extend([[rep,p,*edge] for edge in sorted(selected_by_key[(p,kids)])])
    new_final=verify.audit(rec,bins,candidate_stream)
    new_prof=Counter({r:n*9*verify.T for r,n in verify.LOCAL.items()}); new_prof.update(new_final)
    if sum(r*n for r,n in new_prof.items())!=65088*verify.T or max(new_prof)>51: raise ValueError('candidate mass/cap')
    root_scale=10**25; lo_i=0; hi_i=10**23
    while hi_i-lo_i>1:
        mid=(lo_i+hi_i)//2; mlo,mhi=verify.mom(new_prof,F(mid,root_scale))
        if mhi<1: lo_i=mid
        elif mlo>1: hi_i=mid
        else: raise ValueError('root interval did not separate')
    lo,hi=F(lo_i,root_scale),F(hi_i,root_scale); kappa=min(F(lo.numerator*10**24//lo.denominator,10**24),verify.BIT)-F(1,10**46)-F(1,10**70)
    base_kappa=F(result['kappa'])
    changed=sum(selected_by_key[(p,kids)]!=base for p,kids,reps,rank,base in states)
    objective_value=0
    for (p,kids),reps in groups_by_key.items():
        selected=selected_by_key[(p,kids)]; outs=Counter(c for c,d,v in selected); ins=Counter(d for c,d,v in selected)
        initial={c:caps[p,c]-u for c,u in kids}
        objective_value+=len(reps)*sum(costs[initial[c]-outs[c]+ins[c]] for c in initial)
    out={'status':status_name,'solver_version':__import__('ortools').__version__,'source_head':'f09e5b25381393c604082e58fbe56896b13171b5','objective':'CP-SAT global weighted floor table; g(r)=r*((73/r)^p_star-1), p_star=PR3200 complex-root lower endpoint; Decimal precision=90','objective_scale':SCALE,'patterns':len(states),'groups':len(bins['groups']),'candidate_variables':candidate_count,'orthogonality_conflicts':conflicts,'weighted_objective_upper_bound':objective_upper,'baseline_scaled_objective':str(base_score),'optimized_scaled_objective':str(objective_value),'solver_seconds':round(solve_seconds,3),'wall_seconds':round(time.time()-t0,3),'threads':args.workers,'seed':args.seed,'time_limit_seconds':args.seconds,'profile':{str(k):v for k,v in sorted(new_prof.items())},'baseline_kappa':str(base_kappa),'optimized_complex_root':[str(lo),str(hi)],'optimized_kappa':str(kappa),'kappa_gain':str(kappa-base_kappa),'improves_claim':kappa>base_kappa,'admissible_kappa_claim':None,'physical_operator_status':'NOT_CHECKED_BY_RANK_ONLY_SEARCH','rank_only_score_is_not_a_supplier_claim':True,'pattern_changes':changed,'moves':len(candidate_stream),'best_bound':str(solver.BestObjectiveBound())}
    args.output_dir.mkdir(parents=True,exist_ok=True)
    payload=json.dumps({'columns':['replica','port','donor_child','receiver_child','axis'],'moves':candidate_stream},sort_keys=True,separators=(',',':')).encode()
    compressed=bytearray(gzip.compress(payload,mtime=0)); compressed[9]=255
    (args.output_dir/'RANK-ONLY-MOVES.json.gz').write_bytes(compressed)
    (args.output_dir/'RANK-ONLY-RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True),flush=True)
if __name__=='__main__': main()
