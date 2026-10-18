#!/usr/bin/env python3
"""Minimal primary scan of the exact ordered-pair projection.

Brian Ross with substantial OpenAI Codex assistance, Apache-2.0.
Retains the flemhhh/DreamingOfClouds supplier and audit attribution in the
certified repair. No complete two-move claim follows from a pilot run.

For fixed x,y, omit gates disjoint from R=regs(x)|regs(y). Every omitted gate
commutes with both movers and changes no R frame, COPY frame, or C event.
Consequently the projected first slots preserve y's continuation, including
touches of y's private register; own-touch first classes alone would not.
Both section boundaries remain. An identity first state covers first moves
whose only crossings are erased by projection. The pinned COPY frames and
original catalogue are inherited from the full baseline.

After the second move there is no further continuation: (frame,touch-counts)
may then cache the exact resulting R profile. The first states are NOT
coalesced by profile or by own-touch signature.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'research/pr1048-certified-repair'))
from coverage import Frames, State, WORD, delta, delta_key, legal_moves, require
from pricing import ReferencePricer
from run import check_sources


def ordered_pairs(state):
    touches = defaultdict(set)
    for sec in 'AB':
        for _, t, u, oid in state.sections[sec]:
            touches[t].add(oid)
            touches[u].add(oid)
    pairs = set()
    for ids in touches.values():
        pairs.update((x,y) for x in ids for y in ids if x != y)
    return sorted(pairs)


def projected(full, registers):
    s = full.clone()
    s.sections = {sec:[op for op in full.sections[sec]
                       if registers & set(op[1:3])] for sec in 'AB'}
    # clone retains the full initial COPY snapshot; never recompute it after
    # deleting irrelevant gates or after the first transport.
    require(s.cp == full.cp, 'COPY snapshot was not pinned')
    require(s.profile(registers) == full.profile(registers),
            'projection changed baseline register profile')
    return s


def describe(identity, slot, frame):
    return {'operation':list(identity),'projected_slot':slot,'frame_mask':str(frame)}


def scan(limit=128, time_budget=45, full_scan=False):
    start = time.monotonic()
    source_count = check_sources()
    w = json.load(gzip.open(WORD,'rt'))
    baseline = State(w,Frames(w))
    pairs = ordered_pairs(baseline)
    if full_scan:
        chosen = pairs
    else:
        require(1 <= limit <= len(pairs), 'pilot size outside pair domain')
        chosen = [pairs[k*len(pairs)//limit] for k in range(limit)]
    # Initialize pricing before scanning; report it separately from kernel
    # time so a pilot is not extrapolated from a fixed certificate setup cost.
    pricer = ReferencePricer()
    require(baseline.profile() == pricer.local, 'full baseline differs from certified reference profile')
    setup = time.monotonic()-start
    projections = {}
    prices = {}
    delta_counts = Counter()
    totals = Counter()
    completed = []
    witnesses = []
    digest = hashlib.sha256()
    scan_start = time.monotonic()
    for x,y in chosen:
        if time.monotonic()-start >= time_budget:
            break
        xop = baseline.sections[x[0]][baseline.index(x)]
        yop = baseline.sections[y[0]][baseline.index(y)]
        regs = frozenset(xop[1:3]+yop[1:3])
        if regs not in projections:
            s = projected(baseline,regs)
            projections[regs] = s,s.profile(regs)
        s,base_profile = projections[regs]
        first = [(q,f) for q,f,_ in legal_moves(s,x)]
        first.append((s.index(x),xop[0]))
        require(len(first) == len(set(first)), 'duplicate first projected state')
        row = {'first':list(x),'second':list(y),'first_states':len(first),
               'projected_operations':sum(map(len,s.sections.values())),
               'second_literal_moves':0,'priced_second_classes':0}
        digest.update(json.dumps([x,y,first],separators=(',',':')).encode())
        for q,f in first:
            after = s.moved(x,q,f)
            second = legal_moves(after,y)
            # Include the identity second state too; all one-move states are
            # covered explicitly, and the non-improvement theorem includes
            # at most two transports without an exactly-two loophole.
            second_classes = {}
            for q2,f2,sig in second:
                second_classes.setdefault((f2,sig),(q2,f2))
            row['second_literal_moves'] += len(second)
            totals['second_literal_moves'] += len(second)
            yi = after.index(y)
            preceding = after.sections[y[0]][:yi]
            identity_signature = tuple(sum(r in op[1:3] for op in preceding)
                                       for r in yop[1:3])
            second_classes.setdefault((yop[0],identity_signature),(yi,yop[0]))
            representatives = list(second_classes.values())
            for q2,f2 in representatives:
                final = after.moved(y,q2,f2)
                d = delta(base_profile,final.profile(regs))
                require(sum(r*n for r,n in d.items()) == 0, 'transport changed rank mass')
                key = delta_key(d)
                if key not in prices:
                    prices[key] = pricer.compare_delta(d)
                classification = prices[key]
                totals[classification['status']] += 1
                totals['priced_second_classes'] += 1
                row['priced_second_classes'] += 1
                delta_counts[key] += 1
                digest.update(json.dumps([q,f,q2,f2,key],separators=(',',':')).encode())
                if classification['status'] != 'WORSE_OR_EQUAL' and len(witnesses) < 8:
                    witnesses.append({'first':describe(x,q,f),'second':describe(y,q2,f2),
                                      'registers':sorted(regs),'local_delta':d,
                                      'price':classification})
            totals['first_states'] += 1
        totals['ordered_pairs'] += 1
        completed.append(row)
        if len(completed) in (256,2048) or len(completed)%2000 == 0:
            running = time.monotonic()-scan_start
            print(json.dumps({'progress_pairs':len(completed),'requested_pairs':len(chosen),
                              'first_states':totals['first_states'],
                              'priced_second_classes':totals['priced_second_classes'],
                              'scan_seconds':round(running,3),
                              'linear_full_scan_seconds':round(running*len(pairs)/len(completed),1)},
                             sort_keys=True),flush=True)
        # A putative improvement is a reason to lift and independently verify
        # that witness before launching any broader enumeration.
        if witnesses:
            break
    elapsed = time.monotonic()-scan_start
    return {'status':'PILOT_ONLY' if not full_scan else 'COMPLETE' if len(completed)==len(pairs) else 'INCOMPLETE',
            'complete_domain':len(completed)==len(pairs),
            'domain':{'ordered_distinct_adjacent_pairs':len(pairs),
                      'first_frame_domain':'original636 plus rational closure of per-slot lower frame bound',
                      'first_slots':'all literal slots in pair-specific projection, plus identity',
                      'second_slots':'all legal projected slots; equal frame/touch contexts priced once; plus identity',
                      'sections':'both retained','self_pair_reduction':'final state is a legal single transport in the frozen frame domain'},
            'pilot_selection':'evenly spaced indices in sorted ordered-pair domain' if not full_scan else 'all',
            'requested_pairs':len(chosen),'completed_pair_count':len(completed),
            'pilot_pair_rows':completed if not full_scan else [],
            'checked_source_pins':source_count,
            'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_word_sha256':hashlib.sha256(WORD.read_bytes()).hexdigest(),
            'candidate_digest':digest.hexdigest(),
            'totals':dict(totals),
            'delta_classes':[{'delta':dict(k),'priced_classes':n,'price':prices[k]} for k,n in sorted(delta_counts.items())],
            'witnesses_requiring_full_lift_and_independent_check':witnesses,
            'timing':{'setup_seconds':round(setup,3),'scan_seconds':round(elapsed,3),
                      'total_seconds':round(time.monotonic()-start,3),
                      'linear_full_scan_seconds':round(elapsed*len(pairs)/max(1,len(completed)),1)}}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--pairs',type=int,default=128)
    ap.add_argument('--time-budget',type=float,default=45)
    ap.add_argument('--full',action='store_true',help='explicit full-run authorization required')
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    result = scan(args.pairs,args.time_budget,args.full)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','complete_domain','requested_pairs','totals','timing')},sort_keys=True))
