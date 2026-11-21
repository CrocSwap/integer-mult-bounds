from collections import Counter
from fractions import Fraction
from pathlib import Path
import sys

native = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(native))
from source_inputs import activate

activate()
from raw_binary import Catalogue

c = Catalogue(134, 1)
counts = Counter()
pairs = {tuple(sorted((row[2], row[3]))) for row in c.graph["program"] if row[0] == "MOVE"}
pairs.update(
    tuple(sorted((s, t)))
    for s, t in zip(c.graph["start"][2 * c.ports :], c.graph["final"][2 * c.ports :], strict=True)
)
for word in [c.joint(port) for port in range(c.ports)] + [
    c.difference(s, t).word for s, t in pairs
]:
    for gate in word:
        if gate[0] == "scale":
            value = Fraction(gate[2])
            counts[value] += 1
            counts[1 / value] += 1
print(
    "pairs",
    len(pairs),
    "joint",
    c.ports,
    "scale_types",
    len(counts),
    "max_scalar_limb",
    max(max(abs(x.numerator), x.denominator) for x in counts),
)
print("scales", dict(sorted((str(k), v) for k, v in counts.items())))
