"""Finite corroboration of the projection proof, not a word census at n=8."""

import hashlib
import itertools
import json
from math import comb
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def prefixes(word, dimension):
    require(type(dimension) is int and 1 <= dimension <= 8, "dimension")
    require(type(word) is tuple and len(word) <= 32, "word capacity")
    state = 0
    result = [state]
    for label in word:
        require(type(label) is int and 0 <= label < dimension, "source label")
        state ^= 1 << label
        result.append(state)
    require(state == 0, "connector not restored")
    return tuple(result)


def project(mask, retained):
    return sum(((mask >> old) & 1) << new for new, old in enumerate(retained))


def projected_word(word, retained):
    labels = {old: new for new, old in enumerate(retained)}
    return tuple(labels[label] for label in word if label in labels)


def differences(states):
    return {left ^ right for left in states for right in states}


def check_projection(word, dimension, retained):
    original = prefixes(word, dimension)
    reduced = projected_word(word, retained)
    actual = prefixes(reduced, len(retained))
    require(set(actual) == {project(s, retained) for s in original}, "prefix image")
    image = {project(s, retained) for s in differences(original)}
    require(differences(actual) == image, "difference image")
    count = sum(word.count(label) for label in retained)
    require(len(reduced) == count, "projected length")
    return image


def projection_fixtures():
    words = 0
    projections = 0
    for dimension in range(1, 5):
        for length in range(0, 9, 2):
            for word in itertools.product(range(dimension), repeat=length):
                if any(word.count(label) % 2 for label in range(dimension)):
                    continue
                words += 1
                for size in range(1, dimension + 1):
                    for retained in itertools.combinations(range(dimension), size):
                        check_projection(word, dimension, retained)
                        projections += 1
    return {"closed_words": words, "subset_projections": projections}


def positive_compositions(total, parts):
    require(1 <= parts <= total <= 16, "composition capacity")
    for cuts in itertools.combinations(range(1, total), parts - 1):
        bounds = (0,) + cuts + (total,)
        yield tuple(bounds[i + 1] - bounds[i] for i in range(parts))


def arithmetic_fixtures():
    checked = 0
    feasible = []
    rejected_short = 0
    for half_length in range(8, 17):
        for halves in positive_compositions(half_length, 8):
            counts = tuple(2 * value for value in halves)
            length = sum(counts)
            retained = tuple(length - value for value in counts)
            require(sum(retained) == 7 * length, "averaging identity")
            admitted = min(retained) >= 24
            checked += 1
            if admitted:
                feasible.append((length, counts))
                require(7 * length >= 8 * 24, "projection lower bound")
            elif length < 28:
                rejected_short += 1
    require(checked == comb(16, 8), "composition coverage")
    minimum = min(length for length, _ in feasible)
    boundary = [counts for length, counts in feasible if length == minimum]
    require(minimum == 28 and len(boundary) == comb(8, 2), "boundary count")
    require(all(sorted(row) == [2, 2, 4, 4, 4, 4, 4, 4] for row in boundary),
            "boundary multiplicities")
    return {"count_vectors": checked, "short_vectors_rejected": rejected_short,
            "necessary_minimum": minimum, "length_28_vectors": len(boundary)}


def query_fixtures():
    small = []
    for length in range(16, 23, 2):
        missed = max(0, 255 - comb(length, 2))
        small.append(length + 510 + 2 * missed)
    require(min(small) == 580, "short source-word floor")
    floors = {24: 24 + 510 + 2 * 2, 26: 26 + 510 + 2 * 2,
              28: 28 + 510}
    require(min(floors.values()) == 538, "complete batch lower bound")
    return {"length_16_to_22_query_floors": small,
            "length_24_26_28_query_floors": floors, "batch_lower_bound": 538}


def gray_block(offset):
    vertices = tuple(i ^ (i >> 1) for i in range(16)) + (0,)
    word = []
    for left, right in zip(vertices, vertices[1:]):
        difference = left ^ right
        require(difference.bit_count() == 1, "Gray edge")
        word.append(offset + difference.bit_length() - 1)
    return tuple(word)


