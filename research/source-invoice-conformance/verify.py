#!/usr/bin/env python3
"""Independent claim calibrations and discriminating conformance failures."""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import conform
import native_invoice
import caller_invoice


def need(ok,message):
    if not ok:raise ValueError(message)


def reject(name,action,contains):
    try:action()
    except ValueError as error:
        need(contains in str(error),f'{name}: unexpected rejection {error}')
        return {'control':name,'rejection':str(error)}
    raise ValueError('Accepted invalid conformance control: '+name)


def authenticate():
    for row in conform.read(HERE/'EXPORTS.json')['exports']:
        need(sha256((HERE/row['file']).read_bytes()).hexdigest()==row['sha256'],'Source export drift: '+row['file'])


def ledger_check(audit):
    c=audit['caller'];calls={row['id']:row for row in c['calls']};paid=Counter();targets=Counter();debits=Counter()
    for group in c['local_groups']:
        need(len(group['call_ids'])==len(set(group['call_ids']))==group['count'],'Unique source call occurrences')
        need(all(calls[identifier]['orientation']==group['orientation'] for identifier in group['call_ids']),'Source call orientation provenance')
        dst=paid if group['side']=='paid' else targets if group['side']=='targets' else debits
        dst[group['rank']]+=group['count']
    for row in c['outer_paid']:paid[row['rank']]+=row['count']
    for row in c['main_targets']:targets[row['rank']]+=row['count']
    clean=lambda x:{str(k):v for k,v in sorted(x.items()) if v}
    need(clean(paid)==audit['invoice']['paid'] and clean(targets)==audit['invoice']['targets'],'Complete factored event ledger equals emitted invoice')
    return clean(debits)


def controls(audits,words,controller):
    a=audits['PR5383'];b=audits['PR5387'];rejections=[]
    bad=conform.claim(a);bad['invoice']=deepcopy(bad['invoice']);bad['invoice']['targets']['9']+=128
    rejections.append(reject('omitted_128_owned_helper_debits',lambda:conform.compare(a,bad),'targets H9:'))
    for name,side,rank,count in [('stale_paid_rank8','paid','8',128),('omitted_query_calls','paid','1',-1680),('omitted_whole_idles','paid','16',-448)]:
        bad=deepcopy(conform.claim(a));bad['invoice'][side][rank]+=count
        rejections.append(reject(name,lambda bad=bad:conform.compare(a,bad),'Invoice mismatch:'))
    bad=deepcopy(conform.claim(a));bad['invoice']['paid']['1']-=16;bad['invoice']['paid']['2']+=8
    need(sum(int(k)*v for k,v in bad['invoice']['paid'].items())==sum(int(k)*v for k,v in a['invoice']['paid'].items()),'Rank-mass-preserving billing mutation')
    rejections.append(reject('equal_rank_mass_wrong_profile',lambda:conform.compare(a,bad),'Invoice mismatch:'))
    rejections.append(reject('same_invoice_stale_word_binding',lambda:conform.compare(b,conform.claim(a)),'Claim source binding differs'))
    bad=deepcopy(conform.claim(a));bad['invoice']['paid']['1']=True
    rejections.append(reject('boolean_count_is_not_integer',lambda:conform.compare(a,bad),'exact nonnegative integers'))
    # These invoke the independent interpreter on altered source programs, not
    # author receipts or the annotation hashes that the source parser ignores.
    base=words['PR5383']
    bad=deepcopy(base);next(e for e in bad['programs']['forward'] if e[0]=='climb')[5]+=1
    rejections.append(reject('misstated_actual_paid_rank',lambda:native_invoice.extract(bad),'independently derived frame rank'))
    bad=deepcopy(base);e=next(e for e in bad['programs']['forward'] if e[0]=='warp' and e[3]!=e[4]);e[4]=e[3]
    rejections.append(reject('unpriced_native_frame_residual',lambda:native_invoice.extract(bad),'unpriced residual'))
    bad=deepcopy(base)
    index,event=next((i,e) for i,e in enumerate(bad['programs']['forward']) if e[0]=='climb')
    bad['programs']['forward'][index]=['zero_retag',['L',event[2]],event[3],event[4]]
    rejections.append(reject('false_zero_retag',lambda:native_invoice.extract(bad),'identically zero full symbolic row'))
    bad=deepcopy(base);bad['programs']['backward'][1][1][3]*=-1
    rejections.append(reject('wrong_preparation_sign',lambda:native_invoice.extract(bad),'symbolic return mismatch'))
    bad=deepcopy(base);bad['owned']['backward'].remove(['L',225])
    rejections.append(reject('undeclared_owned_input_clear',lambda:native_invoice.extract(bad),'only declared owned input'))
    bad=deepcopy(base);bad['programs']['forward'].insert(0,['unpriced_magic',1])
    rejections.append(reject('unknown_native_operation',lambda:native_invoice.extract(bad),'unknown event opcode'))
    native=a['native']
    for name,mutate,needle in [
        ('changed_literal_idle',lambda c:next(e for e in c['physical_events'] if e[0]=='IDLE')[2].append(32),'Caller'),
        ('changed_literal_orientation',lambda c:next(e for e in c['physical_events'] if e[0]=='LOCAL').__setitem__(3,True),'Caller'),
        ('wrong_main_diagonal',lambda c:c['diagonal'][0].__setitem__(0,1),'diagonal mismatch'),
        ('unknown_caller_operation',lambda c:c['physical_events'].insert(0,['unpriced_magic']),'Known caller opcode'),
        ('boundary_program_mismatch',lambda c:c['boundaries']['right_program'][0].__setitem__(3,'1'),'program/matrix mismatch')]:
        bad=deepcopy(controller);mutate(bad)
        rejections.append(reject(name,lambda bad=bad:caller_invoice.extract(bad,native),needle))
    bad=deepcopy(base);bad['schema']='unknown-new-abi/1'
    rejections.append(reject('unknown_source_schema',lambda:native_invoice.extract(bad),'schema'))
    # Altering the main endpoint while keeping its formal row cannot inherit
    # the fixed caller tariff. Include the additional paid transport and update
    # its adapter, rather than relying on a stale-final-frame rejection.
    bad=deepcopy(base);v=bad['canonical']['v'];old=bad['canonical']['final'][v]
    full=bad['canonical']['final'][0];bad['canonical']['final'][v]=full
    for direction,program in bad['programs'].items():
        index=next(i for i,e in enumerate(program) if e[:3]==['adapter','new_to_old',v])
        program[index][3]=full
        program.insert(index,['climb','changed_main_contract',v,old,full,1])
    rejections.append(reject('changed_main_endpoint_tariff',lambda:native_invoice.extract(bad),'unsupported native boundary'))
    bad=deepcopy(base);role=next(i for i in range(224,632) if bad['canonical']['start'][i]==0)
    bad['programs']['forward'][1:1]=[['warp',['L',role],1,0,0] for _ in range(4097)]
    rejections.append(reject('symbolic_word_growth_limit',lambda:native_invoice.extract(bad),'unsupported symbolic replay domain'))
    rejections.append(reject('duplicate_json_keys',lambda:conform.parse(b'{"a":1,"a":2}'),'Duplicate JSON key'))
    rejections.append(reject('floating_point_input',lambda:conform.parse(b'{"a":1.0}'),'Exact integer/rational'))
    rejections.append(reject('exponent_rational_notation',lambda:caller_invoice.rational('1e10000'),'integer/positive-integer spelling'))
    # Deleting or poisoning author profile annotations leaves extraction intact.
    changed=deepcopy(base);changed['paid_profiles']={'forward':{'1':0},'backward':{'1':999}}
    changed['canonical']['local_profile']={'untrusted':'fabricated'}
    actual=native_invoice.extract(changed)
    need(all(actual['orientations'][d]['paid']==a['native']['orientations'][d]['paid'] and
             actual['orientations'][d]['helpers']==a['native']['orientations'][d]['helpers'] for d in ('forward','backward')),
         'Declared histograms do not drive extraction')
    return rejections


