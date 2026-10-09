"""Independent passive-witness verifier. No producer/author module imports."""
if not __debug__:
    raise RuntimeError('Assertions are required; -O/-OO/PYTHONOPTIMIZE are unsupported')
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
from collections import Counter
import struct,hashlib,json,gzip,time,resource,math
ROOT=Path(__file__).resolve().parent; BASE=ROOT.parent/'explore_complex_ceiling_breakthrough/pr97_port'; REPO=ROOT.parents[1]
t0=time.monotonic()
manifest=json.loads((BASE/'H24_WITNESS_MANIFEST.json').read_text()); input_hashes={}
for entry in manifest['files']:
    p=REPO/entry['path'];b=p.read_bytes();assert len(b)==entry['bytes'];assert hashlib.sha256(b).hexdigest()==entry['sha256'];input_hashes[entry['path']]=entry['sha256']
assert manifest['head']=='f5f9c56e637463cac1e300d1589ccf42838f688a'
b=(BASE/'H24_GRAPH.bin').read_bytes(); h,v,ng,nr=struct.unpack_from('<4I',b);assert h==24 and v==math.comb(h,3)
assert len(b)==16+28*ng+4*nr
records=list(struct.iter_unpack('<7I',b[16:16+28*ng])); roots=list(struct.unpack_from('<'+'I'*nr,b,16+28*ng));del b
npieces=20240
assert nr==npieces+h and ng==v+28944
size=1+max(r[0] for r in records);nodes=[None]*size;signals=[None]*size;signals[0]=()
triples=list(combinations(range(h),3));tmasks=[sum(1<<i for i in t) for t in triples];full=(1<<h)-1;srcfull=(1<<v)-1
point=[sum(1<<j for j,t in enumerate(triples) if i in t) for i in range(h)]
def plus(a,b):
    out=[];carry=0
    for i in range(max(len(a),len(b))):
        x=a[i] if i<len(a) else 0;y=b[i] if i<len(b) else 0
        out.append(x^y^carry);carry=(x&y)|(x&carry)|(y&carry)
    if carry:out.append(carry)
    while out and not out[-1]:out.pop()
    return tuple(out)
def require_node(n,allow_zero=False):
    if type(n) is not int or (n==0 and not allow_zero) or n<0 or n>=len(nodes) or (n and nodes[n] is None):
        raise ValueError(('Invalid graph/frame node ID',n))
def framekey(n):
    require_node(n,True)
    if n==0:return (0,0,0)
    _,_,c,u,r,t=nodes[n]
    return (t,c,u) if t==1 else ((t,0,u) if t==2 else (t,c,0))
def rank(n):
    require_node(n,True)
    return 0 if n==0 else nodes[n][4]
def contains(x,y):
    require_node(x,True);require_node(y,True)
    if x==0:return True
    if y==0:return False
    _,_,cx,ux,rx,tx=nodes[x];_,_,cy,uy,ry,ty=nodes[y]
    if tx==ty==1:return not(cy&~cx or ux&~uy)
    if tx in (1,2) and ty==2:return not ux&~uy
    if tx==1 and ty==3:return bool(cx&cy)
    if tx==2 and ty==3:return not ux&~cy
    if tx==3 and ty==2:return uy==full
    return tx==ty==3 and cx==cy
last=0
for x,a,b,c,u,r,t in records:
    assert x>last;last=x;nodes[x]=(a,b,c,u,r,t)
    assert 1<=r<=h and t in (1,2) and 0<c|u<=full
    if x<=v:
        assert a==b==0 and c==u==tmasks[x-1] and r==1 and t==1;signals[x]=(1<<(x-1),)
    else:
        assert 0<a<x and 0<b<x and nodes[a] and nodes[b]
        na,nb=nodes[a],nodes[b]
        assert u==na[3]|nb[3]
        sig=plus(signals[a],signals[b]);signals[x]=sig
        assert len(sig)<=2 and (len(sig)<2 or not(sig[0]&sig[1]))
        if t==3:
            assert c.bit_count()==1 and r==h-1
            i=c.bit_length()-1;assert all(not(p&~point[i]) for p in sig)
        else:
            assert na[5]!=3 and nb[5]!=3 and c==na[2]&nb[2]
            assert len(sig)==1 and not(signals[a][0]&signals[b][0])
            assert (t==1 and c.bit_count()>=2 and r==sig[0].bit_count()) or (t==2 and c.bit_count()<2 and r==u.bit_count())
        assert contains(a,x) and contains(b,x)
