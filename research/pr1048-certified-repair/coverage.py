#!/usr/bin/env python3
"""Bounded literal transport coverage; no legacy enumerator is an authority.

Brian Ross with substantial OpenAI Codex assistance, Apache-2.0.
Builds on flemhhh's PR1048 and DreamingOfClouds' PR589. Negative controls
adapt the semantic falsification methodology associated with Brian Ross/Krenn;
they do not attribute the underlying mathematics or supplier to this repair.

Every frame is identified by its root-line mask, every operation by its
original (section,index). The domain is the 636 original catalogue frames plus
the rational span closure of each slot's lower bound. It does not enumerate
all possible subspaces. Literal slots are retained, including transports with
unchanged register itineraries. No equal-profile continuation pruning occurs.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import copy
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
FIRST = (('A', 2028), ('A', 2076), ('A', 2129), ('A', 281), ('B', 1))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def basis(vectors):
    """Reduced row basis over Q, independent of the modular tuner geometry."""
    pivots = {}
    for v in vectors:
        v = list(map(Fraction, v))
        for p, row in sorted(pivots.items()):
            c = v[p]
            if c:
                v = [x-c*y for x, y in zip(v, row)]
        p = next((j for j, x in enumerate(v) if x), None)
        if p is not None:
            c = v[p]
            pivots[p] = [x/c for x in v]
    return pivots


class Frames:
    def __init__(self, word):
        self.lines = word['lines']
        self.original = tuple(sum(1 << j for j in f) for f in word['frames'])
        self.dims = {m: len(basis(self.vectors(m))) for m in self.original}
        self.closures = {}
        self.full = (1 << len(self.lines))-1

    def vectors(self, mask):
        return [v for j, v in enumerate(self.lines) if mask >> j & 1]

    def closure(self, mask):
        if mask in self.closures:
            return self.closures[mask]
        b = basis(self.vectors(mask))
        out = 0
        for j, raw in enumerate(self.lines):
            v = list(map(Fraction, raw))
            for p, row in sorted(b.items()):
                c = v[p]
                if c:
                    v = [x-c*y for x, y in zip(v, row)]
            if not any(v):
                out |= 1 << j
        self.closures[mask] = out
        self.dims[out] = len(b)
        return out


class State:
    def __init__(self, word, frames):
        self.word, self.frames = word, frames
        fm = frames.original
        self.start = [fm[x] for x in word['start']]
        self.final = [fm[x] for x in word['final']]
        self.sections = {s: [(fm[f], t, u, (s, i))
                             for i, (f, t, u) in enumerate((f, t, u)
                                  for f, t, us in word[s] for u in us)] for s in 'AB'}
        self.cp = {}
        after_d = list(self.start)
        for f, t, us in word['D']:
            for r in (t, *us):
                after_d[r] = fm[f]
        for r in word['ret']:
            self.cp[r] = next((f for f, t, u, _ in reversed(self.sections['A'])
                               if r in (t, u)), after_d[r])

    def clone(self):
        s = copy.copy(self)
        s.sections = {k: list(v) for k, v in self.sections.items()}
        return s

    def index(self, identity):
        return next(i for i, op in enumerate(self.sections[identity[0]]) if op[3] == identity)

    def moved(self, identity, q, frame):
        s = self.clone()
        ops = s.sections[identity[0]]
        f, t, u, oid = ops.pop(s.index(identity))
        ops.insert(q, (frame, t, u, oid))
        return s

    def register_sequence(self, r):
        seq = [self.start[r]]
        fm = self.frames.original
        for f, t, us in self.word['D']:
            if r == t or r in us:
                seq.append(fm[f])
        for f, t, u, _ in self.sections['A']:
            if r in (t, u):
                seq.append(f)
        copy_frame = seq[-1] if r in self.cp else None
        for f, t, u, _ in self.sections['B']:
            if r in (t, u):
                seq.append(f)
        v = self.word['v']
        for f, t, u, _ in reversed(self.sections['A'] + self.sections['B']):
            if not v <= t < 2*v and r in (t, u):
                seq.append(self.frames.full)
        seq.append(self.final[r])
        return seq, copy_frame

    def profile(self, regs=None):
        result = collections.Counter()
        for r in range(len(self.start)) if regs is None else regs:
            seq, cp = self.register_sequence(r)
            for a, b in zip(seq, seq[1:]):
                require(a & ~b == 0, 'frame descent at register %d' % r)
                d = self.frames.dims[b] - self.frames.dims[a]
                if d:
                    result[d] += 1
            if cp is not None:
                result[self.frames.dims[cp]] += 1
        result.pop(0, None)
        return result

    def boundaries(self, section, r):
        pre = self.start[r]
        for f, t, us in self.word['D']:
            if r == t or r in us:
                pre = self.frames.original[f]
        if section == 'B':
            for f, t, u, _ in self.sections['A']:
                if r in (t, u):
                    pre = f
        if section == 'A':
            post = next((f for f, t, u, _ in self.sections['B'] if r in (t, u)), None)
            if post is not None:
                return pre, post
        v = self.word['v']
        touched_c = any(not v <= t < 2*v and r in (t, u)
                        for f, t, u, _ in self.sections['A'] + self.sections['B'])
        return pre, self.frames.full if touched_c else self.final[r]


def commute(a, b):
    return a[1] != b[2] and b[1] != a[2]


def legal_moves(state, identity, ignore_copy=False, copy_on_b=False):
    """Enumerate each literal insertion slot and every frame of the domain.

    Legality means all crossed ADDs commute, both frame chains remain nested,
    and the resulting last A frame of each retained total equals its pinned
    COPY frame. Checking the resulting last touch covers removal as well as
    insertion. No legacy nomination or frame choice enters this routine.
    """
    sec, _ = identity
    ops = state.sections[sec]
    i = state.index(identity)
    op = ops[i]
    f0, t, u, _ = op
    rest = ops[:i] + ops[i+1:]
    lo = i
    while lo and commute(op, ops[lo-1]):
        lo -= 1
    hi = i
    while hi+1 < len(ops) and commute(op, ops[hi+1]):
        hi += 1
    contexts = {}
    for r in (t, u):
        pre, post = state.boundaries(sec, r)
        touches = [(j, x[0]) for j, x in enumerate(rest) if r in x[1:3]]
        contexts[r] = (pre, post, touches, [x[0] for x in touches])
    cache = {}
    out = []
    for q in range(lo, hi+1):
        low, high = 0, state.frames.full
        last = {}
        signature = []
        for r in (t, u):
            pre, post, touches, js = contexts[r]
            k = bisect.bisect_left(js, q)
            p = touches[k-1][1] if k else pre
            n = touches[k][1] if k < len(touches) else post
            low |= p
            high &= n
            last[r] = None if k == len(touches) else touches[-1][1]
            signature.append(k)
        if low & ~high:
            continue
        key = (low, high)
        if key not in cache:
            closure = state.frames.closure(low)
            cache[key] = sorted(set(state.frames.original + (closure,)))
            cache[key] = [m for m in cache[key] if low & ~m == 0 and m & ~high == 0]
        for frame in cache[key]:
            if q == i and frame == f0:
                continue
            if not ignore_copy and (sec == 'A' or copy_on_b):
                if any((frame if last[r] is None else last[r]) != state.cp[r]
                       for r in (t, u) if r in state.cp):
                    continue
            out.append((q, frame, tuple(signature)))
    return out


def delta(left, right):
    return {r: right.get(r, 0)-left.get(r, 0)
            for r in sorted(set(left) | set(right)) if right.get(r, 0) != left.get(r, 0)}


def delta_key(d):
    return tuple(sorted(d.items()))


def legacy_tools(word):
    """Legacy imports live only behind this observational comparison adapter."""
    sys.path.insert(0, str(ROOT/'research/e8-bit-p111-tuned/tune'))
    import tune
    spec = importlib.util.spec_from_file_location('pr1048_search_observed', ROOT/'research/bit-profile-pair-audit/code/search.py')
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    return tune, legacy


def observe_legacy(state, identity, tune, legacy):
    w = copy.deepcopy(state.word)
    masks = list(state.frames.original)
    lookup = {m: i for i, m in enumerate(masks)}
    for sec in 'AB':
        for f, _, _, _ in state.sections[sec]:
            if f not in lookup:
                lookup[f] = len(masks)
                masks.append(f)
    w['frames'] = [[i for i in range(len(w['lines'])) if m >> i & 1] for m in masks]
    for sec in 'AB':
        w[sec] = [[lookup[f], t, [u]] for f, t, u, _ in state.sections[sec]]
    tuner = tune.Tuner(w)
    view = tuner.view(identity[0])
    i = state.index(identity)
    nom = tune.best_move(view, i, thr=1e9, all_=True) or []
    all_ = legacy.all_legal_moves(view, i, tune.commute, tune.best_move)
    old_mask = tuner.cat.masks[view.ops[i][0]]
    return ({(q, tuner.cat.masks[f]) for _, q, f in nom},
            {(q, tuner.cat.masks[f]) for q, f in all_ if q != i or tuner.cat.masks[f] != old_mask})


def packed_move(state, identity, move):
    q, f, _ = move
    return {'operation': list(identity), 'current_index': state.index(identity),
            'slot': q, 'frame_mask': str(f),
            'original_frame_id': state.frames.original.index(f) if f in state.frames.original else None}


def compare_sets(moves, nom, original_all):
    lookup = {(q,f): (f,sig) for q,f,sig in moves}
    classes = set(lookup.values())
    nom_classes = {lookup[x] for x in nom if x in lookup}
    all_classes = {lookup[x] for x in original_all if x in lookup}
    return {'original_nominations':len(nom),
            'original_all_legal_returned':len(original_all),
            'original_all_legal_illegal':len(original_all-set(lookup)),
            'original_all_legal_missing_frame_touch_classes':len(classes-all_classes),
            'nomination_missing_frame_touch_classes':len(classes-nom_classes)}


def candidate_digest(moves):
    rows = [[q,str(f),list(sig)] for q,f,sig in moves]
    return hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()


def semantic_controls():
    # Deliberately small artificial local contracts. These are not bit-word
    # suppliers and are not claimed as counterexamples on the PR589 word.
    w = {'v':1,'R':1,'lines':[[1,0],[0,1]],'frames':[[],[0],[0,1]],
         'start':[1,1,1],'final':[2,2,2],'ret':[2], 'D':[], 'C':[],
         'A':[[1,2,[0]],[2,2,[1]]],'B':[]}
    f = Frames(w)
    s = State(w,f)
    tune, legacy = legacy_tools(w)
    oid = ('A',1)
    good = {(q,m) for q,m,_ in legal_moves(s,oid)}
    bad = {(q,m) for q,m,_ in legal_moves(s,oid,ignore_copy=True)}
    _, old = observe_legacy(s,oid,tune,legacy)
    witness = (0,f.original[1])
    require(witness in bad and witness not in good and witness in old,
            'last-A-removal semantic control failed')
    w2 = copy.deepcopy(w)
    w2['A'] = [[1,2,[0]]]
    w2['B'] = [[2,2,[1]],[2,2,[0]]]
    s2 = State(w2,Frames(w2))
    good2 = {(q,m) for q,m,_ in legal_moves(s2,('B',0))}
    bad2 = {(q,m) for q,m,_ in legal_moves(s2,('B',0),copy_on_b=True)}
    _, old2 = observe_legacy(s2,('B',0),tune,legacy)
    witness2 = (1,s2.frames.full)
    require(witness2 in good2 and witness2 not in bad2 and witness2 not in old2,
            'A-only-COPY semantic control failed')
    return [{'control':'remove_last_A_touch_preserves_resulting_COPY_frame',
             'synthetic':True,'mutation':'omit final retained-copy check',
             'mutation_detected':True,'legacy_all_legal_admits_invalid_move':True,
             'witness':{'operation':['A',1],'slot':0,'frame_mask':str(witness[1])}},
            {'control':'COPY_constraint_applies_to_A_only','synthetic':True,
             'mutation':'apply COPY restriction to B', 'mutation_detected':True,
             'legacy_all_legal_omits_valid_move':True,
             'witness':{'operation':['B',0],'slot':1,'frame_mask':str(witness2[1])}}]


def run(max_first=15):
    started = time.monotonic()
    word = json.load(gzip.open(WORD, 'rt'))
    frames = Frames(word)
    state = State(word, frames)
    full = state.profile()
    require(dict(sorted(full.items())) == {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}, 'independent baseline profile')
    tune, legacy = legacy_tools(word)
    first_rows = []
    chosen = []
    effects = collections.Counter()
    witnesses = []
    cross_witnesses = []
    replayed = set()
    continuation_states = []
    continuation_witnesses = []
    all_controls = semantic_controls()
    for identity in FIRST:
        moves = legal_moves(state, identity)
        nom, original_all = observe_legacy(state, identity, tune, legacy)
        classes = collections.defaultdict(list)
        for move in moves:
            classes[(move[1], move[2])].append(move)
        # Three explicitly selected literal states per operation: earliest,
        # lexicographically first original nomination, and first alternative
        # frame (or latest). Equal profiles stay as distinct first states.
        picks = [moves[0]] if moves else []
        nominated_pick = next((m for m in moves if (m[0],m[1]) in nom), None)
        if nominated_pick is not None and nominated_pick not in picks:
            picks.append(nominated_pick)
        old_f = state.sections[identity[0]][state.index(identity)][0]
        other = next((m for m in moves if m[1] != old_f), moves[-1] if moves else None)
        if other is not None and other not in picks:
            picks.append(other)
        for move in picks:
            if len(chosen) < max_first:
                chosen.append((identity, move))
        regs = set(state.sections[identity[0]][state.index(identity)][1:3])
        old = state.profile(regs)
        profile_cache = {}
        for move in moves:
            key = (move[1], move[2])
            if key not in profile_cache:
                after = state.moved(identity, move[0], move[1])
                profile_cache[key] = delta(old, after.profile(regs))
                dk = delta_key(profile_cache[key])
                if dk not in replayed:
                    require(delta(full,after.profile()) == profile_cache[key], 'first full replay disagrees')
                    replayed.add(dk)
            effects[delta_key(profile_cache[key])] += 1
        illegal_all = sorted(original_all - {(q,f) for q,f,_ in moves})
        first_rows.append({'operation': list(identity), 'legal_literal_moves': len(moves),
                          'candidate_sha256':candidate_digest(moves),
                          'frame_touch_classes': len(classes), **compare_sets(moves,nom,original_all),
                          'illegal_witnesses': [{'slot':q,'frame_mask':str(f)} for q,f in illegal_all[:2]],
                          'profile_delta_classes': len(set(delta_key(d) for d in profile_cache.values()))})
    second_rows = []
    for identity, move in chosen:
        after = state.moved(identity, move[0], move[1])
        op = after.sections[identity[0]][after.index(identity)]
        regs1 = set(op[1:3])
        # Every adjacent stable identity, in both sections. No disjointness
        # theorem is asserted: disjoint operations are outside this domain.
        ids = [x[3] for sec in 'AB' for x in after.sections[sec]
               if regs1 & set(x[1:3])]
        nom1, _ = observe_legacy(state,identity,tune,legacy)
        first_nominated = (move[0],move[1]) in nom1
        continuation = []
        reachable_profiles = set()
        reachable_witnesses = {}
        first_delta = delta(state.profile(regs1), after.profile(regs1))
        for identity2 in ids:
            moves2 = legal_moves(after, identity2)
            nom2, original_all2 = observe_legacy(after, identity2, tune, legacy)
            regs2 = set(after.sections[identity2[0]][after.index(identity2)][1:3])
            affected = regs1 | regs2
            baseline = state.profile(affected)
            cache = {}
            for m2 in moves2:
                # Caching values is valid; continuations are never coalesced.
                key = (m2[1], m2[2])
                if key not in cache:
                    final = after.moved(identity2, m2[0], m2[1])
                    d = delta(baseline, final.profile(affected))
                    cache[key] = d
                    dk = delta_key(d)
                    if dk not in replayed:
                        require(delta(full,final.profile()) == d, 'second full replay disagrees')
                        replayed.add(dk)
                    if d and len(witnesses) < 8:
                        witnesses.append({'first': packed_move(state, identity, move),
                                          'second': packed_move(after, identity2, m2),
                                          'local_delta': d})
                    if identity2[0] != identity[0] and first_nominated and (m2[0],m2[1]) in nom2 and len(cross_witnesses) < 6:
                        cross_witnesses.append({'first':packed_move(state,identity,move),
                                                'second':packed_move(after,identity2,m2),
                                                'both_moves_are_original_nominations':True,
                                                'local_delta':d,
                                                'omission':'legacy pair_search obtains the second view from the first section only'})
                effects[delta_key(cache[key])] += 1
                reachable_profiles.add(delta_key(cache[key]))
                reachable_witnesses.setdefault(delta_key(cache[key]),packed_move(after,identity2,m2))
            independent_set = {(q,f) for q,f,_ in moves2}
            cross = identity2[0] != identity[0]
            second_rows.append({'first': packed_move(state, identity, move),
                                'second_operation': list(identity2), 'cross_section': cross,
                                'legal_literal_moves': len(moves2),
                                'candidate_sha256':candidate_digest(moves2),
                                'frame_touch_classes': len(cache),
                                **compare_sets(moves2,nom2,original_all2),
                                'first_is_original_nomination':first_nominated,
                                'legacy_pair_search_evaluates_second_section': not cross,
                                'profile_delta_classes': len(set(map(delta_key, cache.values())))})
            continuation.append([list(identity2),candidate_digest(moves2),len(moves2)])
        # Exact decomposition control compares full replay with register-local
        # replay on every chosen first state, using integers only.
        require(delta(full, after.profile()) == first_delta, 'integer register decomposition')
        all_controls.append({'control':'full_profile_equals_touched_register_delta', 'first':packed_move(state,identity,move),'passed':True})
        continuation_states.append({'first':packed_move(state,identity,move),
                                    'first_local_delta':first_delta,
                                    'continuation_sha256':hashlib.sha256(json.dumps(continuation,separators=(',',':')).encode()).hexdigest(),
                                    'continuation_moves':sum(x[2] for x in continuation),
                                    'reachable_final_local_deltas':[dict(x) for x in sorted(reachable_profiles)]})
        continuation_witnesses.append(reachable_witnesses)
    # Scope-aware semantic tamper controls exercise actual omissions rather
    # than relying on generic branch coverage or echoed implementation logic.
    require(cross_witnesses, 'real cross-section nominated-pair witness missing')
    all_controls.append({'control':'both_sections_are_in_the_declared_second_domain',
                         'synthetic':False,'mutation':'restrict second section to first section',
                         'mutation_detected':True,'lost_nominated_pair_witnesses':len(cross_witnesses)})
    equal_different = []
    for j, left in enumerate(continuation_states):
        for k, right in enumerate(continuation_states[j+1:],j+1):
            if (left['first']['operation'] == right['first']['operation'] and
                    left['first_local_delta'] == right['first_local_delta'] and
                    left['continuation_sha256'] != right['continuation_sha256']):
                lset = {delta_key(d) for d in left['reachable_final_local_deltas']}
                rset = {delta_key(d) for d in right['reachable_final_local_deltas']}
                equal_different.append({'left':left,'right':right,
                                        'reachable_profile_sets_equal':lset == rset,
                                        'only_left_final_local_deltas':[dict(x) for x in sorted(lset-rset)],
                                        'only_right_final_local_deltas':[dict(x) for x in sorted(rset-lset)],
                                        'only_left_witnesses':[{'local_delta':dict(x),'second':continuation_witnesses[j][x]} for x in sorted(lset-rset)],
                                        'only_right_witnesses':[{'local_delta':dict(x),'second':continuation_witnesses[k][x]} for x in sorted(rset-lset)]})
    require(equal_different, 'equal profile/distinct continuation control not exercised')
    all_controls.append({'control':'profile_equality_is_not_continuation_identity',
                         'synthetic':False,'mutation':'reuse second candidate domain by first profile delta',
                         'mutation_detected':True,'witness_pairs':len(equal_different),
                         'meaning':'literal continuation domains differ; reachable profile-set equality is reported separately',
                         'different_reachable_profile_set_pairs':sum(not x['reachable_profile_sets_equal'] for x in equal_different)})
    spec = importlib.util.spec_from_file_location('pr1048_reference_pricing', HERE/'pricing.py')
    pricing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pricing)
    pricer = pricing.ReferencePricer(local=dict(full))
    prices = {k:pricer.compare_delta(dict(k)) for k in effects}
    statuses = collections.Counter()
    for k,n in effects.items():
        statuses[prices[k]['status']] += n
    for witness in witnesses + cross_witnesses:
        witness['certified_price'] = prices[delta_key(witness['local_delta'])]
    totals = {'first_moves':sum(x['legal_literal_moves'] for x in first_rows),
              'second_moves':sum(x['legal_literal_moves'] for x in second_rows),
              'second_operation_rows':len(second_rows),
              'cross_section_second_moves':sum(x['legal_literal_moves'] for x in second_rows if x['cross_section']),
              'unique_local_deltas':len(effects),
              'full_replayed_delta_classes':len(replayed),
              'price_status_occurrences':{k:statuses[k] for k in ('BETTER','WORSE_OR_EQUAL','UNRESOLVED')},
              'exact_profile_tie_occurrences':effects[()]}
    totals['strictly_worse_occurrences'] = sum(n for k,n in effects.items()
        if prices[k].get('interval') and Fraction(prices[k]['interval'][0]) > 0)
    require(sum(statuses.values()) == totals['first_moves']+totals['second_moves'], 'priced occurrence coverage')
    return {'schema': 1, 'status': 'BOUNDED_COVERAGE_RECONSTRUCTED',
            'source_word_sha256': hashlib.sha256(WORD.read_bytes()).hexdigest(),
            'scope': {'first_operations': [list(x) for x in FIRST], 'max_first_states':max_first,
                      'selected_first_states':len(chosen), 'frame_universe':'original catalogue plus exact rational lower-span closure per slot',
                      'first_state_selection':'earliest literal move, first original nomination, first alternative frame or last literal move; duplicates removed',
                      'second_operation_rule':'all adjacent stable operation identities in both sections',
                      'all_literal_slots':True, 'steinberg_in_scope':False,
                      'global_neighborhood_claim':False},
            'independent_local_profile':dict(sorted(full.items())),
            'first':first_rows,'second':second_rows,'totals':totals,
            'reference_root_bracket':list(map(str,pricer.bounds)) if pricer.bounds else None,
            'exact_local_profile_deltas':[{'delta':dict(k),'occurrences':n,'certified_price':prices[k]} for k,n in sorted(effects.items())],
            'witnesses':witnesses,'controls':all_controls,
            'cross_section_omission_witnesses':cross_witnesses,
            'equal_profile_different_continuations':equal_different,
            'timing':{'elapsed_seconds':round(time.monotonic()-started,3)}}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--output','--out', type=Path)
    ap.add_argument('--max-first', type=int, default=15)
    args = ap.parse_args()
    result = run(args.max_first)
    text = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(text)
    print(json.dumps({k:result[k] for k in ('status','scope','totals','timing')}, sort_keys=True))
