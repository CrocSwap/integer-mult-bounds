"""Exact expanded-domain G20 cut obstruction, produced by Nick Petalas.

The cut contract is due to Ali Romman, PR5679/5708 and PR5609.
This standalone implementation imports no predecessor executable. Apache-2.0.
"""
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = "research/g20-conjugation-admission/WORD.json.gz"
FRAMES = "research/g20-conjugation-admission/prior/prior/prior/source/vendor/g20/inputs/FRAMES.json"
MAX_FIELDS = 700
MAX_EVENTS = 20000
MAX_CONTEXTS = 30000


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(rows):
    """Unique rational row space, at most sixteen rows and eight columns."""
    basis = {}
    for source in rows:
        row = list(map(Fraction, source))
        for pivot in sorted(basis):
            factor = row[pivot]
            row = [x - factor*y for x, y in zip(row, basis[pivot])]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is None:
            continue
        factor = row[pivot]
        row = [x / factor for x in row]
        for old in tuple(basis):
            factor = basis[old][pivot]
            basis[old] = [x - factor*y for x, y in zip(basis[old], row)]
        basis[pivot] = row
    return tuple(tuple(row) for _, row in sorted(basis.items()))


def dependencies(rows):
    """A basis of all binary row dependencies, retaining coefficients."""
    basis, result = {}, []
    width = max((row.bit_length() for row in rows), default=0)
    for i, source in enumerate(rows):
        row, coefficients = source, 1 << i
        for _ in range(width + 1):
            if not row:
                result.append(coefficients)
                break
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row, coefficients
                break
            old, combination = basis[pivot]
            row ^= old
            coefficients ^= combination
        else:
            raise ValueError("dependency elimination bound")
    return result


def rank_low(rows):
    """Rank with the opposite pivot order and no dependency bookkeeping."""
    basis = {}
    width = max((row.bit_length() for row in rows), default=0)
    for source in rows:
        row = source
        for _ in range(width + 1):
            if not row:
                break
            pivot = (row & -row).bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
        else:
            raise ValueError("rank elimination bound")
    return len(basis)


def combine(rows, coefficients):
    value = 0
    require(coefficients.bit_length() <= len(rows), "coefficient width")
    for i, row in enumerate(rows):
        if coefficients >> i & 1:
            value ^= row
    return value


def eligible(rows, outside):
    masked = [row & outside for row in rows]
    kernel = dependencies(masked)
    require(len(kernel) == len(rows) - rank_low(masked), "kernel dimension")
    require(rank_low(kernel) == len(kernel), "kernel independence")
    require(all(combine(masked, x) == 0 for x in kernel), "kernel equations")
    return kernel, [combine(rows, x) for x in kernel]


def pairings(prefix, suffix, outside):
    left, inputs = eligible(prefix, outside)
    right, outputs = eligible(suffix, outside)
    boundary = [sum(((c & d).bit_count() & 1) << j
                    for j, d in enumerate(outputs)) for c in inputs]
    internal = [sum(((a & b).bit_count() & 1) << j
                    for j, b in enumerate(right)) for a in left]
    return len(left), len(right), rank_low(boundary), rank_low(internal)


def geometry(frames):
    require(1 <= len(frames) <= 2000, "frame inventory bound")
    for entry in frames.values():
        require(0 <= entry["dim"] <= 8, "frame dimension bound")
        require(len(entry["B"]) == entry["dim"], "frame row count")
        require(all(len(row) == 8 for row in entry["B"]), "frame width")
    spaces = {int(i): canonical(entry["B"]) for i, entry in frames.items()}
    shapes = sorted(set(spaces.values()))
    labels = {i: shapes.index(space) for i, space in spaces.items()}
    labels[None] = None
    return labels, shapes


