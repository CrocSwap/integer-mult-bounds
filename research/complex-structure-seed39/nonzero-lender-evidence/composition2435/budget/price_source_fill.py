#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Conditional source-packing cost screen; no owner or supplier admission."""
from collections import Counter,defaultdict
import importlib.util
import json
import price_composition as p

V=p.ROOT/'composition2435/vendor/new'
originals={};words={}
for tag,wordtag in (('gauge44','base'),('extra','extra')):
    words[tag]=p.read(V/f'borrow/words/BORROW-WORD-43{wordtag}.json.gz')
    originals[tag]=[r for r in range(224,704) if r not in words[tag]['removed']]
fill=p.read(V/'borrow-fill/FILL.json.gz')['rows']
dispatch=p.read(V/'borrow-fill/DISPATCH.json')
plan=p.read(p.RESEARCH/'anticipatory-stage-evidence/parent/new/PLAN.json')
conditional=p.read(p.HERE/'CONDITIONAL-LITERAL.json')
four=p.read(p.ROOT/'words/FOUR-base.json.gz')
neworig=[r for r in range(224,704) if r not in four['removed']]
width=lambda d,r:len(d['helper_final'].get(str(r),range(9)))-len(d['start_extra'].get(str(r),[]))
newwidth={r:width(four,r)-int(r in p.RAISED) for r in neworig}
replacement={640:533,641:554,606:619,635:621,637:622,638:623}
removed=set(four['removed'])-set(words['gauge44']['removed'])
spec=importlib.util.spec_from_file_location('source_fill_moment',p.ENGINE)
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
receipts={}
for candidate in (False,True):
    used=Counter();seen=defaultdict(set);demand=Counter()
    for time,helper,owner,child,port,offset in fill:
        tag=dispatch[time][2];r=originals[tag][helper]
        if candidate:
            if r in (533,554):continue
            if r in replacement:r=replacement[r]
            elif r in removed:continue
            w=newwidth[r]
        else:w=width(words[tag],r)
        p.need(r not in seen[time],'duplicate helper')
        seen[time].add(r);used[owner,child,port]+=w;demand[w]+=1
    p.need(all(s==set(neworig if candidate else originals[dispatch[t][2]]) for t,s in seen.items()),'helper coverage')
    idle=Counter()
    for key,(cap,_) in plan['windows'].items():
        owner,child=map(int,key.split(','))
        for port in range(112):
            rem=cap-used[owner,child,port]
            p.need(rem>=0,'capacity overflow')
            if rem:idle[rem]+=1
    H=Counter(idle)
    for _,_,tag in dispatch:
        paid=conditional['conditional_local_profiles'][tag] if candidate else words[tag]['report']['local_profile']
        H.update(p.integer_counter(paid))
    p.need(73*66304-sum(r*n for r,n in H.items())==23680,'rank deficit')
    bracket=engine.certify(dict(H),73,66304,bad=True)
    receipts[str(candidate)]=dict(root_lower=bracket['lower'],root_upper=bracket['upper'],
        idle=dict(sorted(idle.items())),profile=dict(sorted(H.items())),width_demand=dict(demand),
        replacements=replacement if candidate else {},helpers_per_call=len(next(iter(seen.values()))))
output=dict(status='PASS_CONDITIONAL_PR2435_SLOT_REPLACEMENT_COST_ONLY',cases=receipts,
    assumption=conditional['assumption'],
    scope='All helpers charged with their conditional width; six same-call replacement roles stay in old slots of at least their width; other retained slots unchanged. Complete bin padding and global profiles charged. No source pin enforcement, native word, chronological/family replay or outer admission in this exploratory screen.')
(p.HERE/'CONDITIONAL-SOURCE-FILL.json').write_text(json.dumps(output,indent=2)+'\n')
print(output['status']);print(json.dumps({k:{a:v[a] for a in ('root_lower','root_upper')} for k,v in receipts.items()},indent=2))
