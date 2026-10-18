# SPDX-License-Identifier: Apache-2.0
"""Bounded k=473 owner construction; optional scipy/numpy generation dependency.

Adapted from PR2979 construction/allocation/fill17.py, itself crediting
Yiyang Lu / PR2857 for chronological flow and bipartite edge coloring.
This does not execute that source searcher. The literal output is intended
for a separate standard-library exact checker. No exponent is computed.
"""
import argparse
import collections
import gzip
import hashlib
import importlib.util
import json
import pathlib
import platform
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / 'sources'
WID = (4, 5, 6, 7, 8, 9)
INV = {4: 26, 5: 2, 6: 16, 7: 52, 8: 99, 9: 213}
T = 37
CUT = 45


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    b = pathlib.Path(path).read_bytes()
    return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)


def save(path, obj):
    b = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
    if str(path).endswith('.gz'):
        b = bytearray(gzip.compress(b, mtime=0))
        b[9] = 255
        b = bytes(b)
    pathlib.Path(path).write_bytes(b)


def log(*args):
    print(*args, flush=True)


def target_at(k):
    need(type(k) is int and 0<=k<=1063,'covered target parameter')
    target={(int(cap),tuple(q)):int(n)for cap,q,n in read(SRC/'construction/allocation/T37-FACE-MIX.json')['target']}
    target[16,(0,0,0,1,0,1)]=16253-k
    target[16,(0,0,0,0,2,0)]=323+k
    target[32,(0,0,0,1,2,1)]=1063-k
    target[32,(0,0,0,2,0,2)]=k
    return {key:n for key,n in target.items()if n}


def load():
    full_order = read(SRC / 'allocation/ORDER.json')
    full_dispatch = read(SRC / 'allocation/DISPATCH.json')
    fd = {(s, r): p for s, r, p in full_dispatch}
    order = []
    dispatch = []
    for t in range(333):
        s, r = full_order[2*t]
        need(0 <= r < 37 and full_order[2*t+1] == [s, r+37], 'source two-copy order')
        need(fd[s, r] == fd[s, r+37], 'source two-copy provider')
        order.append([s, r])
        dispatch.append([s, r, fd[s, r]])
    providers = read(SRC / 'allocation/PROVIDERS.json')
    for p in providers.values():
        need(collections.Counter(p['widths']) == INV, 'provider width inventory')
        p['actual_paid_profile'] = {int(k): n for k, n in p['actual_paid_profile'].items()}
    plan = read(SRC / 'allocation/vendor/PLAN.json.gz')
    template = read(SRC / 'allocation/vendor/TEMPLATE.json.gz')
    spec = importlib.util.spec_from_file_location('credited_source_owner', SRC / 'allocation/vendor/independent_owners.py')
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    win = owner.windows(template, order, T)
    # A pending window must never expose its physical family as active data.
    active = {e['stage']: e['pair'] for e in template['recipe'] if e['kind'] == 'local'}
    for (o, c), (cap, lo, hi) in win.items():
        for t in range(max(0, lo+1), min(333, hi+1)):
            s, r = order[t]
            need(o != r or plan['pairs'][str(c)] != active[s], 'active-data family exclusion')
    target = {(int(cap), tuple(q)): int(n) for cap, q, n in read(SRC / 'construction/allocation/T37-FACE-MIX.json')['target']}
    # Exactly 590 inverse saturated swaps from the shipped k=1063 mix.
    for cap, q, dn in [(16, (0,0,0,1,0,1), 590), (16, (0,0,0,0,2,0), -590),
                       (32, (0,0,0,1,2,1), 590), (32, (0,0,0,2,0,2), -590)]:
        target[cap, q] = target.get((cap, q), 0) + dn
    need(all(n > 0 for n in target.values()), 'positive target counts')
    groups = collections.defaultdict(list)
    for (o, c), (cap, lo, hi) in win.items():
        for port in range(112):
            groups[cap, tuple(range(max(0, lo+1), min(333, hi+1)))].append((o, c, port))
    G = sorted(groups)
    # Nonoverlapping pending windows of one physical family make per-bin
    # call-distinct coloring sufficient for the full same-call family rule.
    fw = collections.defaultdict(list)
    for (o, c), (_, lo, hi) in win.items():
        fw[o, plan['pairs'][str(c)], plan['sides'][str(c)]].append((lo, hi))
    for ws in fw.values():
        for j, (lo, hi) in enumerate(ws):
            need(all(max(lo,l) >= min(hi,h) for l,h in ws[j+1:]), 'disjoint physical-family windows')
    return order, dispatch, providers, plan, template, owner, groups, G, target