def upper_fixture():
    word = gray_block(0) + gray_block(4)
    states = prefixes(word, 8)
    witnesses = {}
    for first, left in enumerate(states[:-1]):
        for second in range(first + 1, len(states) - 1):
            mask = left ^ states[second]
            if mask:
                witnesses.setdefault(mask, (first, second))
    require(set(witnesses) == set(range(1, 256)), "upper universality")
    require(len(word) == 32 and len(set(states)) == 31, "upper shape")
    for omitted in range(8):
        keep = tuple(i for i in range(8) if i != omitted)
        require(len(check_projection(word, 8, keep)) == 128, "upper projection")
    return word, witnesses


def apply_map(matrix, vector):
    return tuple((vector[0] if row & 1 else 0)
                 ^ (vector[1] if row & 2 else 0) for row in matrix)


def xor_vectors(left, right):
    return tuple(a ^ b for a, b in zip(left, right))


def dirty_fixture(word, witnesses):
    sources = tuple((1 << (2 * j), 1 << (2 * j + 1)) for j in range(8))
    root_initial = (1 << 16, 1 << 17)
    outputs_initial = tuple((1 << (18 + 2 * i), 1 << (19 + 2 * i))
                            for i in range(255))
    source_maps = tuple(((j * 3 + 1) % 4, (j * 2 + 3) % 4) for j in range(8))
    target_maps = tuple(((i + 1) % 4, (3 * i + 2) % 4) for i in range(255))
    incoming = tuple(apply_map(matrix, data)
                     for matrix, data in zip(source_maps, sources))
    events = [[] for _ in range(33)]
    for mask, positions in witnesses.items():
        for position in positions:
            events[position].append(mask - 1)
    root = root_initial
    outputs = list(outputs_initial)
    for position in range(33):
        for target in events[position]:
            response = apply_map(target_maps[target], root)
            outputs[target] = xor_vectors(outputs[target], response)
        if position < len(word):
            root = xor_vectors(root, incoming[word[position]])
    require(root == root_initial, "dirty connector restored")
    for mask in range(1, 256):
        source_sum = (0, 0)
        for source in range(8):
            if mask & (1 << source):
                source_sum = xor_vectors(source_sum, incoming[source])
        wanted = xor_vectors(outputs_initial[mask - 1],
                             apply_map(target_maps[mask - 1], source_sum))
        require(outputs[mask - 1] == wanted, "dirty target endpoint")
    return {"source_calls": len(word), "readout_calls": sum(map(len, events)),
            "total_queries": len(word) + sum(map(len, events)),
            "dirty_input_basis_columns": 528}


def negative_controls(word, witnesses):
    rejected = 0
    cases = [((0,), 8), ((True, True), 8), ((8, 8), 8),
             ((0, 0), 0), (word + word, 8)]
    for invalid, dimension in cases:
        try:
            prefixes(invalid, dimension)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid word accepted")
    require(len(differences(prefixes(tuple(range(8)) * 2, 8))) < 256,
            "restoration alone is not universality")
    require(26 * 7 < 24 * 8, "26-call false floor control")
    reduced = projected_word((0, 1, 0, 1), (0,))
    require(len(reduced) == 2 and len(reduced) != 4,
            "uncompressed deletion length control")
    omitted = dict(witnesses)
    omitted[1] = (witnesses[1][0],)
    swapped = dict(witnesses)
    swapped[1], swapped[2] = swapped[2], swapped[1]
    reordered = list(word)
    reordered[0], reordered[16] = reordered[16], reordered[0]
    for bad_word, bad_witness in ((word, omitted), (word, swapped),
                                  (tuple(reordered), witnesses)):
        try:
            dirty_fixture(bad_word, bad_witness)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("corrupt literal schedule accepted")
    return rejected + 3


def main():
    word, witnesses = upper_fixture()
    result = {"claim_type": "scoped written proof with finite corroboration",
              "source_lower_bound": 28, "source_upper_bound": 32,
              "projections": projection_fixtures(),
              "arithmetic": arithmetic_fixtures(), "queries": query_fixtures(),
              "upper_fixture": dirty_fixture(word, witnesses),
              "negative_controls": negative_controls(word, witnesses)}
    require(result["upper_fixture"]["total_queries"] == 542, "upper query bill")
    package = Path(__file__).resolve().parent
    result["source_sha256"] = {
        name: hashlib.sha256((package / name).read_bytes()).hexdigest()
        for name in ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    print("PASS_EIGHT_SOURCE_SINGLETON_FLOOR 28<=f(8)<=32 queries>=538 upper=542")


if __name__ == "__main__":
    main()
