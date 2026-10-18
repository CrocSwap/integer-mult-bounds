#!/usr/bin/env python3
"""Exact certificates for PROOF.md; not a Lean or all-size multiplication proof.

Standard library only. No producer or predecessor verifier is imported.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import json
import struct
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
HOST = 'research/community-hyperplane599-audit/pr589/bit589/v9/hosted/GLOBAL-TEMPLATE.json.gz'
GEO = 'research/community-hyperplane599-audit/pr589/bit589/v9/nine/GEOMETRY.json'


class Reject(Exception):
    pass


def need(condition, message):
    if not condition:
        raise Reject(message)


def read(path):
    raw = (ROOT / path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def ident(n):
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))


def trans(a):
    return tuple(zip(*a))


def mul(a, b):
    bt = trans(b)
    return tuple(tuple(sum((x*y for x,y in zip(row,col) if x and y), Q(0))
                       for col in bt) for row in a)


def sub(a, b):
    return tuple(tuple(x-y for x,y in zip(r,s)) for r,s in zip(a,b))


def projection(rows, n=8):
    """Rational Gram-Schmidt, followed by the sum of line projectors."""
    basis = []
    for row in rows:
        u = tuple(map(Q, row))
        for b, norm in basis:
            c = sum(x*y for x,y in zip(u,b)) / norm
            u = tuple(x-c*y for x,y in zip(u,b))
        norm = sum(x*x for x in u)
        if norm:
            basis.append((u,norm))
    p = tuple(tuple(sum((b[i]*b[j]/norm for b,norm in basis), Q(0))
                    for j in range(n)) for i in range(n))
    need(mul(p,p) == p and trans(p) == p, 'non-orthogonal frame projector')
    return p, len(basis)


def dyadic(a):
    return all(x.denominator & (x.denominator-1) == 0 for row in a for x in row)


def swap(p):
    """D_P(x,y) = ((I-P)x+Py, Px+(I-P)y)."""
    c = sub(ident(len(p)), p)
    return tuple(c[i]+p[i] for i in range(len(p))) + tuple(p[i]+c[i] for i in range(len(p)))


@lru_cache(None)
def certify_transport(p, q, down):
    low, high = (q,p) if down else (p,q)
    need(mul(low,high)==low and mul(high,low)==low, 'non-nested transport')
    residual = sub(high,low)
    need(mul(swap(p),swap(q)) == swap(residual), 'wrong address transport')
    need(mul(residual,residual)==residual, 'non-projector residual')


def literal_programs(w, dims):
    """Reconstruct six-integer records from gates, then both orientations."""
    n = 2*w['v']+w['R']; cur = w['start'][:]; rec = []
    def move(r,f):
        if cur[r] != f:
            rec.append([0,r,cur[r],f,dims[f]-dims[cur[r]],0]); cur[r] = f
    def gates(seq,phase):
        for f,d,srcs in seq:
            for r in [d]+srcs:
                move(r,f)
            rec.extend([1,d,s,1,f,phase] for s in srcs)
    gates(w['D'],1); gates(w['A'],2)
    for k,r in enumerate(w['ret']):
        f = cur[r]; rec.append([2,r,n,f,0,dims[f]])
        for j,row in enumerate(w['scatter']):
            if k in row:
                rec.append([1,w['v']+j,n,1,0,3])
        rec.append([3,r,n,f,0,0])
    gates(w['B'],4); gates(w['C'],5)
    for r in range(n):
        move(r,w['final'][r])
    out = {}
    for rev in (False,True):
        events = []
        for op,x,y,c,f,z in (reversed(rec) if rev else rec):
            if op == 0:
                events.append([0,x,c if rev else y,y if rev else c,f,int(rev)])
            elif op == 1:
                events.append([1,x,y,-c if rev else c,f,int(rev)])
            elif op == (3 if rev else 2):
                events.append([2,x,y,c,f,abs(dims[c]-dims[f]),int(rev)])
            else:
                events.append([3,x,y,c,f,z,int(rev)])
        out['reverse' if rev else 'forward'] = events
    raw = b''.join(struct.pack('<6i',*r) for r in rec)
    return out, hashlib.sha256(raw).hexdigest()


def local_replay(events, w, projectors, dims, rev=False):
    n = 2*w['v']+w['R']; v = w['v']
    frames = (w['final'] if rev else w['start'])[:] + [-1]
    values = [1 << r for r in range(n)] + [0]
    centre = None; paid = Counter(); copies = []
    @lru_cache(None)
    def transport(a,b,is_copy):
        p,q = projectors[a],projectors[b]
        if rev:
            p,q = sub(ident(8),p),sub(ident(8),q)
        # COPY can descend; MOVE must ascend.
        down = ((dims[a] < dims[b]) if rev else (dims[a] > dims[b]))
        certify_transport(p,q,is_copy and down)
        return abs(dims[b]-dims[a])
    for pos,e in enumerate(events):
        op,x = e[:2]
        need(0 <= x < n, 'bad role')
        if op == 0:
            _,_,a,b,r,flag=e
            need(flag==int(rev) and frames[x]==a, 'stale MOVE frame')
            need(r==((dims[a]-dims[b]) if rev else (dims[b]-dims[a])) and r>=0, 'wrong MOVE rank')
            need(transport(a,b,False)==r, 'MOVE transport rank')
            frames[x]=b
            if r: paid[r]+=1
        elif op == 1:
            _,_,y,c,f,flag=e
            need(0<=y<=n and x!=y and flag==int(rev), 'bad ADD')
            need(frames[x]==frames[y]==f, 'ADD without common frame')
            need(centre is not None or y!=n, 'read of closed temporary')
            need(x!=centre, 'write to centre while copied')
            if c & 1: values[x] ^= values[y]
        elif op == 2:
            _,_,y,a,b,r,flag=e
            need(y==n and centre is None and values[n]==0 and frames[n]==-1, 'COPY into dirty temporary')
            need(flag==int(rev) and frames[x]==a, 'stale COPY frame')
            need(transport(a,b,True)==r==7, 'COPY must use actual rank seven')
            values[n]=values[x]; frames[n]=b; centre=x; paid[r]+=1
            copies.append(dict(position=pos,source=x,old=a,new=b,rank=r))
        elif op == 3:
            _,_,y,a,b,r,flag=e
            need(flag==int(rev) and y==n and centre==x, 'unmatched ERASE')
            need(frames[x]==a and frames[n]==b and values[n]==values[x], 'invalid ERASE guard')
            need(r==(7 if rev else 0), 'wrong ERASE record')
            need(transport(a,b,True)==7, 'ERASE transport')
            values[n]=0; frames[n]=-1; centre=None
        else:
            raise Reject('unknown opcode')
    expected=[(1<<r) ^ ((1<<(r-v)) if v<=r<2*v else 0) for r in range(n)] + [0]
    need(values==expected and centre is None, 'incorrect dirty endpoint')
    need(frames[:-1]==(w['start'] if rev else w['final']), 'wrong final frames')
    need(len(copies)==9, 'copy count')
    return dict(records=len(events),symbolic_columns=n,private_final_zero=True,
                copies=copies,profile=dict(sorted(paid.items())),transport_pairs=transport.cache_info().currsize)


def pending_axes(e):
    a,b = e['source_level'], e['target_level']
    axes = list(range(1,8+7*b)) if a==-1 else list(range(8+7*a,8+7*b))
    need(len(axes)==e['rank'], 'idle rank disagrees with level interval')
    return axes


def permutation(target):
    need(len(target)==8 and len(set(target))==8 and all(0<=x<64 for x in target), 'bad eight-axis slot')
    return tuple(target + [i for i in range(64) if i not in target])


def five_helper_operators(first):
    """Exact 128-basis-column address action, with the same physical memory."""
    def compose(a,b):
        return tuple(a[b[i]] for i in range(len(a)))
    def inverse(a):
        return tuple(a.index(i) for i in range(len(a)))
    def ds(axes):
        return tuple(i+64 if i in axes else i-64 if i-64 in axes else i for i in range(128))
    result=tuple(range(128)); sigmas=[]
    for axes in first['ambient_axes']:
        p=permutation(axes); sigma=p+tuple(x+64 for x in p); sigmas.append(sigma)
        actual=compose(sigma,compose(ds(set(range(8))),inverse(sigma)))
        need(actual==ds(set(axes)), 'wrong full residual conjugation')
        result=compose(actual,result)
    need(len(set(sigmas))==5, 'five-helper owner map not injective')
    result=compose(ds({41,42}),result)
    need(result==ds(set(range(1,43))), 'five-helper completion operator')
    return dict(address_basis_columns=128,helper_operators=5,remainder_axes=[41,42],
                pending_axes=list(range(1,43)),completion_matches=True)


def ownership(t,w,g):
    n=2*w['v']+w['R']; v=w['v']; m=t['m']; stages=t['stages']; reps=t['replicas']
    need((v,w['R'],m,stages,reps)==(111,439,64,9,32), 'scope changed')
    need(w['start'][2*v:]==[0]*w['R'], 'nonzero helper entrance outside scope')
    need(len(g['ports'])==v, 'port count')
    # Fixed family chart A_q=[q/2 | U_q], independent of stage and idle child.
    for j,p in enumerate(g['ports']):
        need(p['port']==j and p['q']==w['lines'][j], 'stale geometry labels')
        a=tuple((Q(p['q'][i],2),)+tuple(map(Q,p['complement_columns'][i])) for i in range(8))
        need(mul(trans(a),a)==ident(8) and dyadic(a), 'family chart not dyadic orthogonal')
        rho=tuple(tuple(map(Q,row)) for row in p['rho15'])
        line=tuple(tuple(Q(p['q'][i]*p['q'][k],4) for k in range(8)) for i in range(8))
        u=tuple(tuple(map(Q,row)) for row in p['complement_columns'])
        expected=tuple(line[i]+u[i] for i in range(8)) + tuple(tuple(u[k][i] for k in range(8))+(Q(0),)*7 for i in range(7))
        need(rho==expected and mul(rho,rho)==ident(15) and rho==trans(rho), 'wrong data chart')
        need(len(p['routes'])==stages, 'stage route count')
        for s,route in enumerate(p['routes']):
            axes=list(range(8)) + ([] if s==0 else list(range(8+7*(s-1),8+7*s)))
            need(route['stage']==s and route['axes']==axes, 'wrong stage embedding')
    schedule=t['schedule']; idle={e['idx']:e for e in schedule if e['kind']=='idle'}
    pending={i:pending_axes(e) for i,e in idle.items()}
    idle_union=defaultdict(set)
    for i,e in idle.items():
        need(not idle_union[e['pair']].intersection(pending[i]), 'overlapping idle intervals')
        idle_union[e['pair']].update(pending[i])
    last={}; seen=[]; windows={}; positions={}; levels=[-1]*4
    for pos,e in enumerate(schedule):
        if e['kind']=='local_cover_sweep':
            need(levels[e['pair']]==e['stage']-1, 'local stage enters wrong data level')
            levels[e['pair']]=e['stage']
            seen.append((pos,e['stage'],e['pair'])); last[e['pair']]=pos; positions[e['stage']]=pos
        elif e['kind']=='bridge':
            need(levels[e['src']]==levels[e['dst']], 'bridge at unequal levels')
            last[e['src']]=last[e['dst']]=pos
        elif e['kind']=='idle':
            need(levels[e['pair']]==e['source_level'], 'idle source level mismatch')
            levels[e['pair']]=e['target_level']
            windows[e['idx']]={s for p,s,pair in seen if last.get(e['pair'],-1)<p<pos and pair!=e['pair']}
        else:
            need(e['kind']=='exchange' and pos==len(schedule)-1, 'unknown schedule event')
            need(levels==[8]*4, 'terminal levels')
    occupied=defaultdict(set); hosts={}
    for child,cp,off,width,stage,h in t['hosting']['slots']:
        need(child in idle and stage in windows[child], 'host outside untouched window')
        need(0<=cp<2*v and 0<=h<w['R'] and width==8, 'bad host descriptor')
        need(0<=off and off+width<=len(pending[child]), 'host outside pending projector')
        axes=pending[child][off:off+width]; key=(child,cp)
        need(not occupied[key].intersection(axes), 'overlapping host axes')
        occupied[key].update(axes)
        need((stage,h) not in hosts, 'duplicate helper occurrence')
        hosts[stage,h]=(child,cp,off,axes)
    need(len(hosts)==stages*w['R'], 'omitted helper occurrence')
    expected_windows={str(i):[idle[i]['pair'],idle[i]['rank'],sorted(ws)] for i,ws in windows.items() if idle[i]['rank'] and ws}
    need(t['hosting']['windows']==expected_windows, 'stale window certificate')
    maxima={}; first=None; patterns=set()
    need(len(t['calls'])==stages*reps, 'call count')
    for count,c in enumerate(t['calls']):
        s,rep,pair=c['stage'],c['replica'],c['pair']
        need((s,rep)==divmod(count,reps), 'call order')
        event=schedule[positions[s]]
        need(pair==event['pair'] and c['orientation']==('reverse' if event['reverse'] else 'forward'), 'call orientation')
        need(len(c['owners'])==n, 'owner count')
        keys=set(); by_family=defaultdict(list)
        for role,(fam,route) in enumerate(c['owners']):
            if role<2*v:
                side=role//v
                if event['reverse']: side=1-side
                need(fam==rep*8*v+(2*pair+side)*v+role%v and route==['data',s,role%v], 'wrong data owner')
                key=(fam,'data')
            else:
                child,cp,off,axes=hosts[s,role-2*v]; hp=idle[child]['pair']; side,port=divmod(cp,v)
                need(hp!=pair and fam==rep*8*v+(2*hp+side)*v+port, 'wrong hosted family')
                need(route==['hosted',child,off,8], 'wrong hosted route')
                perm=permutation(axes); patterns.add(perm)
                key=(fam,perm); by_family[fam].append((role,child,axes))
            need(key not in keys, 'physical owner collision'); keys.add(key)
        max_count=max(map(len,by_family.values())); maxima[s]=max(maxima.get(s,0),max_count)
        for fam,roles in by_family.items():
            union=set()
            for role,child,axes in roles:
                need(not union.intersection(axes), 'same-call cross-child projector collision')
                union.update(axes)
            if len(roles)==5 and first is None:
                first=dict(stage=s,replica=rep,pair=pair,family=fam,roles=[x[0] for x in roles],
                           children=[x[1] for x in roles],ambient_axes=[x[2] for x in roles])
    remainder=Counter(); summaries={}
    for i,e in idle.items():
        counts=Counter(e['rank']-len(occupied[i,cp]) for cp in range(2*v))
        if str(i) in expected_windows: summaries[str(i)]={str(r):num for r,num in sorted(counts.items())}
        for r,num in counts.items():
            if r: remainder[r]+=num*reps
    need(t['hosting']['remainders']==summaries, 'wrong remainder schedule')
    need(first['family']==666 and first['roles']==list(range(232,237)), 'five-helper fixture changed')
    need(t['live']==28416 and t['private_centre_reserve']==9 and all(x==0 for x in t['banks_per_stage'].values()), 'unexpected bank stock')
    return dict(first_five_helper=first,max_helpers_per_family=maxima,calls=len(t['calls']),
                hosted_occurrences=len(hosts)*reps,distinct_slot_permutations=len(patterns),
                idle_remainder_profile=dict(sorted(remainder.items()))),remainder


def run():
    source=json.loads((HERE/'SOURCES.json').read_text())
    for pin in source['files']:
        if pin['usage']=='input':
            need(hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256'], 'source hash: '+pin['path'])
    w,t,g=read(WORD),read(HOST),read(GEO)
    need(t['geometry_sha256']==hashlib.sha256((ROOT/GEO).read_bytes()).hexdigest(), 'template/geometry binding')
    results=[projection([w['lines'][i] for i in f]) for f in w['frames']]
    ps=[x[0] for x in results]; dims=[x[1] for x in results]
    need(all(dyadic(p) for p in ps), 'projector has an extra excluded prime')
    need(ps[0]==tuple((Q(0),)*8 for _ in range(8)) and ps[1]==ident(8), 'zero/full frames')
    for j,line in enumerate(w['lines']):
        p=tuple(tuple(Q(x*y,4) for y in line) for x in line)
        need(ps[w['start'][j]]==p and ps[w['final'][j]]==ident(8), 'source boundary frame')
        need(ps[w['start'][w['v']+j]]==ps[0] and ps[w['final'][w['v']+j]]==sub(ident(8),p), 'target boundary frame')
    need(all(ps[f]==ident(8) for f in w['final'][2*w['v']:]), 'helper final frame')
    iso=next(x for x in read('research/e8-bit-carrier-skeleton/data/eleven/residual-isometries.json') if x['frame']==0)
    need(t['residual_isometries']==[iso] and iso['entrance_rank']==0, 'residual isometry binding')
    programs,record_hash=literal_programs(w,dims)
    need(programs==t['local_programs'] and record_hash==t['source_record_sha256'], 'word/template binding')
    for c in t['calls']:
        need(c['local_hash']==hashlib.sha256(json.dumps(programs[c['orientation']],separators=(',',':')).encode()).hexdigest(), 'call program binding')
    local={ori:local_replay(es,w,ps,dims,ori=='reverse') for ori,es in programs.items()}
    owners,remainder=ownership(t,w,g)
    five=five_helper_operators(owners['first_five_helper'])
    profile=Counter(remainder)
    for c in t['calls']:
        profile.update(local[c['orientation']]['profile'])
    need(sum(r*n for r,n in profile.items())==1808352 and 64*t['live']-sum(r*n for r,n in profile.items())==10272, 'paid rank mass')
    controls=[]
    def rejects(name,fn):
        try: fn()
        except Reject as e: controls.append(dict(name=name,reason=str(e)))
        else: raise Reject('negative control accepted: '+name)
    def program_mutate(fn,rev=False):
        es=copy.deepcopy(programs['reverse' if rev else 'forward']); fn(es)
        return local_replay(es,w,ps,dims,rev)
    def host_mutate(fn):
        q=copy.deepcopy(t); fn(q); return ownership(q,w,g)
    def change_slot(q,h,offset):
        # Change both the slot and every replica's owner coherently. Rejection
        # must come from geometry, not a stale descriptor or input hash.
        slot=next(x for x in q['hosting']['slots'] if x[4:]==[2,h])
        slot[2]=offset
        for c in q['calls']:
            if c['stage']==2:
                c['owners'][222+h][1][2]=offset
    rejects('duplicate physical owner',lambda:host_mutate(lambda q:change_slot(q,11,0)))
    rejects('wrong same-rank hosted axes',lambda:host_mutate(lambda q:change_slot(q,10,1)))
    rejects('host slot outside last-touch window',lambda:host_mutate(lambda q:q['hosting']['slots'][0].__setitem__(4,8)))
    def wrong_idle_level(q):
        e=next(e for e in q['schedule'] if e['kind']=='idle' and e['idx']==5)
        e.update(source_level=6,target_level=7)  # keep its rank seven
    rejects('idle child before the right data level',lambda:host_mutate(wrong_idle_level))
    rejects('stale MOVE chart',lambda:program_mutate(lambda es:next(e for e in es if e[0]==0).__setitem__(2,1)))
    rejects('rank-eight substitution at rank-seven COPY',lambda:program_mutate(lambda es:next(e for e in es if e[0]==2).__setitem__(5,8)))
    rejects('wrong same-rank COPY frame',lambda:program_mutate(lambda es:next(e for e in es if e[0]==2).__setitem__(3,511)))
    def early_erase(es):
        i=next(i for i,e in enumerate(es) if e[0]==2)
        j=next(j for j in range(i+1,len(es)) if es[j][0]==3)
        es.insert(i+1,es.pop(j))
    rejects('premature temporary erasure',lambda:program_mutate(early_erase))
    def dirty_temp(es):
        i=next(i for i,e in enumerate(es) if e[0]==3); del es[i]
    rejects('missing temporary cleanup',lambda:program_mutate(dirty_temp))
    rejects('reflected rank-eight COPY',lambda:program_mutate(lambda es:next(e for e in es if e[0]==2).__setitem__(5,8),True))
    p,q=ps[510],ps[511]
    need(dims[510]==dims[511]==7 and p!=q and swap(p)!=swap(ident(8)), 'transport mutation not discriminating')
    witness=next(j for j in range(16) if any(swap(p)[i][j]!=swap(ident(8))[i][j] for i in range(16)))
    same_rank_witness=next(j for j in range(16) if any(swap(p)[i][j]!=swap(q)[i][j] for i in range(16)))
    def witness_columns(b,j):
        return dict(field='Q',input_basis_column=j,
                    correct=[str(swap(p)[i][j]) for i in range(16)],
                    incorrect=[str(swap(b)[i][j]) for i in range(16)])
    return dict(status='PASS_PR589_OWNER_AND_FRAMED_CALL_CERTIFICATES',
        scope='Exact finite certificates for PROOF.md; no Lean kernel proof, full cold replay, route cost, all-size compiler or new multiplication bound.',
        word_canonical_sha256=hashlib.sha256(json.dumps(w,separators=(',',':'),sort_keys=True).encode()).hexdigest(),
        template_payload_sha256=hashlib.sha256(gzip.decompress((ROOT/HOST).read_bytes())).hexdigest(),
        record_sha256=record_hash,frames=len(ps),address_fields='all fields of characteristic other than 2 (dyadic certificate identities)',
        local=local,ownership=owners,five_helper_operator=five,profile=dict(sorted(profile.items())),rank_mass=1808352,rank_deficit=10272,
        rank_seven_vs_eight_witness_column=witness,wrong_rank_seven_frame_witness_column=same_rank_witness,
        transport_witnesses=dict(rank_eight=witness_columns(ident(8),witness),
                                 wrong_rank_seven_frame=witness_columns(q,same_rank_witness)),
        negative_controls=controls)


if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--write-receipt',type=Path); args=ap.parse_args()
    try:
        result=run()
        if args.write_receipt:
            args.write_receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        else:
            need(json.loads((HERE/'RESULT.json').read_text())==json.loads(json.dumps(result)), 'stale RESULT.json')
        print(result['status']+' frames='+str(result['frames'])+' calls=288 columns=661 controls='+str(len(result['negative_controls']))+' no_new_kappa')
    except Reject as e:
        raise SystemExit('REJECT: '+str(e))
