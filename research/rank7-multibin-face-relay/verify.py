#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Primary exact literal owner check adapted from Richardson PR3010.

This implementation reuses its forward-event source/geometry checker with
explicit credit. independent.py supplies a separately written implementation.
No optimizer, source owner engine or constructor Python is imported.

Ross Richardson, with substantial OpenAI Codex assistance. Event/window and
owner-contract credit: Tekalign, Dumitrean, Hale, Lu and retained predecessors.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COLS = ['time', 'helper', 'owner_replica', 'child', 'port', 'offset']
WIDTHS = (4, 5, 6, 7, 8, 9)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def authenticate(root=ROOT):
    manifest = read(root / 'SOURCES.json')
    checked = {}
    for name, entry in manifest['exports'].items():
        digest = hashlib.sha256((root / name).read_bytes()).hexdigest()
        need(digest == entry['sha256'], 'source bytes: ' + name)
        checked[name] = digest
    return checked


def source_inputs(root=ROOT):
    source = root / 'sources'
    return (read(source / 'allocation/vendor/TEMPLATE.json.gz'),
            read(source / 'allocation/vendor/PLAN.json.gz'),
            read(source / 'allocation/PROVIDERS.json'))


def windows(order, template, plan):
    """Run the ordered source event blocks separately in each replica.

    Each local call closes the relevant stage block after its call. A pending
    child is available strictly after the last event touching its data pair,
    through the call that immediately precedes its own cover action.
    """
    T = len(order) // 9
    need(len(order) == 9*T and T > 0, 'call count')
    need(all(type(s) is int and type(r) is int for s,r in order), 'integer calls')
    need(set(map(tuple, order)) == {(s,r) for s in range(9) for r in range(T)},
         'call identities')
    local_pairs = {e['stage']: e['pair'] for e in template['recipe']
                   if e['kind'] == 'local'}
    ranks = {}
    ports = defaultdict(set)
    for row in template['idle_children']:
        c, p, rank = row['child'], row['port'], row['rank']
        need(c not in ranks or ranks[c] == rank, 'source rank consistency')
        need(p not in ports[c], 'duplicate source port')
        ranks[c] = rank
        ports[c].add(p)
    need(set(ranks) == set(range(18)), 'source retained children')
    need(all(p == set(range(112)) for p in ports.values()), 'source port coverage')
    blocks = {}
    stage = None
    for e in template['execution_schedule']:
        kind = e['kind']
        if kind in ('bank_padding_cover_sweep', 'translate_every_live_family'):
            continue
        if kind == 'local_cover_sweep':
            stage = e['stage']
            need(stage not in blocks, 'duplicate source stage')
            blocks[stage] = []
        need(stage is not None, 'event before source local')
        blocks[stage].append(e)
    need(set(blocks) == set(range(9)), 'source stages')
    progress = [0]*T
    touch = {}
    result = {}
    for t, (s,r) in enumerate(order):
        need(progress[r] == s, 'replica order')
        progress[r] += 1
        for e in blocks[s]:
            kind = e['kind']
            if kind == 'local_cover_sweep':
                touch[r,local_pairs[s]] = t
            elif kind == 'bridge':
                touch[r,e['src']] = touch[r,e['dst']] = t
            elif kind == 'idle_cover_sweep':
                lower = touch.get((r,e['pair']), -1)
                for c in e['child_indices']:
                    if c in ranks:
                        need((r,c) not in result, 'duplicate source window')
                        need(plan['pairs'][str(c)] == e['pair'], 'source pair')
                        need(lower < t, 'empty retained source window')
                        result[r,c] = (ranks[c],lower,t)
            else:
                need(kind in ('terminal_Y_translations','terminal'), 'unknown source event')
    need(progress == [9]*T and len(result) == 18*T, 'source progression')
    return result, local_pairs


def target_mix(k, root=ROOT):
    need(type(k) is int and 0 <= k <= 1063, 'face parameter')
    face = read(root / 'sources/construction/allocation/T37-FACE-MIX.json')
    need(face['widths'] == list(WIDTHS), 'source width order')
    target = Counter({(cap,tuple(q)):n for cap,q,n in face['target']})
    # Four stipulated changing multiplicities, independently read as full patterns.
    target[16,(0,0,0,0,2,0)] = 323+k
    target[16,(0,0,0,1,0,1)] = 16253-k
    target[32,(0,0,0,1,2,1)] = 1063-k
    target[32,(0,0,0,2,0,2)] = k
    return +target


