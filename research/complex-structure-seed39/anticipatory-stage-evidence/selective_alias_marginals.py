#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Exact formal replay of 48 high aliases plus each of the 32 low aliases.

Provides complete local profile and helper-width inventory to a packing
screen. This is not native admission or an exponent claim for new subsets.
"""
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
VENDOR=HERE/'vendor/pr2339'
sys.path.insert(0,str(VENDOR))
from replay_core import replay


def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)


def canonical(d):
    return json.dumps(d,sort_keys=True,separators=(',',':')).encode()


def check_sources():
    receipt=read(HERE/'PR2339-SOURCE-RECEIPT.json')
    if receipt['head']!='bf1742aee4d855efb8bbd44a8419eddb33a679e5':raise RuntimeError('source head changed')
    required={'vendor/pr2339/replay_core.py','vendor/pr2339/inputs/blocks.json'}
    for name,tag in [('gauge44','base'),('extra','extra')]:
        required|={f'vendor/pr2339/inputs/{name}.canonical.json.gz',f'vendor/pr2339/witness/witness_80_{tag}.json'}
    seen=set()
    for entry in receipt['files']:
        path=entry['vendor_path']
        if path not in required:continue
        data=(HERE/path).read_bytes()
        if hashlib.sha256(data).hexdigest()!=entry['sha256']:raise RuntimeError('source SHA256 mismatch: '+path)
        if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=entry['git_blob_sha1']:raise RuntimeError('Git blob mismatch: '+path)
        seen.add(path)
    if seen!=required:raise RuntimeError('missing source pins')


def subset_witness(full, lows):
    selected=[i for i,p in enumerate(full['pairs'],1) if not p['low'] or p['register'] in lows]
    remap={old:new for new,old in enumerate(selected,1)}
    corr=[]
    for t in full['initial_corrections']:
        if all(abs(op) in remap for op in t['operator_word']):
            t=dict(t);t['operator_word']=[(1 if op>0 else -1)*remap[abs(op)] for op in t['operator_word']];corr.append(t)
    return dict(pairs=[full['pairs'][i-1] for i in selected],initial_corrections=corr,
                early_tail_events=full['early_tail_events'])


def inventory(w,inv,result):
    gone={p['register'] for p in inv['pairs']}
    final={r['register']:len(w['frames'][r['frame']]) for r in result['exact_cold_restoration']}
    widths=Counter(final.get(r,w['h'])-len(w['frames'][w['start'][r]])
                   for r in range(2*w['v'],2*w['v']+w['R']) if r not in gone)
    assert result['local_mass']-sum(r*n for r,n in widths.items())==1856
    return dict(sorted(widths.items()))


def main(output=None):
    if not __debug__:raise RuntimeError('assertions must remain enabled')
    check_sources()
    out=Path(output) if output is not None else HERE/'selective-alias-evidence';out.mkdir(parents=True,exist_ok=False)
    records={}; witnesses={};started=time.monotonic();b=.001697065994108880
    value=lambda p:sum(int(r)*n*math.expm1(b*math.log(73/int(r))) for r,n in p.items())
    for name,tag in [('gauge44','base'),('extra','extra')]:
        w=read(VENDOR/'inputs'/f'{name}.canonical.json.gz')
        blocks=read(VENDOR/'inputs/blocks.json')['sources'][0]['blocks']
        full=read(VENDOR/'witness'/f'witness_80_{tag}.json')
        lows=sorted(p['register'] for p in full['pairs'] if p['low'])
        assert len(lows)==32
        entries=[];base=None
        for selected in ([],*[[r] for r in lows],lows):
            inv=subset_witness(full,set(selected));r=replay(w,blocks,inv,expect_pairs=48+len(selected),expect_low=len(selected))
            widths=inventory(w,inv,r)
            item=dict(low_aliases=selected,helpers=w['R']-len(inv['pairs']),initial_corrections=len(inv['initial_corrections']),
                      local_profile=r['local_profile'],local_mass=r['local_mass'],width_inventory=widths,
                      zero_buffers=r['zero_FULL_cleanup_buffers'],formal_replay=r['status'],
                      diagnostic_local_excess=value(r['local_profile']))
            if base is None:base=item
            else:
                item['profile_delta_from_high48']={k:r['local_profile'].get(k,0)-base['local_profile'].get(k,0) for k in sorted(set(r['local_profile'])|set(base['local_profile'])) if r['local_profile'].get(k,0)!=base['local_profile'].get(k,0)}
                item['width_delta_from_high48']={k:widths.get(k,0)-base['width_inventory'].get(k,0) for k in sorted(set(widths)|set(base['width_inventory'])) if widths.get(k,0)!=base['width_inventory'].get(k,0)}
                item['diagnostic_excess_delta']=item['diagnostic_local_excess']-base['diagnostic_local_excess']
            key='none' if not selected else 'all' if len(selected)==32 else str(selected[0])
            witnesses[name+'/'+key]=dict(witness=inv,replay=r)
            entries.append(item)
            print(name,key,'mass',item['local_mass'],'E73',item['diagnostic_local_excess'],flush=True)
        assert entries[-1]['local_profile']=={int(k):v for k,v in full['replay']['local_profile'].items()}
        # Empirical additivity checks are exact identities for this complete
        # 32-singleton/full-set sample, not a theorem about all 2^32 subsets.
        summed=Counter(base['local_profile'])
        for one in entries[1:-1]:
            for rank,delta in one['profile_delta_from_high48'].items():summed[rank]+=delta
        additive={k:v for k,v in summed.items() if v}==entries[-1]['local_profile']
        records[name]=dict(cases=entries,singleton_deltas_sum_to_full_profile=additive)
    inputs=[VENDOR/'replay_core.py',VENDOR/'inputs/blocks.json']
    for name,tag in [('gauge44','base'),('extra','extra')]:inputs += [VENDOR/'inputs'/f'{name}.canonical.json.gz',VENDOR/'witness'/f'witness_80_{tag}.json']
    sources={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    receipt=dict(status='PASS_SCOPED_SELECTIVE_ALIAS_FORMAL_MARGINALS',seed=39,source_head='bf1742aee4d855efb8bbd44a8419eddb33a679e5',
                 source_sha256=sources,domain='Both words, high48 baseline, each singleton among32low aliases, and full80 aliases:68 cases.',
                 completed_cases=68,seconds=time.monotonic()-started,records=records,
                 scope='Exact free-operator replay and complete local rank/width accounting. Floating excess is diagnostic. New subsets still require native lowering, owner fill and full outer admission. Singleton/full-set additivity is sampled evidence only.')
    (out/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'WITNESSES.json.gz').write_bytes(gzip.compress(canonical(witnesses),mtime=0))
    print(receipt['status'],'68cases',receipt['seconds'])


if __name__=='__main__':main()
