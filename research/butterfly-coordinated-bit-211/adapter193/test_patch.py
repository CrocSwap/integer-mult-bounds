#!/usr/bin/env python3
"""Cheap fresh-evidence portability controls. No physical supplier is run."""
import sys
if sys.flags.optimize:raise SystemExit('Refusing optimized Python')
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
import argparse,copy,gzip,json,math
from pathlib import Path
from semantic_v2 import PREFIX,RECORD,FLOW,canon,compact,pretty,digest,validate
ap=argparse.ArgumentParser();ap.add_argument('--repo193',type=Path,required=True);ap.add_argument('--actual',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
repo=a.repo193;actual=json.loads(a.actual.read_text());published=json.loads((repo/'research/source-assisted-v4/certificate.json').read_text())
def variant(record_change=None,flow_change=None,cert_change=None,cp_change=None,global_change=None,encoding='normal'):
    def obj(rel):return json.loads((repo/rel).read_text())
    record=obj(RECORD);flow=obj(FLOW);cert=json.loads(gzip.decompress((repo/(PREFIX+'lift.certificate.json.gz')).read_bytes()))
    # Reconstruct the exactly observed Mac diagnostics, regardless of host.
    record['numerical_complex_root']=0.0005471133463770651
    flow['numerical_local_root']=0.0007009184438593612
    if record_change:record_change(record)
    rb=compact(record);flow['cache_sha256']['record.json']=digest(rb)
    if flow_change:flow_change(flow)
    fb=pretty(flow);cert['input_profile_sha256']=digest(fb)
    if cert_change:cert_change(cert)
    payload=compact(cert);proof=gzip.compress(payload,compresslevel=1 if encoding=='recompress' else 9,mtime=0)
    if encoding=='OS255':proof=proof[:9]+bytes([255])+proof[10:]
    if encoding=='corrupt':proof=proof[:-1]+bytes([proof[-1]^1])
    lift=obj(PREFIX+'lift.json');lift['certificate_sha256']=digest(proof);lb=pretty(lift)
    cp=obj(PREFIX+'complex-profile.json');cp['numerical_local_root']=flow['numerical_local_root'];cp['entropy']=flow['entropy']
    cp['exact_lift_certificate_sha256']=digest(proof)
    cp['proof_chain_sha256'].update({RECORD:digest(rb),FLOW:digest(fb),PREFIX+'lift.certificate.json.gz':digest(proof),PREFIX+'lift.json':digest(lb)})
    if cp_change:cp_change(cp)
    cb=pretty(cp);glob=obj(PREFIX+'global.json');glob['construction_receipts']['complex_lift_certificate_sha256']=digest(proof);glob['source_sha256']['complex']=digest(cb)
    if global_change:global_change(glob)
    gb=pretty(glob)
    for branch in ('complex','bit'):glob[branch].pop('numerical_root_for_discovery_only',None)
    x=copy.deepcopy(actual);x.update(flow=canon(flow),lift=canon(lift),complex_profile=canon(cp),assembly=canon(glob),lift_certificate_sha256=digest(proof))
    overlay={repo/rel:data for rel,data in [(RECORD,rb),(FLOW,fb),(PREFIX+'lift.certificate.json.gz',proof),(PREFIX+'lift.json',lb),(PREFIX+'complex-profile.json',cb),(PREFIX+'global.json',gb)]}
    return x,lambda p:overlay[p] if p in overlay else p.read_bytes(),dict(record=digest(rb),flow=digest(fb),payload=digest(payload))
accepted=[];rejected=[]
validate(actual,published,repo);accepted.append('Original fresh evidence')
for encoding in ('normal','OS255','recompress'):
    x,reader,hashes=variant(encoding=encoding)
    assert hashes==dict(record='e31f5c73f2744965f63243953858a57ffd099c4a6352a080c3ac74e2b8dd1486',flow='e5024707ca0669de4fa5ee07d5d01d9e61ca2bf32b1229642c717f2d67138959',payload='906adba2d36d6644519783262a8030e70929ff54366905113375ed5ecd45d130')
    validate(x,published,repo,reader);accepted.append('Exact Mac record/flow/payload reconstruction: '+encoding)
def reject(name,**kwargs):
    try:
        x,reader,_=variant(**kwargs);validate(x,published,repo,reader)
    except (AssertionError,ValueError,KeyError,gzip.BadGzipFile,EOFError):rejected.append(name)
    else:raise AssertionError('Accepted adverse control: '+name)
reject('Record exact role count',record_change=lambda r:r.update(R=r['R']+1))
reject('Unapproved gauge trial float',record_change=lambda r:r.update(gauge_trial_saving=math.nextafter(r['gauge_trial_saving'],1)))
reject('Record root beyond diagnostic precision',record_change=lambda r:r.update(numerical_complex_root=r['numerical_complex_root']+1e-8))
reject('Flow root beyond diagnostic precision',flow_change=lambda f:f.update(numerical_local_root=f['numerical_local_root']+1e-8))
reject('Unapproved entropy float',flow_change=lambda f:f.update(entropy=math.nextafter(f['entropy'],math.inf)))
reject('Flow exact histogram',flow_change=lambda f:f['local_histogram'].update({'1':f['local_histogram']['1']+1}))
reject('Flow to record binding',flow_change=lambda f:f['cache_sha256'].update({'record.json':'0'*64}))
reject('Deleted record cache binding',flow_change=lambda f:f['cache_sha256'].pop('record.json'))
reject('Embedded flow binding',cert_change=lambda c:c.update(input_profile_sha256='0'*64))
reject('Embedded witness binding',cert_change=lambda c:c.update(input_witness_sha256='0'*64))
reject('Exact map removed',cert_change=lambda c:c['maps'].pop())
reject('Exact topological order',cert_change=lambda c:c['topological_order'].reverse())
reject('Exact kernel payload',cert_change=lambda c:c['kernel_pairs'].append([0,0,0,0]))
reject('Proof metadata changed',cert_change=lambda c:c.update(schema='changed'))
reject('Actual record proof-chain binding',cp_change=lambda c:c['proof_chain_sha256'].update({RECORD:'0'*64}))
reject('Actual flow proof-chain binding',cp_change=lambda c:c['proof_chain_sha256'].update({FLOW:'0'*64}))
for rel in (RECORD,FLOW,PREFIX+'lift.json',PREFIX+'lift.certificate.json.gz'):
    reject('Deleted proof-chain binding: '+rel,cp_change=lambda c,rel=rel:c['proof_chain_sha256'].pop(rel))
reject('Finite scalar budget',global_change=lambda g:g['finite_bridge']['semantic'].update(G={'base':2,'exponent':10000}))
reject('Gzip CRC',encoding='corrupt')
result=dict(status='PASS two-root portability controls',supplier_proofs_executed=False,accepted=accepted,rejected=rejected,exact_mac_hash_reconstruction=hashes)
with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
