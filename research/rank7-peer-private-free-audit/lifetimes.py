"""Independent forward free-algebra values and forward dependency provenance.

No predecessor replay, covector or dependency-graph implementation is imported.
SPDX-License-Identifier: Apache-2.0
"""
from collections import Counter
from fractions import Fraction
import hashlib
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def encode(row):
    return [[r, list(w), str(q)] for (r, w), q in sorted(row.items()) if q]


def merge(left, right, coefficient):
    out = dict(left)
    for key, value in right.items():
        value = out.get(key, 0) + coefficient * value
        if value:
            out[key] = value
        else:
            out.pop(key, None)
    require(len(out) <= 16384, "formal row capacity")
    return out


def warp(row, operator):
    out = {}
    for (role, word), value in row.items():
        new = word[1:] if word and word[0] == -operator else (operator, *word)
        require(len(new) <= 64, "free word length capacity")
        key = (role, new)
        out[key] = out.get(key, 0) + value
    return {key: value for key, value in out.items() if value}


def values(events, original_roles, backward=False, strict=True):
    """Propagate independent original inputs; capture values BEFORE each free.

    Frames/native wrappers act as coordinate changes. This normalized semantics
    requires the separately checked common-chart/native realization contracts.
    """
    rows = {r: {(r, ()): Fraction(1)} for r in original_roles}
    active, allocated, frees, peaks, helper = set(), set(), [], 0, None
    require(len(events) <= 100000, "event capacity")
    for index, event in enumerate(events):
        tag = event[0]
        if tag == "phase":
            continue
        if tag == "zero_buffer":
            action, r = event[1:]
            if action == "alloc":
                require(r not in allocated and r not in rows, "private allocation is fresh")
                allocated.add(r)
                active.add(r)
                rows[r] = {}
                peaks = max(peaks, len(active))
            else:
                require(action == "free" and r in active, "free requires live allocation")
                value = encode(rows[r])
                frees.append({"role": r, "event": index, "value": value})
                require(not strict or not value, "nonzero private free " + r + " at " + str(index))
                active.remove(r)
                del rows[r]
        elif tag == "scalar":
            op, r = event[1], event[1][1]
            operands = op[1:3] if op[0] in ("add", "copy") else op[1:2]
            require(all(not x.startswith("Z") or x in active for x in operands), "private use outside lifetime")
            if op[0] == "clear":
                require(r in rows or r.startswith("C"), "CLEAR target exists")
                rows[r] = {}
            elif op[0] == "copy":
                require(r != op[2], "distinct COPY roles")
                rows[r] = dict(rows[op[2]])
            elif op[0] == "scale":
                q = Fraction(op[2], op[3])
                require(q != 0, "nonzero scalar scale")
                rows[r] = {key: q * value for key, value in rows[r].items()}
            else:
                require(op[0] == "add" and r != op[2], "distinct ADD roles")
                rows[r] = merge(rows[r], rows[op[2]], Fraction(op[3], op[4]))
        elif tag == "warp":
            r, operator = event[1:3]
            require(r in rows, "warp uses live role")
            if backward:
                operator = (1 if operator > 0 else -1) * (1000000 + abs(operator))
            rows[r] = warp(rows[r], operator)
        else:
            require(tag in ("climb", "center", "adapter", "residual_adapter"), "known native event")
            r = event[1] if tag == "center" else event[2]
            require(r in rows, "native uses live role")
            if tag == "residual_adapter" and event[1:3] == ["post", "L249"]:
                helper = encode(rows[r])
    require(not active, "all private lifetimes closed")
    require(len(frees) == len(allocated), "one free per allocation")
    return {"frees": frees, "peak_live_private": peaks, "helper249": helper}


def bits(mask):
    out = []
    while mask:
        low = mask & -mask
        out.append(low.bit_length() - 1)
        mask ^= low
    return out


def provenance(events, original_roles):
    """Forward event-provenance bitsets on separate value/chart/lifetime channels.

    Unlike backwards slicing or SSA graph reachability, each state channel
    carries its transitive producer set as the stream executes. No cancellations
    are used. COPY/CLEAR overwrite only the value channel.
    """
    initial = [channel + ":" + r for r in sorted(original_roles) for channel in ("v", "c", "l")]
    offset = len(initial)
    state = {r: tuple(1 << (3 * i + j) for j in range(3)) for i, r in enumerate(sorted(original_roles))}
    active, allocated, roots, old = set(), set(), {}, 0
    for index, event in enumerate(events):
        tag, own = event[0], 1 << (offset + index)
        if tag == "phase":
            continue
        if tag == "zero_buffer":
            action, r = event[1:]
            if action == "alloc":
                require(r not in allocated and r not in state, "provenance fresh private")
                allocated.add(r)
                active.add(r)
                state[r] = (own, own, own)
            else:
                require(action == "free" and r in active, "provenance live private free")
                v, c, life = state[r]
                roots[r] = v | c | life | own
                if r == "Z249":
                    old |= roots[r]
                active.remove(r)
                del state[r]
        elif tag == "scalar":
            op, r = event[1], event[1][1]
            operands = op[1:3] if op[0] in ("add", "copy") else op[1:2]
            require(all(not x.startswith("Z") or x in active for x in operands), "provenance private lifetime")
            if r not in state:
                require(op[0] == "clear" and r.startswith("C"), "new center created by CLEAR")
                state[r] = (own, own, own)
                continue
            v, c, life = state[r]
            new = own | c | life
            if op[0] in ("add", "scale"):
                new |= v
            if op[0] in ("add", "copy"):
                sv, sc, sl = state[op[2]]
                new |= sv | sc | sl
            require(op[0] in ("add", "copy", "clear", "scale"), "provenance scalar kind")
            state[r] = (new, c, life)
        else:
            require(tag in ("climb", "center", "warp", "adapter", "residual_adapter"), "provenance native kind")
            r = event[1] if tag in ("center", "warp") else event[2]
            require(r in state, "provenance native role")
            v, c, life = state[r]
            state[r] = (v | c | life | own, c | life | own, life)
            if tag == "residual_adapter" and event[1:3] == ["post", "L249"]:
                old |= state[r][0]
    require(not active, "provenance closed private lifetimes")
    all_free = 0
    for mask in roots.values():
        all_free |= mask
    def decode(mask):
        return {"event_indices": bits(mask >> offset),
                "boundary_inputs": sorted(initial[i] for i in bits(mask & ((1 << offset) - 1)))}
    return {"old_pair": decode(old), "all_frees": decode(all_free),
            "expanded": decode(all_free | old), "free_roots": sorted(roots)}


def summary(events, closure):
    indices = closure["event_indices"]
    ranges = []
    for index in indices:
        if ranges and ranges[-1][1] == index:
            ranges[-1][1] += 1
        else:
            ranges.append([index, index + 1])
    return {"events": len(indices), "by_kind": dict(sorted(Counter(events[i][0] for i in indices).items())),
            "event_ranges_half_open": ranges, "event_indices_sha256": sha(indices),
            "boundary_inputs_count": len(closure["boundary_inputs"]),
            "boundary_inputs_sha256": sha(closure["boundary_inputs"]),
            "event_sha256": sha([events[i] for i in indices])}
