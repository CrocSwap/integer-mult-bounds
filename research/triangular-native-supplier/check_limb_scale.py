"""Check every small ternary unit against the full physical permutation."""

import sys
from io import BytesIO
from random import Random

sys.path.append(sys.argv[1])
from limb_scale import unit_scale
from streaming_routes import cold_swap_tape

rng = Random(3)
count = moved = 0
for v in range(1, 9):
    base = 3**v
    prefix = 2 if v % 2 else 3
    piece = 3
    records = [rng.randbytes(piece) for _ in range(prefix * base)]
    source = b"".join(records)
    sample = [u for u in range(1, base) if u % 3]
    if v > 4:
        sample = rng.sample(sample, 6)
    for unit in sample:
        before = BytesIO(source)
        after = BytesIO()
        unit_scale(before, after, v, prefix, piece, unit, cold_swap_tape)
        back = pow(unit, -1, base)
        expected = b"".join(
            records[p * base + (j * back % base)] for p in range(prefix) for j in range(base)
        )
        assert after.getvalue() == expected, (v, unit)
        count += 1
        moved += len(records)
print(
    "checked", count, "complete unit routes and", moved, "arbitrary ternary records through width 8"
)
