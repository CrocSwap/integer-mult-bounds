#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Selected full-history kernel witnesses. Jose Manuel, with Codex assistance.

I derive scalar rows and boundary phases from pinned data. Native interpretation
uses the explicit inherited common-frame/view theorem in README, not a new
physical compiler replay. Predecessor credit appears in README and SOURCES.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
import gzip
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PIVOTS = (0, 1, 2, 3, 4, 5, 6, 12)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def load():
    pins = json.loads((HERE / "SOURCES.json").read_bytes())
    inputs = []
    for record in pins["files"]:
        if record["usage"] != "input":
            continue
        path = ROOT / record["path"]
        need(not path.is_symlink(), "input symlink")
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == record["sha256"], "source SHA256: " + record["path"])
        blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == record["git_blob"], "source Git blob: " + record["path"])
        inputs.append(record["path"])
    manifest = json.loads((HERE / "VERIFY.json").read_bytes())
    need(sorted(inputs) == sorted(manifest["inputs"]), "complete live input declaration")
    data = {}
    with tarfile.open(ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz", "r:gz") as archive:
        for key, record in pins["archive_members"].items():
            matches = [m for m in archive.getmembers() if m.name == record["path"]]
            need(len(matches) == 1 and matches[0].isfile(), "unique regular member")
            raw = archive.extractfile(matches[0]).read()
            need(sha256(raw).hexdigest() == record["sha256"], "member SHA256: " + key)
            data[key] = json.loads(gzip.decompress(raw) if record["path"].endswith(".gz") else raw)
    return data


def add(row, other, factor):
    for j, value in other.items():
        value = row.get(j, Q(0)) + factor * value
        if value:
            row[j] = value
        else:
            row.pop(j, None)


def replay(program, orientation):
    rows = {("L", i): {i: Q(1)} for i in range(704)}
    cuts = {}
    for event in program:
        if event[0] == "center":
            k = event[1]
            need(k not in cuts, "unique centre")
            cuts[k] = dict(rows["C", k])
        elif event[0] == "scalar":
            op = event[1]
            kind, dst = op[0], tuple(op[1])
            if kind == "clear":
                rows[dst] = {}
            elif kind == "copy":
                rows[dst] = dict(rows[tuple(op[2])])
            elif kind == "scale":
                factor = Q(op[2], op[3])
                rows[dst] = {j: factor * v for j, v in rows[dst].items() if factor * v}
            else:
                need(kind == "add" and dst != tuple(op[2]), "known nonalias scalar")
                add(rows[dst], rows[tuple(op[2])], Q(op[3], op[4]))
        else:
            need(event[0] in ("phase", "climb", "adapter", "residual_adapter"), "known event")
    need(set(cuts) == set(range(8)), "eight centre cuts")
    for i in range(704):
        want = {i: Q(1)}
        if orientation == "forward" and 112 <= i < 224:
            want[i - 112] = Q(1)
        if orientation == "backward" and i < 112:
            want[i + 112] = Q(-1)
        need(rows["L", i] == want, "complete ordinary endpoint")
    need(all(not row for key, row in rows.items() if key[0] == "C"), "private cleanup")
    return [cuts[k] for k in range(8)]


def reverse_cut(program, end, output):
    """A separate adjoint calculation checks each actual pre-transport row."""
    row = {output: Q(1)}
    for event in reversed(program[:end]):
        if event[0] != "scalar":
            continue
        op = event[1]
        kind, dst = op[0], tuple(op[1])
        a = row.get(dst, Q(0))
        if not a:
            continue
        if kind == "clear":
            del row[dst]
        elif kind == "copy":
            del row[dst]
            add(row, {tuple(op[2]): Q(1)}, a)
        elif kind == "scale":
            row[dst] *= Q(op[2], op[3])
            if not row[dst]:
                del row[dst]
        else:
            need(kind == "add", "adjoint opcode")
            add(row, {tuple(op[2]): Q(1)}, a * Q(op[3], op[4]))
    need(all(kind == "L" for kind, _ in row), "no private entrance demand")
    return {j: a for (_, j), a in row.items()}


def determinant(matrix):
    a = [[Q(v) for v in row] for row in matrix]
    result = Q(1)
    for j in range(len(a)):
        pivot = next((i for i in range(j, len(a)) if a[i][j]), None)
        if pivot is None:
            return Q(0)
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            result = -result
        v = a[j][j]
        result *= v
        for i in range(j + 1, len(a)):
            factor = a[i][j] / v
            a[i] = [x - factor * y for x, y in zip(a[i], a[j])]
    return result


def act(columns, x):
    result = 0
    for i, col in enumerate(columns):
        if x >> i & 1:
            result ^= col
    return result


def route(record, stage):
    chart = record["idle_children"][0]["orthogonal_axes"][:8]
    basis = [record["q"]] + chart
    need(all(0 < a < 512 for a in basis), "nine-axis chart")
    need(all(((a & b).bit_count() % 2) == (i == j)
             for i, a in enumerate(basis) for j, b in enumerate(basis)), "orthogonal chart")
    identity = tuple(1 << i for i in range(73))
    if stage == 0:
        return identity
    swaps = [a ^ (1 << (9 + 8 * (stage - 1) + j)) for j, a in enumerate(chart)]
    cols = tuple(x ^ act(swaps, sum(((x & v).bit_count() % 2) << j
                                   for j, v in enumerate(swaps))) for x in identity)
    need(all(act(cols, act(cols, x)) == x for x in identity), "involutive route")
    need(all((a & b).bit_count() % 2 == (i == j)
             for i, a in enumerate(cols) for j, b in enumerate(cols)), "orthogonal route")
    need(act(cols, record["q"]) == record["q"], "route fixes normal")
    return cols


def signature(lines, translation=0):
    """Coefficients of sum sign*parity(axis.u)+2*parity(translation.u) mod4."""
    linear = [2 * ((translation >> i) & 1) for i in range(73)]
    quadratic = set()
    for axis, sign in lines:
        need(0 < axis < 1 << 73 and sign in (-1, 1), "signed phase line")
        bits = [i for i in range(73) if axis >> i & 1]
        for i in bits:
            linear[i] = (linear[i] + sign) % 4
        for a, i in enumerate(bits):
            for j in bits[a + 1:]:
                pair = (i, j)
                if pair in quadratic:
                    quadratic.remove(pair)
                else:
                    quadratic.add(pair)
    return tuple(linear), tuple(sorted(quadratic))


def axes(lo, hi):
    return [(1 << i, 1) for i in range(lo, hi)]


def gauges(q, stage):
    if stage == -1:
        return [(q, 1)], []
    x = axes(0, 9 + 8 * stage)
    return x, x + [(q, -1)]


def boundary(phases):
    checked = 0
    omitted = 0
    unrouted = 0
    routes = []
    first_routes = []
    for record in phases["recipes"]:
        q = record["q"]
        for stage in range(3):
            rho = route(record, stage)
            old = gauges(q, stage - 1)
            new = gauges(q, stage)
            ext = axes(9, 9 + 8 * stage)
            entrance = ([(q, 1)] + ext, ext)
            exit_ = (axes(0, 9) + ext, axes(0, 9) + ext + [(q, -1)])
            align = record["stage_alignment"][stage]
            for side, name in enumerate(("X", "Y")):
                old_routed = [(act(rho, a), sign) for a, sign in old[side]]
                new_routed = [(act(rho, a), sign) for a, sign in new[side]]
                entry_shift = act(rho, align["entry_" + name])
                exit_shift = act(rho, align["exit_" + name])
                need(signature(old_routed, entry_shift) == signature(entrance[side]), "native entry identity")
                need(signature(exit_[side], exit_shift) == signature(new_routed), "native exit identity")
                checked += 2
                omitted += signature(old_routed) != signature(entrance[side])
                unrouted += signature(old_routed, align["entry_" + name]) != signature(entrance[side])
            if stage == 2:
                routes.append(rho)
            if stage == 1:
                first_routes.append(rho)
    need(len(routes) == len(set(routes)) == 112, "distinct stage2 owner routes")
    need(len(set(first_routes)) == 112, "distinct stage1 routes for control")
    need(omitted > 0 and unrouted > 0, "effective entry-phase controls")
    return routes, {"identities": checked, "omitted_entry_failures": omitted,
                    "unrouted_entry_failures": unrouted}


def chronology(data):
    template = data["template"]
    schedule = template["execution_schedule"]
    finish = next(i for i, e in enumerate(schedule)
                  if e["kind"] == "local_cover_sweep" and e["time"] == 10)
    prefix = schedule[:finish + 1]
    need(finish == 18, "F2 event index")
    need(Counter(e["kind"] for e in prefix) ==
         {"local_cover_sweep": 11, "idle_cover_sweep": 4, "bridge": 4}, "prefix census")
    calls = {c["time"]: c for c in template["calls"]}
    need(len(calls) == 144, "unique call times")
    trace = []
    seen = []
    for index, event in enumerate(prefix):
        kind = event["kind"]
        if kind == "local_cover_sweep":
            t = event["time"]
            call = calls[t]
            need(all(call[k] == event[k] for k in ("stage", "replica", "provider_id")), "call/schedule binding")
            owners = call["owners"]
            need(len(owners) == len({f for f, _ in owners}) == 704, "injective family owners")
            need(sha256(canonical(data["programs"][call["orientation"]])).hexdigest()
                 == call["local_program_sha256"], "call/program binding")
            if t in (0, 4, 10):
                stage = (0, 4, 10).index(t)
                need((call["replica"], call["pair"], call["stage"], call["orientation"])
                     == (0, 0, stage, "backward" if t == 4 else "forward"), "paired invocation")
                need(owners[:224] == [[p, [1, stage, p % 112]] for p in range(224)], "paired route binding")
                # With Y=-X, complete F0 leaves only X live. B1 reads zero Y.
            else:
                need(not set(range(112)) & {f for f, _ in owners}, "intervening live-X contact")
            seen.append(t)
        elif kind == "idle_cover_sweep":
            need(event["pair"] == 1 and event["child_indices"] == [0, 2], "idle zero-family boundary")
        elif kind == "bridge":
            need((event["src"], event["dst"], event["coefficient"]) == (1, 0, 1), "bridge direction")
            # X0 += X1 and Y1 -= Y0; both read zero on the witness slice.
        else:
            raise ValueError("unknown schedule kind")
        trace.append({"index": index, "time": event["time"], "kind": kind,
                      "replica": event["replica"]})
    need(seen == list(range(11)), "all prior ten queries included")
    need([e["kind"] for e in prefix[:5]] == ["local_cover_sweep"] * 5, "uninterrupted F0 to B1")
    return trace


def premise_controls(data):
    results = {}
    for name in ("live_helper_contact", "bridge_reads_live_X0", "wrong_entry_phase"):
        changed = deepcopy(data)
        if name == "live_helper_contact":
            call = next(c for c in changed["template"]["calls"] if c["time"] == 8)
            call["owners"][224][0] = 0
            check = lambda: chronology(changed)
            expected = "intervening live-X contact"
        elif name == "bridge_reads_live_X0":
            event = next(e for e in changed["template"]["execution_schedule"] if e["kind"] == "bridge")
            event["src"] = 0
            check = lambda: chronology(changed)
            expected = "bridge direction"
        else:
            changed["phases"]["recipes"][0]["stage_alignment"][2]["entry_X"] ^= 1
            check = lambda: boundary(changed["phases"])
            expected = "native entry identity"
        try:
            check()
        except ValueError as error:
            need(str(error) == expected, "wrong mutation rejection")
            results[name] = str(error)
        else:
            raise ValueError("accepted changed premise: " + name)
    return results


def build():
    data = load()
    need((data["word"]["h"], data["word"]["v"], data["word"]["R"]) == (9, 112, 480), "selected dimensions")
    need(data["phases"]["m"] == data["template"]["m"] == 73, "selected axes")
    need(data["word"]["ports"] == [r["q"] for r in data["phases"]["recipes"]], "port normal order")
    cuts = {}
    for orientation in ("forward", "backward"):
        program = data["programs"][orientation]
        need(len(program) == 24767, "complete program length")
        cuts[orientation] = replay(program, orientation)
        for end, event in enumerate(program):
            if event[0] == "center":
                need(reverse_cut(program, end, ("C", event[1])) == cuts[orientation][event[1]], "reverse cut agreement")
    forward, backward = cuts["forward"], cuts["backward"]
    R = [[row.get(p, Q(0)) for p in range(112)] for row in forward]
    need(all(v.denominator == 1 for row in R for v in row), "integer source matrix")
    need(all(not row.get(p) for row in forward for p in range(112, 224)), "forward target block zero")
    need(backward == [{112 + p: v / 4 for p, v in enumerate(row) if v} for row in R], "backward target-only R/4")
    need(all(sum(a * b for a, b in zip(R[i], R[j])) == 56 * (i == j)
             for i in range(8) for j in range(8)), "RRt=56I")
    need(all(sum(row[p] ** 2 for row in R) == 4 for p in range(112)), "column squared norms")
    P = [[row[p] for p in PIVOTS] for row in R]
    need(determinant(P) == 32, "credited pivot minor")
    routes, phase_receipt = boundary(data["phases"])
    trace = chronology(data)
    witnesses = []
    for p in range(112):
        w = [56 * (p == j) - sum(row[j] * row[p] for row in R) for j in range(112)]
        need(w[p] == 52 and all(v.denominator == 1 for v in w), "integer projector witness")
        need(all(sum(a * b for a, b in zip(row, w)) == 0 for row in R), "first transcript zero")
        need(sum(bool(v) for v in w) == 53, "witness support")
        # At common owner I, data port j reads owner rho2(j). The input
        # witness occupies only g=rho2(p), so exactly j=p contributes.
        response = [sum(row[j] * w[j] for j in range(112) if routes[j] == routes[p]) for row in R]
        need(response == [52 * row[p] for row in R], "routed F2 response")
        need(any(response), "nonzero F2 response")
        if p in PIVOTS:
            witnesses.append({"port": p, "input": [int(v) for v in w], "F2": [int(v) for v in response]})
    response_matrix = [[w["F2"][k] for w in witnesses] for k in range(8)]
    response_det = determinant(response_matrix)
    need(response_det == 52 ** 8 * 32, "eight independent innovations")
    sparse = [Q(0)] * 112
    for p, value in zip((0, 1, 6, 7), (1, -1, -1, -1)):
        sparse[p] = Q(value)
    need(all(sum(a * b for a, b in zip(row, sparse)) == 0 for row in R), "credited four-port kernel")
    need(R[0][0] == 1, "nonzero sparse response")
    # Counterfactual controls demonstrate the hypotheses doing work.
    # Collapsing routes makes F2=Rw=0; preserving oldY=0 exposes B1 instead.
    need(all(sum(row[j] * sparse[j] for j in range(112)) == 0 for row in R), "collapsed-route control")
    b1_controls = {}
    for old_y_factor in (-1, 0, 1):
        # F0's completed target is (1+old_y_factor)*sparse. At common
        # owner g*rho1(0)^-1, the distinct routes isolate port0.
        after_f0_target = [(1 + old_y_factor) * v for v in sparse]
        b1 = [row[0] * after_f0_target[0] / 4 for row in R]
        need(any(b1) == (old_y_factor != -1), "target-cancellation control")
        b1_controls[str(old_y_factor)] = [str(v) for v in b1]
    # A fresh reading of the selected live coordinate distinguishes the pair.
    need(witnesses[0]["input"][0] == 52, "fresh data observation escape")
    record0 = data["phases"]["recipes"][0]
    entrance_shift = act(routes[0], record0["stage_alignment"][2]["entry_X"])
    need(entrance_shift == 917515, "stage2 entrance, not completed-X shift")
    return {
        "status": "PASS_CENTRE_HISTORY_INNOVATION",
        "conditional_native_contract": "Full-space common-frame and cover/local-view premises in pinned proof sources; no fresh native compiler replay.",
        "scalar_events_per_orientation": 24767,
        "ordinary_endpoint_rows": 1408,
        "reverse_centre_rows": 16,
        "prior_zero_centre_fields": 80,
        "observed_F2_owner": "identity",
        "innovation_complex_dimension": "8*dim(M)",
        "whole_cover_rank": "not claimed",
        "new_recursive_child_lower_bound": "not claimed",
        "prefix": trace,
        "stage2_routes": 112,
        "routes_sha256": sha256(canonical([list(r) for r in routes])).hexdigest(),
        "native_boundary": phase_receipt,
        "stage2_port0_entrance_translation": entrance_shift,
        "R": [[int(v) for v in row] for row in R],
        "projector_kernel_vectors_checked": 112,
        "pivot_ports": list(PIVOTS),
        "pivot_determinant": 32,
        "response_determinant": int(response_det),
        "witnesses": witnesses,
        "B1_target_factor_controls": b1_controls,
        "premise_mutations": premise_controls(data),
        "controls": ["collapsed_routes_remove_innovation", "oldY_zero_exposes_B1", "target_cancellation_required", "fresh_data_read_distinguishes", "omitted_entry_phase", "unrouted_entry_translation"]
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print a candidate receipt without comparing it")
    args = parser.parse_args()
    result = build()
    digest = sha256(canonical(result)).hexdigest()
    if not args.emit:
        expected = json.loads((HERE / "RESULT.json").read_bytes())
        need(type(expected) is dict and expected == {"sha256": digest}, "complete receipt digest mismatch")
    if args.emit:
        print(json.dumps({"sha256": digest, "result": result}, sort_keys=True, indent=2))
    else:
        print("PASS_CENTRE_HISTORY_INNOVATION sha256=" + digest)


if __name__ == "__main__":
    main()
