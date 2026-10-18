#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Concrete complete-width owner packing in inherited selected idle windows.

This checks 527 ordinary roles in each of 144 calls on retained P104 data
families. It does not emit or admit a new 104-port global wrapper. The stored
T8 data-owner routes are lifted into two disjoint replica banks solely to
check active-data exclusion. Native wrapper maps, the restricted data phases,
backward supplier and recursive accounting remain separate obligations.

Schedule and frozen owner inputs: Rohan Arun's T16 rare-pattern exchanges,
following jeremykothe2's PR1087, FanPUYen's PR858 and the retained lineage.
Their source archive and notices are reused unchanged, not reauthored here.
"""
from collections import Counter, defaultdict
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 'research/complex-t16-rare-pattern-exchanges/'
INPUTS = {
    'plan': (BASE+'data/PLAN.json','7bd786ba8e66408f02aa9ef446eaf20c1bfe981ea2e4dd1e5a929f0aa7767bc0'),
    'owners': (BASE+'data/OWNERS.json.gz','87902c528dfab7d503dcf8a784260e3ab6fb7424c418a1820f7261f25be7b6bc'),
    'spec': (BASE+'data/SPEC.json','8cb51f25a5da4a29d3783853025b73ff1f452429d4fdb30c599e598bcab0e71d'),
    'archive': (BASE+'upstream1087.tar.gz','d4acf04daef85d4514f80ec5fcd2492d0c60e5d6c49fa71b3e6523f8db2dea86'),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def module(name):
    spec = importlib.util.spec_from_file_location('p104_hosting_'+name,HERE/(name+'.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def verify(fanout_report=None):
    qc = module('query_construction')
    word = qc.load_inputs()['word']
    if fanout_report is None:
        fanout_report = module('fanout').verify()
    require(fanout_report['full_735_column_identity_verified'], 'missing complete forward receipt')
    require(fanout_report['ordinary_fanout_helpers'] == 31, 'unexpected fanout inventory')
    raw = {}
    for name,(path,expected) in INPUTS.items():
        raw[name] = (ROOT/path).read_bytes()
        require(hashlib.sha256(raw[name]).hexdigest()==expected,'hosting source drift: '+path)
    plan, owners, spec = json.loads(raw['plan']),json.loads(gzip.decompress(raw['owners'])),json.loads(raw['spec'])
    with tarfile.open(fileobj=io.BytesIO(raw['archive']),mode='r:gz') as archive:
        member = archive.extractfile('evidence/global/GLOBAL-TEMPLATE.json.gz')
        require(member is not None,'missing inherited data routing template')
        template_bytes = gzip.decompress(member.read())
    template = json.loads(template_bytes)
    require(len(template['calls'])==72 and template['live']==7168,'inherited T8 data stock')
    old_calls = {(c['stage'],c['replica']):c for c in template['calls']}
    require(len(old_calls)==72,'duplicate inherited calls')
    order = [tuple(x) for x in plan['order']]
    require(len(order)==144 and set(order)=={(s,r)for s in range(9)for r in range(16)},'T16 call coverage')
    old_widths = [len(word['frames'][word['final'][r]])-len(word['frames'][word['start'][r]])
                  for r in range(224,704)]
    require(old_widths==spec['providers']['gauge44']['complete_contract']['widths'],'selected width binding')
    require(INPUTS['owners'][1]==spec['data']['owners_sha256'],'selected owner binding')
    complete = fanout_report['complete_public_widths']
    require(len(complete)==735 and all(type(w)is int and 0<=w<=9 for w in complete),'public width vector')
    removed = set(qc.REMOVED)
    registers = list(range(224,704))+list(qc.REMOVED)+[112+i for i in qc.REMOVED]+list(range(704,735))
    widths = [complete[r] for r in registers]
    require(len(widths)==527 and widths[480:]==[9]*47,'whole helper lifetimes')
    require(sum(widths[:480])-sum(old_widths)==21,'existing helper width growth must be charged')
    for i in range(112):
        if i not in removed:
            require(complete[i]==complete[112+i]==8,'live data boundary width changed')
    bins, bykey, bytime = [],{},defaultdict(list)
    for key,(rank,times) in plan['windows'].items():
        replica,child = map(int,key.split(','))
        group = 2*int(plan['pairs'][str(child)])+int(plan['sides'][str(child)])
        for port in range(112):
            if port in removed:
                continue
            index = len(bins)
            bins.append(dict(replica=replica,child=child,port=port,rank=rank,times=set(times),
                             family=replica*896+group*112+port))
            bykey[replica,child,port] = index
            for time in times:
                bytime[time].append(index)
    free = [b['rank']for b in bins]
    assignments, families = {},[set()for _ in order]
    retained = 0
    for owner in owners:
        h = owner['helper']
        if owner['port'] in removed or widths[h]!=old_widths[h]:
            continue
        time = owner['time']
        bi = bykey[owner['owner_replica'],owner['child'],owner['port']]
        b = bins[bi]
        require(time in b['times'] and b['family'] not in families[time],'retained owner conflict')
        require((time,h)not in assignments,'duplicate retained role')
        assignments[time,h] = bi
        families[time].add(b['family'])
        free[bi] -= widths[h]
        require(free[bi]>=0,'retained width exceeds idle child')
        retained += 1
    # A fixed deterministic completion, not a search dependency or a claim of
    # packing optimality. Preserve unchanged old placements; fill narrowest
    # compatible residual bins with largest missing complete roles first.
    for time in sorted(range(144),key=lambda t:(len(bytime[t]),t)):
        missing = [h for h in range(527)if(time,h)not in assignments]
        for h in sorted(missing,key=lambda h:(-widths[h],h)):
            options = [bi for bi in bytime[time] if free[bi]>=widths[h] and bins[bi]['family']not in families[time]]
            require(bool(options),'deterministic complete-role packing failed')
            bi = min(options,key=lambda i:(free[i]-widths[h],len(bins[i]['times']),i))
            assignments[time,h] = bi
            free[bi] -= widths[h]
            families[time].add(bins[bi]['family'])
    slots = defaultdict(list)
    for (time,h),bi in assignments.items():
        slots[bi].append((time,h))
    literal = []
    for bi,roles in sorted(slots.items()):
        b, offset = bins[bi],0
        for time,h in sorted(roles):
            stage,replica = order[time]
            require(time in b['times'],'complete invocation outside owner window')
            require(offset+widths[h]<=b['rank'],'owner rank interval exceeds idle child')
            literal.append(dict(stage=stage,replica=replica,time=time,helper=h,width=widths[h],
                                owner_replica=b['replica'],child=b['child'],port=b['port'],
                                old_family_label=b['family'],offset=offset))
            offset += widths[h]
        require(b['rank']-offset==free[bi],'residual width recount')
    require(len(literal)==144*527==75888,'whole-role assignment coverage')
    for time,(stage,replica) in enumerate(order):
        require(len(families[time])==527,'one physical family serves two roles in a call')
        old = old_calls[stage,replica%8]
        active = {family+(replica//8)*7168 for family,route in old['owners'][:224]}
        require(len(active)==224,'inherited active-data owner count')
        require(not active.intersection(families[time]),'helper owner is active data in its call')
    idle = Counter(r for r in free if r)
    idle_mass = sum(r*n for r,n in idle.items())
    require(idle_mass==144*818==117792,'complete-width residual mass')
    require(sum(complete)==fanout_report['public_rank_mass']==5838,'monotone public width invoice')
    require(idle_mass+144*(5838+56)==144*6712,'full coverage identity')
    return dict(schema='p104-conditional-owner-window-packing-v1',
                scope='Concrete complete-role packing in inherited selected windows on retained P104 DATA families. New global emitter, phase routing, native wrappers, backward interface and recursive admission are not supplied.',
                sources=[dict(path=p,sha256=s)for p,s in INPUTS.values()],
                inherited_template_member_sha256=hashlib.sha256(template_bytes).hexdigest(),
                total_calls=144,ordinary_helpers=527,assigned_roles=75888,retained_old_placements=retained,
                actual_ordinary_registers=registers,actual_ordinary_widths_sha256=digest(widths),
                complete_public_widths_sha256=digest(complete),assignment_sha256=digest(literal),
                existing_helper_width_increase=21,retained_live_families=13312,
                remaining_idle_profile={str(r):n for r,n in sorted(idle.items())},
                idle_rank_mass=idle_mass,per_call_idle_rank_mass='818',
                all_complete_role_widths_checked=True,whole_call_window_membership_roles=75888,
                within_bin_overlaps=0,active_data_aliases=0,per_call_owner_family_aliases=0,
                live_data_boundaries_unchanged=True,removed_family_labels_used=0,
                global_emitter_admitted=False,new_native_wrappers_verified=False,
                optimal_packing_claimed=False,new_kappa_gain_certified=False)


if __name__=='__main__':
    print(json.dumps(verify(),indent=2,sort_keys=True))
