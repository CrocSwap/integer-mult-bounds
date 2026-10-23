"""Load frozen source data and derive the two clean-J scalar words.

The source notices retain the supplier credits. New code is Apache-2.0.
The reconstruction follows the centre-encoding campaign's exact sparse
replay. Research, code and verification used OpenAI Codex assistance.
"""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import argparse
import gzip
import json
import subprocess
import tarfile


BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
ARCHIVE_SHA256 = "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754"
MEMBER_PINS = {
    "slots/local/CANONICAL-WORD.json.gz":
        "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "slots/local/LOCAL-PROGRAMS.json.gz":
        "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    "slots/local/CLIFFORD-RECIPES.json":
        "d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731",
    "slots/local/RESIDUAL-ADAPTERS.json":
        "383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c",
    "t16/global/base/work/complex-nine-native/DATA-PHASES.json":
        "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
}
PAYLOAD_PINS = {
    "CANONICAL-WORD.json.gz":
        "4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c",
    "LOCAL-PROGRAMS.json.gz":
        "9f41d53659e9be84e20c661560c5687abbf5cd0660cdecbe01ad5eb29e6b8ee3",
}
CREDIT_PINS = {
    "research/gauge44-slots-t16/NOTICE.md":
        "7a8d17b04da1e6c9d0ec217fb5bda72faa09d9a21695128722dd1e2827870fcf",
    "research/gauge44-slots-t16/construction/NOTICE.md":
        "defe7e44af610e25a6c50c1c3b2efd0972d0690574995c0c872fc50eebf4c816",
    "research/gauge44-slots-t16/UPSTREAM-NOTICE.md":
        "a75967ebc34e3bf2ff2c25c08e6c7f1a61b0c0d171cfd1b62196ae2caaf2c610",
    "research/gauge44-slots-t16/t16/NOTICE.md":
        "902370e6bfcd39dbea2ece474f15fccbcce3b8e966b2b94066bd03e5174591b5",
    "LICENSE":
        "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_git(repo, path, expected_sha256):
    """Read a blob at BASE. Do not read the worktree copy."""
    raw = subprocess.check_output(
        ["git", "show", BASE + ":" + path], cwd=Path(repo)
    )
    require(sha256(raw).hexdigest() == expected_sha256,
            "Source pin differs: " + path)
    return raw


def archive_members(repo):
    """Check the archive and each full member path before JSON parsing."""
    raw = read_git(repo, ARCHIVE, ARCHIVE_SHA256)
    result = {}
    with tarfile.open(fileobj=BytesIO(raw), mode="r:gz") as archive:
        for name, expected in MEMBER_PINS.items():
            matches = [m for m in archive.getmembers() if m.name == name]
            require(len(matches) == 1 and matches[0].isfile(),
                    "Source member is not one regular file: " + name)
            payload = archive.extractfile(matches[0]).read()
            require(sha256(payload).hexdigest() == expected,
                    "Member pin differs: " + name)
            result[name] = payload
    return result


def load_local(repo):
    """Return the five decoded objects, keyed by their file names."""
    result = {}
    for member, raw in archive_members(repo).items():
        name = member.rsplit("/", 1)[1]
        payload = gzip.decompress(raw) if name.endswith(".gz") else raw
        require(sha256(payload).hexdigest() == PAYLOAD_PINS.get(
            name, MEMBER_PINS[member]), "Payload pin differs: " + name)
        result[name] = json.loads(payload)
    return result


def add(row, other, coefficient):
    for column, value in other.items():
        value = row.get(column, 0) + coefficient * value
        if value:
            row[column] = value
        else:
            row.pop(column, None)


def product(left, right):
    result = []
    for row in left:
        result.append({})
        for k, coefficient in row.items():
            add(result[-1], right[k], coefficient)
    return result


def difference(left, right):
    result = [row.copy() for row in left]
    require(len(left) == len(right), "Matrix row counts differ")
    for row, other in zip(result, right):
        add(row, other, Q(-1))
    return result


def scale(matrix, coefficient):
    return [{j: coefficient * x for j, x in row.items() if coefficient * x}
            for row in matrix]


def replay(program, n=704, cut=None):
    """Replay exact scalar contents on all n+8 independent input columns."""
    rows = [{i: Q(1)} for i in range(n + 8)]
    for index, event in enumerate(program):
        if index == cut:
            break
        if event[0] != "scalar":
            continue
        op = event[1]
        target = op[1][1] + (n if op[1][0] == "C" else 0)
        if op[0] == "clear":
            rows[target] = {}
        elif op[0] == "scale":
            rows[target] = {j: x * Q(op[2], op[3])
                            for j, x in rows[target].items()}
        else:
            require(op[0] in ("copy", "add"), "Unknown scalar operation")
            source = op[2][1] + (n if op[2][0] == "C" else 0)
            if op[0] == "copy":
                rows[target] = rows[source].copy()
            else:
                add(rows[target], rows[source], Q(op[3], op[4]))
    return rows


def primitive_bound(op):
    """Return the retained one-real-component dyadic scalar allowance."""
    if op[0] in ("clear", "copy"):
        return 1
    coefficient = Q(op[3], op[4]) if op[0] == "add" else Q(op[2], op[3])
    a, b = abs(coefficient.numerator), coefficient.denominator
    require(a > 0 and b & (b - 1) == 0, "Non-dyadic scalar allowance")
    if op[0] == "scale":
        require(a & (a - 1) == 0, "Scale is not a signed power of two")
        return abs(a.bit_length() - b.bit_length()) + int(coefficient < 0)
    require(op[0] == "add", "Unknown scalar allowance")
    return 3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1


def corrected_program(program, H, D, backward):
    prefix = []

    def emit(target, source, coefficient):
        prefix.append(["scalar", ["add", target, source,
                       coefficient.numerator, coefficient.denominator], 0])

    for k in range(8):
        private = ["C", k]
        prefix.append(["scalar", ["clear", private], 0])
        if backward:
            for j, row in enumerate(D):
                if k in row:
                    emit(private, ["L", 112 + j], row[k])
            for j, coefficient in sorted(H[k].items()):
                emit(["L", j], private, -coefficient)
        else:
            for j, coefficient in sorted(H[k].items()):
                emit(private, ["L", j], coefficient)
            for j, row in enumerate(D):
                if k in row:
                    emit(["L", 112 + j], private, row[k])
        prefix.append(["scalar", ["clear", private], 0])
    before = program.index(["phase", "A"])
    begin = program.index(["phase", "centers"])
    end = program.index(["phase", "B"])
    return (program[:before] + [["phase", "centre_dirty_correction"]] +
            prefix + program[before:begin] + program[end:]), prefix


def check_frame_access(program, word):
    """Check the canonical scalar ledger, between the retained adapters."""
    current = word["start"].copy() + [None] * 8
    n = len(word["start"])
    for event in program:
        if event[0] == "climb":
            require(current[event[2]] == event[3], "Wrong climb input frame")
            current[event[2]] = event[4]
        elif event[0] == "scalar":
            op, frame = event[1:]
            target = op[1][1] + (n if op[1][0] == "C" else 0)
            if op[0] == "clear":
                current[target] = frame
            else:
                require(current[target] == frame, "Wrong scalar target frame")
                if op[0] in ("add", "copy"):
                    source = op[2][1] + (n if op[2][0] == "C" else 0)
                    require(current[source] == frame, "Wrong scalar source frame")
    require(current[:n] == word["final"], "Wrong persistent final frames")
    require(current[n:] == [0] * 8, "Wrong private final frames")


def reconstruct(repo):
    """Derive R,H,D,J and both exact clean words from the frozen inputs."""
    local = load_local(repo)
    word = local["CANONICAL-WORD.json.gz"]
    programs = local["LOCAL-PROGRAMS.json.gz"]
    v, n = word["v"], 2 * word["v"] + word["R"]
    require((v, n, word["h"]) == (112, 704, 9), "Wrong supplier geometry")
    boundary = replay(programs["forward"], n,
                      programs["forward"].index(["phase", "centers"]))
    R = [{j: x for j, x in boundary[c].items() if j < v}
         for c in word["centers"]]
    H = [{j: x for j, x in boundary[c].items() if j >= 2 * v}
         for c in word["centers"]]
    require(len(R) == 8 and all(
        boundary[c] == R[k] | H[k]
        for k, c in enumerate(word["centers"])), "Unexpected centre dependence")
    RT = [{k: row[j] for k, row in enumerate(R) if j in row}
          for j in range(v)]
    D = [{} for _ in range(v)]
    for event in word["cut"]:
        add(D[event[1] - v], {word["centers"].index(event[2]):
                             Q(event[3], event[4])}, Q(1))
    identity = [{i: Q(1)} for i in range(v)]
    P = scale(product(RT, R), Q(1, 4))
    J = difference(identity, P)
    require(product(R, RT) == [{i: Q(56)} for i in range(8)],
            "R R^T differs from 56 I")
    require(product(P, P) == scale(P, Q(14)), "P^2 differs from 14 P")
    require(product(J, J) == difference(scale(identity, Q(13)),
                                       scale(J, Q(12))), "Wrong J polynomial")
    checks, clean = {}, {}
    for name, program in programs.items():
        fixed, prefix = corrected_program(program, H, D, name == "backward")
        rows = replay(fixed, n)
        for i, row in enumerate(rows):
            expected = {i: Q(1)} if i < n else {}
            if name == "forward" and v <= i < 2 * v:
                add(expected, J[i - v], Q(1))
            if name == "backward" and i < v:
                add(expected, {v + j: x for j, x in J[i].items()}, Q(-1))
            require(row == expected, "Wrong clean-J map: " + name + ":" + str(i))
        check_frame_access(fixed, word)
        native = ("climb", "adapter", "residual_adapter")
        require([e for e in fixed if e[0] in native] ==
                [e for e in program if e[0] in native],
                "Persistent native events changed")
        require(not any(e[0] == "center" for e in fixed), "Centre child remains")
        first_clear = next(i for i, e in enumerate(fixed)
                           if e == ["scalar", ["clear", ["C", 0]], 0])
        dirty = replay(fixed[:first_clear] + fixed[first_clear + 1:], n)
        require(any(n in row for row in dirty[:n]),
                "Missing-private-clear control did not fail")
        start = fixed.index(["phase", "centre_dirty_correction"])
        first_add = next(i for i in range(start, len(fixed))
                         if fixed[i][0] == "scalar" and fixed[i][1][0] == "add")
        require(replay(fixed[:first_add] + fixed[first_add + 1:], n) != rows,
                "Missing-dirty-correction control did not fail")
        profile = Counter(e[5] for e in fixed if e[0] == "climb")
        mass = sum(r * count for r, count in profile.items())
        require(mass == 5522, "Wrong clean-J child rank mass")
        checks[name] = {
            "independent_input_columns": n + 8,
            "persistent_helpers_restored": word["R"],
            "private_outputs_zero": 8,
            "canonical_scalar_frames": "PASS",
            "persistent_native_events": sum(e[0] in native for e in fixed),
            "child_profile": dict(sorted(profile.items())),
            "child_rank_mass": mass,
            "removed_centre_rank_mass": sum(
                e[4] for e in program if e[0] == "center"),
            "scalar_macros": sum(e[0] == "scalar" for e in fixed),
            "primitive_bound_real_components": 2 * sum(
                primitive_bound(e[1]) for e in fixed if e[0] == "scalar"),
            "correction_adds": sum(e[1][0] == "add" for e in prefix),
            "correction_clears": sum(e[1][0] == "clear" for e in prefix),
            "missing_clear_control": "REJECT",
            "missing_correction_control": "REJECT",
        }
        clean[name] = fixed
    clean_raw = json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()
    report = {
        "status": "PASS_PINNED_CLEAN_J_RECONSTRUCTION",
        "source_base": BASE,
        "archive_sha256": ARCHIVE_SHA256,
        "clean_program_payload_sha256": sha256(clean_raw).hexdigest(),
        "geometry": {"ports": v, "helpers": word["R"], "axes": word["h"]},
        "R_row_support": dict(Counter(map(len, R))),
        "R_column_support": dict(Counter(map(len, RT))),
        "J_row_support": dict(Counter(map(len, J))),
        "orientations": checks,
        "scope": "Exact scalar maps, canonical frame access and retained native events. Native recipe phases, global hosting and supplier admission are separate.",
    }
    return {"word": word, "programs": programs,
            "recipes": local["CLIFFORD-RECIPES.json"],
            "residuals": local["RESIDUAL-ADAPTERS.json"],
            "phases": local["DATA-PHASES.json"],
            "R": R, "H": H, "D": D, "J": J,
            "clean_programs": clean, "checks": report}


def source_manifest():
    return {"base": BASE, "archive_path": ARCHIVE,
            "archive_sha256": ARCHIVE_SHA256, "members": MEMBER_PINS,
            "decompressed_payloads": PAYLOAD_PINS, "credit_sources": CREDIT_PINS}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    data = reconstruct(args.repo)
    args.out.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(data["clean_programs"], sort_keys=True,
                     separators=(",", ":")).encode()
    (args.out / "CLEAN-J-PROGRAMS.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    for name, value in (("CLEAN-J-CHECKS.json", data["checks"]),
                        ("SOURCE-MANIFEST.json", source_manifest())):
        (args.out / name).write_text(json.dumps(value, indent=2, sort_keys=True) +
                                    "\n", encoding="utf-8")
    for path, expected in CREDIT_PINS.items():
        target = args.out / "credit-evidence" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(read_git(args.repo, path, expected))
    print(data["checks"]["status"])


if __name__ == "__main__":
    main()
