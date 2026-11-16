#!/usr/bin/env python3
"""Bind and splice exactly one #7620 word; construction is not qualification."""
import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path

GZIP_SHA='2eb2cf1d29529c68a6cb1c0639de3065a805858d3492068e76b70c5a5e80a81c'
GIT_BLOB='2b8a259e017748ab5a3b98c22b42b8d3113edfce'
CANON_SHA='6c46ad38d812ae110392f1c977cc6f02665f8860e98ef1c21cb539ff3779533d'
EDITS={
 38486: (['MOVE',902,3,595,False], ['MOVE',902,3,373,False]),
 38487: (['ADD',1532,902,'2',595], None),
 38785: (['ADD',1479,902,'-1/2',595], None),
 38786: (['ADD',1255,902,'-1',595], None),
 38787: (['ADD',1495,902,'-3/2',595], None),
 38788: (['MOVE',1091,373,618,False], None),
 38789: (['MOVE',902,595,618,False], None),
 38790: (['ADD',1091,902,'1/2',618], ['ADD',1091,902,'1/2',373]),
 38813: (['MOVE',1091,618,733,False], ['MOVE',1091,373,733,False]),
 41448: (['MOVE',902,618,913,False], ['MOVE',902,373,913,False]),
}
# Every operation incident to either role from the last relevant entry-chart
# use through the first exterior 902 observer, inclusive, is pinned.
WINDOW=(37803,41449)
INCIDENTS=[
 (37803,['ADD',1091,1097,'1/2',373]),
 (38482,['ADD',643,902,'-1/4',3]),
 (38483,['ADD',496,902,'-1/2',3]),
 (38484,['ADD',1466,902,'1/2',3]),
 (38485,['ADD',450,902,'-1/2',3]),
 (38486,['MOVE',902,3,595,False]),
 (38487,['ADD',1532,902,'2',595]),
 (38785,['ADD',1479,902,'-1/2',595]),
 (38786,['ADD',1255,902,'-1',595]),
 (38787,['ADD',1495,902,'-3/2',595]),
 (38788,['MOVE',1091,373,618,False]),
 (38789,['MOVE',902,595,618,False]),
 (38790,['ADD',1091,902,'1/2',618]),
 (38813,['MOVE',1091,618,733,False]),
 (38815,['ADD',1091,1093,'-1',733]),
 (38941,['MOVE',1091,733,238,False]),
 (38943,['ADD',1091,1087,'1',238]),
 (41448,['MOVE',902,618,913,False]),
 (41449,['ADD',985,902,'-1',913]),
]


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def write(path,obj):path.write_bytes(canonical(obj)+b'\n')


def touched(event):
    if not isinstance(event,list) or len(event)<2:raise ValueError('malformed event')
    op=event[0]
    if op in ('ADD','COPY'):
        if len(event)!=5:raise ValueError('malformed binary scalar')
        return {event[1],event[2]}
    if op in ('MOVE','SCALE','INIT','CLEAR'):return {event[1]}
    raise ValueError('unknown operation in incident window')


def lifecycle_shape(w):
    live=set();peak=0;initializations=0;clear=0;owned_moves=0
    for e in w['program']:
        op,r=e[:2]
        if op=='INIT':
            if r<w['public'] or r in live:raise ValueError('invalid owned INIT structure')
            live.add(r);initializations+=1;peak=max(peak,len(live))
        elif op=='CLEAR':
            if r not in live:raise ValueError('invalid owned CLEAR structure')
            live.remove(r);clear+=1
        elif op=='MOVE' and r>=w['public']:
            if r not in live:raise ValueError('invalid owned MOVE structure')
            owned_moves+=1
    return {'init':initializations,'clear':clear,'peak':peak,'owned_moves':owned_moves,'live_at_end':len(live)}


