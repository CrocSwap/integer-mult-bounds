#!/usr/bin/env python3
"""Bounded PR5377 physical-delta check; imports no submitted evaluator.

Reverse functional propagation proves the three frozen source rows. A separate
forward propagation checks all independent columns and native frame labels.
This does not lower Gaussian phases or run the completion/compiler pipeline.
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

def advance_all(word, direction, specialized):
    c=word['canonical']; owned={('C',0)}
    if specialized: owned|={('C',1),('L',230)}
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
            check(direction=='backward' and specialized and (dst,old,new)==(('L',92),254,1),'authorized zero replacement')
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
    return {'persistent_inputs':632-int(specialized),'owned_arbitrary_inputs':len(owned),
            'paid':dict(sorted(paid.items())),'checked_zero_event_indices':zeros,
            'endpoint_pass':True,'frame_pass':True}

def main():
    start=time.monotonic(); source=read('ACTUAL-WORD.json.gz'); candidate=read('WORD.json.gz')
    c=source['canonical']; old=source['programs']['backward']; new=candidate['programs']['backward']
    # Pin consumed binary payloads separately from the PR's reported result.
    pins=read('SOURCES.json')
    for row in pins['files']:
        basename=Path(row['path']).name
        if basename not in ('ACTUAL-WORD.json.gz','PHASE-VALIDATION.json.gz'): continue
        raw=(P/basename).read_bytes()
        check(hashlib.sha256(raw).hexdigest()==row['sha256'],'source SHA256')
        check(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source blob')
    check(hashlib.sha1(b'blob '+str(len((P/'WORD.json.gz').read_bytes())).encode()+b'\0'+(P/'WORD.json.gz').read_bytes()).hexdigest()=='5e79bd826c6ca1e782766ea0ae28a61d136303d1','connector pinned candidate blob')
    physical=dict(c); physical.pop('local_profile')
    check(candidate['canonical']==physical,'all canonical physical maps unchanged')
    check(candidate['programs']['forward']==source['programs']['forward'],'literal forward program unchanged')
    expected=[['scalar',['clear',['L',230]],0]]
    for helper,sign in [(324,1),(326,-1),(328,-1),(333,1)]:
        expected.append(['scalar',['add',['L',230],['L',helper],sign,1],0])
    for i,e in enumerate(old):
        if i==11332:
            expected += [['scalar',['clear',['C',0]],254],['scalar',['copy',['C',0],['C',1]],254],['scalar',['clear',['C',1]],254]]
        elif i==15584: expected.append(['zero_retag',['L',92],254,1])
        else: expected.append(e)
        if i==11205: expected += [['scalar',['clear',['C',1]],254],['scalar',['copy',['C',1],['L',92]],254]]
    expected.append(['scalar',['clear',['L',230]],1])
    check(new==expected,'exact only declared event delta')
    delta={(('L',i),()):F(q) for i,q in {230:1,324:-1,326:1,328:1,333:-1}.items()}
    q=pullback(old,('L',92),11205)
    center=pullback(old,('C',0),11332)
    zero=pullback(old,('L',92),15584)
    check(difference(center,q)=={k:v/4 for k,v in delta.items()},'independent reverse center-minus-snapshot')
    check(zero=={k:-v/4 for k,v in delta.items()},'independent reverse zero-site')
    # Negative controls change actual premises, not just reported receipts.
    wrong=dict(delta); wrong[(('L',324),())]*=-1
    check(difference(center,q)!={k:v/4 for k,v in wrong.items()},'wrong relation must fail')
    wrong_q=pullback(old,('L',63),11205)
    check(difference(center,wrong_q)!={k:v/4 for k,v in delta.items()},'wrong snapshot must fail')
    allcolumns={}
    for name,w,specialized in [('source',source,False),('candidate',candidate,True)]:
        for direction in ['forward','backward']:
            allcolumns[name+'_'+direction]=advance_all(w,direction,specialized and direction=='backward')
    controller=read('controller-CONTROLLER.json')
    calls=[e for e in controller['physical_events'] if e[0]=='LOCAL']
    check([e[1] for e in calls if e[3]]==list(range(1,32,2)),'16 backward stage incidence')
    check([e[1] for e in calls if not e[3]]==[0,32],'two retained forward calls')
    check(sum(e[0]=='QUERY_SHEAR' for e in controller['physical_events'])==15,'all query shears')
    phase=read('PHASE-VALIDATION.json.gz')
    check(phase['actual_word_canonical_sha256']==hashlib.sha256(gzip.decompress((P/'ACTUAL-WORD.json.gz').read_bytes())).hexdigest(),'phase exact source payload binding')
    check(phase['status']=='PASS_JOINT_HELPER_MAPS_ALL_ACTUAL_ABSOLUTE_PHASES','source absolute phase receipt')
    result={'status':'PASS_BOUNDED_INDEPENDENT_PHYSICAL_DELTA','head':'c448d13c71908647f968b06cddb795ce7d288139',
            'source_row_pullbacks':{'snapshot_terms':len(q),'center_minus_snapshot':'Delta/4','zero_site':'-Delta/4'},
            'all_columns':allcolumns,'full_local_calls':calls,'query_shears':15,
            'source_phase_receipt_authenticated':True,'source_phase_lowering_rerun':False,
            'negative_controls':['wrong helper relation','wrong snapshot source'],
            'seconds':round(time.monotonic()-start,3),
            'scope':'Exact free-word identities, all-column boundaries, physical gauge compatibility, owned storage and controller orientation incidence. Inherits source physical native recipes, permitted erasure, all-size mixed-target compiler, precision, tape and integer recovery; no full compiler or theorem replay.'}
    (HERE/'independent-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
