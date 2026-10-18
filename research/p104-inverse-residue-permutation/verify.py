"""Read-only exact checks. Run from any directory; no Git/network dependency."""

import hashlib
import itertools
import json
from pathlib import Path
import random
from types import SimpleNamespace

import inverse

HERE = Path(__file__).resolve().parent


def source(name):
    record = json.loads((HERE / "PREDECESSOR.json").read_text(encoding="utf-8"))
    inverse.need(record["head"] == "0cc430349a3f3dc200666bc22e997076e0a557ed",
                 "predecessor head")
    entry = record["files"][name]
    raw = (HERE / "vendor" / name).read_bytes()
    inverse.need(hashlib.sha256(raw).hexdigest() == entry["sha256"], "source hash: " + name)
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    inverse.need(blob == entry["git_blob"], "source blob: " + name)
    return raw


def namespace(name):
    data = source(name)
    values = {"__name__": "pinned_" + name[:-3]}
    exec(compile(data, "pinned/" + name, "exec"), values)
    return SimpleNamespace(**values)


def load():
    for name in ("lattice.py", "lifting.py", "HNF7.json"):
        source(name)
    predecessor, word = namespace("lattice.py"), namespace("lifting.py")
    payload = json.loads(source("HNF7.json"))
    inverse.need(payload["rank"] == 7 and len(payload["rows"]) == 256, "HNF schema")
    rows = [[0] * 256 for _ in range(256)]
    for i, row in enumerate(payload["rows"]):
        seen = set()
        for j, x in row:
            inverse.need(type(j) is type(x) is int and i <= j < 256
                         and j not in seen and x != 0, "sparse HNF entries")
            rows[i][j] = x
            seen.add(j)
    predecessor.validate_basis(rows)
    return rows, predecessor, word


def pair_checks(word):
    count = 0
    for values in itertools.product(range(-3, 4), repeat=4):
        a, b = values[:2], values[2:]
        for backward in (False, True):
            answer = inverse.pair(a, b, backward)
            inverse.need(answer == word.pair(a, b, backward), "literal predecessor pair")
            def swap(z):
                return z[1], z[0]
            conjugated = tuple(swap(z) for z in inverse.pair(swap(a), swap(b), not backward))
            inverse.need(answer == conjugated, "pair swap conjugacy")
            inverse.need(inverse.pair(*answer, not backward) == (a, b), "pair inverse")
            count += 1
    return count


def fixtures():
    rng = random.Random(3035003)
    rows = []
    for rank in range(8):
        for width in (1, 4, 32, 256, 4090):
            value = [rng.getrandbits(width) * rng.choice((-1, 1))
                     for _ in range(2 << rank)]
            rows.append((rank, value))
    return rows


def image_checks(basis, predecessor):
    for j in range(256):
        column = [row[j] for row in basis]
        image = inverse.ideal_prefix(column, 7)
        inverse.need(image == predecessor.ideal(column, 7), "independent ideal image")
        inverse.need(inverse.ideal_prefix(image, 7, True) == column, "reverse parity path")
        inverse.ideal_prefix(inverse.turn(image, 7), 7)
        inverse.need(predecessor.canonical(inverse.turn(image, 7), basis) == [0]*256,
                     "image lattice in turned HNF")
        turned = inverse.turn(column, 7)
        preimage = inverse.ideal_prefix(turned, 7, True)
        inverse.ideal_prefix(preimage, 7)
        inverse.need(predecessor.canonical(preimage, basis) == [0]*256,
                     "turned HNF in image lattice")
    return 256


def run():
    basis, predecessor, word = load()
    pairs = pair_checks(word)
    images = image_checks(basis, predecessor)
    samples = fixtures()
    paired = 0
    for rank, value in samples:
        forward = inverse.literal(value, rank)
        backward = inverse.literal(value, rank, True)
        inverse.need(inverse.turn(inverse.literal(inverse.turn(value, rank), rank), rank)
                     == backward, "all-stage conjugacy")
        inverse.need(inverse.literal(forward, rank, True) == value, "signed paired return")
        for scratch in (0, -71):
            changed = value[:]
            returned, counts = inverse.turn_inplace(changed, rank, scratch)
            inverse.need(returned == scratch and changed == inverse.turn(value, rank),
                         "dirty permutation scratch")
            inverse.need(counts["scalar_swaps"] == 3*(1 << rank), "permutation invoice")
        if rank == 7:
            residue = inverse.inverse_canonical(value, basis, predecessor.canonical)
            turned = inverse.turn(residue, 7)
            inverse.need(all(0 <= x < basis[i][i] for i, x in enumerate(turned)),
                         "inverse residue box")
            inverse.ideal_prefix([x-y for x, y in zip(value, residue, strict=True)], 7, True)
            result, scratch, counts = inverse.inverse_split(value, basis, predecessor.split, -71)
            inverse.need(result == backward and scratch == -71, "exact inverse split")
            inverse.need(inverse.literal(result, 7) == value, "split paired return")
            inverse.need(counts == dict(cycles=256, scalar_swaps=768,
                                       scalar_reads=1536, scalar_writes=1536), "split invoice")
            paired += 1
    exponent = sum(row[i].bit_length()-1 for i, row in enumerate(basis))
    inverse.need(exponent == 343, "residue index")
    return dict(pair_cases=pairs, basis_columns=images, signed_word_fixtures=len(samples),
                inverse_split_fixtures=paired, residue_bits=exponent,
                rank7_one_turn=dict(cycles=128, scalar_swaps=384,
                                    scalar_reads=768, scalar_writes=768),
                rank7_inverse_boundaries=dict(cycles=256, scalar_swaps=768,
                                             scalar_reads=1536, scalar_writes=1536))


def main():
    result = run()
    expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    inverse.need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
                 "typed result receipt")
    print("PASS_P104_INVERSE_RESIDUE_PERMUTATION " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
