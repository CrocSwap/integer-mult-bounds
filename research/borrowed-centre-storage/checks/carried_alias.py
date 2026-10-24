"""Check the carried alias without importing a producer or native compiler."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse
import gzip
import json


HERE = Path(__file__).resolve().parents[1] / "sources" / "work/centre-encoding-campaign-20261014" / "lanes/residual-syndrome/physical-algebra/review-gauss/graph-cache/carried-alias"
PHYSICAL = HERE.parents[2]
LANES = PHYSICAL.parents[1]
ROOT = LANES.parents[2]
MODULE = LANES / "circuit-interface/borrowed-centres"
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
PHASES = "t16/global/base/work/complex-nine-native/DATA-PHASES.json"
TEMPLATE = "t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz"
PLAN = "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
PINS = {
    "payload": "677199e44967cb598bdd6b92f23400cf88ac40020e195f07a0c6e5244a3ace0d",
    "word": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "R": "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3",
    "logger": "ac824c98819dc1defef14788bf5215f72323f49a49f1f8bec4ee373558eba82e",
    "borrowed": "6b88cf885e22ef745eee74db04adc7feadfcc63a8248e8873b1a4caf76b21096",
    "native_review": "ebf14b2eccffc0b3a2f03858a84c72792d27d7dd4a177f0b02609921f6258144",
    "note": "0a1c3319c2d0ffba4cb70f1a5aca35c2d62072a2380afeaad0c301e29b10e12f",
    "producer": "eec25fa79fca117181b619fba9448bbfe0d358373ba00c1ccdc3daceebfa1623",
    "producer_receipt": "42fb664f2273bacdc04603c548961de4a75ec04d752974794f0f0b311ca18bd2",
    ARCHIVE: "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754",
    PHASES: "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    TEMPLATE: "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518",
    PLAN: "7bd786ba8e66408f02aa9ef446eaf20c1bfe981ea2e4dd1e5a929f0aa7767bc0",
}
T = [21, 37, 47, 76, 81, 87, 92, 110]
A = [0, 7, 20, 27, 36, 46, 57, 111]


def pinned(raw, key):
    assert sha256(raw).hexdigest() == PINS[key], key
    return raw


def read(path, key, compressed=False, file_pin=False):
    raw = path.read_bytes()
    if file_pin:
        pinned(raw, key)
    if compressed:
        raw = gzip.decompress(raw)
    if not file_pin:
        pinned(raw, key)
    return json.loads(raw)




def rational(rows):
    return [{int(j): Q(v) for j, v in row.items()} for row in rows]


def add(a, b, coefficient):
    result = a.copy()
    for j, value in b.items():
        result[j] = result.get(j, 0) + coefficient * value
        if not result[j]:
            del result[j]
    return result


def multiply(a, b):
    out = []
    for row in a:
        value = {}
        for j, coefficient in row.items():
            value = add(value, b[j], coefficient)
        out.append(value)
    return out


def place(location):
    bank, j = location
    assert bank in ("L", "C")
    assert 0 <= j < (704 if bank == "L" else 8)
    return j if bank == "L" else 704 + j


def scalar_cost(gate):
    assert gate[0] in ("add", "scale")
    value = Q(*gate[2:]) if gate[0] == "scale" else Q(*gate[3:])
    a, b = abs(value.numerator), value.denominator
    assert a and b & (b - 1) == 0
    if gate[0] == "scale":
        assert a & (a - 1) == 0
        return 2 * (abs(a.bit_length() - b.bit_length()) + (value < 0))
    return 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)


def replay(events, initial, word):
    rows = [row.copy() for row in initial]
    frames = word["start"][:] + [0] * 8
    profile, operations = Counter(), Counter()
    cost = 0
    for event in events:
        kind = event[0]
        if kind == "climb":
            _, _, p, before, after, rank = event
            assert frames[p] == before
            frames[p] = after
            profile[rank] += 1
        elif kind == "input_target_line":
            _, p, label, sign, before, after, rank = event
            assert p in A and label == word["ports"][p] and rank == 1
            assert frames[p] == before
            assert (sign, before, after) in ((-1, word["start"][p], 0), (1, 0, word["start"][p]))
            frames[p] = after
            profile[1] += 1
        elif kind == "scalar":
            gate, frame = event[1:]
            target = place(gate[1])
            assert frames[target] == frame
            assert gate[0] in ("add", "scale")
            if gate[0] == "add":
                source = place(gate[2])
                assert source != target and frames[source] == frame
                rows[target] = add(rows[target], rows[source], Q(*gate[3:]))
            else:
                rows[target] = {j: Q(*gate[2:]) * q for j, q in rows[target].items()}
            operations[gate[0]] += 1
            cost += scalar_cost(gate)
        else:
            assert kind in ("phase", "adapter", "residual_adapter")
    assert frames == word["final"] + [0] * 8
    return rows, {"native_profile": dict(sorted(profile.items())),
                  "native_mass": sum(k * v for k, v in profile.items()),
                  "real_primitives": cost, "scalar_operations": dict(operations)}


def dot(a, b):
    return (a & b).bit_count() % 2


def route(z, stage, complement):
    # Each even transvection swaps one pair of orthonormal axes.
    if stage:
        for k, b in enumerate(complement):
            difference = b ^ (1 << (9 + 8 * (stage - 1) + k))
            if dot(z, difference):
                z ^= difference
    return z


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    payload = read(PHYSICAL / "CARRIED-QUERY-ALIAS-PROGRAMS.json.gz", "payload", True)
    pinned((PHYSICAL / "CARRIED-QUERY-ALIAS.md").read_bytes(), "note")
    pinned((PHYSICAL / "verify_carried_query_alias.py").read_bytes(), "producer")
    producer = read(PHYSICAL / "CARRIED-QUERY-ALIAS.json", "producer_receipt")
    assert producer["payload_sha256"] == PINS["payload"]
    word = read(ROOT / "work/five-pr-sprint-20261013/lanes/centre-sharing/CANONICAL-WORD.json.gz", "word", True, True)
    r = rational(read(LANES / "circuit-interface/INTERFACE.json", "R")["R"])
    logger = read(MODULE / "INPUT-SOURCE-FAMILY-PROGRAMS.json.gz", "logger", True)
    borrowed = read(MODULE / "BORROWED-CENTRES-PROGRAMS.json.gz", "borrowed", True)["programs"]
    native = read(LANES / "interface-proof/INPUT-COMPENSATION-NATIVE-REVIEW.json", "native_review")
    assert native["status"] == "PASS_ACTUAL_INPUT_COMPENSATION_NATIVE_PREMISE"
    assert payload["T_ports"] == logger["T_ports"] == T
    assert logger["A_ports"] == A
    def address(matrix, x):
        return sum(dot(row, x) << i for i, row in enumerate(matrix))
    line_recipes = logger["input_line_recipes"]
    assert {(r["port"], r["sign"]) for r in line_recipes} == {(p, sign) for p in A for sign in (-1, 1)}
    assert len(line_recipes) == 16
    for item in line_recipes:
        recipe, label, sign = item["recipe"], item["label"], item["sign"]
        assert label == word["ports"][item["port"]] and recipe["rank"] == 1
        left, right = recipe["left"], recipe["right"]
        assert left["offset"] == (label if sign == -1 else 0) and right["offset"] == 0
        for side in (left, right):
            assert side["phase"] == 0 and side["linear_Z4"] == side["quadratic_rows"] == [0] * 9
        assert address(left["matrix_rows"], 1) == label
        for i in range(9):
            assert address(left["matrix_rows"], address(right["matrix_rows"], 1 << i)) == 1 << i
            assert address(right["matrix_rows"], address(left["matrix_rows"], 1 << i)) == 1 << i
    identity = [{i: Q(1)} for i in range(712)]
    k_matrix = [{k: row[p] / 4 for k, row in enumerate(r) if p in row} for p in range(112)]
    rt = [{k: row[p] for k, p in enumerate(T) if p in row} for row in r]
    rt_inverse = [k_matrix[p] for p in T]
    assert multiply(rt_inverse, rt) == [{k: 1} for k in range(8)]
    assert multiply(rt, rt_inverse) == [{k: 1} for k in range(8)]
    query = multiply(rt_inverse, r)
    assert query == rational(payload["query_rows"])
    assert Counter(abs(q) for row in query for q in row.values()) == {Q(1): 8, Q(1, 2): 416}
    b0 = [add(row, {p: rt[k][j] for j, p in enumerate(T) if j in rt[k]}, -1) for k, row in enumerate(r)]
    z = [{k: (-12 if p in A else 1) * q for k, q in row.items()} for p, row in enumerate(k_matrix)]
    g = [add({p: Q(1)}, row, 1) for p, row in enumerate(multiply(z, b0))]
    j_matrix = [add({p: Q(1)}, row, -1) for p, row in enumerate(multiply(k_matrix, r))]
    assert [g[p] for p in T] == query

    capture = [["scalar", ["add", ["C", k], ["L", 112 + p], q.numerator, q.denominator], 0]
               for k, row in enumerate(query) for p, q in sorted(row.items())]
    unload = [["scalar", ["add", ["C", k], ["L", 112 + p], -1, 1], 0] for k, p in enumerate(T)]
    assert payload["capture"] == capture and payload["unload"] == unload
    assert payload["captured_backward_word"] == capture + logger["programs"]["logger"]
    assert payload["following_forward_word"] == unload + borrowed["forward"]
    after, backward_bill = replay(payload["captured_backward_word"], identity, word)
    expected = [row.copy() for row in identity]
    for p in range(112):
        expected[p] = add(expected[p], {112 + j: value for j, value in j_matrix[p].items()}, -1)
        expected[112 + p] = {112 + j: value for j, value in g[p].items()}
    for k in range(8):
        expected[704 + k] = add(expected[704 + k], {112 + p: value for p, value in query[k].items()}, 1)
    assert after == expected
    alias_input = [row.copy() for row in identity]
    for k, p in enumerate(T):
        alias_input[704 + k][112 + p] = 1
    after, forward_bill = replay(payload["following_forward_word"], alias_input, word)
    expected = [row.copy() for row in identity]
    for p in range(112):
        expected[112 + p] = add(expected[112 + p], j_matrix[p], 1)
    assert after == expected
    assert backward_bill["native_profile"] == {1: 2428, 2: 418, 3: 432, 4: 142, 5: 82}
    assert backward_bill["native_mass"] == 5538 and backward_bill["real_primitives"] == 232390
    assert sum(scalar_cost(e[1]) for e in capture) == 4224
    assert sum(scalar_cost(e[1]) for e in unload) == 64
    baseline = [add({p: Q(1)}, row, -1) for p, row in zip(T, query)]
    assert baseline[0][2] == Q(-1, 2)

    selected = Path(__file__).resolve().parents[1] / "sources/alias-upstream"
    phase = json.loads(pinned((selected / "DATA-PHASES.json").read_bytes(), PHASES))
    template = json.loads(gzip.decompress(pinned((selected / "GLOBAL-TEMPLATE.json.gz").read_bytes(), TEMPLATE)))
    plan = json.loads(pinned((selected / "PLAN.json").read_bytes(), PLAN))
    assert (plan["K"], plan["T"], plan["M"], plan["L"], plan["live"]) == (4, 16, 73, 9, 14336)
    assert {(c["stage"], c["replica"]) for c in plan["provider_calls"]} == {(s, t) for s in range(9) for t in range(16)}
    for c in plan["provider_calls"]:
        assert c["orientation"] == ("backward" if c["stage"] % 2 else "forward")
    calls = {(c["stage"], c["replica"]): c for c in template["calls"]}
    assert len(calls) == 144
    for (stage, replica), c in calls.items():
        pair = max(0, (stage - 1) // 2)
        assert c["pair"] == pair
        assert c["orientation"] == ("backward" if stage % 2 else "forward")
        assert c["window"] == {"local_axes": list(range(9)), "prefix_axes": list(range(9, 9 + 8 * stage))}
        for p in T:
            assert c["owners"][112 + p] == [replica * 896 + (2 * pair + 1) * 112 + p, [1, stage, p]]
    schedule = template["execution_schedule"]
    for window in payload["windows"]:
        stage, pair = window["backward_stage"], window["pair"]
        assert (stage, window["forward_stage"]) == (2 * pair + 1, 2 * pair + 2)
        start = next(i for i, e in enumerate(schedule) if e.get("kind") == "local_cover_sweep" and e.get("stage") == stage)
        end = next(i for i, e in enumerate(schedule) if e.get("kind") == "local_cover_sweep" and e.get("stage") == stage + 1)
        between = schedule[start + 1:end]
        assert between == window["intervening_events"]
        if pair == 3:
            assert between == []
        else:
            idle, bridge = between
            assert idle["kind"] == "idle_cover_sweep" and idle["pair"] == pair + 1
            assert bridge == {"kind": "bridge", "coefficient": 1, "dst": pair, "src": pair + 1}
    assert payload["global_cover_correction"] == template["cover_final_correction"]["formula"]

    points = [0] + [1 << i for i in range(73)] + [(1 << i) | (1 << j) for i, j in combinations(range(73), 2)]
    phase_checks, hole_checks, omitted_signs_rejected = 0, 0, 0
    for record, p in zip(payload["histories"], T):
        label = word["ports"][p]
        source = phase["recipes"][p]
        assert source["port"] == p and source["q"] == label
        # Read the chart from the pinned idle child, not the producer's chart function.
        complement = source["idle_children"][0]["orthogonal_axes"][:8]
        basis = [label] + complement
        assert all(dot(a, b) == (i == j) for i, a in enumerate(basis) for j, b in enumerate(basis))
        assert record["hole_child_chart_columns"] == complement + [label]
        eta = 0
        for b in basis:
            if ((b.bit_count() - 1) // 2) % 2:
                eta ^= b
        assert eta == record["local_hole_translation"]
        for z0 in range(512):
            left = (z0.bit_count() - dot(z0, label)) % 4
            right = (sum(dot(z0, b) for b in complement) + 2 * dot(z0, eta)) % 4
            assert left == right
            hole_checks += 1
            omitted_signs_rejected += left != sum(dot(z0, b) for b in complement) % 4
        assert len(record["history"]) == 9
        for stage, h in enumerate(record["history"]):
            alignment = source["stage_alignment"][stage]
            assert h["stage"] == stage and h["data_port"] == p and h["label"] == label
            assert h["entry_translation_owner_coordinates"] == alignment["entry_Y"]
            assert h["exit_translation_owner_coordinates"] == alignment["exit_Y"]
            child_axes = [1 << i for i in range(9)] if stage == 8 else complement
            child_sign = 0 if stage == 8 else eta
            assert h["local_child_axes"] == child_axes and h["child_rank"] == len(child_axes)
            assert h["local_translation_after_child"] == child_sign
            assert h["owner_child_axes"] == [route(a, stage, complement) for a in child_axes]
            exterior = ((1 << (9 + 8 * stage)) - 1) ^ 511
            current = (1 << (9 + 8 * stage)) - 1
            previous = (1 << (9 + 8 * (stage - 1))) - 1 if stage else 0
            for point in points:
                local = route(point, stage, complement)
                old = ((local & previous).bit_count() - dot(local, label)) if stage else 0
                entry = old + 2 * dot(local, alignment["entry_Y"])
                assert entry % 4 == (point & exterior).bit_count() % 4
                exit_phase = ((local & exterior).bit_count() + sum(dot(local, a) for a in child_axes)
                              + 2 * dot(local, child_sign) + 2 * dot(point, alignment["exit_Y"]))
                target = (point & current).bit_count() - (dot(point, label) if stage < 8 else 0)
                assert exit_phase % 4 == target % 4
                phase_checks += 2
            for i in range(73):
                point = 1 << i
                assert route(route(point, stage, complement), stage, complement) == point
        assert Counter(h["child_rank"] for h in record["history"]) == {8: 8, 9: 1}
        # The cover identity holds as a matrix identity on every address bit.
        for stage in (1, 3, 5, 7):
            for i in range(73):
                point = 1 << i
                assert route(route(route(point, stage, complement), stage, complement), stage + 1, complement) == route(point, stage + 1, complement)
    assert hole_checks == 4096 and phase_checks == 144 * 2702
    assert omitted_signs_rejected > 0
    report = {
        "status": "PASS_INDEPENDENT_CARRIED_QUERY_ALIAS",
        "source_base": BASE, "pins": PINS, "archive_replayed": False, "packaged_members_verified": True,
        "complete_712_column_replays": ["captured_backward_word", "following_forward_word"],
        "captured_backward": backward_bill, "following_forward": forward_bill,
        "arbitrary_helper_outputs": 480, "arbitrary_cache_inputs": 8,
        "capture_ADDs": 424, "capture_real_primitives": 4224,
        "unload_ADDs": 8, "unload_real_primitives": 64,
        "four_window_real_primitives_per_replica": 17152,
        "global_calls_checked": 144, "windows_checked": 4,
        "signed_input_line_recipes_checked_by_address_algebra": 16,
        "hole_eigenvalues_checked": hole_checks,
        "global_phase_identities": 144, "points_per_identity": 2702,
        "global_phase_value_comparisons": phase_checks,
        "omitted_local_translation_counterexamples": omitted_signs_rejected,
        "profile_per_independent_owner": {8: 8, 9: 1},
        "paid_rank_per_owner": 73,
        "baseline_capture_counterexample": {"cache": 0, "input_Y_port": 2, "residual": "-1/2"},
        "native_scope": "Exact new hole and owner phase identities. Retained local child kernels, local endpoint adapters, and native input-line premises are inherited; no broad kernel replay.",
        "all_tensor_sizes": "Exact base identities have scalar phase one. Tensor them with the same translations and address gathers; use each scalar coefficient once.",
        "credit_scope": "Rank 584 per replica is paid. Productive rank 584 requires eight admitted independent owners and their full F73 outputs; this review does not admit their allocation.",
        "excluded": ["Clean query access", "Restoration of source G", "A complete global data controller", "Final owner allocation", "Address and scalar-control invoice", "Full recursive or precision invoice", "Kappa improvement"],
    }
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"])
    print("all712=2 phase_identities=144 phase_values=389088 hole_eigenvalues=4096")
    print("capture=4224 unload=64 windows=4 owner_rank=73")


if __name__ == "__main__":
    main()
