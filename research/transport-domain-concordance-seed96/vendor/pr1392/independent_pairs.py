"""Separate complete pair-projection replay, using the frozen integer checker.

Brian Ross with substantial OpenAI Codex assistance. Apache-2.0.
The only imported research module is the separate checker at ce0b65fd;
neither pairs.py nor its primary enumeration/pricing engines are imported.
The transcript format is shared for exact cross-implementation comparison.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from math import gcd
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / 'pr1048-certified-repair'
spec = importlib.util.spec_from_file_location('separate_frozen_checker', PREVIOUS / 'independent.py')
ind = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ind)


class Projection(ind.WordCheck):
    """Keep only the two/three relevant register cells in event replay.

    This removes scans of all 661 final registers and all irrelevant D touches
    from every candidate. Literal enumeration and integer geometry remain the
    separate frozen implementation; no primary code enters the checker.
    """
    def __init__(self, source, registers):
        self.__dict__ = source.__dict__.copy()
        self.active = registers
        self.starts = {r: self.catalog[self.word['start'][r]] for r in registers}
        self.ends = {r: self.catalog[self.word['final'][r]] for r in registers}
        self.diagonal = [(self.catalog[f], tuple(r for r in (t, *us) if r in registers))
                         for f, t, us in self.word['D']]
        self.diagonal = [(f, rs) for f, rs in self.diagonal if rs]
        self.after_d = dict(self.starts)
        for f, rs in self.diagonal:
            for r in rs:
                self.after_d[r] = f
        self.retained = set(self.word['ret']) & registers

    def before(self, state, section):
        current = dict(self.after_d)
        if section == 'B':
            for _, f, t, u in state['A']:
                for r in (t,u):
                    if r in current:
                        current[r] = f
        return current

    def after(self, state, section):
        current = dict(self.ends)
        v = self.word['v']
        for _, _, t, u in state['A'] + state['B']:
            if not v <= t < 2*v:
                for r in (t,u):
                    if r in current:
                        current[r] = self.full
        if section == 'A':
            for _, f, t, u in reversed(state['B']):
                for r in (t,u):
                    if r in current:
                        current[r] = f
        return current

    def profile(self, state, selected=None):
        ind.require(selected is None or set(selected) == self.active, 'projection register scope')
        current, counts = dict(self.starts), Counter()
        def touch(r, frame):
            if r not in current:
                return
            old = current[r]
            ind.require(old & ~frame == 0, 'projected frame descent')
            if old != frame:
                difference = self.rank(frame) - self.rank(old)
                ind.require(difference >= 0, 'projected rank descent')
                if difference:
                    counts[difference] += 1
                current[r] = frame
        for f, rs in self.diagonal:
            for r in rs:
                touch(r, f)
        for _, f, t, u in state['A']:
            touch(t, f)
            touch(u, f)
        for r in self.retained:
            counts[self.rank(current[r])] += 1
        for _, f, t, u in state['B']:
            touch(t, f)
            touch(u, f)
        v = self.word['v']
        for _, _, t, u in reversed(state['A'] + state['B']):
            if not v <= t < 2*v:
                touch(t, self.full)
                touch(u, self.full)
        for r, f in self.ends.items():
            touch(r, f)
        counts.pop(0, None)
        return dict(counts)


def closed_catalogue(checker):
    """Exact integer basis reduction: masks really contain all source lines in their spans."""
    def reduce_vector(v, rows):
        v = list(v)
        for pivot, row in rows:
            if v[pivot]:
                a, b = row[pivot], v[pivot]
                v = [a*x-b*y for x, y in zip(v, row)]
                divisor = 0
                for x in v:
                    divisor = gcd(divisor, x)
                if divisor:
                    v = [x//divisor for x in v]
        return v
    for mask in checker.catalog:
        rows = []
        for j, vector in enumerate(checker.word['lines']):
            if mask >> j & 1:
                v = reduce_vector(vector, rows)
                if any(v):
                    rows.append((next(i for i, x in enumerate(v) if x), v))
                    rows.sort()
        closure = sum(1 << j for j, v in enumerate(checker.word['lines'])
                      if not any(reduce_vector(v, rows)))
        ind.require(closure == mask, 'original catalogue mask is not span closed')
    return len(checker.catalog)


def strict_synthetic_control():
    """Same first frame/touch signature can hide a strictly better continuation.

    y=(a<-c)@L, x=(b<-a)@H, e=(f<-g)@H, z=(d<-c)@L;
    baseline order y,x,e,z, L=span(e1,e2), H=span(e1,...,e4).
    This is an abstract transport contract, not an improved PR589 supplier.
    """
    w = dict(v=0, R=6, lines=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],
             frames=[[0],[1],[0,1],[0,1,2,3]], start=[0,3,1,2,3,3], final=[3]*6,
             ret=[], D=[], A=[], B=[[2,0,[2]],[3,1,[0]],[3,4,[5]],[2,3,[2]]])
    t = object.__new__(ind.WordCheck)
    t.word, t.catalog, t.full = w, (1,2,3,15), 15
    t.ranks, t.closures, t.copy_frames = {}, {}, {}
    t.initial = {'A': [], 'B': [(('B', i), t.catalog[f], a, u)
                               for i, (f, a, us) in enumerate(w['B']) for u in us]}
    baseline = t.profile(t.initial)
    singles = set()
    for op in t.initial['B']:
        for q, f, _ in t.literal_moves(t.initial, op[0]):
            singles.add(ind.profile_delta(baseline, t.profile(t.apply(t.initial, op[0], q, f))))
    first = [m for m in t.literal_moves(t.initial, ('B',1)) if m[0] in (2,3)]
    ind.require(len(first) == 2 and first[0][1:] == first[1][1:], 'synthetic first signature')
    reachable = []
    for q, f, _ in first:
        after = t.apply(t.initial, ('B',1), q, f)
        values = {ind.profile_delta(baseline, t.profile(after))}
        for q2, f2, _ in t.literal_moves(after, ('B',0)):
            values.add(ind.profile_delta(baseline, t.profile(t.apply(after, ('B',0), q2, f2))))
        reachable.append(values)
    improving = ((1,-1),(2,-1),(3,1))
    ind.require(singles == {()} and improving not in reachable[0] and improving in reachable[1],
                'own-touch first quotient failed to expose its lost improvement')
    interval = ind.signed_price(dict(improving))
    ind.require(interval[1] < 0, 'synthetic strict sign')
    return dict(synthetic=True, baseline_profile=baseline, all_single_deltas=[{}],
                identical_first_frame_touch_signature_slots=[2,3],
                earlier_continuation_deltas=[dict(x) for x in sorted(reachable[0])],
                later_continuation_deltas=[dict(x) for x in sorted(reachable[1])],
                lost_improving_delta=dict(improving), price_interval=list(map(str, interval)),
                status='PASS_REJECT_UNSOUND_FIRST_TOUCH_QUOTIENT')


def run(limit=128, seconds=45, full=False):
    started = time.monotonic()
    inventory = ind.audit_inventory(json.loads((PREVIOUS / 'SOURCE-PINS.json').read_text()))
    endpoints = [ind.residual(ind.BASE, a) for a in (ind.LOW, ind.HIGH)]
    ind.require(endpoints[0][1] < 0 < endpoints[1][0], 'separate reference endpoint signs')
    checker = ind.WordCheck()
    ind.require(checker.profile(checker.initial) == ind.BASE, 'separate baseline replay')
    closure_count = closed_catalogue(checker)
    synthetic = strict_synthetic_control()
    operations = {op[0]: op for section in 'AB' for op in checker.initial[section]}
    by_register = {}
    for identity, op in operations.items():
        for r in op[2:]:
            by_register.setdefault(r, []).append(identity)
    pairs = sorted({(x,y) for ids in by_register.values() for x in ids for y in ids if x != y})
    ind.require(len(operations) == 3064 and len(pairs) == 59998, 'fixed operation/pair inventory')
    ind.require(full or 1 <= limit <= len(pairs), 'pilot size')
    chosen = pairs if full else [pairs[i*len(pairs)//limit] for i in range(limit)]
    projections, prices, frequencies = {}, {}, Counter()
    totals = Counter()
    witnesses = []
    transcript = hashlib.sha256()
    setup = time.monotonic() - started
    scan_started = time.monotonic()
    for x, y in chosen:
        if time.monotonic() - started >= seconds:
            break
        xo, yo = operations[x], operations[y]
        registers = frozenset(xo[2:] + yo[2:])
        if registers not in projections:
            state = {s: [op for op in checker.initial[s] if registers.intersection(op[2:])]
                     for s in 'AB'}
            local = Projection(checker, registers)
            baseline = local.profile(state, registers)
            ind.require(baseline == checker.profile(checker.initial, registers), 'projection baseline')
            projections[registers] = state, baseline, local
        state, baseline, local = projections[registers]
        first = [(q, f) for q, f, _ in local.literal_moves(state, x)]
        first.append((checker.index(state, x), xo[1]))
        ind.require(len(first) == len(set(first)), 'first projected duplication')
        transcript.update(json.dumps([x,y,first], separators=(',', ':')).encode())
        for q, frame in first:
            after = checker.apply(state, x, q, frame)
            seconds_list = local.literal_moves(after, y)
            representatives = {}
            for q2, frame2, signature in seconds_list:
                representatives.setdefault((frame2, signature), (q2, frame2))
            yi = checker.index(after, y)
            signature = tuple(sum(r in op[2:] for op in after[y[0]][:yi]) for r in yo[2:])
            representatives.setdefault((yo[1], signature), (yi, yo[1]))
            totals['second_literal_moves'] += len(seconds_list)
            for q2, frame2 in representatives.values():
                final = checker.apply(after, y, q2, frame2)
                key = ind.profile_delta(baseline, local.profile(final, registers))
                ind.require(sum(r*n for r,n in key) == 0, 'pair rank mass')
                if key not in prices:
                    candidate = {r: ind.BASE.get(r, 0)+dict(key).get(r, 0)
                                 for r in set(ind.BASE) | set(dict(key))}
                    ind.require(all(n >= 0 for n in candidate.values()), 'negative final profile')
                    ind.require(ind.residual(candidate, ind.Q(0))[1] < 0, 'pair positive root')
                    interval = ind.signed_price(dict(key))
                    prices[key] = dict(status=ind.status_of(interval), interval=list(map(str, interval)))
                price = prices[key]
                totals[price['status']] += 1
                totals['priced_second_classes'] += 1
                frequencies[key] += 1
                transcript.update(json.dumps([q,frame,q2,frame2,key], separators=(',', ':')).encode())
                if price['status'] != 'WORSE_OR_EQUAL' and len(witnesses) < 8:
                    witnesses.append(dict(first=dict(operation=list(x), projected_slot=q, frame_mask=str(frame)),
                                          second=dict(operation=list(y), projected_slot=q2, frame_mask=str(frame2)),
                                          registers=sorted(registers), local_delta=dict(key), price=price))
            totals['first_states'] += 1
        totals['ordered_pairs'] += 1
        if totals['ordered_pairs'] % 2000 == 0:
            print(json.dumps(dict(progress_pairs=totals['ordered_pairs'], total_pairs=len(chosen),
                                  elapsed_seconds=round(time.monotonic()-started, 2))), flush=True)
        if witnesses:
            break
    elapsed = time.monotonic() - scan_started
    complete = totals['ordered_pairs'] == len(pairs)
    return dict(status='COMPLETE' if complete else 'INCOMPLETE' if full else 'PILOT_ONLY',
                complete_domain=complete, engine='independent integer geometry and rational series',
                requested_pairs=len(chosen), source_inventory=inventory,
                source_word_sha256=checker.word_sha, original_span_closed_frames=closure_count,
                synthetic_control=synthetic, candidate_digest=transcript.hexdigest(), totals=dict(totals),
                delta_classes=[dict(delta=dict(k), priced_classes=n, price=prices[k]) for k,n in sorted(frequencies.items())],
                witnesses_requiring_full_lift_and_independent_check=witnesses,
                reference_bracket=list(map(str, (ind.LOW, ind.HIGH))),
                endpoint_residuals=[list(map(str, x)) for x in endpoints],
                driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                frozen_checker_sha256=hashlib.sha256((PREVIOUS / 'independent.py').read_bytes()).hexdigest(),
                timing=dict(setup_seconds=round(setup, 3), scan_seconds=round(elapsed, 3),
                            total_seconds=round(time.monotonic()-started, 3),
                            linear_full_scan_seconds=round(elapsed*len(pairs)/max(1,totals['ordered_pairs']), 1)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pairs', type=int, default=128)
    parser.add_argument('--time-budget', type=float, default=45)
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.pairs, args.time_budget, args.full)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status','complete_domain','requested_pairs','totals','timing')}, sort_keys=True))
