#!/usr/bin/env python3
"""Prepare candidate-bound CLEAR linear certificates; no physical-U admission.

This module is preparation only until the root-controlled qualification invokes
build(root, work, out). The standalone verifier and its controls are separate.
"""
import argparse
import collections
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path

SOURCE_GZ='2eb2cf1d29529c68a6cb1c0639de3065a805858d3492068e76b70c5a5e80a81c'
SOURCE_CAN='6c46ad38d812ae110392f1c977cc6f02665f8860e98ef1c21cb539ff3779533d'
OLD_CERTS='f10f8081d9ebb34e2487ad70ccdcd83aa4cd43fd8e80092af04643ce2445d24d'
CANDIDATE_GZ='4d742e0b6e915cc3c3d31d18d5d2703c1f943c695c25d7c5a24f04626c1f5235'
CANDIDATE_CAN='03da65fb97ffaf4d0e9756f3867df588b162975f6015d8458821d05b5fcb006b'
EXACT_GZ='9ae34179285657fc0830902dc7e75c9ca8a415a37fbce92e18808bdbd426d167'
EXACT_CAN='742a10aa6cb90410e5bdda9c00672b58a1f26082941a86ad5857646b49e6cfc4'
MANIFEST='58fd6a8fb76f0dad335abab6973f0ceae29a1c687c47cb2d98d6d0c64e9ed1e7'
MAX_VECTORS=86
MAX_ELIMINATION_OPS=20_000_000
MAX_STORED_TERMS=2_000_000

class Refusal(Exception): pass

def need(test,msg):
    if not test:raise Refusal(msg)
def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def load(path):
    data=Path(path).read_bytes();return json.loads(gzip.decompress(data) if data[:2]==b'\x1f\x8b' else data)
def unpack(row):return {int(k):F(v) for k,v in (row or {}).items() if F(v)}
def pack(row):return {str(k):str(v) for k,v in sorted(row.items()) if v}
def axpy(dst,src,q):
    for k,v in src.items():
        z=dst.get(k,F(0))+q*v
        if z:dst[k]=z
        else:dst.pop(k,None)
def linear(rows,coeff):
    out={}
    for r,q in coeff.items():axpy(out,rows[r],q)
    return out


def one_canonical_relation(target,rows,old_roles,live,n):
    """One exact echelon solve over old public certificate roles plus four fixed public roles.

    This is a fixed finite basis, not a changing bank or coefficient search.
    Free coefficients are zero, pivots use first contributor in sorted order.
    """
    roles=sorted(set(old_roles)|({451,1495,902,985}&live))
    need(len(roles)<=MAX_VECTORS and all(r<n and r in live for r in roles),'relation basis shape')
    basis={};ops=0;stored=0
    for role in roles:
        v=rows[role].copy();rep={role:F(1)}
        while v:
            p=min(v)
            if p not in basis:
                q=v[p];v={k:x/q for k,x in v.items()};rep={k:x/q for k,x in rep.items()}
                stored+=len(v)+len(rep);need(stored<=MAX_STORED_TERMS,'canonical relation storage bound')
                basis[p]=(v,rep);break
            row,weights=basis[p];q=-v[p];ops+=len(row)+len(weights);need(ops<=MAX_ELIMINATION_OPS,'canonical relation operation bound')
            axpy(v,row,q);axpy(rep,weights,q)
    residual=target.copy();answer={}
    while residual:
        p=min(residual)
        if p not in basis:raise Refusal('target not in canonical basis')
        row,weights=basis[p];q=residual[p];ops+=len(row)+len(weights);need(ops<=MAX_ELIMINATION_OPS,'canonical relation operation bound')
        axpy(residual,row,-q);axpy(answer,weights,q)
    need(linear(rows,answer)==target,'canonical relation internal mismatch')
    return answer,{'basis_candidates':len(roles),'pivots':len(basis),'elimination_ops':ops,'stored_terms':stored}


