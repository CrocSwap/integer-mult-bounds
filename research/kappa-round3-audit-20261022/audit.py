"""Independent finite patch, logical endpoint, transport and full-invoice audit.

Does not import the construction, native verifier, optimizer or price generator.
Uses standard-library exact integer point sets, Fractions and free words.
Cao Yifan; substantial OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter,defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip,json,re,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SOURCE=ROOT/'research/kappa-round3-warp-20261022'
OLD=ROOT/'research/warp-interface-20261022'
PAYLOAD='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
OLDPAYLOAD='4409d2d9328fffbd276bb03fb800f59a33ec3b2ab15f79a330a7af66e75110cc'

def need(p,s):
    if not p:raise ValueError(s)
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def span(b):
    s={0}
    for v in b:
        need(type(v) is int and 0<v<512,'binary frame vector range')
        need(v not in s,'independent binary frame basis')
        s|={v^x for x in tuple(s)}
    return frozenset(s)
def operands(e):
    if e[0]=='scalar':
        g=e[1];return [tuple(r) for r in g[1:3] if isinstance(r,list)] if g[0] in ('add','copy') else [tuple(g[1])]
    return [tuple(e[1])] if e[0]=='warp' else []
def action(cols,x):
    y=0
    for i,v in enumerate(cols):
        if (x>>i)&1:y^=v
    return y
def addto(a,b,q):
    for k,v in tuple(b.items()):
        a[k]=a.get(k,Q(0))+q*v
        if not a[k]:del a[k]

def replay(c,p,backward=False,logical=True):
    ss=[span(b) for b in c['frames']];ds=list(map(len,c['frames']))
    ops={w['op']:w['G_columns'] for w in c['warps']};maps={}
    need(set(ops)==set(range(1,73)),'72 distinct complete native maps')
    for op,cols in ops.items():
        need(len(cols)==9 and len(set(action(cols,x) for x in range(512)))==512,'invertible complete native map')
        positive=[action(cols,x) for x in range(512)];negative=[0]*512
        for x,y in enumerate(positive):negative[y]=x
        maps[op]=positive;maps[-op]=negative
    state={('L',i):f for i,f in enumerate(c['start'])};state['C',0]=None
    rows={('L',i):{(('L',i),()):Q(1)} for i in range(632)};rows['C',0]={(('C',0),()):Q(1)}
    paid=Counter();events=Counter();scalar_cost=0;max_l1=Q(1)
    for k,e in enumerate(p):
        op=e[0];events[op]+=1
        if op in ('phase','adapter','residual_adapter'):continue
        if op in ('climb','center'):
            if op=='climb':_,_,r,a,b,rank=e;r=('L',r);need(ss[a]<ss[b],'strict nested climb')
            else:_,i,a,b,rank=e;r=('C',i);need(ss[a]<ss[b] or ss[b]<ss[a],'nested owned center')
            need(state[r]==a and rank==abs(ds[b]-ds[a]) and 1<=rank<=9,'literal paid rank/source')
            state[r]=b;paid[rank]+=1;continue
        if op=='warp':
            _,r,operator,a,b=e;r=tuple(r)
            need(state[r]==a,'literal warp source')
            need(frozenset(maps[operator][x] for x in ss[a])==ss[b],'actual G transports complete subspace')
            state[r]=b
            if logical:
                symbol=(1 if operator>0 else -1)*(abs(operator)+(1000000 if backward else 0));new={}
                for (variable,word),q in rows[r].items():
                    word=word[1:] if word and word[0]==-symbol else (symbol,)+word
                    need((variable,word) not in new,'injective free-word prefix action');new[variable,word]=q
                rows[r]=new
            continue
        need(op=='scalar','known complete event inventory')
        g,f=e[1:];d=tuple(g[1]);need(d in state,'known scalar role')
        if g[0]=='clear':
            need(d==('C',0),'owned storage alone may be erased');rows[d]={};state[d]=f;scalar_cost+=1
        else:
            need(state[d]==f,'literal scalar target frame')
            if g[0] in ('copy','add'):
                s=tuple(g[2]);need(state[s]==f and d!=s,'literal scalar source frame')
                if g[0]=='copy':need(d==('C',0),'owned storage alone overwritten');rows[d]=dict(rows[s]);scalar_cost+=1
                else:
                    q=Q(g[3],g[4]);n,den=abs(q.numerator),q.denominator
                    need(n>0 and den&(den-1)==0,'nonzero dyadic ADD')
                    scalar_cost+=3+n.bit_length()-1+n.bit_count()+den.bit_length()-1
                    if logical:addto(rows[d],rows[s],q)
            else:
                need(g[0]=='scale','known scalar opcode');q=Q(g[2],g[3]);n,den=abs(q.numerator),q.denominator
                need(n>0 and n&(n-1)==0 and den&(den-1)==0,'unit dyadic scale')
                scalar_cost+=abs(n.bit_length()-den.bit_length())+int(q<0)
                if logical:rows[d]={k:q*v for k,v in rows[d].items()}
        if logical:max_l1=max(max_l1,sum(map(abs,rows[d].values()),Q(0)))
    need([state['L',i] for i in range(632)]==c['final'],'all632 actual final frames')
    if logical:
        for i in range(632):
            wanted={(('L',i),()):Q(1)}
            if (i<112 if backward else 112<=i<224):
                wanted[(('L',i+112 if backward else i-112),())]=Q(-1 if backward else 1)
            need(rows['L',i]==wanted,'arbitrary-input endpoint '+str(i))
        need(not rows['C',0],'owned entry column and scratch return zero')
    return {'paid':dict(paid),'rank_mass':sum(r*n for r,n in paid.items()),'scalar_cost':2*scalar_cost,'complex_scalar_primitive_allowance':scalar_cost,'events':dict(events),'max_formal_prefix_l1':str(max_l1)}

def rebuild(base,patch):
    c=deepcopy(base['canonical']);spaces=[span(b) for b in c['frames']];programs={}
    need(len(c['frames'])==patch['base_frame_count'],'base frame count')
    c['frames']+=patch['additional_frames'];spaces=[span(b) for b in c['frames']]
    for field,changes in patch['boundary_changes'].items():
        need(field in ('start','final') and len({r for r,_,_ in changes})==len(changes),'known unique boundary changes')
        for r,a,b in changes:need(224<=r<632 and c[field][r]==a,'guarded arbitrary-helper-only boundary');c[field][r]=b
    for direction,old in base['programs'].items():
        raw=[deepcopy(e) for e in old if e[0]!='climb']
        need(len({i for i,_,_ in patch['scalar_frame_changes']})==len(patch['scalar_frame_changes']),'unique scalar patch')
        for i,a,b in patch['scalar_frame_changes']:need(raw[i][0]=='scalar' and raw[i][2]==a,'guarded scalar patch');raw[i][2]=b
        for i,op,a,b,x,y in patch['warp_frame_changes']:need(raw[i][0]=='warp' and raw[i][2:]==[op,a,b],'guarded warp patch');raw[i][3:]=[x,y]
        cur=c['start'][:];out=[]
        def move(r,b):
            a=cur[r]
            if a==b:return
            need(spaces[a]<spaces[b],'rebuilt monotone paid transport')
            out.append(['climb','warp_retimed',r,a,b,len(c['frames'][b])-len(c['frames'][a])]);cur[r]=b
        for e in raw:
            if e[0]=='scalar':
                for family,r in operands(e):
                    if family=='L':move(r,e[2])
            elif e[0]=='warp':move(e[1][1],e[3]);cur[e[1][1]]=e[4]
            out.append(e)
        for r,b in enumerate(c['final']):move(r,b)
        programs[direction]=out
    c['warps']=patch['actual_operator_bindings']
    c['local_profile']=dict(Counter(e[5] for e in programs['forward'] if e[0]=='climb')+Counter(e[4] for e in programs['forward'] if e[0]=='center'))
    c['warp_edges']=sorted({(1 if e[2]>0 else -1,abs(e[2]),e[3],e[4]) for e in programs['forward'] if e[0]=='warp'})
    return {'canonical':c,'programs':programs,'discovery_word_sha256':patch['discovery_word_sha256'],'scope':patch['scope']}

def main():
    started=time.monotonic();new=read(SOURCE/'ACTUAL-WORD.json.gz');old=read(OLD/'ACTUAL-WORD.json.gz');patch=read(SOURCE/'PATCH.json')
    need(sha256(gzip.decompress((SOURCE/'ACTUAL-WORD.json.gz').read_bytes())).hexdigest()==PAYLOAD,'pinned current payload')
    need(sha256(gzip.decompress((OLD/'ACTUAL-WORD.json.gz').read_bytes())).hexdigest()==OLDPAYLOAD,'pinned predecessor payload')
    need(patch['base_sha256']==digest(ROOT/patch['base_path']),'patch predecessor compressed pin')
    rebuilt=rebuild(old,patch);need(json.loads(json.dumps(rebuilt))==new,'independently reconstructed every complete payload field')
    c=new['canonical'];base=old['canonical'];need(c['frames']==base['frames'],'all4429 inherited frame bases unchanged')
    need(c['start'][:224]==base['start'][:224] and c['final']==base['final'] and c['ports']==base['ports'],'all main interfaces, helper exits, ports unchanged')
    H=Counter()
    for r in range(224,632):
        a,b=c['start'][r],c['final'][r];need(span(c['frames'][a])<span(c['frames'][b]),'all408 strict arbitrary-input helper boundaries')
        H[len(c['frames'][b])-len(c['frames'][a])]+=1
    need(H=={4:28,7:7,8:47,9:326},'entire actual productive helper census')
    checks={d:replay(c,p,d=='backward') for d,p in new['programs'].items()}
    need(set(checks)=={'forward','backward'},'both orientations present')
    expected={1:2201,2:412,3:510,4:127,5:40,8:8}
    need(all(x['paid']==expected and x['rank_mass']==5327 for x in checks.values()),'both independent complete paid invoices')
    need(checks['forward']['scalar_cost']==158120 and checks['backward']['scalar_cost']==158168,'literal complete scalar invoices')
    # Direct invoice assembly from the retained controller event/diagonal lists.
    ctrl=read(ROOT/'research/joint-helper-lattice/CONTROLLER.json');T=Counter();P=Counter();calls=Counter()
    for e in ctrl['physical_events']:
        if e[0]=='LOCAL':T.update(H);P.update(expected);calls['full']+=1
        elif e[0]=='QUERY_SHEAR':P[1]+=112;calls['query']+=1
        elif e[0]=='IDLE':P[8*len(e[2])]+=224;calls['idle']+=1
    for term in ctrl['diagonal']:T[1+8*sum(term[1:])]+=112
    arithmetic=read(SOURCE/'ARITHMETIC.json')
    need({int(k):v for k,v in arithmetic['targets'].items()}==T and {int(k):v for k,v in arithmetic['paid'].items()}==P,'whole paid/target arithmetic dictionaries rebuilt from actual word census')
    need(calls['full']==18 and calls['query']==15 and sum(P.values())==64404 and sum(T.values())==10928,'complete caller inventory')
    need(sum(r*n for r,n in T.items())-sum(r*n for r,n in P.items())==752,'whole rank-mass surplus')
    # Receipt binding and coverage (physical phases themselves remain separately checked).
    native=read(SOURCE/'NATIVE-VALIDATION.json');phase=read(SOURCE/'PHASE-VALIDATION.json.gz')
    for rec,name in [(native,'verify_candidate.py'),(phase,'phase_check.py')]:
        need(rec['actual_word_canonical_sha256']==PAYLOAD and rec['verifier_sha256']==digest(SOURCE/name),'native/phase proof input provenance')
    need(phase['source_manifest_sha256']==digest(SOURCE/'SOURCES.json'),'phase source manifest provenance')
    oldG={x['op']:x['G_columns'] for x in base['warps']};newG={x['op']:x['G_columns'] for x in c['warps']}
    changed=sorted(op for op in newG if newG[op]!=oldG[op]);need(changed==phase['changed_G_operators'] and len(changed)==20,'every changed map in phase coverage')
    need({x['operator'] for x in phase['native_operator_columns']}==set(changed),'each changed bare native all512-column admission')
    edge=lambda p:{(e[3],e[4]) for e in p if e[0]=='climb'}
    warp=lambda p:{(e[2],e[3],e[4]) for e in p if e[0]=='warp'}
    need(edge(new['programs']['forward'])==edge(new['programs']['backward']),'both complete paid-pair sets')
    need(warp(new['programs']['forward'])==warp(new['programs']['backward']),'both complete warp sets')
    need({(r['operator'],r['input'],r['output']) for r in phase['actual_warp_classes']}==warp(new['programs']['forward']),'all actual warp class receipt coverage')
    need({(r['input'],r['output']) for r in phase['new_paid_pairs']}==edge(new['programs']['forward'])-edge(old['programs']['forward']),'exact new paid phase coverage')
    changedhelpers={r for r in range(224,632) if (c['start'][r],c['final'][r])!=(base['start'][r],base['final'][r])}
    covered=set()
    for h in phase['changed_helper_boundaries']:
        for r in h['helpers']:need(r not in covered and (h['input'],h['output'])==(c['start'][r],c['final'][r]),'unique actual changed helper phase interface');covered.add(r)
    need(covered==changedhelpers and len(covered)==26,'all26 changed arbitrary helper interfaces have phase evidence')
    # Meaningful independent corruption controls; no frozen file is modified.
    controls=[]
    def rejects(name,fn):
        try:fn()
        except (ValueError,AssertionError) as e:controls.append({'name':name,'rejected':str(e)})
        else:raise ValueError('accepted corruption '+name)
    badc=deepcopy(c);r=min(changedhelpers);badc['start'][r]=base['start'][r]
    rejects('stale_changed_helper_entrance',lambda:replay(badc,new['programs']['forward'],logical=False))
    bad=deepcopy(new['programs']['forward']);next(e for e in bad if e[0]=='climb')[5]+=1
    rejects('wrong_paid_rank',lambda:replay(c,bad,logical=False))
    bad=deepcopy(new['programs']['forward']);g=next(e[1] for e in bad if e[0]=='scalar' and e[1][0]=='add');g[3]+=g[4]
    rejects('wrong_scalar_coefficient',lambda:replay(c,bad))
    bad=deepcopy(new['programs']['forward']);index=next(i for i,e in enumerate(bad) if e[0]=='scalar');bad.insert(index,['scalar',['clear',['L',224]],c['start'][224]])
    rejects('erased_arbitrary_helper',lambda:replay(c,bad,logical=False))
    # An invertible but inconsistent map is rejected by point-set transport.
    badc=deepcopy(c);op=changed[0];binding=next(w for w in badc['warps'] if w['op']==op)
    mutant=None
    for i in range(9):
        for j in range(9):
            if i==j:continue
            cols=newG[op][:];cols[i]^=cols[j]
            for e in new['programs']['forward']:
                if e[0]=='warp' and e[2]==op and frozenset(action(cols,x) for x in span(c['frames'][e[3]]))!=span(c['frames'][e[4]]):mutant=cols;break
            if mutant:break
        if mutant:break
    need(mutant is not None,'meaningful invertible-G corruption exists');binding['G_columns']=mutant
    rejects('wrong_invertible_native_G',lambda:replay(badc,new['programs']['forward'],logical=False))
    paths=[Path(__file__),SOURCE/'ACTUAL-WORD.json.gz',SOURCE/'PATCH.json',SOURCE/'NATIVE-VALIDATION.json',SOURCE/'PHASE-VALIDATION.json.gz',SOURCE/'ARITHMETIC.json',SOURCE/'SOURCES.json',OLD/'ACTUAL-WORD.json.gz',ROOT/'research/joint-helper-lattice/CONTROLLER.json']
    result={'status':'PASS_INDEPENDENT_PATCH_LOGICAL_ENDPOINT_AND_COMPLETE_LEDGER_AUDIT','canonical_payload_sha256':PAYLOAD,'native':checks,'helpers':dict(H),'local_paid':expected,'global_targets':dict(T),'global_paid':dict(P),'controller_calls':dict(calls),'changed_G_maps':changed,'changed_helpers':sorted(changedhelpers),'phase_coverage':{'warp_classes':len(phase['actual_warp_classes']),'new_paid_pairs':len(phase['new_paid_pairs']),'changed_helper_roles':len(covered),'changed_bare_native_maps':len(changed)},'controls':controls,'source_sha256':{p.relative_to(ROOT).as_posix():digest(p) for p in paths},'seconds':time.monotonic()-started,'scope':'Separately implemented finite all632 arbitrary-input logical replay, point-set frame/warp validation, guarded payload reconstruction, complete invoice/census and phase-receipt coverage/provenance. Does not independently reprove absolute phases, all-size lifting, compiler/outer mathematics or full multiplication theorem.'}
    (HERE/'AUDIT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('global_paid','global_targets','native','source_sha256')},indent=2))

if __name__=='__main__':main()
