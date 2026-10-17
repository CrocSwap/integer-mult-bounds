#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Rebuild the 428-helper restriction and replay its full finite owner geometry.

Prepared for Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
No new global scalar/compiler, physical invoice or outer admission claim.
"""
import argparse
from collections import Counter, defaultdict
import copy
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import price

HERE=Path(__file__).resolve().parent
OLD=price.OLD
PINS={
    'parent/OWNERS.json.gz':'5a8c9a18c21f635563c9a6b6a433bcb1e804175ef23d677459033344aa2bd4e6',
    'parent/new/PLAN.json':'bf1abd33c8ba946371cae37e021747343ef6603a31297bcc962197cc23f535e2',
    'parent/new/borrow/words/BORROW-WORD-43base.json.gz':'9492a5537fb87d9ca98dffcd0230f7625b3789744fa94e2f18acf23d91d998b5',
    'parent/new/borrow/words/BORROW-WORD-43extra.json.gz':'87d51f5298101d5947f45c43ee02f0ec45d6acbddabb808d0d02db1eaf063734',
    'vendor/pr2339/inputs/gauge44.canonical.json.gz':'65c6d17ffee2eacf27bff438f37fc549c9ed0c909cbc7a52976cc75cf2d15b91',
    'vendor/pr2339/inputs/extra.canonical.json.gz':'d7e48dcbafa236a2e1e41f7958244211506f7c7630fe6a2d43d2bdf17b7ae015',
    'owners/check_owners.py':'5f9512a49a633d04d79b830b5c4e9179a68df3f3b2edcb056306404f25b93c43',
    'budget/verify_nine_capacity.py':'a9a465cfdaca7a12d0b7e93f6e1b8b9badf4269fffe48934dec5c1353c3e36a4',
}


def need(ok,msg):
    if not ok:raise ValueError(msg)


def main():
    need(__debug__,'Optimized Python unsupported by inherited exact engines')
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);args=ap.parse_args()
    price.pin(HERE/'price.py','76f6b7c9d8fdfbf3c86726e2c34f5a13129717511e04876494bda94979474a1a')
    for name,pin in PINS.items():price.pin(OLD/name,pin)
    price.pin(HERE/'../FOUR-CANDIDATE.json','71dd95ccf4d8ef2e0122befc14ab17a1703bff3e6f2eafe23068dc7e7ca5e80f')
    price.pin(HERE/'RESTRICTED-OWNERS.json.gz','cbc1b15a63288d64432d0548774b83526ae1d196b5a6594c0d8f0f4f0418d847')
    audit=price.load(OLD/'owners/check_owners.py','restricted_geometry')
    # The retained geometry and axis functions are cardinality-parametric.
    # Do not use its old local() routine, which assumes zero target COPY levels.
    audit.R=428
    for name,pin in audit.PARENT_PINS.items():price.pin(OLD/'parent'/name,pin)
    price.pin(OLD/'owners/DATA-PHASES.json',audit.PHASE_PIN)
    plan=price.read(OLD/'parent/new/PLAN.json');oldroles=price.read(OLD/'parent/OWNERS.json.gz')
    template=price.read(OLD/'parent/GLOBAL-TEMPLATE.json.gz');phases=price.read(OLD/'owners/DATA-PHASES.json')
    need(template['exact_data_phase_recipe_sha256']==audit.PHASE_PIN,'phase binding')
    rows={r['provider']:r for r in price.read(HERE/'../FOUR-CANDIDATE.json')['cases'] if r['baseline']=='high48'}
    providers={};meta={};removed={}
    for tag,wordtag in (('gauge44','base'),('extra','extra')):
        row=rows[tag]
        need(row['status']=='PASS_FORMAL_FOUR_LIFTED_TARGET_ALIASES_NO_NATIVE_OR_GLOBAL_ADMISSION','formal candidate status')
        oldword=price.read(OLD/f'parent/new/borrow/words/BORROW-WORD-43{wordtag}.json.gz')
        origins=[r for r in range(224,704) if r not in oldword['removed']]
        gone={p['register'] for p in row['witness']['pairs']}
        kept=[r for r in origins if r not in gone]
        removed[tag]=[r for r in origins if r in gone]
        need(len(origins)==437 and len(kept)==428 and removed[tag]==[606,635,637,638,639,640,641,642,644],'removed helper identity')
        original=price.read(OLD/f'vendor/pr2339/inputs/{tag}.canonical.json.gz')
        final={r['register']:len(original['frames'][r['frame']]) for r in row['replay']['exact_cold_restoration']}
        widths={r:final.get(r,9)-len(original['frames'][original['start'][r]]) for r in kept}
        oldwidth=dict(zip(origins,plan['provider_registry'][tag]['widths']))
        need(all(oldwidth[r]==widths[r] for r in kept),'retained helper width changed')
        need(dict(Counter(widths.values()))=={int(w):n for w,n in row['width_inventory'].items()},'candidate width inventory')
        need(row['local_profile']==row['replay']['local_profile'],'candidate profile binding')
        providers[tag]=dict(widths=[widths[r] for r in kept],origins=kept,ports=original['ports'],paid=Counter({int(r):n for r,n in row['local_profile'].items()}))
        meta[tag]=(origins,set(kept),{r:i for i,r in enumerate(kept)})
    dispatch={(c['stage'],c['replica']):c['provider'] for c in plan['provider_calls']}
    rebuilt=[];bins=defaultdict(list)
    for old in oldroles:
        origins,kept,indices=meta[dispatch[old['stage'],old['replica']]]
        origin=origins[old['helper']]
        if origin not in kept:continue
        row=dict(old);row['helper']=indices[origin];row['origin_helper']=origin
        rebuilt.append(row);bins[row['child'],row['owner_replica'],row['port']].append(row)
    for entries in bins.values():
        offset=0
        for row in sorted(entries,key=lambda r:r['offset']):row['offset']=offset;offset+=row['width']
    need(rebuilt==price.read(HERE/'RESTRICTED-OWNERS.json.gz'),'literal restriction differs')
    need(providers['gauge44']['ports']==providers['extra']['ports']==plan['provider_registry']['gauge44']['ports'],'port order')
    geo=audit.geometry(plan,template,phases)
    frames,pending=audit.axes(geo,providers['gauge44']['ports'],phases)
    receipt=audit.audit(rebuilt,geo,providers,dispatch,frames,pending)
    receipt['status']='PASS_428_HELPER_LITERAL_RESTRICTION_WINDOWS_AXES_PROFILE_AND_EXACT_COST'
    need(receipt['profile']=={int(r):n for r,n in price.read(HERE/'RESTRICTED-PROFILE.json').items()},'global profile differs')
    need(receipt['idle']=={int(r):n for r,n in price.read(HERE/'RESTRICTED-IDLE.json').items()},'residual profile differs')
    controls=[]
    for label,key,value,reason in (
        ('changed width','width',rebuilt[0]['width']+1,'whole native helper width'),
        ('changed time','time',rebuilt[0]['time']+1,'owner invocation time'),
        ('changed offset','offset',73,'slice capacity'),
    ):
        bad=[dict(x) for x in rebuilt];bad[0][key]=value
        try:audit.audit(bad,geo,providers,dispatch,frames,pending)
        except ValueError as exc:need(str(exc)==reason,'wrong owner mutation reason')
        else:raise ValueError('owner mutation accepted')
        controls.append(label)
    v=price.load(OLD/'budget/verify_nine_capacity.py','restricted_cost')
    engines={}
    for filename,pin in v.ENGINES.items():
        price.pin(v.INHERITED/filename,pin);engine=price.load(v.INHERITED/filename,'restricted_'+filename[:-3])
        cost={r:v.E(r,price.B,engine) for r in receipt['profile']}
        lo=sum(n*cost[r][0] for r,n in receipt['profile'].items())-23680
        hi=sum(n*cost[r][1] for r,n in receipt['profile'].items())-23680
        need(hi<0,'primitive-rate moment not below one')
        engines[filename]=dict(excess_minus_deficit=v.iv(lo,hi),moment=v.iv(1+lo/(73*66304),1+hi/(73*66304)))
    receipt.update(removed_original_helpers=removed,controls=controls,rate=str(price.B),engines=engines,pins=PINS,
                   owner_sha256=price.digest(HERE/'RESTRICTED-OWNERS.json.gz'),candidate_sha256=price.digest(HERE/'../FOUR-CANDIDATE.json'),
                   scope='Actual four-alias formal profile with inherited owner families, independently reconstructed strict event windows, orthogonal pending axes, residual charts and exact total rank profile. Native/global scalar equivalence, phase binding, 76 private zero-buffer physical reservations, full finite invoice and current outer transfer remain separate required obligations. No new kappa is certified.')
    if args.out:args.out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status']);print(engines['moment.py']['excess_minus_deficit']['decimal_upper_approx'])


if __name__=='__main__':main()
