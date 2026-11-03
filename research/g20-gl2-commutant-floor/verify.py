#!/usr/bin/env python3
"""Legal GL(2) commutant of the PR5840 G20 boundary cannot beat 38 ADDs per side.

The proof is the partition dynamic program below, not a 6^16 circuit search.
Python 3.12 and the standard library are sufficient.
"""
from hashlib import sha256
import json
from itertools import product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GL2 = tuple((p, q, r, s) for p, q, r, s in product((0, 1), repeat=4) if (p & s) ^ (q & r))
CHAIN = set(range(16)) | {30, 31}
EXCHANGE = set(range(16, 30))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha256_file(path):
    return sha256(path.read_bytes()).hexdigest()


def apply_word(word, n):
    rows = [1 << i for i in range(n)]
    for dest, source in word:
        require(0 <= dest < n and 0 <= source < n and dest != source, "invalid gate")
        rows[dest] ^= rows[source]
    return rows


def expand_program(program, n):
    word = []
    for op, dest, source in program:
        require(op in ("ADD", "SWAP"), "unknown opcode")
        if op == "ADD":
            word.append((dest, source))
        else:
            word.extend(((dest, source), (source, dest), (dest, source)))
    require(all(0 <= a < n and 0 <= b < n for a, b in word), "gate leaves the boundary")
    return word


def support_components(rows):
    """Undirected support components. An edge exists when either matrix entry is 1."""
    n = len(rows)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    zeros = 0
    for i, row in enumerate(rows):
        if (row >> i) & 1 == 0:
            zeros += 1
        bit = row
        j = 0
        while bit:
            if bit & 1 and j != i:
                union(i, j)
            bit >>= 1
            j += 1
    return len({find(i) for i in range(n)}), zeros


def link_diagonal_bound(rows):
    """Bu-Fan-Joo counting bound: n - v + z, including cross-component gates."""
    n = len(rows)
    components, zeros = support_components(rows)
    return n - components + zeros


def signature(parent):
    labels = parent[:]

    def find(x):
        while labels[x] != x:
            labels[x] = labels[labels[x]]
            x = labels[x]
        return x

    roots = {}
    out = []
    for i in range(len(parent)):
        root = find(i)
        if root not in roots:
            roots[root] = len(roots)
        out.append(roots[root])
    return tuple(out)


def relabel(sig):
    parent = list(range(len(sig)))
    seen = {}
    for vertex, label in enumerate(sig):
        if label in seen:
            parent[vertex] = seen[label]
        else:
            seen[label] = vertex
    return parent


def minimum_bound(original, local_pairs, mode):
    """Minimum link/diagonal bound over GL(2) on each listed coordinate pair.

    mode "columns" is right multiplication by the block-diagonal basis.
    mode "rows" is left multiplication by its inverse. Pair contributions
    commute, so the dynamic program stores only the reachable support
    partition and the minimum number of zero diagonal entries creating it.
    """
    n = len(original)
    require(mode in ("columns", "rows"), "unknown mixing mode")

    def contribution(pair_index, factor):
        left, right = local_pairs[pair_index]
        p, q, r, s = factor
        edges = []
        if mode == "columns":
            new_columns = [0, 0]
            for row in range(n):
                a = (original[row] >> left) & 1
                b = (original[row] >> right) & 1
                bits = ((p & a) ^ (r & b), (q & a) ^ (s & b))
                if bits[0] and row != left:
                    edges.append((row, left))
                if bits[1] and row != right:
                    edges.append((row, right))
                if row == left:
                    new_columns[0] = bits[0]
                elif row == right:
                    new_columns[1] = bits[1]
            zeros = (new_columns[0] == 0) + (new_columns[1] == 0)
            return edges, zeros
        # inv([[p, q], [r, s]]) = [[s, q], [r, p]] over F2 when the determinant is 1.
        new_left = (original[left] if s else 0) ^ (original[right] if q else 0)
        new_right = (original[left] if r else 0) ^ (original[right] if p else 0)
        for source, row, skip in ((left, new_left, left), (right, new_right, right)):
            bit = row & ~(1 << skip)
            while bit:
                other = (bit & -bit).bit_length() - 1
                edges.append((source, other))
                bit &= bit - 1
        zeros = (((new_left >> left) & 1) == 0) + (((new_right >> right) & 1) == 0)
        return edges, zeros

    states = {signature(list(range(n))): 0}
    peak = 1
    for pair_index in range(len(local_pairs)):
        nxt = {}
        for sig, zeros in states.items():
            parent = relabel(sig)
            for factor in GL2:
                edges, added = contribution(pair_index, factor)
                merged = parent[:]

                def find(x, labels=merged):
                    while labels[x] != x:
                        labels[x] = labels[labels[x]]
                        x = labels[x]
                    return x

                for a, b in edges:
                    ra, rb = find(a), find(b)
                    if ra != rb:
                        merged[rb] = ra
                key = signature(merged)
                total = zeros + added
                if total < nxt.get(key, 10**9):
                    nxt[key] = total
        states = nxt
        peak = max(peak, len(states))
    best = min(n - len(set(sig)) + zeros for sig, zeros in states.items())
    return best, len(states), peak


