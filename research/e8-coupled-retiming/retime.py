"""Change E8 frame assignments and count the resulting blocks."""

from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SOURCE_SHA256 = "3594f19c4d01cf11fb930c5c61baeed399620acbc5b94096b16bcacb23997dd3"
# All positions refer to the original, zero-based phase-A gate list.
MOVES = ((65, 187, 64, (388, 771), 285),
         (100, 198, 98, (693, 839), 296))


def registers(gate):
    return {gate[2]} | {term[0] for term in gate[3]} | set(gate[4] if gate[0] == "out" else [])


def build(source):
    candidate = deepcopy(source)
    additions = {}
    for origin, destination, source_register, targets, frame in MOVES:
        gate = candidate["A"][origin]
        assert gate[0] == "out" and gate[2] == source_register and not gate[4]
        selected = [term for term in gate[3] if term[0] in targets]
        assert len(selected) == len(targets)
        touched = {source_register, *targets}
        # The moved additions commute with every gate they cross.
        assert all(not (registers(g) & touched) for g in source["A"][origin + 1:destination])
        assert source["A"][destination][1] == frame
        gate[3] = [term for term in gate[3] if term[0] not in targets]
        additions[destination] = ["out", frame, source_register, selected, []]
    candidate["A"] = [g for i, gate in enumerate(candidate["A"])
                      for g in ([additions[i], gate] if i in additions else [gate])]
    frame = len(candidate["frames"])
    assert frame == 946
    candidate["frames"].append([256, 128, 64, 39, 20, 15])
    for index in (193, 916, 917):
        assert candidate["B"][index][1] == 599
        candidate["B"][index][1] = frame
    frame = len(candidate["frames"])
    assert frame == 947
    assert candidate["frames"][585] == [161, 81, 9, 5, 3]
    assert candidate["B"][873] == ["out", 585, 550, [[198, 1, 2], [202, -1, 2]], []]
    assert candidate["B"][874] == ["in", 585, 550, [[521, 1, 1]]]
    candidate["frames"].append([305, 161, 81, 9, 5, 3])
    for index in (873, 874):
        candidate["B"][index][1] = frame
    candidate["derived_from"] = (
        "Three frame changes from Sussman E8 at 9c94857b; see PROOF.md"
        "; move B873 and B874 to one common rank-six frame"
    )

    current = list(candidate["start"])
    blocks = {role: Counter() for role in "xysc"}
    v = candidate["v"]

    def climb(register, frame):
        old = current[register]
        if old != frame:
            role = "x" if register < v else "y" if register < 2 * v else "s"
            rank = len(candidate["frames"][frame]) - len(candidate["frames"][old])
            assert rank > 0
            blocks[role][rank] += 1
            current[register] = frame

    for phase in ("A", "B"):
        if phase == "B":
            for _, register, frame in candidate["ret"]:
                assert current[register] == frame
                blocks["c"][len(candidate["frames"][frame])] += 1
        for gate in candidate[phase]:
            for register in registers(gate):
                climb(register, gate[1])
    for register, frame in enumerate(candidate["final"]):
        climb(register, frame)
    candidate["blocks"] = {role: {str(r): count for r, count in sorted(hist.items())}
                           for role, hist in blocks.items()}
    assert sum(r * n for hist in blocks.values() for r, n in hist.items()) == candidate["N"]
    return candidate


def main():
    if sys.flags.optimize:
        raise SystemExit("Assertions must remain enabled for generation")
    raw = gzip.decompress((ROOT / "data/original.json.gz").read_bytes())
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256
    candidate = build(json.loads(raw))
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data/retimed.json.gz"
    raw = json.dumps(candidate, separators=(",", ":")).encode()
    with output.open("wb") as stream:
        with gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0) as zipped:
            zipped.write(raw)
    print(hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
