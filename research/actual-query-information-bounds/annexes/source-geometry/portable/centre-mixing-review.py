"""Check the centre restriction from the native fields and cut intervals."""

from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path


import argparse

ANNEX = Path(__file__).resolve().parents[1]
PARENT = ANNEX.parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--out", required=True)
OUT = Path(parser.parse_args().out).resolve()
OUT.mkdir(parents=True, exist_ok=True)
HERE = ANNEX / "frozen" / 'lanes/bridge-review-20261017/centre-mixing-review-20261018'
LANES = HERE.parents[1]
CORE = LANES / "new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz"
CUTS = LANES / "oblique-native-20261017/interior-cut/ALL-CUT-EDGES.json.gz"
CERT = LANES / "coherent-port/centre-mixing-20261018/SUPPORT.json"
PINS = {
    "coherent-port/centre-mixing-20261018/MIXING.md": "e8ac0be5c3bd03cf853e9cb5718325d1f401eb1fc68d68869843ac6ded408903",
    "coherent-port/centre-mixing-20261018/check_support.py": "82d608f7220d9959925c2990fd717b028a2fce47fcf41ee9f061d0687c32f97c",
    "coherent-port/centre-mixing-20261018/SUPPORT.json": "251e656ce50b87f21149915d73b5c07d968d62aff2f47ccf2e1566cc5d6c756a",
    "coherent-port/centre-mixing-20261018/check_mixing.py": "fe017063d3b5bad93bf2f884813576e169d59daad1c5aec8051001e0a3476dc7",
    "coherent-port/centre-mixing-20261018/MIXING.json": "1a55e02768ad814b1441bfc616244a083ca3776007dcc0a370820059b83bdf11",
    "oblique-native-20261017/interior-cut/ALL-CUT-SUPPORT.md": "758f8750a833ba08b44d9fe1df555f747eef62bd53302993bca6cdae7769d431",
    "oblique-native-20261017/interior-cut/FRAME-SUPPORT.json": "6d9e1de85b7a2492bcef42514da240d74b81559c738aedac54cf65169a5a3fb5",
    "oblique-native-20261017/interior-cut/check_frame_support.py": "3a81e98c83e418408eb7490771867a11f491a6af403820ad722c43a51026b508",
    "oblique-native-20261017/interior-cut/inventory_new_edges.py": "6d77e20d6ef1a10951b7abeaa65852fad9161cc3b48e82d538a9748c3c9cc786",
    "new-native-recipes-20261017/sources/bw_adapters.py": "c5907050a9a7fa36d4fcba3ad4fe440d1bec2063360c095013891785ba65c3ce",
}


def need(test, label):
    if not test:
        raise ValueError(label)


def read_gzip(path, pin):
    raw = gzip.decompress(path.read_bytes())
    need(sha256(raw).hexdigest() == pin, str(path.name) + " input pin")
    return json.loads(raw)


def add(left, right, value=Q(1)):
    for key, coefficient in right.items():
        result = left.get(key, Q(0)) + value * coefficient
        if result:
            left[key] = result
        else:
            left.pop(key, None)


def lin(columns, value):
    answer = 0
    for j, column in enumerate(columns):
        if value >> j & 1:
            answer ^= column
    return answer


def inverse(columns):
    # Solve nine binary systems. Do not use a 512-value inverse table.
    rows = [sum(((columns[j] >> i) & 1) << j for j in range(9)) | (1 << (9+i))
            for i in range(9)]
    for j in range(9):
        pivot = next((k for k in range(j, 9) if rows[k] >> j & 1), None)
        need(pivot is not None, "Invertible binary warp")
        rows[pivot], rows[j] = rows[j], rows[pivot]
        for k in range(9):
            if k != j and rows[k] >> j & 1:
                rows[k] ^= rows[j]
    return [sum(((rows[i] >> (9+j)) & 1) << i for i in range(9)) for j in range(9)]


def space(vectors):
    result = {0}
    for value in vectors:
        result |= {x ^ value for x in result}
    need(len(result) == 1 << len(vectors), "Independent frame basis")
    return result


def row_key(row, allowed):
    return tuple(sorted((s, word, c.numerator, c.denominator)
                        for (s, word), c in row.items() if s not in allowed or word))


