#!/usr/bin/env python3
"""Independent rational corroboration from pinned literal inputs.

Run ``python3 source_review.py`` from this package, or ``--receipt PATH`` to
write a measured JSON result. No Lean data/definitions or pending masks are
read. This is external Python evidence, not a kernel proof or a CI result.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
import argparse
from collections import defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PHASE1 = HERE.parent / "lean-pr442-level-model"
INPUTS = HERE.parent / "lean-multi-host-source" / "inputs"
PINS = {
    "frames.json.gz": "884480e45865a9d9d57f5f7198844a64271b046bc95e9820efbefb9e10878330",
    "states.json.gz": "40c063fd3d7b63c735f762097e692b5c36f618c60e8ed257de9e5f92be11b48e",
    "geometry.json.gz": "fc7b29b16ee754ca9717973b745d6322bbf8351a5e35e3fc9e0fbf7a88dc0317",
    "hosted-template.json.gz": "dd7833dcaff8c84b258847f4c4d65b6402c702700ae37d2c464083ee37b24126",
}


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def git_blob(blob):
    return hashlib.sha1(b"blob " + str(len(blob)).encode() + b"\0" + blob).hexdigest()


def load(name):
    blob = (INPUTS / name).read_bytes()
    raw = gzip.decompress(blob)
    assert digest(raw) == PINS[name], ("published input hash", name)
    return json.loads(raw)


def clean(matrix):
    return {key: value for key, value in matrix.items() if value}


def add(a, b, coefficient=1):
    result = defaultdict(Q, a)
    for key, value in b.items():
        result[key] += coefficient * value
    return clean(result)


def transpose(a):
    return {(j, i): value for (i, j), value in a.items()}


def mul(a, b):
    rows = defaultdict(list)
    for (i, j), value in b.items():
        rows[i].append((j, value))
    result = defaultdict(Q)
    for (i, k), value in a.items():
        for j, other in rows[k]:
            result[i, j] += value * other
    return clean(result)


def inverse(a):
    size = len(a)
    z = [[Q(v) for v in row] + [Q(i == j) for j in range(size)]
         for i, row in enumerate(a)]
    for j in range(size):
        pivot = next(i for i in range(j, size) if z[i][j])
        z[pivot], z[j] = z[j], z[pivot]
        divisor = z[j][j]
        z[j] = [v / divisor for v in z[j]]
        for i in range(size):
            if i != j and z[i][j]:
                coefficient = z[i][j]
                z[i] = [a - coefficient * b for a, b in zip(z[i], z[j])]
    return [row[size:] for row in z]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    frames = load("frames.json.gz")["frames"]
    state = load("states.json.gz")
    geometry = load("geometry.json.gz")
    template = load("hosted-template.json.gz")

    # Join the old word to its published PR370 blob, and the inherited route
    # generator to its published PR386 blob. These retained metadata are
    # evidence of source provenance; the historical commits need not be local.
    carrier = ROOT / "research/e8-bit-carrier-skeleton"
    pin370 = json.loads((carrier / "SOURCE-pr370.json").read_text())
    pin386 = json.loads((carrier / "SOURCE-pr386.json").read_text())
    old_word_blob = (PHASE1 / "inputs/pr386-word.json.gz").read_bytes()
    assert git_blob(old_word_blob) == pin370["identical"][
        "data/bit/bitE8-r865.json.gz"]["blob"] == "8bec1751f7e33c3a1e4673ef5dbc34d6f205321e"
    assert git_blob((carrier / "code/nine/geometry.py").read_bytes()) == pin386[
        "identical"]["code/nine/geometry.py"]["blob"] == "91594e0223e8fac49162b5aef834ffaa8e94a254"
    assert pin370["commit"] == "b7fe9cdf2da009c947ff6b334c562bc190b30373"
    assert pin386["commit"] == "dd11cf8069554f0333afde398f12a56c3a7c29dd"
    source442_blobs = {
        "research/idle-axis-hosting/bit_hosted.py": "e2f015dbb78a95c121e187b3c20e0f8d59b60586",
        "research/e8-early-reset-kernel/bit_global.py": "f6fb51535b53988d106f0883872b26fc249efd8d",
    }
    for source_path, published_blob in source442_blobs.items():
        assert git_blob((ROOT / source_path).read_bytes()) == published_blob
    old_geometry_blob = (PHASE1 / "inputs/pr386-geometry.json.gz").read_bytes()
    assert digest(old_geometry_blob) == geometry["inherited_geometry_sha256"] == (
        "5c980202227859e8bb9b863f94503930c2a59d460c0421356688e2b0d828b4a1")
    old_geometry = json.loads(gzip.decompress(old_geometry_blob))
    old_word = json.loads(gzip.decompress(old_word_blob))
    assert old_geometry["ports"] == geometry["ports"]
    assert old_word["lines"] == [port["q"] for port in geometry["ports"]]
    assert old_word["start"][:240] == [state["initial"][str(i)] for i in range(240)]
    assert old_word["final"][:240] == [state["final"][str(i)] for i in range(240)]

    # Replay endpoint origins using pair identities and the immediately next
    # bridge. Recorded levels/ranks are not used to choose either endpoint.
    origins = [None] * 4
    observations = {}
    schedule = template["schedule"][:10]
    for position, event in enumerate(schedule):
        kind = event["kind"]
        if kind == "local_cover_sweep":
            origins[event["pair"]] = (event["stage"], event["reverse"])
        elif kind == "idle":
            following = schedule[position + 1]
            assert following["kind"] == "bridge"
            pair = event["pair"]
            if pair == following["dst"]:
                partner = following["src"]
            else:
                assert pair == following["src"]
                partner = following["dst"]
            observations[event["idx"]] = (origins[pair], origins[partner])
            origins[pair] = origins[partner]
        else:
            assert kind == "bridge"
            assert origins[event["dst"]] == origins[event["src"]]
    assert observations[1] == ((1, True), (2, False))
    assert observations[2] == (None, (3, True))
    calls = [call for call in template["calls"]
             if call["replica"] == 0 and call["stage"] < 4]
    assert [call["stage"] for call in calls] == list(range(4))
    owner_checks = 0
    for call in calls:
        reverse = call["orientation"] == "reverse"
        for side in [0, 1]:
            local_side = 1 - side if reverse else side
            for port in range(120):
                assert call["owners"][local_side * 120 + port] == [
                    (2 * call["pair"] + side) * 120 + port,
                    ["data", call["stage"], port]]
                owner_checks += 1

    identity8 = {(i, i): Q(1) for i in range(8)}
    identity64 = {(i, i): Q(1) for i in range(64)}
    projector_cache = {}

    def projector(frame_id):
        if frame_id not in projector_cache:
            rows = frames[str(frame_id)]["B"]
            if not rows:
                result = {}
            else:
                gram = [[sum(Q(a) * Q(b) for a, b in zip(x, y))
                         for y in rows] for x in rows]
                gram_inverse = inverse(gram)
                basis = clean({(i, j): Q(value) for i, row in enumerate(rows)
                               for j, value in enumerate(row)})
                gram_inverse = clean({(i, j): value for i, row in enumerate(gram_inverse)
                                      for j, value in enumerate(row)})
                result = mul(mul(transpose(basis), gram_inverse), basis)
            projector_cache[frame_id] = result
        return projector_cache[frame_id]

    def local_id(port, reverse, after, side, swap=True):
        local_side = 1 - side if reverse and swap else side
        final = not after if reverse else after
        return state["final" if final else "initial"][str(120 * local_side + port)]

    def exterior(port, stage, cumulative=True):
        routes = geometry["ports"][port]["routes"]
        axes = (sum([route["axes"][8:] for route in routes[:stage + 1]], [])
                if cumulative else routes[stage]["axes"][8:])
        return {(i, i): Q(1) for i in axes}

    def route(port, stage, axis_shift=0):
        if not stage:
            return identity64
        axes = geometry["ports"][port]["routes"][stage]["axes"][:]
        if axis_shift:
            axes[8:] = [i + axis_shift for i in axes[8:]]
        rho = geometry["ports"][port]["rho15"]
        result = {(axes[i], axes[j]): Q(value) for i, row in enumerate(rho)
                  for j, value in enumerate(row) if Q(value)}
        result.update({(i, i): Q(1) for i in range(64) if i not in axes})
        return result

    def entrance(port, side):
        return projector(state["initial"][str(120 * side + port)])

    def endpoint(port, stage, reverse, after, side, *, ambient=False,
                 cumulative=True, swap=True, axis_shift=0):
        local = projector(local_id(port, reverse, after, side, swap))
        if reverse:
            local = add(identity64 if ambient else identity8, local, -1)
        lifted = add(local, exterior(port, stage, cumulative))
        routing = route(port, stage, axis_shift)
        return mul(mul(routing, lifted), transpose(routing))

    def origin_endpoint(port, origin, side):
        return (entrance(port, side) if origin is None
                else endpoint(port, *origin, True, side))

    def physical_level(port, stage, side):
        local = (add(identity8, projector(state["initial"][str(port)]), -1)
                 if side else identity8)
        return add(local, exterior(port, stage))

    checks = 0
    for port in range(120):
        root_row = geometry["ports"][port]["q"]
        root = {(i, j): Q(a * b, 4) for i, a in enumerate(root_row)
                for j, b in enumerate(root_row) if a * b}
        assert entrance(port, 0) == root and entrance(port, 1) == {}
        checks += 2
        for stage, reverse in [(1, True), (2, False), (3, True)]:
            for side in [0, 1]:
                assert endpoint(port, stage, reverse, True, side) == physical_level(port, stage, side)
                assert endpoint(port, stage, reverse, False, side) == physical_level(port, stage - 1, side)
                checks += 2
        difference1 = {(i, i): Q(1)
                       for i in geometry["ports"][port]["routes"][2]["axes"][8:]}
        difference2 = add(add(identity8, root, -1), exterior(port, 3))
        for side in [0, 1]:
            for child, expected in [(1, difference1), (2, difference2)]:
                before, after = observations[child]
                assert add(origin_endpoint(port, after, side), origin_endpoint(port, before, side), -1) == expected
                checks += 1
        for stage in [1, 2, 3]:
            assert add(physical_level(port, stage, 0), physical_level(port, stage, 1), -1) == root
            checks += 1
        # Replay the literal rational elementary route certificate independently.
        rho = [[Q(v) for v in row] for row in geometry["ports"][port]["rho15"]]
        ops = geometry["ports"][port]["routes"][2]["elementary_inverse_replay"]
        z = [[Q(i == j) for j in range(15)] for i in range(15)]
        for kind, i, j, coefficient in reversed(ops):
            if kind == "swap":
                z[i], z[j] = z[j], z[i]
            elif kind == "scale":
                z[i] = [v / Q(coefficient) for v in z[i]]
            else:
                assert kind == "add"
                z[i] = [a - Q(coefficient) * b for a, b in zip(z[i], z[j])]
        assert z == rho
        checks += 1

    # These are semantic mutations of the actual endpoint reconstruction.
    port = side = 0
    controls = {
        "complement_ambient64_before_exterior": endpoint(port, 1, True, True, side, ambient=True) != physical_level(port, 1, side),
        "omit_cumulative_exterior": endpoint(port, 3, True, True, side, cumulative=False) != physical_level(port, 3, side),
        "omit_reflection_side_swap": endpoint(port, 1, True, True, side, swap=False) != physical_level(port, 1, side),
        "replace_literal_entrance_frame_by_zero": add(endpoint(port, 3, True, True, side), projector(0), -1) != add(add(identity8, entrance(port, side), -1), exterior(port, 3)),
        "shift_stage3_route_exterior": endpoint(port, 3, True, True, side, axis_shift=1) != physical_level(port, 3, side),
        "wrong_bridge_partner_endpoint": add(endpoint(port, 2, False, True, side), entrance(port, side), -1) != add(add(identity8, entrance(port, side), -1), exterior(port, 3)),
    }
    assert all(controls.values()), controls
    result = {
        "status": "PASS_INDEPENDENT_RATIONAL_LITERAL_GRAM_AND_ROUTE_REPLAY",
        "checks": checks, "ports": 120, "sides": 2,
        "endpoint_transport_checks": 1440, "child_difference_checks": 480,
        "distinct_side_endpoint_checks": 360, "route_certificate_checks": 120,
        "entrance_checks": 240, "literal_call_owner_checks": owner_checks,
        "negative_controls": controls, "seconds": time.monotonic() - started,
        "script_sha256": digest(Path(__file__).read_bytes()),
        "input_raw_sha256": PINS,
        "source_provenance": {"PR370": pin370["commit"], "PR386": pin386["commit"],
                              "PR442": "4e16d001d505d4f21dd2bcfc44591f9be4c279bd"},
        "pr442_original_source_blobs": source442_blobs,
        "scope": "External exact rational Python corroboration; not a Lean proof or successful CI. Literal frame Gram projectors, source schedule bridge partners/origins, call owners and rho15 certificates are reconstructed independently. No pending mask is consulted.",
    }
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
