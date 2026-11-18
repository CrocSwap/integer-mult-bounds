"""Check the symbolic two-target core against the literal packed word."""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path

State = tuple[int, int, int]


def packed_step(u: int, t: int, y: int, base: int, block: int) -> tuple[int, int]:
    z0, z1 = u & 1, (u // base) & 1
    data_modulus = block**2
    control_modulus = base**2
    y = (y + 2 * z0 * (t % base) + 2 * z1 * (t // base) * block) % data_modulus
    load = (y & 1) + base * ((y // block) & 1)
    t = (t + load) % control_modulus
    y = (y + z0 * (1 - 2 * (t % base)) + z1 * (1 - 2 * (t // base)) * block) % data_modulus
    unload = ((y & 1) ^ z0) + base * (((y // block) & 1) ^ z1)
    return (t - unload) % control_modulus, y


def raw(state: State, base: int, window: int) -> State:
    u, t, y = state
    block = 2 * window
    t, y = packed_step(u, t, y, base, block)
    loaded = (u + 1 + base) % base**2
    t, y = packed_step(loaded, t, y, base, block)
    return (loaded - 1 - base) % base**2, t, y


def ideal(state: State, window: int) -> State:
    u, t, y = state
    return u, t, y ^ (1 + 2 * window)


def in_core(state: State, base: int, window: int) -> bool:
    u, t, y = state
    upper_temp, lower_temp = divmod(t, base)
    lower_window = (y // 2) % window
    return (u % base < base - 1 and lower_temp < base - 1
            and upper_temp < base - 1 and lower_window + lower_temp < window)


def literal_core(state: State, base: int, window: int) -> bool:
    mate = ideal(state, window)
    return raw(state, base, window) == mate and raw(mate, base, window) == state


def check_domain(base: int, window: int, complete: bool) -> dict:
    # Largest grid is 8 * 2 * 64 * 128 * 4. The upper representatives on
    # partial grids include both parities at both ends of the window.
    block = 2 * window
    upper_controls = range(base) if complete else (0, base - 1)
    upper_blocks = range(block) if complete else (0, 1, block - 2, block - 1)
    states = agreements = 0
    for u0, u1, t, lo, hi in product(
        range(base), upper_controls, range(base**2), range(block), upper_blocks
    ):
        state = u0 + base * u1, t, lo + block * hi
        actual = literal_core(state, base, window)
        if actual != in_core(state, base, window):
            raise ValueError(f"core mismatch at B={base}, N={window}, state={state}")
        agreements += actual
        states += 1
    return dict(base=base, window=window, complete=complete, states=states, core=agreements)


def check_cover(base: int, window: int) -> dict:
    # At most 16**3 * 128 tuples; each checks the five stated translations.
    bad_without_last = 0
    for u0, t0, t1, lower_window in product(range(base), range(base), range(base), range(window)):
        good_phases = []
        for phase in range(5):
            u = (u0 + phase) % base
            t = (t0 + phase) % base + base * ((t1 + phase) % base)
            y = 2 * ((lower_window + phase * (base - 2)) % window)
            if in_core((u, t, y), base, window):
                good_phases.append(phase)
        if not good_phases:
            raise ValueError(f"uncovered coordinate tuple at B={base}, N={window}")
        bad_without_last += good_phases == [4]
    if bad_without_last == 0:
        raise ValueError("shortened menu unexpectedly covers the grid")
    return dict(base=base, window=window, tuples=base**3 * window,
                missed_without_last=bad_without_last)


def check_controls() -> list[str]:
    controls = {
        "lower temporary saturation": (0, 3, 0),
        "upper temporary saturation": (0, 12, 0),
        "source carry": (3, 0, 0),
        "lower window spill": (0, 1, 14),
    }
    for name, state in controls.items():
        if literal_core(state, 4, 8):
            raise ValueError(f"failed to expose {name}")
    if not literal_core((0, 1, 12), 4, 8):
        raise ValueError("safe side of the lower-window boundary failed")
    saturated_upper = controls["upper temporary saturation"]
    if raw(saturated_upper, 4, 8) != ideal(saturated_upper, 8):
        raise ValueError("expected a raw agreement whose ideal mate fails")
    if not literal_core(saturated_upper, 4, 4):
        raise ValueError("expected the upper-window error to wrap at N=B")
    return [*controls, "safe window boundary", "raw agreement only", "wrap at N=B"]


def main() -> None:
    checks = [
        check_domain(2, 4, complete=True),
        check_domain(4, 8, complete=True),
        check_domain(4, 16, complete=True),
        check_domain(8, 16, complete=False),
        check_domain(8, 64, complete=False),
    ]
    covers = [check_cover(8, 64), check_cover(16, 128)]
    controls = check_controls()
    directory = Path(__file__).resolve().parent
    package_hashes = {
        name: sha256((directory / name).read_bytes()).hexdigest()
        for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    }
    print(json.dumps(dict(status="PASS_COMPACT_TWO_TARGET_SYMBOLIC_CORE", domains=checks,
                          covers=covers, controls=controls, package_sha256=package_hashes),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
