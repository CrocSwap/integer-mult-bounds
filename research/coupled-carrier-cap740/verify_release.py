#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check stored release bindings; this does not rerun native or outer stages.

The receipt-binding pattern follows Nick Petalas's PR3030. The scientific
engines and actual release evidence are separately identified in the package.
"""
import copy
import gzip
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

P=Path(__file__).resolve().parent
E=P/'evidence'
SOURCE='fa3e2d855ac5298ecc849e596d79dcef7a72668a276b6524585bc0cd616ce474'
STAGES=['export-pr2894','export-pr2833','four-kernel-stage','preload-stage','parent-paired-stage','paired-extension-stage','rank7-overlay-stage','declared-edit-stage','derive-closed-adapters','fresh-current-native','complete-admission']

def need(ok,why):
    if not ok:raise ValueError(why)
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def validate(records,finite,bindings,invoice,materialized,outer):
    full,admission,release,native=records
    need(full['status']=='PASS_COUPLED_CARRIER_T740_COMPLETE_RELEASE','composition release')
    need(admission['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE','complete admission')
    need(release['status']=='PASS_RELEASE','complete outer release')
    need(full['admission_sha256']==bindings['admission'],'admission binding')
    need(full['release_receipt_sha256']==admission['release_receipt_sha256']==bindings['release'],'release binding')
    need(full['native_receipt_sha256']==admission['native_receipt_sha256']==bindings['native'],'native binding')
    need(admission['fill_sha256']==materialized['sha256'],'actual admitted gzip input')
    need(materialized['payload_sha256']==finite['materialized']['fill_payload_sha256'],'literal checked fill payload')
    for key in ['order_sha256','dispatch_sha256']:
        need(admission[key]==materialized[key]==finite['materialized'][key],'literal allocation '+key)
    need(admission['source_manifest_sha256']==native['manifest_sha256']==full['source_manifest_sha256']==SOURCE,'same coupled-carrier source')
    need(native['status']=='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE' and native['fresh_current_provider_count']==2,'two fresh current native providers')
    for tag in ['base','extra']:need(native['providers'][tag]['word_sha256']==sha(P/f'words/{tag}.json.gz'),'native literal word '+tag)
    need(full['fresh_retained_bootstrap'] is False and native['fresh_retained_parent'] is False and native['reused_retained_parent'] is True,'explicit authenticated retained reuse')
    need(native['reused_retained_native_count']==2 and native['fresh_retained_native_count']==0,'retained cache accounting')
    need(admission['replicas']==740,'T740 admission')
    expected={int(r):n for r,n in finite['profile'].items()}
    need({int(r):n for r,n in admission['profile'].items()}==expected,'complete admitted bill')
    need(admission['package_manifest_sha256']==release['manifest_sha256'],'same released package')
    endpoint=Q(finite['kappa'])
    need(endpoint==Q(full['kappa'])==Q(admission['kappa'])==Q(release['kappa_decimal'])==Q(outer['kappa_rational'])==Q(outer['kappa']),'same modern outer endpoint')
    need(Q(full['baseline_kappa'])==Q(finite['baseline_kappa']) and Q(full['gain'])==Q(finite['gain']),'same strict comparison')
    need(Q(finite['baseline_kappa'])<endpoint<Q(finite['root'][0]),'strict valid improvement')
    need([s['stage'] for s in full['stages']]==STAGES and all(s['exit_code']==0 for s in full['stages']),'all complete source stages')
    need(invoice['status']=='PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE','actual physical invoice')
    need((invoice['physical'],invoice['private_zero_buffers'],invoice['helpers'])==(663549,91,408),'complete physical stock')
    need(invoice['charged_prefix_bits']==2048 and invoice['global_prefix_bits']<=2048,'actual paid prefix bound')
    need(invoice['complete_invocation_sweeps']==invoice['bridge_sweeps']==len(invoice['selected_calls'])==6660,'all invocation sweeps')
    local={int(r):n for r,n in finite['words']['base']['local_profile'].items()}
    need({int(r):n for r,n in invoice['selected_local_paid_profile'].items()}=={r:6660*n for r,n in local.items()},'actual invoice local profile')

def check(finite=None):
    finite=read(E/'FINITE.json') if finite is None else finite
    names=['COMPOSITION-RESULT.json','ADMISSION-RESULT.json','RELEASE-RECEIPT.json','NATIVE-RECEIPT.json']
    records=[read(E/name) for name in names]
    bindings=dict(admission=sha(E/names[1]),release=sha(E/names[2]),native=sha(E/names[3]))
    raw=gzip.decompress((E/'PREFIX-AND-INVOICE.json.gz').read_bytes())
    need(hashlib.sha256(raw).hexdigest()==read(E/'INVOICE-PAYLOAD.json')['decompressed_sha256'],'invoice payload binding')
    invoice=json.loads(raw);materialized=read(E/'MATERIALIZED.json');outer=read(E/'OUTER-CLAIM.json')
    validate(records,finite,bindings,invoice,materialized,outer)
    need(records[3]['retained_reuse_receipt_sha256']==sha(E/'RETAINED-REUSE-RECEIPT.json'),'explicit retained reuse receipt')
    for tag in ['base','extra']:
        path=E/('NATIVE-'+tag+'-STEPS.json');steps=read(path)
        need(sha(path)==records[3]['providers'][tag]['complete_native_files']['STEPS.json'],'native step binding '+tag)
        need([s['step'] for s in steps]==['native','ledgers','local-replay','wrappers','phases'] and all(s['exit_code']==0 for s in steps),'five native stages '+tag)
    claim=read(P/'CLAIM.json')
    for key in ['kappa','baseline_kappa','gain']:need(Q(claim[key])==Q(finite[key]),'public claim '+key)
    need(claim['profile']==finite['profile'] and claim['physical']==invoice['physical'],'public complete bill')
    need(claim['source_manifest_sha256']==SOURCE and claim['admission_sha256']==bindings['admission'],'public source and admission binding')
    need(claim['release_receipt_sha256']==bindings['release'] and claim['native_receipt_sha256']==bindings['native'],'public native and release binding')
    for s in records[0]['stages']:
        name=s['stage'];need(name in STAGES,'safe stage name')
        need(sha(E/'logs'/(name+'.log.txt'))==s['log_sha256'],'exact completed log '+name)
    controls=[(1,'profile',{'1':1}),(1,'source_manifest_sha256','0'*64),(1,'fill_sha256','0'*64),(1,'order_sha256','0'*64),
              (1,'dispatch_sha256','0'*64),(2,'kappa_decimal','1/100'),(3,'fresh_current_provider_count',0),(3,'reused_retained_parent',False)]
    for i,key,value in controls:
        bad=copy.deepcopy(records);bad[i][key]=value
        try:validate(bad,finite,bindings,invoice,materialized,outer)
        except ValueError:continue
        raise ValueError('accepted receipt mutant '+key)
    for key,value in [('private_zero_buffers',90),('charged_prefix_bits',1024)]:
        bad=copy.deepcopy(invoice);bad[key]=value
        try:validate(records,finite,bindings,bad,materialized,outer)
        except ValueError:continue
        raise ValueError('accepted invoice mutant '+key)
    result=dict(status='PASS_COUPLED_CARRIER_T740_STORED_RELEASE_BINDINGS',rejected_controls=10,kappa=finite['kappa'],physical=invoice['physical'],
                global_prefix_bits=invoice['global_prefix_bits'],charged_prefix_bits=invoice['charged_prefix_bits'],
                scope='Stored receipt, source, word, literal allocation and invoice bindings; full replay is separate.')
    print(result['status'],'controls',result['rejected_controls'],flush=True)
    return result

if __name__=='__main__':print(json.dumps(check(),indent=2,sort_keys=True))