def build(root,work,out):
    root,work,out=Path(root),Path(work),Path(out)
    out.mkdir(parents=True,exist_ok=False);audit=[]
    try:
        sourcep=root/'inputs/pr7620/data/word.json.gz';oldp=root/'inputs/pr7620/evidence/certs.json'
        candidatep=work/'built/candidate-word.json.gz';manifestp=work/'built/edit-manifest.json'
        exactp=work/'exact/EXACT.json.gz';statusp=work/'exact/status.json'
        need(sha(sourcep.read_bytes())==SOURCE_GZ and sha(oldp.read_bytes())==OLD_CERTS,'source custody')
        need(sha(candidatep.read_bytes())==CANDIDATE_GZ and sha(manifestp.read_bytes())==MANIFEST and sha(exactp.read_bytes())==EXACT_GZ,'candidate/manifest/exact custody')
        old=load(oldp);word=load(candidatep);manifest=load(manifestp);exact=load(exactp);status=load(statusp)
        need(sha(canonical(word))==CANDIDATE_CAN and sha(canonical(exact))==EXACT_CAN,'candidate/exact canonical custody')
        need(status.get('status')=='U_CONDITIONAL_LITERAL_EXACT_ONLY' and status.get('exact_gzip_sha256')==EXACT_GZ and status.get('exact_sha256')==EXACT_CAN,'exact receipt')
        bind=exact['source'];need(bind==status['source'] and bind['original_canonical_sha256']==SOURCE_CAN and bind['original_gzip_sha256']==SOURCE_GZ and bind['candidate_canonical_sha256']==CANDIDATE_CAN and bind['candidate_gzip_sha256']==CANDIDATE_GZ and bind['manifest_sha256']==MANIFEST,'exact binding')
        need(exact['schema']=='compose7620-exact/v1' and old['summary']['sha256']==SOURCE_GZ and len(old['clears'])==167,'old certificate binding')
        origins=manifest['candidate_origins'];reverse=manifest['original_to_candidate'];program=word['program'];n=word['public'];N=n+word['owned_fields']
        need((n,N,len(program),len(origins),len(reverse))==(1501,1569,77188,77188,77194),'word shape')
        need(all(type(i) is int and 0<=i<len(reverse) and reverse[i]==j for j,i in enumerate(origins)) and all(origins[j]<origins[j+1] for j in range(len(origins)-1)),'origin map')
        oc=exact['original']['clears'];nc=exact['candidate']['clears'];need(len(oc)==len(nc)==167,'exact clear count')
        rows=[{r:F(1)} for r in range(n)]+[{} for _ in range(N-n)]
        live=set(range(n));charts=list(word['initial'])+[None]*(N-n);lifetimes=collections.Counter();current={};new_certs=[]
        for j,e in enumerate(program):
            op,r=e[:2];need(type(r) is int and 0<=r<N,'event role')
            if op=='INIT':
                need(r>=n and r not in live,'bad init');live.add(r);rows[r]={};charts[r]=e[2];lifetimes[r]+=1
                current[r]={'init_event':j,'init_chart':e[2],'moves':[]}
            elif op=='MOVE':
                need(r in live and charts[r]==e[2],'bad move');charts[r]=e[3]
                if r>=n:current[r]['moves'].append([j,e[2],e[3]])
            elif op=='CLEAR':
                k=len(new_certs);need(k<167 and r>=n and r in live and charts[r]==e[2],'bad clear')
                previous=old['clears'][k];original=oc[k];fresh=nc[k];origin=origins[j]
                need(previous['clear_index']==k and previous['event']==origin and previous['field']==r and previous['chart']==e[2],'old clear identity')
                need(original['original_clock']==fresh['original_clock']==origin and fresh['candidate_clock']==j and original['candidate_clock']==j and original['owner']==fresh['owner']==r and original['lifetime']==fresh['lifetime']==lifetimes[r] and original['chart']==fresh['chart']==e[2],'exact clear identity')
                need(unpack(previous['erased'])==unpack(original['row']) and rows[r]==unpack(fresh['row']),'full exact erased row mismatch')
                old_init=previous['init_event'];need(reverse[old_init]==current[r]['init_event'] and previous['init_chart']==current[r]['init_chart'],'init origin mismatch')
                mapped_moves=[[reverse[m[0]],m[1],m[2]] for m in previous['owned_moves']]
                need(mapped_moves==current[r]['moves'],'owned move origin mismatch')
                prior=unpack(previous['certificate']);need(previous['certificate'] is not None and all(role<n and role in live and role!=r for role in prior),'old certificate roles')
                cert=prior;method='retained_exact';solve=None
                if linear(rows,prior)!=rows[r]:
                    cert,solve=one_canonical_relation(rows[r],rows,prior,live,n);method='canonical_relation'
                need(all(role in live and role!=r for role in cert) and linear(rows,cert)==rows[r],'certificate relation mismatch')
                rec=dict(previous);rec.update(event=j,init_event=current[r]['init_event'],owned_moves=current[r]['moves'],erased=pack(rows[r]),erased_support=len(rows[r]),certificate=pack(cert),terms=len(cert),other_live=len(live)-1,other_rank=None,verified_exact=True)
                new_certs.append(rec);audit.append({'clear_index':k,'original_clock':origin,'candidate_clock':j,'field':r,'lifetime':lifetimes[r],'method':method,'solve':solve,'erased_changed':original['row']!=fresh['row']})
                live.remove(r);rows[r]={};charts[r]=None;del current[r]
            elif op=='SCALE':
                need(r in live and charts[r]==e[3] and F(e[2])!=0,'bad scale');q=F(e[2]);rows[r]={i:q*x for i,x in rows[r].items() if q*x}
            elif op in ('ADD','COPY'):
                src=e[2];q=F(e[3]);need(r in live and src in live and r!=src and q!=0 and charts[r]==charts[src]==e[4],'bad scalar')
                if op=='COPY':need(not rows[r],'copy guard')
                axpy(rows[r],rows[src],q)
            else:raise Refusal('unknown opcode')
        need(len(new_certs)==167 and not current and live==set(range(n)),'final lifetime count')
        dirty=sum(bool(c['erased']) for c in new_certs)
        summary={'word':'candidate-word.json.gz','sha256':CANDIDATE_GZ,'label':'candidate_7620_common_U','clears':167,'dirty':dirty,'zero_rows':167-dirty,'certified':167,'n_public':n,'min_other_rank':None,'final_public_rank':None,'rank_status':'not recomputed','status':'local_relations_checked_standalone_verifier_pending','scope':'1501 public-column relations under zero-on-INIT; not physical erasure or common U admission'}
        result={'summary':summary,'clears':new_certs}
        (out/'certificate.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
        report={'status':'PREPARED_RELATIONS_UNVERIFIED_EXTERNALLY','candidate_gzip_sha256':CANDIDATE_GZ,'exact_gzip_sha256':EXACT_GZ,'source_certificates_sha256':OLD_CERTS,'clear_count':167,'retained':sum(x['method']=='retained_exact' for x in audit),'new_canonical':sum(x['method']=='canonical_relation' for x in audit),'audit':audit,'limitations':'Standalone verifier and its two negative controls remain pending; rank metadata not recomputed; common U is not established.'}
    except Exception as exc:
        report={'status':'REFUSED_NO_CERTIFICATE','error_type':type(exc).__name__,'reason':str(exc),'completed_clear_audit':audit,'limitations':'No standalone or physical/common-U acceptance.'}
    (out/'status.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    return report


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--gate',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args()
    result=build(a.root,a.gate,a.out)
    return 0 if result['status']=='PREPARED_RELATIONS_UNVERIFIED_EXTERNALLY' else 1

if __name__=='__main__':raise SystemExit(main())
