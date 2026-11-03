#!/usr/bin/env python3
"""Full-formal shortest-word classification; bounded exact corroboration.

New internal rank-two classification by ToikY with OpenAI Codex assistance.
Credit Petalas6449/4851, JoyboyBrian4765, Ross Richardson1989,
Adam Gall's cut method and Cinna Davis's binary census. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
PIN = "19a9013a27305a7822fa98b70175cc45caa2ca99ffb0b4620a063338253406f4"
IDENTITY = (1, 0, 0, 1)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def strict_load(raw):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    def nonfinite(value):
        raise ValueError("nonfinite JSON " + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=nonfinite)


def authenticate(root=ROOT):
    raw = (root / "SOURCE-PINS.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PIN, "source manifest")
    data = strict_load(raw)
    need(data["schema_version"] == 1 and len(data["files"]) == 3, "source schema")
    for item in data["files"]:
        path = root / item["local_path"]
        need(not path.is_symlink(), "source symlink")
        body = path.read_bytes()
        need(hashlib.sha256(body).hexdigest() == item["sha256"], "source digest")
        blob = hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body)
        need(blob.hexdigest() == item["git_blob"], "source git blob")
    return data


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def group():
    permutations = list(itertools.permutations(range(4)))
    index = {p: i for i, p in enumerate(permutations)}
    table = [[index[tuple(p[q[i]] for i in range(4))]
              for q in permutations] for p in permutations]
    labels = [index[(1, 0, 2, 3)], index[(0, 2, 1, 3)], index[(0, 1, 3, 2)]]
    return {"permutations": permutations, "table": table, "labels": labels,
            "identity": index[(0, 1, 2, 3)], "target": table[labels[0]][labels[1]]}


def reduce_vector(values, q):
    return tuple(x % q for x in values) if q is not None else tuple(values)


def scalar_product(a, b, q):
    return reduce_vector((a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3],
                          a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3]), q)


def scalar_difference(a, b, q):
    return reduce_vector([x - y for x, y in zip(a, b)], q)


def canonical(coefficients, q):
    out = []
    for g, values in sorted(coefficients.items()):
        values = reduce_vector(values, q)
        if any(values):
            out.append((g,) + values)
    return tuple(out)


def product(a, b, table, q):
    out = {}
    for first in a:
        for second in b:
            label = table[first[0]][second[0]]
            values = scalar_product(first[1:], second[1:], q)
            current = out.setdefault(label, [0, 0, 0, 0])
            for i, value in enumerate(values):
                current[i] += value
    return canonical(out, q)


def projectors(q):
    need(type(q) is int and q in (2, 3, 5), "unsupported field")
    out = []
    for code in range(q ** 4):
        p, remainder = [], code
        for _ in range(4):
            p.append(remainder % q)
            remainder //= q
        p = tuple(p)
        if any(p) and (p[0]*p[3]-p[1]*p[2]) % q == 0 and scalar_product(p, p, q) == p:
            out.append(p)
    need(len(out) == len(set(out)), "duplicate projector")
    return out


def paid(g, p, address, q):
    return canonical({address["identity"]: scalar_difference(IDENTITY, p, q),
                      g: p}, q)


def word_product(word, gates, address, q):
    state = ((address["identity"],) + IDENTITY,)
    for gate_id in word:
        state = product(state, gates[gate_id], address["table"], q)
    return state


def left_target(state, address):
    table, w = address["table"], address["target"]
    return tuple(sorted((table[w][term[0]],) + term[1:] for term in state))


def half_table(gates, address, q, omitted=None):
    lookup, products = {}, []
    stream = hashlib.sha256()
    for i, first in enumerate(gates):
        for j, second in enumerate(gates):
            state = product(first, second, address["table"], q)
            products.append(state)
            stream.update(encoded([i, j, state]))
            if (i, j) != omitted:
                lookup.setdefault(state, []).append((i, j))
    return lookup, products, stream.hexdigest()


def join_all(gates, address, q, omitted=None):
    lookup, products, half_sha = half_table(gates, address, q, omitted)
    count, hits = len(gates), []
    for k in range(count):
        for ell in range(count):
            wanted = left_target(products[ell*count+k], address)
            for i, j in lookup.get(wanted, ()):
                hits.append((i, j, k, ell))
    need(len(hits) == len(set(hits)), "duplicate full word")
    return sorted(hits), len(lookup), half_sha


def predicted_families(projector_list, q):
    count = len(projector_list)
    indices = {p: i for i, p in enumerate(projector_list)}
    complement = [indices[scalar_difference(IDENTITY, p, q)] for p in projector_list]
    block = {(p, complement[p], count+r, count+complement[r])
             for p in range(count) for r in range(count)}
    interleaved = {(p, count+p, complement[p], count+complement[p]) for p in range(count)}
    need(not block.intersection(interleaved), "family overlap")
    return block, interleaved


def domain(q, address):
    ps = projectors(q)
    gates = [paid(g, p, address, q) for g in address["labels"] for p in ps]
    identity = ((address["identity"],) + IDENTITY,)
    for gate in gates:
        need(product(gate, gate, address["table"], q) == identity, "paid involution")
    hits, distinct, half_sha = join_all(gates, address, q)
    block, interleaved = predicted_families(ps, q)
    observed = set(hits)
    extra, missing = sorted(observed-(block|interleaved)), sorted((block|interleaved)-observed)
    need(not extra and not missing, "classification counterexample " +
         json.dumps({"q": q, "extra": extra[:1], "missing": missing[:1]}))
    target = ((address["target"],) + IDENTITY,)
    for word in hits:
        need(word_product(word, gates, address, q) == target, "actual full endpoint")
    labels = Counter("".join("stu"[i//len(ps)] for i in word) for word in hits)
    return {"q": q, "projectors": ps, "gates": len(gates),
            "half_pairs": len(gates)**2, "distinct_half_products": distinct,
            "half_pairs_sha256": half_sha, "full_words_covered": len(gates)**4,
            "hits": hits, "hit_sha256": digest(hits),
            "hit_label_histogram": dict(sorted(labels.items())),
            "family_counts": {"block": len(block), "interleaved": len(interleaved)}}


def regular_call(vector, label, projector, size, table):
    out = list(vector)
    for h in range(24):
        for i in range(size):
            for j in range(size):
                value = projector[i*size+j] * vector[h*size+j]
                out[table[label][h]*size+i] += value
                out[h*size+i] -= value
    return out


def embed(p):
    return (p[0], p[1], 0, p[2], p[3], 0, 0, 0, 0)


def rational_fixture(name, calls, address):
    size, columns = 3, []
    e = (1, 0, 0, 0, 1, 0, 0, 0, 0)
    for col in range(24*size):
        vector = [Fraction(0)] * (24*size)
        vector[col] = Fraction(1)
        observed = vector
        for label, p in reversed(calls):
            observed = regular_call(observed, label, p, size, address["table"])
        expected = regular_call(vector, address["target"], e, size, address["table"])
        need(observed == expected, "rational full regular-action endpoint")
        columns.append([str(x) for x in observed])
    return {"name": name, "registers": size, "checked_basis_columns": len(columns),
            "calls": [{"label": address["labels"].index(g),
                       "projector": [str(x) for x in p]} for g, p in calls],
            "target_projector": [str(x) for x in e], "columns_sha256": digest(columns)}


def rational_fixtures(address):
    p = (Fraction(1, 3), Fraction(1, 3), Fraction(2, 3), Fraction(2, 3))
    q = (1, 0, 0, 0)
    need(scalar_product(p, q, None) != scalar_product(q, p, None), "noncommuting fixture")
    bp, bq = scalar_difference(IDENTITY, p, None), scalar_difference(IDENTITY, q, None)
    s, t = address["labels"][:2]
    block = [(s, embed(p)), (s, embed(bp)), (t, embed(q)), (t, embed(bq))]
    interleaved = [(s, embed(p)), (t, embed(p)), (s, embed(bp)), (t, embed(bp))]
    return [rational_fixture("noncommuting-block-dirty-spectator", block, address),
            rational_fixture("oblique-interleaved-dirty-spectator", interleaved, address)]


def rejects(function, *args):
    try:
        function(*args)
    except ValueError:
        return True
    raise ValueError("negative control accepted")


def semantic_controls(first, address):
    q, ps = first["q"], [tuple(p) for p in first["projectors"]]
    gates = [paid(g, p, address, q) for g in address["labels"] for p in ps]
    word = tuple(first["hits"][0])
    target = ((address["target"],) + IDENTITY,)
    fewer, _, _ = join_all(gates, address, q, omitted=word[:2])
    need(word not in fewer and set(fewer) != set(map(tuple, first["hits"])), "omitted halfword detection")
    changed = list(word)
    p_index = changed[0] % len(ps)
    other = ps.index(scalar_difference(IDENTITY, ps[p_index], q))
    changed[0] = changed[0]//len(ps)*len(ps) + other
    need(word_product(changed, gates, address, q) != target, "broken complement accepted")
    need(word_product(tuple(reversed(word)), gates, address, q) != target, "reversed orientation accepted")
    need(word_product(word[:-1], gates, address, q) != target, "omission accepted")
    return {"omitted_actual_halfword": True, "broken_complement": True,
            "reversed_written_order": True, "omitted_paid_call": True,
            "boolean_field": rejects(projectors, True), "unsupported_field": rejects(projectors, 4),
            "duplicate_json": rejects(strict_load, '{"x":1,"x":2}'),
            "nonfinite_json": rejects(strict_load, '{"x":NaN}')}


def quotient_control(address):
    pairs = [(i, j) for i in range(4) for j in range(4) if i != j]
    image = [[0]*len(pairs) for _ in pairs]
    lookup = {p: i for i, p in enumerate(pairs)}
    for p in address["permutations"]:
        for col, (i, j) in enumerate(pairs):
            row = lookup[(p[i], p[j])]
            image[row][col] ^= 1
    need(all(not any(row) for row in image), "ordered-pair group norm image")
    formal = tuple((g, 0, 1, 0, 0) for g in range(24))
    need(len(formal) == 24 and any(any(t[1:]) for t in formal), "formal norm nonzero")
    return True


def source_control():
    with tempfile.TemporaryDirectory(prefix="rank-two-source-control-") as name:
        root = Path(name)
        raw = (ROOT / "SOURCE-PINS.json").read_bytes()
        (root / "SOURCE-PINS.json").write_bytes(raw)
        manifest = strict_load(raw)
        for item in manifest["files"]:
            path = root / item["local_path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / item["local_path"]).read_bytes())
        path = root / manifest["files"][0]["local_path"]
        body = bytearray(path.read_bytes())
        body[0] ^= 1
        path.write_bytes(body)
        return rejects(authenticate, root)


def receipt(first_only=False):
    authenticate()
    address = group()
    fields = (2,) if first_only else (2, 3, 5)
    domains = [domain(q, address) for q in fields]
    controls = semantic_controls(domains[0], address)
    controls["unfaithful_ordered_pair_image"] = quotient_control(address)
    controls["actual_source_corruption"] = source_control()
    return {"schema_version": 1, "source_manifest_sha256": PIN,
            "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "domains": domains, "rational_fixtures": rational_fixtures(address),
            "controls": controls}


def same_type_tree(actual, expected):
    need(type(actual) is type(expected), "receipt value type")
    if type(expected) is dict:
        need(actual.keys() == expected.keys(), "receipt keys")
        for key in expected:
            same_type_tree(actual[key], expected[key])
    elif type(expected) is list:
        need(len(actual) == len(expected), "receipt list length")
        for a, b in zip(actual, expected):
            same_type_tree(a, b)
    else:
        need(actual == expected, "receipt value")


def main():
    need(sys.argv[1:] in ([], ["--emit"], ["--first-field"]), "unsupported arguments")
    result = receipt(sys.argv[1:] == ["--first-field"])
    result = json.loads(json.dumps(result))
    if sys.argv[1:]:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        retained = strict_load((ROOT / "RESULT.json").read_bytes())
        same_type_tree(retained, result)
        print("PASS_RANK_TWO_ST_SHORTEST_WORDS")


if __name__ == "__main__":
    main()
