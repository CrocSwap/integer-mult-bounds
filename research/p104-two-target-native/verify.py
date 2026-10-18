"""Independent native interpreter and source-bound whole-word induction.

Default verification imports neither the Clifford compiler nor source verifier.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations,product
from collections import Counter
import argparse,copy,gzip,hashlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import BASE,HERE,assemble,canon,check_sources,load_module,native_source,need,physical_map,read_json,span
N=None

def geometry(base):
    rr=[]
    for i,j in combinations(range(8),2):
        for sign in [-1,1]:
            r=[0]*8;r[i]=2;r[j]=2*sign;rr.append(tuple(r))
    rr+= [(1,*s)for s in product([-1,1],repeat=7)if s.count(-1)%2==0]
    rr.sort();need(len(set(rr))==120,'root reconstruction')
    iso=base['label_isometry'];convert=physical_map(iso,N)
    inner=lambda a,b:sum(x*y for x,y in zip(a,b))//4
    binary=[sum(((inner(a,b)+1)&1)<<j for j,b in enumerate(rr))for a in rr]
    ix=iso['pivot_root_indices'];need(len(ix)==len(set(ix))==9,'nine root pivots')
    compressed=[sum(((row>>j)&1)<<k for k,j in enumerate(ix))for row in binary]
    physical=[convert(x)for x in compressed]
    need(physical==iso['physical_root_labels'],'physical root coordinates')
    for i,a in enumerate(physical):
        for j,b in enumerate(physical):need(((a&b).bit_count()&1)==((binary[i]>>j)&1),'root pairing')
    fix=read_json(BASE/'inputs/P104-FIXTURE.json')['section4_explicit_P104']
    removed={tuple(r)for r in fix['F0']+fix['C']};ports=[r for r in rr if r not in removed]
    need(len(ports)==104,'104 source ports')
    return ports,dict(zip(rr,physical)),convert

def operator(rec,inverse=False):
    old,new=tuple(rec['old']),tuple(rec['new'])
    need(len(span(old))==1<<len(old)and len(span(new))==1<<len(new),'independent frames')
    need(span(old)<=span(new)or span(new)<=span(old),'nested transport')
    recipe=rec['inverse_recipe']if inverse else rec['recipe']
    need(recipe['rank']==rec['rank']==abs(len(old)-len(new))and rec['rank']>0,'native rank invoice')
    a,b=(new,old)if inverse else (old,new)
    N.equal(N.recipe(recipe),N.adjoint(N.frame(a,9))+N.frame(b,9),'signed Pauli and scalar phase')

def occurrence_set(extra,events,added,frame):
    covered=set()
    for rec in extra['transports']:
        key=(tuple(rec['old']),tuple(rec['new']))
        for i in rec['events']:
            need(type(i)is int and i in added and i not in covered,'unique added occurrence')
            e=events[i];need(e[0]=='transport'and(frame(e[2]),frame(e[3]))==key and e[4]==rec['rank'],'literal occurrence binding');covered.add(i)
    need(covered=={i for i in added if events[i][0]=='transport'},'complete occurrence coverage')
    return covered

def native_check(base,extra,events,added,convert):
    frame=lambda f:canon(convert(x)for x in f)
    need(extra['source_circuit_sha256']==hashlib.sha256((HERE/'inputs/PR2445-CIRCUIT.json').read_bytes()).hexdigest(),'compiled source pin')
    maps=[]
    for source in [base,extra]:
        mapping={}
        for rec in source['transports']:
            key=(tuple(rec['old']),tuple(rec['new']));need(key not in mapping,'unique edge');mapping[key]=rec
            operator(rec)
            if source is extra:operator(rec,True)
        maps.append(mapping)
    covered=occurrence_set(extra,events,added,frame)
    paid=Counter();newpaid=Counter()
    for i,e in enumerate(events):
        if e[0]!='transport':continue
        rec=maps[int(i in added)].get((frame(e[2]),frame(e[3])))
        need(rec is not None and rec['rank']==e[4],'every occurrence natively realized')
        paid[e[4]]+=1
        if i in added:newpaid[e[4]]+=1
    need(dict(newpaid)=={1:142,2:16,6:18,7:60},'added histogram')
    need(dict(paid)=={1:1216,2:74,3:86,4:104,5:48,6:42,7:68,8:8},'whole histogram')
    return dict(unique_added=len(maps[1]),previously_absent_edges=len(set(maps[1])-set(maps[0])),added_occurrences=len(covered),all_occurrences=sum(paid.values()),added_profile=dict(sorted(newpaid.items())),full_profile=dict(sorted(paid.items())),rank_mass=sum(k*v for k,v in paid.items()))

def endpoints(base,initial,final,labels,ports,convert):
    frame=lambda f:canon(convert(x)for x in f);seen=set()
    for rec in base['endpoint_adapters']:
        reg,pos=rec['register'],rec['position'];need((reg,pos)not in seen,'unique endpoint');seen.add((reg,pos))
        normal=labels[ports[int(reg[1:])]];f=tuple(rec['frame'])
        need(normal==rec['normal']and rec['recipe']['rank']==0,'endpoint label and cost')
        if pos=='entry':
            need(reg.startswith('X')and f==frame(initial[reg])==(normal,),'source entry chart')
            expected=N.adjoint((('C',normal,1),))+N.frame(f,9)
        else:
            need(pos=='exit'and reg.startswith('Y')and f==frame(final[reg]),'target exit chart')
            need(len(f)==8 and all(not((v&normal).bit_count()&1)for v in f),'target hyperplane')
            expected=N.adjoint(N.frame(f,9))+(('C',normal,-1),)+N.fourier(9)
        N.equal(N.recipe(rec['recipe']),expected,'intrinsic endpoint phase')
    need(seen=={('X'+str(i),'entry')for i in range(104)}|{('Y'+str(i),'exit')for i in range(104)},'208 endpoints')

def induction(initial,final,events,ports,convert):
    frame=lambda f:canon(convert(x)for x in f)
    state={name:{name:Q(1)}for name in initial};frames={name:frame(f)for name,f in initial.items()};adds=Counter();private=Counter()
    for e in events:
        op=e[0]
        if op=='transport':
            _,reg,old,new,rank=e;a,b=frame(old),frame(new)
            need(reg in frames and frames[reg]==a,'transport chronological source')
            need(rank==abs(len(a)-len(b))and(span(a)<=span(b)or span(b)<=span(a)),'nested charge');frames[reg]=b
        elif op=='zero':
            _,reg,f=e;need(reg=='C'and reg not in state,'owned initialization');state[reg]={};frames[reg]=frame(f);private[op]+=1
        elif op=='copy':
            _,reg,src,f=e;need(reg=='C'and not state[reg]and frames[reg]==frames[src]==frame(f),'owned common-frame copy');state[reg]=dict(state[src]);private[op]+=1
        elif op=='erase':
            _,reg,f=e;need(reg=='C'and frames[reg]==frame(f),'owned discard');state.pop(reg);frames.pop(reg);private[op]+=1
        else:
            need(op=='add','event type');_,reg,src,a,f=e;a=Q(a)
            need(reg!=src and frames[reg]==frames[src]==frame(f),'common physical scalar chart')
            for name,v in tuple(state[src].items()):
                v=state[reg].get(name,Q(0))+a*v
                if v:state[reg][name]=v
                else:state[reg].pop(name,None)
            adds[str(a)]+=1
    need(set(state)==set(initial)==set(final)and len(state)==358,'358 public columns')
    for name in initial:
        expected={name:Q(1)}
        if name.startswith('Y'):
            t=int(name[1:])
            if t in (0,1):expected['X'+str(t)]=Q(1)
            else:expected.update({'X'+str(k):Q(sum(a*b for a,b in zip(ports[t],r)),8)for k,r in enumerate(ports)if sum(a*b for a,b in zip(ports[t],r))})
        need(state[name]==expected,'logical endpoint '+name);need(frames[name]==frame(final[name]),'final chart '+name)
    need(private=={'zero':8,'copy':8,'erase':8},'eight owned private lifetimes')
    serial=[[name,[[k,str(v)]for k,v in sorted(state[name].items())]]for name in sorted(state)]
    return dict(columns=358,endpoint_coefficients=128164,scalar_additions=sum(adds.values()),scalar_coefficients=dict(sorted(adds.items())),private_lifetimes=dict(private),endpoint_sha256=hashlib.sha256(json.dumps(serial,separators=(',',':')).encode()).hexdigest())

def rejected(fn,label):
    try:fn()
    except (ValueError,KeyError,IndexError):return label
    raise ValueError('accepted faulty control: '+label)

def replay():
    global N
    check_sources()
    N=load_module('p104_two_target_native_interpreter',BASE/'vendor/native_verify.py')
    base=native_source();extra=json.loads(gzip.decompress((HERE/'NATIVE.json.gz').read_bytes()))
    initial,final,events,added=assemble();ports,labels,convert=geometry(base)
    catalog=native_check(base,extra,events,added,convert);endpoints(base,initial,final,labels,ports,convert)
    logical=induction(initial,final,events,ports,convert);controls=[]
    for inverse in (False,True):
        rec=copy.deepcopy(extra['transports'][0]);key='inverse_recipe'if inverse else 'recipe';rec[key]['left']['phase']=(rec[key]['left']['phase']+1)%4
        controls.append(rejected(lambda:operator(rec,inverse),'inverse phase'if inverse else 'forward phase'))
    rec=copy.deepcopy(extra['transports'][0]);rec['rank']+=1
    controls.append(rejected(lambda:operator(rec),'rank mischarge'))
    bad=copy.deepcopy(extra);bad['transports'].pop()
    controls.append(rejected(lambda:occurrence_set(bad,events,added,lambda f:canon(convert(x)for x in f)),'missing native edge'))
    for label,predicate in [('dirty compensation',lambda e:e[0]=='add'and e[1]=='Y0'and e[2].startswith('N')),('source capture',lambda e:e[0]=='add'and e[1].startswith('N')and e[2].startswith('X')),('collector mixing',lambda e:e[0]=='add'and e[1].startswith('N')and e[2].startswith('N'))]:
        bad=copy.deepcopy(events);ix=next(i for i in sorted(added)if predicate(bad[i]));bad[ix][3]='0'
        controls.append(rejected(lambda:induction(initial,final,bad,ports,convert),label))
    bad=copy.deepcopy(events);ix=next(i for i in sorted(added)if bad[i][0]=='add'and bad[i][4]);bad[ix][4]=[]
    controls.append(rejected(lambda:induction(initial,final,bad,ports,convert),'unequal scalar chart'))
    alt=copy.deepcopy(events)
    for e in alt:
        if e[0]=='transport':e[2].reverse();e[3].reverse()
        else:e[-1].reverse()
    need(induction(initial,final,alt,ports,convert)==logical,'equivalent basis positive control')
    return dict(status='PASS_P104_TWO_TARGET_NATIVE',events=len(events),native=catalog,logical=logical,intrinsic_endpoint_adapters=208,physical_pairings=14400,forward_and_inverse_added_operators=2*catalog['unique_added'],controls=controls,positive_controls=['equivalent binary basis order'],scope='Exact finite native frame transport and forward logical identity for PR2445. Inverse edge recipes are not supplier reverse-orientation admission. Global owners, moment, precision, address/tape and all-size admission remain open.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);ap.add_argument('--emit-initial-result',action='store_true');args=ap.parse_args()
    result=json.loads(json.dumps(replay()));raw=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.emit_initial_result:
        with (HERE/'RESULT.json').open('x',encoding='utf8')as f:f.write(raw)
    else:need(result==read_json(HERE/'RESULT.json'),'fixed receipt mismatch')
    if args.out:
        with args.out.open('x',encoding='utf8')as f:f.write(raw)
    print('PASS_P104_TWO_TARGET_NATIVE added=236 unique=161 columns=358 rank_mass=3070 controls='+str(len(result['controls'])))

if __name__=='__main__':main()
