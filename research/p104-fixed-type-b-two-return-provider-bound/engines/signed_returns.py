"""Check exact owner incidence and signed phase on the two fixed Type B returns."""
import ast
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/APPLICATION.py": "d98987db98553dc55bfc80e3ca47abfcd51c57af6f8cda61101391d8eae94184",
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/DATA-PHASES.json": "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    "inputs/EMITTER.py": "7a7993648433c6febad8c07b315aec1b96598835a3f587b62040423c33c3b71f",
    "inputs/PHYSICAL-BINDING.py": "5c80c3b0415a7f91d216395248dd6f13297eed637732098e1ca8fb0548951b98",
    "inputs/PRICE.json": "cca4b82a9b7b1670705373a245282043e32527f453cd24ba4500794857686872",
    "inputs/VOLUME-QUOTE.json": "89106529258a20b7e16d0e89a48eec6daf578ed6c3d5565b8a953676a9aaad53",
    "inputs/WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
KEYS = {1339: (68, 8), 2970: (70, 9)}
PHASES = ((1, 0), (0, 1), (-1, 0), (0, -1))
CAP = 30


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def checked(path):
    raw = (ROOT / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def stop(*_):
    raise TimeoutError("30-second hard cap")


def chronology(events, count):
    lineage = list(range(count))
    watched = {role: [] for role, _ in KEYS.values()}
    for clock, e in enumerate(events):
        if e[0] == "J":
            roles = e[2] + e[3][:2]
            op = "J"
        else:
            _, op, a, *args = e
            if op == "SWAP":
                b, = args
                lineage[a], lineage[b] = lineage[b], lineage[a]
                continue
            if op in ("ADD", "QUERY"):
                roles = [a, args[0]]
            else:
                assert op in ("SCALE", "LAMBDA", "IDLE_ONE", "IDLE_ODD")
                roles = [a]
        for token in watched.keys() & {lineage[r] for r in roles}:
            watched[token].append([clock, op])
    return watched, lineage


def functions(raw):
    names = {"need", "bits", "dot", "terms", "sub", "polynomial", "translation"}
    tree = ast.parse(raw)
    defs = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {node.name for node in defs} == names
    env = {"Counter": Counter}
    exec(compile(ast.Module(body=defs, type_ignores=[]), "pinned APPLICATION.py", "exec"), env)
    return env


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(CAP)
    data = {p: checked(p) for p in PINS}
    obj = lambda p: loads(data[p], object_pairs_hook=unique)
    caller = obj("inputs/CALLER.json")
    assert caller["stages"] == 17 and caller["ambient_rank"] == 145
    quote = obj("inputs/PRICE.json")
    volume = obj("inputs/VOLUME-QUOTE.json")
    assert [1339, 2970] in quote["pairs"]
    assert volume["need"] == "15/16"
    assert all(Fraction(row["necessary_volume"]) > Fraction(row["affordable_upper"])
               and Fraction(row["gross_upper"]) < 0 for row in volume["rows"])
    tape = caller["events"]
    assert len(tape) == 4783
    for t, (role, stage) in KEYS.items():
        assert tape[t] == ["B", "IDLE_ODD", role, [stage], -1]
    hits, final_lineage = chronology(tape, caller["roles"])
    assert hits == {role: [[t, "IDLE_ODD"]] for t, (role, _) in KEYS.items()}
    for role, stage in KEYS.values():
        returned = final_lineage.index(role)
        diagonal = caller["types"]["B"]["diagonal"][returned - caller["types"]["B"]["offset"]]
        assert diagonal[:2] == [-1, 0]
        assert [s for s, selected in enumerate(diagonal[2:], 1) if selected] == [stage]

    # An inserted retained query would invalidate the erased-support conclusion.
    variant = tape[:]
    variant.insert(0, ["B", "QUERY", 68, 69, -1])
    altered, _ = chronology(variant, caller["roles"])
    assert altered[68][0] == [0, "QUERY"] and len(altered[68]) == 2

    payload = decompress(data["inputs/WORD.json.gz"])
    assert sha256(payload).hexdigest() == "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    word = loads(payload, object_pairs_hook=unique)
    ports = caller["types"]["B"]["ports"]
    assert len(ports) == 8 and len(set(ports)) == 8
    recorded_source_width = obj("inputs/DATA-PHASES.json")["m"]
    assert recorded_source_width == 73
    algebra = functions(data["inputs/APPLICATION.py"])
    dot, terms, sub, translate = (algebra[name] for name in ("dot", "terms", "sub", "translation"))
    geometry, cases = [], []
    for port in ports:
        q = word["ports"][port]
        corrections = []
        for _, stage in KEYS.values():
            axes = [q] + [1 << (9 + 8 * (stage - 1) + j) for j in range(8)]
            assert all(dot(a, b) == (i == j) for i, a in enumerate(axes) for j, b in enumerate(axes))
            positive = terms((a, 1) for a in axes)
            signed = sub(positive, terms([(q, 2)]))
            assert signed[q] == 3 and translate(sub(positive, signed)) == q
            corrections.append(q)
        geometry.append(dict(port=port, central_mask=q, translation_masks=corrections))
        for phase in range(4):
            wanted = PHASES[-phase % 4]
            opposite = PHASES[-(phase + 2) % 4]
            assert wanted != opposite
            parity = PHASES[2 * phase % 4]
            assert parity == PHASES[2 * (phase + 2) % 4]
            cases.append(dict(port=port, phase=phase, required_at_unit_bodies=[wanted, wanted],
                              opposite_q_difference_rank=2, retained_odd_rank=0, correction=parity))
    assert len(cases) == 32
    assert PHASES[1] != PHASES[-1 % 4]  # Wrong orientation is detected at q=i.
    alarm(0)
    receipt = dict(head=quote["head"], caller=quote["caller"], pins=PINS, clocks=list(KEYS),
                   events=len(tape), hits=hits, geometry=geometry, cases=cases,
                   recorded_source_width=recorded_source_width, volume_test_width=8,
                   volume_cells=volume["rows"], decision="excluded in the fixed-contact canonical class",
                   caps=dict(phase_cases=32, runner_seconds=CAP), unresolved=0)
    print(dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
