#!/usr/bin/env python3
"""Check an exact lower cost for every allowed frame assignment and packing.

Floating edge messages only nominate a bound. The checker rounds them to
rationals, corrects every edge inequality, and minimizes every node potential
over its complete subspace interval. Both independent source moment engines
supply outward lower costs. No optimizer is imported by this checker.
Prepared with OpenAI Codex (GPT-6 Astra) assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

from optimize_frames import frame_graph, contained


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cost_bounds(source, rate):
    costs=[]
    hashes={}
    for name in ('moment','base_two_moment'):
        path=source/'engines'/(name+'.py')
        hashes[name]=digest(path)
        spec=importlib.util.spec_from_file_location(name,path)
        engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
        current={0:Q(0)}
        for r in range(1,49):
            if name=='moment':
                lo,hi=engine.logarithm(Q(73,r));e=engine.exponential(rate*lo,rate*hi)[0]
            else:
                lo,_=engine.log_bounds(Q(73,r));e=engine.exp_bounds(rate*lo)[0]
            current[r]=Q((r*(e-1)/rate*10**18).__floor__(),10**18)
        costs.append(current)
    return {r:min(c[r] for c in costs) for r in range(49)},hashes


def certify(words,plan_path,messages_path,source,kappa):
    require(0<kappa<Q(1,100),'Invalid target')
    rate=kappa/(1-kappa)
    costs,engine_hashes=cost_bounds(source,rate)
    messages=json.loads(gzip.decompress(messages_path.read_bytes()))
    require(len(messages['providers'])==len(words),'Provider count mismatch')
    rational=lambda x:Q(round(float(x)*10**9),10**9)
    width_y={int(w):rational(v) for w,v in messages['widths'].items()}
    width_set=set()
    local=[]
    for path,msg in zip(words,messages['providers']):
        word=json.loads(gzip.decompress(path.read_bytes()))
        graph,frames,edges=frame_graph(word,True)
        require(len(msg)==len(edges),'Edge message count mismatch')
        node_costs=[[Q(0)]*len(states) for states in frames]
        pairs_checked=0
        for ((left,right),multiplicity),(left_msg,right_msg) in zip(sorted(edges.items()),msg):
            require(len(left_msg)==len(frames[left]) and len(right_msg)==len(frames[right]),'State message count mismatch')
            a=list(map(rational,left_msg));b=list(map(rational,right_msg))
            pairs=[(i,j,multiplicity*costs[len(g)-len(f)]) for i,f in enumerate(frames[left])
                   for j,g in enumerate(frames[right]) if contained(f,g)]
            require(bool(pairs),'Empty edge')
            correction=max(Q(0),max(a[i]+b[j]-cost for i,j,cost in pairs))
            a=[v-correction for v in a]
            require(all(a[i]+b[j]<=cost for i,j,cost in pairs),'Invalid exact edge inequality')
            pairs_checked+=len(pairs)
            node_costs[left]=[x+y for x,y in zip(node_costs[left],a)]
            node_costs[right]=[x+y for x,y in zip(node_costs[right],b)]
        for r in range(2*graph.v,len(graph.regs)):
            start=graph.regs[r][0]
            for i,frame in enumerate(frames[start]):
                width=graph.h-len(frame)
                width_set.add(width)
                require(width in width_y,'Missing width price')
                node_costs[start][i]+=width_y[width]
        center=sum(n*costs[r] for r,n in graph.center_profile.items())
        potential=center+sum(min(values) for values in node_costs)
        initial_inventory=Counter(graph.h-len(graph.nodes[graph.regs[r][0]]['F']) for r in range(2*graph.v,len(graph.regs)))
        profile=graph.profile()
        require(sum(r*n for r,n in profile.items())-sum(r*n for r,n in initial_inventory.items())==1856,'Wrong local mass gap')
        local.append(dict(word=str(path.resolve()),word_sha256=digest(path),nodes=len(frames),
                          edge_states_checked=pairs_checked,provider_potential=str(potential)))
    require(width_set==set(width_y),'Width alphabet mismatch')
    plan=json.loads(plan_path.read_text())
    capacities={r:112*n for r,n in sorted(Counter(v[0] for v in plan['windows'].values()).items())}
    require(sum(r*n for r,n in capacities.items())+72*1856==520704,'Global mass gap mismatch')
    widths=sorted(width_set)
    caps={}
    pattern_count=0
    for cap in capacities:
        values=[]
        def rec(i,remaining,price):
            nonlocal pattern_count
            if i==len(widths):
                values.append(costs[remaining]-price);pattern_count+=1
                return
            w=widths[i]
            for n in range(remaining//w+1):
                rec(i+1,remaining-w*n,price+n*width_y[w])
        rec(0,cap,Q(0))
        caps[cap]=min(values)
    call=min(Q(v['provider_potential']) for v in local)
    lower=sum(capacities[r]*caps[r] for r in capacities)+72*call
    margin=rate*lower-2560
    require(margin>0,'This nominee does not exclude the target')
    return dict(status='PASS_EXACT_JOINT_FRAME_AND_PACKING_EXCLUSION',rejected_kappa=str(kappa),
                rejected_rate=str(rate),cost_lower_bound=str(lower),strict_rejection_margin=str(margin),
                providers=local,width_prices={str(w):str(y) for w,y in width_y.items()},
                capacity_potentials={str(r):str(y) for r,y in caps.items()},call_potential=str(call),
                packing_patterns=pattern_count,source_plan_sha256=digest(plan_path),
                messages_sha256=digest(messages_path),engine_sha256=engine_hashes,
                checker_sha256=digest(Path(__file__)),
                graph_code_sha256=digest(Path(__file__).with_name('optimize_frames.py')),
                scope='All monotone gate-frame assignments and every enlargement of existing helper entrances '
                      'within the fixed scalar dependency graph for the three pinned words, combined with '
                      'fractional provider mixtures and every pending-capacity pattern. Scalar operations, '
                      'initial entrance lower bounds, center cuts and target caps remain fixed. This '
                      'excludes the stated kappa in this family only, not new scalar words or bases.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word',type=Path,action='append',required=True)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--messages',type=Path,required=True)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--kappa',default='0.001600620000000000')
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    result=certify(args.word,args.plan,args.messages,args.source,Q(args.kappa))
    if args.out:
        require(not args.out.exists(),'Use a fresh receipt path')
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','rejected_kappa','packing_patterns','strict_rejection_margin')}))


if __name__=='__main__':
    main()