assert all(nodes[i] for i in range(1,v+1))
# Independently bind every split signed side and all T/E centers.
terminal_data=json.loads((BASE/'H24_TERMINALS.json').read_text());side_table=terminal_data['sides'];center_table=terminal_data['centers']
assert len(side_table)==npieces and len(center_table)==h
side_targets=[];pos=[0]*v;neg=[0]*v
for expected_j,row in enumerate(side_table):
    j,node,target,num,den=row;require_node(node)
    assert type(j) is int and j==expected_j and node==roots[j]
    assert type(target) is int and 0<=target<v and num in (-1,1) and den==2
    assert len(signals[node])==1;mask=signals[node][0];acc=pos if num==1 else neg
    assert not(acc[target]&mask);acc[target]|=mask;side_targets.append(target)
for j,(a,b,c) in enumerate(triples):
    assert pos[j]==srcfull&~(point[a]|point[b]|point[c])
    assert neg[j]==((point[a]&point[b]&~point[c])|(point[a]&point[c]&~point[b])|(point[b]&point[c]&~point[a]))
for i,item in enumerate(center_table):
    assert item==dict(index=i,node=roots[npieces+i],name=['E',i] if i<h-1 else ['T'])
    node=item['node'];assert signals[node]==((srcfull^point[i],) if i<h-1 else (srcfull,))
    assert nodes[node][5]==2 and nodes[node][3]==(full^(1<<i) if i<h-1 else full)
def characteristic(n):
    require_node(n,True)
    if n==0:return 0
    _,_,c,u,r,t=nodes[n]
    return (u^c)^(c if r%2 else 0) if t==1 else u
alternating_calls=Counter()
# Reconstruct region ownership and exact use IDs from graph data.
region={};reps=[];owner=[-1]*size;ins=[]
for x,*_ in records:
    k=framekey(x)
    if k not in region:region[k]=len(reps);reps.append(x);ins.append(set())
    owner[x]=region[k]
for x,a,b,*_ in records:
    for y in (a,b):
        if y and owner[y]!=owner[x]:ins[owner[x]].add(y)
uses=[]
for k,ys in enumerate(ins):
    for y in sorted(ys):uses.append((y,reps[k],False))
