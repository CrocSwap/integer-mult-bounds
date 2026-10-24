#!/usr/bin/env python3
"""Standalone local commutation proof for the 98-event scalar rewrite.

Apache-2.0. The trace generator adapts Cinna Davis's scalar-trace-compression
combine rule. The separate verifier scans each crossed surviving instruction;
it does not trust the generator's dependency bookkeeping. Substantial OpenAI
Codex assistance. No full multiplication-theorem or new-kappa claim.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import gzip
import json
from pathlib import Path


def need(value,message):
    if not value: raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def read(path):
    raw=Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def roles(event):
    if event[0]=='scalar':
        return {tuple(x) for x in event[1][1:] if isinstance(x,list)}
    if event[0]=='warp': return {tuple(event[1])}
    return set()


def live_add(event):
    return (event[0]=='scalar' and event[1][0]=='add'
            and all(r[0]=='L' for r in event[1][1:3]))


def scalar_coefficient(event):
    return Fraction(*event[1][3:5])


def summed(left,right):
    value=scalar_coefficient(left)+scalar_coefficient(right)
    if not value:return None
    result=deepcopy(left)
    result[1][3:5]=[value.numerator,value.denominator]
    return result


def trace_generate(program):
    """Credited combine rule; stable original ordinals are only trace labels."""
    out=[];ordinals=[];previous={};writes={};reads={};barriers={};trace=[]
    phase=-1
    for ordinal,event in enumerate(e for e in program if e[0]!='climb'):
        index=len(out)
        if live_add(event):
            a,b=map(tuple,event[1][1:3]); prior=previous.get((a,b),-1)
            barrier=max(phase,writes.get(b,-1),reads.get(a,-1),
                        barriers.get(a,-1),barriers.get(b,-1))
            if prior>barrier:
                trace.append([ordinals[prior],ordinal])
                out[prior]=summed(out[prior],event)
                if out[prior] is None:previous.pop((a,b))
                continue
            previous[a,b]=index
        if event[0]=='scalar' and event[1][0]=='add':
            a,b=map(tuple,event[1][1:3]);writes[a]=index;reads[b]=index
        else:
            for role in roles(event):barriers[role]=index
        if event[0]=='phase':phase=index
        out.append(deepcopy(event));ordinals.append(ordinal)
    return trace


def commute(add,event):
    """Exact elementary-matrix criterion, with conservative other barriers.

    An ADD i<-j commutes with k<-l iff i!=l and j!=k. All other
    operations crossing its two live roles are rejected. Center events affect
    owned C only. Adapters are inert native markers in both retained engines.
    Phase markers are conservative barriers, matching the credited rewrite.
    """
    a,b=map(tuple,add[1][1:3])
    if event[0]=='phase':return False
    if event[0]=='scalar' and event[1][0]=='add':
        x,y=map(tuple,event[1][1:3])
        return a!=y and b!=x
    if event[0] in ('scalar','warp'):
        return not ({a,b}&roles(event))
    need(event[0] in ('center','adapter'),'Unknown crossed event')
    return True


def trace_verify(program,trace):
    raw=[deepcopy(e) for e in program if e[0]!='climb']
    prior_right=-1;crossed=cancelled=0
    for left,right in trace:
        need(type(left) is int and type(right) is int and 0<=left<right<len(raw),
             'Bad trace ordinals')
        need(right>prior_right,'Trace must follow chronological incoming events')
        prior_right=right
        a,b=raw[left],raw[right]
        need(a is not None and b is not None and live_add(a) and live_add(b),
             'Trace endpoints are surviving live ADDs')
        need(a[1][1:3]==b[1][1:3],'Different elementary matrices')
        need(a[1][1]!=a[1][2],'Self-ADD is not a nilpotent elementary generator')
        for event in raw[left+1:right]:
            if event is not None:
                need(commute(b,event),'Noncommuting crossed instruction')
                crossed+=1
        raw[left]=summed(a,b);raw[right]=None
        cancelled+=raw[left] is None
    return [e for e in raw if e is not None],{'merges':len(trace),
      'cancelled_pairs':cancelled,'crossed_instruction_checks':crossed}


def span(basis):
    result={0}
    for vector in basis:result|={x^vector for x in tuple(result)}
    need(len(result)==1<<len(basis),'Dependent source frame basis')
    return result


def reconstruct(c,raw):
    spaces=list(map(span,c['frames']));current=c['start'][:];out=[]
    def move(role,target):
        old=current[role]
        if old==target:return
        need(spaces[old]<spaces[target],'Non-monotone reconstructed transport')
        out.append(['climb','trace',role,old,target,
                    len(c['frames'][target])-len(c['frames'][old])])
        current[role]=target
    for event in raw:
        if event[0]=='scalar':
            for typ,role in sorted(roles(event)):
                if typ=='L':move(role,event[2])
        elif event[0]=='warp':
            move(event[1][1],event[3]);current[event[1][1]]=event[4]
        out.append(deepcopy(event))
    for role,target in enumerate(c['final']):move(role,target)
    return out


def paid(program):
    return Counter(e[5] if e[0]=='climb' else e[4]
                   for e in program if e[0] in ('climb','center'))


def verify(source,candidate,traces,source_digest):
    need(digest(source)==source_digest,'Source payload binding mismatch')
    need(source['canonical']==candidate['canonical'],'Changed canonical source')
    need(set(source['programs'])==set(candidate['programs'])==set(traces)
         =={'forward','backward'},'Both orientations required')
    result={}
    for direction,program in source['programs'].items():
        raw,receipt=trace_verify(program,traces[direction])
        reconstructed=reconstruct(source['canonical'],raw)
        new=candidate['programs'][direction]
        need(reconstructed==new,'Candidate differs from verified rewrite and reconstruction')
        need(paid(program)==paid(new),'Paid profile changed')
        before={(e[3],e[4]) for e in program if e[0]=='climb'}
        after={(e[3],e[4]) for e in new if e[0]=='climb'}
        need(after<=before,'New physical transport requires a new recipe')
        for kind in ('warp','center','adapter','phase'):
            need([e for e in program if e[0]==kind]==[e for e in new if e[0]==kind],
                 'Changed non-scalar source event: '+kind)
        receipt.update(removed_scalar_events=sum(e[0]=='scalar' for e in program)
                       -sum(e[0]=='scalar' for e in new),paid_profile=dict(paid(new)),
                       new_physical_pairs=0,program_sha256=digest(new))
        result[direction]=receipt
    return result


def controls(source,candidate,traces,source_digest):
    def rejected(action):
        try:action()
        except (ValueError,AssertionError):return True
        raise ValueError('Mutation control was accepted')
    bad=deepcopy(candidate)
    next(e for e in bad['programs']['forward'] if live_add(e))[1][3]*=-1
    coefficient=rejected(lambda:verify(source,bad,traces,source_digest))
    bad=deepcopy(candidate)
    next(e for e in bad['programs']['forward'] if e[0]=='warp')[2]*=-1
    non_scalar=rejected(lambda:verify(source,bad,traces,source_digest))
    bad_source=deepcopy(source);bad_source['canonical']['v']+=1
    source_binding=rejected(lambda:verify(bad_source,candidate,traces,source_digest))
    def add(dst,src,n):return ['scalar',['add',['L',dst],['L',src],n,1],0]
    bad_word=[add(0,1,1),add(1,2,1),add(0,1,-1)]
    source_write=rejected(lambda:trace_verify(bad_word,[[0,2]]))
    bad_word=[add(0,1,1),add(2,0,1),add(0,1,-1)]
    target_read=rejected(lambda:trace_verify(bad_word,[[0,2]]))
    return dict(wrong_coefficient_rejected=coefficient,changed_warp_rejected=non_scalar,
      changed_source_rejected=source_binding,source_write_barrier_rejected=source_write,
      target_read_barrier_rejected=target_read)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--trace',type=Path,required=True)
    parser.add_argument('--source-sha256',required=True,
                        help='Pinned SHA256 of canonical JSON for the complete source payload')
    parser.add_argument('--write-trace',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();source=read(args.source);candidate=read(args.candidate)
    if args.write_trace:
        need(digest(source)==args.source_sha256,'Source payload binding mismatch')
        traces={d:trace_generate(p) for d,p in source['programs'].items()}
        args.trace.write_text(json.dumps(traces,indent=2)+'\n',encoding='utf-8')
    traces=read(args.trace)
    report={'status':'PASS_LOCAL_COMMUTATION_PROOF','new_kappa':None,
      'source_canonical_json_sha256':digest(source),'candidate_canonical_json_sha256':digest(candidate),
      'trace_canonical_json_sha256':digest(traces),
      'directions':verify(source,candidate,traces,args.source_sha256),
      'controls':controls(source,candidate,traces,args.source_sha256),
      'scope':'Exact local rewrite equivalence and paid-path preservation; retained source semantics assumed. No cold theorem replay.'}
    if args.output:args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,sort_keys=True))


if __name__=='__main__':main()
