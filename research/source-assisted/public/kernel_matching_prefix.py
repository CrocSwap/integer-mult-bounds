#!/usr/bin/env python3
"""Exact transversal-matroid prefix certificate for the selected kernel flow.

GPT-6 Astra, 2026-10-09. No selected source/witness is modified.
The compatibility relation is exactly the selected compiler's: a distinct
later-or-equal phase vertex at an actual containing frame, with a dirty birth.
This optimizes only the matching on that fixed finite graph.
"""
from collections import Counter, defaultdict, deque
import argparse
from hashlib import sha256
from pathlib import Path
import json
import math
import time

HERE=Path(__file__).resolve().parent
WITNESS=HERE.parent/'decision/aligned_parity_purified_flow.result.witness.json'
PROFILE=HERE.parent/'decision/aligned_parity_purified_flow.result.json'
RECEIPT=HERE/'kernel_matching_prefix.json'


def incidence_digest(witness):
    body={k:v for k,v in witness.items() if k!='kernel_pairs'}
    return sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def contained(U,V):
    for x in U:
        for row in V:
            if x & (1 << (row.bit_length()-1)):
                x ^= row
        if x:
            return False
    return True


def run(witness_path=WITNESS,profile_path=PROFILE,output_path=RECEIPT,allow_improvement=False):
    started=time.monotonic()
    witness=json.loads(witness_path.read_text())
    profile=json.loads(profile_path.read_text())
    nodes=witness['nodes']
    donors=[(i,a) for i,n in enumerate(nodes) for a in range(n['retired']-n['d']+n['r'])]
    recipients=[(i,b) for i,n in enumerate(nodes) for b in range(n['new_dirty'])]
    recipients.sort(key=lambda z:(len(nodes[z[0]]['frame'][1]),nodes[z[0]]['frame'][0],z))
    assert len(donors)==706
    assert {len(nodes[i]['frame'][1]) for i,a in donors}=={3}
    did={z:i for i,z in enumerate(donors)}
    rid={z:i for i,z in enumerate(recipients)}
    donor_nodes=defaultdict(list)
    for d,(i,a) in enumerate(donors):donor_nodes[i].append(d)
    recipient_nodes=defaultdict(list)
    for r,(i,b) in enumerate(recipients):recipient_nodes[i].append(r)
    adjL=[[] for _ in donors]
    adjR=[[] for _ in recipients]
    for i,ds in donor_nodes.items():
        p,U=nodes[i]['frame']
        for j,rs in recipient_nodes.items():
            q,V=nodes[j]['frame']
            if i==j or p>q or len(U)>len(V) or not contained(U,V):continue
            for d in ds:adjL[d].extend(rs)
            for r in rs:adjR[r].extend(ds)
    print(json.dumps(dict(stage='compatibility',donors=len(donors),recipients=len(recipients),
                         edges=sum(map(len,adjL)),seconds=time.monotonic()-started)),flush=True)
    # Greedy by recipient dimension in the transversal matroid. An augment
    # preserves every earlier accepted recipient, adding one whenever possible.
    matchL=[-1]*len(donors)
    matchR=[-1]*len(recipients)
    def augment(start):
        # Alternating BFS from this new right vertex to any unmatched left.
        queue=deque([start]); seenR={start}; parentL={}
        free=-1
        while queue and free<0:
            r=queue.popleft()
            for d in adjR[r]:
                if d in parentL:continue
                parentL[d]=r
                if matchL[d]<0:
                    free=d;break
                old=matchL[d]
                if old not in seenR:
                    seenR.add(old);queue.append(old)
        if free<0:return False
        d=free
        while True:
            r=parentL[d]
            old_d=matchR[r]
            matchL[d]=r;matchR[r]=d
            if r==start:
                assert old_d<0
                break
            assert old_d>=0
            d=old_d
        return True
    old_pairs=witness['kernel_pairs']
    old_match=[(did[i,a],rid[j,b]) for i,a,j,b in old_pairs]
    assert len(old_match)==len(donors)
    assert len({d for d,r in old_match})==len(old_match)
    assert len({r for d,r in old_match})==len(old_match)
    assert all(d in adjR[r] for d,r in old_match)
    maxdim=max(len(nodes[i]['frame'][1]) for i,b in recipients)
    prefixes=[];stop=0
    for k in range(maxdim+1):
        while stop<len(recipients) and len(nodes[recipients[stop][0]]['frame'][1])<=k:
            augment(stop);stop+=1
        matching=[(d,r) for d,r in enumerate(matchL) if r>=0]
        # Konig certificate: alternating reachability from unmatched lefts.
        seenL={d for d,r in enumerate(matchL) if r<0};seenR=set();queue=deque(seenL)
        while queue:
            d=queue.popleft()
            for r in adjL[d]:
                if r>=stop or matchL[d]==r or r in seenR:continue
                seenR.add(r)
                dd=matchR[r]
                assert dd>=0, 'An augmenting path survived the greedy scan'
                if dd not in seenL:seenL.add(dd);queue.append(dd)
        coverL=sorted(set(range(len(donors)))-seenL)
        coverR=sorted(seenR)
        assert len(coverL)+len(coverR)==len(matching)
        L=set(coverL);RR=set(coverR)
        assert all(d in L or r in RR for d,rs in enumerate(adjL) for r in rs if r<stop)
        old_count=sum(len(nodes[recipients[r][0]]['frame'][1])<=k for d,r in old_match)
        prefixes.append(dict(max_recipient_dimension=k,recipient_count=stop,maximum_matching=len(matching),
                             selected_matching_prefix=old_count,selected_prefix_optimal=old_count==len(matching),
                             matching=matching,minimum_vertex_cover_left=coverL,minimum_vertex_cover_right=coverR))
    assert all(r>=0 for r in matchL), 'Not all kernels could be assigned'
    proposed=[[donors[d][0],donors[d][1],recipients[r][0],recipients[r][1]] for d,r in enumerate(matchL)]
    oldhist=Counter(len(nodes[j]['frame'][1]) for i,a,j,b in old_pairs)
    newhist=Counter(len(nodes[j]['frame'][1]) for i,a,j,b in proposed)
    local=Counter({int(r):n for r,n in profile['local_histogram'].items()})
    child=Counter({int(r):n for r,n in profile['child_histogram'].items()})
    delta=Counter()
    for r in set(oldhist)|set(newhist):
        n=newhist[r]-oldhist[r]
        delta[r]-=n;delta[r-3]+=n
    for r,n in delta.items():local[r]+=n;child[r]+=3*n
    local={r:n for r,n in sorted(local.items()) if r and n}
    child={r:n for r,n in sorted(child.items()) if r and n}
    assert min(local.values())>0 and min(child.values())>0
    assert sum(r*n for r,n in delta.items())==0
    h,m,W=profile['h'],3*profile['h'],profile['new_W']
    cap=m*W
    assert cap-sum(r*n for r,n in child.items())==profile['deficit']
    def root(hist):
        lo,hi=0.,.01
        for _ in range(80):
            a=(lo+hi)/2
            E=math.fsum(n*r*math.expm1(a*math.log(m/r)) for r,n in hist.items())
            if E<profile['deficit']:lo=a
            else:hi=a
        return lo
    a=.0009218338
    extra_drop=-3*sum(n*r*math.expm1(a*math.log(m/r)) for r,n in delta.items() if r)
    summary=dict(author='GPT-6 Astra',scope='Maximum-weight reuse matching on the fixed selected incidence graph; no global producer optimum',
                 witness_sha256=sha256(witness_path.read_bytes()).hexdigest(),profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),
                 incidence_sha256_excluding_kernel_pairs=incidence_digest(witness),
                 incidence_hash_encoding='UTF-8 JSON, sorted object keys, compact separators, every witness field except kernel_pairs',
                 donors=len(donors),donor_nodes=len(donor_nodes),recipients=len(recipients),compatibility_edges=sum(map(len,adjL)),
                 selected_prefix_optimal=all(z['selected_prefix_optimal'] for z in prefixes),
                 first_nonoptimal_prefix=next((z['max_recipient_dimension'] for z in prefixes if not z['selected_prefix_optimal']),None),
                 all_new_prefixes_certified_by_equal_matching_and_vertex_cover=True,
                 selected_recipient_dimension_histogram=dict(sorted(oldhist.items())),
                 proposed_recipient_dimension_histogram=dict(sorted(newhist.items())),
                 local_histogram_delta={r:n for r,n in sorted(delta.items()) if n},
                 extra_excess_drop_at_target=extra_drop,
                 selected_local_root=root({int(r):n for r,n in profile['child_histogram'].items()}),
                 proposed_local_root=root(child),physical_R=profile['new_R'],W=W,deficit=profile['deficit'],
                 seconds=time.monotonic()-started)
    assert allow_improvement or summary['selected_prefix_optimal'], 'Selected matching misses a prefix maximum; use --optimize only for an explicitly unselected proposal'
    result=dict(summary=summary,donors=donors,recipients=recipients,prefix_certificates=prefixes,
                historical_input_kernel_pairs=old_pairs,
                proposed_kernel_pairs=proposed,proposed_local_histogram=local,proposed_child_histogram=child)
    output_path.parent.mkdir(parents=True,exist_ok=True)
    output_path.write_text(json.dumps(result,separators=(',',':'))+'\n')
    print(json.dumps(summary,indent=2),flush=True)
    return result


