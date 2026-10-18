"""Emit the credited PR2182 star upper bound; this is not a new construction.

Mason Hale, with OpenAI Codex assistance. Apache-2.0.
"""


def star(n):
    if not isinstance(n, int) or n < 4:
        raise ValueError("need n >= 4")
    roots = n - 3
    gray = [i ^ (i >> 1) for i in range(1 << (n - 4))]
    operations, frame = [], 0
    for phase in range(2):
        if phase:
            operations += [["B", j, j - 3] for j in range(4, n)]
        for t, point in enumerate((0, 1, 3, 2)):
            itinerary = gray if t % 2 == 0 else gray[::-1]
            for destination in itinerary:
                for bit in range(n - 4):
                    if (frame ^ destination) >> bit & 1:
                        operations.append(["X", 0, bit + 1])
                        frame ^= 1 << bit
                for other in range(4):
                    low = (point | other << 2) if phase == 0 else (other | point << 2)
                    mask = low | destination << 4
                    if mask:
                        operations.append(["A", mask, 0])
            operations.append(["B", 2 * phase + (t % 2), 0])
    operations += [["B", j, j - 3] for j in range(4, n)]
    return {"sources": n, "roots": roots, "operations": operations}
