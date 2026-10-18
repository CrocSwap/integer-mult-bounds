# SPDX-License-Identifier: Apache-2.0
"""Reverse demand closure and exact normalized endpoint pullback.

Substantial OpenAI Codex assistance. Native identities, COPY/CLEAR macro
contracts, physical ownership and precision are separately stated obligations.
"""
from fractions import Fraction


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def slots(r):
    return ["v:" + r, "c:" + r, "l:" + r]


def records(events, live_roles):
    require(type(events) is list and len(events) <= 100000, "cone event capacity")
    initial = [s for r in live_roles for s in slots(r)]
    known = set(initial)
    operations = []
    centers = set()
    active_private = set()
    for i, event in enumerate(events):
        tag, outputs, roots = event[0], {}, []
        if tag == "phase":
            continue
        if tag == "scalar":
            op, r = event[1], event[1][1]
            used = op[1:3] if op[0] in ("add", "copy") else op[1:2]
            require(all(not x.startswith("Z") or x in active_private for x in used), "scalar uses live private role")
            v, c, life = slots(r)
            if op[0] == "clear" and r.startswith("C") and r not in centers:
                outputs = {v: [], c: [], life: []}
                centers.add(r)
            else:
                dependencies = [c, life]
                if op[0] in ("add", "scale"):
                    dependencies.append(v)
                if op[0] in ("add", "copy"):
                    dependencies.extend(slots(op[2]))
                outputs[v] = dependencies
        elif tag == "zero_buffer":
            r = event[2]
            v, c, life = slots(r)
            if event[1] == "alloc":
                require(r not in active_private and v not in known, "fresh private allocation")
                outputs = {v: [], c: [], life: []}
                active_private.add(r)
            else:
                require(event[1] == "free" and r in active_private, "matched private free")
                outputs = {life: [v, c, life]}
                active_private.remove(r)
                if r == "Z249":
                    roots.append(life)
        else:
            require(tag in ("climb", "center", "warp", "adapter", "residual_adapter"), "cone native kind")
            r = event[2] if tag in ("climb", "adapter", "residual_adapter") else event[1]
            require(not r.startswith("Z") or r in active_private, "native uses live private role")
            v, c, life = slots(r)
            outputs = {v: [v, c, life], c: [c, life]}
            if tag == "residual_adapter" and event[1] == "post" and r == "L249":
                roots.append(v)
        require(all(s in known for deps in outputs.values() for s in deps), "cone read before creation")
        known.update(outputs)
        require(len(known) <= 4096, "cone total slot capacity")
        operations.append({"index": i, "outputs": outputs, "roots": roots})
    require(not active_private, "unclosed private lifetimes")
    require(sum(bool(r["roots"]) for r in operations) == 2, "both precise endpoint roots")
    return operations, sorted(initial)


def reverse_demand(operations, initial, final=()):
    demand, selected = set(final), []
    for record in reversed(operations):
        demand.update(record["roots"])
        needed = demand.intersection(record["outputs"])
        if needed:
            selected.append(record["index"])
            predecessors = {s for target in needed for s in record["outputs"][target]}
            demand.difference_update(needed)
            demand.update(predecessors)
    require(demand <= set(initial), "unresolved dependency boundary")
    return {"event_indices": sorted(selected), "boundary_inputs": sorted(demand)}


def reduced(word, op):
    if word and word[-1] == -op:
        return word[:-1]
    require(len(word) < 64, "free operator word capacity")
    return (*word, op)


def add_terms(target, source, factor):
    for word, q in tuple(source.items()):
        value = target.get(word, Fraction(0)) + factor * q
        if value:
            target[word] = value
        else:
            target.pop(word, None)
    require(len(target) <= 4096, "endpoint per-role term capacity")


def pull(rows, event, backward):
    tag = event[0]
    if tag == "warp":
        r, op = event[1:3]
        if backward:
            op = (1 if op > 0 else -1) * (1000000 + abs(op))
        rows[r] = {reduced(w, op): q for w, q in rows.get(r, {}).items()}
    elif tag == "zero_buffer" and event[1] == "alloc":
        rows.pop(event[2], None)
    elif tag == "scalar":
        op, r = event[1], event[1][1]
        if op[0] == "clear":
            rows.pop(r, None)
        elif op[0] == "scale":
            q = Fraction(op[2], op[3])
            rows[r] = {w: q * x for w, x in rows.get(r, {}).items()}
        elif op[0] == "add":
            require(r != op[2], "endpoint distinct ADD operands")
            add_terms(rows.setdefault(op[2], {}), rows.get(r, {}), Fraction(op[3], op[4]))
        elif op[0] == "copy":
            require(r != op[2], "endpoint distinct COPY operands")
            old = rows.pop(r, {})
            add_terms(rows.setdefault(op[2], {}), old, Fraction(1))
        else:
            raise ValueError("unsupported endpoint scalar")
    else:
        require(tag in ("phase", "zero_buffer", "climb", "center", "adapter", "residual_adapter"), "endpoint native kind")
    require(sum(len(value) for value in rows.values()) <= 16384, "endpoint total term capacity")


def endpoint(events, role, boundary, backward, included=None):
    require(type(boundary) is int and 0 <= boundary < len(events), "endpoint boundary index")
    rows = {role: {(): Fraction(1)}}
    for i in range(boundary, -1, -1):
        if included is None or i in included:
            pull(rows, events[i], backward)
    return [[r, list(w), str(q)] for r in sorted(rows)
            for w, q in sorted(rows[r].items()) if q]


def endpoints(events, backward, included):
    helper = [i for i, e in enumerate(events) if e[:3] == ["residual_adapter", "post", "L249"]]
    private = [i - 1 for i, e in enumerate(events) if e == ["zero_buffer", "free", "Z249"]]
    require(len(helper) == len(private) == 1, "unique endpoint boundaries")
    result = {}
    for r, index in (("L249", helper[0]), ("Z249", private[0])):
        complete = endpoint(events, r, index, backward)
        restricted = endpoint(events, r, index, backward, set(included))
        expected = [["L249", [], "1"]] if r == "L249" else []
        require(complete == restricted == expected, "closed emitted normalized endpoint " + r)
        result[r] = {"boundary_event": index, "full_and_restricted_covector": complete}
    return result
