#!/usr/bin/env python3
"""Check the exact character obstruction for the rank-sixteen factor."""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "odd16-normal-v2/EXTENSION-PROGRAM.json.gz"
SOURCE_PIN = "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4"


def need(test, message):
    if not test:
        raise ValueError(message)


def rank(rows, columns):
    data = [[row.get(j, F(0)) for j in range(columns)] for row in rows]
    used = 0
    for column in range(columns):
        pivot = next((i for i in range(used, len(data)) if data[i][column]), None)
        if pivot is None:
            continue
        data[used], data[pivot] = data[pivot], data[used]
        scale = data[used][column]
        data[used] = [value / scale for value in data[used]]
        for i in range(used + 1, len(data)):
            scale = data[i][column]
            if scale:
                data[i] = [a - scale * b for a, b in zip(data[i], data[used])]
        used += 1
    return used


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    need(not args.out.exists(), "Use a new receipt path")
    raw = gzip.decompress(SOURCE.read_bytes())
    need(sha256(raw).hexdigest() == SOURCE_PIN, "Exact rank16 source")
    model = json.loads(raw)["model"]
    q, cliques = model["ports"], model["small_cliques"]
    u = [{int(p): F(c) for p, c in row.items()} for row in model["correction_U"]]
    v = [{int(p): F(c) for p, c in row.items()} for row in model["correction_V"]]
    need(rank(u, 16) == rank(v, 112) == 16, "Both factors have full rank")
    z = 45
    need(z.bit_count() % 2 == 0, "The common direction is isotropic")
    need(sorted(p for clique in cliques for p in clique) == sorted(model["small_ports"]),
         "The eight cliques partition the actual small ports")
    for i, clique in enumerate(cliques):
        need(len(clique) == 8 and all(
            (q[p] & q[t]).bit_count() % 2 == int(p == t) for p in clique for t in clique),
            "Each clique contains eight orthonormal directions")
        total = 0
        for p in clique:
            total ^= q[p]
        need(total == z and all((q[p] & z).bit_count() % 2 == 1 for p in clique),
             "Each actual orthonormal clique sums to the same isotropic direction")
        need(v[8 + i] == {p: F(1) for p in clique}, "Exact small query row")
        need(all(u[p].get(8 + i, 0) == (-1 if p in clique else 0) for p in range(112)),
             "Exact small scatter column")
        need(all(u[p] == {8 + i: F(-1)} for p in clique), "No other scatter uses this clique")
        need(all(not set(v[j]).intersection(clique) for j in range(16) if j != 8 + i),
             "The small cross-Gram block is isolated")
    counts = [0] * 8
    character_masks = []
    character_ranks = []
    sector_ranks = [Counter(), Counter()]
    witness = None
    for w in range(512):
        gram = [{} for _ in range(16)]
        for i, row in enumerate(v):
            for p, coefficient in row.items():
                sign = (-1) ** ((q[p] & w).bit_count() % 2)
                for j, value in u[p].items():
                    gram[i][j] = gram[i].get(j, F(0)) + coefficient * sign * value
        gram = [{j: value for j, value in row.items() if value} for row in gram]
        current_rank = rank(gram, 16)
        character_ranks.append(current_rank)
        sector_ranks[(z & w).bit_count() % 2][current_rank] += 1
        mask = 0
        for i, clique in enumerate(cliques):
            signs = [(-1) ** ((q[p] & w).bit_count() % 2) for p in clique]
            value = -sum(signs)
            if value == 0:
                counts[i] += 1
                mask |= 1 << i
                need((z & w).bit_count() % 2 == 0, "Every zero is in the positive Z sector")
                if witness is None:
                    witness = {"character": w, "clique_index": i, "ports": clique,
                               "directions": [q[p] for p in clique], "signs": signs,
                               "cross_gram_column": 8 + i}
        character_masks.append(mask)
    need(counts == [140] * 8 and witness is not None, "Exact balanced-sign counts")
    need(Counter(character_masks) == {0: 372, 255: 140}, "All eight small zeros occur together")
    need(all(character_masks[w] == 0 for w in range(512) if (z & w).bit_count() % 2),
         "No small-block zero in the negative Z sector")
    need(sector_ranks == [{0: 32, 4: 96, 8: 12, 16: 116}, {14: 256}],
         "Exact full cross-Gram ranks in both Z sectors")
    output = {
        "status": "PASS_EVEN_CLIQUE_CROSS_GRAM_OBSTRUCTION",
        "source_decompressed_sha256": SOURCE_PIN,
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "zero_characters_per_clique": counts,
        "characters_with_at_least_one_zero_small_block": sum(bool(mask) for mask in character_masks),
        "character_zero_block_masks": character_masks,
        "character_full_cross_gram_ranks": character_ranks,
        "full_cross_gram_rank_counts": dict(sorted(Counter(character_ranks).items())),
        "positive_Z_rank_counts": dict(sorted(sector_ranks[0].items())),
        "negative_Z_rank_counts": dict(sorted(sector_ranks[1].items())),
        "invertible_characters": character_ranks.count(16),
        "witness": witness,
        "scope": "The exact minimal cross-Gram V Q^2 U is not an everywhere unit in the local nine-axis character algebra. Other terminal mechanisms remain open.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(output["status"], output["full_cross_gram_rank_counts"], witness)


if __name__ == "__main__":
    main()
