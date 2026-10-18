#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""PR1736 mixed-width pending projectors; see README for the precise boundary.

The predecessor generates candidate placements; this file checks their geometry.
Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""
import argparse
import ast
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRE = "research/bit589-width7-windows-seed72"
BIT = "research/e8-bit-p111-tuned"
GEOMETRY = "research/e8-bit-carrier-skeleton/code/nine/geometry.py"
LOCAL = 254  # chart axes 1,...,7; axis 0 is q/2
N, R, STAGES, REPLICAS = 222, 439, 9, 32


class Reject(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise Reject(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    result = {}
    for item in manifest["files"]:
        if item["usage"] == "input":
            raw = (ROOT / item["path"]).read_bytes()
            need(digest(raw) == item["sha256"], "source digest: " + item["path"])
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            need(blob == item["git_blob"], "source blob: " + item["path"])
            result[item["path"]] = digest(raw)
    selected = json.loads((ROOT / "research/community-frontier1094-audit/SELECTED-SOURCE.json").read_text())
    word_path = BIT + "/tune/bitE8mut-p111-tuned.json.gz"
    need(selected["files"][word_path] == result[word_path], "selected port source")
    assembly = json.loads((ROOT / "research/community-frontier1094-audit/ASSEMBLY.json").read_text())
    need(assembly["bit_supplier"]["commit"] == "a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46", "PR589 binding")
    return result


def predecessor():
    spec = importlib.util.spec_from_file_location("mixed_projectors_source1736", ROOT / PRE / "verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def literal_idle_table():
    """Read only the literal geometry table, without importing its dependencies."""
    tree = ast.parse((ROOT / GEOMETRY).read_text())
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    starts = [i for i, n in enumerate(main.body) if isinstance(n, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == "idle" for t in n.targets)]
    need(len(starts) == 1, "unique source idle table")
    body = main.body[starts[0]:starts[0] + 3]
    need(len(body) == 3 and all(isinstance(n, ast.For) for n in body[1:]), "source table syntax")
    namespace = {}
    exec(compile(ast.Module(body=body, type_ignores=[]), GEOMETRY, "exec"), namespace)
    return namespace["idle"]


def mask(axes):
    axes = tuple(axes)
    need(len(set(axes)) == len(axes) and all(type(x) is int and 0 <= x < 64 for x in axes), "axis domain")
    return sum(1 << x for x in axes)


def source_children(source):
    """Derive ambient axes from source levels, and windows by direct chronology."""
    events = source.wopt.windows.schedule()
    table = literal_idle_table()
    levels, children = [-1] * 4, []
    for pos, event in enumerate(events):
        kind = event["kind"]
        if kind == "local_cover_sweep":
            need(levels[event["pair"]] == event["stage"] - 1, "local source level")
            levels[event["pair"]] = event["stage"]
        elif kind == "bridge":
            need(levels[event["dst"]] == levels[event["src"]], "bridge source level")
        elif kind == "idle":
            i, pair = event["idx"], event["pair"]
            entry = table[i]
            a, b = entry["source_level"], entry["target_level"]
            need(i == len(children) and pair == entry["pair"] and a == levels[pair], "idle source binding")
            need(event["rank"] == entry["rank"] == 7 * (b - a), "idle source rank")
            axes = tuple(range(1 if a == -1 else 8 + 7 * a, 8 + 7 * b))
            need(len(axes) == event["rank"], "source axis dimension")
            window = []
            for before, candidate in enumerate(events[:pos]):
                if candidate["kind"] != "local_cover_sweep" or candidate["pair"] == pair:
                    continue
                untouched = all(not ((e["kind"] == "local_cover_sweep" and e["pair"] == pair)
                                    or (e["kind"] == "bridge" and pair in (e["src"], e["dst"])))
                                for e in events[before + 1:pos])
                if untouched:
                    window.append(candidate["stage"])
            children.append(dict(idx=i, pair=pair, source_level=a, target_level=b,
                                 axes=axes, window=tuple(window), rank=len(axes)))
            levels[pair] = b
        else:
            need(kind == "exchange" and levels == [8] * 4, "exchange source levels")
    need(len(children) == 10, "all source children including zero")
    need({c["idx"]: (c["rank"], c["window"]) for c in children if c["rank"]} == source.WIN,
         "independent chronology agrees with placement generator")
    by_pair = defaultdict(int)
    for child in children:
        whole = mask(child["axes"])
        need(not (whole & by_pair[child["pair"]]), "cross-child source orthogonality")
        by_pair[child["pair"]] |= whole
    return children


def partition(whole, factors, completion_free=True):
    used = 0
    for factor in factors:
        need(type(factor) is int and factor >= 0 and not factor & ~whole, "factor outside source child")
        need(not factor & used, "factor overlap")
        if completion_free:
            need((factor & 255) in (0, LOCAL), "split local q-perp")
        used |= factor
    need(used == whole, "missing source axes")


def audit(k, slots, children):
    """Independent validator: DP values and predecessor audit flags are not evidence here."""
    need(type(k) is int and 0 <= k <= 74, "k domain")
    groups, seen = defaultdict(list), set()
    for slot in slots:
        need(len(slot) == 6 and all(type(x) is int for x in slot), "typed slot")
        child, copy, offset, width, stage, helper = slot
        need(0 <= child < 10 and 0 <= copy < N and 0 <= stage < STAGES and 0 <= helper < R, "role indices")
        c = children[child]
        need(stage in c["window"], "slot window")
        need(width == (7 if helper < k else 8), "helper width")
        need(0 <= offset and offset + width <= c["rank"], "slot bounds")
        need((stage, helper) not in seen, "duplicate helper")
        seen.add((stage, helper))
        groups[child, copy].append((offset, width))
    need(seen == {(s, h) for s in range(STAGES) for h in range(R)}, "helper coverage")
    idle, first_widths = Counter(), Counter()
    support_counts = Counter(width7=0, width8=0, local_width7=0, local_width8=0)
    all_masks, family = set(), defaultdict(int)
    for c in children:
        whole = mask(c["axes"])
        for copy in range(N):
            factors, end = [], 0
            packed = sorted(groups[c["idx"], copy])
            for offset, width in packed:
                need(offset == end, "contiguous prefix")
                active = mask(c["axes"][offset:offset + width])
                need(active.bit_count() == width, "factor rank")
                factors.append(active)
                support_counts["width" + str(width)] += 1
                support_counts["local_width" + str(width)] += int(bool(active & LOCAL))
                key = c["pair"], copy
                need(not family[key] & active, "cross-child hosted overlap")
                family[key] |= active
                end += width
            if c["source_level"] == -1:
                first_widths[str(packed[0][1]) if packed else "empty"] += 1
            remainder = whole ^ mask(c["axes"][:end])
            need(remainder.bit_count() == c["rank"] - end, "remainder rank")
            partition(whole, factors + [remainder])
            idle[remainder.bit_count()] += 1
            all_masks.update(factors + [remainder])
    need(sum(idle.values()) == 2220 and sum(support_counts["width" + str(w)] for w in (7, 8)) == 3951,
         "complete factor census")
    need(support_counts["width7"] == 9 * k and support_counts["width8"] == 9 * (R - k), "width census")
    return dict(k=k, slots_sha256=digest(canonical(slots)), helper_slots=3951,
                factors=support_counts, entrance_first_widths=first_widths,
                idle_with_zero={str(r): n for r, n in sorted(idle.items())},
                distinct_masks=len(all_masks), split_factors=0,
                child_copy_partitions=2220, physical_helper_occurrences=3951 * REPLICAS)


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def add(a, b, sign=1):
    return [[x + sign * y for x, y in zip(u, v)] for u, v in zip(a, b)]


def projector(columns):
    return [[sum(v[i] * v[j] for v in columns) for j in range(8)] for i in range(8)]


def completion(q):
    """Rational Householder completion, used only for the ambiguity control."""
    unit = [Q(x, 2) for x in q]
    v = [Q(i == 0) - x for i, x in enumerate(unit)]
    norm = sum(x*x for x in v)
    h = identity(8) if not norm else [[Q(i == j) - 2*v[i]*v[j]/norm for j in range(8)] for i in range(8)]
    need(multiply(h, h) == identity(8) and [row[0] for row in h] == unit, "Householder control")
    return list(zip(*h))


def rational_checks():
    word = json.loads(gzip.decompress((ROOT / BIT / "tune/bitE8mut-p111-tuned.json.gz").read_bytes()))
    need((word["h"], word["v"], word["R"]) == (8, 111, 439), "selected word header")
    lines = word["lines"]
    need(len(lines) == 111 and len({tuple(q) for q in lines}) == 111, "all live ports")
    different, zero = 0, [[Q(0)] * 8 for _ in range(8)]
    for q in lines:
        need(len(q) == 8 and sum(x*x for x in q) == 4, "port norm")
        p = [[Q(x*y, 4) for y in q] for x in q]
        k = add(identity(8), p, -1)
        need(multiply(k, k) == k and sum(k[i][i] for i in range(8)) == 7, "rank-seven projector")
        need(multiply(p, k) == zero and add(p, k) == identity(8), "orthogonal local decomposition")
        columns = completion(q)
        need(projector(columns[1:]) == k, "completion gives same whole K")
        six = projector(columns[1:7])
        swapped = projector(columns[1:6] + [columns[7]])
        need(six != swapped, "proper local subset depends on completion")
        complement = add(k, six, -1)
        need(multiply(six, complement) == zero and add(six, complement) == k, "split control still partitions K")
        different += 1
    return dict(ports=111, rational_projectors=111, completion_ambiguity_witnesses=different)


def replica_lift(labels=tuple(range(REPLICAS))):
    ids = [replica * (4 * N) + pair * N + copy for replica in labels for pair in range(4) for copy in range(N)]
    need(len(labels) == 32 and set(ids) == set(range(28416)) and len(set(ids)) == len(ids), "injective replica lift")
    return dict(replicas=32, distinct_families=len(ids), per_replica_families=888)


def controls(slots, children):
    rejected = []

    def rejects(name, action, fragment):
        try:
            action()
        except Reject as error:
            need(fragment in str(error), "unexpected rejection for " + name + ": " + str(error))
            rejected.append(name)
        else:
            raise Reject("accepted negative control: " + name)

    rejects("omitted_helper", lambda: audit(1, slots[1:], children), "helper coverage")
    rejects("duplicate_helper", lambda: audit(1, slots + slots[:1], children), "duplicate helper")
    bad = [list(x) for x in slots]
    bad[0][3] = 8
    rejects("wrong_width", lambda: audit(1, bad, children), "helper width")
    bad = [list(x) for x in slots]
    bad[0][4] = 8
    rejects("out_of_window", lambda: audit(1, bad, children), "slot window")
    rejects("replica_alias", lambda: replica_lift(tuple([0] + list(range(31)))), "injective replica lift")
    # PR1736 k=1 has two width-seven slices in child0/copy0.
    need(slots[:2] == [(0, 0, 0, 7, 0, 0), (0, 0, 7, 7, 1, 0)], "source split-control anchor")
    whole = mask(range(1, 15))
    actual = [mask(range(1, 8)), mask(range(8, 15))]
    partition(whole, actual)
    split = [mask((*range(1, 7), 8)), mask((7, *range(9, 15)))]
    need([m.bit_count() for m in split] == [7, 7], "control keeps ranks")
    partition(whole, split, completion_free=False)
    rejects("equal_rank_local_split", lambda: partition(whole, split), "split local q-perp")
    shifted = [actual[0], (actual[1] ^ (1 << 8)) | (1 << 36)]
    need([m.bit_count() for m in shifted] == [7, 7], "wrong-axis control keeps ranks")
    rejects("equal_rank_wrong_exterior_axis", lambda: partition(whole, shifted), "outside source child")
    rejects("missing_factor", lambda: partition(whole, actual[:1]), "missing source axes")
    rejects("overlapping_factor", lambda: partition(whole, actual + actual[:1]), "factor overlap")
    partition(whole, list(reversed(actual)))
    need(audit(1, list(reversed(slots)), children)["idle_with_zero"] == audit(1, slots, children)["idle_with_zero"],
         "valid record-order control")
    return dict(rejected=rejected, accepted=["original_k1", "factor_order", "slot_record_order", "weak_split_partition"])


def run():
    hashes = pins()  # Check before any source module executes.
    source = predecessor()
    children = source_children(source)
    reference = json.loads((ROOT / PRE / "RESULT.json").read_text())
    rows, k1 = [], None
    for k in range(75):
        # Exactly PR1736 main()'s construction point; no moment recertification.
        _, _, plan, _ = source.wopt.solve(k, Q(1, 570), True)
        slots = []
        generated_idle = source.build(k, plan, slots)
        row = audit(k, slots, children)
        idle = {r: n for r, n in row["idle_with_zero"].items() if int(r)}
        need(idle == reference["rows"][str(k)]["idle"], "retained idle profile k=" + str(k))
        need(idle == {str(r): n for r, n in generated_idle.items()}, "generator/auditor remainder agreement")
        rows.append(row)
        if k == 1:
            k1 = slots
    result = dict(status="PASS_BIT_MIXED_WIDTH_PROJECTORS", source_hashes=hashes,
                  source_children=children, scope="geometric factorization; no physical width-seven provider or new kappa",
                  rows=rows, rational=rational_checks(), replica_lift=replica_lift(), controls=controls(k1, children),
                  totals=dict(placements=75, representative_helper_slots=75*3951,
                              lifted_helper_occurrences=75*3951*32, child_copy_partitions=75*2220,
                              split_factors=0))
    return json.loads(canonical(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="Write evidence to a new file, refusing overwrite")
    args = parser.parse_args()
    result = run()
    if args.write:
        with args.write.open("x") as out:
            out.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        need(canonical(result) == canonical(expected), "receipt equality")
    print("PASS_BIT_MIXED_WIDTH_PROJECTORS k=0..74 slots=296325 split=0 ports=111 controls=9 no_new_kappa")


if __name__ == "__main__":
    main()
