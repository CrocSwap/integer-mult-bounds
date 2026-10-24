"""Check the two positive five-query normal forms on three roles."""

from itertools import product
from pathlib import Path
import hashlib
import json
import struct
import time

from search import I, Z, ROLE_I, det, encode, left, mul, outer, permitted, stages

HERE = Path(__file__).resolve().parent


def main():
    start = time.monotonic()
    a = (2, -1, 1, 0)
    b = (0, -1, 1, 2)
    c = (1, 0, 4, 1)
    c_inverse = (1, 0, -4, 1)
    d = mul(mul(c, b), c_inverse)
    assert d == (4, -1, 9, -2)
    assert mul(mul(c, b), a) == Z
    maps = {"A": a, "B": b, "C": c, "D": d}
    assert all(g != I and det(g) == 1 and g[0]+g[3] == 2
               for g in maps.values())
    forms = [("A", "B", "C", "A", "B"),
             ("A", "B", "C", "D", "A")]
    pool = [(u, v, outer(u, v)) for u in range(1, 8) for v in range(1, 8)
            if (u & v).bit_count() % 2]
    assert len(pool) == 28 and pool[0] == (1, 1, 1)
    tables = [[left(u, v, value) for value in range(512)] for u, v, n in pool]
    tuples = []
    for values in product(range(28), repeat=4):
        choices = [pool[0]]+[pool[i] for i in values]
        if permitted([choice[0] for choice in choices]) and \
                permitted([choice[1] for choice in choices]):
            tuples.append(values)
    records = []
    for form in forms:
        steps, addresses = stages(form, maps)
        target_index = addresses.index(Z)
        packing = struct.Struct("<"+"H"*len(addresses))
        stream_hash = hashlib.sha256()
        hits = []
        best = None
        for values in tuples:
            coefficients = [ROLE_I]
            for choice, (id_indices, g_indices, size) in zip((0,)+values, steps):
                out = [0]*size
                tab = tables[choice]
                for j, value in enumerate(coefficients):
                    if value:
                        delta = tab[value]
                        out[id_indices[j]] ^= value ^ delta
                        out[g_indices[j]] ^= delta
                coefficients = out
            stream_hash.update(packing.pack(*coefficients))
            bad = sum((value ^ (ROLE_I if i == target_index else 0)).bit_count()
                      for i, value in enumerate(coefficients))
            if best is None or bad < best["wrong_binary_coefficients"]:
                best = {"wrong_binary_coefficients": bad,
                        "projectors": [0]+list(values),
                        "coefficients": coefficients}
            if bad == 0:
                hits.append({"projectors": [0]+list(values),
                             "coefficients": coefficients})
        record = {"form": list(form), "addresses": list(map(encode, addresses)),
                  "target_index": target_index, "checked_words": len(tuples),
                  "hits": hits, "best": best,
                  "terminal_coefficient_sha256": stream_hash.hexdigest()}
        records.append(record)
        print(json.dumps({"form": form, "checked": len(tuples),
                          "hits": len(hits), "elapsed": time.monotonic()-start}),
              flush=True)
    result = {
        "status": "EXACT_WORD_FOUND" if any(record["hits"] for record in records)
                  else "EXACT_EXHAUSTION_NO_WORD",
        "scope": "The two literal unipotent forms, all binary rank-one idempotent projectors on three complete roles.",
        "normalization": "Common DATA conjugation sets the first projector to E00.",
        "filters": "All image and covector spans must have dimension three and no coloop.",
        "maps": {name: encode(g) for name, g in maps.items()},
        "projector_pool": [{"u": u, "v": v, "mask": n} for u, v, n in pool],
        "unfiltered_tuples": 28**4, "permitted_tuples": len(tuples),
        "forms": records, "elapsed_seconds": time.monotonic()-start,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "utility_sha256": hashlib.sha256((HERE/"search.py").read_bytes()).hexdigest(),
        "kappa_gain": None,
    }
    (HERE/"POSITIVE-FIVE-RESULT.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({key: result[key] for key in
                      ("status", "unfiltered_tuples", "permitted_tuples", "elapsed_seconds")},
                     indent=2))


if __name__ == "__main__":
    main()
