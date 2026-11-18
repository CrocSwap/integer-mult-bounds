"""Check the new gate list against a direct floor-count specification."""

from collections import Counter

from circuit import COIN_WIRE, FIRST_SCRATCH, MODULUS, PACKET_WIDTH, Gate, reversible_step

WEIGHTS = (144, 12, 12, 1)
PERIOD = 156
EXPECTED = (232, 2238, 590, 473)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def packet(phase: int, node: int, done: bool = False) -> int:
    return phase | (node << 8) | (int(done) << 10)


def comparisons() -> tuple[tuple[int, int], ...]:
    cases = []
    unfinished = 1
    phase = 1
    powers = 1
    phases = set()
    for _ in range(PERIOD):
        require(phase not in phases, "phase repeated before the closing edge")
        phases.add(phase)
        next_phase = (2 * powers) % MODULUS
        leaves = tuple(
            label for label, weight in enumerate(WEIGHTS)
            if (2 * powers * weight) // MODULUS - 2 * (powers * weight // MODULUS)
        )
        require(1 <= unfinished <= 3, "reference index does not fit two bits")
        for rank in range(2 * unfinished):
            node, coin = divmod(rank, 2)
            output = leaves[rank] if rank < len(leaves) else rank - len(leaves)
            before = packet(phase, node) | (coin << COIN_WIRE)
            after = packet(next_phase, output, rank < len(leaves)) | (coin << COIN_WIRE)
            cases.append((before, after))
        unfinished = 2 * unfinished - len(leaves)
        powers *= 2
        phase = next_phase
    require((phase, unfinished) == (1, 1), "reference graph did not close")
    return tuple(cases)


def lanes(records: tuple[int, ...], width: int) -> list[int]:
    return [
        sum(((record >> wire) & 1) << index for index, record in enumerate(records))
        for wire in range(width)
    ]


def run(gates: tuple[Gate, ...], records: tuple[int, ...], width: int) -> list[int]:
    state = lanes(records, width)
    full = (1 << len(records)) - 1
    for target, controls in gates:
        flip = full
        for control in controls:
            flip &= state[control]
        state[target] ^= flip
    return state


def main() -> None:
    gates, width = reversible_step()
    for target, controls in gates:
        require(0 <= target < width and target != COIN_WIRE, "illegal gate target")
        require(len(controls) <= 2 and len(set(controls)) == len(controls), "illegal gate arity")
        require(all(0 <= x < width and x != target for x in controls), "illegal gate controls")
    counts = Counter(len(controls) for _, controls in gates)
    bill = (counts[0], counts[1], counts[2], width - FIRST_SCRATCH)
    require(bill == EXPECTED, f"gate or scratch bill changed: {bill}")

    pairs = comparisons()
    before, after = zip(*pairs, strict=True)
    require(len(set(after)) == len(after), "reference inverse is not unique")
    require(run(gates, before, width) == lanes(after, width), "forward or cleanup mismatch")
    require(run(tuple(reversed(gates)), after, width) == lanes(before, width), "inverse mismatch")

    # A spurious NOT on an erased bit must change the check, even with correct outputs.
    dirty = (*gates, (FIRST_SCRATCH, ()))
    require(run(dirty, before, width) != lanes(after, width), "dirty scratch went undetected")
    # A spurious NOT on the stopping flag leaves the phase and node intact.
    wrong_stop = (*gates, (PACKET_WIDTH - 1, ()))
    require(run(wrong_stop, before, width) != lanes(after, width), "wrong stop went undetected")
    print("PASS_PAIRED_DDG_ARITHMETIC_STEP")
    print(f"{len(pairs)} complete forward/inverse transitions; two fault controls")
    print(f"{bill[0]} X, {bill[1]} CNOT, {bill[2]} Toffoli; {len(gates)} total gates")
    print(f"{bill[3]} temporary Boolean wires plus {PACKET_WIDTH} clean packet backing bits")


if __name__ == "__main__":
    main()
