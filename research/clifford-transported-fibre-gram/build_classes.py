"""Compare the complete native GAP output against the retained rational class data."""
import argparse
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from class_algebra import IDENTITY, apply_columns, data, require, signature, source_semantics


def reverse_high_nibble(x):
    # GAP's preserved form is antidiagonal. Reverse the high four coordinates
    # to pair low bit i with high bit 4+i, as in the project's Pauli convention.
    return (x & 15) | sum(((x >> (4 + i)) & 1) << (7-i) for i in range(4))


def adapt(raw):
    return tuple(reverse_high_nibble(apply_columns(raw, reverse_high_nibble(1 << i))) for i in range(8))


def build(path):
    raw_reps, sizes, packet_rows = json.loads(path.read_text().replace('\\\n',''))
    reps = list(map(adapt,raw_reps))
    labels = [signature(m) for m in reps]
    require(len(set(labels)) == len(reps) == len(sizes) == 81, "Native conjugacy class coverage")
    columns = list(zip(*packet_rows,strict=True))
    packets = {}
    for i, col in enumerate(columns):
        packets.setdefault(col, []).append(i)
    groups = [sorted(v,key=labels.__getitem__) for v in packets.values()]
    groups.sort(key=lambda ids: (reps[ids[0]] != IDENTITY, labels[ids[0]]))
    result = []
    for indices in groups:
        fixed = {sum(apply_columns(reps[i],v)==v for v in range(256)) for i in indices}
        require(len(fixed)==1, "Disagreement inside rational class")
        count = fixed.pop()
        require(count.bit_count()==1, "Fixed space size")
        result.append({"size":sum(sizes[i] for i in indices),"fixed":count.bit_length()-1,
                       "representatives":[list(reps[i]) for i in indices]})
    rows = sorted([r[ids[0]] for ids in groups] for r in packet_rows)
    return {"classes":result, "characters":rows}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    args=parser.parse_args()
    actual=build(args.raw)
    expected=data()
    require(source_semantics(actual["classes"],actual["characters"]) ==
            source_semantics(expected["classes"],expected["characters"]), "Native table mismatch")
    print("PASS native Sp(8,2) class representatives, sizes and rationalized characters")