def submatrix(rows, wires):
    index = {wire: pos for pos, wire in enumerate(wires)}
    out = []
    for wire in wires:
        packed = 0
        bits = rows[wire]
        for other in wires:
            if (bits >> other) & 1:
                packed |= 1 << index[other]
        out.append(packed)
    return out


def polynomial_diagonal(monomials, factor, pair):
    """Diagonal labels of S^{-1} D S for a 2-by-2 factor on one pair."""
    p, q, r, s = factor
    left, right = pair
    # Columns of S are (p, r) and (q, s) in the (left, right) coordinates.
    # D scales each old basis vector by its monomial. Because those monomials
    # are scalars in a polynomial ring, a column supported on both wires is
    # legal only when the two monomials agree; otherwise the output is not a
    # scalar multiple of one new basis vector.
    columns = ((p, r), (q, s))
    diagonal = []
    for col in columns:
        support = []
        if col[0]:
            support.append(monomials[left])
        if col[1]:
            support.append(monomials[right])
        require(support, "singular column")
        require(len(set(support)) == 1, "column mixes unequal target monomials")
        diagonal.append(support[0])
    return diagonal


def main():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    live = [item for item in manifest["files"] if item["usage"] == "input"]
    require(len(live) == 1, "expected one live controller input")
    controller_path = ROOT / live[0]["path"]
    require(sha256_file(controller_path) == live[0]["sha256"], "controller hash mismatch")
    controller = json.loads(controller_path.read_text(encoding="utf-8"))
    boundary = controller["boundaries"]
    monomials = boundary["diagonal_monomials"]
    require(monomials == controller["diagonal"], "diagonal monomials disagree")
    require(len(monomials) == 32, "boundary rank is not 32")
    pairs = [(2 * k, 2 * k + 1) for k in range(16)]
    for left, right in pairs:
        require(monomials[left] == monomials[right], "equal-target pair is not equal")
        require(left in CHAIN and right in CHAIN or left in EXCHANGE and right in EXCHANGE,
                "coordinate pair crosses the chain/exchange cut")
    require(len({monomials[2 * k] for k in range(16)}) == 16, "distinct pairs share a monomial")
    # Every GL(2) block on an equal pair preserves both labels. A shear across
    # unequal monomials is not diagonal, and a transposition of those wires
    # exchanges the labels.
    for factor in GL2:
        labels = polynomial_diagonal(monomials, factor, pairs[0])
        require(labels == [monomials[0], monomials[0]], "equal pair was not preserved")
    require(monomials[0] != monomials[2], "control pair is not unequal")
    try:
        polynomial_diagonal(monomials, (1, 1, 0, 1), (0, 2))
    except ValueError as exc:
        require("unequal target monomials" in str(exc), "cross-monomial shear was accepted")
    else:
        raise ValueError("cross-monomial shear was accepted")
    swapped = polynomial_diagonal(monomials, (0, 1, 1, 0), (0, 2))
    require(swapped == [monomials[2], monomials[0]], "unequal transposition did not move labels")

    for name in ("left_rows", "right_rows"):
        rows = boundary[name]
        require(len(rows) == 32 and all(isinstance(row, int) for row in rows), "rows are not 32 masks")
        for i, row in enumerate(rows):
            for j in range(32):
                if (row >> j) & 1:
                    require((i in CHAIN) == (j in CHAIN), "source matrix already crosses the cut")

    chain_wires = [i for i in range(32) if i in CHAIN]
    exchange_wires = [i for i in range(32) if i in EXCHANGE]
    chain_pairs = []
    exchange_pairs = []
    for left, right in pairs:
        if left in CHAIN:
            chain_pairs.append((chain_wires.index(left), chain_wires.index(right)))
        else:
            exchange_pairs.append((exchange_wires.index(left), exchange_wires.index(right)))
    require(len(chain_pairs) == 9 and len(exchange_pairs) == 7, "pair split changed")

    floors = {}
    peaks = {}
    for side in ("left", "right"):
        rows = boundary[side + "_rows"]
        chain = submatrix(rows, chain_wires)
        exchange = submatrix(rows, exchange_wires)
        chain_mode = "rows" if side == "left" else "columns"
        chain_floor, chain_states, chain_peak = minimum_bound(chain, chain_pairs, chain_mode)
        exchange_floor, exchange_states, exchange_peak = minimum_bound(exchange, exchange_pairs, chain_mode)
        require(chain_floor == 20, side + " chain floor " + str(chain_floor))
        require(exchange_floor == 18, side + " exchange floor " + str(exchange_floor))
        floors[side] = (chain_floor, exchange_floor, chain_states, exchange_states)
        peaks[side] = (chain_peak, exchange_peak)
        require(link_diagonal_bound(chain) == 20, side + " source chain is not 20")
        require(link_diagonal_bound(exchange) == 18, side + " source exchange is not 18")
        require(link_diagonal_bound(rows) == 38, side + " source boundary is not 38")

    # Deterministic samples: direct bounds meet the split floors and add.
    seed = 20261103
    for sample in range(48):
        factors = []
        for _ in range(16):
            seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
            factors.append(GL2[seed % 6])
        for side in ("left", "right"):
            rows = boundary[side + "_rows"][:]
            for (left, right), factor in zip(pairs, factors):
                p, q, r, s = factor
                if side == "right":
                    mask = ~((1 << left) | (1 << right))
                    updated = []
                    for row in rows:
                        a = (row >> left) & 1
                        b = (row >> right) & 1
                        packed = row & mask
                        if (p & a) ^ (r & b):
                            packed |= 1 << left
                        if (q & a) ^ (s & b):
                            packed |= 1 << right
                        updated.append(packed)
                    rows = updated
                else:
                    inverse_left = (rows[left] if s else 0) ^ (rows[right] if q else 0)
                    inverse_right = (rows[left] if r else 0) ^ (rows[right] if p else 0)
                    rows = rows[:]
                    rows[left] = inverse_left
                    rows[right] = inverse_right
            chain_bound = link_diagonal_bound(submatrix(rows, chain_wires))
            exchange_bound = link_diagonal_bound(submatrix(rows, exchange_wires))
            full_bound = link_diagonal_bound(rows)
            require(chain_bound >= 20 and exchange_bound >= 18, "sample fell below a block floor")
            require(full_bound == chain_bound + exchange_bound, "sample crossed the cut")
            require(full_bound >= 38, "sample fell below 38")

    words = {}
    for side in ("left", "right"):
        word = expand_program(boundary[side + "_program"], 32)
        rows = apply_word(word, 32)
        require(rows == boundary[side + "_rows"], side + " program does not match its matrix")
        require(len(word) == 38, side + " witness is not 38 ADDs")
        require(link_diagonal_bound(rows) == 38, side + " witness misses the bound")
        words[side] = word
    require(apply_word(words["left"] + words["right"], 32) == [1 << i for i in range(32)],
            "the two boundaries are not inverses")
    require(link_diagonal_bound([1 << i for i in range(32)]) == 0, "identity control")
    require(link_diagonal_bound([1 << 1, 1 << 0]) == 3, "swap control")
    require(link_diagonal_bound([1 | 2, 1 << 1]) == 1, "single ADD control")

    print(
        "PASS_G20_GL2_COMMUTANT_FLOOR "
        "legal=GL2^16 chain=20 exchange=18 side=38 witness=38 "
        "states=" + str(floors["left"][2]) + "+" + str(floors["left"][3]) + "/"
        + str(floors["right"][2]) + "+" + str(floors["right"][3]) + " "
        "peak=" + str(peaks["left"]) + "/" + str(peaks["right"]) + " "
        "samples=48 no_new_kappa"
    )


if __name__ == "__main__":
    main()
