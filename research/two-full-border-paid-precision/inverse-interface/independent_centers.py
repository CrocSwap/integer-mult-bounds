#!/usr/bin/env python3
"""Independent both-orientation center macros and complete inverse IR.
Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0

Reads pinned input only. Known phase/adapter records are gauge annotations,
not additional physical operators in this IR. Exact Clifford lowering is
inherited; this checks a generic two-coordinate oracle model independently.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import gzip,json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
PIN='7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'

def need(ok,msg):
    if not ok:raise ValueError(msg)
def owned_clear(e):
    return e[0]=='scalar' and e[1]==['clear',['C',0]]
def role(r):
    need(r[0] in ('L','C'),'known role')
    if r[0]=='C':need(r[1]==0,'only C0');return 632
    need(0<=r[1]<632,'persistent role');return r[1]
def parse(c,p,direction):
    macros=[]
    for i,e in enumerate(p):
        if e[0]!='center':continue
        j=i-1
        while j>=0 and not owned_clear(p[j]):j-=1
        k=i+1
        while k<len(p) and not owned_clear(p[k]):k+=1
        need(0<=j<i<k<len(p),'bounded center macro')
        _,owner,old,new,rank=e
        need(owner==0 and rank==8,'actual rank8 owned call')
        need(p[j][2]==old and p[k][2]==new,'owned clear frame endpoints')
        capture=[]
        for item in p[j+1:i]:
            need(item[0]=='scalar' and item[2]==old,'capture frame')
            g=item[1]
            need(g[0] in ('copy','add') and g[1]==['C',0] and g[2][0]=='L','capture into C only')
            need(g[0]!='copy' or not capture,'copy is initial capture')
            capture.append((role(g[2]),Q(1) if g[0]=='copy' else Q(g[3],g[4])))
        fanout=[]
        for item in p[i+1:k]:
            need(item[0]=='scalar' and item[2]==new,'fanout frame')
            g=item[1]
            need(g[0]=='add' and g[1][0]=='L' and g[2]==['C',0],'C-to-persistent fanout only')
            fanout.append((role(g[1]),Q(g[3],g[4])))
        sources={x for x,a in capture};targets={x for x,a in fanout}
        need(len(sources)==len(capture) and len(targets)==len(fanout),'distinct capture and target fields')
        need(sources.isdisjoint(targets),'capture fields untouched by fanout')
        if direction=='forward':
            need((len(capture),len(fanout))==(1,22),'forward1to22 shape')
            need((len(c['frames'][old]),len(c['frames'][new]))==(8,0),'forward8to0 frame')
            need(capture[0][1]==1 and all(abs(a)==Q(1,4) for x,a in fanout),'forward coefficients')
        else:
            need((len(capture),len(fanout))==(22,1),'backward22to1 shape')
            need((len(c['frames'][old]),len(c['frames'][new]))==(0,8),'backward0to8 frame')
            need(fanout[0][1]==-1 and all(abs(a)==Q(1,4) for x,a in capture),'backward coefficients')
        macros.append({'start':j,'paid_site':i,'end':k,'old':old,'new':new,'rank':rank,
                       'capture':capture,'fanout':fanout})
    need(len(macros)==8,'all eight centers')
    need(all(macros[i]['end']<macros[i+1]['start'] for i in range(7)),'disjoint macro intervals')
    starts={m['start']:m for m in macros};ir=[];i=0
    while i<len(p):
        if i in starts:
            m=starts[i];ir.append(('macro',m,1));i=m['end']+1;continue
        e=p[i]
        if e[0]=='scalar':
            need(e[1][0] in ('add','scale') and e[1][1][0]=='L','outside macro persistent reversible scalar')
            if e[1][0]=='add':need(e[1][2][0]=='L','persistent source')
            ir.append(('scalar',e[1],e[2]))
        elif e[0]=='climb':
            _,part,a,old,new,r=e
            need(len(c['frames'][new])-len(c['frames'][old])==r,'paid rank from endpoint dimensions')
            ir.append(('oracle',i,a,old,new,r,False,'climb'))
        elif e[0]=='warp':
            _,reg,operator,old,new=e
            ir.append(('oracle',i,role(reg),old,new,0,False,'warp'))
        else:need(e[0] in ('phase','adapter','residual_adapter'),'only known gauge annotations ignored')
        i+=1
    return macros,ir

def reverse_ir(ir):
    inv=[]
    for e in reversed(ir):
        if e[0]=='macro':inv.append(('macro',e[1],-e[2]))
        elif e[0]=='scalar':
            g=list(e[1])
            if g[0]=='add':g[3]=-g[3]
            else:
                need(g[2]!=0,'invertible SCALE')
                q=1/Q(g[2],g[3]);g[2],g[3]=q.numerator,q.denominator
            inv.append(('scalar',g,e[2]))
        else:
            _,i,a,old,new,r,back,kind=e
            inv.append(('oracle',i,a,new,old,r,not back,kind))
    return inv

def frame_walk(c,ir,start,end):
    frames=list(c[start])+[None];contacts=paid=warps=0
    for e in ir:
        if e[0]=='macro':
            m=e[1];frames[632]=m['old']
            for a,q in m['capture']:need(frames[a]==m['old'],'capture persistent frame');contacts+=1
            need(abs(len(c['frames'][m['new']])-len(c['frames'][m['old']]))==m['rank'],'center frame rank')
            frames[632]=m['new'];paid+=1
            for a,q in m['fanout']:need(frames[a]==m['new'],'fanout persistent frame');contacts+=1
        elif e[0]=='scalar':
            g,fr=e[1:];need(frames[role(g[1])]==fr,'persistent scalar destination frame')
            if g[0]=='add':need(frames[role(g[2])]==fr,'persistent scalar source frame')
            contacts+=1
        else:
            _,site,a,old,new,r,back,kind=e
            need(frames[a]==old,'oracle source frame');frames[a]=new
            if kind=='climb':paid+=1
            else:warps+=1
    need(frames[:632]==c[end],'all632 final frames')
    need(paid==3298 and warps==240,'all actual paid and warp sites retained')
    return {'persistent_scalar_contacts':contacts,'paid_sites':paid,'warp_sites':warps,'persistent_endpoint_frames':632}

def oracle(site,seed):
    a=Q((site+seed)%3-1,2);b=Q((site//3+2*seed)%3-1,2)
    return (1+a*b,a,b,Q(1))
def transform(v,A,back=False):
    a,b,c,d=A
    if back:
        det=a*d-b*c;need(det!=0,'invertible two-coordinate oracle');a,b,c,d=d/det,-b/det,-c/det,a/det
    return (a*v[0]+b*v[1],c*v[0]+d*v[1])
def run(ir,state,seed,wrong_first_inverse=False):
    x=list(state);owned=(Q(0),Q(0));wrong_used=False
    for e in ir:
        if e[0]=='scalar':
            g=e[1];a=role(g[1])
            if g[0]=='add':
                b=role(g[2]);q=Q(g[3],g[4]);x[a]=(x[a][0]+q*x[b][0],x[a][1]+q*x[b][1])
            else:
                q=Q(g[2],g[3]);x[a]=(q*x[a][0],q*x[a][1])
        elif e[0]=='oracle':
            _,site,a,old,new,r,back,kind=e
            A=oracle(site,seed)
            if wrong_first_inverse and back and not wrong_used and A!=(Q(1),Q(0),Q(0),Q(1)):
                back=False;wrong_used=True
            x[a]=transform(x[a],A,back)
        else:
            m,sign=e[1:];owned=(Q(0),Q(0))
            for a,q in m['capture']:owned=(owned[0]+q*x[a][0],owned[1]+q*x[a][1])
            owned=transform(owned,oracle(m['paid_site'],seed)) # SAME map in reverse.
            for a,q in m['fanout']:
                x[a]=(x[a][0]+sign*q*owned[0],x[a][1]+sign*q*owned[1])
            owned=(Q(0),Q(0))
    need(owned==(0,0),'owned cleanup')
    if wrong_first_inverse:need(wrong_used,'inverse-oracle control actually changed')
    return x

def local_roundtrips(macros):
    maps=[lambda z:3*z+Q(7,8),lambda z:Q((3*z+Q(7,5)).numerator//(3*z+Q(7,5)).denominator,8)]
    inputs=[[Q(((i*37+seed*11)%101)-50,8) for i in range(632)] for seed in range(3)]
    tests=0
    for m in macros:
        for A in maps:
            for original in inputs:
                state=list(original)
                for sign in (1,-1):
                    value=A(sum(q*state[a] for a,q in m['capture']))
                    for a,q in m['fanout']:state[a]+=sign*q*value
                need(state==original,'same-map macro roundtrip');tests+=1
    return tests

def serialize(m):
    return {k:[[a,str(q)] for a,q in v] if k in ('capture','fanout') else v for k,v in m.items()}
def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();need(not args.output.exists(),'fresh output path required')
    checker_sha=sha256(Path(__file__).read_bytes()).hexdigest()
    raw=args.source.read_bytes();need(sha256(raw).hexdigest()==PIN,'pinned actual source')
    packet=json.loads(gzip.decompress(raw));c=packet['canonical'];records={};controls={};total=0;last=None
    for direction in ('forward','backward'):
        program=packet['programs'][direction];macros,ir=parse(c,program,direction);inv=reverse_ir(ir)
        walk1=frame_walk(c,ir,'start','final');walk2=frame_walk(c,inv,'final','start')
        local=local_roundtrips(macros);need(local==48,'48 local tests per orientation')
        full=[]
        for seed in (1,2):
            data=[(Q(((i*17+seed*3)%43)-21,8),Q(((i*23+seed*7)%47)-23,16)) for i in range(632)]
            for order,one,two in [('forward_then_inverse',ir,inv),('inverse_then_forward',inv,ir)]:
                middle=run(one,data,seed);actual=run(two,middle,seed)
                need(actual==data,'complete632-role two-coordinate inverse')
                full.append({'seed':seed,'order':order,'persistent_roles':632,'coordinates_per_role':2})
                total+=1
            if seed==1 and direction=='backward':
                need(run(inv,run(ir,data,seed),seed,True)!=data,'wrong inverse oracle rejected')
                controls['wrong_backward_inverse_oracle']={'rejected':True,'reason':'complete public state not restored'}
        bad=deepcopy(program);m=macros[0]
        if direction=='forward':bad[m['paid_site']+1][1][1]=['L',m['capture'][0][0]]
        else:bad[m['paid_site']+1][1][1]=['L',m['capture'][0][0]]
        try:parse(c,bad,direction)
        except ValueError as exc:controls[direction+'_capture_destination_overlap']={'rejected':True,'reason':str(exc)}
        else:raise ValueError('overlap mutant accepted')
        bad=deepcopy(program);bad[m['paid_site']][4]=7
        try:parse(c,bad,direction)
        except ValueError as exc:controls[direction+'_wrong_center_rank']={'rejected':True,'reason':str(exc)}
        else:raise ValueError('rank mutant accepted')
        records[direction]={'macros':[serialize(m) for m in macros],'local_roundtrips':local,
                            'full_word_roundtrips':full,'forward_frame_walk':walk1,'inverse_frame_walk':walk2,
                            'paid_profile':dict(sorted(Counter(e[5] if e[0]=='climb' else e[4] for e in program if e[0] in ('climb','center')).items())),
                            'ignored_known_gauge_markers':dict(Counter(e[0] for e in program if e[0] in ('phase','adapter','residual_adapter')))}
    f=records['forward']['macros'];b=records['backward']['macros']
    need(all(x['capture'][0][0]==y['fanout'][0][0] and x['fanout']==y['capture'] and x['old']==y['new'] and x['new']==y['old'] for x,y in zip(f,b)),'literal transpose-shaped source pairing')
    result={'status':'PASS_INDEPENDENT_BOTH_ORIENTATIONS_CENTER_AND_INVERSE_IR','checker_sha256':checker_sha,
            'source_sha256':PIN,'source_head':'0ce1b5c9fb7163d0b2f0ac3db95fc418dbbcec62',
            'orientations':records,'total_local_roundtrips':96,'total_full_word_roundtrips':total,
            'controls':controls,'source_unchanged':sha256(args.source.read_bytes()).hexdigest()==PIN,
            'scope':['Both literal center shapes; same deterministic center map in inverse, negated fanout, exact scalar arithmetic.',
                     'Complete generic632-role two-coordinate execution with true inverse at every non-center paid/warp oracle.',
                     'Known adapter/phase records are annotations in this gauge; actual physical lowerings are inherited.',
                     'Not a proof of recursive child inverse availability or fresh-D Laurent coherence.']}
    need(result['source_unchanged'],'input unchanged')
    need(sha256(Path(__file__).read_bytes()).hexdigest()==checker_sha,'checker unchanged during replay')
    with args.output.open('x') as output:
        output.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'local_roundtrips':96,'full_word_roundtrips':total,'controls':len(controls)}))
if __name__=='__main__':main()
