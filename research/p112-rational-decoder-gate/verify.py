#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact changed-mask certificate. Standard library; no predecessor code imports."""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import io
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
OLD = 'research/tri-plane-port-p112-seeddb093026/CANDIDATE.json'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
MEMBER_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'

def need(ok, message):
    if not ok: raise ValueError(message)

def strict_json(raw):
    def unique(items):
        result={}
        for key,value in items:
            need(key not in result,'duplicate JSON key: '+key)
            result[key]=value
        return result
    def bad_constant(value):
        raise ValueError('nonfinite JSON constant: '+value)
    return json.loads(raw,object_pairs_hook=unique,parse_constant=bad_constant)

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)

def load():
    pins = strict_json((HERE/'SOURCES.json').read_text())
    pin = {x['path']:x for x in pins['files'] if x['usage']=='input'}
    raw = {}
    for path in (ARCHIVE, OLD):
        data = (ROOT/path).read_bytes()
        need(hashlib.sha256(data).hexdigest()==pin[path]['sha256'], 'source sha256 '+path)
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==pin[path]['git_blob'], 'source blob '+path)
        raw[path]=data
    with tarfile.open(fileobj=io.BytesIO(raw[ARCHIVE]),mode='r:gz') as arc:
        payload=arc.extractfile(MEMBER).read()
    need(hashlib.sha256(payload).hexdigest()==MEMBER_SHA,'phase payload')
    rows=sorted(json.loads(payload)['recipes'],key=lambda x:x['port'])
    need([r['port'] for r in rows]==list(range(112)),'port order')
    q=[r['q'] for r in rows]
    need(len(set(q))==112 and all(0<x<512 for x in q),'labels')
    return q,json.loads(raw[OLD])['groups']

def dot(a,b): return (a&b).bit_count()&1

def rank(matrix):
    """Explicit binary row arrays, low-to-high elimination."""
    a=[row[:] for row in matrix]
    if not a:return 0
    n=0
    for c in range(len(a[0])):
        p=next((r for r in range(n,len(a)) if a[r][c]),None)
        if p is None:continue
        a[n],a[p]=a[p],a[n]
        for r in range(n+1,len(a)):
            if a[r][c]:a[r]=[x^y for x,y in zip(a[r],a[n])]
        n+=1
        if n==len(a):break
    return n

def rho(a,b):return rank([[dot(x,y) for y in b] for x in a])

def geometry(q,groups):
    need(len(groups)==38 and len(groups[0])==1 and all(len(g)==3 for g in groups[1:]),'group dimensions')
    need(sorted(p for g in groups for p in g)==list(range(112)),'partition')
    spaces=[[q[p] for p in g] for g in groups]
    for basis in spaces:
        need(all(dot(x,y)==int(i==j) for i,x in enumerate(basis) for j,y in enumerate(basis)),'orthonormal basis')
    owner={p:i for i,g in enumerate(groups) for p in g}
    table=[[rho(a,b) for b in spaces] for a in spaces]
    return spaces,owner,table

def clique(ids,groups,table):
    need(len(set(ids))==len(ids) and all(0<=i<38 and len(groups[i])==3 for i in ids),'clique groups')
    need(all(table[i][j] for i in ids for j in ids),'orthogonal pair in clique')
    return [p for i in ids for p in groups[i]]

def fit(supports,scales):
    a=[[F(0) for _ in range(112)] for _ in range(112)]
    for support in supports:
        for i in support:
            for j in support:a[i][j]+=scales[i]/scales[j]
    return a

def check(a,owner,table):
    need(all(a[i][i]==1 for i in range(112)),'scalar diagonal')
    need(all(a[i][j]==0 for i in range(112) for j in range(112) if i!=j and table[owner[i]][owner[j]]),'forbidden scalar entry')

def charge(supports,spaces,owner):
    result=Counter()
    for support in supports:
        vectors=[q for g in sorted({owner[p] for p in support}) for q in spaces[g]]
        result[rho(vectors,vectors)]+=1
    return dict(sorted(result.items()))

def rejects(fn,label):
    try:fn()
    except (ValueError,IndexError):return label
    raise ValueError('control failed: '+label)

