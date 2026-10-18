#!/usr/bin/env python3
"""Exact typed-host realization check for one selected PR589 physical family.

Standard library only. The selected PR589 construction and scope limits are
described in README.md. Prepared for @1337isnot1337 with substantial
OpenAI Codex assistance; Apache-2.0.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import json
from itertools import permutations
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
V = 111
R = 439
REPLICAS = 32
WIDTH = 8
DIM = 64
V2 = 2 * V
GEOMETRY = "research/e8-bit-carrier-skeleton/code/nine/geometry.py"
CONTROLLER = ("research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/"
              "vendor/e8-r715-eleven-stage-whole/code/global_k.py")
SELECTION = "research/e8-bit-p111-tuned/data/selection9-p111.json"
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
TASK_CATALOG = "docs/research/agent-task-catalog.json"


class Reject(ValueError):
    """A source, scope, or exact-operator mismatch."""


def need(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def read_json(relative: str):
    return json.loads((ROOT / relative).read_text())


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def source_hashes() -> dict[str, str]:
    manifest = read_json("research/seed03-bit-physical-family/SOURCES.json")
    need(manifest["base_commit"] == BASE, "base commit pin")
    hashes = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        raw = (ROOT / row["path"]).read_bytes()
        need(digest(raw) == row["sha256"], "source SHA-256: " + row["path"])
        hashes[row["path"]] = digest(raw)
    cert = read_json("certificates/selected-result.json")
    need(cert["kappa"] == "836330098538459/500000000000000000", "selected kappa")
    need(589 in cert["source_prs"], "selected source includes PR589")
    assembly = read_json("research/community-frontier1094-audit/ASSEMBLY.json")
    bit = assembly["bit_supplier"]
    need(bit["commit"] == "a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46", "selected PR589 commit")
    selected = read_json("research/community-frontier1094-audit/SELECTED-SOURCE.json")["files"]
    for path in ("research/e8-bit-p111-tuned/tune/EXPECTED.json", WORD, SELECTION):
        need(selected[path] == hashes[path], "selected-source binding: " + path)
    need(bit["git_blob_sha1"] == blob_id("research/e8-bit-p111-tuned/tune/EXPECTED.json"),
         "assembly PR589 receipt blob")
    return hashes


def blob_id(relative: str) -> str:
    """Recompute the Git blob id from bytes without relying on the index."""
    raw = (ROOT / relative).read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def source_function(path: str, name: str):
    tree = ast.parse((ROOT / path).read_text())
    nodes = [node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name == name]
    need(len(nodes) == 1, "unique source function " + name)
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), path, "exec"), namespace)
    return namespace[name]


def source_idle_table():
    """Extract the literal idle table from the pinned geometry main body."""
    tree = ast.parse((ROOT / GEOMETRY).read_text())
    main = next(node for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name == "main")
    start = next(i for i, node in enumerate(main.body)
                 if isinstance(node, ast.Assign)
                 and any(isinstance(target, ast.Name) and target.id == "idle"
                         for target in node.targets))
    nodes = main.body[start:start + 3]
    need(isinstance(nodes[0], ast.Assign)
         and all(isinstance(node, ast.For) for node in nodes[1:]),
         "source idle table shape")
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), GEOMETRY, "exec"), namespace)
    return namespace["idle"]


def source_schedule():
    """Replay the pinned nine-stage recipe and its idle child boundaries."""
    recipe = source_function(CONTROLLER, "recipe")(4)
    levels = [-1] * 4
    events: list[dict] = []
    children: list[dict] = []

    def advance(pair: int, target: int) -> None:
        old = levels[pair]
        need(-1 <= old <= target <= 8, "monotone idle levels")
        child = dict(kind="idle", idx=len(children), pair=pair,
                     source_level=old, target_level=target,
                     rank=7 * (target - old))
        children.append(child)
        events.append(child)
        levels[pair] = target

    for event in recipe:
        kind = event["kind"]
        if kind == "local":
            stage, pair = event["stage"], event["pair"]
            need(levels[pair] == stage - 1, "local entry level")
            levels[pair] = stage
            events.append(event)
            if 1 <= stage <= 6:
                advance((stage + 1) // 2, stage)
            if stage == 8:
                for other in range(4):
                    advance(other, 8)
        elif kind == "bridge":
            need(levels[event["dst"]] == levels[event["src"]], "bridge level match")
            events.append(event)
        else:
            need(kind == "exchange" and levels == [8] * 4, "terminal exchange")
            events.append(event)

    fields = ("pair", "source_level", "target_level", "rank")
    found = [[child[field] for field in fields] for child in children]
    expected = [[child[field] for field in fields] for child in source_idle_table()]
    need(found == expected, "recipe idle levels equal geometry source")
    need(len(children) == 10 and sum(c["rank"] for c in children) == 189,
         "ten idle children and total rank")
    return events, children


def child_axes(child: dict) -> tuple[int, ...]:
    a, b = child["source_level"], child["target_level"]
    need(-1 <= a <= b <= 8, "child level range")
    lo = 1 if a == -1 else 8 + 7 * a
    hi = 8 + 7 * b
    axes = tuple(range(lo, hi))
    need(len(axes) == child["rank"], "child axis rank")
    return axes


def windows(events: list[dict], children: list[dict]):
    answer = {}
    for child in children:
        idx, pair = child["idx"], child["pair"]
        pos = events.index(child)
        allowed = set()
        for event in reversed(events[:pos]):
            if event["kind"] == "local" and event["pair"] == pair:
                break
            if event["kind"] == "bridge" and pair in (event["src"], event["dst"]):
                break
            if event["kind"] == "local":
                allowed.add(event["stage"])
        answer[idx] = allowed
    return answer


def allocate_slots(children: list[dict], allowed: dict[int, set[int]]):
    """Expand the frozen selection independently into one replica's slots."""
    selection = read_json(SELECTION)["bit"]
    patterns: dict[int, list[tuple[tuple[int, ...], int]]] = defaultdict(list)
    for child, widths, count in selection["patterns"]:
        patterns[child].append((tuple(widths), count))
    need_stage: dict[tuple[int, int], list[int]] = defaultdict(list)
    for child, width, stage, count in sorted(selection["stages"]):
        need(stage in allowed[child], "selected stage outside child window")
        need_stage[child, width].extend([stage] * count)
    ptr = Counter()
    pools = {stage: list(range(R)) for stage in range(9)}
    slots = []
    for child in children:
        idx = child["idx"]
        pats = sorted(patterns[idx], key=lambda row: (-sum(row[0]), row[0]))
        copy = 0
        for pat, count in pats:
            for _ in range(count):
                offset = 0
                for width in sorted(pat, reverse=True):
                    stages = need_stage[idx, width]
                    stage_pos = ptr[idx, width]
                    need(stage_pos < len(stages), "selection stage demand underflow")
                    stage = stages[stage_pos]
                    ptr[idx, width] += 1
                    need(pools[stage], "helper supply exhausted")
                    helper = pools[stage].pop(0)
                    slots.append((idx, copy, offset, width, stage, helper))
                    offset += width
                need(offset <= child["rank"], "pattern exceeds child rank")
                copy += 1
        need(copy <= V2, "too many selected copies")
        while copy < V2:
            copy += 1
    need(len(slots) == 3951, "selected one-replica slot count")
    need(all(not pool for pool in pools.values()), "all 439 helpers used at every stage")
    need(sum(1 for c, _, _, _, _, _ in slots) == len(slots), "slot row structure")
    return slots


