"""Check the borrowed centre word without the producer implementation."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

from check_decoder_rank_budget import ROOT, REPO, require, sources


def read(name, pin, compressed=False):
    raw = (ROOT / name).read_bytes()
    if compressed:
        raw = gzip.decompress(raw)
    require(sha256(raw).hexdigest() == pin, "A reviewed input changed: " + name)
    return json.loads(raw)


def index(register):
    return register[1] + (704 if register[0] == "C" else 0)


def plus(target, source, coefficient):
    for key, value in source.items():
        result = target.get(key, Q(0)) + coefficient * value
        if result:
            target[key] = result
        else:
            target.pop(key, None)


def replay(program, word):
    rows = [{i: Q(1)} for i in range(712)]
    frames = word["start"] + [0]*8
    cost, gates, native = 0, Counter(), Counter()
    for event in program:
        if event[0] == "climb":
            _, _, target, before, after, rank = event
            require(frames[target] == before, "A native entry frame is wrong.")
            frames[target] = after
            native[rank] += 1
        if event[0] != "scalar":
            continue
        gate, frame = event[1:]
        kind, target = gate[0], index(gate[1])
        gates[kind] += 1
        require(kind in ("add", "scale"), "A borrowed word clears or copies a field.")
        require(frames[target] == frame, "A scalar target frame is wrong.")
        if kind == "add":
            source, coefficient = index(gate[2]), Q(gate[3], gate[4])
            require(frames[source] == frame, "A scalar source frame is wrong.")
            plus(rows[target], rows[source], coefficient)
        else:
            coefficient = Q(gate[2], gate[3])
            rows[target] = {key: coefficient*value for key, value in rows[target].items()}
        a, b = abs(coefficient.numerator), coefficient.denominator
        require(a > 0 and b & (b-1) == 0, "A coefficient is not a nonzero dyadic.")
        if kind == "scale":
            require(a & (a-1) == 0, "A scale is not a power of two.")
            cost += 2*(abs(a.bit_length()-b.bit_length())+int(coefficient < 0))
        else:
            cost += 2*(3+a.bit_length()-1+a.bit_count()+b.bit_length()-1)
    require(frames == word["final"]+[0]*8, "The complete frames changed.")
    return rows, cost, gates, native


def main():
    old = read("lanes/circuit-interface/CENTRE-FREE-PROGRAMS.json.gz",
               "fa60b4af013dd8b8db289845e3ed597720ff955751ad270c3d58236b64080877", True)
    new = read("lanes/circuit-interface/borrowed-centres/BORROWED-CENTRES-PROGRAMS.json.gz",
               "6b88cf885e22ef745eee74db04adc7feadfcc63a8248e8873b1a4caf76b21096", True)
    interface = read("lanes/circuit-interface/INTERFACE.json",
                     "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3")
    word = sources.load_local(REPO)["CANONICAL-WORD.json.gz"]
    r = [[Q(row.get(str(p), 0)) for p in range(112)] for row in interface["R"]]
    j = [[Q(a == b)-sum(r[k][a]*r[k][b] for k in range(8))/4
          for b in range(112)] for a in range(112)]
    checks = {}
    for direction in ("forward", "backward"):
        program = new["programs"][direction]
        native = lambda p: [event for event in p if event[0] != "scalar"]
        require(native(program) == native(old[direction]), "A native event or phase label changed.")
        rows, cost, gates, children = replay(program, word)
        expected = [{i: Q(1)} for i in range(712)]
        for a in range(112):
            target, offset, sign = (112+a, 0, 1) if direction == "forward" else (a, 112, -1)
            plus(expected[target], {offset+b: q for b, q in enumerate(j[a]) if q}, Q(sign))
        require(rows == expected, "The complete arbitrary-input content map is wrong.")
        require(cost == 207606 and sum(gates.values()) == 20653,
                "The literal scalar invoice differs.")
        require(sum(rank*count for rank, count in children.items()) == 5522,
                "The native rank mass differs.")
        start = program.index(["phase", "centre_dirty_correction"])
        finish = program.index(["phase", "A"])
        block = program[start+1:finish]
        require(len(block) == 1160 and all(e[0] == "scalar" and e[2] == 0 for e in block),
                "The borrowed block is not the expected zero-frame word.")
        bad = program[:start+1] + program[start+2:]
        wrong, _, _, _ = replay(bad, word)
        require(any(any(k >= 704 for k in row) for row in wrong[:704]),
                "Omitting the initial subtraction did not expose borrowed data.")
        bad = program[:finish-1] + program[finish:]
        wrong, _, _, _ = replay(bad, word)
        require(wrong[704:] != expected[704:], "Omitting the last uncompute did not break restoration.")
        checks[direction] = dict(input_columns=712, arbitrary_helpers_restored=480,
                                 arbitrary_centre_fields_restored=8, native_events_unchanged=True,
                                 scalar_frames_checked=True, native_rank_mass=5522,
                                 scalar_macros=sum(gates.values()), real_primitives=cost,
                                 baseline_omission_rejected=True, uncompute_omission_rejected=True)
    report = dict(status="PASS_INDEPENDENT_BORROWED_CENTRES_NATIVE_INTERFACE",
                  producer_imported=False, source_commit=sources.BASE,
                  checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  borrowed_payload_sha256="6b88cf885e22ef745eee74db04adc7feadfcc63a8248e8873b1a4caf76b21096",
                  checks=checks,
                  scope="The actual unchanged native frames and children with arbitrary borrowed centre state. The old exact complex native contracts are inherited.",
                  not_claimed=["The stage-seven private cancellation preserves these fields",
                               "A global query carrier schedule", "A complete supplier or kappa gain"])
    (ROOT / "root/BORROWED-CENTRES-REVIEW.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(report["status"])
    print(json.dumps(checks, sort_keys=True))


if __name__ == "__main__":
    main()
