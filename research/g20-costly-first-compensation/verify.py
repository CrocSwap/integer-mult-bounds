"""Complete costly-first, two-rewrite native-route lower invoice.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Source A2 word and emitter: Ali Romman, PR5708; all-native floor and first
census: PR6324, following unpaidmoon PR6290 and Nick Petalas PR6305.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from types import ModuleType
import argparse
import gzip
import json
import time

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[1]
PREFIX='research/g20-neutral-two-step-obstruction/'

def need(condition,message):
    if not condition:raise ValueError(message)

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()

def module(name,path):
    raw=path.read_bytes();result=ModuleType(name);result.__file__=str(path)
    exec(compile(raw,str(path),'exec'),result.__dict__)
    return result

def authenticate():
    manifest=json.loads((PACKAGE/'SOURCES.json').read_bytes())
    for entry in manifest['files']:
        if entry['usage']=='input':
            raw=(ROOT/entry['path']).read_bytes()
            need(sha256(raw).hexdigest()==entry['sha256'],'source bytes: '+entry['path'])

def descriptor(c):return [c[0],c[1],c[2],c[3],len(c[4])]

def hinges(delta):
    return [sum(min(rank,k)*count for rank,count in enumerate(delta,1)) for k in range(1,9)]

def sign(delta):
    witness=hinges(delta)
    need(min(witness)>=0,'unproved concave-power sign: '+str(delta))
    need(bool(any(witness))==bool(any(delta)),'invertible hinge transform')
    return 'strict_loss' if any(delta) else 'zero'

def prepare(primary,native):
    word=json.loads(gzip.decompress((ROOT/'research/g20-conjugation-admission/WORD.json.gz').read_bytes()))
    paths=json.loads((ROOT/'research/g20-conjugation-admission/PATHS.json').read_bytes())
    raw_frames=gzip.decompress((ROOT/'research/bit-g20-contact-expansion-bound/FRAMES.json.gz').read_bytes())
    need(sha256(raw_frames).hexdigest()==native.FRAME_SHA,'decompressed current catalogue')
    edges,dims=native.native_graph(json.loads(raw_frames)['frames'])
    need(len(edges)==52624 and len(dims)==645,'complete native geometry')
    for key,path in paths.items():
        need(len(path)==1,'source singleton route')
        a,b,r=path[0]
        need(key==f'{a}:{b}' and edges[a,b]==r,'source native route inclusion')
    distances=native.metric(edges,dims)
    old=json.loads(gzip.decompress((ROOT/PREFIX/'NATIVE-ONE-STEP.json.gz').read_bytes()))
    need(native.metric_digest(distances)==old['graph']['metric_sha256'],'independent metric binding')
    records=[tuple(e) for e in word['records'] if e[0] not in ('Q','ZERO_Q')]
    need(len(records)==11930 and len(word['start'])==685,'source word dimensions')
    owned=set(word['owned'])
    endpoint=[0 if i in owned else (1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(685)]
    need(primary.scalar_rows(records,685,owned)==endpoint,'source exact endpoint')
    base,_,missing=native.invoice(records,word['start'],word['final'],owned,distances,edges)
    need(dict(base)=={1:1281,2:1338,3:58,4:57,5:102,6:10} and not missing,'source full native invoice')
    return word,records,owned,endpoint,edges,distances,base,old

def census(primary,native,trace,quiet=False,part=0,parts=1):
    domain=module('independent_bitmask_domain',PACKAGE/'domain.py')
    word,records,owned,endpoint,edges,distances,base,old=prepare(primary,native)
    original=trace.Trace(records,word['start'],word['final'],owned,distances)
    need(original.base==[base[i] for i in range(9)],'original per-role invoice')
    firsts=list(primary.candidates(records))
    need(firsts==list(domain.candidates(records)),'independent complete first domain')
    need(len(firsts)==len(old['outcomes'])==2270,'complete first interval domain')
    branches=[];shapes=Counter();counts=Counter();first_counts=Counter();proofs={};exceptions=[];started=time.monotonic()
    for first_id,(first,previous) in enumerate(zip(firsts,old['outcomes'],strict=True)):
        need(descriptor(first)==[previous['first'],previous['last'],*previous['gate'],previous['contacts']], 'independent first interval')
        delta1=original.delta(first)
        need([[r,v] for r,v in enumerate(delta1) if v]==previous['delta'],'independent first invoice')
        first_counts[sign(delta1[1:])]+=1
        if not any(delta1):continue
        if first_id%parts!=part:continue
        changed=primary.rewrite(records,first)
        local=trace.Trace(changed,word['start'],word['final'],owned,distances)
        need(local.endpoint==endpoint,'all 685 first-output columns')
        need(local.base==[base[r]+delta1[r] for r in range(9)],'whole first invoice')
        zero_sources=sum(e[0]=='ADD' and not values[1] for e,values in zip(changed,local.values,strict=True))
        need(zero_sources==0,'literal first word equals emitted scalar projection')
        candidates=list(primary.candidates(changed))
        need(candidates==list(domain.candidates(changed)),'independent complete second domain')
        digest=sha256();branch_counts=Counter()
        for second in candidates:
            incremental=local.delta(second)
            delta=tuple(incremental[r]+delta1[r] for r in range(1,9))
            if delta not in proofs:
                q=hinges(delta)
                proofs[delta]=('requires_nonedge_floor' if min(q)<0 else sign(delta),q)
            verdict=proofs[delta][0]
            if verdict in ('requires_nonedge_floor','zero'):
                final=primary.rewrite(changed,second)
                bill,_,nonedges=native.invoice(final,word['start'],word['final'],owned,distances,edges)
                need([bill[r]-base[r] for r in range(1,9)]==list(delta),'independent exceptional full invoice')
                need(primary.scalar_rows(final,685,owned)==endpoint,'all 685 exceptional endpoint columns')
                completed=trace.Trace(final,word['start'],word['final'],owned,distances)
                multiplicities=Counter()
                for role,requests in enumerate(completed.requests):
                    frame=word['start'][role]
                    for _,_,target,paid in requests:
                        if paid and frame!=target and (frame,target) not in edges:
                            multiplicities[frame,target,distances[frame][target]]+=1
                        frame=target
                need({(a,b) for a,b,r in multiplicities}==nonedges,'independent nonedge demand set')
                strengthened=list(delta)
                for (a,b,r),number in multiplicities.items():
                    need(r>=2 and (a,b) not in edges,'nonedge requires at least two positive-rank edges')
                    strengthened[0]+=number;strengthened[r-2]+=number;strengthened[r-1]-=number
                verdict=sign(strengthened)
                need(verdict!='zero' or not nonedges,'zero native attainer')
                exceptions.append({'first_id':first_id,'first':descriptor(first),'second':descriptor(second),
                    'raw_delta':list(delta),'nonedge_demands':[[a,b,r,n] for (a,b,r),n in sorted(multiplicities.items())],
                    'strengthened_delta':strengthened,'hinges':hinges(strengthened),'sign':verdict,
                    'word_sha256':sha256(json.dumps(final,separators=(',',':')).encode()).hexdigest()})
            shapes[delta]+=1;branch_counts[verdict]+=1;branch_counts['candidates']+=1
            branch_counts['zero_contact']+=not second[4]
            digest.update(json.dumps([descriptor(second),delta],separators=(',',':')).encode()+b'\n')
        counts.update(branch_counts)
        branches.append({'first_id':first_id,'first':descriptor(first),'count':len(candidates),'counts':dict(sorted(branch_counts.items())),
                         'zero_sources':zero_sources,'domain_sha256':digest.hexdigest()})
        if not quiet and len(branches)%200==0:
            print(json.dumps({'branches':len(branches),'pairs':counts['candidates'],'seconds':round(time.monotonic()-started,1)}),flush=True)
    need(first_counts=={'strict_loss':2248,'zero':22},'complete costly-first domain')
    expected_branches=sum(bool(row['delta']) and i%parts==part for i,row in enumerate(old['outcomes']))
    need(len(branches)==expected_branches and sum(shapes.values())==counts['candidates'],'complete second domain accounting')
    return {'schema':'g20-costly-first-all-native-two-step/v1','base_paid':dict(sorted(base.items())),
            'first_counts':dict(sorted(first_counts.items())),'counts':dict(sorted(counts.items())),
            'graph':old['graph'],'branches':branches,'exceptions':exceptions,
            'shapes':[{'delta':list(d),'count':n,'hinges':proofs[d][1],'sign':proofs[d][0]} for d,n in sorted(shapes.items())]}

def aggregate():
    pieces=[json.loads(gzip.decompress((PACKAGE/f'CERTIFICATE-{i}.json.gz').read_bytes())) for i in range(4)]
    whole=json.loads(gzip.decompress((PACKAGE/'CERTIFICATE.json.gz').read_bytes()))
    merged=dict(pieces[0]);counts=Counter();shapes=Counter();proofs={};branches=[];exceptions=[]
    for residue,piece in enumerate(pieces):
        for key in ('schema','base_paid','first_counts','graph','controls'):
            need(piece[key]==whole[key],'shard common field '+key)
        need(all(row['first_id']%4==residue for row in piece['branches']),'exact residue shard')
        counts.update(piece['counts']);branches.extend(piece['branches']);exceptions.extend(piece['exceptions'])
        for row in piece['shapes']:
            delta=tuple(row['delta']);shapes[delta]+=row['count']
            proof=(row['hinges'],row['sign'])
            if delta in proofs:need(proofs[delta]==proof,'consistent shard proof')
            proofs[delta]=proof
    need(len({row['first_id'] for row in branches})==len(branches)==2248,'disjoint complete costly first partition')
    merged['counts']=dict(sorted(counts.items()));merged['branches']=sorted(branches,key=lambda row:row['first_id'])
    merged['exceptions']=sorted(exceptions,key=lambda row:(row['first_id'],row['second'][2],row['second'][3],row['second'][0],row['second'][1]))
    merged['shapes']=[{'delta':list(d),'count':n,'hinges':proofs[d][0],'sign':proofs[d][1]} for d,n in sorted(shapes.items())]
    need(canonical(merged)==canonical(whole),'four shard receipts reconstruct complete author census')
    print('PASS_G20_COSTLY_FIRST_SHARD_AGGREGATE')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--controls-only',action='store_true')
    parser.add_argument('--quiet',action='store_true')
    parser.add_argument('--part',type=int,choices=range(4))
    parser.add_argument('--aggregate-only',action='store_true')
    args=parser.parse_args();authenticate()
    if args.aggregate_only:
        aggregate();return
    primary=module('pinned_indexed_scalar',ROOT/PREFIX/'verify.py')
    native=module('pinned_native_metric',ROOT/PREFIX/'native_floor.py')
    trace=module('local_role_trace',PACKAGE/'trace.py')
    controls=module('independent_chronological_controls',PACKAGE/'controls.py')
    checked=controls.run(primary,trace)
    # Strict concavity and counter-sign controls are not numerical samples.
    need(sign([2,-1,0,0,0,0,0,0])=='strict_loss','split invoice control')
    need(sign([0]*8)=='zero','zero invoice control')
    for bad in ([-1,0,0,0,0,0,0,0],[1,-2,1,0,0,0,0,0]):
        try:sign(bad)
        except ValueError:pass
        else:raise ValueError('profitable sign mutant accepted')
    if args.controls_only:
        print(json.dumps(checked,sort_keys=True));print('PASS_G20_COSTLY_FIRST_CONTROLS');return
    result=census(primary,native,trace,args.quiet,0 if args.part is None else args.part,1 if args.part is None else 4)
    result['controls']=checked
    payload=canonical(result)
    if args.output:
        need(not args.output.resolve().is_relative_to(ROOT),'write receipt outside checkout')
        args.output.write_bytes(payload)
    else:
        name='CERTIFICATE.json.gz' if args.part is None else f'CERTIFICATE-{args.part}.json.gz'
        expected=gzip.decompress((PACKAGE/name).read_bytes())
        need(payload==expected,'complete costly-first receipt mismatch')
    print(json.dumps({'counts':result['counts'],'shapes':len(result['shapes']),'sha256':sha256(payload).hexdigest()},sort_keys=True))
    print('PASS_G20_COSTLY_FIRST_COMPENSATION')

if __name__=='__main__':main()