def tail_key(row):
    return tuple(sorted((t, c.numerator, c.denominator) for t, c in row.items()))


def add_interval(out, field, start, end, frame, value):
    if start < end and value:
        out.append((field, start, end, frame, value))


def replay_sources(item, centre_rows):
    word, events = item["canonical"], item["programs"]["forward"]
    size = len(word["start"])
    sources = set(range(112)) | set(range(224, size))
    allowed = {p for p in range(224, size) if word["start"][p] == 0}
    rows = {p: {(p, ()): Q(1)} for p in range(size+8)}
    frames = dict(enumerate(word["start"] + [0]*8))
    keys = {p: row_key(rows[p], allowed) for p in sources}
    starts = {p: 0 for p in sources}
    intervals, views, counts = [], [], Counter()
    spaces = [space(vectors) for vectors in word["frames"]]
    canonical_start = events.index(["phase", "A"])
    canonical_end = events.index(["phase", "exit_adapters"])
    need((canonical_start, canonical_end) == (7502, 17249), "Actual canonical interval")
    need(all(e[0] in ("scalar", "climb", "warp", "phase")
             for e in events[canonical_start:canonical_end]), "No wrapper inside the canonical interval")
    maps = {record["op"]: record["G_columns"] for record in word["warps"]}
    maps.update({-k: inverse(v) for k, v in list(maps.items())})
    for s in range(112):
        need(word["ports"][s] in spaces[frames[s]], "Initial X line")
        need(all((v & word["ports"][s]).bit_count() % 2 == 0
                 for v in spaces[word["final"][112+s]]), "Final Y hyperplane")

    def slot(value):
        return value[1] if value[0] == "L" else size+value[1] if value[0] == "C" else ("Z", value[1])

    for pos, event in enumerate(events):
        tag, changed = event[0], None
        if pos == canonical_start:
            for field, row in rows.items():
                if isinstance(field, int) and field < 112:
                    need(row == {(field, ()): Q(1)}, "The exterior prefix preserves each X input")
                else:
                    need(not any(s < 112 for s, _ in row), "The exterior prefix has no other X branch")
        counts[tag] += 1
        if tag == "scalar":
            gate, frame = event[1:]
            op, target = gate[0], slot(gate[1])
            if pos >= canonical_end:
                need(not (isinstance(target, int) and 112 <= target < 224), "The exterior suffix makes no Y write")
            old_frame = frames.get(target)
            if op == "clear":
                rows[target], frames[target] = {}, frame
            else:
                need(frames[target] == frame, "Literal scalar target frame")
                if op == "scale":
                    q = Q(*gate[2:4])
                    rows[target] = {k: q*v for k, v in rows[target].items() if q*v}
                else:
                    source = slot(gate[2])
                    need(source != target and frames[source] == frame, "Literal scalar source frame")
                    if op == "copy":
                        rows[target] = dict(rows[source])
                    else:
                        need(op == "add", "Known scalar operation")
                        need(not (isinstance(source, int) and 112 <= source < 224)
                             or isinstance(target, int) and 112 <= target < 224,
                             "No Y feedback to fixed sources")
                        add(rows[target], rows[source], Q(*gate[3:5]))
            changed = target
        elif tag == "climb":
            target, old_frame, new, rank = event[2:6]
            need(frames[target] == old_frame and spaces[old_frame] < spaces[new], "Nested positive climb")
            need(len(word["frames"][new]) - len(word["frames"][old_frame]) == rank, "Exact climb rank")
            frames[target], changed = new, target
        elif tag == "warp":
            target, op, old_frame, new = slot(event[1]), event[2], event[3], event[4]
            need(frames[target] == old_frame, "Literal warp input frame")
            need({lin(maps[op], v) for v in spaces[old_frame]} == spaces[new], "Actual warp frame image")
            updated = {}
            for (s, history), coefficient in rows[target].items():
                history = history[1:] if history and history[0] == -op else (op,) + history
                add(updated, {(s, history): coefficient})
            rows[target], frames[target], changed = updated, new, target
        elif tag == "zero_buffer":
            target = ("Z", event[2])
            if event[1] == "alloc":
                need(target not in rows, "Private buffer allocation")
                rows[target], frames[target] = {}, 1
            else:
                need(not rows[target], "Private buffer return")
                del rows[target], frames[target]
        elif tag in ("adapter", "residual_adapter"):
            target = event[2]
            x_terms = [(s, history) for s, history in rows[target] if s < 112]
            if x_terms:
                views.append({"event": pos, "kind": event[:2], "field": target,
                              "frame": frames[target], "X_terms": len(x_terms)})
                if target >= 224:
                    need(tag == "adapter" and event[1] == "new_to_old" and frames[target] == 1,
                         "Every X-dependent helper view change is at FULL")
        else:
            need(tag == "phase", "Known event kind")
        if changed in sources:
            new_key = row_key(rows[changed], allowed)
            if new_key != keys[changed] or frames[changed] != old_frame:
                add_interval(intervals, changed, starts[changed], pos+1, old_frame, keys[changed])
                starts[changed], keys[changed] = pos+1, new_key
        if tag == "scalar" and isinstance(changed, int) and changed >= size:
            need(not any(s < 112 for s, _ in rows[changed]), "Owned fields have no X input branch")
    for field in sources:
        add_interval(intervals, field, starts[field], len(events)+1, frames[field], keys[field])
    need([frames[p] for p in range(size)] == word["final"], "All final frames")
    for p in range(size):
        if not 112 <= p < 224:
            need(rows[p] == {(p, ()): Q(1)}, "Every fixed source and helper restores")
        else:
            target = p-112
            goal = {(p, ()): Q(1), (target, ()): Q(1)}
            for row in centre_rows:
                add(goal, {(s, ()): value for s, value in row.items()}, -row.get(target, Q(0))/4)
            need(rows[p] == goal, "Exact clean-J response on every arbitrary input")
    need(not rows[size] and all(rows[size+p] == {(size+p, ()): Q(1)} for p in range(1, 8)), "Owned endpoint")
    return intervals, views, dict(counts), [canonical_start, canonical_end]


