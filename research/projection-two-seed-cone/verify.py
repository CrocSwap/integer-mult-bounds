"""Bounded exact corroboration; PROOF.md supplies the infinite tail."""

from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import sys

MAX_BLOCK = 64
BOUNDARY = Q(7, 3)
MODES = (Q(0), Q(-9, 4))
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
         "VERIFY.json", "verify.py")


def check(condition, message):
    if not condition:
        raise ValueError(message)


def block_contract(k):
    check(type(k) is int and 2 <= k <= MAX_BLOCK, "block outside 2..64")


def row_coefficients(k, r):
    block_contract(k)
    check(type(r) is int and 0 <= r <= k, "invalid row")
    first = 2**(k-r)-1 + 4**k-2**(k+r)
    second = 2*(2**k-2**(k-r)) + (2**r-1)*2**(k-1)
    third = (2**r-1)*(2**(r-1)-1)*2**(k-r) if r >= 2 else 0
    check(min(first, second, third) >= 0, "negative row coefficient")
    return first, second, third


def raw_profiles(limit):
    """Integer coefficient pairs for the complete seed (0,1,t)."""
    block_contract(limit)
    profile = [(0, 0), (1, 0), (0, 1)]
    result = {2: tuple(profile)}
    for k in range(3, limit+1):
        following = []
        for r in range(k+1):
            weights = row_coefficients(k, r)
            pair = tuple(sum(weights[i]*profile[r-i][j]
                             for i in range(3) if 0 <= r-i < k)
                         for j in range(2))
            following.append(pair)
        check(following[1][1] == 0 and following[1][0] > 0,
              "wrong normalization")
        profile = following
        result[k] = tuple(profile)
    return result


def operator_entries(r):
    check(type(r) is int and 1 <= r <= MAX_BLOCK, "invalid operator row")
    x = 2**r
    return (Q(3, 2)+Q(1, x)-x, Q(x, 2)+Q(3, 2)-Q(2, x),
            Q(x, 2)-Q(3, 2)+Q(1, x))


def eigenvectors(limit):
    block_contract(limit)
    vectors = [[Q(0)]*(limit+1) for _ in range(2)]
    vectors[0][1], vectors[1][2] = Q(1), Q(1)
    for j in range(2):
        for r in range(j+2, limit+1):
            diagonal, lower, lowest = operator_entries(r)
            vectors[j][r] = (lower*vectors[j][r-1] + lowest*vectors[j][r-2]) / (MODES[j]-diagonal)
    return vectors


def mode_tops(limit):
    """Separate scalar recurrence with the new block-two initial values."""
    block_contract(limit)
    check(limit >= 3, "two initial blocks required")
    modes = [{2: Q(4, 3), 3: Q(77, 51)}, {2: Q(1), 3: Q(14, 17)}]
    for m in range(4, limit+1):
        x = 2**m
        alpha = Q((x-1)*(x+4), (x-2)*(2*x+1))
        for values, h in zip(modes, MODES):
            beta = Q(x-1, 2*x+1)*(1+Q(2*x*h, (x-4)*(x+1)))
            values[m] = alpha*values[m-1] + beta*values[m-2]
    return modes


def top(profiles, m, t):
    block_contract(m)
    check(isinstance(t, Q) and t >= 0, "seed must be a nonnegative Fraction")
    constant, linear = profiles[m][-1]
    return (constant+t*linear)/profiles[m][1][0]


def compare_representations(profiles, modes):
    vectors = eigenvectors(MAX_BLOCK)
    products = [Q(1), Q(1)]
    entries = 0
    for m in range(2, MAX_BLOCK+1):
        if m > 2:
            d = (2**(m-1)-1)*(2**(m+1)+1)
            for j in range(2):
                value = (2**(m-j-1)-1)*(2**(m+j+1)+1)
                products[j] *= Q(value, d)
        denominator = profiles[m][1][0]
        for r, (constant, linear) in enumerate(profiles[m]):
            first, second = (products[j]*vectors[j][r] for j in range(2))
            check(Q(linear, denominator) == second, "wrong second mode")
            check(Q(constant, denominator) == first-Q(4, 3)*second, "wrong first mode")
            entries += 1
        for j in range(2):
            check(modes[j][m] == products[j]*vectors[j][m], "wrong scalar recurrence")
    return entries


