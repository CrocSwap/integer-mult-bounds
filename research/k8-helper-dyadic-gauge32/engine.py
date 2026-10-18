"""One-helper dyadic basis search. @woklerx with OpenAI Codex, Apache-2.0.

Retained copy-init lowering: Sagar Thakrar's complex-dyadic-lowering/lower.py;
original Horner vocabulary: icekylinx PR425/433/531, Jeremy Kothe PR622.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
import copy, gzip, hashlib, json, tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 'ce7ad1b6ab09452c3478723a2e96ed5ff212dc08'
ARCHIVE = 'research/community-frontier1042-audit/selected-replay.tar.gz'
REQUIRED = frozenset([
 ARCHIVE, 'research/community-frontier1042-audit/RESULT.json',
 'research/community-frontier1094-audit/selected-replay.tar.gz',
 'research/community-frontier1094-audit/RESULT.json',
 'research/community-frontier1094-audit/ASSEMBLY.json',
 'docs/research/community-batch1099-review.md',
 'scripts/verify_frontier1094.py',
 'research/complex-dyadic-lowering/lower.py',
 'research/complex-dyadic-lowering/README.md',
 'research/gauge44-slots/code/invoice_allcold.py',
 'research/gauge44-slots/independent/audit_local.py'])
MEMBERS = ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz',
           'INDEPENDENT-LOCAL-REPLAY.json','LOCAL-CHECKS.json')

def require(value, message):
    if not value: raise ValueError(message)

def canonical(value):
    return json.dumps(json.loads(json.dumps(value)), sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode()

def digest(data): return hashlib.sha256(data).hexdigest()
def pin(path):
    b = path.read_bytes()
    return digest(b if path.name.endswith('.gz') else b.replace(b'\r\n',b'\n'))

def check_sources(manifest=None):
    m = manifest if manifest is not None else json.loads((HERE/'SOURCES.json').read_bytes())
    require(m['base'] == BASE and set(m['files']) == REQUIRED, 'source inventory')
    require(set(m['archive_members'])=={'slots/local/'+n for n in MEMBERS},'archive member inventory')
    for p,d in m['files'].items(): require(pin(ROOT/p)==d, 'source pin '+p)
    selected=json.loads((HERE/'BASE-SELECTED.json').read_bytes())
    require(digest(canonical(selected))==m['selected_snapshot_sha256'],'selected snapshot')
    require(selected['kappa']=='836330098538459/500000000000000000','selected kappa')
    old=json.loads((ROOT/'research/community-frontier1042-audit/RESULT.json').read_bytes())
    current=json.loads((ROOT/'research/community-frontier1094-audit/RESULT.json').read_bytes())
    require(current['baseline_receipt_sha256']==digest((ROOT/'research/community-frontier1042-audit/RESULT.json').read_bytes()),'selected baseline receipt')
    require(old['status']=='PASS_COMPLETE_PR1042_COMPOSITION' and current['status']=='PASS_COMPLETE_PR1094_COMPOSITION','selected receipt statuses')
    return m

def load():
    m=check_sources(); objs={}
    with tarfile.open(ROOT/ARCHIVE) as t:
        for n in MEMBERS:
            name='slots/local/'+n; raw=t.extractfile(name).read()
            require(digest(raw)==m['archive_members'][name], 'archive member '+name)
            objs[n]=json.loads(gzip.decompress(raw) if n.endswith('.gz') else raw)
    w=objs[MEMBERS[0]]; programs=objs[MEMBERS[1]]; receipt=objs[MEMBERS[2]]
    require(set(m['archive_members'])=={'slots/local/'+n for n in MEMBERS},'archive member inventory')
    with tarfile.open(ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz') as t:
        for n in MEMBERS:
            raw=t.extractfile('candidate/strict/global8/base/providers/gauge44/'+n).read()
            require(digest(raw)==m['archive_members']['slots/local/'+n],'selected1094 provider alias '+n)
    require((w['v'],w['h'],w['R'])==(112,9,480),'source dimensions')
    require(receipt['canonical_word_sha256']==m['archive_members']['slots/local/'+MEMBERS[0]] and receipt['local_programs_sha256']==m['archive_members']['slots/local/'+MEMBERS[1]],'native receipt artifact binding')
    require(set(programs)=={'forward','backward'},'orientations')
    return w,programs,receipt,objs[MEMBERS[3]]

def power(k): return Q(2**k) if k>=0 else Q(1,2**-k)

def parts(q):
    a=abs(q.numerator);d=q.denominator
    require(a and d&(d-1)==0,'nonzero dyadic')
    v=(a&-a).bit_length()-1
    return a>>v, v-(d.bit_length()-1)

def price(q, mode='copy-init'):
    p,e=parts(q)
    return 3+(p.bit_length()-1)+p.bit_count()+abs(e) if mode=='horner' else 2+(p.bit_length()-1)+p.bit_count()+abs(e)-int(p==1 and e==0)

def cost(g,mode='copy-init'):
    if g[0]=='add':return price(Q(g[3],g[4]),mode)
    if g[0] in ('copy','clear'):return 1
    require(g[0]=='scale','scalar opcode')
    q=Q(g[2],g[3]);p,e=parts(q);require(p==1,'power of two scale')
    return abs(e)+int(q<0)

def domain(w,programs):
    excluded=set(w['centers']) & set(range(224,704))
    for events in programs.values():
        for ev in events:
            if ev[0]=='scalar' and ev[1][0] in ('copy','clear'):
                for r in ev[1][1:]:
                    if isinstance(r,list) and r[0]=='L' and 224<=r[1]<704:excluded.add(r[1])
    return sorted(set(range(224,704))-excluded),sorted(excluded)

def search(events,helpers,mode='copy-init'):
    terms=defaultdict(list)
    for ev in events:
        if ev[0]=='scalar' and ev[1][0]=='add':
            g=ev[1];p,e=parts(Q(g[3],g[4]))
            for r,s in ((g[1],1),(g[2],-1)):
                if r[0]=='L':terms[r[1]].append((p,e,s))
    rows=[]
    for h in helpers:
        ts=terms[h]; points=sorted({0}|{-s*e for p,e,s in ts})
        def delta(k):
            return 2*abs(k)+sum(abs(e+s*k)-abs(e) - (int(p==1 and e+s*k==0)-int(p==1 and e==0) if mode=='copy-init' else 0) for p,e,s in ts)
        values=[[k,delta(k)] for k in points]
        best=min(values,key=lambda kv:(kv[1],abs(kv[0]),kv[0]))
        rows.append(dict(helper=h,incident_adds=len(ts),candidates=values,best_k=best[0],delta=best[1],tail_slope=2+len(ts)))
    return rows

def transform(events,w,h,k):
    require(224<=h<704 and h not in w['centers'],'non-center helper only')
    result=copy.deepcopy(events)
    for ev in result:
        if ev[0]!='scalar':continue
        g=ev[1]
        if g[0]=='add':
            shift=k*(int(g[1]==['L',h])-int(g[2]==['L',h]))
            q=Q(g[3],g[4])*power(shift);g[3:5]=[q.numerator,q.denominator]
        elif g[0] in ('copy','clear'):
            require(['L',h] not in g[1:],'copy/clear carrier excluded')
    q=power(k); entry=['scalar',['scale',['L',h],q.numerator,q.denominator],w['start'][h]]
    q=1/q; leave=['scalar',['scale',['L',h],q.numerator,q.denominator],w['final'][h]]
    # The materialized winner is cold/FULL and has no residual wrapper. The
    # exit scale follows full-frame cleanup, in the retained FULL coordinate.
    require(w['start'][h]==0 and w['final'][h]==1,'materialized cold/FULL helper')
    require(not any(e[0]=='residual_adapter' and e[2]==h for e in result),'unwrapped helper')
    require(result[0]==['phase','zero_frame_precondition'] and result[-1]==['phase','done'],'boundary phases')
    result.insert(len(result)-1,leave);result.insert(1,entry)
    require([e for e in result if e[0]!='scalar']==[e for e in events if e[0]!='scalar'],'nonscalar stream preserved')
    return result

def replay(events,orientation):
    # Independent formal variables for all 704 data/helper and 8 centre registers.
    rows={('L',i):{i:Q(1)} for i in range(704)}
    rows.update({('C',i):{704+i:Q(1)} for i in range(8)})
    for ev in events:
        if ev[0]!='scalar':continue
        g=ev[1];t=tuple(g[1]);tag=g[0]
        if tag=='clear':rows[t]={}
        elif tag=='copy':rows[t]=dict(rows[tuple(g[2])])
        elif tag=='scale':rows[t]={i:a*Q(g[2],g[3]) for i,a in rows[t].items()}
        elif tag=='add':
            s=tuple(g[2]);q=Q(g[3],g[4]);require(t!=s,'distinct add operands')
            for i,a in rows[s].items():
                v=rows[t].get(i,Q(0))+q*a
                if v:rows[t][i]=v
                else:rows[t].pop(i,None)
        else:raise ValueError('scalar opcode')
    for i in range(704):
        expected={i:Q(1)}
        if orientation=='forward' and 112<=i<224:expected[i-112]=Q(1)
        if orientation=='backward' and i<112:expected[i+112]=Q(-1)
        require(rows['L',i]==expected,'all-column endpoint '+str((orientation,i)))
    require(all(not rows['C',i] for i in range(8)),'private centre erased')
    return dict(formal_input_columns=712,data_helper_columns=704,dirty_helper_columns=480,centre_columns=8,all_restored=True)

def invoice(events,mode):
    env={('L',i):Q(1) for i in range(704)}
    env.update({('C',i):Q(1) for i in range(8)})
    peak=Q(1);count=0;paid=Counter()
    for ev in events:
        if ev[0]=='climb':paid[ev[5]]+=1
        elif ev[0]=='center':paid[ev[4]]+=1
        if ev[0]!='scalar':continue
        g=ev[1];tag=g[0];t=tuple(g[1]);count+=cost(g,mode)
        if tag=='clear':env[t]=Q(0)
        elif tag=='copy':env[t]=env[tuple(g[2])]
        elif tag=='scale':
            q=Q(g[2],g[3]);env[t]*=abs(q)
        else:
            s=tuple(g[2]);q=Q(g[3],g[4]);a=abs(q.numerator)
            # Integer Horner work grows to |numerator| times source before halving.
            # Copy-init has the same bound; unit direct-add does not touch W until clear.
            if mode=='horner' or abs(q)!=1:peak=max(peak,a*env[s])
            env[t]+=abs(q)*env[s]
        peak=max(peak,env[t])
    bits=peak.numerator.bit_length()-peak.denominator.bit_length()+1
    require(peak<2**192,'local 192-bit payload cap')
    return dict(real_primitives=count,complex_primitives=2*count,prefix_l1=str(peak),prefix_bits=bits,charged_payload_bits=192,paid_profile=dict(sorted(paid.items())))

def compute():
    w,programs,receipt,checks=load();helpers,excluded=domain(w,programs)
    result=dict(base=BASE,geometry=dict(v=112,h=9,R=480),helpers=helpers,excluded_center_or_copy_helpers=excluded,orientations={})
    candidates={}
    for orientation in ('forward','backward'):
        events=programs[orientation];rows=search(events,helpers)
        winner=min(rows,key=lambda row:(row['delta'],row['helper'],abs(row['best_k']),row['best_k']))
        h,k=winner['helper'],winner['best_k'];candidate=transform(events,w,h,k);candidates[orientation]=candidate
        entry={ 'optima':rows,'winner':winner,'candidate_sha256':digest(canonical(candidate)),
                'boundary_frames':[w['start'][h],w['final'][h]],'baseline_endpoint':replay(events,orientation),'candidate_endpoint':replay(candidate,orientation),'prices':{}}
        for mode in ('horner','copy-init'):
            before=invoice(events,mode);after=invoice(candidate,mode)
            require(before['paid_profile']==after['paid_profile'],'paid children unchanged')
            if mode=='horner':
                require(before['prefix_l1']==receipt['local'][orientation]['prefix_l1_upper'],'source prefix invoice')
                require(before['complex_primitives']==checks[orientation]['real_component_primitive_bound'],'source primitive invoice')
            else:require(after['real_primitives']-before['real_primitives']==winner['delta'],'search vs whole stream cost')
            entry['prices'][mode]=dict(before=before,after=after,saving_real=before['real_primitives']-after['real_primitives'],saving_complex=before['complex_primitives']-after['complex_primitives'])
        result['orientations'][orientation]=entry
    result['status']='PASS_EXACT_UNBOUNDED_SINGLE_NONCENTER_HELPER_DYADIC_GAUGE'
    return result,candidates