def replay_tails(item):
    word, events = item["canonical"], item["programs"]["forward"]
    rows = [{t: Q(1)} for t in range(112)]
    frames = word["final"][112:224].copy()
    ends = [len(events)+1]*112
    intervals = []
    for pos in range(len(events)-1, -1, -1):
        event, changed = events[pos], None
        if event[0] == "climb" and 112 <= event[2] < 224:
            changed = event[2]-112
            old_key, old_frame = tail_key(rows[changed]), frames[changed]
            need(old_frame == event[4], "Reverse Y frame")
            frames[changed] = event[3]
        elif event[0] == "scalar":
            gate = event[1]
            if gate[1][0] == "L" and 112 <= gate[1][1] < 224:
                target = gate[1][1]-112
                if gate[0] == "scale":
                    changed = target
                    old_key, old_frame = tail_key(rows[changed]), frames[changed]
                    rows[target] = {k: Q(*gate[2:4])*v for k, v in rows[target].items()}
                elif gate[0] == "add" and gate[2][0] == "L" and 112 <= gate[2][1] < 224:
                    changed = gate[2][1]-112
                    old_key, old_frame = tail_key(rows[changed]), frames[changed]
                    add(rows[changed], rows[target], Q(*gate[3:5]))
        elif event[0] == "warp":
            need(not (event[1][0] == "L" and 112 <= event[1][1] < 224), "No Y warp")
        if changed is not None:
            new_key = tail_key(rows[changed])
            if new_key != old_key or frames[changed] != old_frame:
                add_interval(intervals, changed, pos+1, ends[changed], old_frame, old_key)
                ends[changed] = pos+1
    for target in range(112):
        add_interval(intervals, target, 0, ends[target], frames[target], tail_key(rows[target]))
    need(rows == [{t: Q(1)} for t in range(112)] and frames == [0]*112, "Y scalar subword is identity")
    return intervals


def join_intervals(source, target):
    groups = defaultdict(list)
    for kind, intervals in enumerate((source, target)):
        for index, (_, lo, hi, frame, value) in enumerate(intervals):
            groups[frame].append((lo, 1, kind, index, value))
            groups[frame].append((hi, 0, kind, index, value))
    products, overlaps = set(), 0
    for events in groups.values():
        active = [{}, {}]
        for _, start, kind, index, value in sorted(events):
            if not start:
                del active[kind][index]
                continue
            for other in active[1-kind].values():
                products.add((value, other) if kind == 0 else (other, value))
                overlaps += 1
            active[kind][index] = value
    return products, overlaps


