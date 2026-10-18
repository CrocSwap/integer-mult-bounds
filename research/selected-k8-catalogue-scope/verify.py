#!/usr/bin/env python3
"""Bind the selected k8 interface to the scope of the historical catalogue bound."""
import json
from hashlib import sha256, sha1
from pathlib import Path
from collections import Counter

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok, why):
    if not ok:raise ValueError(why)


def read(name):return json.loads((ROOT/name).read_bytes())


def interface(provider):
    return {'inventory':provider['inventory'],'profile':provider.get('expected_profile',provider.get('profile'))}


def mass(table):return sum(int(k)*v for k,v in table.items())


def verify():
    for row in json.loads((HERE/'SOURCES.json').read_bytes())['files']:
        if row['usage']!='input':continue
        data=(ROOT/row['path']).read_bytes()
        need(sha256(data).hexdigest()==row['sha256'],'source SHA256 mismatch')
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],'source blob mismatch')
    selected=read('certificates/selected-result.json')
    manifest=read(selected['source_manifest'])
    name='research/complex-t16-rare-pattern-exchanges/data/SPEC.json'
    need(name in manifest['files'],'selected manifest does not bind current SPEC')
    need(sha256((ROOT/name).read_bytes()).hexdigest()==manifest['files'][name],'SPEC selected binding')
    spec=read(name)
    need(set(spec['providers'])=={'gauge44'},'selected provider set')
    chosen=interface(spec['providers']['gauge44'])
    old_spec=read('research/gauge44-leaver8/data/SPEC.json')
    need(len(old_spec['providers'])==1,'pre-slot provider set')
    old=interface(next(iter(old_spec['providers'].values())))
    catalogue=read('research/heterogeneous-owner-assembly/CATALOGUE.json')
    rows=[interface(r) for r in catalogue['interfaces']]
    baseline=interface(next(r for r in catalogue['interfaces'] if r['id']=='P25'))
    need(len(rows)==25 and len(catalogue['records'])==71,'historical catalogue size')
    need(baseline in rows and chosen not in rows and old not in rows,'interface applicability')
    need(chosen['inventory']==old['inventory'],'helper inventory changed across slot delta')
    ranks=set(chosen['profile'])|set(old['profile'])
    delta={r:chosen['profile'].get(r,0)-old['profile'].get(r,0) for r in ranks}
    delta={r:v for r,v in delta.items() if v}
    need(delta=={'3':14,'4':-28,'5':14},'seven-slot paid-profile delta')
    need(mass(delta)==0 and sum(delta.values())==0,'rank/count preserving slot delta')
    widths=chosen['inventory'];prices={'4':-1,'5':-20,'7':-8,'8':-2,'9':4}
    def summarize(p):
        return {'helper_count':sum(p['inventory'].values()),'helper_width':mass(p['inventory']),
                'local_rank_mass':mass(p['profile']),
                'signed_helper_price':sum(prices[k]*v for k,v in p['inventory'].items())}
    stats={k:summarize(v) for k,v in [('U8',baseline),('R480_before_slots',old),('selected_k8',chosen)]}
    need(all(s['local_rank_mass']-s['helper_width']==1856 for s in stats.values()),'shared mass identity')
    need(stats['selected_k8']['helper_width']==3730 and stats['U8']['helper_width']==3778,'width difference')
    # Matching only the shared mass identity would incorrectly admit this
    # outside-catalogue provider. Both exact dictionaries are necessary.
    changed={'inventory':baseline['inventory'],'profile':dict(baseline['profile'])}
    changed['profile']['3']+=4;changed['profile']['4']-=8;changed['profile']['5']+=4
    need(mass(changed['profile'])==mass(baseline['profile']) and changed not in rows,'mass-only alias control')
    need({'inventory':baseline['inventory'],'profile':chosen['profile']} not in rows,'mixed-interface control')
    need({'inventory':chosen['inventory'],'profile':baseline['profile']} not in rows,'inventory-only control')
    return {'status':'PASS_SELECTED_K8_CATALOGUE_SCOPE','selected_kappa':selected['kappa'],
            'catalogue_base':catalogue['base'],'records':71,'interfaces':25,
            'selected_in_catalogue':False,'pre_slot_R480_in_catalogue':False,
            'selected_SPEC':name,'selected_interface':chosen,'pre_slot_interface':old,
            'slot_delta':delta,'statistics':stats,'controls':3,
            'symbolic_reduced_cost_delta':'14*(phi_b(3)-2*phi_b(4)+phi_b(5)) < 0 for 0 < b < 1',
            'scope':'Source-bound navigation/applicability receipt; no new catalogue theorem, numerical frontier or supplier replay.'}


if __name__=='__main__':
    result=verify()
    if (HERE/'RESULT.json').exists():need(result==json.loads((HERE/'RESULT.json').read_bytes()),'receipt mismatch')
    print(json.dumps(result,indent=2,sort_keys=True))