def color_pattern(n, q, counts):
    """PR2857/PR2979 regular bipartite multigraph decomposition."""
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import maximum_bipartite_matching
    slots = [w for w, k in zip(WID, q) for _ in range(k)]
    if not slots:
        need(not counts, 'empty pattern has no roles')
        return [[] for _ in range(n)]
    times = sorted({t for t, w in counts})
    K = len(times)
    need(K >= len(slots), 'enough distinct times for pattern')
    A = np.zeros((K, K), dtype=np.int64)
    slot_by_w = collections.defaultdict(list)
    for j, w in enumerate(slots):
        slot_by_w[w].append(j)
    for w, js in slot_by_w.items():
        atslot, remaining = 0, n
        for r, t in enumerate(times):
            needed = counts.get((t, w), 0)
            while needed:
                take = min(needed, remaining)
                A[r, js[atslot]] += take
                needed -= take
                remaining -= take
                if remaining == 0:
                    atslot += 1
                    remaining = n
        need(atslot == len(js), 'all width slots filled')
    need(all(int(v) <= n for v in A.sum(axis=1)), 'distinct calls per bin')
    j, remaining = len(slots), n
    for r in range(K):
        needed = n - int(A[r].sum())
        while needed:
            need(j < K, 'padding degree')
            take = min(needed, remaining)
            A[r, j] += take
            needed -= take
            remaining -= take
            if remaining == 0:
                j += 1
                remaining = n
    need(bool(np.all(A.sum(axis=0) == n) and np.all(A.sum(axis=1) == n)), 'regular bipartite graph')
    output = []
    for _ in range(n):
        matching = maximum_bipartite_matching(csr_matrix(A > 0), perm_type='column')
        need(len(matching) == K and min(matching) >= 0 and len(set(map(int, matching))) == K, 'perfect matching')
        output.append([(times[r], slots[int(c)]) for r, c in enumerate(matching) if c < len(slots)])
        A[np.arange(K), matching] -= 1
    need(not A.any(), 'all multigraph edges consumed')
    return output


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seconds', type=int, default=600)
    ap.add_argument('--out', type=pathlib.Path, default=HERE / 'candidate')
    ap.add_argument('--repair', action='store_true', help='Direct inverse-swap bipartite matching on the source literal fill; no optimizer')
    args = ap.parse_args()
    need(1 <= args.seconds <= 600, 'at most 600 solver seconds')
    args.out.mkdir(parents=True, exist_ok=False)
    if args.repair:
        return repair(args.out)
    import numpy as np
    import scipy
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import coo_matrix
    started = time.time()
    order, dispatch, providers, plan, template, owner, groups, G, target = load()
    pats = collections.defaultdict(list)
    for cap, q in sorted(target):
        pats[cap].append(q)
    edges, lb, ub, rl, ru = [], [], [], [], []
    Xv, Zv = {}, {}

    def cr(l, u=None):
        j = len(rl)
        rl.append(int(l))
        ru.append(int(l if u is None else u))
        return j

    def cv(u):
        j = len(lb)
        lb.append(0)
        ub.append(int(u))
        return j

    def put(r, v, n):
        if n:
            edges.append((r, v, n))

    callrow = {(t,w): cr(INV[w]) for t in range(333) for w in WID}
    globalrow = {key: cr(n) for key, n in sorted(target.items())}
    restricted_x = restricted_z = 0
    for gi, (cap, ts) in enumerate(G):
        nb = len(groups[G[gi]])
        br = cr(nb)
        for q in pats[cap]:
            # Consequences of the attained width-7 cut; no extra assumption.
            meet_cut = any(t >= CUT for t in ts)
            forbidden = cap == 16 and meet_cut and q[3] == 0
            xv = cv(0 if forbidden else nb)
            restricted_x += forbidden
            Xv[gi,q] = xv
            put(br, xv, 1)
            put(globalrow[cap,q], xv, 1)
            residual = {w:q[j] for j,w in enumerate(WID) if q[j]}
            wr = {w:cr(0) for w in residual}
            for w,n in residual.items():
                put(wr[w], xv, -n)
            for t in ts:
                tr = cr(-nb, 0)
                put(tr, xv, -1)
                for w in residual:
                    limit = min(nb, INV[w])
                    if forbidden or (w == 7 and t < CUT and (cap != 16 or meet_cut)):
                        limit = 0
                        restricted_z += 1
                    zv = cv(limit)
                    Zv[gi,q,t,w] = zv
                    put(tr,zv,1)
                    put(wr[w],zv,1)
                    put(callrow[t,w],zv,1)
    rr = np.fromiter((e[0] for e in edges), np.int32)
    cc = np.fromiter((e[1] for e in edges), np.int32)
    vv = np.fromiter((e[2] for e in edges), np.int64)
    exact_mat = coo_matrix((vv,(rr,cc)),shape=(len(rl),len(lb))).tocsr()
    info = dict(T=37, k=473, calls=333, groups=len(G), variables=len(lb), pattern_variables=len(Xv),
                flow_variables=len(Zv), constraints=len(rl), nonzeros=len(edges),
                restricted_x=restricted_x, restricted_z=restricted_z,
                source_model='PR2979 fill17.py, PR2857 chronological flow',
                restrictions='Necessary equality consequences of PR2987 cut [45,332] at k473',
                python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__)
    save(args.out / 'MODEL.json', info)
    save(args.out / 'PATTERNS.json', dict(k=473,T=37,widths=WID,target=[[cap,q,n]for(cap,q),n in sorted(target.items())]))
    log('MODEL', info)
    # One feasibility invocation. No LP or extra parameter round is launched.
    solvestart = time.time()
    res = milp(np.zeros(len(lb)), integrality=np.ones(len(lb)),
               bounds=Bounds(np.array(lb,dtype=float),np.array(ub,dtype=float)),
               constraints=LinearConstraint(exact_mat.astype(float),np.array(rl,dtype=float),np.array(ru,dtype=float)),
               options={'time_limit': args.seconds, 'mip_rel_gap':0, 'disp':True, 'threads':1})
    receipt = dict(status=int(res.status),message=str(res.message),solver='scipy.optimize.milp / HiGHS',
                   max_seconds=args.seconds,seconds=time.time()-solvestart,
                   candidate=res.x is not None, proof_level='Float solver status alone is no proof of infeasibility or feasibility',
                   source_head='be191346391661f4d35fc0d1508d0a6029572576',
                   predecessor_head='02c3047a1e78e6e35e7573c12434ba26f6f9bd96')
    for name in ['mip_node_count','mip_gap','mip_dual_bound','fun']:
        if hasattr(res,name) and getattr(res,name) is not None:
            receipt[name]=float(getattr(res,name))
    save(args.out/'SOLVER.json',receipt)
    log('SOLVER', receipt)
    if res.x is None:
        save(args.out/'HANDOFF.json',dict(status='NO_EXACT_CANDIDATE',remaining='Recover the same fixed model; no infeasibility proof is claimed.',seconds=time.time()-started))
        return
    value=np.rint(res.x).astype(np.int64)
    need(np.all(np.isfinite(res.x)), 'finite solver vector')
    need(float(np.max(np.abs(res.x-value))) < 1e-5, 'solver integrality tolerance')
    need(bool(np.all(value>=lb) and np.all(value<=ub)), 'exact integer variable bounds')
    lhs=exact_mat@value
    need(bool(np.all(lhs>=rl) and np.all(lhs<=ru)), 'exact integer model equations')
    # These integer bounds also preclude overflow in the int64 check above.
    need(max(abs(int(v))for v in lhs)<10**9, 'small exact model range')
    xc=collections.defaultdict(collections.Counter)
    zc=collections.defaultdict(collections.Counter)
    for(gi,q),j in Xv.items():
        if value[j]:xc[gi][q]=int(value[j])
    for(gi,q,t,w),j in Zv.items():
        if value[j]:zc[gi,q][t,w]=int(value[j])
    save(args.out/'FLOW.json.gz',dict(x=[[gi,q,n]for gi,c in xc.items()for q,n in c.items()],
                                      z=[[gi,q,t,w,n]for(gi,q),c in zc.items()for(t,w),n in c.items()]))
    globalcounts=collections.Counter()
    demand=collections.defaultdict(collections.Counter)
    for gi,(cap,ts)in enumerate(G):
        need(sum(xc[gi].values())==len(groups[G[gi]]),'exact group bin count')
        for q,n in xc[gi].items():globalcounts[cap,q]+=n
    need(dict(globalcounts)==target,'exact target mix')
    for(gi,q),c in zc.items():
        bywidth=collections.Counter()
        bytime=collections.Counter()
        for(t,w),n in c.items():
            need(t in G[gi][1] and q[WID.index(w)]>0,'exact window/width eligibility')
            bywidth[w]+=n;bytime[t]+=n;demand[t][w]+=n
        need(all(bywidth[w]==q[j]*xc[gi][q]for j,w in enumerate(WID)),'exact pattern demand')
        need(all(n<=xc[gi][q]for n in bytime.values()),'exact call-distinct bin capacity')
    need(all(demand[t]==INV for t in range(333)),'exact call width demands')
    log('EXACT_FLOW_PASS', 'coloring')
    slots=[]
    for gi,(cap,ts)in enumerate(G):
        bins=groups[G[gi]];offset=0
        for q,n in sorted(xc[gi].items()):
            colored=color_pattern(n,q,zc[gi,q])
            for b,it in zip(bins[offset:offset+n],colored):
                z=0
                for t,w in sorted(it):
                    slots.append((t,w,*b,z));z+=w
                need(z<=cap,'colored capacity')
            offset+=n
        need(offset==len(bins),'colored complete bins')
    disp={(s,r):p for s,r,p in dispatch}
    available={t:collections.defaultdict(list)for t in range(333)}
    for t,sr in enumerate(order):
        for h,w in enumerate(providers[disp[tuple(sr)]]['widths']):available[t][w].append(h)
    rows=[]
    for t,w,o,c,p,z in sorted(slots):rows.append([t,available[t][w].pop(),o,c,p,z])
    need(not any(v for d in available.values()for v in d.values()),'all literal helper identities assigned')
    fill=dict(columns=['time','helper','owner_replica','child','port','offset'],dispatch_overrides=[],
              method='k473 single bounded scipy MILP and PR2857/PR2979 coloring; GPT-6.1 Sol assisted',rows=sorted(rows))
    result,_,_=owner.check(T,order,fill,disp,None,plan,template,providers)
    need(result['profile']=={1:822840,2:235098,3:79734,4:35964,5:6858,8:2664,48:14095},'complete inherited profile')
    result.update(status='PASS_SOURCE_OWNER_ENGINE_FINITE_GEOMETRY',physical=896*37+408+8+91+2,
                  physical_formula='896*T + 408 helpers + 8 centres + 91 private buffers + 2 guards',
                  proof_level='Finite exact integer equations and literal geometry; parent independent check pending',
                  k=473,solver_status=receipt['message'],seconds=time.time()-started)
    for name,obj in [('ORDER.json',order),('DISPATCH.json',dispatch),('FILL.json.gz',fill),
                     ('PROFILE.json',result['profile']),('PROVIDERS.json',providers)]:save(args.out/name,obj)
    save(args.out/'CONSTRUCTION-CHECK.json',result)
    log('LITERAL_CONSTRUCTION_PASS',result)


