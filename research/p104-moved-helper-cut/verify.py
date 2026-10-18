# SPDX-License-Identifier: Apache-2.0
"""Literal-subspace audit of PR3124's moved helper 13.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
No predecessor Python is imported. Model/method credit: README.md.
"""
import argparse
import hashlib
import json
from collections import Counter, defaultdict, deque
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
HELPER, COUNT = 13, 208


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)


def load():
    inputs = {}
    for row in read_json(PACKAGE / "SOURCES.json")["files"]:
        if row["usage"] != "input":
            continue
        raw = (ROOT / row["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])
        inputs[Path(row["path"]).name] = json.loads(raw, object_pairs_hook=unique)
    require(set(inputs) == {"WITNESS.json", "CONTROL.json", "CERTIFICATE.json", "LOWRANK-WITNESS.json",
                            "P104-FIXTURE.json"}, "input inventory")
    return inputs


def points(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def encode(values):
    return sum(1 << x for x in set(values))


def extend(space, vector):
    return space | encode(x ^ vector for x in points(space))


def span(rows):
    space = 1
    for vector in rows:
        require(type(vector) is int and 0 < vector < 512, "binary label")
        require(not (space >> vector) & 1, "independent basis")
        space = extend(space, vector)
    return space


def dim(space):
    size = space.bit_count()
    require(size > 0 and size & (size - 1) == 0, "frame cardinality")
    return size.bit_length() - 1


def subset(a, b):
    return a & b == a


def basis(space):
    generated, result = 1, []
    for x in points(space):
        if not (generated >> x) & 1:
            result.append(x)
            generated = extend(generated, x)
    require(generated == space, "linear subspace")
    return result


def data_paths(word):
    paths = {f"{k}{i}": [span(word["initial_frames"][f"{k}{i}"])]
             for k in "XY" for i in range(104)}
    require(len(word["program"]) == 4058, "original word length")
    for event in word["program"]:
        op, name = event[:2]
        if op == "transport" and name in paths:
            before, after = span(event[2]), span(event[3])
            require(before == paths[name][-1] and before != after and subset(before, after), "data chronology")
            require(dim(after) - dim(before) == event[4], "data rank")
            paths[name].append(after)
        elif op != "transport":
            require(op in {"add", "copy", "zero", "erase"}, "opcode")
            require(not name.startswith("X"), "immutable source")
            if op in {"add", "copy"}:
                require(not event[2].startswith("Y"), "unread target")
    for name, chain in paths.items():
        require(chain[-1] == span(word["final_frames"][name]), "data final frame")
        expected = (1, 9) if name[0] == "X" else (0, 8)
        require((dim(chain[0]), dim(chain[-1])) == expected, "data dimensions")
    return paths


def quotient_layers():
    """Every literal subspace of F2^5, by exhaustive one-vector extension."""
    layers = [{1}]
    for _ in range(5):
        layers.append({extend(s, v) for s in layers[-1] for v in range(1, 32) if not (s >> v) & 1})
    require(list(map(len, layers)) == [1, 31, 155, 155, 31, 1], "quotient completeness")
    return [sorted(layer) for layer in layers]


def helper_frames(low, high, line, cap, quotients):
    require(dim(low) == 2 and dim(high) == 7 and subset(low, high), "helper endpoints")
    current, generators = low, []
    for vector in points(high):
        if not (current >> vector) & 1:
            generators.append(vector)
            current = extend(current, vector)
    require(current == high and len(generators) == 5, "quotient generators")
    cosets = []
    for q in range(32):
        value = 0
        for i, generator in enumerate(generators):
            if q >> i & 1:
                value ^= generator
        cosets.append(encode(x ^ value for x in points(low)))
    require(len(set(cosets)) == 32, "distinct cosets")
    frames = {1: {line}, 8: {cap}}
    for d, layer in enumerate(quotients, 2):
        frames[d] = {sum(cosets[q] for q in points(s)) for s in layer}
    return frames


def geometry(inputs):
    paths = data_paths(inputs["LOWRANK-WITNESS.json"])
    cert, witness = inputs["CERTIFICATE.json"], inputs["WITNESS.json"]
    matching = witness["pairing"]
    require(witness["cycle"] == [13, 203, 191, 63], "named cycle")
    require(len(matching) == COUNT and all(type(x) is int for x in matching)
            and sorted(matching) == list(range(COUNT)), "perfect matching")
    previous = inputs["CONTROL.json"]["pairing"]
    expected = list(previous)
    cycle = witness["cycle"]
    for i, h in enumerate(cycle):
        expected[h] = previous[cycle[(i + 1) % len(cycle)]]
    require(matching == expected, "exact alternating-cycle orientation")
    lines = [paths[f"X{s}"][0] for s in range(104)]
    caps = [paths[f"Y{t}"][-1] for t in range(104)]
    require(len(set(lines)) == len(set(caps)) == 104, "distinct endpoints")
    lows, highs = [], []
    for i in range(104):
        for form in cert["forms"]["departure"][i]:
            lows.append(extend(lines[i], form))
        for form in cert["forms"]["arrival"][i]:
            highs.append(encode(x for x in points(caps[i]) if (x & form).bit_count() % 2 == 0))
    q = quotient_layers()
    frames = [helper_frames(lows[h], highs[matching[h]], lines[h // 2], caps[matching[h] // 2], q)
              for h in range(COUNT)]
    read_frames, write_frames = defaultdict(int), defaultdict(int)
    for s in range(104):
        for frame in paths[f"X{s}"]:
            read_frames[frame] |= 1 << s
    for t in range(104):
        for frame in paths[f"Y{t}"]:
            write_frames[frame] |= 1 << t
    return {"paths": paths, "matching": matching, "lows": lows, "highs": highs,
            "frames": frames, "reads": read_frames, "writes": write_frames}


def required_coefficients(fixture):
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            root = [0] * 8
            root[i], root[j] = 2, 2 * sign
            roots.append(tuple(root))
    roots.extend((1, *tail) for tail in product((-1, 1), repeat=7) if tail.count(-1) % 2 == 0)
    removed = fixture["section4_explicit_P104"]
    ports = sorted(set(roots) - {tuple(x) for x in removed["F0"] + removed["C"]})
    require(len(roots) == 120 and len(ports) == 104, "root reconstruction")
    matrix = [[Fraction(8 * (t == s) - sum(a * b for a, b in zip(ports[t], ports[s])), 8)
               for s in range(104)] for t in range(104)]
    demands = [encode(s for s in range(104) if matrix[t][s]) for t in range(104)]
    require(sum(x.bit_count() for x in demands) == 4992, "correction demand count")
    require(all(x.bit_count() == 48 for x in demands), "48 demands per target")
    return matrix, demands, ports


def source_response(word, correction):
    """Bind the independently reconstructed Gram matrix to all X columns.

    Transports preserve logical rows; their native realization is inherited.
    Independent helper/target entrance columns are not replayed here.
    """
    frames = {name: span(b) for name, b in word["initial_frames"].items()}
    rows = {name: ({int(name[1:]): Fraction(1)} if name.startswith("X") else {})
            for name in frames}
    scalar_adds, private_copies = 0, 0
    for event in word["program"]:
        op, dst = event[:2]
        if op == "transport":
            require(frames[dst] == span(event[2]), "logical replay transport entry")
            frames[dst] = span(event[3])
        elif op == "zero":
            require(dst not in frames, "private allocation is fresh")
            frames[dst], rows[dst] = span(event[2]), {}
        elif op == "erase":
            require(frames[dst] == span(event[2]), "private discard frame")
            del frames[dst]
            del rows[dst]
        elif op == "copy":
            src = event[2]
            require(frames[dst] == frames[src] == span(event[3]) and not rows[dst], "private copy boundary")
            rows[dst] = dict(rows[src])
            private_copies += 1
        elif op == "add":
            src, coefficient = event[2], Fraction(event[3])
            require(dst != src and frames[dst] == frames[src] == span(event[4]), "common-frame ADD")
            for source, value in rows[src].items():
                total = rows[dst].get(source, 0) + coefficient * value
                if total:
                    rows[dst][source] = total
                else:
                    rows[dst].pop(source, None)
            scalar_adds += 1
        else:
            raise ValueError("logical replay opcode")
    require(frames == {name: span(b) for name, b in word["final_frames"].items()}, "logical replay final frames")
    for name, row in rows.items():
        if name.startswith("X"):
            require(row == {int(name[1:]): 1}, "source column preservation")
        elif name.startswith("Y"):
            target = int(name[1:])
            for source in range(104):
                require(row.get(source, 0) == int(target == source) - correction[target][source],
                        "Gram/channel port-order binding")
        else:
            require(not row, "helper has no final source response")
    return {"source_columns": 104, "target_coefficients": 104 * 104,
            "events": len(word["program"]), "scalar_adds": scalar_adds,
            "private_copies": private_copies, "required_X1_Y40_correction": str(correction[40][1]),
            "native_realization_replayed": False, "dirty_entrance_columns_replayed": False}


def incidence(g):
    adjacency, reads, writes = {}, {}, {}
    for d in range(1, 9):
        members = defaultdict(list)
        for h in range(COUNT):
            for frame in g["frames"][h][d]:
                members[frame].append(h)
        a, r, w = [set() for _ in range(COUNT)], [0] * COUNT, [0] * COUNT
        for frame, helpers in members.items():
            for h in helpers:
                a[h].update(helpers)
                r[h] |= g["reads"][frame]
                w[h] |= g["writes"][frame]
        adjacency[d], reads[d], writes[d] = a, r, w
    direct = [0] * 104
    for frame, source_bits in g["reads"].items():
        for t in points(g["writes"][frame]):
            direct[t] |= source_bits
    return adjacency, reads, writes, direct


def profiles(g):
    """Merge flags only when every incident edge/read/write agrees."""
    layers = [sorted(g["frames"][HELPER][d]) for d in range(2, 8)]
    successors = [{x: [y for y in layers[i + 1] if subset(x, y)] for x in layer}
                  for i, layer in enumerate(layers[:-1])]
    per_frame = {}
    for d in range(1, 9):
        for f in g["frames"][HELPER][d]:
            per_frame[d, f] = (tuple(h for h in range(COUNT) if f in g["frames"][h][d]),
                               g["reads"][f], g["writes"][f])
    result = {}

    def visit(flag):
        if len(flag) < 6:
            for nxt in successors[len(flag) - 1][flag[-1]]:
                visit(flag + [nxt])
            return
        full = [next(iter(g["frames"][HELPER][1])), *flag, next(iter(g["frames"][HELPER][8]))]
        key = tuple(per_frame[d, f] for d, f in enumerate(full, 1))
        if key not in result:
            result[key] = {"count": 0, "flag": full}
        result[key]["count"] += 1

    visit([layers[0][0]])
    require(sum(x["count"] for x in result.values()) == 9765, "complete flag count")
    return result


def constrain(base, profile):
    adjacency, reads, writes, direct = base
    aa, rr, ww = {}, {}, {}
    for d in range(1, 9):
        neighbors, read, write = profile[d - 1]
        aa[d] = [set(row) - {HELPER} for row in adjacency[d]]
        aa[d][HELPER] = set(neighbors)
        for h in neighbors:
            aa[d][h].add(HELPER)
        rr[d], ww[d] = list(reads[d]), list(writes[d])
        rr[d][HELPER], ww[d][HELPER] = read, write
    return aa, rr, ww, direct


def flag_profile(g, flag, require_nested=True):
    require(len(flag) == 8, "eight flag layers")
    for d, frame in enumerate(flag, 1):
        require(frame in g["frames"][HELPER][d], "flag frame in endpoint interval")
    if require_nested:
        require(all(subset(a, b) for a, b in zip(flag, flag[1:])), "nested flag")
    return tuple((tuple(h for h in range(COUNT) if f in g["frames"][h][d]),
                  g["reads"][f], g["writes"][f]) for d, f in enumerate(flag, 1))


def cut_receipt(g, base, matrix, demands):
    """Source-bound small proof certificate, independent of the flag census."""
    adjacency, reads, writes, direct = base
    # Exact complete neighborhoods, not selected edges from a path search.
    expected = {
        13: [[12], [], [63, 185], [63, 91, 118, 185], [63, 91, 118, 185], [91], [], [124]],
        17: [[16], [], [], [], [], [], [], [83]],
        83: [[82], [], [], [91], [91], [91], [], [17]],
        91: [[90], [], [], [13, 83], [13, 83], [13, 83], [], [183]],
    }
    contacts, local_reads, local_writes = {}, {}, {}
    for h in expected:
        contacts[str(h)] = [sorted(adjacency[d][h] - {h}) for d in range(1, 9)]
        local_reads[str(h)] = [list(points(reads[d][h])) for d in range(1, 9)]
        local_writes[str(h)] = [list(points(writes[d][h])) for d in range(1, 9)]
        require(contacts[str(h)] == expected[h], "complete local contact boundary")
        require(local_reads[str(h)] == [[h // 2]] + [[] for _ in range(7)], "local source boundary")
        # The dimension-one partner cannot inject a different source there.
        component = adjacency[1][h]
        require(component == {h, h ^ 1}, "source-line component")
        require(all(reads[1][k] == 1 << (h // 2) for k in component), "paired source only")
    writers = [[d, h] for d in range(1, 9) for h in range(COUNT) if writes[d][h] >> 40 & 1]
    require(writers == [[8, 17], [8, 83]], "all Y40 writers")
    require(direct[40] == 0, "no direct Y40 source read")
    require(g["matching"][91] == 8 and g["matching"][13] == 180, "named arrival assignment")
    separators = []
    for incoming in (63, 118, 185):
        excluded = g["lows"][incoming] & ~g["highs"][8]
        require(excluded != 0, "nested relay separator")
        separators.append({"incoming": incoming, "outgoing": 91,
                           "vector": min(points(excluded)),
                           "incoming_departure_basis": basis(g["lows"][incoming]),
                           "outgoing_arrival_slot": 8})
    support_bound = {6, 8, 41, 45}
    missing = [s for s in points(demands[40]) if s not in support_bound]
    require(len(missing) == 44 and matrix[40][1] == Fraction(1, 2), "cut coefficient")
    # One intentionally nonnested choice restores the missing X1 -> Y40 path.
    broken_bases = [[200], [200, 288], [104, 160, 288], [2, 53, 200, 277],
                    [13, 37, 64, 133, 261], [2, 13, 37, 64, 133, 261],
                    [2, 13, 16, 37, 64, 133, 261], [1, 2, 12, 16, 36, 64, 132, 260]]
    broken = [span(b) for b in broken_bases]
    require(not subset(broken[3], broken[4]), "control breaks nestedness")
    profile = flag_profile(g, broken, require_nested=False)
    controlled = constrain(base, profile)
    output, _ = propagate(controlled)
    require(output == bfs_outputs(controlled), "nonnested control algorithms agree")
    require(output[40] >> 1 & 1, "nonnested control restores distinguished path")
    return {"target": 40, "distinguished_source": 1, "required_coefficient": "1/2",
            "source_support_upper_bound": sorted(support_bound), "missing_required_sources": missing,
            "complete_contacts_by_dimension": contacts, "local_reads_by_dimension": local_reads,
            "local_writes_by_dimension": local_writes, "all_target_writers": writers,
            "separators": separators, "arrival_8_basis": basis(g["highs"][8]),
            "nonnested_positive_control": {"flag_bases": broken_bases, "X1_reaches_Y40": True}}


def propagate(network, count=COUNT, target_count=104):
    """Exact source-support closure of the relaxed layered graph."""
    adjacency, reads, writes, direct = network
    state, outputs, traces = [0] * count, list(direct), []
    for d in sorted(adjacency):
        state = [x | r for x, r in zip(state, reads[d])]
        unseen = set(range(count))
        while unseen:
            seed = min(unseen)
            component, todo, sources = {seed}, [seed], 0
            unseen.remove(seed)
            while todo:
                h = todo.pop()
                sources |= state[h]
                for neighbor in adjacency[d][h]:
                    if neighbor not in component:
                        component.add(neighbor)
                        unseen.discard(neighbor)
                        todo.append(neighbor)
            for h in component:
                state[h] = sources
        for h in range(count):
            for t in points(writes[d][h]):
                require(t < target_count, "target index")
                outputs[t] |= state[h]
        traces.append(list(state))
    return outputs, traces


def bfs_outputs(network, source_count=104, count=COUNT):
    """Separate per-source graph traversal, without component propagation."""
    adjacency, reads, writes, direct = network
    layers, output = sorted(adjacency), list(direct)
    for s in range(source_count):
        todo = deque((i, h) for i, d in enumerate(layers) for h in range(count) if reads[d][h] >> s & 1)
        visited = set(todo)
        while todo:
            i, h = todo.popleft()
            d = layers[i]
            for t in points(writes[d][h]):
                output[t] |= 1 << s
            following = [(i, k) for k in adjacency[d][h]]
            if i + 1 < len(layers):
                following.append((i + 1, h))
            for vertex in following:
                if vertex not in visited:
                    visited.add(vertex)
                    todo.append(vertex)
    return output


def derive(inputs):
    g = geometry(inputs)
    matrix, demands, _ = required_coefficients(inputs["P104-FIXTURE.json"])
    binding = source_response(inputs["LOWRANK-WITNESS.json"], matrix)
    base = incidence(g)
    cut = cut_receipt(g, base, matrix, demands)
    relaxed, _ = propagate(base)
    require(relaxed == bfs_outputs(base), "relaxed component/BFS agreement")
    require(all(need & got == need for need, got in zip(demands, relaxed)), "relaxed matching passes")
    groups, histogram, rows, union = profiles(g), Counter(), [], [0] * 104
    for profile, record in sorted(groups.items()):
        net = constrain(base, profile)
        outputs, _ = propagate(net)
        require(outputs == bfs_outputs(net), "constrained component/BFS agreement")
        missing = sum((need & ~got).bit_count() for need, got in zip(demands, outputs))
        histogram[missing] += record["count"]
        union = [a | b for a, b in zip(union, outputs)]
        rows.append({"multiplicity": record["count"], "missing": missing,
                     "flag_bases": [basis(frame) for frame in record["flag"]],
                     "source_support_by_target_hex": [f"{x:026x}" for x in outputs]})
    always_missing = [[t, s] for t in range(104) for s in points(demands[t] & ~union[t])]
    return {"schema_version": 1, "helper": HELPER,
            "matching_sha256": hashlib.sha256(canonical(g["matching"]).encode()).hexdigest(),
            "quotient_subspace_counts": [1, 31, 155, 155, 31, 1],
            "flags": sum(histogram.values()), "contact_profiles": len(groups),
            "missing_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "relaxed_missing": 0, "always_missing_pairs": always_missing,
            "first_missing_coefficient": (str(matrix[always_missing[0][0]][always_missing[0][1]])
                                          if always_missing else None),
            "source_response_binding": binding, "cut": cut, "classes": rows, "no_new_kappa": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit derived receipt to stdout")
    parser.add_argument("--cut-only", action="store_true", help="check the small cut without enumerating flags")
    args = parser.parse_args()
    inputs = load()
    if args.cut_only:
        g = geometry(inputs)
        matrix, demands, _ = required_coefficients(inputs["P104-FIXTURE.json"])
        source_response(inputs["LOWRANK-WITNESS.json"], matrix)
        result = cut_receipt(g, incidence(g), matrix, demands)
    else:
        result = derive(inputs)
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = read_json(PACKAGE / "RESULT.json")
        if args.cut_only:
            expected = expected["cut"]
        require(canonical(result) == canonical(expected), "receipt equality")
        if args.cut_only:
            print("PASS_P104_MOVED_HELPER_SMALL_CUT target=40 source=1 missing_coefficients=44 no_new_kappa")
        else:
            print("PASS_P104_MOVED_HELPER_CUT flags=9765 helper=13 profiles="
                  f"{result['contact_profiles']} always_missing={len(result['always_missing_pairs'])} no_new_kappa")


if __name__ == "__main__":
    main()