def check(order, dispatch_rows, fill, k, template, plan, providers, root=ROOT):
    T = len(order)//9
    need(T in (37,74), 'covered replica count')
    scale = T//37
    win, active = windows(order,template,plan)
    need(len(dispatch_rows) == len(order), 'dispatch length')
    dispatch = {}
    for row in dispatch_rows:
        need(len(row) == 3 and type(row[0]) is int and type(row[1]) is int,
             'dispatch shape')
        s,r,pid = row
        need((s,r) not in dispatch and pid in providers, 'dispatch identities')
        dispatch[s,r] = pid
    need(set(dispatch) == set(map(tuple,order)), 'dispatch coverage')
    for v in providers.values():
        need(len(v['widths']) == 408 and Counter(v['widths']) ==
             Counter({4:26,5:2,6:16,7:52,8:99,9:213}), 'source ordered widths')
    need(fill['columns'] == COLS, 'role columns')
    need(fill.get('dispatch_overrides',[]) == [], 'fixed provider interface')
    rows = fill['rows']
    need(len(rows) == len(order)*408, 'role count')
    roles = [set() for _ in order]
    families = [set() for _ in order]
    bybin = defaultdict(list)
    cut_counts = Counter()
    for row in rows:
        need(len(row) == 6 and all(type(x) is int for x in row), 'integer role')
        t,h,r,c,p,z = row
        need(0 <= t < len(order) and 0 <= h < 408 and 0 <= p < 112 and
             (r,c) in win, 'role bounds')
        cap,L,U = win[r,c]
        need(L < t <= U, 'source window')
        need(h not in roles[t], 'duplicate helper')
        roles[t].add(h)
        s,caller = order[t]
        pair,side = plan['pairs'][str(c)],plan['sides'][str(c)]
        family = (r,pair,side,p)
        need(not (r == caller and pair == active[s]), 'active data family')
        need(family not in families[t], 'repeated physical family')
        families[t].add(family)
        w = providers[dispatch[s,caller]]['widths'][h]
        need(0 <= z and z+w <= cap, 'capacity')
        bybin[r,c,p].append((z,w,t,h))
        base_t = t//scale
        if w == 7 and 45 <= base_t <= 332:
            cut_counts['cap16' if cap == 16 else 'other'] += 1
    need(all(len(v) == 408 for v in roles), 'complete helpers')
    actual = Counter()
    idle = Counter()
    for (r,c),(cap,L,U) in win.items():
        for p in range(112):
            occupied = sorted(bybin.get((r,c,p),[]))
            q = Counter()
            end = 0
            for z,w,t,h in occupied:
                need(z >= end, 'coordinate overlap')
                need(z == end, 'noncompact prefix')
                end += w
                q[w] += 1
            actual[cap,tuple(q[w] for w in WIDTHS)] += 1
            if end < cap:
                idle[cap-end] += 1
    expected = Counter({key:n*scale for key,n in target_mix(k,root).items()})
    need(actual == expected, 'exact face pattern mix')
    profile = Counter(idle)
    for s,r in order:
        profile.update({int(rank):n for rank,n in
                        providers[dispatch[s,r]]['actual_paid_profile'].items()})
    source_profile = read(root / 'sources/allocation/PROFILE.json')
    need(Counter({rank:n*2//scale for rank,n in profile.items()}) ==
         Counter({int(rank):n for rank,n in source_profile.items()}), 'complete paid profile')
    need(sum(rank*n for rank,n in profile.items()) == 65088*T, 'rank mass')
    if k == 473:
        need(cut_counts == Counter(cap16=13440*scale,other=1536*scale),
             'saturated boundary cut')
    return {'replicas':T,'calls':len(order),'roles':len(rows),
            'windows':len(win),'bins':112*len(win),'k':k,
            'local_and_idle_profile':dict(sorted(profile.items())),
            'idle_profile':dict(sorted(idle.items())),
            'rank_mass':65088*T,'cut_width7':dict(cut_counts),
            'namespace_count_conditional':896*T+408+8+91+2,
            'namespace_is_not_physical_execution':True}


def double(order,dispatch,fill):
    doubled_order = [[s,r+37*b] for s,r in order for b in (0,1)]
    bycall = {(s,r):pid for s,r,pid in dispatch}
    doubled_dispatch = [[s,r+37*b,bycall[s,r]] for s,r in order for b in (0,1)]
    rows = [[2*t+b,h,r+37*b,c,p,z] for t,h,r,c,p,z in fill['rows'] for b in (0,1)]
    return doubled_order,doubled_dispatch,{'columns':COLS,'rows':rows}


def relay(candidate, order, dispatch, fill, k, template, plan, providers, root=ROOT,
          journal_override=None):
    """Replay the finite journal without invoking its constructor.

    A stage is an offline reassignment certificate, not a claim that moving
    arithmetic data at runtime is free. Every stage endpoint has full geometry.
    """
    journal = journal_override if journal_override is not None else read(candidate/'JOURNAL.json')
    start = read(root/'start/FILL.json.gz')
    need(order == read(root/'start/ORDER.json') and
         dispatch == read(root/'start/DISPATCH.json'), 'relay fixed start chronology')
    need(journal['start_k'] == 940 and journal['end_k'] == k == 939,
         'relay face endpoints')
    need(journal['columns'] == COLS and len(journal['stages']) == 3,
         'relay journal structure')
    check(order,dispatch,start,940,template,plan,providers,root)
    state = {tuple(row[:2]):list(row) for row in start['rows']}
    initial = deepcopy(state)
    need(len(state) == 135864, 'relay complete initial identities')
    disp = {(s,r):pid for s,r,pid in dispatch}
    def width(role):
        t,h = role
        return providers[disp[tuple(order[t])]]['widths'][h]
    stage_results = []
    transfers_count = 0
    for i, stage in enumerate(journal['stages']):
        need(stage['name'] == ('same_width_7','same_width_9','inverse_face_swap')[i],
             'relay stage order')
        old = deepcopy(state)
        changed = set()
        for field in ('transfers','repacked_stationary'):
            for item in stage[field]:
                role = tuple(item['role'])
                need(role in state and role not in changed, 'relay unique stage role')
                need(state[role] == item['before'], 'relay stage before binding')
                need(item['after'][:2] == list(role), 'relay immutable helper identity')
                if field == 'transfers':
                    need(width(role) == item['width'], 'relay declared width')
                    need(item['before'][2:5] != item['after'][2:5], 'relay actual transfer')
                    transfers_count += 1
                else:
                    need(item['before'][2:5] == item['after'][2:5], 'relay stationary owner')
                changed.add(role)
                state[role] = list(item['after'])
        need(all(old[x] == state[x] for x in state if x not in changed),
             'relay unlisted roles unchanged')
        stage_k = 940 if i < 2 else 939
        stage_result = check(order,dispatch,{'columns':COLS,'rows':list(state.values())},
                             stage_k,template,plan,providers,root)
        stage_results.append({'name':stage['name'],'k':stage_k,
                              'transfers':len(stage['transfers']),
                              'roles_checked':stage_result['roles'],
                              'profile':stage_result['local_and_idle_profile']})
    need(state == {tuple(row[:2]):row for row in fill['rows']}, 'relay final literal binding')
    moved = {x for x in state if initial[x][2:5] != state[x][2:5]}
    shifted = {x for x in state if initial[x] != state[x] and x not in moved}
    need(len(moved) == 6 and transfers_count == 8, 'relay transfer counts')
    for field,expected in (('moves',moved),('repacked_stationary',shifted)):
        items = journal[field]
        need(len(items) == len(expected) and {tuple(x['role']) for x in items} == expected,
             'relay endpoint journal coverage')
        for item in items:
            role = tuple(item['role'])
            need(item['before'] == initial[role] and item['after'] == state[role],
                 'relay endpoint journal binding')
            if field == 'moves':
                need(item['width'] == width(role) and
                     item['before_bin'] == initial[role][2:5] and
                     item['after_bin'] == state[role][2:5], 'relay endpoint move fields')
    win,_ = windows(order,template,plan)
    changed_bins = {tuple(row[2:5]) for role in moved for row in (initial[role],state[role])}
    need(len(changed_bins) == 4 and all(win[b[:2]][0] != 48 for b in changed_bins),
         'relay four bins without capacity48')
    before_load = Counter()
    after_load = Counter()
    for role in initial:
        before_load[tuple(initial[role][2:5])] += width(role)
        after_load[tuple(state[role][2:5])] += width(role)
    need(before_load == after_load, 'relay every occupied bin load unchanged')
    need(len(journal['bin_states']) == 4 and
         {tuple(x['bin']) for x in journal['bin_states']} == changed_bins,
         'relay bin state coverage')
    for item in journal['bin_states']:
        b = tuple(item['bin']); cap,lo,hi = win[b[:2]]
        need(item['capacity'] == cap and item['window'] ==
             {'lower_open':lo,'upper_closed':hi}, 'relay displayed source windows')
        need(sorted(item['before']) == sorted(row for row in initial.values() if tuple(row[2:5]) == b)
             and sorted(item['after']) == sorted(row for row in state.values() if tuple(row[2:5]) == b),
             'relay displayed bin states')
    meta = read(candidate/'META.json')
    manifest = read(root/'SOURCES.json')
    need(meta['k'] == 939 and meta['T'] == 37 and meta['moves'] == 6 and
         meta['staged_transfers'] == 8 and meta['changed_bins'] == 4 and
         meta['capacity48_bins_changed'] == 0 and meta['private_buffers'] == 91 and
         meta['conditional_stock'] == 33661 and meta['no_new_kappa'] is True and
         meta['cost_delta_for_every_rank_tariff'] == 0, 'relay metadata counts')
    need(meta['base_commit'] == manifest['base_commit'] and
         meta['source_commit'] == manifest['source_commit'] and
         meta['start_reference'] == {'commit':manifest['predecessor_commit'],
         'path':'start/FILL.json.gz','sha256':hashlib.sha256((root/'start/FILL.json.gz').read_bytes()).hexdigest(),
         'k':940}, 'relay metadata pins')
    final = stage_results[-1]['profile']
    need({int(r):n for r,n in meta['profile'].items()} == final and
         meta['rank_mass'] == sum(r*n for r,n in final.items()), 'relay metadata invoice')
    patterns = read(candidate/'PATTERNS.json')
    need(patterns['T'] == 37 and patterns['k'] == k and patterns['widths'] == list(WIDTHS)
         and Counter({(cap,tuple(q)):n for cap,q,n in patterns['target']}) == target_mix(k,root),
         'relay pattern certificate')
    return {'start_k':940,'end_k':939,'distinct_owner_moves':6,'staged_transfers':8,
            'changed_bins':4,'every_bin_load_unchanged':True,'stages':stage_results}


def verify(candidate, root=ROOT, controls=True, k=473):
    pins = authenticate(root)
    candidate_hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in candidate.iterdir() if p.is_file()}
    template,plan,providers = source_inputs(root)
    order = read(candidate/'ORDER.json')
    dispatch = read(candidate/'DISPATCH.json')
    fill = read(candidate/'FILL.json.gz')
    args = (k,template,plan,providers,root)
    first = check(order,dispatch,fill,*args)
    if (candidate/'PROFILE.json').exists():
        need({int(k):n for k,n in read(candidate/'PROFILE.json').items()} ==
             first['local_and_idle_profile'], 'candidate profile binding')
    if (candidate/'PROVIDERS.json').exists():
        need(read(candidate/'PROVIDERS.json') == providers, 'candidate provider binding')
    O,D,F = double(order,dispatch,fill)
    need(O == read(root/'sources/allocation/ORDER.json'), 'source T74 order embedding')
    need(D == read(root/'sources/allocation/DISPATCH.json'), 'source T74 provider embedding')
    second = check(O,D,F,*args)
    journal_result = relay(candidate,order,dispatch,fill,k,template,plan,providers,root)
    rejected = []

    def reject(name,call,reason):
        try:
            call()
        except ValueError as exc:
            need(str(exc) == reason, 'wrong defect rejection: '+name+': '+str(exc))
            rejected.append(name)
        else:
            raise ValueError('accepted defect: '+name)

    def change(index,replacement):
        rows = list(fill['rows'])
        rows[index] = replacement
        return {**fill,'rows':rows}

    if controls:
        reject('missing helper',lambda:check(order,dispatch,{**fill,'rows':fill['rows'][:-1]},*args),'role count')
        a = fill['rows'][0]
        j = next(i for i,r in enumerate(fill['rows'][1:],1) if r[0] == a[0])
        b = list(fill['rows'][j]); b[1] = a[1]
        reject('duplicate helper',lambda:check(order,dispatch,change(j,b),*args),'duplicate helper')
        win,_ = windows(order,template,plan)
        bad = list(a)
        owner,child = next(key for key,(_,lo,hi) in win.items() if not lo < a[0] <= hi)
        bad[2:4] = owner,child
        reject('unavailable source',lambda:check(order,dispatch,change(0,bad),*args),'source window')
        bad = list(fill['rows'][j]); bad[2:5] = a[2:5]
        reject('same call physical family',lambda:check(order,dispatch,change(j,bad),*args),'repeated physical family')
        bad = list(a); bad[5] = 48
        reject('capacity overflow',lambda:check(order,dispatch,change(0,bad),*args),'capacity')
        other_k = k+1 if k < 1063 else k-1
        reject('wrong face member',lambda:check(order,dispatch,fill,other_k,template,plan,providers,root),'exact face pattern mix')
        bybin = defaultdict(list)
        for i,row in enumerate(fill['rows']):
            bybin[tuple(row[2:5])].append((row[5],i))
        multi = next(sorted(items) for items in bybin.values() if len(items) >= 2)
        z,index = multi[1]
        bad = list(fill['rows'][index]); bad[5] = multi[0][0]
        reject('overlapping coordinates',lambda:check(order,dispatch,change(index,bad),*args),'coordinate overlap')
        # Shift the last role of an unfilled bin, retaining legal capacity but
        # leaving an unpriced gap in the required compact child prefix.
        for (r,c,p),items in bybin.items():
            z,index = max(items)
            t,h,_,_,_,_ = fill['rows'][index]
            w = providers[dict(((s,r),pid) for s,r,pid in dispatch)[tuple(order[t])]]['widths'][h]
            if z+w < win[r,c][0]:
                bad = list(fill['rows'][index]); bad[5] += 1
                break
        else:
            raise ValueError('no prefix-gap defect fixture')
        reject('unpaid prefix gap',lambda:check(order,dispatch,change(index,bad),*args),'noncompact prefix')
        noninteger = list(a); noninteger[5] = float(noninteger[5])
        reject('fractional mask representation',lambda:check(order,dispatch,change(0,noninteger),*args),'integer role')
        # The strict source lower endpoint remains excluded even if all other
        # row fields and total width counts are retained.
        index,row = next((i,r) for i,r in enumerate(fill['rows']) if win[r[2],r[3]][1] >= 0)
        bad = list(row); bad[0] = win[row[2],row[3]][1]
        reject('open lower endpoint',lambda:check(order,dispatch,change(index,bad),*args),'source window')
        bad_providers = deepcopy(providers)
        for p in bad_providers.values():
            p['actual_paid_profile']['1'] += 1
        reject('unpaid local child',lambda:check(order,dispatch,fill,k,template,plan,bad_providers,root),'complete paid profile')
        bad_journal = read(candidate/'JOURNAL.json')
        bad_journal['stages'][0]['transfers'][0]['width'] += 1
        reject('relay width lie',lambda:relay(candidate,order,dispatch,fill,k,template,plan,providers,root,bad_journal),
               'relay declared width')
        bad_journal = read(candidate/'JOURNAL.json')
        bad_journal['stages'][1]['transfers'][0]['before'][5] += 1
        reject('relay false intermediate offset',lambda:relay(candidate,order,dispatch,fill,k,template,plan,providers,root,bad_journal),
               'relay stage before binding')
    need(authenticate(root) == pins, 'source drift')
    need(candidate_hashes == {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in candidate.iterdir() if p.is_file()}, 'candidate drift')
    return {'status':'PASS_RANK7_MULTIBIN_RELAY_LITERAL','T37':first,'T74':second,
            'relay':journal_result,
            'controls_rejected':rejected,'source_hashes':pins,
            'candidate_hashes':candidate_hashes,
            'scope':'Finite literal owner geometry conditional on ordered native widths and source local costs; no native/dirty restoration, phase, physical storage, precision, outer, all-size, formal-kernel or new-kappa claim.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate',type=Path,default=ROOT/'candidate')
    ap.add_argument('--k',type=int,default=939)
    ap.add_argument('--out',type=Path)
    ap.add_argument('--check-result',action='store_true')
    a = ap.parse_args()
    result = verify(a.candidate,k=a.k)
    if a.check_result:
        need(read(ROOT/'RESULT.json') == json.loads(json.dumps(result)), 'stored result')
    text = json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.out:
        a.out.write_text(text)
    print(text,end='')


if __name__ == '__main__':
    main()