for x in roots:uses.append((x,reps[owner[x]],True))
assert len(uses)==71591 and len(reps)==24410
non_source_regions={k for k,ys in enumerate(ins) if ys}
# Exact source-vector linear relation, clearing rational denominators before
# adding positive and negative coefficient-bitplanes. No modular hashing.
relations_checked=0
def relation(terms):
    global relations_checked
    for n,c in terms:require_node(n,True)
    terms=[(n,Q(c)) for n,c in terms if n and c];D=1
    for _,c in terms:D=math.lcm(D,c.denominator)
    pos=();neg=()
    for n,c in terms:
        c=c.numerator*(D//c.denominator);w=abs(c);shift=0
        while w:
            if w&1:
                q=(0,)*shift+signals[n]
                if c>0:pos=plus(pos,q)
                else:neg=plus(neg,q)
            w>>=1;shift+=1
    relations_checked+=1;assert pos==neg,('Incorrect exact source relation',terms)
def qread(num,den):
    assert type(num) is int and type(den) is int and den>0
    return Q(num,den)
expected=json.loads((BASE/'H24_WITNESS_REPLAY_SCREEN.json').read_text());R=expected['profile']['R'];assert R==40011
frames=[0]*R;sig=[0]*R;state=['unused']*R;promised={};pending_role={};seen_uses=set();consumed=set();injected=set();seen_blocks=set();last_consumed=[None]*R
H=Counter();counts=Counter();reltypes=Counter();terminal_slots=set();terminal_ids=set();centers={};side_records={};mixer_gates=0;max_num=max_den=1;maxrow=Q(1);maxblock=0;started_blocks=False;footer=None
reclaim_old={};eventnum=0

def coeff_seen(c):
    global max_num,max_den
    max_num=max(max_num,abs(c.numerator));max_den=max(max_den,c.denominator)

def require_slot(s):
    if type(s) is not int or not 0<=s<R:raise ValueError(('Invalid original slot ID',s))
def live(s):
    require_slot(s)
    assert state[s] not in ('unused','terminal','done')
for eventnum,line in enumerate(gzip.open(BASE/'H24_EVENTS_CLAIMED.jsonl.gz','rt'),1):
    assert footer is None, 'Records after footer'
    e=json.loads(line);kind=e[0];counts[kind]+=1
    if kind=='header':
        assert eventnum==1;hdr=e[1]
        assert hdr['head']==manifest['head'] and hdr['h']==h and hdr['v']==v and hdr['R']==R
        assert hdr['initial_original_dirty_roles']==list(range(R)) and hdr['initial_frame']==0
        assert hdr['graph_sha256']==input_hashes['research/explore_complex_ceiling_breakthrough/pr97_port/H24_GRAPH.bin']
        for rel,sha in hdr['source_hashes'].items():assert hashlib.sha256((ROOT.parent/rel).read_bytes()).hexdigest()==sha
        assert hdr['terminal_binding_sha256']==hashlib.sha256((BASE/'H24_TERMINALS.json').read_bytes()).hexdigest()
        assert hdr['stage2_exterior']=='Actual paid552 entrance C_B; no translated-gauge exit substitution'
    elif kind=='activate':
        _,s,old,E=e;require_slot(s);require_node(E);assert 0<=s<R and state[s]=='unused' and old==0 and nodes[E]
        assert frames[s]==0 and sig[s]==0;frames[s]=E;state[s]='local';H[rank(E)]+=1
        if characteristic(E)==0:alternating_calls['entrance']+=1
    elif kind=='inject':
        _,s,source,c,E,claim=e;live(s);assert not started_blocks
        assert state[s]=='local' and s not in injected and sig[s]==0 and 0<=source<v
        assert qread(*c)==1 and claim==source+1 and frames[s]==E and framekey(E)==framekey(claim)
        injected.add(s);sig[s]=claim
    elif kind=='promise':
        _,uid,s,node,G,terminal=e;live(s)
        assert 0<=uid<len(uses) and uses[uid]==(node,G,terminal)
        assert uid not in seen_uses and s not in pending_role and state[s]=='local'
        relation([(sig[s],1),(node,-1)]);assert contains(frames[s],G)
        seen_uses.add(uid);promised[uid]=(s,node,G,terminal);pending_role[s]=uid;state[s]='pending'
    elif kind=='consume':
        _,uid,s=e;require_slot(s);assert uid in promised and pending_role[s]==uid and state[s]=='pending'
        ss,node,G,terminal=promised.pop(uid);assert ss==s;relation([(sig[s],1),(node,-1)])
        assert contains(frames[s],G);del pending_role[s];state[s]='local';consumed.add(uid);last_consumed[s]=(uid,node,G,terminal)
    elif kind=='raise':
        _,s,old,E=e;live(s);assert state[s]!='cleared' and frames[s]==old and contains(old,E)
        if s in pending_role:assert contains(E,promised[pending_role[s]][2])
        d=rank(E)-rank(old);assert d>=0
        if d:
            H[d]+=1
            if characteristic(old)==characteristic(E):alternating_calls['raise']+=1
        frames[s]=E
    elif kind=='block':
        _,slots,rows,E,labels,ops=e;started_blocks=True;n=len(slots);maxblock=max(maxblock,n)
        assert 0<n<=8 and len(set(slots))==n and len(rows)==len(labels)==n
        k=region[framekey(E)];assert k in non_source_regions and k not in seen_blocks;seen_blocks.add(k)
        for s in slots:live(s)
        assert {last_consumed[s][1] for s in slots}==ins[k]
        for s in slots:
            live(s);assert state[s]=='local' and frames[s]==E and last_consumed[s][2]==E and not last_consumed[s][3]
        M=[]
        for rr in rows:
            row=[Q(0)]*n;seen=set()
            for i,a,b in rr:assert 0<=i<n and i not in seen;seen.add(i);row[i]=qread(a,b);coeff_seen(row[i])
            M.append(row);maxrow=max(maxrow,sum(abs(c) for c in row))
        # Check emitted elementary factorization against its complete matrix.
        A=[[Q(i==j) for j in range(n)] for i in range(n)]
        for op in ops:
            if op[0]=='swap':
                _,a,b=op;assert 0<=a<n and 0<=b<n and a!=b;A[a],A[b]=A[b],A[a];mixer_gates+=3
            elif op[0]=='scale':
                _,a,u,w=op;c=qread(u,w);assert 0<=a<n and c;coeff_seen(c);coeff_seen(1/c)
                A[a]=[c*x for x in A[a]];mixer_gates+=1;maxrow=max(maxrow,abs(c),abs(1/c))
            else:
                assert op[0]=='add';_,a,b,u,w=op;c=qread(u,w);assert 0<=a<n and 0<=b<n and a!=b
                A[a]=[x+c*y for x,y in zip(A[a],A[b])];mixer_gates+=1;coeff_seen(c);maxrow=max(maxrow,1+abs(c))
        assert A==M,('Incorrect block factorization',eventnum)
        before=[sig[s] for s in slots];after=[]
        for row,(typ,data) in zip(M,labels):
            assert typ in ('value','carry','retire');claim=data[1] if typ=='carry' else data
            require_node(claim);relation([(ss,c) for ss,c in zip(before,row)]+[(claim,-1)])
            if typ=='carry':assert 0<=data[0]<len(uses) and uses[data[0]][0]==claim
            after.append(claim)
        for s,claim in zip(slots,after):sig[s]=claim;last_consumed[s]=None
    elif kind=='retire':
        _,s,E=e;live(s);assert state[s]=='local' and frames[s]==E and s not in pending_role;state[s]='retired'
    elif kind=='add':
        _,s,terms,E,claim=e;live(s);assert state[s] in ('local','retired') and frames[s]==E
        cs=[]
        for q,num,den in terms:
            live(q);assert q!=s and state[q]!='cleared' and frames[q]==E;c=qread(num,den);coeff_seen(c);cs.append((q,c))
        relation([(sig[s],1)]+[(sig[q],c) for q,c in cs]+[(claim,-1)])
        if state[s]=='retired':
            assert claim==0;reclaim_old[s]=(sig[s],cs);state[s]='cleared'
        else:assert sig[s]==0 and claim!=0
        sig[s]=claim;mixer_gates+=len(cs);maxrow=max(maxrow,1+sum(abs(c) for q,c in cs))
    elif kind=='reuse':
        _,s,E,typ=e;require_slot(s);require_node(E);assert state[s]=='cleared' and sig[s]==0 and frames[s]==E
        old,cs=reclaim_old.pop(s);coefs=[c for q,c in cs]
        assert (typ=='duplicate' and coefs==[-1]) or (typ=='sum' and coefs==[-1,-1]) or (typ=='difference' and coefs==[-1,1])
        state[s]='local';reltypes[typ]+=1
    elif kind=='side_terminal':
        _,s,E,j,node,c,a,b,target_id=e;live(s)
        assert state[s]=='local' and frames[s]==E and 0<=j<npieces and j not in terminal_ids and s not in terminal_slots
        assert node==roots[j] and last_consumed[s]==(len(uses)-nr+j,node,E,True)
        relation([(sig[s],1),(node,-1)]);assert framekey(E)==framekey(node)
        q=qread(*c);assert [j,node,target_id,*c]==side_table[j] and a==h-1-rank(E) and b==1
        # Every triple generator in its frame is orthogonal to target line.
        target=tmasks[side_targets[j]]
        if nodes[E][5]==2:assert not(nodes[E][3]&target)
        else:assert nodes[E][5]==1
        for idx,tmask in enumerate(tmasks):
            if signals[node][0]>>idx&1:assert (tmask&target).bit_count()%2==0
        H[a]+=1
        if a and characteristic(E)==(full^target):alternating_calls['side']+=1
        H[b]+=1;state[s]='terminal';frames[s]=-1;terminal_slots.add(s);terminal_ids.add(j);side_records[j]=(s,node,q)
    elif kind=='center_terminal':
        _,s,E,i,node,r,a,recipe,name=e;live(s)
        assert state[s]=='local' and frames[s]==E and 0<=i<h and i not in centers and s not in terminal_slots
        j=npieces+i;assert node==roots[j] and last_consumed[s]==(len(uses)-nr+j,node,E,True)
        relation([(sig[s],1),(node,-1)]);assert framekey(E)==framekey(node)
        assert r==rank(E)==(h-1 if i<h-1 else h) and a==h-r and recipe=='forward_copy_C_U_inverse;inverse_read_copy_C_U'
        assert name==(['E',i] if i<h-1 else ['T'])
        if characteristic(E)==0:alternating_calls['center_copy']+=1
        if a and characteristic(E)==full:alternating_calls['center_cleanup']+=1
        H[r]+=1;H[a]+=1;state[s]='terminal';frames[s]=-1;terminal_slots.add(s);terminal_ids.add(j);centers[i]=(s,node)
    elif kind=='cleanup':
        _,s,E,a=e;live(s);require_node(E);assert state[s]=='retired' and frames[s]==E and a==h-rank(E)
        H[a]+=1
        if a and characteristic(E)==full:alternating_calls['cleanup']+=1
        state[s]='done';frames[s]=-1
    elif kind=='footer':
        assert footer is None;footer=e[1]
    else:raise AssertionError(('Unknown event',kind))
    if eventnum%100000==0:print(json.dumps(dict(events=eventnum,seconds=time.monotonic()-t0,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)),flush=True)
assert footer is not None and counts['footer']==1 and counts['header']==1
assert seen_blocks==non_source_regions and seen_uses==consumed==set(range(len(uses)))
assert not promised and not pending_role and not reclaim_old and all(s in ('terminal','done') for s in state)
assert len(terminal_slots)==len(terminal_ids)==nr and len(centers)==h
assert dict(reltypes)==expected['relation_types'] and sum(reltypes.values())==7569
assert mixer_gates==footer['literal_mixer_scalar_gate_upper']==133074
assert max_num==footer['max_scalar_numerator']==1 and max_den==footer['max_scalar_denominator']==1
assert maxrow==Q(footer['max_local_row_sum'])==8
assert {k:v for k,v in counts.items() if k!='footer'}==footer['events']
assert dict(H)=={int(t):n for t,n in expected['profile']['histogram'].items()}
assert sum(t*n for t,n in H.items())==h*R+553
# Derive the exact signed T/E scatter from literal terminal records.
bytarget=[[] for _ in range(v)]
for j,(slot,node,c) in side_records.items():bytarget[side_targets[j]].append((node,c))
scatter_terms=0;max_scatter_coeff=Q(0);max_scatter_rowsum=Q(0);center_terms=0
for j,t in enumerate(triples):
    assert len(bytarget[j])==10;terms=list(bytarget[j]);cs=[]
    if h-1 not in t:
        cs=[(centers[h-1][1],Q(1))]+[(centers[i][1],Q(-1,2)) for i in t]
    else:
        cs=[(centers[h-1][1],Q(5-h,2))]+[(centers[i][1],Q(1,2)) for i in range(h-1) if i not in t]
    terms+=cs;relation(terms+[(j+1,-1)]);scatter_terms+=len(terms);center_terms+=len(cs)
    max_scatter_coeff=max(max_scatter_coeff,*[abs(c) for node,c in cs]);max_scatter_rowsum=max(max_scatter_rowsum,sum(abs(c) for node,c in terms))
assert center_terms==12650 and scatter_terms==32890
N=v*v;m=h*h;W=2*N+2*v*R;C=Counter({m-h:2*v*R,(h-1)**2:2*N,h-1:4*N,1:N})
for t,n in H.items():
    if t:C[t]+=2*v*n
assert dict(C)=={int(t):n for t,n in expected['profile']['child_histogram'].items()}=={int(t):n for t,n in hdr['expected_positive_children'].items()}
rankmass=sum(t*n for t,n in C.items());assert W==170157680 and rankmass==98008965648 and W*m-rankmass==1858032
assert not alternating_calls
# Exact rational characteristic enclosure of the independently replayed list.
def log12(q):
    z=(q-1)/(q+1);lo=2*sum(z**(2*k+1)/Q(2*k+1) for k in range(40));return lo,lo+2*z**81/(81*(1-z*z))
l2,u2=log12(Q(2))
def logb(q):
    k=0
    while q>=2:q/=2;k+=1
    l,u=log12(q);return l+k*l2,u+k*u2
logs={t:logb(Q(m,t)) for t in C}
def expb(l,u):
    def s(x):
        a=term=Q(1)
        for k in range(1,9):term*=x/k;a+=term
        return a,term*x/9
    a,_=s(l);b,tail=s(u);return a,b+tail/(1-u/10)
def moment(a):
    lo=hi=Q(0)
    for t,n in C.items():
        l,u=logs[t];p,q=expb(a*l,a*u);lo+=n*t*p;hi+=n*t*q
    return lo/(W*m),hi/(W*m)
lo=Q(86808403,10**12);hi=Q(86808405,10**12);assert moment(lo)[1]<1 and moment(hi)[0]>1
for _ in range(12):
    md=(lo+hi)/2;l,u=moment(md)
    if u<1:lo=md
    elif l>1:hi=md
    else:raise AssertionError('Undecided exact moment bisection')
ab97=Q(31987,500000000);certified_ac=Q(868084,10**10)
assert moment(certified_ac)[1]<1 and Q(9,10)*certified_ac>ab97
# Independently reprice the author's conservative local guard and product rows.
price=json.loads((BASE/'PRECISION_AND_ROWS.json').read_text())
algebraic=4*mixer_gates+2*len(injected)+2*scatter_terms
local=algebraic+8*h+4*R;G=2*v*local+4*N
Eguard=64*(W+m+G+1)**3;literal=2*G*W**2+8*rankmass+4*W+4+32*m
Bguard=rankmass+Eguard;C0=32*m*Bguard**2
assert literal<Eguard and 2*Bguard*(m-(m-h))>=rankmass+Eguard
least=lambda mm,rr:next(k for k in range(1,1000) if mm**k>2*rr**k)
tc=least(m,m-h);tb=least(529,527);wc=W.bit_length();wb=(108516254).bit_length();rows=tc*wc+tb*wb;gap=Q(12000)-Q(51,25)*rows
for key,value in dict(local_mixer_scalar_upper=mixer_gates,source_injection_incidence=len(injected),side_scatter_incidence=npieces,center_scatter_incidence=center_terms,local_weighted_word_and_copy_scan_upper=local,global_scalar_group_upper=G,E=Eguard,literal_charge=literal,semantic_B=Bguard,C0=C0,C1=1,complex_halving_degree=tc,complex_wire_bits=wc,bit_halving_degree=tb,bit_wire_bits=wb,row_coefficient=rows,row_degree=12000,row_gap=str(gap),suffix_slope=48000).items():assert price[key]==value,(key,price[key],value)
assert gap>0 and price['scalar_max_abs']==str(max_scatter_coeff) and price['scalar_denominator_max']==2
# Read footer profile values as a final independent consistency comparison.
assert footer['profile']==expected['profile']
out=dict(assertions_enabled=__debug__,strict_node_and_slot_indices=True,scatter_schema='Only fixed terminal-derived J; unlisted scatter event kinds rejected',status='PASS: original streaming exact fresh-signal/frame/GL/terminal replay; all-dirty word follows from proved signed frame lift, not dense dirty-basis expansion',base=manifest['head'],input_hashes=input_hashes,
    graph_nodes=ng,regions=len(reps),events=eventnum,counts=dict(counts),source_relations_checked=relations_checked,source_injections=len(injected),block_count=len(seen_blocks),max_block_width=maxblock,
    roles=R,reclaims=dict(reltypes),literal_mixer_scalar_gate_upper=mixer_gates,max_mixer_numerator=max_num,max_mixer_denominator=max_den,max_local_matrix_row_sum=str(maxrow),
    scatter_terms=scatter_terms,max_scatter_coefficient=str(max_scatter_coeff),max_scatter_row_sum=str(max_scatter_rowsum),terminal_slots=len(terminal_slots),copied_centers=len(centers),
    one_axis_echo_algebraic_gate_upper=4*mixer_gates+2*len(injected)+2*scatter_terms,all_axis_echo_algebraic_gate_upper=2*v*(4*mixer_gates+2*len(injected)+2*scatter_terms),
    internal_histogram=dict(sorted(H.items())),internal_mass=sum(t*n for t,n in H.items()),W=W,rank=rankmass,deficit=W*m-rankmass,child_histogram=dict(sorted(C.items())),
    exact_root_enclosure=dict(lower=str(lo),upper=str(hi),lower_decimal=float(lo),upper_decimal=float(hi)),certified_complex_saving=str(certified_ac),stopped_complex_saving=str(Q(9,10)*certified_ac),unchanged_bit_saving=str(ab97),alternating_positive_residuals=dict(alternating_calls),zero_rank_endpoint_records=H[0],
    conservative_guard=dict(local=local,G=G,E=Eguard,literal=literal,B=Bguard,C0=C0,C1=1,rows=rows,row_gap=str(gap),complex_halving_degree=tc,complex_wire_bits=wc),
    seconds=time.monotonic()-t0,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
(ROOT/'H24_CHECK_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('input_hashes','internal_histogram','child_histogram','conservative_guard')},indent=2))