def compute():
    q,old_groups=load()
    raw=(HERE/'CANDIDATE.json').read_bytes(); c=strict_json(raw)
    need(c['source_payload_sha256']==MEMBER_SHA,'candidate source binding')
    groups=c['groups']; spaces,owner,table=geometry(q,groups)
    edges=[[i,j] for i in range(38) for j in range(i+1,38) if not table[i][j]]
    need(edges==c['orthogonal_group_pairs'],'complete free-group table')
    free=sum(2*len(groups[i])*len(groups[j]) for i,j in edges)
    need(free==420,'free pair count')
    ports=clique(c['clique_groups'],groups,table); supports=c['factor_supports']
    need(all(s for s in supports) and sorted(p for s in supports for p in s)==list(range(112)),'disjoint nonempty factors partition ports')
    need(len(ports)==len(supports)==c['claimed_minimum_scalar_rank']==57,'matching rank certificates')
    unit=[F(1)]*112; scales=list(map(F,c['rational_test_scalings']))
    need(len(scales)==112 and all(scales),'rational scales')
    a=fit(supports,unit); b=fit(supports,scales)
    check(a,owner,table);check(b,owner,table)
    need(any(x.denominator==2 for row in b for x in row),'fractional positive control')
    need(all(a[i][j]==int(i==j) for i in ports for j in ports),'I57 minor')
    profile=charge(supports,spaces,owner); mass=sum(r*n for r,n in profile.items())
    need({str(r):n for r,n in profile.items()}==c['claimed_copy_profile'],'profile')
    need(mass==c['claimed_copy_mass']==334,'full port-space charge')
    unpaid=sum(len(groups[owner[p]]) for p in range(112)); allowance=F(8*unpaid,9)
    moment=F(73*896-8*unpaid+9*mass,73*896)
    need(unpaid==334 and allowance==F(2672,9) and moment==F(32871,32704)>1,'coverage screen')
    # Subtract only free off-diagonal entries: exact final scalar identity.
    corrected=[[b[i][j] if i==j or table[owner[i]][owner[j]] else F(0) for j in range(112)] for i in range(112)]
    need(all(corrected[i][j]==int(i==j) for i in range(112) for j in range(112)),'corrected scalar identity')
    old_spaces,old_owner,old_table=geometry(q,old_groups)
    old_ports=clique([g for g in range(1,38) if g not in (12,13,19,25)],old_groups,old_table)
    old_supports=[[i,j] for x,y in ((6,13),(7,12),(9,19),(22,25)) for i,j in zip(old_groups[x],old_groups[y])]
    old_supports.append([old_groups[0][0],old_groups[1][0]])
    used={i for s in old_supports for i in s};old_supports.extend([[i] for i in range(112) if i not in used])
    need(len(old_ports)==len(old_supports)==99,'old rank certificates')
    check(fit(old_supports,unit),old_owner,old_table)
    old_profile=charge(old_supports,old_spaces,old_owner)
    need(sum(r*n for r,n in old_profile.items())==334,'old copy mass')
    controls=[]
    wrong=[g[:] for g in groups];wrong[1][0]=wrong[2][0]
    controls.append(rejects(lambda:geometry(q,wrong),'duplicate/missing port'))
    controls.append(rejects(lambda:clique(c['clique_groups']+[2],groups,table),'orthogonal pair in clique'))
    wrong=[row[:] for row in b];wrong[ports[0]][ports[1]]=F(1,2)
    controls.append(rejects(lambda:check(wrong,owner,table),'forbidden rational coefficient'))
    wrong_diagonal=[row[:] for row in b];wrong_diagonal[0][0]=2
    controls.append(rejects(lambda:check(wrong_diagonal,owner,table),'wrong diagonal'))
    controls.append(rejects(lambda:check(fit(supports[:-1],unit),owner,table),'missing factor'))
    binary=[[F(dot(q[i],q[j])) for j in range(112)] for i in range(112)]
    controls.append(rejects(lambda:check(binary,owner,table),'binary pairing as scalar endpoint'))
    line=next(s for s in supports if groups[0][0] in s)
    need(charge([line],spaces,owner)=={7:1},'residual tariff must be seven')
    need(table[1][2]==0 and charge([supports[0]],spaces,owner)=={6:1},'free cross pairing is not copy charge')
    controls+=['residual undercharge rejected','cross-rank-zero undercharge rejected']
    return dict(candidate_sha256=hashlib.sha256(raw).hexdigest(),payload_sha256=MEMBER_SHA,
                ports=112,free_ordered_pairs=free,scalar_minrank=57,clique_ports=ports,
                copy_profile={str(r):n for r,n in profile.items()},copy_mass=mass,
                rational_endpoint_entries=12544,zero_saving_allowance=str(allowance),
                centre_excess=str(F(mass)-allowance),favorable_M0=str(moment),
                historical_scalar_minrank=99,historical_copy_profile={str(r):n for r,n in old_profile.items()},
                controls=controls,scope='finite scalar fit; no native word, supplier or exponent improvement')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',type=Path);args=parser.parse_args()
    result=compute()
    if args.write:
        with args.write.open('x',encoding='utf-8') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    else:need(canonical(result)==canonical(strict_json((HERE/'RESULT.json').read_text())),'receipt drift')
    print('PASS_P112_TRIPLANE_FIT minrank=57 previous=99 free_pairs=420 profile=3H3+53H6+H7 mass=334 M0=32871/32704 controls=8 no_kappa')

if __name__=='__main__':main()