def family_key(child: dict, copy: int) -> tuple[int, int]:
    return child["pair"], copy


def select_family(children: list[dict], slots: list[tuple]):
    groups: dict[tuple[int, int], list[tuple]] = defaultdict(list)
    child_by_id = {child["idx"]: child for child in children}
    for slot in slots:
        child, copy = slot[0], slot[1]
        groups[family_key(child_by_id[child], copy)].append(slot)
    candidates = []
    for key, rows in groups.items():
        child_ids = {row[0] for row in rows}
        if len(child_ids) > 1:
            candidates.append((key, rows, child_ids))
    need(len(candidates) == 444, "mixed-child physical family census per replica")
    need(max(len(ids) for _, _, ids in candidates) == 2, "maximum mixed-child count")
    # Maximize helper multiplicity, then use source pair/copy as a stable tie-break.
    key, rows, child_ids = min(candidates,
                               key=lambda item: (-len(item[1]), item[0][0], item[0][1]))
    need(key == (1, 0), "deterministic maximum-multiplicity family key")
    need(sorted(child_ids) == [0, 7] and len(rows) == 4,
         "selected family children and helper multiplicity")
    return key, sorted(rows, key=lambda row: (row[4], row[5]))


def q_perp(q: tuple[int, ...]):
    need(len(q) == 8 and sum(x * x for x in q) == 4, "selected port norm")
    return tuple(tuple(Q(int(i == j)) - Q(q[i] * q[j], 4)
                       for j in range(8)) for i in range(8))


def make_projector(axes, q: tuple[int, ...], label: str):
    axes = tuple(axes)
    need(len(set(axes)) == len(axes), "duplicate physical axis")
    need(all(0 <= axis < DIM for axis in axes), "physical axis range")
    local = {axis for axis in axes if axis < 8}
    q_axes = set(range(1, 8))
    need(local in (set(), q_axes), "split q-perp block or q direction used")
    ext = tuple(sorted(axis for axis in axes if axis >= 8))
    return {"label": label, "q": q if local else None, "external": ext,
            "rank": (7 if local else 0) + len(ext), "axes": axes}


