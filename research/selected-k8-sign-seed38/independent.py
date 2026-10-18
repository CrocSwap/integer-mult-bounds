"""Independent integer-dyadic arithmetic, lowering, splitting and sign compiler.

Scratch-net with substantial OpenAI Codex assistance. Apache-2.0.
Imports neither Fraction nor the primary verifier or predecessor code.
Checks the same finite construction; no independent human review is claimed.
"""
import gzip
import hashlib
import json
from collections import Counter
from math import gcd
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = "slots/local/"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
RECEIPT = "research/community-frontier1042-audit/RESULT.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def reduce_pair(n, d):
    require(d != 0, "zero denominator")
    if d < 0:
        n, d = -n, -d
    divisor = gcd(n, d)
    return n // divisor, d // divisor


def power_two(n):
    return n > 0 and n & (n - 1) == 0


def lower(operation):
    """Reconstruct the PR696 convention without importing its implementation."""
    kind, dst = operation[0], tuple(operation[1])
    work = ("W", 0)
    require(dst != work, "work aliases macro target")
    if kind == "clear":
        return [("clear", dst)]
    if kind == "copy":
        src = tuple(operation[2])
        require(src != work, "work aliases macro source")
        return [("copy", dst, src)]
    if kind == "scale":
        numerator, denominator = reduce_pair(operation[2], operation[3])
        require(power_two(abs(numerator)) and power_two(denominator), "invalid scale")
        shift = abs(numerator).bit_length() - denominator.bit_length()
        result = [("double" if shift > 0 else "halve", dst)] * abs(shift)
        if numerator < 0:
            result += [("negate", dst)]
        return result
    require(kind == "add", "invalid macro")
    src = tuple(operation[2])
    numerator, denominator = reduce_pair(operation[3], operation[4])
    require(src not in (dst, work) and numerator != 0 and power_two(denominator), "invalid add")
    update = "add" if numerator > 0 else "subtract"
    if abs(numerator) == denominator:
        return [(update, dst, src), ("clear", work)]
    result = [("copy", work, src)]
    for bit in format(abs(numerator), "b")[1:]:
        result += [("double", work)]
        if bit == "1":
            result += [("add", work, src)]
    result += [("halve", work)] * (denominator.bit_length() - 1)
    return result + [(update, dst, work), ("clear", work)]


def compile_signs(word):
    """Use integer +/-1 labels; materialize all labels at the final boundary."""
    signs, result = {}, []
    for instruction in word:
        kind, dst = instruction[:2]
        if kind == "negate":
            signs[dst] = -signs.get(dst, 1)
        elif kind in ("add", "subtract"):
            src = instruction[2]
            coefficient = (1 if kind == "add" else -1) * signs.get(src, 1) * signs.get(dst, 1)
            result.append(("add" if coefficient == 1 else "subtract", dst, src))
        elif kind == "copy":
            signs[dst] = signs.get(instruction[2], 1)
            result.append(instruction)
        elif kind == "clear":
            signs[dst] = 1
            result.append(instruction)
        elif kind in ("double", "halve"):
            result.append(instruction)
        else:
            raise ValueError("invalid primitive")
    result += [("negate", reg) for reg in sorted(signs) if signs[reg] == -1]
    return result


def runs(events):
    index = 0
    while index < len(events):
        if events[index][0] != "scalar":
            index += 1
            continue
        start, frame = index, events[index][2]
        while index < len(events) and events[index][0] == "scalar" and events[index][2] == frame:
            index += 1
        yield start, frame, events[start:index]


