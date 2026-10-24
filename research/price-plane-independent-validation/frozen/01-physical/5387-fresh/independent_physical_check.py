#!/usr/bin/env python3
"""Independent exact PR5387 physical audit; no candidate evaluator imports.

Core free-group pullback/forward algorithms adapted from our independent PR5377
engine. PR5387 obligations below are newly instantiated and derived from bytes.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import gzip, hashlib, json, time

HERE = Path(__file__).resolve().parent
P = HERE / 'pinned'

def read(name):
    raw = (P / name).read_bytes()
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)

def check(test, message):
    if not test:
        raise ValueError(message)

def merge(dst, key, value):
    q = dst.get(key, F(0)) + value
    if q:
        dst[key] = q
    else:
        dst.pop(key, None)

def right_letter(word, op):
    return word[:-1] if word and word[-1] == -op else word + (op,)

def pullback(program, role, stop):
    """Right-append words while pulling one output functional to source inputs."""
    functional = {role: {(): F(1)}}
    for event in reversed(program[:stop+1]):
        if event[0] == 'warp':
            dst, op = tuple(event[1]), event[2]
            if dst in functional:
                functional[dst] = {right_letter(w, op): q for w, q in functional[dst].items()}
        elif event[0] == 'scalar':
            g = event[1]; dst = tuple(g[1])
            row = functional.get(dst, {})
            if g[0] == 'clear':
                functional.pop(dst, None)
            elif g[0] == 'scale':
                functional[dst] = {w: q*F(*g[2:]) for w,q in row.items()}
            else:
                src = tuple(g[2]); copy = g[0] == 'copy'
                check(copy or g[0] == 'add', 'known scalar pullback')
                q = F(1) if copy else F(*g[3:])
                if copy:
                    functional.pop(dst, None)
                for w, a in tuple(row.items()):
                    merge(functional.setdefault(src, {}), w, q*a)
        else:
            check(event[0] in ('climb','center','phase','adapter'), 'source opcode')
    return {(r,w): q for r,row in functional.items() for w,q in row.items() if q}

def difference(a,b):
    out=dict(a)
    for k,q in b.items(): merge(out,k,-q)
    return out

def span(basis):
    s={0}
    for b in basis: s |= {x^b for x in tuple(s)}
    check(len(s)==2**len(basis), 'independent frame basis')
    return s


# Published source obligations: seven shared PR5383 rows plus the exact-head
# PR5387 RELATIONS eighth row; proved by reverse propagation without importing
# either candidate native.py or a candidate witness evaluator.
SPECS=[
 (11205,92,254,11332,15584,1,{230:1,324:-1,326:1,328:1,333:-1}),
 (11218,57,274,11358,17264,1,{225:1,384:-1,388:-1,390:1,391:1,392:1,397:-1}),
 (11231,81,619,11384,17256,1,{225:1,227:-1,229:1,231:-2,232:1,234:-1,235:-1,236:-1,237:-1,238:2,239:1,384:-1,388:-1,390:1,391:1,392:1,397:-1}),
 (11244,224,279,11410,17722,-1,{227:1,229:1,232:-1,234:1,235:1,236:-1,237:1,239:-1,324:-1,326:1,328:1,333:-1}),
 (11257,11,621,11436,15876,1,{241:1,243:-1,245:1,247:-1,252:-1,253:-1,254:1,255:1}),
 (11270,240,280,11462,17245,-1,{225:1,241:-1,243:1,245:1,247:-1,252:-1,253:1,254:1,255:-1,324:-1,326:1,328:1,333:-1,384:-1,388:-1,390:1,391:1,392:1,397:-1}),
 (11283,9,624,11488,15870,1,{257:1,259:-1,261:1,263:-1,268:-1,269:-1,270:1,271:1}),
 (11296,256,281,11514,17233,-1,{225:1,257:-1,259:1,261:1,263:-1,268:-1,269:1,270:1,271:-1,324:-1,326:1,328:1,333:-1,384:-1,388:-1,390:1,391:1,392:1,397:-1}),
]

def rref_relations():
    columns=sorted(set().union(*(set(s[-1]) for s in SPECS)))
    a=[[F(s[-1].get(i,0)) for i in columns] for s in SPECS]
    pivot_columns=[]; row=0
    for j,col in enumerate(columns):
        found=next((k for k in range(row,len(a)) if a[k][j]),None)
        if found is None:continue
        a[row],a[found]=a[found],a[row]
        q=a[row][j]; a[row]=[x/q for x in a[row]]
        for k in range(len(a)):
            if k==row:continue
            q=a[k][j]
            a[k]=[x-q*y for x,y in zip(a[k],a[row])]
        pivot_columns.append(col);row+=1
        if row==len(a):break
    check(row==8,'relations have exact rational rank eight')
    check(pivot_columns==[225,227,229,230,241,245,257,261],'source-declared pivot set derived')
    rows=[{col:q for col,q in zip(columns,r) if q} for r in a]
    for pivot,r in zip(pivot_columns,rows):
        check(r[pivot]==1 and all(p not in r for p in pivot_columns if p!=pivot),'pivot block is identity')
        check(all(q.denominator in (1,2) for q in r.values()),'preparation dyadic half-integer grammar')
    return pivot_columns,rows

def source_identity_checks(source):
    old=source['programs']['backward']; identities=[]
    for n,(snap,lender,frame,center,zero,sign,relation) in enumerate(SPECS,1):
        check(old[snap][0]=='climb' and old[snap][2]==lender and old[snap][4]==frame,'literal snapshot endpoint')
        check(old[center]==['center',0,0,frame,8],'literal rank-eight center')
        check(old[zero][0]=='climb' and old[zero][2:]==[lender,frame,1,1],'literal rank-one zero job')
        q=pullback(old,('L',lender),snap)
        c=pullback(old,('C',0),center)
        z=pullback(old,('L',lender),zero)
        d={(('L',i),()):F(v*sign,4) for i,v in relation.items()}
        check(difference(c,q)==d,'unrestricted center-snapshot identity D'+str(n))
        check(z=={k:-v for k,v in d.items()},'unrestricted zero identity D'+str(n))
        wrong=dict(d);k=next(iter(wrong));wrong[k]=-wrong[k]
        check(difference(c,q)!=wrong,'wrong relation sign rejects D'+str(n))
        check(difference(c,pullback(old,('L',(lender+1)%632),snap))!=d,'wrong snapshot rejects D'+str(n))
        identities.append({'relation':n,'snapshot':snap,'lender':lender,'frame':frame,'center':center,'zero':zero,'sign':sign,'snapshot_terms':len(q),'relation_terms':len(d),'center_minus_snapshot':'sign*D/4','later_zero_row':'-sign*D/4'})
    return identities

def advance_all(word, direction, specialized):
    c=word['canonical']; owned={('C',0)}
    if specialized: owned|={('C',i) for i in range(1,9)}|{('L',p) for p in rref_relations()[0]}
    state={('L',i): {(('L',i),()): F(1)} for i in range(632)}
    state.update({r:{(r,()):F(1)} for r in owned})
    frames={('L',i):f for i,f in enumerate(c['start'])}
    frames.update({r:None for r in owned if r[0]=='C'})
    spaces=list(map(span,c['frames'])); paid=Counter(); zeros=[]
    for index,event in enumerate(word['programs'][direction]):
        kind=event[0]
        if kind=='scalar':
            g,frame=event[1:]; dst=tuple(g[1])
            if g[0]=='clear':
                check(dst in owned,'erase only owned storage')
                state[dst]={}; frames[dst]=frame
            else:
                check(frames[dst]==frame,'scalar output gauge')
                if g[0]=='scale': state[dst]={k:q*F(*g[2:]) for k,q in state[dst].items()}
                else:
                    src=tuple(g[2]); check(frames[src]==frame and src!=dst,'scalar source gauge')
                    if g[0]=='copy':
                        check(dst in owned and not state[dst], 'copy clears owned destination')
                        state[dst]=dict(state[src])
                    else:
                        check(g[0]=='add','known scalar')
                        for k,q in tuple(state[src].items()): merge(state[dst],k,q*F(*g[3:]))
        elif kind=='warp':
            _,role,op,old,new=event; dst=tuple(role)
            check(frames[dst]==old,'native warp input gauge')
            transformed={}
            for (r,w),q in state[dst].items():
                nw=w[1:] if w and w[0]==-op else (op,)+w
                merge(transformed,(r,nw),q)
            state[dst]=transformed; frames[dst]=new
        elif kind in ('climb','center'):
            if kind=='climb': _,_,i,old,new,rank=event; dst=('L',i)
            else: _,i,old,new,rank=event; dst=('C',i)
            check(frames[dst]==old,'paid input gauge')
            check(spaces[old]<spaces[new] or (kind=='center' and spaces[new]<spaces[old]),'nested paid transition')
            check(rank==abs(len(c['frames'][new])-len(c['frames'][old])),'whole paid rank')
            frames[dst]=new; paid[rank]+=1
        elif kind=='zero_retag':
            _,role,old,new=event; dst=tuple(role)
            check(direction=='backward' and specialized and (dst,old,new) in {(('L',s[1]),s[2],1) for s in SPECS},'authorized zero replacement')
            check(frames[dst]==old and state[dst]=={},'all independent columns zero')
            frames[dst]=new; zeros.append(index)
        else:
            check(kind in ('phase','adapter'),'known inherited marker')
    check([frames['L',i] for i in range(632)]==c['final'],'every final gauge')
    for i in range(632):
        r=('L',i)
        if r in owned: continue
        want={(r,()):F(1)}
        if direction=='backward' and i<112: want[(('L',i+112),())]=F(-1)
        if direction=='forward' and 112<=i<224: want[(('L',i-112),())]=F(1)
        check(state[r]==want,'independent endpoint '+str(i))
    check(all(not state[r] for r in owned),'all owned outputs erased')
    return {'persistent_inputs':632-8*int(specialized),'owned_arbitrary_inputs':len(owned),'owned_roles':sorted(map(list,owned)),
            'paid':dict(sorted(paid.items())),'checked_zero_event_indices':zeros,
            'endpoint_pass':True,'frame_pass':True}


def literal_expected(source):
    pivots,rows=rref_relations();expected=[]
    for pivot,row in zip(pivots,rows):
        expected.append(['scalar',['clear',['L',pivot]],0])
        for i,q in sorted(row.items()):
            if i==pivot:continue
            expected.append(['scalar',['add',['L',pivot],['L',i],-q.numerator,q.denominator],0])
    snaps={s[0]:(j+1,s) for j,s in enumerate(SPECS)}
    centers={s[3]:(j+1,s) for j,s in enumerate(SPECS)}
    zeros={s[4]:s for s in SPECS}
    for i,e in enumerate(source['programs']['backward']):
        if i in centers:
            j,s=centers[i];frame=s[2]
            expected += [['scalar',['clear',['C',0]],frame],['scalar',['copy',['C',0],['C',j]],frame],['scalar',['clear',['C',j]],frame]]
        elif i in zeros:
            s=zeros[i];expected.append(['zero_retag',['L',s[1]],s[2],1])
        else:expected.append(e)
        if i in snaps:
            j,s=snaps[i];frame=s[2]
            expected += [['scalar',['clear',['C',j]],frame],['scalar',['copy',['C',j],['L',s[1]]],frame]]
    expected += [['scalar',['clear',['L',p]],1] for p in pivots]
    return expected

def phase_catalogue_subset(source,candidate):
    # Native signed operators, exact gauges, geometry and owner labels bind
    # retained phase recipes to the accepted actual source catalogue.
    out={}
    for direction in ('forward','backward'):
        old=source['programs'][direction];new=candidate['programs'][direction]
        warps=lambda p:Counter(json.dumps(e,separators=(',',':')) for e in p if e[0]=='warp')
        paid=lambda p:Counter(json.dumps(e,separators=(',',':')) for e in p if e[0] in ('climb','center'))
        check(warps(new)==warps(old),'all signed warp occurrences unchanged')
        a,b=paid(old),paid(new)
        check(not b-a,'retained paid recipe catalogue exact subset')
        removed=a-b
        check(sum(removed.values())==(0 if direction=='forward' else 16),'exact removed paid count')
        out[direction]={'warp_occurrences':sum(warps(new).values()),'retained_paid_occurrences':sum(b.values()),'removed_paid_occurrences':sum(removed.values()),'removed_literal_events':[json.loads(e) for e,n in removed.items() for _ in range(n)]}
    return out

def main():
    import copy
    started=time.monotonic()
    capsule=HERE.parents[1]/'09-capsule-cold'/'capsule-5387-v1'
    manifest_bytes=(capsule/'IMMUTABLE-MANIFEST.json').read_bytes()
    manifest_hash=hashlib.sha256(manifest_bytes).hexdigest()
    check(manifest_hash=='b0b7eaeef8895264f33e86d87c1bf63fba495d6ac2f50e1414ee3eae775a1594','immutable capsule contract hash')
    manifest=json.loads(manifest_bytes)
    check(manifest['candidate_head']=='b1ab650d36f59e5be682a813145b7c67e219e341','exact candidate head')
    verified=[]
    for r in manifest['rows']:
        raw=(capsule/r['capsule_path']).read_bytes()
        check(hashlib.sha256(raw).hexdigest()==r['sha256'],'capsule row SHA256')
        check(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['git_blob'],'capsule row Git blob')
        verified.append({k:r[k] for k in ('capsule_path','sha256','git_blob','source_commit')})
    snapshot=capsule/'snapshot'
    def load(path):
        raw=(snapshot/path).read_bytes()
        return json.loads(gzip.decompress(raw) if path.endswith('.gz') else raw)
    source_path='research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
    candidate_path='research/eight-owned-relations/WORD.json.gz'
    source=load(source_path);candidate=load(candidate_path)
    check(hashlib.sha256(gzip.decompress((snapshot/source_path).read_bytes())).hexdigest()=='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd','accepted4610 source payload')
    physical=dict(source['canonical']);physical.pop('local_profile')
    check(candidate['canonical']==physical,'all actual physical maps/frames/gauges unchanged')
    check(candidate['programs']['forward']==source['programs']['forward'],'forward literal chronology unchanged')
    expected=literal_expected(source)
    actual=candidate['programs']['backward']
    boundary=lambda p:next(i for i,e in enumerate(p) if e[0]!='scalar')
    ei,ai=boundary(expected),boundary(actual)
    check(expected[ei:]==actual[ai:],'exact snapshot/COPY/zero/cleanup source delta')
    check(Counter(map(str,expected[:ei]))==Counter(map(str,actual[:ai])),'same exact RREF preparation events up to ordering')
    # Every prelude ADD reads only nonpivot helpers; different destination
    # blocks and ADD order therefore commute in exact arithmetic. Full column
    # execution below additionally validates initial clears and chronology.
    pivots,rref=rref_relations();identities=source_identity_checks(source)
    for e in actual[:ai]:
        check(e[0]=='scalar' and e[2]==0,'only frame0 preparation scalars')
        g=e[1]
        check(g[1][0]=='L' and g[1][1] in pivots,'preparation writes only owned pivots')
        if g[0]=='add':check(g[2][0]=='L' and g[2][1]>=224 and g[2][1] not in pivots,'every RHS nonpivot independent helper')
        else:check(g[0]=='clear','preparation scalar species')
    relations=load('research/eight-owned-relations/RELATIONS.json')
    check(relations['pivots']==pivots,'published pivot set independently derived')
    check([{int(k):F(q) for k,q in r.items()} for r in relations['rows']]==rref,'published relation basis independently derived')
    witness=relations['sites']
    for w,s in zip(witness,SPECS):
        snap,lender,frame,center,zero,sign,relation=s
        check(w['snapshot']==snap and w['role']==['L',lender] and w['frame']==frame and w['center']==center and w['zeros']==[[zero,1,['L',lender]]],'witness event fields')
        check({int(i):F(q) for i,q in w['relation']}==relation,'witness relation equals independently proved relation')
    check(len(witness)==8,'eight distinct witnesses')
    allcolumns={name+'_'+d:advance_all(word,d,specialized) for name,word,d,specialized in [('source',source,'forward',False),('source',source,'backward',False),('candidate',candidate,'forward',False),('candidate',candidate,'backward',True)]}
    check(candidate['owned']=={d:allcolumns['candidate_'+d]['owned_roles'] for d in ('forward','backward')},'declared owned inventory exact')
    subset=phase_catalogue_subset(source,candidate)
    phase=load('research/kappa-round3-warp-20261022/PHASE-VALIDATION.json.gz')
    check(phase['actual_word_canonical_sha256']=='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd','exact phase source payload binding')
    check(phase['status']=='PASS_JOINT_HELPER_MAPS_ALL_ACTUAL_ABSOLUTE_PHASES','source phase receipt status')
    controller=load('research/joint-helper-lattice/CONTROLLER.json')
    calls=[e for e in controller['physical_events'] if e[0]=='LOCAL']
    check([e[1] for e in calls if e[3]]==list(range(1,32,2)),'16 backward call stages')
    check([e[1] for e in calls if not e[3]]==[0,32],'two forward call stages')
    check(sum(e[0]=='QUERY_SHEAR' for e in controller['physical_events'])==15,'15 thin queries')
    # Full word controls mutate executable data, with positive all-column run above.
    def reject(label,mutate):
        bad=copy.deepcopy(candidate);mutate(bad['programs']['backward'])
        try:advance_all(bad,'backward',True)
        except ValueError as e:return {'control':label,'status':'REJECTED','reason':str(e)}
        raise ValueError('mutation incorrectly accepted: '+label)
    def first(p,predicate):return next(i for i,e in enumerate(p) if predicate(e))
    controls=[]
    controls.append(reject('wrong preparation sign',lambda p:p[1][1].__setitem__(3,-p[1][1][3])))
    controls.append(reject('omitted pivot entry clear',lambda p:p.pop(0)))
    def badsnapshot(p):
        i=first(p,lambda e:e[0]=='scalar' and e[1][0]=='copy' and e[1][1]==['C',1]);p[i][1][2]=['L',93]
    controls.append(reject('wrong snapshot role',badsnapshot))
    def badzero(p):
        i=first(p,lambda e:e[0]=='zero_retag');p[i][3]=2
    controls.append(reject('wrong zero output frame',badzero))
    def badrank(p):
        i=first(p,lambda e:e[0]=='climb');p[i][-1]+=1
    controls.append(reject('wrong retained paid rank',badrank))
    def badcopy(p):
        i=first(p,lambda e:e[0]=='scalar' and e[1][0]=='copy');p[i][2]=0
    controls.append(reject('wrong COPY frame',badcopy))
    controls.append(reject('omitted pivot output clear',lambda p:p.pop()))
    raw=(snapshot/candidate_path).read_bytes()
    result={'status':'PASS_BOUNDED_FRESH_INDEPENDENT_PHYSICAL_5387_EIGHT_RELATIONS','candidate_head':manifest['candidate_head'],'canonical_main':manifest['canonical_main'],'manifest_sha256':manifest_hash,'word_sha256':hashlib.sha256(raw).hexdigest(),'word_payload_sha256':hashlib.sha256(gzip.decompress(raw)).hexdigest(),'word_git_blob':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'verified_capsule_rows':len(verified),'rank':8,'pivots':pivots,'rref':[{str(k):str(q) for k,q in r.items()} for r in rref],'unrestricted_source_identities':identities,'all_columns':allcolumns,'source_phase_catalogue_subset':subset,'source_phase_lowering_rerun':False,'source_phase_foundation':'accepted exact4610 through selected5241; unchanged recipes plus subset proof, not fresh lowering','snapshot_lifetimes':{'all_eight_live_before_first_center':max(s[0] for s in SPECS)<min(s[3] for s in SPECS),'distinct_snapshot_owners':8,'distinct_owned_backward':17},'controller':{'backward_stages':list(range(1,32,2)),'forward_stages':[0,32],'queries':15,'independent_helper_outputs':16*400+2*408,'main_outputs':32*112,'productive_total':16*400+2*408+32*112,'bank_rule':'eachLOCALstage has disjoint helper bank and distinct suspended owned banks; source controller proof section4'},'negative_controls':controls,'preparation_ordering_checked':'exact event multiset matches independently derived RREF; RHS uses only nonpivot independent helper inputs; actual chronology checked on all641entrycolumns','seconds':round(time.monotonic()-started,3),'scope':'Exact free-word identities; all624retained plus17arbitrary-owned columns; literal delta, actual gauge chronology, owned returns, unchanged phase catalogue subset and 18-call controller incidence. Inherits five selected conditional framework assumptions; no full phase lowering/compiler/precision/BIT/analytic replay.'}
    (HERE/'VERIFIED-PINS.json').write_text(json.dumps({'manifest_sha256':manifest_hash,'rows':verified},indent=2)+'\n')
    (HERE/'PHYSICAL-RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
