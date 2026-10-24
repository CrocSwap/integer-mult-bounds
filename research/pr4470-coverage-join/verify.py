#!/usr/bin/env python3
"""Event-derived coverage join for PR4470. Apache-2.0; OpenAI assistance.

The inherited constructor emits candidate data only. Neither its proof engines
nor the predecessor physical-matrix checker is imported by this verifier.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PHYSICAL='research/joint-helper-lattice/NATIVE.json.gz'
COVERAGE_DIGEST='5f3923deb45470a9e9f3cf958e3876ea9e81bb2837f32b835196572993ed5d1f'


def need(ok,why):
    if not ok:raise ValueError(why)


def authenticate():
    for row in json.loads((HERE/'SOURCES.json').read_bytes())['files']:
        if row['usage']!='input':continue
        path=ROOT/row['path'];need(path.is_file() and not path.is_symlink(),'Missing/aliased source')
        data=path.read_bytes()
        need(hashlib.sha256(data).hexdigest()==row['sha256'],'Changed source bytes')
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],'Changed source blob')


def emit():
    authenticate()
    with tempfile.TemporaryDirectory(prefix='coverage-private-cache-') as cache:
        code="import json,sys;sys.path.insert(0,sys.argv[1]);import native_joint;c,p,b,o,ch=native_joint.construct();print(json.dumps({'canonical':c,'programs':p,'baseline':b,'before':o}))"
        result=subprocess.run([sys.executable,'-I','-B','-X','pycache_prefix='+cache,'-c',code,str(ROOT/'research/joint-helper-lattice')],check=True,capture_output=True,timeout=60)
    return json.loads(result.stdout)


@lru_cache(None)
def space(basis):
    pivots={}
    for x in basis:
        need(type(x) is int and 0<x<512,'Nine-axis vector')
        for k in sorted(pivots,reverse=True):
            if (x>>k)&1:x^=pivots[k]
        need(x!=0,'Dependent frame basis')
        k=x.bit_length()-1
        for j in pivots:
            if (pivots[j]>>k)&1:pivots[j]^=x
        pivots[k]=x
    return tuple(pivots[k] for k in sorted(pivots,reverse=True))


def subset(a,b):
    pivots={x.bit_length()-1:x for x in b}
    for x in a:
        for k in sorted(pivots,reverse=True):
            if (x>>k)&1:x^=pivots[k]
        if x:return False
    return True


def pair(c,a,b):
    A=tuple(c['frames'][a]);B=tuple(c['frames'][b])
    aa,bb=space(A),space(B)
    need(aa!=bb and subset(aa,bb),'Positive nested transport')
    # Preserve embeddings too: changing a basis does not silently preserve phase.
    return (aa,bb,A,B)


def operands(g):
    return g[1:3] if g[0] in ('add','copy') else g[1:2]


def trace(program,c):
    need(len(c['start'])==len(c['final'])==632,'Persistent ownership count')
    for b in c['frames']:space(tuple(b))
    state={('L',r):f for r,f in enumerate(c['start'])}
    edges=Counter();bill=Counter();counts=Counter();zero=False
    for e in program:
        tag=e[0];counts[tag]+=1
        if tag=='climb':
            _,_,role,a,b,r=e
            need(type(role) is int and 0<=role<632,'Unique persistent role domain')
            need(state['L',role]==a,'Chronological climb entrance')
            key=pair(c,a,b)
            need(r==len(key[1])-len(key[0]),'Charged transport rank')
            state['L',role]=b;edges[key]+=1;bill[r]+=1
        elif tag=='scalar':
            g,f=e[1:];dst=tuple(g[1])
            if g[0]=='clear':
                need(dst==('C',0),'Only owned centre may be cleared');state[dst]=f;zero=True
            else:
                need(g[0] in ('add','copy','scale'),'Scalar alphabet')
                for role in operands(g):need(state.get(tuple(role))==f,'Actual common frame')
                if g[0]=='copy':need(dst==('C',0),'Copy destination must be owned')
                else:
                    q=Fraction(*g[-2:]);need(q!=0 and q.denominator&(q.denominator-1)==0,'Legal dyadic scalar')
                if dst==('C',0):zero=False
        elif tag=='warp':
            role=tuple(e[1]);need(role[0]=='L' and state[role]==e[3],'Retained warp entrance')
            state[role]=e[4]
        elif tag=='center':
            _,r,a,b,k=e
            need(r==0 and state.get(('C',0))==a,'Owned centre entrance')
            aa,bb=space(tuple(c['frames'][a])),space(tuple(c['frames'][b]))
            need((subset(aa,bb) or subset(bb,aa)) and abs(len(aa)-len(bb))==k==8,'Owned centre charge')
            state['C',0]=b;bill[8]+=1
        else:need(tag in ('phase','adapter','residual_adapter'),'Unknown event')
    need(all(state['L',r]==f for r,f in enumerate(c['final'])),'Persistent endpoints')
    need(zero and counts['center']==8,'Owned restoration and all centre charges')
    return edges,bill,counts


def inventory(records,c):
    keys=set();raw=set();digest=hashlib.sha256()
    for row in records:
        a,b,r=row['old'],row['new'],row['rank']
        need((a,b) not in raw,'Duplicate physical record');raw.add((a,b))
        key=pair(c,a,b)
        need(r==len(key[1])-len(key[0]),'Physical record rank')
        need(set(row['recipes'])=={'forward','backward'},'Both orientations required')
        for d in ('forward','backward'):
            need(row['recipes'][d]['rank']==r,'Recipe rank mismatch')
            keys.add((key,d))
            digest.update(json.dumps([a,b,r,d],separators=(',',':')).encode())
    return keys,digest.hexdigest()


def check_cover(required,available):
    need(required==available,'Missing or extra changed/helper coverage')


def self_tests():
    need(space((1,2))==space((3,2)),'Equivalent subspace canonicalisation')
    need(subset(space((1,)),space((1,2))) and not subset(space((4,)),space((1,2))),'Containment')
    c={'frames':[[],[1],[1,2],[3,2]]}
    need(pair(c,0,2)!=pair(c,0,3),'Different basis embedding must not silently collapse')
    good=[{'old':0,'new':1,'rank':1,'recipes':{'forward':{'rank':1},'backward':{'rank':1}}}]
    available,_=inventory(good,c);check_cover(available,available)
    rejected=0
    for bad in (good+good,[dict(good[0],rank=2)],[dict(good[0],recipes={'forward':{'rank':1}})]):
        try:inventory(bad,c)
        except ValueError:rejected+=1
        else:raise ValueError('Malformed recipe inventory accepted')
    for missing in (set(),{next(iter(available))}):
        try:check_cover(available,missing)
        except ValueError:rejected+=1
        else:raise ValueError('Omitted coverage accepted')
    for b in ((1,1),(0,)):
        try:space(b)
        except ValueError:rejected+=1
        else:raise ValueError('Invalid basis accepted')
    return dict(positive_checks=4,rejected_controls=rejected)


def run():
    controls=self_tests();data=emit();c=data['canonical'];before=data['baseline']
    receipt=json.loads(gzip.decompress((ROOT/PHYSICAL).read_bytes()))
    records=receipt['new_physical_edges_and_boundaries']
    need(len(records)==423,'Original source physical census')
    available,digest=inventory(records,c)
    prior_raw=(HERE/'evidence/PR14-RESULT.json').read_bytes()
    need(hashlib.sha256(prior_raw).hexdigest()=='53bdd869ebeee0980b139e422043922c87585bef90c2989969532ccb7b289a00','Prior physical receipt changed')
    prior=json.loads(prior_raw)
    need(prior['status']=='PASS_EXACT_TRANSPORT_MATRICES' and prior['source_head']=='b9a13c1673e0e9697de410de16e8bbf3207a7363','Prior evidence scope')
    need(hashlib.sha256((ROOT/PHYSICAL).read_bytes()).hexdigest()==prior['source_files']['PR4470-NATIVE.json.gz']['sha256'],'Same physical source bytes')
    need(digest==prior['coverage_index_sha256']==COVERAGE_DIGEST,'Bind exact index to the prior successful matrix audit')
    helpers={pair(c,c['start'][r],c['final'][r]) for r in range(224,632)}
    required=set();summary={}
    for d in ('forward','backward'):
        old,oldbill,oldcounts=trace(data['before'][d],before)
        new,bill,counts=trace(data['programs'][d],c)
        need(dict(bill)=={1:2237,2:388,3:494,4:147,5:36,8:8},'Complete actual paid bill')
        changed=set(new)-set(old)
        required.update((k,d) for k in changed|helpers)
        direct=sum(n for k,n in new.items() if (k,d) in available)
        inherited=sum(n for k,n in new.items() if (k,d) not in available and k in old)
        need(direct+inherited==sum(new.values()),'Unclassified chronological demand')
        summary[d]=dict(changed_distinct_transports=len(changed),all_distinct_transports=len(new),
            persistent_transports=sum(new.values()),directly_covered_occurrences=direct,
            inherited_transport_occurrences=inherited,owned_center_jobs=counts['center'],
            retained_warp_events=counts['warp'],scalar_events=counts['scalar'])
    check_cover(required,available)
    removed=set(available);removed.remove(next(iter(removed)))
    try:check_cover(required,removed)
    except ValueError:pass
    else:raise ValueError('Actual omitted orientation record accepted')
    return dict(schema='pr4470-coverage-join/v1',status='PASS_EVENT_DERIVED_COVERAGE_JOIN',
        source_head='b9a13c1673e0e9697de410de16e8bbf3207a7363',physical_records=len(records),
        canonical_basis_bound_oriented_records=len(available),independent_helper_owners=408,
        distinct_helper_boundaries=len(helpers),coverage_index_sha256=digest,
        orientations=summary,controls=controls,actual_omission_rejected=True,new_kappa=False,
        physical_matrix_evidence='Fork PR14 receipt at af86fb28f4fe039d4bb8419850af99a6fc474587 is reused, not rerun',
        not_covered=['fresh matrix replay','physical verification of inherited transports, warps and centres',
            'complete arbitrary-input native endpoint','p16 caller and outer theorem'])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=self_tests() if args.self_test else run();text=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if args.write:(HERE/'RESULT.json').write_text(text)
    elif not args.self_test and (HERE/'RESULT.json').exists():need(json.loads((HERE/'RESULT.json').read_bytes())==out,'Receipt changed')
    print(text,end='')

if __name__=='__main__':main()
