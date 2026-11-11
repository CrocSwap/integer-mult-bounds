#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Find causal pairings from literal stationary and retimable observations.

Retiming and temporal elimination follow the credited #7156 lineage. The
changed pool adds complete live zero-MOVE intervals and guards same-cut COPY.
A nomination is an input to the whole-word and complete-caller replays.
"""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from replay_sources import need, parent_archive, predecessor


def add(dst, src, scale):
    for k, v in src.items():
        value = dst.get(k, 0) + v*scale
        if value:
            dst[k] = value
        else:
            dst.pop(k, None)


def span(basis):
    out = {0}
    for a in basis:
        need(a not in out, "Independent axes")
        out |= {a ^ v for v in out}
    return out


def affected(event):
    return event[1:3] if event[0] in ("ADD", "COPY") else event[1:2]


def windows(word, charts):
    events = word["program"]
    live = {r: (0, f, []) for r, f in enumerate(word["initial"])}
    neutral, movers = defaultdict(list), []

    def close(role, hi):
        lo, a, indices = live[role]
        if indices:
            frames = [a, *(events[j][3] for j in indices)]
            path = dict(role=role, lo=lo, hi=hi, moves=indices, frames=frames)
            movers.append(path)
            for f in sorted(set(frames) & charts):
                neutral[f].append(path | {"frame": f})
        elif a in charts:
            neutral[a].append(dict(role=role, lo=lo, hi=hi, frame=a, stationary=True))
        return events[indices[-1]][3] if indices else a

    for i, e in enumerate(events):
        op, r = e[:2]
        if op == "INIT":
            need(r not in live, "Fresh owned interval")
            live[r] = i+1, e[2], []
        elif op == "MOVE":
            live[r][2].append(i)
        else:
            for owner in affected(e):
                f = close(owner, i)
                need(f == e[-1], "Literal contact chart")
                live[owner] = i+1, f, []
            if op == "CLEAR":
                del live[r]
    for role in live:
        need(role < word["public"] and close(role, len(events)) == word["final"][role], "Literal final chart")
    return neutral, movers


def affordable_paths(word, charts, movers, spaces, cap, descending_owned):
    ranks = list(map(len, word["frames"]))
    n = word["public"]
    proposals = []
    for path in movers:
        if len(path["moves"]) != 1:
            continue
        a, b = path["frames"]
        owned = path["role"] >= n
        if owned and (not descending_owned or ranks[b] >= ranks[a]):
            continue
        rank = abs(ranks[b]-ranks[a])
        if not 2 <= rank <= 8:
            continue
        for f in sorted(charts - {a, b}):
            if spaces[a] < spaces[f] < spaces[b] or (owned and spaces[b] < spaces[f] < spaces[a]):
                legs = [abs(ranks[f]-ranks[a]), abs(ranks[b]-ranks[f])]
                proposal = path | dict(frame=f, old=a, new=b, old_paid=[rank], new_paid=legs,
                                       private=owned, paid=True)
                proposals.append((rank, min(legs), f, path["lo"], path["role"], proposal))
    proposals.sort(key=lambda row: row[:5])
    return [p[-1] for p in proposals[:cap]], len(proposals)


def annotate(word, observations):
    """One forward and one guarded backward pass over the exact source."""
    events = word["program"]
    n, m = word["public"], word["public"]+word["owned_fields"]
    starts, stops = defaultdict(list), defaultdict(list)
    for obs in observations:
        starts[obs["lo"]].append(obs)
        stops[obs["hi"]].append(obs)
    rows = [{r: Q(1)} if r < n else {} for r in range(m)]
    for cut in range(len(events)+1):
        for x in starts.get(cut, ()):
            x["pre"] = rows[x["role"]].copy()
        if cut == len(events):
            break
        op, r, *a = events[cut]
        if op in ("INIT", "CLEAR"):
            rows[r] = {}
        elif op == "SCALE":
            rows[r] = {j: v*Q(a[0]) for j, v in rows[r].items()}
        elif op in ("ADD", "COPY"):
            if op == "COPY":
                need(not rows[r], "Original COPY destination zero")
            add(rows[r], rows[a[0]], Q(a[1]))
    cols = [{r: Q(1)} for r in range(m)]
    for cut in range(len(events), -1, -1):
        for x in stops.get(cut, ()):
            x["suf"] = cols[x["role"]].copy()
        if cut == 0:
            break
        op, r, *a = events[cut-1]
        if op in ("INIT", "CLEAR"):
            cols[r] = {}
        elif op == "SCALE":
            cols[r] = {j: v*Q(a[0]) for j, v in cols[r].items()}
        elif op in ("ADD", "COPY"):
            add(cols[a[0]], cols[r], Q(a[1]))
            if op == "COPY":
                cols[r] = {m+cut-1: Q(1)}


def kernel(observations, side, group, skip_stationary=False):
    """A chronological generating set for the pure helper images."""
    is_prefix = side == "pre"
    endpoint = "lo" if is_prefix else "hi"
    order = sorted(range(len(observations)),
                   key=lambda j: observations[j][endpoint], reverse=not is_prefix)
    pivots, pure = {}, []
    for j in order:
        obs = observations[j]
        if skip_stationary and obs.get("stationary"):
            continue
        outside = {r: v for r, v in obs[side].items() if r not in group}
        inside = {r: v for r, v in obs[side].items() if r in group}
        provenance = {j: Q(1)}
        while outside:
            r = min(outside)
            if r not in pivots:
                coefficient = outside[r]
                pivots[r] = tuple({k: v/coefficient for k, v in row.items()}
                                  for row in (outside, inside, provenance))
                break
            factor = -outside[r]
            for row, pivot in zip((outside, inside, provenance), pivots[r]):
                add(row, pivot, factor)
        if not outside and inside:
            clock = (max if is_prefix else min)(observations[k][endpoint] for k in provenance)
            pure.append((inside, provenance, clock))
    return pure


def pair(c, d):
    return sum(q*d.get(r, 0) for r, q in c.items())


def smooth(x):
    for p in (2, 3, 5):
        while x % p == 0:
            x //= p
    return x == 1


def legal(op, q):
    return (q and abs(q)+1 < 2**16 and abs(q.numerator).bit_length() <= 24
            and smooth(q.denominator) and (op != "SCALE" or smooth(abs(q.numerator))))


def point(obs, q, side, index, remap):
    row = dict(cut=obs["lo" if side == "pre" else "hi"], role=obs["role"], frame=obs["frame"],
               coefficient=str(q))
    if obs.get("stationary"):
        row["stationary_interval"] = [obs["lo"], obs["hi"]]
    elif obs.get("paid"):
        row["paid_path"] = 0
    else:
        row["path"] = remap[index]
    return row


def nominate(observations, word, group, f, split, extra, counts, extension=None, baseline=None):
    pre = kernel(observations, "pre", group)
    suf = kernel(observations, "suf", group)
    if baseline is None:
        mpre = kernel(observations, "pre", group, skip_stationary=True)
        msuf = kernel(observations, "suf", group, skip_stationary=True)
    else:
        mpre, msuf = baseline
    residents = [(o["lo"], o["hi"], o["role"], j) for j, o in enumerate(observations)
                 if o["role"] in group]
    counts["cases"] += 1
    counts["prefix_generators"] += len(pre)
    counts["suffix_generators"] += len(suf)
    reference_pair_windows = sorted((lo, hi) for c, _, lo in mpre for d, _, hi in msuf
                                 if lo <= hi and pair(c, d))
    for c, a, lo in pre:
        for d0, b0, hi in suf:
            if lo > hi:
                continue
            pairing = pair(c, d0)
            if not pairing:
                continue
            counts["rational_pairs"] += 1
            if extension:
                if extension["role"] not in c and extension["role"] not in d0:
                    continue
            elif not any(observations[j].get("stationary") for j in set(a) | set(b0)):
                continue
            d = {r: q/pairing for r, q in d0.items()}
            b = {j: q/pairing for j, q in b0.items()}
            scales = {Q(1), *(1/q for q in d.values()), *c.values()}
            for born, expired, pivot, pivot_index in residents:
                cut = max(lo, born)
                for first, last in reference_pair_windows:
                    if first > cut:
                        break
                    if last >= cut:
                        cut = last+1
                if cut > min(hi, expired):
                    continue
                counts["new_access_required_pairs"] += 1
                for s in sorted(scales, key=lambda q: (abs(q.numerator).bit_length()+q.denominator.bit_length(), q)):
                    cc, dd = {r: q/s for r, q in c.items()}, {r: q*s for r, q in d.items()}
                    aa, bb = {j: q/s for j, q in a.items()}, {j: q*s for j, q in b.items()}
                    if not all(legal("ADD", q) for q in [*aa.values(), *bb.values()]):
                        continue
                    code = split.basis(cc, dd, pivot, 3)
                    if not all(legal(e[0], Q(e[-2])) for e in code + split.inverse(code)):
                        continue
                    used = sorted(j for j in set(aa) | set(bb) | {pivot_index}
                                  if not (observations[j].get("stationary") or observations[j].get("paid")))
                    remap = {j: k for k, j in enumerate(used)}
                    paths = [{k: v for k, v in observations[j].items() if k not in ("pre", "suf")} for j in used]
                    rank = len(word["frames"][f])
                    hit = dict(frame=f, cut=cut, pivot=pivot, ranks=[rank, 9-rank],
                               c={str(r): str(q) for r, q in cc.items()}, d={str(r): str(q) for r, q in dd.items()},
                               gathers=[point(observations[j], q, "pre", j, remap) for j, q in aa.items()],
                               injections=[point(observations[j], q, "suf", j, remap) for j, q in bb.items()],
                               paid_delta={})
                    if extension:
                        hit["extension"] = extension
                    if extra:
                        delta = Counter(extra["new_paid"])
                        delta.subtract(extra["old_paid"])
                        hit.update(paid_path=0, path={k: v for k, v in extra.items() if k not in ("pre", "suf", "paid")},
                                   paid_delta={str(r): v for r, v in delta.items() if v})
                    return hit, paths, dict(full_generators=[len(pre), len(suf)],
                                           reference_generators=[len(mpre), len(msuf)],
                                           reference_pair_windows=len(reference_pair_windows), boundary_instructions=len(code))
    return None


def run(word, split, paid_limit, ranks, descending_owned):
    spaces = list(map(span, word["frames"]))
    main = set(word["live"]) | {r+112 for r in word["live"]} | set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    group = {r for r, (a, b) in enumerate(zip(word["initial"], word["final"]))
             if r not in main and (a, b) == (3, 127)}
    charts = {f for f, s in enumerate(spaces) if len(s) in {2**rank for rank in ranks} and spaces[3] < s < spaces[127]}
    charts -= {120, 237, 306, 595}
    neutral, movers = windows(word, charts)
    eligible = {f for f in charts if any(o.get("stationary") for o in neutral[f])}
    paid, available_paid = affordable_paths(word, eligible, movers, spaces, paid_limit, descending_owned)
    by_chart = [o for f in sorted(eligible) for o in neutral[f]]
    annotate(word, [*by_chart, *paid])
    counts = Counter()
    summary = dict(group_size=len(group), eligible_charts=len(eligible),
                   stationary=sum(o.get("stationary", False) for o in by_chart),
                   moving=len(by_chart)-sum(o.get("stationary", False) for o in by_chart),
                   affordable_single_midpoints=available_paid, paid_case_cap=paid_limit, ranks=ranks, descending_owned=descending_owned)
    print("DOMAIN", summary, flush=True)
    for f in sorted(eligible):
        obs = neutral[f]
        if not any(o["role"] in group for o in obs):
            counts["charts_without_pivot"] += 1
            continue
        found = nominate(obs, word, group, f, split, None, counts)
        if found:
            return found, summary | dict(neutral=dict(counts), paid={})
    neutral_counts, counts = dict(counts), Counter()
    print("NEUTRAL", neutral_counts, flush=True)
    for extra in paid:
        f = extra["frame"]
        found = nominate([*neutral[f], extra], word, group, f, split, extra, counts)
        if found:
            return found, summary | dict(neutral=neutral_counts, paid=dict(counts))
    return None, summary | dict(neutral=neutral_counts, paid=dict(counts))



def run_exit(word, split):
    spaces = list(map(span, word["frames"]))
    main = set(word["live"]) | {r+112 for r in word["live"]} | set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    group = {r for r, (a, b) in enumerate(zip(word["initial"], word["final"]))
             if r not in main and (a, b) == (3, 127)}
    exits = {r: b for r, (a, b) in enumerate(zip(word["initial"], word["final"]))
             if r not in main and a == 3 and len(spaces[b]) == 256 and spaces[b] < spaces[127]}
    charts = {f for f, s in enumerate(spaces) if 4 <= len(s) <= 128 and spaces[3] < s < spaces[127]}
    charts -= {120, 237, 306, 595}
    pool, _ = windows(word, charts)
    annotate(word, [o for obs in pool.values() for o in obs])
    order = sorted(pool, key=lambda f: (abs(len(word["frames"][f])-4.5), f))
    counts = Counter()
    summary = dict(group_size=len(group), eligible_exits=len(exits), charts=len(order))
    print("EXIT DOMAIN", summary, flush=True)
    for f in order:
        obs = pool[f]
        roles = {o["role"] for o in obs}
        supported = set().union(*(row.keys() for o in obs for row in (o["pre"], o["suf"])))
        choices = [r for r in exits if r in supported and (r in roles or not roles.isdisjoint(group))]
        if not choices:
            continue
        baseline = kernel(obs, "pre", group), kernel(obs, "suf", group)
        for r in choices:
            extra = dict(role=r, old=exits[r], new=127, cut=len(word["program"]))
            found = nominate(obs, word, group | {r}, f, split, None, counts, extension=extra, baseline=baseline)
            if found:
                return found, summary | dict(screen=dict(counts))
        if counts["cases"] % 200 < len(choices):
            print("EXIT SCREEN", dict(counts), flush=True)
    return None, summary | dict(screen=dict(counts))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--paid-limit", type=int, default=500)
    parser.add_argument("--ranks", type=int, nargs="+", default=[4, 5])
    parser.add_argument("--descending-owned", action="store_true")
    parser.add_argument("--funded-exit", action="store_true")
    args = parser.parse_args()
    need(all(1 <= r <= 8 for r in args.ranks) and 0 <= args.paid_limit <= 500, "Bounded search scope")
    args.output.mkdir()
    with parent_archive() as parent:
        sys.path.insert(0, str(parent))
        import split
        word = predecessor(parent)
        if args.funded_exit:
            result, info = run_exit(word, split)
        else:
            result, info = run(word, split, args.paid_limit, args.ranks, args.descending_owned)
    if result:
        hit, paths, detail = result
        for name, data in [("WITNESS.json", hit), ("PATHS.json", paths)]:
            (args.output / name).write_text(json.dumps(data, indent=2)+"\n")
        info.update(witness=dict(frame=hit["frame"], cut=hit["cut"], pivot=hit["pivot"], **detail))
    info.update(status="EXACT_CAUSAL_NOMINEE" if result else "NO_EMITTED_NOMINEE",
                scope="Exact rational availability and bounded literal basis synthesis")
    (args.output / "DISCOVERY.json").write_text(json.dumps(info, indent=2)+"\n")
    print(info, flush=True)


if __name__ == "__main__":
    main()