def determinant_fraction(matrix):
    rows = [[Q(x) for x in row] for row in matrix]
    det = Q(1)
    for j in range(len(rows)):
        pivot = next((k for k in range(j, len(rows)) if rows[k][j]), None)
        if pivot is None:
            return Q(0)
        if pivot != j:
            rows[pivot], rows[j] = rows[j], rows[pivot]
            det = -det
        value = rows[j][j]
        det *= value
        rows[j] = [x/value for x in rows[j]]
        for k in range(j+1, len(rows)):
            value = rows[k][j]
            if value:
                rows[k] = [x-value*y for x, y in zip(rows[k], rows[j])]
    return det


def two_basis_certificate(r, ports):
    left = [0, 7, 20, 27, 36, 46, 57, 111]
    right = [3, 6, 18, 21, 89, 92, 105, 109]
    disconnected = [21, 37, 47, 76, 81, 87, 92, 110]

    def gram(a, b):
        return [[sum(r[k][s]*r[k][t] for k in range(8)) for t in b] for s in a]

    def check_basis(fields):
        need(gram(fields, fields) == [[4*int(i == j) for j in range(8)] for i in range(8)],
             "Actual orthogonal centre basis")
        need(all((ports[s] & ports[t]).bit_count() % 2 for s in fields for t in fields),
             "All within-basis pairs have binary dot one")

    def components(matrix):
        neighbours = {i: set() for i in range(16)}
        for i in range(8):
            for j in range(8):
                if matrix[i][j]:
                    neighbours[i].add(8+j)
                    neighbours[8+j].add(i)
        groups, tree = [], []
        unseen = set(range(16))
        while unseen:
            seed = min(unseen)
            group, queue = {seed}, [seed]
            unseen.remove(seed)
            for node in queue:
                for next_node in sorted(neighbours[node] & unseen):
                    unseen.remove(next_node)
                    group.add(next_node)
                    queue.append(next_node)
                    tree.append([node, next_node])
            groups.append(sorted(group))
        return groups, tree

    for fields in (left, right, disconnected):
        check_basis(fields)
    numerator = gram(left, right)
    need(all(x in (-2, 0, 2) for row in numerator for x in row), "Every overlap is zero or a dyadic unit")
    groups, tree = components(numerator)
    need(len(groups) == 1 and len(tree) == 15, "Connected two-basis graph")
    control_groups, _ = components(gram(left, disconnected))
    need(len(control_groups) == 2 and all(len(group) == 8 for group in control_groups),
         "A real disconnected basis pair has two scalar blocks")
    return dict(core_decompressed_sha256="a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa",
                left_ports=left, right_ports=right, overlap_denominator=4,
                overlap_numerator=numerator, components=groups, spanning_tree=tree,
                disconnected_control_ports=disconnected, disconnected_control_components=control_groups,
                exact_common_diagonal_algebra="scalar multiples of I8")