def project(p: dict, vector: tuple[Q, ...]) -> tuple[Q, ...]:
    need(len(vector) == DIM, "projector vector dimension")
    result = [Q(0)] * DIM
    if p["q"] is not None:
        K = q_perp(p["q"])
        for i in range(8):
            result[i] = sum(K[i][j] * vector[j] for j in range(8))
    for axis in p["external"]:
        result[axis] = vector[axis]
    return tuple(result)


def apply_D(p: dict, state: tuple[Q, ...]) -> tuple[Q, ...]:
    """Apply D(P)=[I-P P; P I-P] to an exact 128-coordinate state."""
    need(len(state) == 2 * DIM, "address state dimension")
    x, y = state[:DIM], state[DIM:]
    px, py = project(p, x), project(p, y)
    return tuple(x[i] - px[i] + py[i] for i in range(DIM)) + tuple(
        px[i] + y[i] - py[i] for i in range(DIM))


def basis_columns(factors: list[dict]) -> tuple[tuple[Q, ...], ...]:
    columns = []
    for basis_index in range(2 * DIM):
        state = [Q(0)] * (2 * DIM)
        state[basis_index] = Q(1)
        current = tuple(state)
        for p in factors:
            current = apply_D(p, current)
        columns.append(current)
    return tuple(columns)


def factor_intervals(events, children, slots, word, family):
    pair, copy = family
    side, port = divmod(copy, V)
    need(side == 0 and port == 0, "selected physical family address")
    q = tuple(word["lines"][port])
    child_by_id = {child["idx"]: child for child in children}
    child_event_pos = {child["idx"]: events.index(child) for child in children}
    local_pos = {event["stage"]: i for i, event in enumerate(events)
                 if event["kind"] == "local"}
    rows_by_child: dict[int, list[tuple]] = defaultdict(list)
    for row in slots:
        child, slot_copy, offset, width, stage, helper = row
        if slot_copy == copy and child_by_id[child]["pair"] == pair:
            axes = child_axes(child_by_id[child])[offset:offset + width]
            need(len(axes) == width, "slot axis slice")
            rows_by_child[child].append((stage, helper, axes, row))

    interval_data = {}
    for child_id in sorted(rows_by_child):
        child = child_by_id[child_id]
        deadline = child_event_pos[child_id]
        host_rows = sorted(rows_by_child[child_id], key=lambda x: (local_pos[x[0]], x[1]))
        used = set()
        host_factors = []
        for stage, helper, axes, row in host_rows:
            call_pos = local_pos[stage]
            need(stage < 9 and call_pos < deadline, "host call precedes child deadline")
            need(stage in windows(events, children)[child_id], "source window membership")
            for event in events[call_pos + 1:deadline]:
                if event["kind"] == "local":
                    need(event["pair"] != pair, "pair touched before idle deadline")
                elif event["kind"] == "bridge":
                    need(pair not in (event["src"], event["dst"]), "bridge touches pair before deadline")
            need(not (used & set(axes)), "hosted axes overlap")
            used.update(axes)
            host_factors.append(make_projector(axes, q, f"child{child_id}:stage{stage}:helper{helper}"))
        full_axes = child_axes(child)
        need(used <= set(full_axes), "hosted axes leave source pending block")
        rest_axes = tuple(axis for axis in full_axes if axis not in used)
        rest = make_projector(rest_axes, q, f"child{child_id}:idle-remainder")
        full = make_projector(full_axes, q, f"child{child_id}:source-pending")
        need(sum(p["rank"] for p in host_factors) + rest["rank"] == full["rank"],
             "paid hosts plus idle remainder preserve rank")
        interval_data[child_id] = dict(child=child, host_rows=host_rows,
                                       host_factors=host_factors, remainder=rest,
                                       source=full, rest_axes=list(rest_axes),
                                       host_event_positions=[local_pos[row[0]] for row in host_rows],
                                       deadline_event_position=deadline)
    need(sorted(interval_data) == [0, 7], "selected family interval set")
    return q, interval_data


def compose_intervals(interval_data):
    outcomes = {}
    for child_id, data in interval_data.items():
        actual = data["host_factors"] + [data["remainder"]]
        expected = [data["source"]]
        actual_columns = basis_columns(actual)
        expected_columns = basis_columns(expected)
        outcomes[child_id] = dict(equal=actual_columns == expected_columns,
                                  columns_checked=len(actual_columns),
                                  host_ranks=[p["rank"] for p in data["host_factors"]],
                                  remainder_rank=data["remainder"]["rank"],
                                  source_rank=data["source"]["rank"],
                                  host_labels=[p["label"] for p in data["host_factors"]],
                                  host_axes=[list(p["axes"]) for p in data["host_factors"]],
                                  host_event_positions=data["host_event_positions"],
                                  deadline_event_position=data["deadline_event_position"],
                                  chronological_order=(
                                      ["host:" + p["label"] for p in data["host_factors"]]
                                      + ["idle-remainder:child" + str(child_id)]),
                                  remainder_axes=data["rest_axes"],
                                  source_axes=list(data["source"]["axes"]))
    need(all(value["equal"] for value in outcomes.values()), "exact typed host composition")
    return outcomes


