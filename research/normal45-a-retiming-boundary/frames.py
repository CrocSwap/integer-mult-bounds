# SPDX-License-Identifier: Apache-2.0
"""Complete A-frame domains with the prelude, B, restore and endpoints fixed.

The forward-join/backward-meet event-graph method follows navinor's PR864 frame
model and Thomas DiFiore's k8 adaptation. This graph handles the later borrowed-word warp/prelude ABI.
Tekalign with substantial OpenAI Codex assistance.
"""
from functools import lru_cache
import common as s

pm, FULL = s.pm, s.FULL


@lru_cache(None)
def join(left, right):
    return pm.basis(left + right)


@lru_cache(None)
def meet(left, right):
    rows = pm.basis(tuple((v << 9) | v for v in left) + tuple(v << 9 for v in right))
    return pm.basis(tuple(v for v in rows if v < 512))


def roles(gate):
    return gate[1:3] if gate[0] == 'add' else gate[1:2]


def solve(word):
    """Construct every exact frame domain, then one legal preferred assignment."""
    n, A = word['prelude_events'], word['A']
    start = [(p,) for p in word['ports']] + [()] * 592
    for r, frame in word['start_extra'].items():
        start[int(r)] = pm.basis(frame)
    for gate in A[:n]:
        if gate[0] == 'warp':
            start[gate[1]] = pm.basis(gate[4])
        else:
            for r in roles(gate):
                start[r] = pm.basis(gate[-1])
    end = ([FULL] * 112 +
           [pm.basis([v for v in range(1, 512) if (v & p).bit_count() % 2 == 0])
            for p in word['ports']] + [FULL] * 480)
    for r, frame in word['helper_final'].items():
        end[int(r)] = pm.basis(frame)
    # First post-A scalar touch permits a climb. A warp requires exact equality.
    upper, exact, seen = list(end), {}, set()
    for r, frame in zip(word['centers'], word['center_frames']):
        exact[r] = pm.basis(frame)
    for r in range(112, 224):
        exact[r] = pm.basis(word['target_levels'].get(str(r - 112), []))
    warps = {}
    for warp in word['warps']:
        warps.setdefault(warp[0], []).append(warp)
    for pos in range(len(word['B']) + 1):
        for warp in warps.get(pos, []):
            r = warp[1]
            if r not in seen:
                upper[r] = pm.basis(warp[3])
                if r in exact:
                    s.require(exact[r] == upper[r], 'consistent centre/warp equality')
                exact[r] = upper[r]
                seen.add(r)
        if pos < len(word['B']):
            gate = word['B'][pos]
            for r in roles(gate):
                if r not in seen:
                    upper[r] = pm.basis(gate[-1])
                    seen.add(r)
    for gate in word['restore']:
        for r in roles(gate):
            if r not in seen:
                upper[r] = pm.basis(gate[-1])
                seen.add(r)
    last = {r: -1 - r for r in range(704)}
    lo = {-1 - r: frame for r, frame in enumerate(start)}
    fixed, pred, succ = dict(lo), {}, {}
    for i, gate in enumerate(A[n:], n):
        rs = roles(gate)
        pred[i] = [last[r] for r in rs]
        frame = ()
        for r in rs:
            frame = join(frame, lo[last[r]])
            succ.setdefault(last[r], []).append(i)
            last[r] = i
        lo[i] = frame
    hi = {i: FULL for i in lo}
    for r, frame in enumerate(upper):
        hi[last[r]] = meet(hi[last[r]], frame)
    # No invisible climb into an exact centre/warp pin: pin its actual last node.
    for r, frame in exact.items():
        node = last[r]
        s.require(node not in fixed or fixed[node] == frame, ('pin conflict', node, r))
        fixed[node] = frame
        hi[node] = meet(hi[node], frame)
    for i in range(n, len(A)):
        frame = ()
        for previous in pred[i]:
            frame = join(frame, lo[previous])
        if i in fixed:
            s.require(join(frame, fixed[i]) == fixed[i], ('fixed below lower', i))
            frame = fixed[i]
        lo[i] = frame
    for i in range(len(A) - 1, n - 1, -1):
        for following in succ.get(i, []):
            hi[i] = meet(hi[i], hi[following])
        s.require(i not in fixed or join(fixed[i], hi[i]) == hi[i], ('fixed above upper', i))
        s.require(join(lo[i], hi[i]) == hi[i], ('empty frame domain', i))
    for i, frame in fixed.items():
        if i < 0:
            for following in succ.get(i, []):
                s.require(join(frame, hi[following]) == hi[following], ('start above upper', i))
    values = {i: frame for i, frame in fixed.items() if i < 0}
    for i in range(n, len(A)):
        frame = ()
        for previous in pred[i]:
            frame = join(frame, values[previous])
        if i in fixed:
            frame = fixed[i]
        else:
            frame = join(frame, meet(pm.basis(A[i][-1] or []), hi[i]))
        values[i] = frame
        A[i][-1] = list(frame)
    profile, inventory = pm.frame_report(word)
    word['report']['local_profile'] = profile
    word['report']['width_inventory'] = inventory
    return word, dict(lo=lo, hi=hi, fixed=fixed, pred=pred, succ=succ,
                      values=values, n=n, last=last, upper=upper)