def group_contract(word, labels, shapes, helper_begin):
    groups = defaultdict(set)
    owned = set(word["owned"])
    for h in range(helper_begin, len(word["start"])):
        if h not in owned:
            groups[labels[word["start"][h]], labels[word["final"][h]]].add(h)
    compatible = defaultdict(list)
    masks = {}
    full = (1 << len(word["start"])) - 1
    for group, members in groups.items():
        entrance, exit_frame = group
        masks[group] = full ^ sum(1 << h for h in members)
        for f, shape in enumerate(shapes):
            if not len(shapes[exit_frame]) < len(shape) < len(shapes[entrance]):
                continue
            if canonical(shapes[entrance] + shape) != shapes[entrance]:
                continue
            if canonical(shape + shapes[exit_frame]) == shape:
                compatible[f].append(group)
    return groups, compatible, masks


def suffix_start(events, n):
    columns = [1 << i for i in range(n)]
    erased = {}
    for k in reversed(range(len(events))):
        event = events[k]
        op, d = event[:2]
        if op == "ADD":
            columns[event[2]] ^= columns[d]
        elif op == "ERASE":
            erased[k] = columns[d]
            columns[d] = 0
    return columns, erased


def inspect_bank(f, cut, state, banks, prefix, suffix, contract, seen, counts, digest):
    groups, compatible, masks = contract
    if f not in compatible or not banks[f]:
        return
    slots = tuple(sorted(banks[f]))
    aa, bb = tuple(prefix[i] for i in slots), tuple(suffix[i] for i in slots)
    for group in compatible[f]:
        key = group, f, slots, aa, bb
        if key in seen:
            continue
        require(len(seen) < MAX_CONTEXTS, "context resource bound")
        seen.add(key)
        ldim, rdim, boundary_rank, internal_rank = pairings(aa, bb, masks[group])
        free_carrier = not (set(slots) & groups[group])
        counts["contexts"] += 1
        counts["without_helper_slot"] += int(free_carrier)
        counts["both_kernels_nonzero"] += int(ldim > 0 and rdim > 0)
        counts["boundary_nonzero"] += int(boundary_rank > 0)
        counts["internal_nonzero"] += int(internal_rank > 0)
        if free_carrier:
            counts["new_both_kernels_nonzero"] += int(ldim > 0 and rdim > 0)
            counts["new_boundary_nonzero"] += int(boundary_rank > 0)
            counts["new_internal_nonzero"] += int(internal_rank > 0)
        record = [cut, list(group), state[slots[0]], list(slots),
                  ldim, rdim, boundary_rank, internal_rank, free_carrier]
        digest.update((json.dumps(record, separators=(",", ":")) + "\n").encode())


def move(event, k, prefix, suffix, erased, state, labels, banks):
    op, d = event[:2]
    before = labels[state[d]]
    touched = {before}
    if op == "ADD":
        source, frame = event[2:]
        require(state[d] == state[source] == frame, "literal ADD common frame")
        prefix[d] ^= prefix[source]
        suffix[source] ^= suffix[d]
    elif op in ("ERASE", "INIT", "Q", "ZERO_Q"):
        if op == "ERASE":
            prefix[d] = 0
            suffix[d] = erased[k]
        if op in ("Q", "ZERO_Q"):
            require(state[d] == event[2], "query entrance")
            state[d] = event[3]
        else:
            state[d] = event[2]
        banks[before].remove(d)
        banks[labels[state[d]]].add(d)
        touched.add(labels[state[d]])
    else:
        raise ValueError("unknown event")
    return touched