def negative_controls(interval_data, q, word):
    rejected = []

    def differs(child_id, factors):
        data = interval_data[child_id]
        return basis_columns(factors) != basis_columns([data["source"]])

    # Drop one actual helper from the three-helper terminal child.
    terminal = interval_data[7]
    need(differs(7, terminal["host_factors"][:-1] + [terminal["remainder"]]),
         "omitted helper changes map")
    rejected.append("omitted_helper")

    # Keep rank eight but move child 0's one exterior axis outside its source block.
    first = interval_data[0]
    changed_axes = list(first["host_factors"][0]["axes"])
    ext_index = next(i for i, axis in enumerate(changed_axes) if axis >= 8)
    changed_axes[ext_index] = 22
    wrong = make_projector(changed_axes, q, "wrong-equal-rank-axis")
    need(wrong["rank"] == first["host_factors"][0]["rank"], "wrong-axis rank retained")
    need(differs(0, [wrong, first["remainder"]]), "wrong physical axis changes map")
    rejected.append("equal_rank_wrong_axis")

    # A duplicate D(P) cancels that involutive factor instead of implementing it once.
    p = terminal["host_factors"][1]
    need(differs(7, terminal["host_factors"] + [p, terminal["remainder"]]),
         "duplicate helper changes map")
    rejected.append("duplicate_helper")

    # Substitute the first distinct source line so the local q-perp projector changes.
    K0 = q_perp(q)
    replacement = None
    for index, line in enumerate(word["lines"]):
        candidate = tuple(line)
        if candidate != q and q_perp(candidate) != K0:
            replacement = candidate
            break
    need(replacement is not None, "distinct source line for wrong-q control")
    host = first["host_factors"][0]
    wrong_q = dict(host, q=replacement, label="wrong-source-port")
    need(differs(0, [wrong_q, first["remainder"]]), "wrong source port changes map")
    rejected.append("wrong_source_port")
    return rejected


def positive_permutation_controls(interval_data):
    terminal = interval_data[7]
    host = terminal["host_factors"]
    results = 0
    target = basis_columns([terminal["source"]])
    for order in permutations(host):
        need(basis_columns(list(order) + [terminal["remainder"]]) == target,
             "orthogonal helper order invariance")
        results += 1
    need(results == 6, "all helper permutations checked")
    return results


def verify():
    hashes = source_hashes()
    events, children = source_schedule()
    legal = windows(events, children)
    slots = allocate_slots(children, legal)
    family, family_rows = select_family(children, slots)
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    need((word["h"], word["v"], word["R"]) == (8, V, R), "selected word header")
    q, intervals = factor_intervals(events, children, slots, word, family)
    outcomes = compose_intervals(intervals)
    controls = negative_controls(intervals, q, word)
    permutations_checked = positive_permutation_controls(intervals)
    need(len(family_rows) == 4, "selected family role count")
    return dict(
        status="PASS_PR589_PHYSICAL_FAMILY",
        base_commit=BASE,
        family=dict(pair=family[0], copy=family[1], side=0, port=0,
                    child_ids=[0, 7], roles=[list(row) for row in family_rows]),
        interval_results={str(k): v for k, v in sorted(outcomes.items())},
        summary=dict(children=2, helper_occurrences=4,
                     child0_source_rank=14, child0_hosted_rank=8,
                     child0_remainder_rank=6, child7_source_rank=28,
                     child7_hosted_rank=24, child7_remainder_rank=4,
                     exact_basis_columns_per_interval=2 * DIM,
                     helper_order_permutations_checked=permutations_checked,
                     rejected_controls=controls,
                     source_schedule_events=len(events),
                     source_idle_children=len(children),
                     one_replica_slots=len(slots)),
        source_hashes=hashes,
        scope="One selected PR589 physical family only; finite exact address operators, no full supplier admission or new kappa.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="create a new RESULT.json exclusively")
    args = parser.parse_args()
    result = verify()
    if args.write:
        with args.write.open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        expected = read_json("research/seed03-bit-physical-family/RESULT.json")
        need(result == expected, "committed result mismatch")
    print("PASS_PR589_PHYSICAL_FAMILY pair=1 copy=0 children=0,7 helpers=4 "
          "columns=128 controls=4 orderings=6 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (Reject, OSError, KeyError, TypeError, ValueError, IndexError) as error:
        raise SystemExit("REJECT_PR589_PHYSICAL_FAMILY: " + str(error)) from error
