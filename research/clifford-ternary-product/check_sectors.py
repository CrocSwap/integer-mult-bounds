"""Check independent sector labels, all Pauli coordinates and the carried product."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_product import positions
from multiply import geometry, multiply_bits
from operand import recognise_sparse
from sectors import control_sites, high_pairs, recognise_sectors, sector_product
from templates import pack, unpack


def pauli_check():
    # The coefficient alpha of a Pauli word is its Hilbert-Schmidt adjoint / 2^m.
    pauli = (((1,0),(0,1)), ((0,1),(1,0)), ((1,0),(0,-1)))
    rng = Random(7824)
    checked = 0
    for m in range(1, 5):
        n = 1 << m
        for _ in range(4):
            a = [rng.randrange(2) for _ in range(n)]
            b = [rng.randrange(2) for _ in range(n)]
            alpha = {}
            for word in product(range(3), repeat=m):
                adjoint = 0
                for x in range(n):
                    for y in range(n):
                        entry = a[x]*b[y]
                        for i, p in enumerate(word):
                            entry *= pauli[p][(x >> i) & 1][(y >> i) & 1]
                        adjoint += entry
                alpha[word] = Fraction(adjoint, n)
            for address in range(3 ** m):
                pairs = list(high_pairs(address, m))
                trits = tuple(((pairs[0][0] >> i) & 1) + ((pairs[0][1] >> i) & 1)
                              for i in range(m))
                decoded = sum(v * (-1)**sum(s == 2 and p == 2 for s, p in zip(trits, word))
                              for word, v in alpha.items()
                              if all((s == 1) == (p == 1) for s,p in zip(trits,word)))
                decoded *= 1 << trits.count(1)
                if decoded != sum(a[x]*b[y] for x,y in pairs):
                    raise ValueError("The fused local Clifford decoder differs from its adjoint")
                checked += 1
    return checked


def independent_sectors(m, rng):
    h = control_sites(m)
    k = m-h
    high, low = positions(h), positions(k)
    payload = bytearray(3 ** m)
    # The isolated low selector makes each fibre full and balanced.
    for label, hi in enumerate(high):
        lin = rng.randrange(1 << k) & ~1
        edges = [(1 << i) | (1 << j) for i in range(k) for j in range(1,i) if rng.randrange(2)]
        for x, lo in enumerate(low):
            payload[hi*(3**k)+lo] = ((x & 1) ^ (label.bit_count() & 1)
                ^ ((x & lin).bit_count() & 1) ^ (sum(x & e == e for e in edges) & 1))
    return bytes(payload)


def main():
    rng = Random(105)
    paulis = pauli_check()
    for h in range(7):
        offsets = positions(h)
        seen = set()
        for a in range(3**h):
            for x, y in high_pairs(a, h):
                if (x,y) in seen or offsets[x] + offsets[y] != a:
                    raise ValueError("Incorrect ordered sector pair")
                seen.add((x,y))
        if len(seen) != 4**h:
            raise ValueError("A sector pair is missing")

    m = 6
    cubic = bytearray(3**m)
    for x, place in enumerate(positions(m)):
        cubic[place] = (x & 1) ^ int(x & 38 == 38)
    if recognise_sparse(cubic, m) is not None:
        raise ValueError("An irreducible cubic was admitted as a single chart")
    for h in range(1, m // 2 + 1):
        fitted = recognise_sectors(cubic, m, h)
        if fitted is None or pack(sector_product(fitted, fitted)) != pack(cubic)**2:
            raise ValueError("The high-bit quadratic restriction was lost")

    for m in (5, 6, 7, 8):
        extent = 3 ** m
        _, width, count = geometry(extent)
        left, right = (independent_sectors(m, rng) for _ in range(2))
        if recognise_sparse(left, m) is not None or recognise_sparse(right, m) is not None:
            raise ValueError("The fixture must require independent Clifford labels")
        a, b = (recognise_sectors(item, m) for item in (left, right))
        if pack(sector_product(a, b)) != pack(left)*pack(right):
            raise ValueError("Incorrect block products or carries")
        geometric = ((1 << (width*count))-1)//((1 << width)-1)
        periods = (1 << (width-1)) + 1, (1 << (width-1)) - 1
        x = geometric * periods[0] + (pack(left) << width)
        y = geometric * periods[1] - (pack(right) << width)
        receipt = {}
        result = multiply_bits(unpack(x, extent), unpack(y, extent), evidence=receipt)
        if (pack(result) != x*y or receipt["route"] != "clifford-sectors"
                or receipt["delivery"]["pairs"] != 4**control_sites(m)):
            raise ValueError((m, receipt))
        if m == 8:
            print("independent_sector_product", len(result), "bits", receipt,
                  "sha256", sha256(result).hexdigest())
    print("pauli_readouts", paulis, "sector_partitions", 7, "independent_products", 8)


if __name__ == "__main__":
    main()