def scan(word, labels, shapes, helper_begin=222):
    n, events = len(word["start"]), word["records"]
    require(1 <= n <= MAX_FIELDS and len(events) <= MAX_EVENTS, "word bounds")
    require(len(word["final"]) == n, "boundary lengths")
    for event in events:
        require(2 <= len(event) <= 5 and 0 <= event[1] < n, "event destination")
        if event[0] == "ADD":
            require(len(event) == 4 and 0 <= event[2] < n, "ADD source")
    contract = group_contract(word, labels, shapes, helper_begin)
    prefix = [1 << i for i in range(n)]
    suffix, erased = suffix_start(events, n)
    state = word["start"][:]
    banks = defaultdict(set)
    for i, frame in enumerate(state):
        banks[labels[frame]].add(i)
    counts, seen, digest = Counter(), set(), hashlib.sha256()
    for f in sorted(f for f in banks if f is not None):
        inspect_bank(f, -1, state, banks, prefix, suffix, contract, seen, counts, digest)
    for k, event in enumerate(events):
        touched = move(event, k, prefix, suffix, erased, state, labels, banks)
        for f in sorted(f for f in touched if f is not None):
            inspect_bank(f, k, state, banks, prefix, suffix, contract, seen, counts, digest)
    require(state == word["final"], "cut traversal reaches declared frames")
    require(suffix == [1 << i for i in range(n)], "suffix traversal closure")
    return dict(counts), digest.hexdigest(), contract[0]


def controls():
    checked = 0
    for rows in itertools.product(range(8), repeat=3):
        kernel = dependencies(rows)
        exhaustive = [x for x in range(8) if combine(rows, x) == 0]
        generated = {combine(kernel, x) for x in range(1 << len(kernel))}
        require(generated == set(exhaustive), "exhaustive dependency control")
        checked += 1
    # A genuine nonhelper carrier: swap an arbitrary helper into the borrowed
    # role, cross the intermediate frame there, return and undo the swap.
    shapes = [(), ((Fraction(1),) + (Fraction(0),)*7,),
              tuple(tuple(Fraction(i == j) for j in range(8)) for i in range(8))]
    labels = {0: 0, 1: 1, 2: 2, None: None}
    swap = [["ADD", 0, 1, 2], ["ADD", 1, 0, 2], ["ADD", 0, 1, 2]]
    word = {"start": [2, 2], "final": [0, 2], "owned": [1],
            "records": swap + [["Q", 1, 2, 1, 7], ["Q", 1, 1, 2, 7]]
            + swap + [["Q", 0, 2, 0, 8]]}
    result, _, _ = scan(word, labels, shapes, 0)
    require(result["new_boundary_nonzero"] == 1, "true outside-carrier accepted")
    require(pairings([1], [2], 0)[2] == 0, "orthogonal nonzero images")
    require(pairings([1], [1], 0)[2] == 1, "unit boundary channel")
    require(pairings([1], [1], 1)[2] == 0, "foreign-coordinate exclusion")
    return checked + 4


def load_sources():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    expected = {row["path"]: row["sha256"] for row in manifest["files"]
                if row["usage"] == "input"}
    require(set(expected) == {WORD, FRAMES}, "exact two-input boundary")
    payloads = {}
    for path in (WORD, FRAMES):
        raw = (ROOT / path).read_bytes()
        require(len(raw) <= 16 * 1024 * 1024, "input size bound")
        require(hashlib.sha256(raw).hexdigest() == expected[path], "source hash " + path)
        decoded = gzip.decompress(raw) if path.endswith(".gz") else raw
        require(len(decoded) <= 16 * 1024 * 1024, "decoded input bound")
        payloads[path] = json.loads(decoded)
    return payloads[WORD], payloads[FRAMES]["frames"]


def main():
    word, frames = load_sources()
    labels, shapes = geometry(frames)
    count_controls = controls()
    counts, digest, groups = scan(word, labels, shapes)
    require(counts["boundary_nonzero"] == 0, "zero boundary pairing at every context")
    report = {"claim_type": "finite exact certificate and scoped algebraic obstruction",
              "fields": len(word["start"]), "events": len(word["records"]),
              "all_cuts": len(word["records"]) + 1,
              "frame_classes": len(shapes),
              "helper_group_sizes": sorted(map(len, groups.values())),
              "counts": counts, "controls": count_controls,
              "context_digest": digest}
    print(json.dumps(report, sort_keys=True, indent=2))
    print("PASS_G20_FREE_CARRIER_SPLIT_OBSTRUCTION")


if __name__ == "__main__":
    main()