def splice(w):
    """Literal structural edit only; exact semantics belong to downstream gate."""
    p=w['program']
    if (w['public'],w['owned_fields'],len(p),len(w['initial']),len(w['final']))!=(1501,68,77194,1501,1501):
        raise ValueError('source shape mismatch')
    if lifecycle_shape(w)!={'init':167,'clear':167,'peak':50,'owned_moves':47,'live_at_end':0}:
        raise ValueError('source lifecycle structure mismatch')
    observed=[(i,p[i]) for i in range(WINDOW[0],WINDOW[1]+1) if touched(p[i]) & {902,1091}]
    if observed!=INCIDENTS:raise ValueError('complete incident window mismatch')
    for i,(old,_) in EDITS.items():
        if p[i]!=old:raise ValueError('edit literal mismatch at %d'%i)
    result=[];origins=[];reverse=[None]*len(p);edits=[]
    for i,e in enumerate(p):
        if i in EDITS:
            old,new=EDITS[i];edits.append({'original_index':i,'old':old,'new_or_null':new})
            if new is None:continue
            e=new
        reverse[i]=len(result);origins.append(i);result.append(e)
    if len(result)!=77188 or len(origins)!=len(result) or len(edits)!=10 or sum(x is None for x in reverse)!=6:
        raise ValueError('splice count mismatch')
    if any(origins[i]>=origins[i+1] for i in range(len(origins)-1)):
        raise ValueError('non-increasing origin ledger')
    if any(reverse[i]!=j for j,i in enumerate(origins)):
        raise ValueError('origin/reverse mismatch')
    old_counts=Counter(e[0] for e in p);new_counts=Counter(e[0] for e in result)
    if {k:new_counts[k]-old_counts[k] for k in set(old_counts)|set(new_counts) if new_counts[k]!=old_counts[k]}!={'ADD':-4,'MOVE':-2}:
        raise ValueError('opcode delta mismatch')
    candidate=dict(w);candidate['program']=result
    if lifecycle_shape(candidate)!=lifecycle_shape(w):raise ValueError('owned lifecycle structure changed')
    metadata={k:v for k,v in w.items() if k!='program'}
    if metadata!={k:v for k,v in candidate.items() if k!='program'}:raise ValueError('metadata changed')
    return candidate,origins,reverse,edits,sha(canonical(metadata))


def build(root,out):
    root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    try:
        raw=(root/'inputs/pr7620/data/word.json.gz').read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if sha(raw)!=GZIP_SHA or blob!=GIT_BLOB:raise ValueError('compressed source custody mismatch')
        source=json.loads(gzip.decompress(raw))
        if sha(canonical(source))!=CANON_SHA:raise ValueError('source canonical SHA mismatch')
        candidate,origins,reverse,edits,metadata_sha=splice(source)
        data=canonical(candidate)
        buf=io.BytesIO()
        with gzip.GzipFile(filename='',mode='wb',fileobj=buf,mtime=0) as z:z.write(data)
        compressed=buf.getvalue()
        manifest={'schema':'compose7620-edit-manifest/v1',
          'source_canonical_sha256':CANON_SHA,'source_gzip_sha256':GZIP_SHA,'source_git_blob':GIT_BLOB,
          'candidate_canonical_sha256':sha(data),'candidate_gzip_sha256':sha(compressed),
          'metadata_sha256':metadata_sha,'edits':edits,'candidate_origins':origins,'original_to_candidate':reverse,
          'incident_window':{'inclusive':list(WINDOW),'roles':[902,1091],'events':[[i,e] for i,e in INCIDENTS]},
          'shape':{'original_events':len(source['program']),'candidate_events':len(candidate['program']),
                   'public':1501,'owned_fields':68,'owned_init':167,'owned_clear':167,'owned_peak':50,'owned_moves':47},
          'opcode_delta':{'ADD':-4,'MOVE':-2}}
        (out/'candidate-word.json.gz').write_bytes(compressed)
        write(out/'edit-manifest.json',manifest)
        status={'status':'CANDIDATE_BUILT_UNQUALIFIED','candidate_canonical_sha256':manifest['candidate_canonical_sha256'],
                'candidate_gzip_sha256':manifest['candidate_gzip_sha256']}
        write(out/'status.json',status);return status
    except Exception as exc:
        write(out/'status.json',{'status':'INCOMPLETE','error_type':type(exc).__name__,'error':str(exc)})
        raise


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--out',required=True)
    args=ap.parse_args();print(json.dumps(build(args.root,args.out),sort_keys=True),flush=True)