def verify_selected(witness_path=WITNESS,profile_path=PROFILE,receipt_path=RECEIPT):
    """Check the saved primal/dual certificates against the selected incidence.

    No matching library or optimization heuristic is trusted by this checker.
    It verifies every edge of each prefix is covered and that an equally large
    matching exists, then verifies the selected matching attains all prefixes.
    """
    result=json.loads(receipt_path.read_text())
    witness=json.loads(witness_path.read_text())
    profile=json.loads(profile_path.read_text())
    nodes=witness['nodes'];summary=result['summary']
    assert incidence_digest(witness)==summary['incidence_sha256_excluding_kernel_pairs']
    donors=[(i,a) for i,n in enumerate(nodes) for a in range(n['retired']-n['d']+n['r'])]
    recipients=[(i,b) for i,n in enumerate(nodes) for b in range(n['new_dirty'])]
    recipients.sort(key=lambda z:(len(nodes[z[0]]['frame'][1]),nodes[z[0]]['frame'][0],z))
    assert donors==[tuple(z) for z in result['donors']]
    assert recipients==[tuple(z) for z in result['recipients']]
    ds=defaultdict(list);rs=defaultdict(list)
    for d,(i,a) in enumerate(donors):ds[i].append(d)
    for r,(i,b) in enumerate(recipients):rs[i].append(r)
    adj=[set() for _ in donors]
    for i,cols in ds.items():
        p,U=nodes[i]['frame']
        for j,rows in rs.items():
            q,V=nodes[j]['frame']
            if i!=j and p<=q and len(U)<=len(V) and contained(U,V):
                for d in cols:adj[d].update(rows)
    assert sum(map(len,adj))==summary['compatibility_edges']
    rank=[]
    for cert in result['prefix_certificates']:
        k=cert['max_recipient_dimension'];stop=cert['recipient_count']
        assert stop==sum(len(nodes[i]['frame'][1])<=k for i,b in recipients)
        matching=[tuple(z) for z in cert['matching']]
        L=set(cert['minimum_vertex_cover_left']);R=set(cert['minimum_vertex_cover_right'])
        assert all(0<=d<len(donors) and 0<=r<stop and r in adj[d] for d,r in matching)
        assert len({d for d,r in matching})==len({r for d,r in matching})==len(matching)
        assert all(0<=d<len(donors) for d in L) and all(0<=r<stop for r in R)
        assert len(L)+len(R)==len(matching)==cert['maximum_matching']
        assert all(d in L or r in R for d,rows in enumerate(adj) for r in rows if r<stop)
        rank.append((k,len(matching)))
    did={z:d for d,z in enumerate(donors)};rid={z:r for r,z in enumerate(recipients)}
    proposed=result['proposed_kernel_pairs']
    assert witness['kernel_pairs']==proposed, 'Selected witness does not use the certified matching'
    pairs=[(did[i,a],rid[j,b]) for i,a,j,b in proposed]
    assert len({d for d,r in pairs})==len({r for d,r in pairs})==len(donors)
    assert all(r in adj[d] for d,r in pairs)
    for k,maximum in rank:
        assert sum(len(nodes[recipients[r][0]]['frame'][1])<=k for d,r in pairs)==maximum
    assert {int(r):n for r,n in profile['local_histogram'].items()}=={int(r):n for r,n in result['proposed_local_histogram'].items()}
    assert {int(r):n for r,n in profile['child_histogram'].items()}=={int(r):n for r,n in result['proposed_child_histogram'].items()}
    # The original comparison receipt is reproducible without a second giant
    # witness: substituting its old matching restores its exact original bytes.
    old=dict(witness);old['kernel_pairs']=result['historical_input_kernel_pairs']
    old_bytes=(json.dumps(old,separators=(',',':'))+'\n').encode()
    assert sha256(old_bytes).hexdigest()==summary['witness_sha256']
    print(json.dumps(dict(author='GPT-6 Astra',status='PASS',
                          fixed_incidence_sha256=incidence_digest(witness),
                          selected_witness_sha256=sha256(witness_path.read_bytes()).hexdigest(),
                          donors=len(donors),recipients=len(recipients),edges=sum(map(len,adj)),
                          prefix_matching_and_vertex_cover_certificates=len(rank),
                          selected_attains_all_prefix_ranks=True,
                          historical_witness_reconstructed_by_only_replacing_kernel_pairs=True),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--witness',type=Path,default=WITNESS)
    parser.add_argument('--profile',type=Path,default=PROFILE)
    parser.add_argument('--output',type=Path,default=RECEIPT,help='Receipt destination, or receipt to inspect with --verify')
    parser.add_argument('--verify',action='store_true',help='Check the saved matching/vertex-cover receipt without rewriting it')
    parser.add_argument('--optimize',action='store_true',help='Permit a nonoptimal input matching and emit an unselected improved proposal; default requires the selected input to attain every prefix maximum')
    args=parser.parse_args()
    if args.verify:
        verify_selected(args.witness,args.profile,args.output)
    else:
        run(args.witness,args.profile,args.output,args.optimize)
