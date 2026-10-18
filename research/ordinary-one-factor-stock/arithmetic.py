"""Independent integer specification; verification code, never a tape backend."""
from math import prod


def depth(n, m, rank):
    levels = 0
    while n >= m:
        n = rank * (n // m)
        levels += 1
    return levels


def least_width(e, numerator, denominator):
    target = e ** numerator
    low, high = 1, e
    while low < high:
        mid = (low + high) // 2
        if mid ** denominator >= target:
            high = mid
        else:
            low = mid + 1
    return low


def plan(e, q, profile, compatibility, repeated=False):
    w = least_width(e, profile.numerator, profile.denominator)
    d = depth(e, profile.dimension, profile.child_rank)
    order = prod(q ** profile.dimension - q ** i for i in range(profile.dimension))
    b = profile.row_factor * order * q ** (profile.dimension ** 2 * (w - 1))
    stock = (compatibility * b) ** d if repeated else (compatibility * b ** d if d else 1)
    rows, k = 1, 0
    while rows < stock:
        rows *= q
        k += 1
    n, ell = divmod(e - k, w) if 2 * k < e else (0, 0)
    return dict(width=w, depth=d, stock=stock, rows=rows, borrowed=k,
                body=n, remainder=ell, fits=2 * k < e and n >= profile.dimension)


def guard_chain(rows, b, compatibility, levels):
    for _ in range(levels):
        rows, rem = divmod(rows, b)
        if rem or not rows or rows % compatibility:
            return False
    return rows > 0


def check_arithmetic():
    guards = padding = depth_checks = 0
    # Exhaustive declared finite contract domain, not a general proof by replay.
    for b in range(1, 9):
        for qfactor in range(1, 8):
            for d in range(5):
                s = qfactor * b ** d if d else 1
                for r in range(1, 3 * s + 2):
                    if guard_chain(r, b, qfactor, d) != (r % s == 0):
                        raise ValueError("exact guard/divisor equivalence")
                    guards += 1
                for genuine in range(s, s + 25):
                    padded = ((genuine + s - 1) // s) * s
                    if not genuine <= padded < 2 * genuine or padded % s:
                        raise ValueError("padding contract")
                    for child_d in range(d + 1):
                        child_s = qfactor * b ** child_d if child_d else 1
                        if padded % child_s:
                            raise ValueError("body-depth admission")
                    padding += 1
    for n in range(1, 4097):
        d = depth(n, 64, 42)
        if n >= 64:
            for rank in range(1, 43):
                if depth(rank * (n // 64), 64, 42) > d - 1:
                    raise ValueError("child-depth contraction")
                depth_checks += 1
    if guard_chain(36, 6, 2, 2) or not guard_chain(72, 6, 2, 2) or 72 % 144 == 0:
        raise ValueError("missing-Q and stronger-format boundary controls")
    return dict(guard_decisions=guards, padding_contracts=padding,
                selected_child_depths=depth_checks,
                missing_factor_control="36 passes first guard, fails second",
                stronger_format_control="72 satisfies guards, not divisor144")