def normalize(coefficients, depth):
    if not coefficients:
        return {}, 0
    while depth and all(n % 2 == 0 for n in coefficients.values()):
        coefficients = {column: n // 2 for column, n in coefficients.items()}
        depth -= 1
    return coefficients, depth


def step(rows, instruction):
    kind, dst = instruction[:2]
    coefficients, depth = rows[dst]
    if kind == "clear":
        rows[dst] = ({}, 0)
    elif kind == "copy":
        source, scale = rows[instruction[2]]
        rows[dst] = (dict(source), scale)
    elif kind == "negate":
        rows[dst] = ({column: -n for column, n in coefficients.items()}, depth)
    elif kind == "double":
        rows[dst] = ((dict(coefficients), depth - 1) if depth else
                     ({column: 2 * n for column, n in coefficients.items()}, 0))
    elif kind == "halve":
        rows[dst] = normalize(coefficients, depth + 1)
    elif kind in ("add", "subtract"):
        source, source_depth = rows[instruction[2]]
        new_depth = max(depth, source_depth)
        result = {column: n << (new_depth - depth) for column, n in coefficients.items()}
        sign = 1 if kind == "add" else -1
        for column, n in source.items():
            value = result.get(column, 0) + sign * (n << (new_depth - source_depth))
            if value:
                result[column] = value
            else:
                result.pop(column, None)
        rows[dst] = normalize(result, new_depth)
    else:
        raise ValueError("invalid primitive")


def identity(registers):
    return {reg: ({reg: 1}, 0) for reg in registers}


def norm(row):
    coefficients, depth = row
    return reduce_pair(sum(abs(n) for n in coefficients.values()), 1 << depth)


def maximum(left, right):
    return right if left[0] * right[1] < right[0] * left[1] else left


def rational_text(pair):
    return str(pair[0]) if pair[1] == 1 else str(pair[0]) + "/" + str(pair[1])


def endpoint_digest(rows):
    serialized = []
    for reg, (coefficients, depth) in sorted(rows.items()):
        serialized.append([reg, [[column, *reduce_pair(n, 1 << depth)]
                                  for column, n in sorted(coefficients.items())]])
    return digest(canonical(serialized))


def replay(events, checks, registers):
    require(digest(canonical(events)) == checks["sha256"], "event hash differs")
    require(len(events) == checks["events"], "event count differs")
    full = [identity(registers), identity(registers)]
    peaks, depths = [(1, 1), (1, 1)], [0, 0]
    counts = [Counter(), Counter()]
    streams = [hashlib.sha256(), hashlib.sha256()]
    boundary = hashlib.sha256()
    access_hash = hashlib.sha256()
    changes, census = [], Counter()
    macros, n_runs = 0, 0
    for start, frame, block in runs(events):
        before = [p for event in block for p in lower(event[1])]
        after = compile_signs(before)
        old_accesses = [("update" if p[0] in ("add", "subtract") else p[0], *p[1:])
                        for p in before if p[0] != "negate"]
        new_accesses = [("update" if p[0] in ("add", "subtract") else p[0], *p[1:])
                        for p in after if p[0] != "negate"]
        require(old_accesses == new_accesses, "access sequence differs")
        access_hash.update(canonical([start, frame, new_accesses]) + b"\n")
        touched = {reg for p in before for reg in p[1:]}
        require({reg for p in after for reg in p[1:]} <= touched, "register added")
        local = [identity(touched), identity(touched)]
        local_peaks = [{reg: (1, 1) for reg in touched} for _ in range(2)]
        local_depths = [{reg: 0 for reg in touched} for _ in range(2)]
        for version, word in enumerate((before, after)):
            for instruction in word:
                step(local[version], instruction)
                step(full[version], instruction)
                dst = instruction[1]
                local_peaks[version][dst] = maximum(local_peaks[version][dst], norm(local[version][dst]))
                local_depths[version][dst] = max(local_depths[version][dst], local[version][dst][1])
                peaks[version] = maximum(peaks[version], norm(full[version][dst]))
                depths[version] = max(depths[version], full[version][dst][1])
                counts[version][instruction[0]] += 1
                streams[version].update(canonical([frame, instruction]) + b"\n")
        require(local[0] == local[1] and full[0] == full[1], "endpoint differs: " + str(start))
        require(local_peaks[0] == local_peaks[1] and local_depths[0] == local_depths[1],
                "run precision differs: " + str(start))
        endpoint = endpoint_digest(local[1])
        boundary.update(canonical([start, frame, len(block), endpoint]) + b"\n")
        saving = 2 * (len(before) - len(after))
        require(saving >= 0, "cost increased")
        census[saving] += 1
        if saving:
            changes.append({"start_event": start, "frame": frame, "scalar_macros": len(block),
                            "baseline_real_primitives": 2 * len(before),
                            "candidate_real_primitives": 2 * len(after),
                            "real_saved": saving, "endpoint_sha256": endpoint})
        macros += len(block)
        n_runs += 1
    require(macros == checks["scalar_macros"], "incomplete macro coverage")
    require(peaks[0] == peaks[1] and depths[0] == depths[1], "projection precision differs")
    require(all(not row[0] for reg, row in full[1].items() if reg[0] != "L"), "private work remains")
    opaque = [[i, e] for i, e in enumerate(events) if e[0] != "scalar"]
    paid = Counter(e[5] if e[0] == "climb" else e[4] for _, e in opaque if e[0] in ("climb", "center"))
    require({str(k): v for k, v in paid.items()} == checks["paid_profile"], "profile differs")
    for kind in ("copy", "clear", "double", "halve"):
        require(counts[0][kind] == counts[1][kind], "non-sign cost differs")
    require(counts[0]["add"] + counts[0]["subtract"] == counts[1]["add"] + counts[1]["subtract"],
            "source-read count differs")
    return {
        "formal_input_columns": len(registers), "logical_columns": 704, "private_input_columns": 9,
        "events": len(events), "scalar_macros": macros, "runs": n_runs,
        "boundary_maps_sha256": boundary.hexdigest(), "non_scalar_events": len(opaque),
        "non_negation_accesses_sha256": access_hash.hexdigest(),
        "indexed_non_scalar_sha256": digest(canonical(opaque)),
        "baseline_real_primitives": 2 * sum(counts[0].values()),
        "candidate_real_primitives": 2 * sum(counts[1].values()),
        "real_saved": 2 * (sum(counts[0].values()) - sum(counts[1].values())),
        "baseline_tags_per_component": dict(sorted(counts[0].items())),
        "candidate_tags_per_component": dict(sorted(counts[1].items())),
        "baseline_primitive_sha256": streams[0].hexdigest(), "candidate_primitive_sha256": streams[1].hexdigest(),
        "scalar_projection_row_l1_max": list(map(rational_text, peaks)),
        "scalar_projection_fractional_bits_max": depths,
        "scalar_projection_endpoint_sha256": endpoint_digest(full[1]),
        "paid_profile": dict(sorted(checks["paid_profile"].items())),
        "run_savings_census": {str(k): v for k, v in sorted(census.items())}, "changed_runs": changes,
    }


def verify():
    pins = read(HERE / "SOURCE-PINS.json")
    context = pins["selected_context"]
    context_bytes = (HERE / context["path"]).read_bytes()
    require(digest(context_bytes) == context["sha256"], "selected context pin differs")
    selected = json.loads(context_bytes)
    require(selected["kappa"] == context["kappa"] and
            selected["audited_source_head"] == context["audited_source_head"], "selected context differs")
    required = {"research/complex-dyadic-lowering/lower.py",
                "research/ck-sign-normalization-seed22/compile.py",
                ARCHIVE, RECEIPT}
    require(set(pins["files"]) == required, "source inventory differs")
    for name, pin in pins["files"].items():
        data = (ROOT / name).read_bytes()
        require(pin["representation"] == "file bytes", "source representation differs")
        require(digest(data) == pin["sha256"], "source pin differs: " + name)
    saved = read(ROOT / RECEIPT)
    require(saved["selected_assembly_sha256"] == selected["certificate_sha256"], "assembly differs")
    values = {}
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as archive:
        for name, pin in pins["members"].items():
            members = [m for m in archive.getmembers() if m.name == name]
            require(len(members) == 1 and members[0].isfile(), "member missing or duplicated")
            data = archive.extractfile(members[0]).read()
            if name != "RESULT.json":
                require(digest(data) == saved["artifacts"][name], "saved artifact differs")
            payload = gzip.decompress(data) if name.endswith(".gz") else data
            require(digest(payload) == pin["sha256"], "member payload differs")
            values[name] = json.loads(payload)
    require(canonical(values["RESULT.json"]) == canonical(saved), "saved receipt differs")
    require(digest(canonical(values[PROVIDER + "FULL-WORD.json.gz"])) == pins["selected_word_content_sha256"],
            "wrong selected word")
    native = values[PROVIDER + "INDEPENDENT-LOCAL-REPLAY.json"]
    require(native["helpers"] == 480 and native["v"] == 112, "wrong ancestor")
    require(native["local_programs_sha256"] == saved["artifacts"][PROVIDER + "LOCAL-PROGRAMS.json.gz"],
            "native program differs")
    programs, checks = values[PROVIDER + "LOCAL-PROGRAMS.json.gz"], values[PROVIDER + "LOCAL-CHECKS.json"]
    require(set(programs) == {"forward", "backward"}, "orientation missing")
    registers = {reg for events in programs.values() for event in events if event[0] == "scalar"
                 for primitive in lower(event[1]) for reg in primitive[1:]}
    require(registers == {("L", i) for i in range(704)} | {("C", i) for i in range(8)} | {("W", 0)},
            "register inventory differs")
    result = {"status": "PASS_SELECTED_K8_SIGN_NORMALIZATION", "base_commit": pins["base_commit"],
              "assignment_seed": 38, "source_pr": 1042, "kappa": "unchanged",
              "programs": {d: replay(programs[d], checks[d], registers) for d in ("backward", "forward")}}
    require(canonical(result) == canonical(read(HERE / "EXPECTED.json")), "independent receipt differs")
    return result


if __name__ == "__main__":
    result = verify()
    print("PASS_SELECTED_K8_SIGN_INDEPENDENT runs=2166+2166 columns=713 saved=408/408 receipt=identical")
