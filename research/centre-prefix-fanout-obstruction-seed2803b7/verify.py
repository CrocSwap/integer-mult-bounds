#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact common-frame scalar test for early, no-storage centre fanout."""
import argparse
import copy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
BASE = "candidate/strict/global/base/providers/gauge44/"
RECORD_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER_SHA256 = {
    "CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "LOCAL-PROGRAMS.json.gz": "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    "LOCAL-CHECKS.json": "2b8b1891a736598010232bfb26abc31973b265a53a2009a3fcfd9138b5ecadb4",
}
MEMBER_PAYLOAD_SHA256 = {
    "CANONICAL-WORD.json.gz": "4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c",
    "LOCAL-PROGRAMS.json.gz": "9f41d53659e9be84e20c661560c5687abbf5cd0660cdecbe01ad5eb29e6b8ee3",
    "LOCAL-CHECKS.json": "2b8b1891a736598010232bfb26abc31973b265a53a2009a3fcfd9138b5ecadb4",
}
SOURCES = [92, 57, 81, 224, 11, 240, 9, 256]
FRAMES = list(range(415, 423))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def pinned_inputs():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    need(manifest["base_commit"] == "e112d71c8d7bb32435debcc54df932593dd8223a",
         "research base changed")
    paths = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = (ROOT / row["path"]).resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), "invalid/missing pinned source")
        raw = path.read_bytes()
        need(sha256(raw) == row["sha256"], "source pin mismatch: " + row["path"])
        paths[row["path"]] = path
    need(paths.get("certificates/selected-result.json") is not None,
         "selected record is not declared")
    need(sha256(paths["certificates/selected-result.json"].read_bytes()) == RECORD_SHA256,
         "selected-record identity changed")
    need(paths.get(ARCHIVE) is not None, "selected replay archive is not declared")
    need(sha256(paths[ARCHIVE].read_bytes()) == ARCHIVE_SHA256, "selected archive changed")
    return paths[ARCHIVE]


def load_source_data(archive_path):
    result = {}
    with tarfile.open(archive_path, "r:gz") as archive:
        for name, expected in MEMBER_SHA256.items():
            raw = archive.extractfile(BASE + name).read()
            need(sha256(raw) == expected, "selected archive member bytes changed: " + name)
            payload = gzip.decompress(raw) if name.endswith(".gz") else raw
            need(sha256(payload) == MEMBER_PAYLOAD_SHA256[name],
                 "selected archive member payload changed: " + name)
            result[name] = json.loads(payload)
    return result


def cut_rows(canonical, source):
    return [(row[1], Fraction(row[3], row[4]))
            for row in canonical["cut"] if row[2] == source]


def validate_data(canonical, programs, checks):
    need(canonical["v"] == 112 and canonical["centers"] == SOURCES and
         canonical["center_frames"] == FRAMES, "selected centre inventory changed")
    need(len(canonical["cut"]) == 176, "selected cut cardinality changed")
    need(canonical["frames"][0] == [], "common frame is not the empty frame")
    for phase in ("forward", "backward"):
        need(canonical_digest(programs[phase]) == checks[phase]["sha256"],
             "complete selected program digest changed: " + phase)

    events = programs["forward"]
    centers = [(i, event) for i, event in enumerate(events) if event[0] == "center"]
    need(len(centers) == 8, "forward centre event count changed")
    for k, (i, event) in enumerate(centers):
        need(event == ["center", k, FRAMES[k], 0, 8], "forward centre event changed")
        block = events[i + 1:i + 23]
        parsed = []
        for scalar in block:
            need(scalar[0] == "scalar" and scalar[1][0] == "add",
                 "centre scatter is no longer 22 scalar additions")
            op = scalar[1]
            need(op[1] == ["L", op[1][1]] and op[2] == ["C", k],
                 "centre scatter address changed")
            need(type(op[1][1]) is int and 0 <= op[1][1] < 704 and
                 type(op[3]) is int and type(op[4]) is int and op[4] != 0,
                 "invalid centre scatter scalar")
            parsed.append((op[1][1], Fraction(op[3], op[4])))
        need(len(parsed) == 22 and parsed == cut_rows(canonical, SOURCES[k]),
             "forward scatter differs from the pinned canonical cut")
        need(events[i + 23] == ["scalar", ["clear", ["C", k]], 0],
             "centre scratch is not cleared after scatter")
    return events


def addr_key(addr):
    need(isinstance(addr, list) and len(addr) == 2 and addr[0] in ("L", "C"),
         "unexpected scalar address")
    return addr[0], addr[1]


def scale(vector, q):
    return {symbol: coefficient * q for symbol, coefficient in vector.items()
            if coefficient * q}


def add(target, source, q):
    out = dict(target)
    for symbol, coefficient in source.items():
        out[symbol] = out.get(symbol, Fraction(0)) + q * coefficient
        if not out[symbol]:
            del out[symbol]
    return out


def run_projection(events, canonical, channel, early):
    """Keep exact scalar maps; phase/frame/native events are projected away."""
    state = {}
    basis = ("c", channel)
    if early:
        for target, coefficient in cut_rows(canonical, SOURCES[channel]):
            key = ("L", target)
            state[key] = add(state.get(key, {}), {basis: Fraction(1)}, coefficient)

    for event in events:
        tag = event[0]
        if tag == "center":
            k = event[1]
            state[("C", k)] = {} if early or k != channel else {basis: Fraction(1)}
            continue
        if tag != "scalar":
            continue
        op = event[1]
        target = addr_key(op[1])
        if op[0] == "clear":
            state[target] = {}
        elif op[0] == "copy":
            state[target] = dict(state.get(addr_key(op[2]), {}))
        elif op[0] == "scale":
            state[target] = scale(state.get(target, {}), Fraction(op[2], op[3]))
        elif op[0] == "add":
            state[target] = add(state.get(target, {}), state.get(addr_key(op[2]), {}),
                                Fraction(op[3], op[4]))
        else:
            raise ValueError("unknown scalar operation: " + str(op[0]))
    return {key: value for key, value in state.items() if value}