def repair(out):
    """Match source C=[8,8] bins to D=[7,7,9,9] bins for inverse swaps."""
    import numpy as np
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import maximum_bipartite_matching
    started=time.time()
    order,dispatch,providers,plan,template,owner,groups,G,target=load()
    disp={(s,r):p for s,r,p in dispatch}
    win=owner.windows(template,order,T)
    source=read(SRC/'allocation/FILL.json.gz')
    rows=[]
    for t,h,o,c,p,z in source['rows']:
        if t%2==0:
            need(o<37,'source repair copy ownership')
            rows.append([t//2,h,o,c,p,z])
    need(len(rows)==333*408,'repair source role count')
    bybin=collections.defaultdict(list)
    widths=[]
    for i,(t,h,o,c,p,z)in enumerate(rows):
        w=providers[disp[tuple(order[t])]]['widths'][h]
        widths.append(w)
        bybin[o,c,p].append(i)
    Cs=[];Ds=[]
    for b,ids in sorted(bybin.items()):
        cap,lo,hi=win[b[:2]]
        ws=sorted(widths[i]for i in ids)
        if cap==16 and ws==[8,8]:Cs.append((b,ids,lo,hi))
        if cap==32 and ws==[7,7,9,9]:Ds.append((b,ids,lo,hi))
    need(len(Cs)==1386 and len(Ds)==1063,'source inverse-swap donor counts')
    edge_rows=[];edge_cols=[];choices={}
    for ci,(cb,cids,clo,chi)in enumerate(Cs):
        ct=[rows[i][0]for i in cids]
        for di,(db,dids,dlo,dhi)in enumerate(Ds):
            if not all(dlo<t<=dhi for t in ct):continue
            sevens=[i for i in dids if widths[i]==7 and clo<rows[i][0]<=chi]
            nines=[i for i in dids if widths[i]==9 and clo<rows[i][0]<=chi]
            chosen=None
            for a in sevens:
                for b in nines:
                    if rows[a][0]==rows[b][0]:continue
                    remaining=[i for i in dids if i not in(a,b)]
                    if len(set(ct+[rows[i][0]for i in remaining]))==4:
                        chosen=(a,b);break
                if chosen:break
            if chosen:
                edge_rows.append(ci);edge_cols.append(di);choices[ci,di]=chosen
    mat=coo_matrix((np.ones(len(edge_rows),dtype=np.int8),(edge_rows,edge_cols)),shape=(len(Cs),len(Ds))).tocsr()
    matching=maximum_bipartite_matching(mat,perm_type='column')
    matched=[(ci,int(di))for ci,di in enumerate(matching)if di>=0]
    # Exact primal/dual matching certificate. Alternating reachability gives
    # a vertex cover; checking its edges and size needs no matching library.
    inverse={di:ci for ci,di in matched}
    reached_c={ci for ci in range(len(Cs))if matching[ci]<0}
    reached_d=set()
    queue=list(sorted(reached_c))
    cursor=0
    while cursor<len(queue):
        ci=queue[cursor];cursor+=1
        for di0 in mat.indices[mat.indptr[ci]:mat.indptr[ci+1]]:
            di=int(di0)
            if di==matching[ci] or di in reached_d:continue
            reached_d.add(di)
            if di in inverse and inverse[di]not in reached_c:
                reached_c.add(inverse[di]);queue.append(inverse[di])
    cover_c=set(range(len(Cs)))-reached_c
    cover_d=reached_d
    need(all(ci in cover_c or di in cover_d for ci,di in choices),'exact graph vertex cover')
    need(len(cover_c)+len(cover_d)==len(matched),'exact matching-cover equality')
    need(len({ci for ci,di in matched})==len(matched)and len({di for ci,di in matched})==len(matched),'exact matching distinct vertices')
    need(all((ci,di)in choices for ci,di in matched),'exact matching graph edges')
    graph=dict(left=[[list(b),ids,lo,hi]for b,ids,lo,hi in Cs],
               right=[[list(b),ids,lo,hi]for b,ids,lo,hi in Ds],
               edges=[[ci,di,*choices[ci,di]]for ci,di in sorted(choices)])
    save(out/'PAIR-GRAPH.json.gz',graph)
    certificate=dict(matching=[[ci,di]for ci,di in matched],cover_left=sorted(cover_c),cover_right=sorted(cover_d),
                     matching_cardinality=len(matched),cover_cardinality=len(cover_c)+len(cover_d),
                     graph_sha256=hashlib.sha256((out/'PAIR-GRAPH.json.gz').read_bytes()).hexdigest(),
                     proof='The listed matching is a lower bound and the equal-sized listed vertex cover covers every listed edge, giving an exact maximum for this graph. Completeness of graph reconstruction must be independently checked.')
    save(out/'MATCHING-CERT.json',certificate)
    report=dict(status='PASS_DIRECT_SWAP_GRAPH_MATCHING_COVER',capacity16_bins=len(Cs),capacity32_bins=len(Ds),
                graph_edges=len(edge_rows),maximum_matching=len(matched),needed=590,
                exact_vertex_cover=len(cover_c)+len(cover_d),
                source_head='be191346391661f4d35fc0d1508d0a6029572576',seconds=time.time()-started,
                graph_recipe='edge C,D iff two width8 roles fit D window and one width7 plus one width9 from D fit C window, with all receiving-bin call times distinct',
                proof_limit='Failure to find590 direct disjoint swaps would obstruct only this frozen one-swap matching graph, not full k473 chronological feasibility.')
    save(out/'MATCHING.json',report)
    log('REPAIR_MATCHING',report)
    attained=out/'attained'
    attained.mkdir(exist_ok=False)
    used_swaps=len(matched)
    attained_k=1063-used_swaps
    target=target_at(attained_k)
    journal=[]
    for ci,di in matched:
        cb,cids,clo,chi=Cs[ci];db,dids,dlo,dhi=Ds[di]
        a,b=choices[ci,di]
        moves=[]
        for i in cids:
            moves.append(dict(source_row=i,before=list(rows[i]),after_owner=list(db),width=8))
            rows[i][2:5]=db
        for i in(a,b):
            moves.append(dict(source_row=i,before=list(rows[i]),after_owner=list(cb),width=widths[i]))
            rows[i][2:5]=cb
        journal.append(dict(C=list(cb),D=list(db),moves=moves))
    # Deterministically repack every bin from offset zero; unchanged owners
    # keep their helper identities but are allowed a different coordinate order.
    newbins=collections.defaultdict(list)
    for i,r in enumerate(rows):newbins[tuple(r[2:5])].append(i)
    for b,ids in newbins.items():
        z=0
        for i in sorted(ids,key=lambda j:(rows[j][0],rows[j][1])):
            rows[i][5]=z;z+=widths[i]
        need(z<=win[b[:2]][0],'repair exact capacity')
        need(len({rows[i][0]for i in ids})==len(ids),'repair call-distinct receiving bin')
    fill=dict(columns=['time','helper','owner_replica','child','port','offset'],dispatch_overrides=[],
              method=f'{used_swaps} disjoint direct inverse saturated swaps from PR2979 source, chosen by exact bipartite matching; GPT-6.1 Sol assisted',rows=sorted(rows))
    result,_,_=owner.check(T,order,fill,disp,None,plan,template,providers)
    need(result['profile']=={1:822840,2:235098,3:79734,4:35964,5:6858,8:2664,48:14095},'repair unchanged complete profile')
    actual=collections.Counter()
    for(o,c),(cap,lo,hi)in win.items():
        for p in range(112):
            ids=newbins.get((o,c,p),[])
            actual[cap,tuple(sum(widths[i]==w for i in ids)for w in WID)]+=1
    need(dict(actual)==target,'repair exact attained target mix')
    report.update(status='PASS_DIRECT_MATCHING_LITERAL_CONSTRUCTION',used_swaps=used_swaps,attained_k=attained_k,seconds=time.time()-started)
    save(out/'MATCHING.json',report)
    save(attained/'JOURNAL.json.gz',journal)
    for name,obj in [('ORDER.json',order),('DISPATCH.json',dispatch),('FILL.json.gz',fill),
                     ('PROFILE.json',result['profile']),('PROVIDERS.json',providers),
                     ('PATTERNS.json',dict(k=attained_k,T=37,widths=WID,target=[[cap,q,n]for(cap,q),n in sorted(target.items())]))]:save(attained/name,obj)
    result.update(status='PASS_SOURCE_OWNER_ENGINE_FINITE_GEOMETRY',k=attained_k,physical=896*37+408+8+91+2,
                  proof_level='Finite exact inverse-swap matching and source literal geometry; independent parent check pending')
    save(attained/'CONSTRUCTION-CHECK.json',result)
    log('REPAIR_LITERAL_PASS',result)


if __name__=='__main__':
    main()
