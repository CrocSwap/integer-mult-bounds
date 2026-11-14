# SPDX-License-Identifier: Apache-2.0
"""Dense exact integer replay of the complete normalized native map."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256

import numpy as np

from word import require

GRID = 1125 * 2**25
SAFE = 2**62 - 1


def spaces(frames):
    spans = []
    for basis in frames:
        span = {0}
        for v in basis:
            require(0 < v < 512 and v not in span, "Independent native binary basis")
            span |= {w ^ v for w in span}
        spans.append(span)
    return spans


def run(word, unit=GRID, mutation=None):
    n, m = word["public"], word["public"] + word["owned_fields"]
    frames = list(word["initial"]) + [None] * (m - n)
    span = spaces(word["frames"])
    values = np.zeros((m, n), dtype=np.int64)
    values[np.arange(n), np.arange(n)] = unit
    coeff_cache = {}
    content = unit
    maximum, peak_at = unit, None
    census, paid, copy_events = Counter(), Counter(), []
    labels = set()
    lives = peak = 0

    def observe(row, event, stage):
        nonlocal content, maximum, peak_at
        # 1,499 columns fit both component sums even if every entry is
        # 2**62-1: the high terms use at most 50 bits each. Recombine
        # after summing using Python integers.
        magnitudes = np.abs(row)
        high = int(np.sum(magnitudes >> 12, dtype=np.int64))
        low = int(np.sum(magnitudes & 4095, dtype=np.int64))
        norm = (high << 12) + low
        if norm > maximum:
            maximum, peak_at = norm, [event, stage]
        if content > 1:
            content = int(np.gcd.reduce(magnitudes, initial=content))

    def times_scalar(row, text, event):
        if text not in coeff_cache:
            q = Fraction(text)
            require(abs(q.numerator).bit_length() <= 24 and q.denominator.bit_length() <= 20,
                    f"Coefficient format at {event}")
            coeff_cache[text] = q.numerator, q.denominator
        a, b = coeff_cache[text]
        if b != 1:
            require(not np.any(row % b), f"Nonexact scaled product at {event}")
            row = row // b
        require(not a or int(np.max(np.abs(row))) <= SAFE // abs(a), f"Product range at {event}")
        return row * a

    for i, e in enumerate(word["program"]):
        op, r = e[:2]
        if mutation == "omit_exit" and i == 76298:
            require(e == ["MOVE", 133, 591, 127, False], "Wrong exit control location")
            continue
        if mutation == "omit_injection" and i == 42453:
            require(e == ["ADD", 1531, 1561, "1", 1031], "Wrong injection control location")
            continue
        census[op] += 1
        if op == "MOVE":
            a, b, owned = e[2:]
            require(frames[r] == a and owned == (r >= n), f"MOVE owner/source at {i}")
            require(span[a] < span[b] or (owned and span[b] < span[a]), f"Strict MOVE geometry at {i}")
            paid[abs(len(word["frames"][a]) - len(word["frames"][b]))] += 1
            frames[r] = b
        elif op == "INIT":
            require(r >= n and frames[r] is None and not np.any(values[r]), f"Clean INIT at {i}")
            frames[r] = e[2]
            labels.add(r)
            lives += 1
            peak = max(peak, sum(f is not None for f in frames[n:]))
        elif op == "CLEAR":
            require(r >= n and frames[r] == e[2], f"Owned CLEAR at {i}")
            values[r].fill(0)
            frames[r] = None
        elif op == "SCALE":
            require(frames[r] == e[-1], f"Scalar frame at {i}")
            values[r] = times_scalar(values[r], e[2], i)
            observe(values[r], i, "scaled")
        else:
            s = e[2]
            require(op in ("ADD", "COPY") and r != s and frames[r] == frames[s] == e[-1],
                    f"Scalar frame at {i}")
            if op == "COPY":
                if mutation == "dirty_copy":
                    require(np.any(values[s]), "COPY source is live for dirty control")
                    values[r] = values[s]
                require(not np.any(values[r]), f"Dirty COPY destination at {i}")
                copy_events.append(i)
            prod = times_scalar(values[s], e[3], i)
            observe(prod, i, "product")
            # Both summands lie in [-(2**62-1), 2**62-1].
            # Their unguarded sum therefore fits the signed machine word.
            row = values[r] + prod
            require(int(np.max(np.abs(row))) <= SAFE, f"Stored range at {i}")
            values[r] = row
            observe(row, i, "stored")
    require(frames == word["final"] + [None] * (m - n), "Complete final frames")
    require(not np.any(values[n:]), "Every retired owned row is zero")

    h = word["hosted"]
    direct = set(h["Dports"])
    targets = {r: {r: unit} for r in range(n)}
    for i, x in enumerate(word["live"]):
        y = x + 112
        if i in direct:
            targets[y][x] = unit
        else:
            targets[x][y] = -unit
            targets[y] = {x: unit//2, y: unit//2}
    for x, y in zip(h["X2"], h["Y2"]):
        targets[x][y] = -unit
    for r, row in enumerate(values[:n]):
        got = {int(i): int(row[i]) for i in np.flatnonzero(row)}
        require(got == targets[r], f"Wrong complete endpoint at public role {r}")
    return dict(public=n, owned=len(labels), lifetimes=lives, peak_owned=peak, exact_input_output_coefficients=n*n,
                allocated_input_output_coefficients=m*n, strict_COPY_events=copy_events, opcodes=dict(census),
                paid=dict(paid), complete_endpoint_sha256=sha256(values.astype("<i8").tobytes()).hexdigest(),
                required_grid=unit//content, absolute_integer_row_mass=maximum, mass_witness=peak_at,
                scaled_row_mass=str(Fraction(maximum,2**25)))



def check(word, receipt):
    result = run(word)
    require(result["required_grid"] == GRID
            and result["scaled_row_mass"] == receipt["derived_grid"]["scaled_maximum_mass"]
            and result["mass_witness"] == receipt["derived_grid"]["mass_witness"],
            "Independent grid and mass equality")
    require((result["public"], result["owned"], result["lifetimes"], result["peak_owned"])
            == (1499, 63, 66, 48), "Independent liveness totals")
    tests = {
        "omit_exit": (GRID, "Scalar frame"),
        "omit_injection": (GRID, "Wrong complete endpoint"),
        "dirty_copy": (GRID, "Dirty COPY destination"),
        "odd_grid_375": (375 * 2**25, "Nonexact scaled product"),
        "fractional_grid_24": (1125 * 2**24, "Nonexact scaled product"),
    }
    controls = {}
    for tag, (unit, expected) in tests.items():
        try:
            run(word, unit, tag)
        except ValueError as exc:
            require(str(exc).startswith(expected), f"Unexpected {tag} control: {exc}")
            controls[tag] = str(exc)
        else:
            raise ValueError(f"Surviving native control: {tag}")
    return {"result": result, "controls": controls}
