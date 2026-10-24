"""Bounded exact first-event verification; no native or owner-fill replay."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time
from adapter import *


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def unit(p):
    return ((1,0),(0,1),(-1,0),(0,-1))[p % 4]


def tensor_reference(d, address):
    c,a,_,geo=source()
    event=d['event']
    op=a['canonical_frame'](9,c['frames'][event[3]]).adjoint().then(a['canonical_frame'](9,c['frames'][event[4]]))
    q=c['ports'][d['event'][2] % 112]
    rho=geo['rho'](q,d['stage'])
    # Native frame = physical cover g times the relative stage frame rho(U).
    host=compose(d['physical_cover_rows'],rho)
    host_inverse=inverse(host)
    state={address >> (73*d['f']) << (73*d['f']): (F(1),F(0))}
    for j in range(d['f']):
        local=mv(host_inverse,address >> (73*j) & ((1<<73)-1))
        vec,den=op.zero_state(local & 511)
        terms=[(mv(host,(local>>9<<9)|k),(F(z[0],1<<den),F(z[1],1<<den))) for k,z in enumerate(vec) if z != (0,0)]
        state={key | (k << (73*j)):mul(value,z) for key,value in state.items() for k,z in terms}
    return state


def emitted_endpoint(d, packet):
    calls=[]
    def child(desc, records):
        calls.append(desc['child_width'])
        for packed,value in records:
            for flip in range(1 << desc['child_width']):
                coefficient=value
                for j in range(desc['child_width']):
                    coefficient=mul(coefficient,(F(1,2),F(-1 if flip>>j&1 else 1,2)))
                yield {**packed,'active':packed['active']^flip},coefficient
    result={}
    for out,value in execute(d,[(packet,(F(1),F(0)))],child):
        need(all(out[k] == packet[k] for k in packet if k != 'address'),'spectator/row corruption')
        result[out['address']]=value
    need(calls == [d['child_width']], 'not exactly one rf child')
    return {x:z for x,z in result.items() if z != (0,0)}


def reject(name, fn):
    try:
        fn()
    except ValueError:
        return name
    raise ValueError('accepted mutant: '+name)


def helper_binding():
    import re
    pattern=re.compile(rb'\[1665, 316, (\d+), (\d+), (\d+), (\d+)\]')
    with gzip.open(SOURCE/'owner/FILL.json.gz','rb') as stream:
        tail=b''
        while True:
            block=stream.read(65536)
            need(bool(block),'missing actual helper row')
            data=tail+block
            match=pattern.search(data)
            if match:
                row=[1665,316,*map(int,match.groups())]
                break
            tail=data[-128:]
    c,_,emitter,_=source()
    event=emitter['emit'](True)[8469]
    plan=read(SOURCE/'owner/PLAN.json.gz')
    _,_,owner,child,port,offset=row
    side=2*plan['pairs'][str(child)]+plan['sides'][str(child)]
    width=len(c['frames'][c['final'][540]])-len(c['frames'][c['start'][540]])
    axes=read(SOURCE/'inputs/DATA-PHASES.json')['recipes'][port]['idle_children'][child]['orthogonal_axes'][offset:offset+width]
    handoff=read(HERE/'HELPER-HANDOFF.json')
    need(handoff['fill_row']==row and handoff['event']==event,'helper source witness')
    need(handoff['physical_family']==896*owner+112*side+port==206381,'helper family')
    need(handoff['selected_axes']==axes==[1<<i for i in range(64,73)],'helper actual axes')
    need(handoff['original_register']==c['helper_origin'][316]==546 and width==9,'helper origin/width')
    need(handoff['physical_family']!=66172,'data formula silently reused on helper')


def main():
    started=time.monotonic()
    pins=read(HERE/'SOURCES.json')
    for entry in pins['files']:
        if entry['usage']=='input':
            need(hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256'],'source hash '+entry['path'])
    helper_binding()
    cover=[1<<j for j in range(73)];cover[0],cover[1]=cover[1],cover[0]
    d=request(1665,8814,147,2,cover)
    need(d['family']==65689 and d['orientation']=='backward' and d['rank']==3 and d['child_width']==6,'actual source fixture')
    need(d['recipe']['right']['offset']==426 and d['recipe']['right']['phase']==1,'actual nonzero translation and absolute phase')
    need(d['physical_cover_rows'] != d['common_cover_rows'],'rho must not disappear')
    c,_,_,geometry=source()
    actual_full=geometry['stage_frame'](c['ports'][57],3,'H')[:9]
    need([mv(d['physical_cover_rows'],axis) for axis,sign in actual_full]
         ==[mv(d['native_chart_rows'],1<<j) for j in range(9)], 'owning stage_frame native chart')
    need(d['stage_alignment']=={'entry_X':57,'entry_Y':57,'exit_X':939524097,'exit_Y':939524097},'actual stage alignment')
    packet={'remaining_row':1,'address':0,'compact':{'left':7,'right':11},'prefix':19,'suffix':23,'dirty':[29,31]}
    # Every bit is touched by a round trip; an 8-coordinate slice checks correlations.
    addresses=[1<<i for i in range(147)]+[sum(((x>>j)&1)<<i for j,i in enumerate([0,2,8,72,73,80,145,146])) for x in range(256)]
    for x in addresses:
        inp={**packet,'address':x}
        child,pre=pack(d,inp);out,post=unprepare(d,child)
        need(out==inp and (pre+post)%4==0,'complete affine-phase inverse')
    reference_inputs=[0,1,(1<<146)|(1<<100)|37]
    for x in reference_inputs:
        inp={**packet,'address':x}
        need(emitted_endpoint(d,inp)==tensor_reference(d,x),'actual right-child-left endpoint')
    controls=[]
    def endpoint_mutant(key,value):
        bad=deepcopy(d);bad['recipe']['right'][key]=value
        need(emitted_endpoint(bad,{**packet,'address':1})==tensor_reference(d,1),'changed source chart endpoint')
    controls.append(reject('omit_right_translation',lambda:endpoint_mutant('offset',0)))
    controls.append(reject('omit_absolute_phase',lambda:endpoint_mutant('phase',0)))
    badview=deepcopy(d)
    badview['native_chart_rows']=badview['physical_cover_rows']
    badview['native_chart_inverse']=badview['physical_cover_inverse']
    controls.append(reject('cover_label_as_native_chart',lambda:need(
        emitted_endpoint(badview,{**packet,'address':1})==tensor_reference(d,1), 'cover label/chart confusion')))
    controls.append(reject('omit_dirty',lambda:pack(d,{k:v for k,v in packet.items() if k!='dirty'})))
    controls.append(reject('stock_out_of_range',lambda:pack(d,{**packet,'remaining_row':2})))
    badcover=cover[:];badcover[0]=badcover[1]
    controls.append(reject('singular_cover',lambda:request(1665,8814,147,2,badcover)))
    controls.append(reject('wrong_provider',lambda:request(0,8814,147,2,cover)))
    controls.append(reject('helper_is_not_data',lambda:request(1665,8469,147,2,cover)))
    # The descriptor makes packet cardinality symbolic; it allocates no 2^147 array.
    need(d['child_width']+(73-d['rank'])*d['f']+d['t']==d['e'],'full volume')
    result={'status':'PASS_ACTUAL_DATA_CLIMB_PARTIAL','event':d['event'],'family':d['family'],
            'roundtrips':len(addresses),'endpoint_inputs':len(reference_inputs),'controls':controls,
            'scope':'First actual FOUR/base data climb. Helper hosting, full class and physical tape costs are unimplemented.',
            'seconds':time.monotonic()-started}
    print(json.dumps(result,sort_keys=True))
    if '--write-fixture' in __import__('sys').argv:
        (HERE/'FIXTURE.json').write_text(json.dumps(d,indent=2)+'\n')
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':
    main()
