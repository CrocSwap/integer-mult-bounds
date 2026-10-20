"""Source-bound census and independent action checks for the price envelope.

Produced by Nick Petalas. Apache-2.0. No predecessor executable is imported.
"""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

import envelope


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
HISTOGRAM = {16: 42, 19: 120, 21: 180, 22: 56, 23: 45,
             24: 220, 26: 110, 28: 150, 31: 22}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def matching_words():
    """Five bounded pairing layers, independent of restricted-growth generation."""
    layer = [(tuple(range(10)), ())]
    for _ in range(5):
        following = []
        for points, pairs in layer:
            first = points[0]
            for partner in points[1:]:
                remaining = tuple(p for p in points if p not in (first, partner))
                following.append((remaining, pairs + ((first, partner),)))
        layer = following
    words = []
    for remaining, pairs in layer:
        need(not remaining, "incomplete matching")
        word = [-1] * 10
        for label, (left, right) in enumerate(pairs):
            word[left] = word[right] = label
        words.append(tuple(word))
    return tuple(sorted(words))


def independent_prefixes(word):
    return tuple(sum((sum(j == label for j in word[:cut]) % 2) << label
                     for label in range(5)) for cut in range(len(word) + 1))


def census():
    words = matching_words()
    need(len(words) == len(set(words)) == 945, "matching census cardinality")
    need(words == tuple(sorted(envelope.canonical_words())), "word generators disagree")
    histogram, sole, records = Counter(), Counter(), []
    odd_masks = set(envelope.ELIGIBLE_OUTPUTS)
    for word in words:
        states = independent_prefixes(word)
        need(states == envelope.prefixes(word), "prefix implementations disagree")
        available = {left ^ right for left in states for right in states}
        missing = sorted(set(range(32)) - available)
        need(odd_masks.intersection(missing), "a word covers every odd mask")
        histogram[len(available)] += 1
        if len(missing) == 1:
            sole[missing[0].bit_count()] += 1
        records.append([word, missing])
    need(dict(histogram) == HISTOGRAM, "predecessor histogram differs")
    need(dict(sole) == {3: 20, 5: 2}, "sole-omission classes differ")
    digest = sha256(json.dumps(records, separators=(",", ":")).encode()).hexdigest()
    return {"paths": len(words), "histogram": dict(sorted(histogram.items())),
            "sole_omissions": dict(sorted(sole.items())), "records_sha256": digest}


def symbolic(word):
    """Free noncommutative words, with every dirty input independent."""
    z = {("z",)}
    outputs = {m: {(f"y{m}",)} for m in range(1, 32)}
    for kind, index in word:
        if kind == "B":
            z.symmetric_difference_update({(f"B{index}", f"x{index}")})
        else:
            outputs[index].symmetric_difference_update((f"A{index}",) + term for term in z)
    expected = {m: {(f"y{m}",)} | {(f"A{m}", f"B{j}", f"x{j}")
                                  for j in range(5) if m >> j & 1}
                for m in range(1, 32)}
    return z == {("z",)} and outputs == expected


def matrix_apply(matrix, value):
    return sum(((row & value).bit_count() % 2) << bit for bit, row in enumerate(matrix))


def dense_replay(word, bits, inverse=False):
    # Two-bit maps include a noncommuting pair and a singular map.
    sources = ((1, 3), (2, 1), (3, 2), (1, 1), (0, 3))
    targets = tuple(((m % 3) + 1, ((m + 1) % 4)) for m in range(1, 32))
    rows = list(bits)
    operations = reversed(word) if inverse else word
    for kind, index in operations:
        if kind == "B":
            rows[36] ^= matrix_apply(sources[index], rows[index])
        else:
            rows[4 + index] ^= matrix_apply(targets[index - 1], rows[36])
    return rows


def expected_dense(bits):
    sources = ((1, 3), (2, 1), (3, 2), (1, 1), (0, 3))
    targets = tuple(((m % 3) + 1, ((m + 1) % 4)) for m in range(1, 32))
    rows = list(bits)
    for mask in range(1, 32):
        total = 0
        for j in range(5):
            if mask >> j & 1:
                total ^= matrix_apply(sources[j], bits[j])
        rows[4 + mask] ^= matrix_apply(targets[mask - 1], total)
    return rows


