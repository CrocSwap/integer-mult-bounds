#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Emit and independently verify the composed428 literal owner replacement.

Prepared for Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
Credits Jeremy Kothe (@jeremykothe2), PR2435, for source order and packing.
Native/global/compiler/physical/outer admission remain separate obligations.
"""
from collections import Counter,defaultdict
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import price_composition as p

OLD=p.RESEARCH/'anticipatory-stage-evidence'
COM=p.ROOT/'composition2435'
V=COM/'vendor'
REPLACE={640:533,641:554,606:619,635:621,637:622,638:623}
PINS={
    p.ENGINE:'81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482',
    V/'new/borrow-fill/FILL.json.gz':'6920ed0b8a30e168d4a8599a760de5114ae8833d3caaa4dd555dc9f9b626faee',
    V/'new/borrow-fill/ORDER.json':'f693a8f0b78eaa803d4e7860b3cc71112dafb323db27998cea132d5b0f18dd84',
    V/'new/borrow-fill/DISPATCH.json':'e7a20e652d6bd8371e48f9463d266a2d23c6c5cd3d41b7c039ef9efa8fc3cd3e',
    V/'new/borrow/words/BORROW-WORD-43base.json.gz':'46924868825e07168c2e8149dada6b1157afa444b316eb00c16555ec8a4004db',
    V/'new/borrow/words/BORROW-WORD-43extra.json.gz':'b678b0bad0275b6870681b40bbcaefc7e815ed36713f0318a1b236cdf7d9e0b6',
    COM/'interface/COMPOSITION-CHECK.json':'6357cd8d5571b793b8df4e38b4013e2cdf1cc2f66486e09359a93f9923c4a075',
    COM/'interface/COMPOSED-base.json.gz':'6cbe99808ecc5cf4a3a29df3bb70300ecf1b509d58de8d621acdb64fee87e919',
    COM/'interface/COMPOSED-extra.json.gz':'38146a4faa04fb1fd697c57cae0b323d06b00ae5561984689c62ec518b0e4be0',
    OLD/'parent/new/PLAN.json':'bf1abd33c8ba946371cae37e021747343ef6603a31297bcc962197cc23f535e2',
    OLD/'owners/check_owners.py':'5f9512a49a633d04d79b830b5c4e9179a68df3f3b2edcb056306404f25b93c43',
}

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def write(path,obj):
    raw=(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n').encode()
    path.write_bytes(gzip.compress(raw,mtime=0) if path.suffix=='.gz' else raw)

def make_windows(order,template):
    # Direct event expansion produces the proposed plan windows. The imported
    # independent checker then reconstructs them from its own source traversal.
    source=template['execution_schedule']
    starts=[i for i,e in enumerate(source) if e['kind']=='local_cover_sweep']
    blocks={source[a]['stage']:source[a:b] for a,b in zip(starts,starts[1:]+[30])}
    pairs={e['stage']:e['pair'] for e in template['recipe'] if e['kind']=='local'}
    ranks={x['child']:x['rank'] for x in template['idle_children']}
    touched={r:{pair:-1 for pair in range(4)} for r in range(74)}
    callpos={};intervals={};pos=0
    for stage,replica in order:
        for event in blocks[stage]:
            kind=event['kind']
            if kind=='local_cover_sweep':
                callpos[stage,replica]=pos;touched[replica][pairs[stage]]=pos
            elif kind=='bridge':
                touched[replica][event['src']]=touched[replica][event['dst']]=pos
            elif kind=='idle_cover_sweep':
                for child in event['child_indices']:
                    if child in ranks:intervals[replica,child]=(touched[replica][event['pair']],pos)
            pos+=1
    return {f'{owner},{child}':[ranks[child],[t for t,call in enumerate(order) if lo<callpos[tuple(call)]<hi]] for (owner,child),(lo,hi) in intervals.items()}

def controls(audit,roles,geo,providers,dispatch,frames,pending):
    first=roles[0];same=next(i for i,r in enumerate(roles) if i and r['time']==first['time'])
    mutations=[
        ('wrong_width',0,dict(first,width=first['width']-1),'whole native helper width'),
        ('wrong_family',0,dict(first,family=8*74*112),'physical family identity'),
        ('wrong_time',0,dict(first,time=(first['time']+1)%666),'owner invocation time'),
        ('duplicate_helper',same,dict(roles[same],helper=first['helper'],width=first['width']),'duplicate native helper role'),
        ('duplicate_family',same,dict(first,helper=roles[same]['helper'],width=roles[same]['width']),'duplicate physical family within call'),
        ('slice_overflow',0,dict(first,offset=geo['ranks'][first['child']]),'slice capacity')]
    for label,active,reason in (('active_data_alias',True,'helper aliases active data family'),('outside_bridge_window',False,'strict bridge-aware window')):
        replacement=None;call=first['stage'],first['replica']
        for child,cap in geo['ranks'].items():
            is_active=geo['pair'][child]==geo['stage_pair'][first['stage']]
            lo,hi=geo['windows'][first['replica'],child]
            if cap<first['width'] or is_active!=active or (not active and lo<geo['callpos'][call]<hi):continue
            replacement=dict(first,owner_replica=first['replica'],child=child,offset=0,
                copy=112*first['replica']+first['port'],
                family=first['replica']*8*112+(2*geo['pair'][child]+geo['side'][child])*112+first['port']);break
        p.need(replacement is not None,'construct '+label)
        mutations.append((label,0,replacement,reason))
    previous={};overlap=None
    for i,row in enumerate(roles):
        key=row['owner_replica'],row['child'],row['port']
        if key in previous:
            earlier=previous[key]
            if earlier['time']!=row['time'] and earlier['offset']+row['width']<=geo['ranks'][row['child']]:
                overlap=(i,dict(row,offset=earlier['offset']));break
        previous[key]=row
    p.need(overlap is not None,'construct overlap control')
    mutations.append(('overlapping_residual_axes',overlap[0],overlap[1],'overlapping residual axes in bin'))
    passed=[]
    for name,index,bad,reason in mutations:
        changed=list(roles);changed[index]=bad
        try:audit.audit(changed,geo,providers,dispatch,frames,pending)
        except ValueError as exc:p.need(str(exc)==reason,'unexpected control '+name+': '+str(exc))
        else:raise ValueError('accepted control '+name)
        passed.append(name)
    return passed

def main():
    p.need(__debug__,'optimized Python unsupported')
    for path,pin in PINS.items():p.need(digest(path)==pin,'source pin mismatch: '+str(path))
    audit=load(OLD/'owners/check_owners.py','composed_independent_owners');audit.R=428
    for name,pin in audit.PARENT_PINS.items():p.need(digest(OLD/'parent'/name)==pin,'parent pin '+name)
    p.need(digest(OLD/'owners/DATA-PHASES.json')==audit.PHASE_PIN,'phase pin')
    original_plan=p.read(OLD/'parent/new/PLAN.json');plan=copy.deepcopy(original_plan)
    order=p.read(V/'new/borrow-fill/ORDER.json');source_dispatch=p.read(V/'new/borrow-fill/DISPATCH.json')
    p.need([row[:2] for row in source_dispatch]==order,'dispatch order binding')
    template=p.read(OLD/'parent/GLOBAL-TEMPLATE.json.gz');phases=p.read(OLD/'owners/DATA-PHASES.json')
    plan['order']=order;plan['windows']=make_windows(order,template)
    oldcalls={(x['stage'],x['replica']):x for x in original_plan['provider_calls']}
    plan['provider_calls']=[dict(oldcalls[stage,replica],stage=stage,replica=replica,provider=tag,time=t) for t,(stage,replica,tag) in enumerate(source_dispatch)]
    comp=p.read(COM/'interface/COMPOSITION-CHECK.json');providers={};source_origins={};replacement_sources={}
    for tag,wordtag in (('gauge44','base'),('extra','extra')):
        word=p.read(COM/f'interface/COMPOSED-{wordtag}.json.gz')
        source=p.read(V/f'new/borrow/words/BORROW-WORD-43{wordtag}.json.gz')
        record=comp['providers'][wordtag]
        p.need(record['transport']['status']=='PASS_BORROW_WORD_FREE_ALGEBRA_ALL_COLUMNS_AND_NATIVE_FRAMES','composition transport')
        origins=[r for r in range(224,704) if r not in word['removed']]
        source_origins[tag]=[r for r in range(224,704) if r not in source['removed']]
        width=lambda r:len(word['helper_final'].get(str(r),range(9)))-len(word['start_extra'].get(str(r),[]))
        widths=[width(r) for r in origins]
        paid=p.integer_counter(record['local_profile'])
        p.need(dict(Counter(widths))==p.integer_counter(record['width_inventory']),'actual word width binding')
        providers[tag]=dict(origins=origins,widths=widths,paid=paid,ports=word['ports'])
        desc=plan['provider_registry'][tag];desc['widths']=widths;desc['actual_paid_profile']=dict(paid)
        desc['composed_word_sha256']=record['composed_word_sha256']
        replacement_sources[tag]=set(word['removed'])-set(source['removed'])
    plan['per_call_widths']=[dict(stage=c['stage'],replica=c['replica'],time=c['time'],widths=providers[c['provider']]['widths']) for c in plan['provider_calls']]
    plan['metadata_scope']='Order/dispatch/width/profile are this candidate. Legacy native artifact fields copied from source are provisional and must be replaced by the native bridge before global admission.'
    geo=audit.geometry(plan,template,phases)
    frames,pending=audit.axes(geo,providers['gauge44']['ports'],phases)
    dispatch={(stage,replica):tag for stage,replica,tag in source_dispatch}
    index={tag:{r:i for i,r in enumerate(providers[tag]['origins'])} for tag in providers}
    fill=p.read(V/'new/borrow-fill/FILL.json.gz');p.need(fill['columns']==['time','helper','owner_replica','child','port','offset'] and fill['dispatch_overrides']==[],'fill schema')
    roles=[];bins=defaultdict(list)
    for time,helper,owner,child,port,offset in fill['rows']:
        stage,replica,tag=source_dispatch[time];origin=source_origins[tag][helper]
        if origin in (533,554):continue
        if origin in REPLACE:origin=REPLACE[origin]
        elif origin in replacement_sources[tag]:continue
        newhelper=index[tag][origin]
        row=dict(stage=stage,replica=replica,time=time,helper=newhelper,origin_helper=origin,
            owner_replica=owner,child=child,port=port,offset=offset,width=providers[tag]['widths'][newhelper],
            copy=112*owner+port,family=owner*8*112+(2*geo['pair'][child]+geo['side'][child])*112+port)
        roles.append(row);bins[owner,child,port].append(row)
    for entries in bins.values():
        offset=0
        for row in sorted(entries,key=lambda r:r['offset']):row['offset']=offset;offset+=row['width']
    roles.sort(key=lambda r:(r['time'],r['helper']))
    result=audit.audit(roles,geo,providers,dispatch,frames,pending)
    result['controls']=controls(audit,roles,geo,providers,dispatch,frames,pending)
    expected=p.integer_counter(p.read(p.HERE/'CONDITIONAL-SOURCE-FILL.json')['cases']['True']['profile'])
    p.need(result['profile']==expected,'screen profile binding')
    engine=load(p.ENGINE,'composed_owner_moment')
    endpoints={}
    for bad in (False,True):
        raw=engine.certify(result['profile'],73,66304,bad=bad)
        endpoints['inherited_bad' if bad else 'native_no_bad']={k:raw[k] for k in ('lower','upper','lower_endpoint_residual_upper','upper_endpoint_residual_lower')}
    write(p.HERE/'RESTRICTED-OWNERS.json.gz',roles)
    write(p.HERE/'RESTRICTED-PROFILE.json',result['profile']);write(p.HERE/'RESTRICTED-IDLE.json',result['idle'])
    plan['profile']=result['profile'];plan['assignment_sha256']=digest(p.HERE/'RESTRICTED-OWNERS.json.gz')
    plan['assignment_content_sha256']=hashlib.sha256(gzip.decompress((p.HERE/'RESTRICTED-OWNERS.json.gz').read_bytes())).hexdigest()
    plan['replica_lift']['owners_file_sha256']=plan['assignment_sha256']
    plan['source_plan_sha256']=digest(OLD/'parent/new/PLAN.json');plan['source_owners_sha256']=digest(V/'new/borrow-fill/FILL.json.gz')
    plan['status']='COMPOSED428_FORMAL_GEOMETRY_NATIVE_REBINDING_REQUIRED'
    plan['mode']='PR2435-order-six-role-replacement';plan['solver_status']='Literal six-role replacement and compacted residual prefixes; no search'
    write(p.HERE/'PLAN.json',plan)
    result.update(status='PASS_COMPOSED428_EXACT_LITERAL_WINDOWS_FAMILIES_AXES_PROFILE',
        base='7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261',seed=39,source_head='324d7d3590dc21003940a44cb0cbdc32b3620f25',
        plan_sha256=digest(p.HERE/'PLAN.json'),owner_sha256=digest(p.HERE/'RESTRICTED-OWNERS.json.gz'),
        profile_sha256=digest(p.HERE/'RESTRICTED-PROFILE.json'),idle_sha256=digest(p.HERE/'RESTRICTED-IDLE.json'),
        source_pins={str(path.relative_to(p.RESEARCH)):pin for path,pin in PINS.items()},
        geometry_source_pins=audit.PARENT_PINS,phase_sha256=audit.PHASE_PIN,
        checker_sha256=digest(Path(__file__)),endpoints=endpoints,replacements=REPLACE,
        attribution='Tekalign (@tekuuu), substantial OpenAI Codex assistance; PR2435 source order/packing/entrances by Jeremy Kothe (@jeremykothe2).',
        scope='Exact428 helper roles at each666 invocations; PR2435 event order and all strict bridge-aware windows independently reconstructed from source schedule; distinct families, active exclusion, whole widths, residual axes and full profile checked. Nine negative controls rejected. Formal local composition is bound. Native realization, global scalar/compiler replay, full physical invoice and modern outer transfer remain separate obligations.')
    (p.HERE/'RESTRICTED-VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status']);print(json.dumps(endpoints,indent=2));print('roles',result['roles'],'charts',result['unique_residual_spectator_charts'])

if __name__=='__main__':main()
