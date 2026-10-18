"""Independent reverse-mode audit and complete private-center omission atlas.

@Scratch-net with substantial OpenAI Codex assistance. Apache-2.0.
Imports no constructor, production verifier, or predecessor implementation.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import re
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PERSISTENT, CENTERS, SIZE, PORTS = 704, 8, 712, 112
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
RECEIPT = "research/community-frontier1042-audit/RESULT.json"
CHECKPOINT = "certificates/checkpoints/frontier1042.json"
MEMBER = "slots/local/LOCAL-PROGRAMS.json.gz"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def render(value):
    """Keep exact sparse-vector entries on one line for review."""
    pretty = json.dumps(value, indent=2, sort_keys=True)
    return re.sub(r'\[\n\s*(\d+),\n\s*"(-?\d+(?:/\d+)?)"\n\s*\]',
                  r'[\1, "\2"]', pretty) + "\n"


def read(path):
    return json.loads(path.read_bytes())


def sources():
    pins = read(HERE / "SOURCE-PINS.json")
    require(set(pins["files"]) == {ARCHIVE, RECEIPT, CHECKPOINT}, "source inventory differs")
    for name, digest in pins["files"].items():
        require(sha((ROOT / name).read_bytes()) == digest, "source pin differs: " + name)
    require(sha((HERE / "BASE-SELECTED.json").read_bytes()) == pins["context_sha256"], "base context differs")
    selected = read(HERE / "BASE-SELECTED.json")
    require(selected["source_prs"][0] == 1094 and 1042 in selected["source_prs"], "wrong selection lineage")
    receipt, checkpoint = read(ROOT / RECEIPT), read(ROOT / CHECKPOINT)
    require(receipt["selected_assembly_sha256"] == checkpoint["certificate_sha256"], "checkpoint binding differs")
    values = {}
    expected = {MEMBER, "slots/local/LOCAL-CHECKS.json", "slots/local/INDEPENDENT-LOCAL-REPLAY.json",
                "slots/local/FULL-WORD.json.gz"}
    require(set(pins["members"]) == expected, "member inventory differs")
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as archive:
        for name, digest in pins["members"].items():
            members = [m for m in archive.getmembers() if m.name == name]
            require(len(members) == 1 and members[0].isfile(), "member missing or duplicate")
            raw = archive.extractfile(members[0]).read()
            require(sha(raw) == receipt["artifacts"][name], "artifact binding differs")
            payload = gzip.decompress(raw) if name.endswith(".gz") else raw
            require(sha(payload) == digest, "member payload differs")
            values[name] = json.loads(payload)
    native = values["slots/local/INDEPENDENT-LOCAL-REPLAY.json"]
    require(native["helpers"] == 480 and native["v"] == PORTS, "wrong retained ancestor")
    require(native["local_programs_sha256"] == receipt["artifacts"][MEMBER], "native program binding differs")
    programs = values[MEMBER]
    checks = values["slots/local/LOCAL-CHECKS.json"]
    require(set(programs) == {"forward", "backward"}, "orientation missing")
    for direction, events in programs.items():
        require(sha(canonical(events)) == checks[direction]["sha256"], "event payload differs")
    return pins, programs


def register(value):
    require(isinstance(value, list) and len(value) == 2, "malformed register")
    kind, index = value
    require(type(index) is int and index >= 0, "malformed register index")
    if kind == "L":
        require(index < PERSISTENT, "persistent register out of range")
        return index
    require(kind == "C" and index < CENTERS, "private register out of range")
    return PERSISTENT + index


def operations(events):
    result = []
    for index, event in enumerate(events):
        if event[0] != "scalar":
            continue
        word = event[1]
        kind, dst = word[0], register(word[1])
        src, coefficient = None, Q(1)
        if kind in ("add", "copy"):
            src = register(word[2])
            require(src != dst, "aliasing source and target")
        if kind == "add":
            coefficient = Q(word[3], word[4])
        elif kind == "scale":
            coefficient = Q(word[2], word[3])
        else:
            require(kind in ("copy", "clear"), "unknown scalar operation")
        require(coefficient and coefficient.denominator & (coefficient.denominator - 1) == 0,
                "nonzero dyadic coefficient required")
        result.append((index, kind, dst, src, coefficient))
    return result


def add_row(target, source, coefficient=Q(1)):
    for column, value in list(source.items()):
        total = target.get(column, Q(0)) + coefficient * value
        if total:
            target[column] = total
        else:
            target.pop(column, None)


def pullback(ops, omission=None):
    """Joint reverse-mode covectors: input index -> output functional weights."""
    rows = [{i: Q(1)} for i in range(SIZE)]
    for index, kind, dst, src, q in reversed(ops):
        if index == omission:
            continue
        if kind == "add":
            add_row(rows[src], rows[dst], q)
        elif kind == "scale":
            rows[dst] = {column: value * q for column, value in rows[dst].items()}
        elif kind == "clear":
            rows[dst] = {}
        else:
            old = rows[dst]
            rows[dst] = {}
            add_row(rows[src], old)
    return rows


def expected(direction):
    rows = [{i: Q(1)} if i < PERSISTENT else {} for i in range(SIZE)]
    if direction == "forward":
        for source in range(PORTS):
            rows[source][PORTS + source] = Q(1)
    else:
        for source in range(PORTS):
            rows[PORTS + source][source] = Q(-1)
    return rows


def evaluate(ops, values, omission=None):
    """Direct value execution, independently of symbolic covector rows."""
    state = dict(values)
    for index, kind, dst, src, q in ops:
        if index == omission:
            continue
        if kind == "add":
            value = state.get(dst, Q(0)) + q * state.get(src, Q(0))
        elif kind == "scale":
            value = q * state.get(dst, Q(0))
        elif kind == "copy":
            value = state.get(src, Q(0))
        else:
            value = Q(0)
        if value:
            state[dst] = value
        else:
            state.pop(dst, None)
    return state


def prefix_functional(ops, functional):
    """Single covector through a prefix, with scalar coefficients, not row maps."""
    state = dict(functional)
    for _, kind, dst, src, q in reversed(ops):
        weight = state.get(dst, Q(0))
        if kind == "scale":
            state[dst] = weight * q
        elif kind == "add":
            state[src] = state.get(src, Q(0)) + q * weight
        elif kind == "copy":
            state.pop(dst, None)
            state[src] = state.get(src, Q(0)) + weight
        else:
            state.pop(dst, None)
        state = {key: value for key, value in state.items() if value}
    return state


def vector(value):
    return [[index, str(coefficient)] for index, coefficient in sorted(value.items())]


def matrix_digest(rows):
    return sha(canonical([vector(row) for row in rows]))


def delta(mutant, baseline):
    rows = []
    for after, before in zip(mutant, baseline):
        row = dict(after)
        add_row(row, before, Q(-1))
        rows.append(row)
    return rows


def atlas(direction, ops, baseline):
    result, classes = [], Counter()
    for position, (index, kind, dst, src, _) in enumerate(ops):
        if dst < PERSISTENT or kind not in ("clear", "copy"):
            continue
        mutant = pullback(ops, index)
        defect = delta(mutant, baseline)
        # S(I-E)P = (S e_dst) (e_dst^T P) for CLEAR;
        # COPY uses (e_dst^T-e_src^T)P instead.
        response = evaluate(ops[position + 1:], {dst: Q(1)})
        functional = {dst: Q(1)}
        if kind == "copy":
            functional[src] = Q(-1)
        sensitivity = prefix_functional(ops[:position], functional)
        factored = [{output: value * sensitivity[input_] for output, value in response.items()}
                    if input_ in sensitivity else {} for input_ in range(SIZE)]
        require(defect == factored, "rank-one factorization differs at event " + str(index))
        nonzero = any(defect)
        ordinary_detects = any(defect[:PERSISTENT])
        classification = ("redundant" if not nonzero else
                          "ordinary_input_visible" if ordinary_detects else "private_input_only")
        classes[classification] += 1
        witness = None
        if nonzero:
            input_ = next(i for i in range(SIZE) if defect[i])
            honest = evaluate(ops, {input_: Q(1)})
            faulty = evaluate(ops, {input_: Q(1)}, index)
            actual = dict(faulty)
            add_row(actual, honest, Q(-1))
            require(actual == defect[input_], "direct witness differs")
            require(actual, "empty adverse witness")
            witness = {"input": input_, "output_difference": vector(actual)}
        result.append({"direction": direction, "event_index": index, "operation": kind,
                       "center": dst - PERSISTENT, "classification": classification,
                       "defect_rank": int(nonzero), "ordinary_inputs_detect": ordinary_detects,
                       "response": vector(response), "sensitivity": vector(sensitivity),
                       "defect_sha256": matrix_digest(defect), "witness": witness})
    return result, dict(sorted(classes.items()))


def verify():
    pins, programs = sources()
    receipts = {}
    for direction in ("backward", "forward"):
        ops = operations(programs[direction])
        baseline = pullback(ops)
        require(baseline == expected(direction), "arbitrary-input endpoint differs: " + direction)
        faults, classes = atlas(direction, ops, baseline)
        receipts[direction] = {"events": len(programs[direction]), "scalar_macros": len(ops),
                               "input_coordinates": SIZE, "output_coordinates": SIZE,
                               "persistent_coordinates": PERSISTENT, "private_coordinates": CENTERS,
                               "matrix_sha256": matrix_digest(baseline), "fault_sites": len(faults),
                               "classification": classes, "faults": faults}
    require(sum(r["fault_sites"] for r in receipts.values()) == 40, "omission census incomplete")
    return {"status": "PASS_R480_PRIVATE_CENTER_ADJOINT", "assignment_seed": 80,
            "base_commit": pins["base_commit"], "selected_at_base": 1094,
            "scope": "Finite scalar macro projection and single private-center CLEAR/COPY omissions",
            "kappa": "unchanged", "programs": receipts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new certificate; refuses existing output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.write:
        with args.write.open("x") as out:
            out.write(render(result))
    else:
        require(canonical(result) == canonical(read(HERE / "CERTIFICATE.json")), "certificate differs")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS_R480_PRIVATE_CENTER_ADJOINT coordinates=712 orientations=2 omissions=40 no_new_kappa")


if __name__ == "__main__":
    main()
