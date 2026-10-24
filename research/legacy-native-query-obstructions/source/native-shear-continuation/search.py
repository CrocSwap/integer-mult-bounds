"""Check one rational plane family by exact group-algebra replay."""

from fractions import Fraction as Q
from itertools import permutations, product
from pathlib import Path
import hashlib
import json
import struct
import time

HERE = Path(__file__).resolve().parent
I = (Q(1), Q(0), Q(0), Q(1))
Z = tuple(-x for x in I)
ROLE_I = 1 | (1 << 4) | (1 << 8)


def mul(a, b):
    return tuple(sum(a[2*i+k]*b[2*k+j] for k in range(2))
                 for i in range(2) for j in range(2))


def det(a):
    return a[0]*a[3]-a[1]*a[2]


def outer(u, v):
    return sum(((u >> i) & 1)*((v >> j) & 1) << (3*i+j)
               for i in range(3) for j in range(3))


def left(u, v, c):
    row = 0
    for i in range(3):
        if (v >> i) & 1:
            row ^= (c >> (3*i)) & 7
    return outer(u, row)


def rank(vectors):
    pivots = [0]*3
    for value in vectors:
        while value:
            pivot = value.bit_length()-1
            if pivots[pivot]:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return sum(bool(value) for value in pivots)


def permitted(vectors):
    if rank(vectors) != 3:
        return False
    return all(rank(vectors[:i]+vectors[i+1:]) == 3 for i in range(5))


def stages(order, maps):
    keys = [I]
    tables = []
    for name in order:
        transformed = [mul(maps[name], g) for g in keys]
        following = sorted(set(keys+transformed))
        index = {g: i for i, g in enumerate(following)}
        tables.append(([index[g] for g in keys],
                       [index[g] for g in transformed], len(following)))
        keys = following
    return tables, keys


def encode(g):
    return [str(x) for x in g]


def main():
    start = time.monotonic()
    maps = {
        "R1": (Q(-1), Q(0), Q(0), Q(1)),
        "R2": (Q(1), Q(0), Q(0), Q(-1)),
        "U": (Q(2), Q(-1), Q(1), Q(0)),
        "V": (Q(0), Q(-1), Q(1), Q(2)),
        "W": (Q(1), Q(0), Q(4), Q(1)),
    }
    assert mul(mul(maps["W"], maps["V"]), maps["U"]) == Z
    assert mul(maps["R2"], maps["R1"]) == Z
    assert mul(mul(maps["R1"], maps["V"]), maps["R1"]) == (
        Q(0), Q(1), Q(-1), Q(2))
    for name, g in maps.items():
        difference = tuple(x-int(i % 3 == 0) for i, x in enumerate(g))
        assert any(difference) and det(difference) == 0
        assert det(g) == (-1 if name.startswith("R") else 1)
    pool = [(u, v, outer(u, v)) for u in range(1, 8) for v in range(1, 8)
            if (u & v).bit_count() % 2]
    assert len(pool) == 28 and pool[0] == (1, 1, 1)
    tables = [[left(u, v, c) for c in range(512)] for u, v, n in pool]
    assert all(tables[i][n] == n for i, (u, v, n) in enumerate(pool))
    triples = []
    for a, b, c in product(range(28), repeat=3):
        choices = [pool[a], pool[b], pool[c]]
        images = [1, 1]+[choice[0] for choice in choices]
        covectors = [1, 1]+[choice[1] for choice in choices]
        if permitted(images) and permitted(covectors):
            triples.append((a, b, c))
    stream_hash = hashlib.sha256()
    count = 0
    hits = []
    best = None
    records = []
    for order_index, order in enumerate(permutations(maps)):
        steps, addresses = stages(order, maps)
        target_index = addresses.index(Z)
        target_subset_count = sum(
            1 for bits in product((0, 1), repeat=5)
            if _subset_product(order, maps, bits) == Z)
        record = {"order": list(order), "target_subsets": target_subset_count,
                  "terminal_address_terms": len(addresses), "checked": 0}
        records.append(record)
        if target_subset_count < 3:
            continue
        packing = struct.Struct("<"+"H"*len(addresses))
        for a, b, c in triples:
            role_tables = {"R1": tables[0], "R2": tables[0],
                           "U": tables[a], "V": tables[b], "W": tables[c]}
            coefficients = [ROLE_I]
            for name, (id_indices, g_indices, size) in zip(order, steps):
                out = [0]*size
                tab = role_tables[name]
                for j, value in enumerate(coefficients):
                    if value:
                        delta = tab[value]
                        out[id_indices[j]] ^= value ^ delta
                        out[g_indices[j]] ^= delta
                coefficients = out
            stream_hash.update(packing.pack(*coefficients))
            count += 1
            record["checked"] += 1
            bad = sum((value ^ (ROLE_I if i == target_index else 0)).bit_count()
                      for i, value in enumerate(coefficients))
            if best is None or bad < best["wrong_binary_coefficients"]:
                best = {"wrong_binary_coefficients": bad, "order": list(order),
                        "projectors": [0, 0, a, b, c],
                        "addresses": list(map(encode, addresses)),
                        "coefficients": coefficients}
            if bad == 0:
                hits.append({"order": list(order), "U_projector": a,
                             "V_projector": b, "W_projector": c})
        if (order_index+1) % 20 == 0:
            print(json.dumps({"orders": order_index+1, "candidates": count,
                              "hits": len(hits), "elapsed": time.monotonic()-start}),
                  flush=True)
    result = {
        "status": "EXACT_WORD_FOUND" if hits else "EXACT_EXHAUSTION_NO_WORD",
        "scope": "These five rational maps, each once, all orders, on three complete roles.",
        "normalization": "The two negative projectors are equal by determinant sign. Common DATA conjugation sets them to E00.",
        "filters": "All images and covectors span three and have no coloop. The target has at least three subset products.",
        "projector_pool": [{"u": u, "v": v, "mask": n} for u, v, n in pool],
        "maps": {name: encode(g) for name, g in maps.items()},
        "unfiltered_projector_triples": 28**3,
        "permitted_projector_triples": len(triples),
        "orders": records, "checked_words": count, "hits": hits, "best": best,
        "terminal_coefficient_sha256": stream_hash.hexdigest(),
        "elapsed_seconds": time.monotonic()-start,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "kappa_gain": None,
    }
    (HERE/"RESULT.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({key: result[key] for key in
                      ("status", "permitted_projector_triples", "checked_words",
                       "hits", "elapsed_seconds", "terminal_coefficient_sha256")}, indent=2))


def _subset_product(order, maps, bits):
    value = I
    for name, bit in zip(order, bits):
        if bit:
            value = mul(maps[name], value)
    return value


if __name__ == "__main__":
    main()