def fixture_controls():
    x, c = ("x", 0), ("c", 0)

    def compare(prefix, early_injection):
        before = {("L", 0): {x: Fraction(1)}}
        after = {k: dict(v) for k, v in before.items()}
        for target, coefficient in early_injection:
            key = ("L", target)
            before[key] = add(before.get(key, {}), {c: Fraction(1)}, coefficient)
        for op, target, coefficient in prefix:
            before[target] = scale(before.get(target, {}), coefficient) if op == "scale" else before.get(target, {})
            if op == "scale" and not before[target]:
                before.pop(target, None)
            if op != "scale":
                raise ValueError("bad control prefix")
        for op, target, coefficient in prefix:
            after[target] = scale(after.get(target, {}), coefficient) if op == "scale" else after.get(target, {})
            if op == "scale" and not after[target]:
                after.pop(target, None)
            if op != "scale":
                raise ValueError("bad control prefix")
        for target, coefficient in early_injection:
            key = ("L", target)
            after[key] = add(after.get(key, {}), {c: Fraction(1)}, coefficient)
        return before == after

    need(compare([], [(1, Fraction(1, 3))]), "identity-prefix positive control failed")
    need(not compare([("scale", ("L", 0), Fraction(2))], [(0, Fraction(1))]),
         "read-before-center negative control failed")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()

    archive = pinned_inputs()
    data = load_source_data(archive)
    canonical = data["CANONICAL-WORD.json.gz"]
    programs = data["LOCAL-PROGRAMS.json.gz"]
    checks = data["LOCAL-CHECKS.json"]
    events = validate_data(canonical, programs, checks)
    scalar_count = sum(event[0] == "scalar" for event in events)
    need(scalar_count == 19693, "selected forward scalar event count changed")
    fixture_controls()

    # A mutated coefficient must fail against the exact selected forward scatter.
    mutated = copy.deepcopy(canonical)
    mutated["cut"][0][3] += 1
    rejected = False
    try:
        validate_data(mutated, programs, checks)
    except ValueError:
        rejected = True
    need(rejected, "mutated-cut negative control was accepted")

    channels = []
    for k in range(8):
        normal = run_projection(events, canonical, k, early=False)
        early = run_projection(events, canonical, k, early=True)
        # Compare every local role explicitly; sparse zero vectors are equivalent to zeros.
        different = [("L", role) for role in range(704)
                     if normal.get(("L", role), {}) != early.get(("L", role), {})]
        different += [("C", role) for role in range(8)
                      if normal.get(("C", role), {}) != early.get(("C", role), {})]
        need(different, "expected a noncommuting channel but found equality")
        need(all(key[0] == "L" for key in different), "a center scratch differs at endpoint")
        role114 = normal.get(("L", 114), {}).get(("c", k), Fraction(0)) - \
                  early.get(("L", 114), {}).get(("c", k), Fraction(0))
        channels.append({
            "channel": k,
            "center_source_role": SOURCES[k],
            "different_endpoint_roles": len(different),
            "first_different_role": list(different[0]),
            "role_114_normal_minus_early": str(role114),
        })
    counts = [row["different_endpoint_roles"] for row in channels]
    need(counts == [34, 34, 36, 36, 54, 54, 56, 56],
         "exact endpoint difference census changed")
    need(channels[0]["role_114_normal_minus_early"] == "1/4",
         "exact role-114 witness changed")

    result = {
        "status": "SCOPED_NEGATIVE_RESULT",
        "seed": "2803b7f39d0d886af6d0a63cd1521a40",
        "track": "recursive-interfaces",
        "task_id": "centre-path-sharing",
        "base_commit": "e112d71c8d7bb32435debcc54df932593dd8223a",
        "selected_record_sha256": RECORD_SHA256,
        "archive_sha256": ARCHIVE_SHA256,
        "model": "exact Q-linear common-frame projection of all 19693 scalar events in the selected forward program; all 704 local roles are compared, with zero coordinates implicit; native frame, climb and adapter events are omitted",
        "comparison": "normal center scatter at its selected event versus the same canonical 176-entry scatter injected before the forward program and all center outputs suppressed",
        "basis_domain": "the eight formal center outputs c_0,...,c_7; exact Fraction coefficients",
        "channel_results": channels,
        "controls": {"identity_prefix_commutes": True,
                     "target_read_before_center_does_not_commute": True,
                     "mutated_canonical_cut_rejected": True},
        "conclusion": "The no-storage early-fanout timing move fails exact endpoint equality in every basis channel in this pinned scalar projection. This is not a result about native frame transport, persistent storage, reordered full-call phases, other schedules, suppliers, or kappa.",
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write_result:
        out = args.write_result.resolve()
        need(not out.exists(), "refusing to overwrite result path")
        out.write_text(encoded)
    print("PASS_CENTRE_PREFIX_FANOUT_OBSTRUCTION channels=8 mismatched=8 "
          "counts=" + ",".join(map(str, counts)) +
          " center0_role114=1/4 controls=3 no_new_kappa")


if __name__ == "__main__":
    main()
