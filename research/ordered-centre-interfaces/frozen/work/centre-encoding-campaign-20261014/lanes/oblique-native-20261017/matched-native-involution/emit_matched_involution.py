#!/usr/bin/env python3
"""Emit the full data response through two disjoint native matchings."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
LANES=HERE.parents[1]
UTILITY=HERE.parent/'radical-centre-carry/emit_radical_centres.py'
UTILITY_SHA='fc7d93bf1efc963fa5db880aaaf9d53578083e32b4e75ef43cb739042713a2f6'
if sha256(UTILITY.read_bytes()).hexdigest()!=UTILITY_SHA:
    raise ValueError('Pinned native utility changed')
spec=importlib.util.spec_from_file_location('matching_native_utility',UTILITY)
u=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=u
spec.loader.exec_module(u)
need,basis,add=u.need,u.basis,u.add
PINS={
    'controller-followthrough-20261017/matched-involution-20261018/MATCHED-INVOLUTION-PROGRAM.json':
        ('plain','e2443eee2a7081ce3b57b9b7afcf4f1b061b9d8ddf0fbbeb5f7b29ce0d148902'),
    'history-encoding/permutation64-native-20261018/PERMUTATION64-PROGRAMS.json.gz':
        ('decompressed','87c76a500f8e22e4b500a5f5a64f23ef8cecadd0036785d7f54b2415972f1ff9'),
}
PHASE_CACHE={}
ENDPOINT_CACHE=set()


def read(relative):
    mode,want=PINS[relative]
    raw=(LANES/relative).read_bytes()
    if mode=='decompressed':
        raw=gzip.decompress(raw)
    need(sha256(raw).hexdigest()==want,'Pinned input '+relative)
    return json.loads(raw)


def rational_rows(rows):
    return [{int(k):F(v) for k,v in row.items()} for row in rows]


def multiply(left,right):
    product=[]
    for row in left:
        value={}
        for j,c in row.items():
            add(value,right[j],c)
        product.append(value)
    return product


def build(provider,canonical,matching,component64,response,direction):
    frames=deepcopy(canonical['frames'])
    index={tuple(row):i for i,row in enumerate(frames)}

    def frame_id(vectors):
        vectors=tuple(vectors)
        if vectors not in index:
            index[vectors]=len(frames)
            frames.append(list(vectors))
        return index[vectors]

    start=list(canonical['start'])
    finish=list(start)
    finish[:112]=[1]*112
    finish[112:224]=canonical['final'][112:224]
    current=list(start)
    state=[{i:F(1)} for i in range(len(start))]
    events,recipes=[],{}
    prefix_bound=F(1)

    def scalar(op,target,origin=None,coefficient=F(1)):
        nonlocal prefix_bound
        frame=current[target]
        coefficient=F(coefficient)
        if op=='scale':
            gate=[op,target,coefficient.numerator,coefficient.denominator]
            state[target]={k:coefficient*v for k,v in state[target].items() if coefficient*v}
        else:
            need(op=='add' and target!=origin and current[origin]==frame,'Equal-frame scalar addition')
            gate=[op,target,origin,coefficient.numerator,coefficient.denominator]
            add(state[target],state[origin],coefficient)
        events.append(['scalar',gate,frame])
        prefix_bound=max(prefix_bound,sum(abs(v) for v in state[target].values()))

    def native(target,new):
        old=current[target]
        need(old!=new,'Nontrivial native edge')
        key=str(old)+':'+str(new)
        physical=(tuple(frames[old]),tuple(frames[new]))
        if physical not in PHASE_CACHE:
            operation=u.compiler.canonical_frame(9,physical[0]).adjoint().then(
                u.compiler.canonical_frame(9,physical[1]))
            record,_=u.compiler.lower_child(operation)
            need(record['rank']==abs(len(frames[new])-len(frames[old])),'Exact nested native rank')
            u.phase.equal(u.phase.recipe(record),u.phase.adjoint(u.phase.frame(frames[old],9))+
                          u.phase.frame(frames[new],9),'Matching native edge '+key)
            PHASE_CACHE[physical]=record
        recipes[key]=PHASE_CACHE[physical]
        events.append(['native',target,old,new,recipes[key]['rank'],key])
        current[target]=new

    modes=matching['modes']
    mode_by_id={mode['id']:mode for mode in modes}
    planes,holes={},{}
    codes=[]
    for pair in matching['pair_codes']:
        a,b=pair['ports']
        plane_basis=basis((canonical['ports'][a],canonical['ports'][b]))
        need(len(plane_basis)==2,'Pair plane rank')
        plane=frame_id(plane_basis)
        hole_basis=basis(v for v in range(1,512) if all((v&q).bit_count()%2==0 for q in plane_basis))
        need(len(hole_basis)==7,'Pair-hole rank')
        hole=frame_id(hole_basis)
        for mid in pair['mode_ids']:
            planes[mid],holes[mid]=plane,hole
        native(a,plane)
        native(b,plane)
        av,bv,aw,bw=[F(c) for row in pair['matrix'] for c in row]
        need(av*aw+bv*bw==0 and all(abs(c)==1 for c in (av,bv,aw,bw)),'Hadamard pair rows')
        local=[]

        def code(op,target,origin=None,coefficient=F(1)):
            if op=='scale' and coefficient==1:
                return
            scalar(op,target,origin,coefficient)
            local.append((op,target,origin,F(coefficient)))

        for offset in (0,112):
            code('scale',offset+a,coefficient=av)
            code('scale',offset+b,coefficient=bv)
            code('add',offset+a,offset+b)
            code('scale',offset+b,coefficient=-2)
            code('add',offset+b,offset+a)
            code('scale',offset+b,coefficient=aw/av)
        need(state[a]=={a:av,b:bv} and state[b]=={a:aw,b:bw},'Coded X pair')
        need(state[112+a]=={112+a:av,112+b:bv} and state[112+b]=={112+a:aw,112+b:bw},'Coded Y pair')
        codes.append({'ports':[a,b],'plane':plane,'pair_hole':hole,'code':local})
    transfer_cuts=[]
    A=rational_rows(matching['mode_response'])
    for target_mode,row in enumerate(A):
        need(len(row)==1,'One mode source per target')
        source_mode,weight=next(iter(row.items()))
        need(source_mode!=target_mode and abs(weight)==1,'Signed off-diagonal matching')
        source=mode_by_id[source_mode]['carrier']
        target=112+mode_by_id[target_mode]['carrier']
        need(mode_by_id[source_mode]['vertex']==mode_by_id[target_mode]['vertex'],'One vertex per matching edge')
        source_plane=planes[source_mode]
        target_hole=holes[target_mode]
        need(len(basis((*frames[source_plane],*frames[target_hole])))==7,'Source plane lies in the target pair hole')
        native(target,source_plane)
        transfer_cuts.append({'source_mode':source_mode,'target_mode':target_mode,'weight':str(weight),
                              'source':source,'target':target,'frame':source_plane,'add_event':len(events)})
        if direction=='forward':
            scalar('add',target,source,weight)
        else:
            scalar('add',source,target,-weight)
        native(target,target_hole)
    for p in matching['large_ports']:
        native(p,1)
    for pair in reversed(codes):
        for op,target,origin,c in reversed(pair['code']):
            scalar(op,target,origin,1/c if op=='scale' else -c)
    for p in matching['large_ports']:
        native(112+p,finish[112+p])

    inherited=component64['providers'][provider][direction]
    old_to_new={i:frame_id(row) for i,row in enumerate(inherited['frames'])}
    inherited_first=len(events)
    for event in inherited['events']:
        if event[0]=='native':
            _,target,old,new,rank,key=event
            need(current[target]==old_to_new[old],'Inherited native entry frame')
            native(target,old_to_new[new])
            need(events[-1][4]==rank and json.dumps(recipes[events[-1][5]],sort_keys=True)==json.dumps(inherited['native_recipes'][key],sort_keys=True),
                 'Inherited native recipe is unchanged')
        else:
            need(event[0]=='scalar','Inherited event grammar')
            gate,frame=event[1:]
            op,target,origin,num,den=gate
            need(current[target]==old_to_new[frame] and op=='add','Inherited scalar frame')
            scalar(op,target,origin,F(num,den))
    expected=[{i:F(1)} for i in range(len(start))]
    for t,row in enumerate(response):
        if direction=='forward':
            add(expected[112+t],row)
        else:
            for s,c in row.items():
                add(expected[s],{112+t:-c})
    need(state==expected and current==finish,'All native data and borrowed input columns')
    endpoints=json.loads(u.read('new-native-recipes-20261017/'+provider+'/CLIFFORD-RECIPES.json'))['endpoint_adapters']
    for record in endpoints:
        port,role=record['port'],record['role']
        key=provider,role,port
        if key not in ENDPOINT_CACHE:
            conventional=(('C',canonical['ports'][port],1),) if role=='source' else (
                ('C',canonical['ports'][port],-1),)+u.phase.fourier(9)
            f=start[port] if role=='source' else finish[112+port]
            u.phase.equal(u.phase.recipe(record),u.phase.adjoint(conventional)+u.phase.frame(frames[f],9),
                          'Matched endpoint '+str(key))
            ENDPOINT_CACHE.add(key)
    profile=Counter(event[4] for event in events if event[0]=='native')
    word={'frames':frames,'start':start,'final':finish,'events':events,'native_recipes':recipes,
          'endpoint_adapters':endpoints,'pair_codes':codes,'transfer_cuts':transfer_cuts,
          'inherited_64_first_event':inherited_first}
    receipt={'all_input_columns':len(start),'arbitrary_untouched_helpers':len(start)-224,
             'owned_fields':0,'private_fields':0,'extra_query_children':0,
             'profile':dict(sorted(profile.items())),'native_mass':sum(k*v for k,v in profile.items()),
             'native_children':sum(profile.values()),'real_scalar_primitives':u.scalar_price(events),
             'native_recipe_count':len(recipes),'endpoint_map_count':len(endpoints),
             'native_side_map_bound':2*sum(profile.values()),
             'top_level_max_array_l2_amplification_bound':str(prefix_bound)}
    print(provider,direction,receipt,flush=True)
    return word,receipt


def replay(word,response,direction):
    current=list(word['start'])
    state=[{i:F(1)} for i in range(len(current))]
    for event in word['events']:
        if event[0]=='native':
            _,target,old,new,rank,key=event
            need(current[target]==old and word['native_recipes'][key]['rank']==rank,'Serialized native edge')
            current[target]=new
        else:
            need(event[0]=='scalar','Serialized grammar')
            gate,frame=event[1:]
            op,target=gate[:2]
            need(current[target]==frame,'Serialized scalar target')
            if op=='scale':
                c=F(*gate[2:])
                state[target]={k:c*v for k,v in state[target].items() if c*v}
            else:
                need(op=='add','Serialized scalar kind')
                origin=gate[2]
                need(target!=origin and current[origin]==frame,'Serialized scalar source')
                add(state[target],state[origin],F(*gate[3:]))
    expected=[{i:F(1)} for i in range(len(current))]
    for t,row in enumerate(response):
        if direction=='forward':
            add(expected[112+t],row)
        else:
            for s,c in row.items():
                add(expected[s],{112+t:-c})
    need(state==expected and current==word['final'],'Serialized all-column map')


def encode(value):
    if isinstance(value,F):
        return str(value)
    raise TypeError(type(value).__name__)


def main():
    core=json.loads(u.read('new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz'))
    matching=read('controller-followthrough-20261017/matched-involution-20261018/MATCHED-INVOLUTION-PROGRAM.json')
    component64=read('history-encoding/permutation64-native-20261018/PERMUTATION64-PROGRAMS.json.gz')
    large=set(matching['large_ports'])
    need(large.isdisjoint(component64['active_ports']) and large|set(component64['active_ports'])==set(range(112)),
         'Disjoint complete response support')
    old=rational_rows(matching['response'])
    small=rational_rows(component64['response'])
    response=[old[i] if i in large else small[i] for i in range(112)]
    need(all(response[i].get(j,0)==response[j].get(i,0) for i in range(112) for j in range(112)),
         'Symmetric full response')
    need(multiply(response,response)==[{i:F(1)} for i in range(112)],'Full response is an involution')
    selected=matching['selected_ports']
    L=[{j:response[p].get(q,0) for j,q in enumerate(selected) if response[p].get(q,0)} for p in selected]
    need(L==rational_rows(matching['selected_block']),'Selected principal block is unchanged')
    need(multiply(L,rational_rows(matching['selected_inverse']))==[{i:F(1)} for i in range(8)],
         'Selected dyadic inverse')
    ordinary=[p for p in range(112) if p not in selected]
    Linv=rational_rows(matching['selected_inverse'])
    B=[{j:response[p].get(q,0) for j,q in enumerate(ordinary) if response[p].get(q,0)} for p in selected]
    D=[{j:response[p].get(q,0) for j,q in enumerate(selected) if response[p].get(q,0)} for p in ordinary]
    H=[{j:response[p].get(q,0) for j,q in enumerate(ordinary) if response[p].get(q,0)} for p in ordinary]
    Hinv=deepcopy(H)
    for row,correction in zip(Hinv,multiply(multiply(D,Linv),B)):
        add(row,correction,-1)
    identity=[{i:F(1)} for i in range(len(ordinary))]
    need(multiply(H,Hinv)==identity and multiply(Hinv,H)==identity,'Ordinary principal inverse in both orders')
    programs,receipts={},{}
    for provider,item in core['providers'].items():
        programs[provider],receipts[provider]={},{}
        for direction in ('forward','backward'):
            word,receipt=build(provider,item['canonical'],matching,component64,response,direction)
            programs[provider][direction]=word
            receipts[provider][direction]=receipt
    payload={'schema':'full-matched-native-involution-v1','response':response,'selected_ports':selected,
             'selected_block':L,'selected_inverse':matching['selected_inverse'],
             'ordinary_ports':ordinary,'ordinary_inverse':Hinv,'providers':programs}
    encoded=(json.dumps(payload,default=encode,sort_keys=True,separators=(',',':'))+'\n').encode()
    decoded=json.loads(encoded)
    for provider,words in decoded['providers'].items():
        for direction,word in words.items():
            replay(word,rational_rows(decoded['response']),direction)
    (HERE/'MATCHED-NATIVE-PROGRAM.json.gz').write_bytes(gzip.compress(encoded,mtime=0))
    receipt={'schema':'full-matched-native-involution-receipt-v1','source_pins':PINS,
             'utility_sha256':UTILITY_SHA,'utility_source_pins':u.PINS,
             'producer_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
             'payload_decompressed_sha256':sha256(encoded).hexdigest(),'providers':receipts,
             'distinct_native_phases_checked':len(PHASE_CACHE),'endpoint_phases_checked':len(ENDPOINT_CACHE),
             'full_response_symmetric':True,'full_response_square_identity':True,'selected_inverse_checked':True,
             'ordinary_inverse_both_orders_checked':True,
             'scope':'Full112 data response and both native shears; borrowed helper progress and global supplier remain separate.'}
    (HERE/'MATCHED-NATIVE-RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')


if __name__=='__main__':
    main()