def finite_tail_certificate(profiles, modes):
    finite = 0
    for t in (Q(0), BOUNDARY):
        for m in range(3, 18):
            difference = top(profiles, m, t)-top(profiles, m-1, t)
            tie = t == BOUNDARY and m == 3
            check(difference == 0 if tie else difference > 0, "boundary seed fails")
            finite += 1
    witnesses = []
    for m in (16, 17):
        scaled = [2**m*(values[m]-values[m-1]) for values in modes]
        norms = [max(abs(values[m]), abs(z)) for values, z in zip(modes, scaled)]
        check(max(norms) <= 2, "mode state norm exceeds two")
        margins = [scaled[0]+(t-Q(4, 3))*scaled[1] for t in (Q(0), BOUNDARY)]
        check(min(margins) > Q(1, 2), "scaled difference below one half")
        series = Q(8192, 3*2**m)
        error = Q(14, 3)*series/(1-series)
        check(0 < series < 1 and error < Q(1, 4), "tail budget fails")
        witnesses.append({"block": m, "state_norms": list(map(str, norms)),
                          "scaled_differences": list(map(str, margins)),
                          "tail_error_bound": str(error)})
    return finite, witnesses


def seed_checks(profiles):
    seeds = {Q(n, d) for n in range(36) for d in range(1, 13)}
    seeds.update((BOUNDARY-Q(1, 10**8), BOUNDARY, BOUNDARY+Q(1, 10**8), Q(10**8)))
    comparisons = 0
    for t in sorted(seeds):
        previous = t
        for m in range(3, MAX_BLOCK+1):
            current = top(profiles, m, t)
            if m == 3:
                check(current-previous == (7-3*t)/17, "wrong first difference")
            if m == 4:
                check(current-previous == (t+13)/187, "wrong second difference")
            if t <= BOUNDARY:
                tie = m == 3 and t == BOUNDARY
                check(current == previous if tie else current > previous, "false monotonicity")
            comparisons += 1
            previous = current
        if t > BOUNDARY:
            check(top(profiles, 3, t) < t and top(profiles, 4, t) > top(profiles, 3, t),
                  "missing nonmonotonicity witnesses")
    return len(seeds), comparisons


def reject(function, *arguments):
    try:
        function(*arguments)
    except ValueError:
        return 1
    raise ValueError("negative control accepted")


def controls(profiles, modes):
    count = sum(reject(raw_profiles, value) for value in (True, 1, 65, Q(3, 2)))
    count += sum(reject(top, profiles, 3, value) for value in (Q(-1), 1.0, True))
    cases = ((top(profiles, 3, Q(8, 3)) >= Q(8, 3), "larger threshold"),
             (top(profiles, 3, BOUNDARY) > BOUNDARY, "false strict boundary"),
             (top(profiles, 4, Q(0)) <= top(profiles, 3, Q(0)), "wrong direction"),
             (modes[0][3] == modes[1][3], "swapped modes"),
             (Q(14, 69) < Q(1, 8), "insufficient tail allowance"))
    return count + sum(reject(check, condition, message) for condition, message in cases)


def package_hashes():
    directory = Path(__file__).resolve().parent
    result = {}
    for name in FILES:
        path = directory/name
        check(path.is_file() and not path.is_symlink(), "missing regular package file")
        check(path.stat().st_size <= 2*1024*1024, "package file exceeds size cap")
        result[name] = sha256(path.read_bytes()).hexdigest()
    return result


def main():
    check(len(sys.argv) == 1, "this bounded verifier accepts no arguments")
    profiles, modes = raw_profiles(MAX_BLOCK), mode_tops(MAX_BLOCK)
    entries = compare_representations(profiles, modes)
    finite, witnesses = finite_tail_certificate(profiles, modes)
    seeds, comparisons = seed_checks(profiles)
    receipt = {"claim_type": "scoped proof with exact finite corroboration",
               "profile_entries": entries, "boundary_steps": finite,
               "tail_witnesses": witnesses, "seed_fixtures": seeds,
               "adjacent_comparisons": comparisons, "rejection_controls": controls(profiles, modes),
               "sha256": package_hashes()}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_PROJECTION_TWO_SEED_CONE")


if __name__ == "__main__":
    main()
