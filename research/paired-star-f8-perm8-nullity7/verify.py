#!/usr/bin/env python3
"""The next distinct nullity-7 class of two thin maps, extended to F8.

The rank bound is the case analysis in PROOF.md. This file checks that
analysis on the displayed shape, derives the shape from the paired-star word,
and compares an independent Gaussian elimination with search.c on every F8
point. Failures are raised, so python -O still fails closed.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
BINARY = Path("/tmp/paired-star-f8-perm8-nullity7")
MASK64 = (1 << 64) - 1
FNV = 1469598103934665603
FNV_PRIME = 1099511628211

# x^3 + x + 1. Element bits are 1, x, x^2. Addition is XOR.
MUL = [[0] * 8 for _ in range(8)]
for _a in range(8):
    for _b in range(8):
        prod = 0
        x = _a
        y = _b
        while y:
            if y & 1:
                prod ^= x
            x <<= 1
            if x & 8:
                x ^= 0xB
            y >>= 1
        MUL[_a][_b] = prod
INV = [0] * 8
for _a in range(1, 8):
    INV[_a] = next(_b for _b in range(1, 8) if MUL[_a][_b] == 1)


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def rank_matrix(buf):
    a = buf[:]
    rank = 0
    for col in range(8):
        pivot = None
        for i in range(rank, 8):
            if a[i * 8 + col]:
                pivot = i
                break
        if pivot is None:
            continue
        if pivot != rank:
            rs = rank * 8
            ps = pivot * 8
            for j in range(8):
                a[rs + j], a[ps + j] = a[ps + j], a[rs + j]
        inv = INV[a[rank * 8 + col]]
        rs = rank * 8
        for j in range(8):
            a[rs + j] = MUL[inv][a[rs + j]]
        for i in range(8):
            if i == rank:
                continue
            factor = a[i * 8 + col]
            if not factor:
                continue
            base = i * 8
            rowmul = MUL[factor]
            for j in range(8):
                a[base + j] ^= rowmul[a[rs + j]]
        rank += 1
    return rank


def rank_small(rows):
    a = [row[:] for row in rows]
    n = len(a)
    cols = len(a[0])
    rank = 0
    for col in range(cols):
        pivot = next((i for i in range(rank, n) if a[i][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        inv = INV[a[rank][col]]
        a[rank] = [MUL[inv][value] for value in a[rank]]
        for i in range(n):
            if i != rank and a[i][col]:
                factor = a[i][col]
                a[i] = [value ^ MUL[factor][a[rank][j]] for j, value in enumerate(a[i])]
        rank += 1
    return rank


def matrices(coeffs):
    c0, c1, c2, c3, c4, c5, c6 = coeffs
    zg = [
        c6, 0, 1, 0, 1, 0, 0, 0,
        0, c6, 0, 1, 0, 1, 0, 0,
        1, 0, c0, 0, 0, c1, 0, 0,
        0, 1, 0, c2, 0, 0, 0, 0,
        1, 0, 0, 0, c3, 0, 0, 0,
        0, 1, c4, 0, 0, c5, 0, 0,
        0, 0, 0, 0, 0, 0, c6, 0,
        0, 0, 0, 0, 0, 0, 0, c6,
    ]
    zh = [
        c6, 0, 0, 0, 0, 0, 1, 0,
        0, c6, 0, 0, 0, 0, 0, 1,
        0, 0, c0, 0, 0, c1, 0, 0,
        0, 0, 0, c2, 0, 0, 0, 0,
        0, 0, 0, 0, c3, 0, 0, 0,
        0, 0, c4, 0, 0, c5, 0, 0,
        1, 0, 0, 0, 0, 0, c6, 0,
        0, 1, 0, 0, 0, 0, 0, c6,
    ]
    return zg, zh


def rank_m(c1, c2, c3, c4):
    return rank_small([[c1, c2], [c3, c4]])


def rank_zh_blocks(coeffs):
    c0, c1, c2, c3, c4, c5, c6 = coeffs
    corner = [
        [c6, 0, 1, 0],
        [0, c6, 0, 1],
        [1, 0, c6, 0],
        [0, 1, 0, c6],
    ]
    return rank_small(corner) + rank_m(c0, c1, c4, c5) + (c2 != 0) + (c3 != 0)


def enumerate_shape():
    checksum = FNV
    hist = [0] * 17
    minimum = 99
    below = 0
    equals = []
    limit = 8 ** 7
    for code in range(limit):
        coeffs = [0] * 7
        rest = code
        for i in range(7):
            coeffs[i] = rest % 8
            rest //= 8
        zg, zh = matrices(coeffs)
        rank_g = rank_matrix(zg)
        rank_h = rank_matrix(zh)
        total = rank_g + rank_h
        hist[total] += 1
        if total < minimum:
            minimum = total
        if total < 8:
            below += 1
        if total == 8 and len(equals) < 4:
            equals.append((tuple(coeffs), rank_g, rank_h))
        require(rank_h == rank_zh_blocks(coeffs), "Zh block formula at " + str(coeffs))
        checksum = ((checksum ^ (total + 17 * rank_g + 1)) * FNV_PRIME) & MASK64
    return {
        "count": limit,
        "min": minimum,
        "below": below,
        "checksum": checksum,
        "hist": hist,
        "equals": equals,
    }


def check_field_and_controls():
    require(MUL[2][2] == 4 and MUL[2][4] == 3, "x^3 = x+1")
    for value in range(1, 8):
        require(MUL[value][INV[value]] == 1, "inverse")
        require(all(MUL[value][other] != 0 for other in range(1, 8)), "field")
    for c6 in range(8):
        corner = rank_small([
            [c6, 0, 1, 0],
            [0, c6, 0, 1],
            [1, 0, c6, 0],
            [0, 1, 0, c6],
        ])
        require(corner == (2 if c6 == 1 else 4), "corner rank")
    for c0 in range(8):
        for c2 in range(8):
            minor = [
                [0, 0, 1, 0],
                [0, 0, 0, 1],
                [1, 0, c0, 0],
                [0, 1, 0, c2],
            ]
            minor[0], minor[2] = minor[2], minor[0]
            minor[1], minor[3] = minor[3], minor[1]
            require(minor == [
                [1, 0, c0, 0],
                [0, 1, 0, c2],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ], "minor shape")
            require(rank_small(minor) == 4, "c6=0 minor")
    zero = [0, 0, 0, 0, 0, 0, 0]
    zg, zh = matrices(zero)
    require(rank_matrix(zg) == 4 and rank_matrix(zh) == 4, "zero point")
    one = [0, 0, 0, 0, 0, 0, 1]
    zg, zh_one = matrices(one)
    require(rank_matrix(zg) == 6 and rank_matrix(zh_one) == 2, "c6=1 point")
    broken = [0] * 64
    _zg, zh_zero = matrices(zero)
    require(rank_matrix(broken) + rank_matrix(zh_zero) == 4, "deleted ones are load-bearing")


def mono_tables():
    mono = [[0] * 27 for _ in range(27)]

    def index(e0, e1, e2):
        return e0 + 3 * e1 + 9 * e2

    for i in range(27):
        e0, e1, e2 = i % 3, (i // 3) % 3, i // 9
        for j in range(27):
            f0, f1, f2 = j % 3, (j // 3) % 3, j // 9
            g0, g1, g2 = e0 + f0, e1 + f1, e2 + f2
            mono[i][j] = 255 if g0 > 2 or g1 > 2 or g2 > 2 else index(g0, g1, g2)
    return mono


MONO = mono_tables()
OVERFLOW = {"n": 0}


def pmul(left, right):
    out = 0
    while left:
        bit = left & -left
        i = bit.bit_length() - 1
        left ^= bit
        rest = right
        while rest:
            bit_b = rest & -rest
            j = bit_b.bit_length() - 1
            rest ^= bit_b
            mixed = MONO[i][j]
            if mixed == 255:
                OVERFLOW["n"] += 1
            else:
                out ^= 1 << mixed
    return out


def mmul(left, right):
    out = [[0] * 8 for _ in range(8)]
    for i in range(8):
        row = left[i]
        for k in range(8):
            if not row[k]:
                continue
            factor = row[k]
            col = right[k]
            for j in range(8):
                if col[j]:
                    out[i][j] ^= pmul(factor, col[j])
    return out


def madd(left, right):
    return [[left[i][j] ^ right[i][j] for j in range(8)] for i in range(8)]


def eye():
    return [[1 if i == j else 0 for j in range(8)] for i in range(8)]


def mul2(left, right):
    out = 0
    for i in range(2):
        for j in range(2):
            bit = (((left >> (2 * i)) & 1) & ((right >> j) & 1)) ^ (
                ((left >> (2 * i + 1)) & 1) & ((right >> (2 + j)) & 1)
            )
            out |= bit << (2 * i + j)
    return out


def rank2(bits):
    rows = [bits & 3, (bits >> 2) & 3]
    rank = 0
    for col in range(2):
        mask = 1 << col
        pivot = next((i for i in range(rank, 2) if rows[i] & mask), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        if rows[rank ^ 1] & mask:
            rows[rank ^ 1] ^= rows[rank]
        rank += 1
    return rank


def block_rows(a_bits, b_bits):
    mixed = a_bits ^ b_bits
    blocks = ((mixed, b_bits), (b_bits, mixed))
    rows = []
    for half in range(2):
        for r in range(2):
            mask = 0
            for bc in range(2):
                block = blocks[half][bc]
                for c in range(2):
                    if (block >> (2 * r + c)) & 1:
                        mask |= 1 << (2 * bc + c)
            rows.append(mask)
    return rows


def mul4(left, right):
    out = []
    for row in left:
        value = 0
        rest = row
        while rest:
            bit = rest & -rest
            value ^= right[bit.bit_length() - 1]
            rest ^= bit
        out.append(value)
    return out


def embed_proj(cc, cl, lc, ll, leaf):
    rows = [0] * 8
    for r in range(2):
        for c in range(2):
            if (cc >> (2 * r + c)) & 1:
                rows[r] |= 1 << c
            if (cl >> (2 * r + c)) & 1:
                rows[r] |= 1 << (2 * leaf + c)
            if (lc >> (2 * r + c)) & 1:
                rows[2 * leaf + r] |= 1 << c
            if (ll >> (2 * r + c)) & 1:
                rows[2 * leaf + r] |= 1 << (2 * leaf + c)
    return rows


def build_resolutions():
    found = []
    seen = []
    for bits_a in range(16):
        if mul2(bits_a, bits_a) != bits_a or rank2(bits_a) != 1:
            continue
        complement = bits_a ^ 0x9
        for bits_b in range(16):
            first = block_rows(bits_a, bits_b)
            second = block_rows(complement, bits_b)
            if mul4(first, first) != first or mul4(second, second) != second:
                continue
            if mul4(first, second) != [0, 0, 0, 0] or mul4(second, first) != [0, 0, 0, 0]:
                continue
            k1 = 0
            k2 = 0
            for i in range(4):
                k1 |= first[i] << (4 * i)
                k2 |= second[i] << (4 * i)
            lo, hi = (k1, k2) if k1 < k2 else (k2, k1)
            if (lo, hi) in seen:
                continue
            seen.append((lo, hi))
            found.append((bits_a, bits_b, complement))
    return found


def pure_from_proj(proj, stage):
    out = eye()
    shift = 1 if stage == 0 else 3 if stage == 1 else 9
    for i in range(8):
        row = proj[i]
        while row:
            bit = row & -row
            col = bit.bit_length() - 1
            out[i][col] ^= 1
            out[i][col] ^= 1 << shift
            row ^= bit
    return out


def scale_read(readm, stage):
    out = [[0] * 8 for _ in range(8)]
    shift = 1 if stage == 0 else 3 if stage == 1 else 9
    for i in range(8):
        row = readm[i]
        while row:
            bit = row & -row
            col = bit.bit_length() - 1
            out[i][col] = 1 << shift
            row ^= bit
    return out


def support_e(stage):
    proj = [0] * 8
    proj[0] = 1
    proj[1] = 2
    leaf = stage + 1
    proj[2 * leaf] = 1 << (2 * leaf)
    proj[2 * leaf + 1] = 1 << (2 * leaf + 1)
    return proj


def build_target():
    target = eye()
    for stage in range(3):
        target = mmul(pure_from_proj(support_e(stage), stage), target)
    return target


def heap_perms():
    a = [0, 1, 2, 3, 4, 5]
    c = [0] * 6
    perms = [a[:]]
    i = 0
    while i < 6:
        if c[i] < i:
            j = c[i] if (i & 1) else 0
            a[j], a[i] = a[i], a[j]
            perms.append(a[:])
            c[i] += 1
            i = 0
        else:
            c[i] = 0
            i += 1
    require(len(perms) == 720, "permutation count")
    return perms


def eq_add(eq, left, right):
    for a in range(8):
        for b in range(8):
            u = a * 8 + b
            bit = 1 << u
            for i in range(8):
                if not left[i][a]:
                    continue
                for j in range(8):
                    if not right[b][j]:
                        continue
                    poly = pmul(left[i][a], right[b][j])
                    e = i * 8 + j
                    while poly:
                        mon = poly & -poly
                        m = mon.bit_length() - 1
                        eq[m][e] ^= bit
                        poly ^= mon


def basis_bit(lo, hi, var):
    if var < 64:
        return (lo >> var) & 1
    return (hi >> (var - 64)) & 1


def basis_insert(basis, lo, hi, rhs):
    if basis["bad"]:
        return
    for q in range(basis["np"]):
        var = basis["pvar"][q]
        if basis_bit(lo, hi, var):
            lo ^= basis["lo"][q]
            hi ^= basis["hi"][q]
            rhs ^= basis["rhs"][q]
    if lo == 0 and hi == 0:
        if rhs:
            basis["bad"] = 1
        return
    var = (lo & -lo).bit_length() - 1 if lo else 64 + (hi & -hi).bit_length() - 1
    for q in range(basis["np"]):
        if basis_bit(basis["lo"][q], basis["hi"][q], var):
            basis["lo"][q] ^= lo
            basis["hi"][q] ^= hi
            basis["rhs"][q] ^= rhs
    basis["lo"].append(lo)
    basis["hi"].append(hi)
    basis["rhs"].append(rhs)
    basis["pvar"].append(var)
    basis["np"] += 1


def solve_pair(eq_g, eq_h, defect):
    basis = {"lo": [], "hi": [], "rhs": [], "pvar": [], "np": 0, "bad": 0}
    for m in range(27):
        for e in range(64):
            lo = eq_g[m][e]
            hi = eq_h[m][e]
            rhs = (defect[e >> 3][e & 7] >> m) & 1
            if not lo and not hi and not rhs:
                continue
            basis_insert(basis, lo, hi, rhs)
            if basis["bad"]:
                return None
    return basis


def unpack(basis):
    zg = [0] * 8
    zh = [0] * 8
    for p in range(basis["np"]):
        if not basis["rhs"][p]:
            continue
        var = basis["pvar"][p]
        if var < 64:
            zg[var >> 3] |= 1 << (var & 7)
        else:
            zh[(var - 64) >> 3] |= 1 << ((var - 64) & 7)
    return zg, zh


def fill_class(basis):
    used = [0] * 128
    for var in basis["pvar"]:
        used[var] = 1
    free = [v for v in range(128) if not used[v]]
    zg, zh = unpack(basis)
    part = [0] * 128
    dep = [0] * 128
    for e in range(64):
        part[e] = (zg[e >> 3] >> (e & 7)) & 1
        part[64 + e] = (zh[e >> 3] >> (e & 7)) & 1
    for t, var in enumerate(free):
        dep[var] |= 1 << t
        for p in range(basis["np"]):
            if basis_bit(basis["lo"][p], basis["hi"][p], var):
                dep[basis["pvar"][p]] |= 1 << t
    return zg, zh, part, dep, free


def shape_var(row, col):
    if (row, col) in ((0, 0), (1, 1), (6, 6), (7, 7)):
        return 6
    return {(2, 2): 0, (2, 5): 1, (3, 3): 2, (4, 4): 3, (5, 2): 4, (5, 5): 5}.get((row, col), -1)


def settled_var(row, col):
    if (row, col) in ((0, 0), (1, 1), (6, 6), (7, 7)):
        return 6
    return {(2, 2): 0, (3, 3): 1, (3, 4): 2, (4, 3): 3, (4, 4): 4, (5, 5): 5}.get((row, col), -1)


def shape_const_g(row, col):
    return (row, col) in {(0, 2), (0, 4), (1, 3), (1, 5), (2, 0), (3, 1), (4, 0), (5, 1)}


def shape_const_h(row, col):
    return (row, col) in {(0, 6), (1, 7), (6, 0), (7, 1)}


def matches_var(part, dep, var_at):
    for row in range(8):
        for col in range(8):
            e = row * 8 + col
            var = var_at(row, col)
            expect = 0 if var < 0 else 1 << var
            if dep[e] != expect or dep[64 + e] != expect:
                return False
            if part[e] != int(shape_const_g(row, col)):
                return False
            if part[64 + e] != int(shape_const_h(row, col)):
                return False
    return True


def matches_shape(part, dep):
    return matches_var(part, dep, shape_var)


def matches_settled(part, dep):
    return matches_var(part, dep, settled_var)


def make_bank(resolutions):
    bank = []
    for bits_a, bits_b, complement in resolutions:
        calls = []
        for stage in range(3):
            for half in range(2):
                leaf = stage + 1
                matrix_a = complement if half else bits_a
                mixed = matrix_a ^ bits_b
                proj = embed_proj(mixed, bits_b, bits_b, mixed, leaf)
                readm = embed_proj(matrix_a, matrix_a, matrix_a, matrix_a, leaf)
                calls.append((proj, readm, stage))
        bank.append(calls)
    return bank


def derive_class():
    resolutions = build_resolutions()
    require(len(resolutions) == 12, "resolution count")
    require(resolutions[0][0] == 1 and resolutions[0][1] == 0, "resolution 0")
    require(resolutions[3][0] == 1 and resolutions[3][1] == 6, "resolution 3")
    bank = make_bank(resolutions)
    perms = heap_perms()
    require(perms[4] == [1, 2, 0, 3, 4, 5], "permutation 4")
    require(perms[5] == [2, 1, 0, 3, 4, 5], "permutation 5")
    require(perms[8] == [0, 3, 1, 2, 4, 5], "permutation 8")
    target = build_target()
    diagonal = next(i for i, res in enumerate(resolutions) if res[1] == 0)
    thin0 = [0] * 8
    thin1 = [0] * 8
    for leaf in (1, 2):
        for bit in range(2):
            thin0[bit] |= 1 << (2 * leaf + bit)
            thin0[2 * leaf + bit] |= 1 << bit
    for bit in range(2):
        thin1[bit] |= 1 << (6 + bit)
        thin1[6 + bit] |= 1 << bit
    word_p = eye()
    word_e = [[0] * 8 for _ in range(8)]
    chrono = [(0, 0), (0, 1), None, (1, 0), (1, 1), (2, 0), (2, 1), "second"]
    for item in chrono:
        if item is None or item == "second":
            factor_p = eye()
            thin = thin0 if item is None else thin1
            factor_e = [[0] * 8 for _ in range(8)]
            for i in range(8):
                for j in range(8):
                    if thin[i] & (1 << j):
                        factor_e[i][j] = 1
        else:
            stage, half = item
            proj, readm, _stage = bank[diagonal][stage * 2 + half]
            factor_p = pure_from_proj(proj, stage)
            factor_e = scale_read(readm, stage)
        next_p = mmul(factor_p, word_p)
        next_e = madd(mmul(factor_p, word_e), mmul(factor_e, word_p))
        word_p, word_e = next_p, next_e
    require(word_p == target and word_e == target, "Python control identity")
    screened = 0
    settled = None
    duplicate = False
    for c0 in range(12):
        for c1 in range(12):
            for c2 in range(12):
                for perm in range(720):
                    screened += 1
                    hit = solve_word_pure(bank, perms, target, c0, c1, c2, perm)
                    if hit is None:
                        continue
                    for g0 in range(7):
                        for g1 in range(g0 + 1, 7):
                            basis = solve_loaded(hit, g0, g1)
                            if basis is None:
                                continue
                            nullity = 128 - basis["np"]
                            if nullity < 7:
                                raise SystemExit("FAIL: nullity below 7")
                            if nullity != 7:
                                continue
                            _zg, _zh, part, dep, free = fill_class(basis)
                            key = (tuple(part), tuple(dep))
                            word = (c0, c1, c2, perm, g0, g1)
                            if settled is None:
                                require(word == (0, 0, 3, 4, 2, 5), "settled class moved")
                                require(matches_settled(part, dep), "settled shape")
                                require(not matches_shape(part, dep), "shapes collided")
                                settled = key
                                continue
                            if key == settled:
                                require(word == (0, 0, 3, 5, 2, 5) and not duplicate, "duplicate")
                                duplicate = True
                                continue
                            require(word == (0, 0, 3, 8, 2, 5), "next class moved")
                            require(duplicate, "missing duplicate")
                            require(screened == 2169, "screened count")
                            require(len(free) == 7, "nullity")
                            require(matches_shape(part, dep), "Python shape")
                            require(not matches_settled(part, dep), "still the settled class")
                            require(OVERFLOW["n"] == 0, "degree overflow")
                            return screened
    raise SystemExit("FAIL: no second nullity-7 class")


def solve_word_pure(bank, perms, target, c0, c1, c2, perm):
    choice = (c0, c1, c2)
    gates = []
    reads = []
    stages = []
    for stage in range(3):
        for half in range(2):
            proj, readm, _stage = bank[choice[stage]][stage * 2 + half]
            gates.append(pure_from_proj(proj, stage))
            reads.append(readm)
            stages.append(stage)
    right = [eye()]
    order = perms[perm]
    for k in range(6):
        right.append(mmul(gates[order[k]], right[k]))
    if right[6] != target:
        return None
    left = [None] * 7
    left[6] = eye()
    for k in range(5, -1, -1):
        left[k] = mmul(left[k + 1], gates[order[k]])
    full = [[0] * 8 for _ in range(8)]
    for k in range(6):
        ident = order[k]
        read = scale_read(reads[ident], stages[ident])
        full = madd(full, mmul(left[k + 1], mmul(read, right[k])))
    defect = madd(full, target)
    eqs = []
    for g in range(7):
        eq = [[0] * 64 for _ in range(27)]
        eq_add(eq, left[g], right[g])
        eqs.append(eq)
    return defect, eqs


def solve_loaded(hit, g0, g1):
    defect, eqs = hit
    return solve_pair(eqs[g0], eqs[g1], defect)


def fields(text):
    found = {}
    for token in text.split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        found[key] = value
    return found


def run_search():
    compiled = subprocess.run(
        ["gcc", "-O3", "-std=c11", "-Wall", "-Wextra", "-o", str(BINARY), str(PKG / "search.c")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(compiled.returncode == 0, "gcc\n" + compiled.stderr)
    require(compiled.stderr.strip() == "", "compiler warning\n" + compiled.stderr)
    proc = subprocess.run([str(BINARY)], cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise SystemExit("FAIL: search\n" + proc.stdout + proc.stderr)
    require("PASS_PAIRED_STAR_F8_PERM8_NULLITY7" in proc.stdout, "search token")
    return proc.stdout


def cleared_vectors(coeffs):
    """Rows of the leading block after clearing columns 0 and 1 at c6 = 1."""
    c0, c1, c2, c3, c4, c5, _c6 = coeffs
    rows = [
        [1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1],
        [1, 0, c0, 0, 0, c1],
        [0, 1, 0, c2, 0, 0],
        [1, 0, 0, 0, c3, 0],
        [0, 1, c4, 0, 0, c5],
    ]
    pivot0, pivot1 = rows[0], rows[1]
    cleared = []
    for row in rows[2:]:
        work = row[:]
        if work[0]:
            work = [value ^ pivot0[j] for j, value in enumerate(work)]
        if work[1]:
            work = [value ^ pivot1[j] for j, value in enumerate(work)]
        require(work[0] == 0 and work[1] == 0, "pivot columns")
        cleared.append(tuple(work[2:]))
    expect = [
        (1 ^ c0, 0, 1, c1),
        (0, 1 ^ c2, 0, 1),
        (1, 0, 1 ^ c3, 0),
        (c4, 1, 0, 1 ^ c5),
    ]
    require(cleared == expect, "cleared vectors")
    return expect


def check_c6_one():
    for code in range(8 ** 6):
        coeffs = [0] * 7
        rest = code
        for i in range(6):
            coeffs[i] = rest % 8
            rest //= 8
        coeffs[6] = 1
        vectors = cleared_vectors(coeffs)
        c0 = coeffs[0]
        pair = (vectors[0], vectors[1]) if c0 != 1 else (vectors[0], vectors[2])
        require(rank_small([list(pair[0]), list(pair[1])]) == 2, "c6=1 independence")
        span = rank_small([list(vector) for vector in vectors])
        require(span >= 2, "reduced rank")


def main():
    check_field_and_controls()
    check_c6_one()
    census = enumerate_shape()
    require(census["count"] == 8 ** 7, "domain size")
    require(census["min"] == 8 and census["below"] == 0, "Python minimum")
    require(sum(census["hist"]) == 8 ** 7, "histogram total")
    require(census["hist"][8] == 2, "two equality points")
    require(
        census["equals"] == [((0, 0, 0, 0, 0, 0, 0), 4, 4), ((0, 0, 0, 0, 0, 0, 1), 6, 2)],
        "equality witnesses",
    )
    require(((0 * 12 + 0) * 12 + 3) * 720 + 8 + 1 == 2169, "screen index")
    screened = derive_class()
    text = run_search()
    got = fields(text)
    require(got.get("next_screened") == str(screened) == "2169", "lex screen")
    require(got.get("settled_choice") == "0,0,3" and got.get("settled_perm") == "4", "settled")
    require(got.get("settled_gaps") == "2,5" and got.get("settled_screened") == "2165", "settled word")
    require(got.get("duplicate_perm") == "5" and got.get("duplicate_calls") == "2,1,0,3,4,5", "duplicate")
    require(got.get("choice") == "0,0,3" and got.get("perm") == "8" and got.get("gaps") == "2,5", "word")
    require(got.get("nullity") == "7" and got.get("new_shape") == "1", "shape")
    require(got.get("settled_shape") == "0", "not the settled shape")
    require(got.get("dep_bad") == "0" and got.get("star_bad") == "0", "star")
    require(got.get("resolution_ab") == "1,0;1,0;1,6", "resolutions")
    require(got.get("perm_calls") == "0,3,1,2,4,5", "calls")
    require(got.get("control_identity") == "1", "control")
    require(got.get("f8_count") == "2097152" and got.get("f8_min") == "8", "F8 census")
    require(got.get("f8_below8") == "0", "no rank 6 or 7")
    require(got.get("f8_checksum") == str(census["checksum"]), "checksum")
    require(got.get("f8_hist") == ",".join(str(n) for n in census["hist"]), "histogram")
    require(got.get("f8_eq8") == "2", "equality count")
    require(got.get("f8_eq8_0") == "0,0,0,0,0,0,0", "first equality")
    require(got.get("f8_eq8_1") == "0,0,0,0,0,0,1", "second equality")
    kappa = (ROOT / "certificates" / "selected-result.json").read_text(encoding="utf-8")
    require('"kappa": "781451/250000000"' in kappa, "selected kappa")
    print("f8_points=2097152 f8_min_rank_sum=8 equality_points=2")
    print("PASS_PAIRED_STAR_F8_PERM8_NULLITY7")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        sys.stderr.write("FAIL: " + str(exc) + "\n")
        sys.exit(1)