def cli_check(case):
    with tempfile.TemporaryDirectory(prefix='source-invoice-') as directory:
        root=Path(directory);claim_file=root/'CLAIM.json';claim_file.write_text(json.dumps(case['claim']))
        invoice=root/'INVOICE.json';audit=root/'AUDIT.json'
        cmd=[sys.executable,'-I','-B',str(HERE/'conform.py'),'--word',str(HERE/case['file']),
             '--controller',str(HERE/'source/CONTROLLER.json'),'--expect',str(claim_file),
             '--write-invoice',str(invoice),'--write-audit',str(audit)]
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
        need(p.returncode==0,'CLI conformance and opt-in exports: '+p.stderr)
        stdout=conform.parse(p.stdout.encode());need(stdout['status']=='PASS_SOURCE_INVOICE_CONFORMANCE','CLI reports a checked claim')
        need(conform.read(invoice)==case['claim']['invoice'],'CLI preflight-compatible complete invoice')
        blob=conform.read(audit);need(blob['source_binding']==case['claim']['source_binding'],'CLI audit source binding')
        try:conform.write_new(invoice,{})
        except FileExistsError:pass
        else:raise ValueError('CLI output overwrite accepted')
        return {'status':stdout['status'],'audit_sha256':conform.digest(blob),'invoice_sha256':conform.digest(conform.read(invoice))}


def run():
    authenticate();controller=conform.read(HERE/'source/CONTROLLER.json')
    cases=conform.read(HERE/'CALIBRATIONS.json')['cases'];audits={};words={};results={}
    for case in cases:
        name=case['name'];words[name]=conform.read(HERE/case['file'])
        audit=conform.extract(words[name],controller);conform.compare(audit,case['claim']);audits[name]=audit
        result=conform.summary(audit,True);result['surrendered_target_ledger']=ledger_check(audit)
        results[name]=result
    a,b=audits['PR5383'],audits['PR5387']
    need(a['invoice']==b['invoice'] and a['source_binding']!=b['source_binding'],'Same recursive invoice, different source programs')
    need(b['native']['orientations']['backward']['scalar_allowance']-
         a['native']['orientations']['backward']['scalar_allowance']==32,'Actual scalar-cost difference is retained')
    need(results['PR5383']['surrendered_target_ledger']=={'9':128},'Every lost target is traced to owned source roles and actual call sites')
    return {'status':'PASS_SOURCE_INVOICE_CONFORMANCE_SUITE','calibrations':results,
            'controls':controls(audits,words,controller),'cli':cli_check(cases[1]),
            'scope':'Source-protocol and recursive invoice conformance; separate ordinary costs, phase, precision/tape, compiler and analytic obligations remain.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--emit',action='store_true');args=parser.parse_args()
    result=run()
    if not args.emit:
        expected=conform.read(HERE/'RESULT.json')
        need(caller_invoice.canonical(result)==caller_invoice.canonical(expected),'Complete typed deterministic receipt')
    print(json.dumps(result,indent=2,sort_keys=True))
