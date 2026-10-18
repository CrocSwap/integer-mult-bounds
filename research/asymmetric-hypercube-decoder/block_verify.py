#!/usr/bin/env python3
"""Exact finite research verification; Python 3.10+, standard library only.

Copyright 2026 Sam Sung. Apache-2.0. Substantial OpenAI Codex assistance.
Finite checks supplement the written proofs; they are not formal proofs.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
from itertools import combinations, product
from collections import Counter, defaultdict
import json

def require(condition, message):
    if not condition:
        raise ValueError(message)

def partials(p, size):
    for pairs in combinations(range(p), size):
        for signs in product((0, 1), repeat=size):
            yield sum(1 << (2 * pair + sign) for pair, sign in zip(pairs, signs))

def echelon(rows):
    pivots = {}
    for word in rows:
        while word:
            pivot = word.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = word
                break
            word ^= pivots[pivot]
    return list(pivots.values())

def shortened(rows, allowed):
    outside_pivots, inside = {}, []
    for original in rows:
        word = original
        while word & ~allowed:
            pivot = (word & ~allowed).bit_length() - 1
            if pivot not in outside_pivots:
                outside_pivots[pivot] = word
                break
            word ^= outside_pivots[pivot]
        else:
            inside.append(word)
    return echelon(inside)

def positions(word):
    result = []
    while word:
        bit = word & -word
        result.append(bit.bit_length() - 1)
        word ^= bit
    return result

def constant_weight_spaces(eight, masks):
    ordered, available, spaces, planes = sorted(eight), set(eight), set(), 0
    for i, a in enumerate(ordered):
        for b in ordered[i+1:]:
            if a ^ b not in available or b >= a ^ b:
                continue
            planes += 1
            for c in ordered:
                if c <= b:
                    continue
                coset = (c, c ^ a, c ^ b, c ^ a ^ b)
                if c != min(coset) or not all(word in available for word in coset):
                    continue
                signature = tuple(sorted((a, b, a ^ b, *coset)))
                require(signature not in spaces, "duplicate canonical rank-three subspace")
                spaces.add(signature)
                union = a | b | c
                require(union.bit_count() == 14, "constant-weight subspace support")
                require(any(union & ~mask == 0 for mask in masks), "nonlocalized optimizer")
    return dict(constant_weight8_planes=planes,rank3_support14_spaces=len(spaces),
                all_rank3_support14_spaces_in_one_block=True)

def complementary_census(masks, family, syndromes, core_mask):
    buckets, quadruples = [], []
    for mask in masks:
        table = defaultdict(list)
        count = 0
        for quad in combinations(positions(mask), 4):
            syndrome, word = 0, 0
            for index in quad:
                syndrome ^= syndromes[index]
                word |= 1 << index
            table[syndrome].append(word)
            count += 1
        buckets.append(table)
        quadruples.append(count)
    accepted = 0
    for syndrome, left in buckets[0].items():
        for first in left:
            for second in buckets[1].get(syndrome, []):
                require(all(len({family[i] & core_mask for i in positions(word)}) == 1
                            for word in (first, second)), "weight-four slice not unsigned")
                accepted += 1
    return dict(quadruples_per_block=quadruples,logical_4_plus_4_supports=quadruples[0]*quadruples[1],
                accepted_supports=accepted,all_accepted_slices_unsigned=True)

def cycle_census(k, edges, family, syndromes):
    index = {port: i for i, port in enumerate(family)}
    options = {}
    for edge in edges:
        for width in (3,4):
            choices = []
            for core in partials(k-2,k-2):
                block = [index[core | (1 << (2*edge[0]+a)) | (1 << (2*edge[1]+b))]
                         for a,b in product((0,1),repeat=2)]
                choices += [tuple(quad) for quad in combinations(block,width)]
            options[edge,width] = choices
    histogram, examined = Counter(), 0
    for widths in ((3,4,3,4),(4,3,4,3)):
        for blocks in product(*(options[edge,width] for edge,width in zip(edges,widths))):
            support = tuple(i for block in blocks for i in block)
            dimension = 14-len(echelon(syndromes[i] for i in support))
            require(dimension < 3, f"cycle optimizer survived: k={k}, support={support}")
            histogram[dimension] += 1
            examined += 1
    require(examined == 32 * 2**(4*(k-2)), "complete alternating-block coverage")
    return dict(fixed_core_per_block_supports=examined,shortened_dimension_histogram=dict(histogram),
                rank3_support14_candidates_admitted=0,includes_both_3_4_orientations=True)

def build(k):
    p = k + 2
    family = list(partials(p, k))
    stars = [star for size in range(k) for star in partials(p, size)]
    rows = [sum(1 << i for i, port in enumerate(family) if port & star == star)
            for star in stars]
    global_basis = sorted(echelon(rows),key=int.bit_length,reverse=True)
    def residual(word):
        for pivot in global_basis:
            if word >> (pivot.bit_length()-1) & 1:
                word ^= pivot
        return word
    syndromes = [residual(1 << i) for i in range(len(family))]
    core = set(range(k - 2))
    block_masks = {}
    for pair in combinations(range(k - 2, p), 2):
        required = core | set(pair)
        block_masks[pair] = sum(1 << i for i, port in enumerate(family)
                                if {coordinate // 2 for coordinate in range(2 * p)
                                    if port >> coordinate & 1} == required)
    a, b, c, d = range(k - 2, p)
    core_mask = sum(3 << (2*i) for i in core)
    geometries = {"complementary": [(a,b), (c,d)], "four_cycle": [(a,b),(b,c),(c,d),(a,d)]}
    results = []
    for name, edges in geometries.items():
        masks = [block_masks[edge] for edge in edges]
        allowed = sum(masks)
        basis = shortened(rows, allowed)
        require(all(word & ~allowed == 0 for word in basis), "shortening outside coordinates")
        require(len(basis) == len(global_basis)-len(echelon(word & ~allowed for word in rows)),
                "independent shortening rank identity")
        entry = dict(k=k,p=p,geometry=name,ports=len(family),global_stars=len(stars),
                     allowed_ports=allowed.bit_count(),shortened_dimension=len(basis),
                     all_codewords_enumerated=len(basis)<=22)
        if len(basis) <= 22:
            weights, word, eight = Counter({0: 1}), 0, []
            for step in range(1, 1 << len(basis)):
                word ^= basis[(step & -step).bit_length() - 1]
                weight = word.bit_count()
                weights[weight] += 1
                if weight == 8:
                    eight.append(word)
            require(sum(weights.values()) == 1 << len(basis), "complete codeword census")
            require(min(weight for weight in weights if weight) == 8, "reduced-model minimum weight")
            universal_counts = Counter()
            for word in eight:
                universal = (1 << p)-1
                for i in positions(word):
                    pair_set = sum(1 << pair for pair in range(p) if family[i] & (3 << (2*pair)))
                    universal &= pair_set
                universal_counts[universal.bit_count()] += 1
                require(universal.bit_count() in (k-2,k), "weight-eight universal-pair gap")
            entry.update(codewords=1 << len(basis),weight_histogram=dict(sorted(weights.items())),
                         weight_eight_words=len(eight),universal_pair_histogram=dict(universal_counts),
                         **constant_weight_spaces(eight,masks))
        if name == "complementary":
            entry.update(complementary_census(masks,family,syndromes,core_mask))
            fixed_core = sum(1 << (2*i) for i in core)
            projected_star = sum(1 << i for i, port in enumerate(family)
                                 if port & (fixed_core | (1 << (2*a))) == fixed_core | (1 << (2*a))) & allowed
            require(projected_star.bit_count() == 2 and residual(projected_star) != 0,
                    "projection-versus-shortening control")
            wrong_first = [fixed_core ^ (1 << 0) ^ (1 << sign)
                           | (1 << (2*a+sa)) | (1 << (2*b)) for sign,sa in product((0,1),repeat=2)]
            other = [fixed_core | (1 << (2*c+sc)) | (1 << (2*d+sd)) for sc,sd in product((0,1),repeat=2)]
            wrong = sum(1 << family.index(port) for port in wrong_first+other)
            require(all((wrong & mask).bit_count() == 4 for mask in masks) and residual(wrong) != 0,
                    "ordinary cube parity insufficient control")
            entry["negative_controls"] = ["projected two-point star is not shortened codeword",
                                           "even 4+4 affine slices with varying core rejected"]
        else:
            entry.update(cycle_census(k,edges,family,syndromes))
            fixed_core = sum(1 << (2*i) for i in core)
            vector_words = [0,0,0]
            for j, edge in enumerate(edges):
                block = [fixed_core | (1 << (2*edge[0]+s)) | (1 << (2*edge[1]+t))
                         for s,t in product((0,1),repeat=2)]
                labels = (1,2,3) if j%2 == 0 else (4,5,6,7)
                for port,label in zip(block,labels):
                    for bit in range(3):
                        if label >> bit & 1:
                            vector_words[bit] |= 1 << family.index(port)
            false_span = [0]
            for word in vector_words:
                false_span += [word ^ existing for existing in false_span]
            require(len(set(false_span)) == 8 and all(word.bit_count() == 8 for word in false_span[1:]),
                    "false geometric model not constant weight")
            require(all(all((word & mask).bit_count()%2 == 0 for mask in masks) for word in vector_words),
                    "false model should satisfy ordinary cube parity")
            require(any(residual(word) != 0 for word in vector_words), "false cycle model escaped")
            entry["negative_controls"] = ["rank3 constant-weight8 four-cycle passes block parity but fails full code"]
        results.append(entry)
    return results


def verify():
    return dict(status="PASS", scope="Full-generator complementary-block and four-cycle "
                "shortenings for k=3,4,5 at q=2. Full word enumeration only when dimension<=22. "
                "Complementary 4+4 candidates use exact syndrome meet-in-the-middle; "
                "cycle support candidates have fixed core signs separately in each block. "
                "Case counts overlap and are not global distinct-subcode counts.",
                cases=[case for k in (3,4,5) for case in build(k)])

RECEIPT = 'BLOCK-RESULTS.json'


def self_test(result):
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        script = directory / Path(__file__).name
        script.write_bytes(Path(__file__).read_bytes())
        receipt = directory / RECEIPT
        receipt.write_text(json.dumps(result))
        command = [sys.executable, "-I", "-O", "-B", str(script)]
        run = subprocess.run(command, capture_output=True, text=True)
        require(run.returncode == 0, f"isolated optimized relocated replay failed: {run.stderr}")
        receipt.write_text(json.dumps(dict(result, status="CORRUPTED")))
        protected = directory / "protected.json"
        protected.write_text("preserve this output\n")
        run = subprocess.run(command + ["--check", str(receipt), "--write", str(protected)],
                             capture_output=True, text=True)
        require(run.returncode != 0, "corrupt receipt accepted")
        require(protected.read_text() == "preserve this output\n", "failed check overwrote output")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = json.loads(json.dumps(verify()))
    if args.check or not args.write:
        receipt = args.check or Path(__file__).resolve().with_name(RECEIPT)
        require(json.loads(receipt.read_text()) == result, f"receipt mismatch: {receipt}")
    if args.self_test:
        self_test(result)
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS", Path(__file__).name)


if __name__ == "__main__":
    main()
