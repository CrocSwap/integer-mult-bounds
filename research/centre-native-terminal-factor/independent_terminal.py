#!/usr/bin/env python3
"""Independent adjoint audit of the selected first terminal quotient.

This checker does not import a primary checker. It consumes the same immutable
selected archive. Native lifting is the conditional argument in the accompanying
review, using exact recipes and the retained common-frame embedding semantics.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PINS = {
    "global": ("candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz", "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760"),
    "word": ("candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz", "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"),
    "programs": ("candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz", "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"),
    "phases": ("candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json", "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"),
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(root):
    path = root / ARCHIVE
    need(sha(path.read_bytes()) == ARCHIVE_SHA, "immutable archive hash")
    result = {}
    with tarfile.open(path) as archive:
        members = archive.getmembers()
        for key, (name, digest) in PINS.items():
            matches = [m for m in members if m.name == name]
            need(len(matches) == 1 and matches[0].isfile(), "unique member " + key)
            raw = archive.extractfile(matches[0]).read()
            need(sha(raw) == digest, "member bytes " + key)
            result[key] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    return result


def increment(row, role, value):
    value += row.get(role, Q(0))
    if value:
        row[role] = value
    else:
        row.pop(role, None)


def adjoint(program, stop, output):
    """Pull one output functional backwards through the literal scalar prefix.

    Native relabels are identities only in the moving-frame representation;
    scalar coefficient zeros lift using common-frame conjugation, not by
    assuming the physical relabels act identically.
    """
    row = {output: Q(1)}
    for event in reversed(program[:stop]):
        tag = event[0]
        if tag != "scalar":
            need(tag in {"phase", "center", "climb", "adapter", "residual_adapter"}, "known event")
            continue
        op = event[1]
        kind, dst = op[0], tuple(op[1])
        a = row.get(dst, Q(0))
        if kind == "clear":
            row.pop(dst, None)
        elif kind == "copy":
            row.pop(dst, None)
            if a:
                increment(row, tuple(op[2]), a)
        elif kind == "scale":
            if a:
                row[dst] = a * Q(op[2], op[3])
        elif kind == "add":
            need(dst != tuple(op[2]), "no aliasing self ADD")
            if a:
                increment(row, tuple(op[2]), a * Q(op[3], op[4]))
        else:
            raise ValueError("unknown scalar operation")
    need(all(kind == "L" for kind, _ in row), "no uncleared private input dependence")
    return {r: v for (_, r), v in row.items() if v}


def cut_rows(program):
    result = {}
    for pos, event in enumerate(program):
        if event[0] == "center":
            k = event[1]
            need(k not in result and event[4] == 8, "one rank-eight event per channel")
            result[k] = adjoint(program, pos, ("C", k))
    need(set(result) == set(range(8)), "all eight cuts")
    return [result[k] for k in range(8)]


def check_common_frames(program, word):
    current = {("L", r): f for r, f in enumerate(word["start"])}
    # A numerical start-frame ID is insufficient before a source conversion
    # or residual pre-wrapper. Those physical boundary labels are distinct.
    wrapped = {r for r in range(224, 704)
               if (word["start"][r], word["final"][r]) != (0, 1)}
    canonical = {("L", r) for r in range(112, 704) if r not in wrapped}
    checked = 0
    for event in program:
        tag = event[0]
        if tag == "climb":
            role, old, new = event[2:5]
            need(("L", role) in canonical, "climb before canonical conversion")
            need(current["L", role] == old, "climb starts in current frame")
            current["L", role] = new
        elif tag == "center":
            k, old, new = event[1:4]
            need(("C", k) in canonical, "centre canonical conversion")
            need(current["C", k] == old, "centre starts in current frame")
            current["C", k] = new
        elif tag == "scalar":
            op, frame = event[1:3]
            kind, dst = op[0], tuple(op[1])
            if kind == "clear":
                need(dst[0] == "C", "only private CLEAR")
                current[dst] = frame
                canonical.add(dst)
            else:
                need(dst in canonical, "scalar destination before/after canonical conversion")
                need(current[dst] == frame, "destination scalar frame")
                if kind in ("copy", "add"):
                    need(tuple(op[2]) in canonical, "scalar source before/after canonical conversion")
                    need(current[tuple(op[2])] == frame, "source scalar frame")
            checked += 1
        elif tag == "adapter":
            direction, role = event[1:3]
            if direction == "old_to_new":
                canonical.add(("L", role))
            elif 112 <= role < 224:
                canonical.discard(("L", role))
        elif tag == "residual_adapter":
            direction, role = event[1:3]
            if direction == "pre":
                canonical.add(("L", role))
            else:
                canonical.discard(("L", role))
    need([current["L", r] for r in range(704)] == word["final"], "all terminal frames")
    return checked


def check_endpoints(program, backward):
    """704 independent reverse functional pulls, not forward row propagation."""
    for r in range(704):
        expected = {r: Q(1)}
        if backward and r < 112:
            expected[r + 112] = Q(-1)
        elif not backward and 112 <= r < 224:
            expected[r - 112] = Q(1)
        need(adjoint(program, len(program), ("L", r)) == expected, "complete endpoint " + str(r))
    return 704


def multiply(columns, x):
    out = 0
    for i, col in enumerate(columns):
        if (x >> i) & 1:
            out ^= col
    return out


def check_routes(phases):
    """Reconstruct all 112 stage-one involutions and the needed side alignment."""
    identity = [1 << i for i in range(73)]
    for record in phases["recipes"]:
        b = record["idle_children"][0]["orthogonal_axes"][:8]
        basis = [record["q"]] + b
        need(all(((x & y).bit_count() & 1) == (i == j)
                 for i, x in enumerate(basis) for j, y in enumerate(basis)), "port orthogonal basis")
        swaps = [x ^ (1 << (9 + i)) for i, x in enumerate(b)]
        rho = [x ^ multiply(swaps, sum(((x & z).bit_count() & 1) << i
                                       for i, z in enumerate(swaps))) for x in identity]
        need(multiply(rho, record["q"]) == record["q"], "route fixes q")
        need(all(multiply(rho, multiply(rho, x)) == x for x in identity), "route involution")
        for a in record["stage_alignment"][:3]:
            need(a["entry_X"] == a["entry_Y"] and a["exit_X"] == a["exit_Y"], "same-side translations")
    return len(phases["recipes"])


def schedule_inputs(data):
    global_ = data["global"]
    key = lambda c: (c["time"], c["replica"], c["stage"], c["provider_id"])
    calls = {key(c): c for c in global_["calls"]}
    schedule = global_["execution_schedule"]
    finish = next(i for i, e in enumerate(schedule)
                  if e["kind"] == "local_cover_sweep" and e["time"] == 10)
    prefix = schedule[:finish + 1]
    need(finish == 18 and Counter(e["kind"] for e in prefix) ==
         {"local_cover_sweep": 11, "idle_cover_sweep": 4, "bridge": 4}, "exact observation boundary")
    selected = []
    for e in prefix:
        if e["kind"] != "local_cover_sweep":
            continue
        c = calls[key(e)]
        need(len(c["owners"]) == len({f for f, _ in c["owners"]}) == 704, "injective family map")
        raw = json.dumps(data["programs"][c["orientation"]], sort_keys=True, separators=(",", ":")).encode()
        need(sha(raw) == c["local_program_sha256"], "bound program for call")
        selected.append(c)
    need([c["time"] for c in selected] == list(range(11)), "chronological call census")
    for i, stage, orientation in ((0, 0, "forward"), (4, 1, "backward"), (10, 2, "forward")):
        c = selected[i]
        need((c["stage"], c["replica"], c["pair"], c["orientation"]) ==
             (stage, 0, 0, orientation), "selected invocation")
        need(c["owners"][:224] == [[r, [1, stage, r % 112]] for r in range(224)], "data view binding")
    for c in selected:
        if c["time"] not in (0, 4, 10):
            need(not ({f for f, _ in c["owners"]} & set(range(224))), "other calls cannot touch X0/Y0")
    return prefix, selected


def response_support(prefix, calls, backward_mode="normal"):
    """Family support only, conditional on the written native B1 cancellation.

    Complete helpers have unit rows, so arbitrary native wrappers can change
    their payload without changing family support. The special B1 cancellation
    is valid because Y=C_q^-1 X, same data routes, and common phase alignment;
    it is not inferred merely from support sets.
    """
    live = set(range(112))
    trace = []
    call8_helpers = []
    for e in prefix:
        kind = e["kind"]
        if kind == "local_cover_sweep":
            c = calls[e["time"]]
            families = [f for f, _ in c["owners"]]
            if c["time"] == 10:
                return live, trace, call8_helpers
            if c["time"] == 4:
                need(set(range(224)) <= live, "paired F0 response present")
                if backward_mode == "normal":
                    live -= set(range(112))
                else:
                    need(backward_mode in ("omitted", "reversed_sign"), "known B1 mutation")
            else:
                source = families[:112] if c["orientation"] == "forward" else families[112:224]
                target = families[112:224] if c["orientation"] == "forward" else families[:112]
                live.update(t for s, t in zip(source, target) if s in live)
            if c["time"] == 8:
                call8_helpers = [(r, f) for r, f in enumerate(families) if r >= 224 and f in live]
                need(not (set(families[:224]) & live), "call8 response only on helper inputs")
        elif kind == "idle_cover_sweep":
            need(e["pair"] == 1 and e["child_indices"] == [0, 2], "declared prefix idle children")
            # A unary native operation cannot create response on a zero family.
        elif kind == "bridge":
            need(e["src"] == 1 and e["dst"] == 0 and e["coefficient"] == 1, "bridge algebra binding")
            base = 896 * e["replica"]
            for p in range(112):
                if base + 224 + p in live:
                    live.add(base + p)
                if base + 112 + p in live:
                    live.add(base + 336 + p)
        else:
            raise ValueError("unsupported prefix event")
        trace.append(dict(kind=kind, time=e["time"], live_families=len(live)))
    raise ValueError("missing terminal call")


def zero_demand(rows, roles):
    return all(not row.get(r, 0) for row in rows for r in roles)


def root(v, q, sign=1):
    # Exact Gaussian pairs; independent primitive, no Clifford-kernel import.
    out = []
    for x, (a, b) in enumerate(v):
        c, d = v[x ^ q]
        out.append(((a - sign*b + c + sign*d)/2,
                    (b + sign*a + d - sign*c)/2))
    return out


def shift(v, q):
    return [v[x ^ q] for x in range(len(v))]


def minus(a, b):
    return [(x-u, y-v) for (x, y), (u, v) in zip(a, b)]


def operator_controls(q):
    v = [(Q(i == 0), Q(0)) for i in range(512)]
    x = root(v, q, -1)
    y = root(x, q, -1)
    for axis in range(9):
        x, y = root(x, 1 << axis), root(y, 1 << axis)
    zero = [(Q(0), Q(0))] * 512
    need(minus(root(x, q, -1), y) == zero, "nonconstant boundary cancellation")
    need(root(root(v, q), q) == shift(v, q), "Cq square equals translation")
    wrong_phase = [(-b, a) for a, b in y]
    need(minus(root(x, q, -1), wrong_phase) != zero, "wrong phase detected")
    need(minus(root(x, q, -1), shift(y, 1)) != zero, "unequal side translation detected")
    return ["nonconstant_cancellation", "root_square", "wrong_phase_detected", "unequal_side_translation_detected"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=HERE.parents[1])
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if args.write and args.write.exists():
        raise FileExistsError(args.write)
    data = load(args.root)
    word, programs = data["word"], data["programs"]
    need((word["v"], word["R"], word["h"]) == (112, 480, 9), "word dimensions")
    frames = {name: check_common_frames(programs[name], word) for name in ("forward", "backward")}
    endpoints = {name: check_endpoints(programs[name], name == "backward") for name in ("forward", "backward")}
    rows = cut_rows(programs["forward"])
    prefix, calls = schedule_inputs(data)
    routes = check_routes(data["phases"])
    live, trace, call8 = response_support(prefix, calls)
    need(live == set(range(112, 224)) | set(range(336, 448)), "all possible live response families before F2")
    f2 = calls[10]
    inputs = [(r, f) for r, (f, _) in enumerate(f2["owners"]) if f in live]
    targets = [r for r, _ in inputs if r < 224]
    helpers = [r for r, _ in inputs if r >= 224]
    need(targets == list(range(112, 224)) and len(helpers) == 99, "112 targets and 99 helper inputs")
    need(zero_demand(rows, targets + helpers), "native-zero coefficient criterion")
    need(len(call8) == 15, "call8 retains fifteen helper responses")
    for mutation in ("omitted", "reversed_sign"):
        changed, _, _ = response_support(prefix, calls, mutation)
        roles = [r for r, (f, _) in enumerate(f2["owners"]) if f in changed]
        need(not zero_demand(rows, roles), "B1 mutation must destroy zero-demand guarantee: " + mutation)
    # Independently realize the sign change as conjugation by -1 on source 0.
    # This keeps every other endpoint unchanged and changes X0-Y0 to X0+Y0.
    plus_word = copy.deepcopy(programs["backward"])
    plus_at = plus_word.index(["phase", "A"]) + 1
    plus_word.insert(plus_at, ["scalar", ["scale", ["L", 0], -1, 1], word["start"][0]])
    plus_word.append(["scalar", ["scale", ["L", 0], -1, 1], word["final"][0]])
    check_common_frames(plus_word, word)
    need(adjoint(plus_word, len(plus_word), ("L", 0)) == {0: Q(1), 112: Q(1)},
         "literal sign-conjugated B1 endpoint")
    need(any(row.get(0) for row in rows), "changed port0 source reaches a second query")
    # A legal same-frame cold-helper injection contaminates a demanded row.
    h = next(r for r in helpers if word["start"][r] == 0)
    r = next(r for row in rows for r in row if r >= 224 and word["start"][r] == 0)
    changed = copy.deepcopy(programs["forward"])
    insert_at = changed.index(["phase", "A"]) + 1
    changed.insert(insert_at, ["scalar", ["add", ["L", r], ["L", h], 1, 1], 0])
    check_common_frames(changed, word)
    mutated_rows = cut_rows(changed)
    need(not zero_demand(mutated_rows, targets + helpers), "same-frame helper contamination detected")
    # The earlier diagnostic placement before adapters must fail closed: h
    # still has its noncanonical residual input label at that boundary.
    before_conversion = copy.deepcopy(programs["forward"])
    before_conversion.insert(1, ["scalar", ["add", ["L", r], ["L", h], 1, 1], 0])
    try:
        check_common_frames(before_conversion, word)
    except ValueError as error:
        need("canonical conversion" in str(error), "wrong pre-wrapper rejection")
    else:
        raise ValueError("pre-wrapper scalar contamination accepted")
    controls = operator_controls(word["ports"][0])
    encoded = [{str(r): str(v) for r, v in sorted(row.items())} for row in rows]
    result = dict(status="PASS_INDEPENDENT_TERMINAL_ADJOINT_CONDITIONAL_NATIVE_LIFT",
                  archive_sha256=ARCHIVE_SHA, member_sha256={k: v[1] for k, v in PINS.items()},
                  reverse_adjoint_endpoint_rows=endpoints, common_frame_scalar_events=frames,
                  centre_rows=encoded, centre_rows_sha256=sha(json.dumps(encoded, sort_keys=True, separators=(",", ":")).encode()),
                  schedule_events=len(prefix), source_support_trace=trace, first_stage_q_routes=routes,
                  f2_target_zero_columns=len(targets), f2_helper_zero_columns=len(helpers),
                  call8_live_helpers=call8, f2_live_helpers=[(r, f) for r, f in inputs if r >= 224],
                  controls=controls + ["omitted_B1_detected", "reversed_B1_sign_detected", "same_frame_helper_contamination_detected", "pre_wrapper_contamination_rejected"],
                  helper_contamination=dict(source=h, destination=r, event_index=insert_at,
                      placement="immediately after phase A marker, after all entry/residual adapters",
                      nonzero_coefficients={str(k): str(row[h]) for k, row in enumerate(mutated_rows) if row.get(h)}),
                  scope="Independent scalar adjoints, supports and primitive controls; universal native factorization uses the written common-frame/endpoint proof. No full native rank, dirty-offset implementation, child saving, or supplier claim.")
    if args.write:
        with args.write.open("x", encoding="utf-8", newline="\n") as out:
            out.write(json.dumps(result, sort_keys=True, indent=2)+"\n")
    else:
        expected=json.loads((HERE/"INDEPENDENT.json").read_bytes())
        need(json.dumps(expected,sort_keys=True)==json.dumps(result,sort_keys=True), "complete independent receipt mismatch")
    print("PASS_INDEPENDENT_TERMINAL_ADJOINT_CONDITIONAL_NATIVE_LIFT endpoints=1408 cuts=8 live_helpers=99")


if __name__ == "__main__":
    main()
