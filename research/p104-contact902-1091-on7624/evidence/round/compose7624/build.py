#!/usr/bin/env python3
"""Bind and splice exactly one #7624 word; construction is not qualification."""
import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path

GZIP_SHA='bfe2a4fb54dd82940ba78d8b3efd4f587e3fc9e978ccfd48561199d2c9fb4887'
GIT_BLOB='81725205c5200d0cf34f9f2debef49d75273e4af'
CANON_SHA='c14f365d254598f6a2daa349b47f815d20c649f0439cc36897b531412e19a3de'
EDITS={
 38369: (['MOVE',902,3,618,False], ['MOVE',902,3,373,False]),
 38623: (['MOVE',1091,373,618,False], None),
 40279: (['ADD',1091,902,'1/2',618], ['ADD',1091,902,'1/2',373]),
 40280: (['MOVE',1091,618,733,False], ['MOVE',1091,373,733,False]),
 41663: (['MOVE',902,618,913,False], ['MOVE',902,373,913,False]),
}
WINDOW=(37928,41664)
INCIDENTS=[
 (37928,['ADD',1091,1097,'1/2',373]),
 (38365,['ADD',643,902,'-1/4',3]),
 (38366,['ADD',496,902,'-1/2',3]),
 (38367,['ADD',1466,902,'1/2',3]),
 (38368,['ADD',450,902,'-1/2',3]),
 (38369,['MOVE',902,3,618,False]),
 (38623,['MOVE',1091,373,618,False]),
 (40279,['ADD',1091,902,'1/2',618]),
 (40280,['MOVE',1091,618,733,False]),
 (40281,['ADD',1091,1093,'-1',733]),
 (40283,['MOVE',1091,733,238,False]),
 (40285,['ADD',1091,1087,'1',238]),
 (41663,['MOVE',902,618,913,False]),
 (41664,['ADD',985,902,'-1',913]),
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


def validate_maps(origins,reverse,edits,n,deleted):
    if type(n) is not int or n<=1 or type(deleted) is not int or not 0<=deleted<n:raise ValueError('map bounds')
    if not isinstance(origins,list) or len(origins)!=n-1 or not isinstance(reverse,list) or len(reverse)!=n or not isinstance(edits,list):raise ValueError('map shape')
    if any(type(v) is not int or not 0<=v<n for v in origins):raise ValueError('origin type or bounds')
    for i,v in enumerate(reverse):
        if i==deleted:
            if v is not None:raise ValueError('deleted map entry')
        elif type(v) is not int or not 0<=v<n-1:raise ValueError('reverse type or bounds')
    if any(not isinstance(e,dict) or type(e.get('original_index')) is not int or not 0<=e['original_index']<n for e in edits):raise ValueError('edit type or bounds')
    expected=[i for i in range(n) if i!=deleted]
    if origins!=expected or any(reverse[i]!=j for j,i in enumerate(expected)):raise ValueError('map order')

def require_incidents(p,window,incidents):
    lo,hi=window
    if type(lo) is not int or type(hi) is not int or not 0<=lo<=hi<len(p):raise ValueError('window bounds')
    observed=[(i,p[i]) for i in range(lo,hi+1) if touched(p[i]) & {902,1091}]
    if observed!=incidents:raise ValueError('complete incident window mismatch')

def require_edits(p,edits):
    for i,(old,_) in edits.items():
        if type(i) is not int or not 0<=i<len(p):raise ValueError('edit type or bounds')
        if p[i]!=old:raise ValueError('edit literal mismatch at %d'%i)

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
    if (w['public'],w['owned_fields'],len(p),len(w['initial']),len(w['final']))!=(1501,68,77372,1501,1501):
        raise ValueError('source shape mismatch')
    shape=lifecycle_shape(w)
    if shape['init']!=204 or shape['clear']!=204 or shape['peak']!=50 or shape['live_at_end']!=0:
        raise ValueError('source lifecycle structure mismatch')
    require_incidents(p,WINDOW,INCIDENTS)
    require_edits(p,EDITS)
    result=[];origins=[];reverse=[None]*len(p);edits=[]
    for i,e in enumerate(p):
        if i in EDITS:
            old,new=EDITS[i];edits.append({'original_index':i,'old':old,'new_or_null':new})
            if new is None:continue
            e=new
        reverse[i]=len(result);origins.append(i);result.append(e)
    if len(result)!=77371 or len(origins)!=len(result) or len(edits)!=5 or sum(x is None for x in reverse)!=1:
        raise ValueError('splice count mismatch')
    if any(origins[i]>=origins[i+1] for i in range(len(origins)-1)):
        raise ValueError('non-increasing origin ledger')
    if any(reverse[i]!=j for j,i in enumerate(origins)):
        raise ValueError('origin/reverse mismatch')
    validate_maps(origins,reverse,edits,len(p),38623)
    old_counts=Counter(e[0] for e in p);new_counts=Counter(e[0] for e in result)
    if {k:new_counts[k]-old_counts[k] for k in set(old_counts)|set(new_counts) if new_counts[k]!=old_counts[k]}!={'MOVE':-1}:
        raise ValueError('opcode delta mismatch')
    # No scalar or lifecycle instruction changes, apart from the one public
    # ADD chart. MOVE is the sole deleted opcode.
    source_nonmove=[(i,e) for i,e in enumerate(p) if e[0]!='MOVE']
    candidate_nonmove=[(origins[j],e) for j,e in enumerate(result) if e[0]!='MOVE']
    if len(source_nonmove)!=len(candidate_nonmove):raise ValueError('non-MOVE stream length changed')
    for (i,a),(j,b) in zip(source_nonmove,candidate_nonmove):
        if i!=j:raise ValueError('non-MOVE stream origin changed')
        if i==40279:
            if (a,b)!=EDITS[i] or a[:4]!=b[:4]:raise ValueError('contact scalar changed')
        elif a!=b:raise ValueError('non-MOVE record changed')
    candidate=dict(w);candidate['program']=result
    if lifecycle_shape(candidate)!=lifecycle_shape(w):raise ValueError('owned lifecycle structure changed')
    metadata={k:v for k,v in w.items() if k!='program'}
    if metadata!={k:v for k,v in candidate.items() if k!='program'}:raise ValueError('metadata changed')
    return candidate,origins,reverse,edits,sha(canonical(metadata))


def build(root,out):
    root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    try:
        raw=(root/'inputs/pr7624/research/p104-w2-primal-dual-bypass/data/word.json.gz').read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if sha(raw)!=GZIP_SHA or blob!=GIT_BLOB:raise ValueError('compressed source custody mismatch')
        source=json.loads(gzip.decompress(raw))
        if sha(canonical(source))!=CANON_SHA:raise ValueError('source canonical SHA mismatch')
        candidate,origins,reverse,edits,metadata_sha=splice(source)
        data=canonical(candidate)
        buf=io.BytesIO()
        with gzip.GzipFile(filename='',mode='wb',fileobj=buf,mtime=0) as z:z.write(data)
        compressed=buf.getvalue()
        manifest={'schema':'compose7624-edit-manifest/v1',
          'source_canonical_sha256':CANON_SHA,'source_gzip_sha256':GZIP_SHA,'source_git_blob':GIT_BLOB,
          'candidate_canonical_sha256':sha(data),'candidate_gzip_sha256':sha(compressed),
          'metadata_sha256':metadata_sha,'edits':edits,'candidate_origins':origins,'original_to_candidate':reverse,
          'incident_window':{'inclusive':list(WINDOW),'roles':[902,1091],'events':[[i,e] for i,e in INCIDENTS]},
          'shape':{'original_events':len(source['program']),'candidate_events':len(candidate['program']),
                   'public':1501,'owned_fields':68,'owned_init':204,'owned_clear':204,'owned_peak':50,'owned_moves':lifecycle_shape(source)['owned_moves']},
          'opcode_delta':{'MOVE':-1}}
        (out/'candidate-word.json.gz').write_bytes(compressed)
        write(out/'edit-manifest.json',manifest)
        status={'status':'CANDIDATE_BUILT_UNQUALIFIED','candidate_canonical_sha256':manifest['candidate_canonical_sha256'],
                'candidate_gzip_sha256':manifest['candidate_gzip_sha256']}
        write(out/'status.json',status);return status
    except Exception as exc:
        write(out/'status.json',{'status':'INCOMPLETE','error_type':type(exc).__name__,'error':str(exc)})
        raise


def controls():
    rejected=[]
    def reject(name,fn):
        try:fn()
        except ValueError:rejected.append(name);return
        raise ValueError('control did not reject: '+name)
    p=[['ADD',1091,10,'1',373],['MOVE',902,3,618,False],['ADD',0,1,'1',0]]
    require_incidents(p,(0,2),[(0,p[0]),(1,p[1])]);require_edits(p,{1:(p[1],None)})
    reject('missing_incident',lambda:require_incidents(p,(0,2),[(0,p[0])]))
    reject('changed_literal',lambda:require_edits(p,{1:(['MOVE',902,3,373,False],None)}))
    reject('boolean_edit_key',lambda:require_edits(p,{True:(p[1],None)}))
    m=[{'original_index':1}];validate_maps([0,2,3],[0,None,1,2],m,4,1)
    reject('boolean_origin',lambda:validate_maps([False,2,3],[0,None,1,2],m,4,1))
    reject('negative_origin',lambda:validate_maps([-1,2,3],[0,None,1,2],m,4,1))
    reject('boolean_reverse',lambda:validate_maps([0,2,3],[False,None,1,2],m,4,1))
    reject('boolean_manifest_edit',lambda:validate_maps([0,2,3],[0,None,1,2],[{'original_index':True}],4,1))
    return {'status':'PASS_SOURCE_FREE_CONTROLS','rejected':rejected}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root');ap.add_argument('--out');ap.add_argument('--controls-only',action='store_true')
    args=ap.parse_args()
    if args.controls_only:print(json.dumps(controls(),sort_keys=True),flush=True)
    else:
        if args.root is None or args.out is None:ap.error('--root and --out are required unless --controls-only is set')
        print(json.dumps(build(args.root,args.out),sort_keys=True),flush=True)