def check_witnesses(witnesses):
    basis_cases = 0
    for repeat, word in witnesses.items():
        counts = Counter(f"{kind}{index}" for kind, index in word)
        expected = {f"B{j}": 2 for j in range(5)}
        expected.update({f"A{m}": 2 for m in range(1, 32)})
        expected[repeat] += 2
        need(counts == expected and len(word) == 74, "wrong repeated operator")
        need(symbolic(word), "generic action or dirty restoration")
        for bit in range(74):
            data = [0] * 37
            data[bit // 2] = 1 << (bit % 2)
            forward = dense_replay(word, data)
            need(forward == expected_dense(data), "dense basis action")
            need(dense_replay(word, forward, inverse=True) == data, "dense inverse")
            basis_cases += 1
        for sample in range(32):
            data = [((sample + 1) * (j + 3) ^ (sample >> (j % 5))) % 4 for j in range(37)]
            need(dense_replay(word, data) == expected_dense(data), "dense dirty mixture")
    return basis_cases


def check_prices(witnesses):
    # Each linear piece is uniquely active at one positive price vector.
    for repeat, word in witnesses.items():
        source, output = [100] * 5, [100] * 31
        kind, index = repeat[0], int(repeat[1:])
        (source if kind == "B" else output)[index if kind == "B" else index - 1] = 1
        minimum, chosen = envelope.optimum(source, output)
        bills = {name: envelope.invoice(w, source, output) for name, w in witnesses.items()}
        need(chosen == repeat and bills[repeat] == minimum, "price facet not attained")
        need(sum(value == minimum for value in bills.values()) == 1, "redundant facet")
        need(envelope.invoice(word, source, output) == minimum, "invoice mismatch")
    need(envelope.optimum([1, 4, 10, 16, 28], [1] * 31)[0] == 182, "PR1770 fixture")
    need(envelope.optimum([1] * 5, [1] * 31)[0] == 74, "PR943 fixture")
    source, output = [100] * 5, [100] * 31
    output[2] = 1  # Cheap mask 3 has weight two, so cannot pay the odd-mask defect.
    minimum, _ = envelope.optimum(source, output)
    need(minimum == 2 * (sum(source) + sum(output)) + 200, "even-mask price control")
    source = [Fraction(j + 1, 7) for j in range(5)]
    output = [Fraction(m + 2, 11) for m in range(31)]
    value, chosen = envelope.optimum(source, output)
    need(envelope.invoice(witnesses[chosen], source, output) == value, "rational prices")
    return 20


def check_controls(witnesses):
    word = witnesses["B0"]
    for kind in ("A", "B"):
        cut = next(i for i, op in enumerate(word) if op[0] == kind)
        need(not symbolic(word[:cut] + word[cut + 1:]), "deleted call accepted")
    changed = tuple((kind, 1 if index == 0 else index) if kind == "B" else (kind, index)
                    for kind, index in word)
    need(not symbolic(changed), "source-only relabelling accepted")
    changed = tuple((kind, 2 if index == 1 else index) if kind == "A" else (kind, index)
                    for kind, index in word)
    need(not symbolic(changed), "wrong output accepted")
    rejected = 0
    for source, output in (([0] * 5, [1] * 31), ([1] * 4, [1] * 31),
                           ([1.0] * 5, [1] * 31)):
        try:
            envelope.optimum(source, output)
        except ValueError:
            rejected += 1
    need(rejected == 3, "invalid tariff accepted")
    return 7


def source_hashes():
    manifest = json.loads((ROOT / "SOURCES.json").read_text())
    hashes = {}
    for entry in manifest["files"]:
        if entry["usage"] != "input":
            continue
        data = (REPO / entry["path"]).read_bytes()
        digest = sha256(data).hexdigest()
        need(digest == entry["sha256"], "source pin mismatch: " + entry["path"])
        hashes[entry["path"]] = digest
    for name in ("envelope.py", "verify.py", "README.md", "TASK.json", "SOURCES.json", "VERIFY.json"):
        hashes[name] = sha256((ROOT / name).read_bytes()).hexdigest()
    predecessor = json.loads((REPO / "research/universal-connector-boundary/CERTIFICATE.json").read_text())
    word = predecessor["schedules"]["five_extra_source"]["word"]
    need(tuple(index for kind, index in word if kind == "B") == envelope.EXTRA_SOURCE,
         "twelve-toggle predecessor template changed")
    return hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--show-witness", choices=[f"B{j}" for j in range(5)] +
                        [f"A{m}" for m in envelope.ELIGIBLE_OUTPUTS])
    args = parser.parse_args()
    hashes = source_hashes()
    counted = census()
    witnesses = envelope.schedules()
    need(len(witnesses) == 16, "witness family size")
    basis = check_witnesses(witnesses)
    tariffs = check_prices(witnesses)
    controls = check_controls(witnesses)
    receipt = {"claim_type": "scoped proof with finite census", "census": counted,
               "witnesses": 16, "basis_cases": basis, "dirty_cases": 512,
               "price_cases": tariffs, "controls": controls, "source_sha256": hashes,
               "witness_sha256": sha256(json.dumps(witnesses, sort_keys=True).encode()).hexdigest()}
    print(json.dumps(receipt, sort_keys=True))
    if args.show_witness:
        print(json.dumps({"repeat": args.show_witness, "word": witnesses[args.show_witness]}))
    print(f"PASS_CONNECTOR_PRICE_ENVELOPE paths=945 witnesses=16 basis={basis} "
          f"dirty=512 price_cases={tariffs} controls={controls} no_new_kappa")


if __name__ == "__main__":
    main()
