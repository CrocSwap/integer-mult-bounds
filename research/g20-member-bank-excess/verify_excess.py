#!/usr/bin/env python3
"""Exact source-bound necessary member/bank pairing gate; no typed word or bill.

New one-member/one-published-edge contexts only. The prior unchanged-bank
criterion and normalized query semantics are retained premises, independently
recounted where used. No predecessor executable is imported.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PINS = {'sources/WORD.json.gz': ['8dd441fdb9c8923df06eb5ebfda37d03e4539f2305763e688d8c7025d196c4b1', '3877a72d8a15adb03f6492f7d2fd8fa902ecb639'], 'sources/PATHS.json': ['f4dd58b78121040b1f054c0f7a626b25f6ef8d39f3de044d3456ea7dea8a6a5e', 'efbdf632746a971f9a593f57ccbb7d2cc67a6760'], 'sources/FRAMES.json': ['0d99fc6b8f45c03dfba5252a03dd9e7fe23be3a7593dfe15368e34da6629a654', '9edf8d95b45a9c9c766a956bfcd3c19cf07bc13c'], 'sources/gap-source.py': ['91e201fd3c96267c878863abba794a16025070c98145ae598ee0ed7383c7f9c6', '93bf7baf7c01de63a57a8ad1e4653ca48047eaae'], 'sources/gap-PROOF.md': ['121649b47271f45e18a1053ca5615c94e1cc81cc42136d8ccf3b2dca7d93f706', '26f776a79accbb8a6378e5ad5ebefc3693a26501'], 'sources/prior-source.py': ['a9aea8b108ebbeae8041770cefecfdabdfaf91b72ba7b5cfa2ff13408f1d16dd', '13326f590033f6633bc91f919c802b6ddaf576bc'], 'sources/prior-PROOF.md': ['af88b44f1c61fb91d63ace7a2ece8d798bf6378864b2c4e1d44e01070fd485db', 'c6d2f2c7626a7c42da025ef360ce1673f6a116dc'], 'sources/NOTICE.md': ['a4fdb5e2dfeeb216f3f58417891fc0a084c218d9a75228fb977e3cb82973be72', 'accbc28384515af7b94b33e5f4eb57a150e0d9a1'], 'sources/source-README.md': ['e443b2fd7b988316953bfc7d21045690ea0d3ce9069ce1a06880f6ccfc7ec054', 'b1655b59134ae7a5734628ba1efef6611b2dcd31']}


def need(ok, text):
    if not ok:
        raise ValueError(text)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def strict(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def read_inputs():
    data = {}
    for name, (sha, blob) in PINS.items():
        raw = (HERE/name).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == sha, "SHA256 source authentication: "+name)
        need(hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest() == blob,
             "Git blob source authentication: "+name)
        data[name] = raw
    return (strict(gzip.decompress(data["sources/WORD.json.gz"])),
            strict(data["sources/FRAMES.json"])["frames"], strict(data["sources/PATHS.json"]))


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return len(pivots)


def xor_sum(values, coefficients):
    result = 0
    while coefficients:
        bit = coefficients & -coefficients
        result ^= values[bit.bit_length()-1]
        coefficients ^= bit
    return result


def decomposition(rows, outside):
    """Restriction echelon rows retain exact cut-coordinate combinations."""
    pivots = {}
    kernel = []
    images = []
    for i, original in enumerate(rows):
        x, combination = original & outside, 1 << i
        while x:
            p = x.bit_length()-1
            if p not in pivots:
                pivots[p] = (x, combination)
                break
            old, coef = pivots[p]
            x ^= old
            combination ^= coef
        if not x:
            kernel.append(combination)
            images.append(xor_sum(rows, combination))
    need(len(kernel)+len(pivots) == len(rows), "complete restriction kernel")
    return pivots, kernel, images


def extend(decomp, rows, extra, outside):
    pivots, kernel, images = decomp
    x, combination = extra & outside, 1 << len(rows)
    while x:
        p = x.bit_length()-1
        if p not in pivots:
            return kernel, images
        old, coef = pivots[p]
        x ^= old
        combination ^= coef
    return kernel+[combination], images+[xor_sum(rows, combination & ((1 << len(rows))-1)) ^ extra]


def form(left, right):
    return [sum(((a & b).bit_count() & 1) << j for j, b in enumerate(right)) for a in left]


def details(rows, columns, outside):
    _, l, c = decomposition(rows, outside)
    _, r, d = decomposition(columns, outside)
    boundary, internal = form(c, d), form(l, r)
    return {"left": l, "right": r, "inputs": c, "outputs": d,
            "boundary": boundary, "internal": internal,
            "ranks": [len(l), len(r), binary_rank(boundary), binary_rank(internal)]}


def unit_pair(left, right, inputs, outputs):
    boundary, internal = form(inputs, outputs), form(left, right)
    candidate = next((1 << i for i in range(len(left)) if boundary[i] and internal[i]), None)
    if candidate is None:
        a = next((i for i, row in enumerate(boundary) if row), None)
        b = next((i for i, row in enumerate(internal) if row), None)
        if a is None or b is None:
            return None
        candidate = (1 << a) ^ (1 << b)
    cb, ib = xor_sum(boundary, candidate), xor_sum(internal, candidate)
    need(cb and ib, "unit pair left selection")
    both = cb & ib
    if both:
        choice = both & -both
    else:
        choice = (cb & -cb) | (ib & -ib)
    a, b = xor_sum(left, candidate), xor_sum(right, choice)
    c, d = xor_sum(inputs, candidate), xor_sum(outputs, choice)
    need((a & b).bit_count() % 2 == (c & d).bit_count() % 2 == 1, "simultaneous unit pair")
    return {"a": str(a), "b": str(b), "c": str(c), "d": str(d),
            "internal": 1, "boundary": 1}


def rational_space(rows):
    reduced = {}
    for raw in rows:
        need(type(raw) in (list, tuple) and len(raw) == 8, "frame row width")
        row = [Fraction(x) for x in raw]
        for p in sorted(reduced):
            q = row[p]
            if q:
                row = [x-q*y for x, y in zip(row, reduced[p])]
        p = next((i for i, x in enumerate(row) if x), None)
        if p is None:
            continue
        q = row[p]
        row = [x/q for x in row]
        for old in reduced:
            q = reduced[old][p]
            if q:
                reduced[old] = [x-q*y for x, y in zip(reduced[old], row)]
        reduced[p] = row
    return tuple(tuple(row) for _, row in sorted(reduced.items()))


def setup(word, frames, paths):
    need(type(word) is dict and set(word) == {"records", "owned", "start", "final"}, "word schema")
    n = len(word["start"])
    need(n == 685 and len(word["final"]) == n and len(word["records"]) == 14794, "frozen word dimensions")
    need(all(type(i) is int and 0 <= i < n for i in word["owned"]), "owned role types")
    need(len(set(word["owned"])) == len(word["owned"]), "distinct owned roles")
    spaces = {}
    for key, record in frames.items():
        need(key == str(int(key)) and type(record["dim"]) is int, "frame key/type")
        shape = rational_space(record["B"])
        need(len(shape) == record["dim"], "frame declared dimension")
        spaces[int(key)] = shape
    shapes = sorted(set(spaces.values()))
    label = {key: shapes.index(value) for key, value in spaces.items()}
    label[None] = None
    need(len(shapes) == 645, "exact physical shape count")
    need(all(type(v) is int and v in spaces or v is None for v in word["start"]+word["final"]), "boundary frame labels")
    group_members = defaultdict(list)
    owned = set(word["owned"])
    for h in range(222, n):
        if h not in owned:
            need(word["start"][h] is not None and word["final"][h] is not None, "public helper boundary")
            group_members[(label[word["start"][h]], label[word["final"][h]])].append(h)
    groups = [(key, tuple(value)) for key, value in sorted(group_members.items())]
    need(sorted(len(value) for _, value in groups) == [1, 1, 413], "three endpoint groups")
    outside = [(1 << n)-1 ^ sum(1 << h for h in value) for _, value in groups]
    compatible = []
    for (entrance, final), _ in groups:
        U, V = shapes[entrance], shapes[final]
        compatible.append({j for j, F in enumerate(shapes)
                           if len(V) < len(F) < len(U)
                           and rational_space(list(U)+list(F)) == U
                           and rational_space(list(F)+list(V)) == F})
    edges = [tuple(e) for route in paths.values() for e in route]
    need(len(edges) == len(set(edges)) == 2369, "distinct published route edges")
    for edge in edges:
        need(len(edge) == 3 and all(type(x) is int for x in edge), "route edge type")
        src, dst, rank = edge
        need(src in spaces and dst in spaces and len(spaces[src])-len(spaces[dst]) == rank > 0, "route rank/direction")
    return n, shapes, label, groups, outside, compatible, sorted(edges)


def synthetic_controls():
    inherited = details([1, 2], [0, 2], 0)
    inherited_single = details([2], [2], 0)
    genuine = details([1, 0], [0, 1], 0)
    foreign = details([4], [4], 4)
    internal_only = details([1], [2], 0)
    need(inherited["ranks"][2] == inherited_single["ranks"][2] == 1, "inherited singleton control")
    need(genuine["ranks"][2] == 1 and details([0], [1], 0)["ranks"][2] == 0, "bank essential control")
    witness = unit_pair(genuine["left"], genuine["right"], genuine["inputs"], genuine["outputs"])
    need(witness is not None and foreign["ranks"][:3] == [0, 0, 0], "eligibility control")
    need(internal_only["ranks"][2:] == [0, 1], "internal is not boundary control")
    return {"inherited_singleton": inherited["ranks"], "inherited_singleton_alone": inherited_single["ranks"],
            "genuine_bank_excess": genuine["ranks"], "genuine_unit_pair": witness,
            "foreign_support": foreign["ranks"], "internal_only": internal_only["ranks"],
            "qualification": "Synthetic algebra fixtures are not source edits, typed continuations, native checks or invoices."}


def scan(word, prepared, diagnostic=None):
    n, shapes, label, groups, outside, compatible, edges = prepared
    events = word["records"]
    prefix = [1 << i for i in range(n)]
    suffix = [1 << i for i in range(n)]
    erased = {}
    for index in range(len(events)-1, -1, -1):
        e = events[index]
        need(type(e) is list and e and e[0] in ("ADD", "Q", "ZERO_Q", "ERASE", "INIT"), "event opcode")
        op, d = e[:2]
        need(type(d) is int and 0 <= d < n, "event destination")
        if op == "ADD":
            need(len(e) == 4 and type(e[2]) is int and 0 <= e[2] < n and type(e[3]) is int and e[3] in label, "ADD schema")
            suffix[e[2]] ^= suffix[d]
        elif op == "ERASE":
            need(len(e) == 3 and (type(e[2]) is int or e[2] is None) and e[2] in label, "ERASE schema")
            erased[index], suffix[d] = suffix[d], 0
        else:
            need(len(e) == (5 if op in ("Q", "ZERO_Q") else 3), "query/INIT schema")
            need(all(type(x) is int and x in label for x in e[2:4]), "event frame types")
            if op in ("Q", "ZERO_Q"):
                need(type(e[4]) is int and len(shapes[label[e[2]]])-len(shapes[label[e[3]]]) == e[4] > 0, "literal query rank")
    state = word["start"][:]
    banks = defaultdict(set)
    for role, frame in enumerate(state):
        banks[label[frame]].add(role)
    member_group = {h: g for g, (_, members) in enumerate(groups) for h in members}
    member_sources = defaultdict(set)
    for h in member_group:
        member_sources[state[h]].add(h)
    outgoing, incoming = defaultdict(list), defaultdict(list)
    for edge in edges:
        outgoing[edge[0]].append(edge)
        incoming[label[edge[1]]].append(edge)
    active = {}
    active_by_shape = defaultdict(set)
    active_by_member = defaultdict(set)
    bank_cache = {}
    census, transitions = Counter(), Counter()
    digest = hashlib.sha256()
    hits = []
    evaluations = 0
    maximum_active = 0
    maximum_cache_bytes = 0

    def bank_data(g, shape):
        key = g, shape
        if key not in bank_cache:
            slots = tuple(sorted(banks[shape]))
            rows, columns = [prefix[i] for i in slots], [suffix[i] for i in slots]
            ld, rd = decomposition(rows, outside[g]), decomposition(columns, outside[g])
            boundary, internal = form(ld[2], rd[2]), form(ld[1], rd[1])
            rank = binary_rank(boundary)
            need(rank == 0, "prior zero-bank boundary premise independently recounted")
            input_sha = hashlib.sha256(canonical([slots, rows, columns]).encode()).hexdigest()
            bank_cache[key] = (slots, rows, columns, ld, rd, rank, binary_rank(internal), input_sha)
        return bank_cache[key]

    def flush(key, at):
        old = active.pop(key, None)
        if old is None:
            return
        first, summary = old
        active_by_shape[summary[5]].remove(key)
        active_by_member[key[0]].remove(key)
        length = at-first
        need(length > 0, "nonempty context interval")
        g, h, src, dst, rank, shape, base4, singleton4, augmented4, bankhash, carrierhash = summary
        category = (g, base4, singleton4, augmented4)
        census[category] += length
        digest.update((canonical([first, at-1, summary])+"\n").encode())
        transitions["context_intervals"] += 1

    def inspect(h, edge, cut):
        nonlocal evaluations, maximum_active
        src, dst, paid_rank = edge
        g, shape = member_group[h], label[dst]
        key = h, src, dst
        flush(key, cut)
        if state[h] != src or shape not in compatible[g] or not banks[shape] or h in banks[shape]:
            return
        slots, rows, columns, ld, rd, base, baseinternal, bankhash = bank_data(g, shape)
        left, ins = extend(ld, rows, prefix[h], outside[g])
        right, outs = extend(rd, columns, suffix[h], outside[g])
        boundary, internal = form(ins, outs), form(left, right)
        augmented, irank = binary_rank(boundary), binary_rank(internal)
        sl = int((prefix[h] & outside[g]) == 0)
        sr = int((suffix[h] & outside[g]) == 0)
        singleton = sl * sr * ((prefix[h] & suffix[h]).bit_count() & 1)
        need(augmented <= base+2, "one-coordinate rank bound")
        carrierhash = hashlib.sha256(canonical([prefix[h], suffix[h]]).encode()).hexdigest()
        base4 = (len(ld[1]), len(rd[1]), base, baseinternal)
        singleton4 = (sl, sr, singleton, sl*sr)
        augmented4 = (len(left), len(right), augmented, irank)
        summary = (g, h, src, dst, paid_rank, shape, base4, singleton4, augmented4, bankhash, carrierhash)
        active[key] = cut, summary
        active_by_shape[shape].add(key)
        active_by_member[h].add(key)
        evaluations += 1
        maximum_active = max(maximum_active, len(active))
        need(len(active) <= 160000, "bounded active context cache")
        if augmented > max(base, singleton):
            transitions["excess_evaluations"] += 1
            if not hits or not any(item["group"] == g for item in hits):
                need(len(hits) < 3, "one retained complete witness per endpoint group")
                item = {"cut_t": cut, "record_index_after": cut-1, "group": g, "member": h, "edge": list(edge), "bank": list(slots),
                        "base_ranks": [len(ld[1]), len(rd[1]), base, baseinternal],
                        "singleton_ranks": list(singleton4),
                        "augmented": {"left": list(map(str, left)), "right": list(map(str, right)),
                                      "inputs": list(map(str, ins)), "outputs": list(map(str, outs)),
                                      "boundary": list(map(str, boundary)), "internal": list(map(str, internal)),
                                      "ranks": [len(left), len(right), augmented, irank]},
                        "simultaneous_unit_pair": unit_pair(left, right, ins, outs),
                        "coordinate_order": list(slots)+[h]}
                if singleton:
                    hc, hd, eh = prefix[h], suffix[h], 1 << len(slots)
                    qleft = [a ^ (eh if (c & hd).bit_count() & 1 else 0) for a, c in zip(left, ins)]
                    qright = [b ^ (eh if (hc & d).bit_count() & 1 else 0) for b, d in zip(right, outs)]
                    qins = [xor_sum(rows+[prefix[h]], a) for a in qleft]
                    qouts = [xor_sum(columns+[suffix[h]], b) for b in qright]
                    qboundary, qinternal = form(qins, qouts), form(qleft, qright)
                    need(binary_rank(qboundary) == augmented-1, "inherited unit-pivot quotient rank")
                    item["inherited_pivot_quotient"] = {"left": list(map(str, qleft)), "right": list(map(str, qright)),
                          "boundary": list(map(str, qboundary)), "internal": list(map(str, qinternal)),
                          "ranks": [binary_rank(qboundary), binary_rank(qinternal)],
                          "simultaneous_unit_pair": unit_pair(qleft, qright, qins, qouts)}
                hits.append(item)

    def refresh(dirty_shapes, changed_members, cut):
        nonlocal maximum_cache_bytes
        for key in list(bank_cache):
            if key[1] in dirty_shapes:
                del bank_cache[key]
        targets = set()
        for shape in dirty_shapes:
            if shape is None:
                continue
            for edge in incoming[shape]:
                for h in member_sources[edge[0]]:
                    targets.add((h, edge))
            # Old active contexts must close even when the bank just emptied.
            for key in active_by_shape[shape]:
                targets.add((key[0], (key[1], key[2], len(shapes[label[key[1]]])-len(shapes[shape]))))
        for h in changed_members:
            for edge in outgoing[state[h]]:
                targets.add((h, edge))
            for key in active_by_member[h]:
                targets.add((h, (key[1], key[2], len(shapes[label[key[1]]])-len(shapes[label[key[2]]]))))
        for h, edge in sorted(targets):
            inspect(h, edge, cut)
        # Current-bank decompositions only; no all-cut map or context snapshots.
        cache_bytes = sum(sys.getsizeof(key)+sys.getsizeof(value)+
                          sum(sys.getsizeof(x) for x in value[:3]) for key, value in bank_cache.items())
        maximum_cache_bytes = max(maximum_cache_bytes, cache_bytes)
        need(cache_bytes <= 128*1024*1024, "bounded current-bank cache")

    refresh(set(banks), set(member_group), 0)
    end = len(events) if diagnostic is None else min(diagnostic, len(events))
    for index, e in enumerate(events[:end]):
        op, d = e[:2]
        before_frame = state[d]
        before = label[before_frame]
        changed = {d} & member_group.keys()
        if op == "ADD":
            s = e[2]
            need(state[d] == state[s] == e[3], "ADD literal common frame")
            prefix[d] ^= prefix[s]
            suffix[s] ^= suffix[d]
            changed |= {s} & member_group.keys()
            dirty = {before}
        else:
            if op == "ERASE":
                prefix[d] = 0
                suffix[d] = erased[index]
                state[d] = e[2]
            elif op in ("Q", "ZERO_Q"):
                need(state[d] == e[2], "query actual entrance frame")
                state[d] = e[3]
            elif op == "INIT":
                state[d] = e[2]
            after = label[state[d]]
            banks[before].remove(d)
            banks[after].add(d)
            if d in member_group:
                member_sources[before_frame].remove(d)
                member_sources[state[d]].add(d)
            dirty = {before, after}
        refresh(dirty, changed, index+1)
    for key in sorted(list(active)):
        flush(key, end+1)
    if diagnostic is None:
        need(state == word["final"], "complete final frame array")
        need(suffix == [1 << i for i in range(n)], "complete suffix identity closure")
    return {"scope": "complete" if diagnostic is None else "bounded diagnostic only",
            "cuts": end+1, "recomputed_contexts": evaluations,
            "weighted_cut_edge_contexts": sum(census.values()),
            "categories": [{"group": k[0], "base_ranks": k[1], "singleton_ranks": k[2], "augmented_ranks": k[3],
                            "cut_edge_contexts": v} for k, v in sorted(census.items())],
            "interval_digest": digest.hexdigest(), "intervals": transitions["context_intervals"],
            "excess_recomputed_contexts": transitions["excess_evaluations"],
            "excess_cut_edge_contexts": sum(v for k, v in census.items() if k[3][2] > max(k[1][2], k[2][2])),
            "peak_active_contexts": maximum_active,
            "witnesses": hits}


def run(diagnostic=None):
    word, frames, paths = read_inputs()
    prepared = setup(word, frames, paths)
    result = scan(word, prepared, diagnostic)
    return {"schema_version": 1, "source_pins": PINS,
            "group_members": [{"group": g, "entrance_shape": key[0], "exit_shape": key[1],
                              "members": list(members)} for g, (key, members) in enumerate(prepared[3])],
            "census": result, "controls": synthetic_controls(),
            "limits": ["Necessary scalar kernel/pairing gate only, including all inherited singleton comparisons.",
                       "No new typed continuation, native phase, independent target, restoration, price or kappa is certified.",
                       "The unchanged-bank zero boundary checks are predecessor coverage, not counted as a new result.",
                       "The published edge supplies only the normalized relocation premise; future scalar contacts remain unretargeted."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--diagnostic-events", type=int)
    options = parser.parse_args()
    need(options.diagnostic_events is None or 0 <= options.diagnostic_events <= 14794, "diagnostic event bound")
    result = run(options.diagnostic_events)
    payload = (json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+"\n").encode()
    if options.emit or options.diagnostic_events is not None:
        sys.stdout.buffer.write(payload)
    else:
        retained = HERE/"RESULT.json"
        need(retained.is_file(), "retained RESULT.json receipt required")
        parsed = strict(retained.read_bytes())
        need(type(parsed) is dict and type(parsed.get("schema_version")) is int and parsed["schema_version"] == 1,
             "typed RESULT receipt schema")
        need(canonical(parsed) == canonical(result), "exact typed RESULT receipt")
        print("PASS source-bound member-bank excess census and retained receipt")