def main():
    for path, pin in PINS.items():
        need(sha256((LANES/path).read_bytes()).hexdigest() == pin, "Pinned producer file " + path)
    core = read_gzip(CORE, "a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa")
    cuts = read_gzip(CUTS, "18c89367243fc7c09411f28a8022884130373ce4886de806f4b011edec030418")
    cert = json.loads(CERT.read_text())
    supplied = set()
    for product in cuts["products"]:
        source = tuple(sorted((s, tuple(sign*op[1] for op, sign in history), num, den)
                              for s, history, num, den in cuts["source_rows"][product["source_row"]]["constrained"]))
        tail = tuple(tuple(x) for x in cuts["tail_columns"][product["tail_column"]])
        supplied.add((source, tail))
    reports = {}
    centre_rows = [{int(k): Q(v) for k, v in row.items()} for row in core["R"]]
    for name, item in core["providers"].items():
        sources, views, counts, canonical_cuts = replay_sources(item, centre_rows)
        tails = replay_tails(item)
        actual, overlaps = join_intervals(sources, tails)
        need(actual == supplied, "Independent interval inventory equals the supplied product set")
        word = item["canonical"]
        spaces = [space(vectors) for vectors in word["frames"]]
        maps = {record["op"]: record["G_columns"] for record in word["warps"]}
        maps.update({-k: inverse(v) for k, v in list(maps.items())})
        checks, history_lengths = set(), Counter()
        for _, _, _, frame, row in sources:
            for s, history, _, _ in row:
                if s >= 112 or (frame, s, history) in checks:
                    continue
                checks.add((frame, s, history))
                value = word["ports"][s]
                for op in reversed(history):
                    value = lin(maps[op], value)
                need(value in spaces[frame], "Actual X term support at every source interval")
                history_lengths[len(history)] += 1
        tail_checks = set()
        for _, _, _, frame, row in tails:
            for t, _, _ in row:
                if (frame, t) not in tail_checks:
                    tail_checks.add((frame, t))
                    need(all((x & word["ports"][t]).bit_count() % 2 == 0 for x in spaces[frame]),
                         "Every reverse tail frame is inside the target hyperplane")
        reports[name] = dict(source_intervals=len(sources), target_intervals=len(tails),
                             interval_overlaps=overlaps, distinct_products=len(actual),
                             actual_X_term_frame_checks=len(checks), history_lengths=dict(history_lengths),
                             target_frame_checks=len(tail_checks), event_counts=counts,
                             canonical_rewiring_cuts=canonical_cuts,
                             X_dependent_view_changes=views)
        print(name, len(actual), "products from", overlaps, "interval overlaps", flush=True)
    r = [[int(row.get(str(p), 0)) for p in range(112)] for row in core["R"]]
    need([[sum(r[a][p]*r[b][p] for p in range(112)) for b in range(8)] for a in range(8)]
         == [[56*int(a == b) for b in range(8)] for a in range(8)], "Actual full centre Gram matrix")
    ports = core["providers"]["base"]["canonical"]["ports"]
    equations = []
    for t in range(112):
        need(sum(r[a][t]**2 for a in range(8)) == 4 and ports[t].bit_count() % 2, "Each port is odd and each R column has norm four")
        for s in range(112):
            if t != s and (ports[t] & ports[s]).bit_count() % 2:
                row = [r[a][t]*r[b][s] for a in range(8) for b in range(8)]
                need(sum(row[9*a] for a in range(8)) == 0, "Scalar identity satisfies all constraints")
                equations.append((t, s, row))
    need(len(equations) == 6608, "Every forbidden off-diagonal pair")
    two_bases = two_basis_certificate(r, ports)
    (OUT/"TWO-BASES.json").write_text(json.dumps(two_bases, indent=2, sort_keys=True)+"\n")
    by_pair = {(t, s): row for t, s, row in equations}
    matrix = [[by_pair[tuple(pair)][j] for j in cert["centre_entry_columns"]]
              for pair in cert["independent_pairs"]]
    need(len(matrix) == 63 and cert["centre_entry_columns"] == list(range(63)), "Full centre matrix certificate")
    det = determinant_fraction(matrix)
    need(det == -(1 << 71), "Independent rational determinant")
    projection = [Q(a == b)-Q(1, 8) for a in range(8) for b in range(8)]
    failures = [(t, s) for t, s, row in equations if sum(x*y for x, y in zip(row, projection))]
    need(failures, "Dense rank-seven projection is rejected")
    duplicated = [row[:] for row in matrix]
    duplicated[-1] = duplicated[0][:]
    need(determinant_fraction(duplicated) == 0, "Duplicate certificate row is rejected")
    report = dict(status="PASS_INDEPENDENT_NATIVE_CENTRE_REVIEW", producer_pins=PINS,
                  core_decompressed_sha256="a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa",
                  inventory_decompressed_sha256="18c89367243fc7c09411f28a8022884130373ce4886de806f4b011edec030418",
                  providers=reports, forbidden_pairs=len(equations), determinant=str(det),
                  two_basis_certificate=two_bases,
                  exact_kernel="scalar multiples of I8", dense_rank_seven_failures=len(failures),
                  negative_controls=["dense rank-seven projection", "duplicate certificate row"],
                  checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/"REVIEW.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(report["status"], "determinant", det, flush=True)


if __name__ == "__main__":
    main()
