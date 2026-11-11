"""Rational support of charged endpoint splits on the literal #7277 word."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys
from time import monotonic

HEAD = 'ed090b57ed88f8859e5ff4643645099e6ba856ea'
WORD = 'complex/source/inputs/WORD.json.gz'
PINS = {
    'round30/'+WORD: '2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756',
    'round37/preflight/PRICE.json': 'bc6134776a077b4ae3ef595c6000563062b2a42a3684a3852ba4f2f77b8dc726',
    'round36/cochart-audit/verify.py': '58cab0bb2f24fe29d0e190cbe3cc0dc85f889ec4af66b5a02328d1e1d0e37e8a',
    'round36/incremental/predecessor_split.py': '999b9eeabe5cd1a7e3ec014d1a449f850b4ac9bfb19749cddef41ae12cd0b405',
    'round36/incremental/support.py': 'f3e6eeb879480715c5c32c1a390a63c57d26ea1c9a9cbdb89b83ca34260e47f6',
}


def read_json(raw):
    def unique(items):
        result = dict(items)
        assert len(result)==len(items),'Duplicate keys'
        return result
    return json.loads(raw,object_pairs_hook=unique)


def save(out,name,receipt):
    path = out/(name+'.tmp')
    path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    path.replace(out/name)


def dot(a,b):
    return sum(x*b.get(i,0) for i,x in a.items())


def pure_coefficients(rows, roles, group, add):
    exterior, output = {}, []
    for role in reversed(roles):
        residual = rows[role].copy()
        coefficients = {role:Q(1)}
        while (lead:=max((k for k in residual if k not in group),default=-1))>=0:
            if lead not in exterior:
                exterior[lead] = residual,coefficients
                break
            old,co = exterior[lead]
            scale = -residual[lead]/old[lead]
            add(residual,old,scale)
            add(coefficients,co,scale)
        else:
            output.append((residual,coefficients))
    return output


def admissible(program):
    def smooth(n):
        for p in (2,3,5):
            while n%p==0:
                n//=p
        return n==1
    for op,*e in program:
        q = Q(e[-2])
        if not q or not smooth(q.denominator) or op=='SCALE' and not smooth(abs(q.numerator)):
            return False
    return True


def nominate(word, side, extender, new, t, frame, pivot, ranks, a,b,c,d, check):
    u,v = new
    changed = dict(word,initial=word['initial'].copy(),final=word['final'].copy())
    if side=='input':
        prior = changed['initial'][extender]
        changed['initial'][extender] = u
        changed['program'] = [['MOVE',extender,u,prior,False]]+word['program']
    else:
        prior = changed['final'][extender]
        changed['final'][extender] = v
        changed['program'] = word['program']+[['MOVE',extender,prior,v,False]]
    h = dict(cut_after=t+(side=='input'),frame=frame,pivot=pivot,ranks=ranks)
    h.update({name:{str(i):str(q) for i,q in vector.items()} for name,vector in zip('abcd',(a,b,c,d),strict=True)})
    check(changed,h)
    return dict(extender=extender,side=side,new=new,original_cut=t,split=h,added_move=changed['program'][0 if side=='input' else -1])


def run(roots,out,seconds):
    start = monotonic()
    files = {}
    for name,digest in PINS.items():
        prefix,p = name.split('/',1)
        path = roots[prefix]/p
        assert sha256(path.read_bytes()).hexdigest()==digest,name
        files[name] = path
    word = read_json(gzip.decompress(files['round30/'+WORD].read_bytes()))
    receipt = read_json(files['round37/preflight/PRICE.json'].read_bytes())
    predecessor = runpy.run_path(str(files['round36/cochart-audit/verify.py']))
    sys.path.insert(0,str(roots['round36']/'incremental'))
    from predecessor_split import basis, check_cut
    space,linear,add = (predecessor[name] for name in ('binary_span','linear','add'))
    pure_images = predecessor['pure_images']
    assert receipt['head']==HEAD and receipt['copies']==17 and receipt['typed_signatures']==777
    rows = [r for r in receipt['rows'] if r['old_rank']==7]
    assert len(rows)==90
    assert all(Q(r['complete_margin_interval'][0])>0 for r in rows)
    n,tape = word['public'],word['program']
    spaces = list(map(space,word['frames']))
    dims = list(map(len,word['frames']))
    main = set(word['live']) | {i+112 for i in word['live']}
    main.update(word['hosted']['X2'])
    main.update(word['hosted']['Y2'])
    groups = defaultdict(set)
    for i,(a,b) in enumerate(zip(word['initial'],word['final'],strict=True)):
        if i not in main:
            groups[a,b].add(i)
    options = defaultdict(dict)
    typed = defaultdict(list)
    for row in rows:
        side = row['side']
        a,b = row['prior']
        u,v = row['new']
        g = groups[u,v]
        assert set(row['new_cohort_before_extension'])==g
        assert groups[a,b]==set(row['extender_roles']) and not g&groups[a,b]
        assert (b==v and spaces[u]<spaces[a] and dims[a]-dims[u]==1 if side=='input'
                else a==u and spaces[b]<spaces[v] and dims[v]-dims[b]==1)
        parts = tuple(row['parts'])
        assert parts in {(2,6),(3,5),(4,4)}
        assert dims[v]-dims[u]==sum(parts)==8
        key = u,v,*parts
        typed[key].append(row)
        for extender in row['extender_roles']:
            assert extender not in options[key]
            options[key][extender] = row
    assert len(options)==78
    universe = {key:groups[key[:2]]|opts.keys() for key,opts in options.items()}
    possible = [tuple(key for key in options if dims[f]-dims[key[0]] in key[2:]
                      and spaces[key[0]]<sp<spaces[key[1]])
                for f,sp in enumerate(spaces)]
    chart = word['initial']+[None]*word['owned_fields']
    live = defaultdict(set)
    for i,f in enumerate(chart[:n]):
        live[f].add(i)
    schedule, decoded = defaultdict(list), []
    coverage = Counter()
    typed_cuts = Counter()
    for t,(op,dst,*args) in enumerate(tape):
        src,q = dst,None
        if op=='MOVE':
            a,b,owned = args
            assert chart[dst]==a and owned==(dst>=n)
            assert spaces[a]<spaces[b] or owned and spaces[b]<spaces[a]
            live[a].remove(dst)
            live[b].add(dst)
            chart[dst]=b
            touched=(a,b)
        elif op=='INIT':
            f = args[0]
            assert chart[dst] is None
            live[f].add(dst)
            chart[dst]=f
            touched=(f,)
        elif op=='CLEAR':
            f = args[0]
            assert chart[dst]==f
            live[f].remove(dst)
            chart[dst]=None
            touched=(f,)
        else:
            f = args[-1]
            src = args[0] if op in ('ADD','COPY') else dst
            assert chart[dst]==chart[src]==f
            q = Q(args[-2])
            touched=(f,)
        decoded.append((op,dst,src,q))
        for f in touched:
            eligible = [key for key in possible[f] if live[f]&universe[key]]
            if not eligible:
                continue
            roles = tuple(sorted(live[f]))
            for key in eligible:
                schedule[t].append((key,f,roles))
                coverage[key]+=1
                g=groups[key[:2]]
                for i,row in enumerate(typed[key]):
                    if live[f] & (g|set(row['extender_roles'])):
                        typed_cuts[key,i]+=1
    assert chart==word['final']+[None]*word['owned_fields']
    save(out,'INVENTORY.json',dict(head=HEAD,pins=PINS,seconds=seconds,
         selected_signatures=len(rows),prior_rank_eight=24,
         smaller_unvisited=receipt['typed_signatures']-len(rows)-24,
         union_groups=len(options),cuts=sum(coverage.values()),
         counts=[dict(endpoints=k[:2],parts=k[2:],cohort=len(groups[k[:2]]),
                      extenders=len(options[k]),cuts=coverage[k]) for k in options],
         typed=[dict(side=row['side'],prior=row['prior'],new=k[:2],parts=k[2:],cuts=typed_cuts[k,i])
                for k,group in typed.items() for i,row in enumerate(group)]))

    counts = Counter()
    by_parts = defaultdict(Counter)
    unresolved = []
    snaps = defaultdict(list)
    candidate = None
    def checkpoint(phase,t):
        save(out,'SUPPORT.json',dict(head=HEAD,phase=phase,clock=t,candidate=candidate,
             counts=dict(counts),by_parts=[dict(endpoints=k[:2],parts=k[2:],**by_parts[k]) for k in options],
             unresolved=unresolved))
    def bump(key,name):
        counts[name]+=1
        by_parts[key][name]+=1
    def identity():
        return [{i:Q(1)} for i in range(n)]+[{} for _ in range(word['owned_fields'])]
    forward = identity()
    for t,e in enumerate(decoded):
        if monotonic()-start>=seconds:
            return checkpoint('prefix_cap',t)
        linear(forward,*e)
        for key,f,roles in schedule.get(t,()):
            pp = pure_images(forward,roles,universe[key])
            bump(key,'prefix_checked')
            if pp:
                snaps[t].append((key,f,roles,pp))
                bump(key,'prefix_nonzero')
        if t%4096==0:
            checkpoint('prefix',t)
    assert all(forward[i]=={i:Q(1)} for i in set().union(*universe.values()))
    backward = identity()
    for t in reversed(range(len(decoded))):
        if monotonic()-start>=seconds:
            return checkpoint('suffix_cap',t)
        for key,f,roles,pp in snaps.get(t,()):
            ss = pure_images(backward,roles,universe[key])
            bump(key,'suffix_checked')
            if not any(dot(c,d) for c in pp for d in ss):
                continue
            bump(key,'union_nonzero')
            # Recover the exact prefix only at cuts surviving the union test.
            local = identity()
            for e in decoded[:t+1]:
                linear(local,*e)
            pivot_stock = set(roles)
            u,v = key[:2]
            g = groups[u,v]
            for extender,row in options[key].items():
                if monotonic()-start>=seconds:
                    unresolved.append(dict(clock=t,frame=f,endpoints=key[:2],parts=key[2:],reason='extender_cap'))
                    return checkpoint('extender_cap',t)
                group = g|{extender}
                pivots = sorted(pivot_stock&group)
                if not pivots:
                    continue
                cc = pure_coefficients(local,roles,group,add)
                dd = pure_coefficients(backward,roles,group,add)
                bump(key,'exact_extender_checked')
                nonzero = False
                for c,a in cc:
                    for d,b in dd:
                        paired = dot(c,d)
                        if not paired:
                            continue
                        nonzero = True
                        if dot(a,b)!=paired:
                            continue
                        for scale in (Q(1),paired,Q(-1)):
                            aa = {i:q/scale for i,q in a.items()}
                            co = {i:q/scale for i,q in c.items()}
                            bb = {i:q*scale/paired for i,q in b.items()}
                            do = {i:q*scale/paired for i,q in d.items()}
                            for pivot in pivots:
                                try:
                                    ops = basis(aa,bb,pivot,f)+basis(co,do,pivot,u)
                                except ValueError:
                                    continue
                                if admissible(ops):
                                    candidate = nominate(word,row['side'],extender,(u,v),t,f,pivot,
                                        [dims[f]-dims[u],dims[v]-dims[f]],aa,bb,co,do,check_cut)
                                    candidate['price_margin'] = row['complete_margin_interval']
                                    return checkpoint('witness',t)
                if nonzero:
                    unresolved.append(dict(clock=t,frame=f,endpoints=key[:2],parts=key[2:],extender=extender,reason='no_admissible_basis_pair'))
        linear(backward,*decoded[t],reverse=True)
        if t%4096==0:
            checkpoint('suffix',t)
    checkpoint('exhausted' if not unresolved else 'unresolved_basis_pairs',0)


if __name__=='__main__':
    assert __debug__
    p = ArgumentParser()
    p.add_argument('round30',type=Path)
    p.add_argument('round36',type=Path)
    p.add_argument('round37',type=Path)
    p.add_argument('out',type=Path)
    p.add_argument('--seconds',type=int,default=175)
    a = p.parse_args()
    a.out.mkdir()
    run({k:getattr(a,k) for k in ('round30','round36','round37')},a.out,a.seconds)
