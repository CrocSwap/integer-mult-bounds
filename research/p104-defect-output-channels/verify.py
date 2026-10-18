"""Read-only exact witness, source, and delivery replay. Apache-2.0."""

from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import types

ROOT = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def module(path, name):
    result = types.ModuleType(name)
    result.__file__ = str(path)
    # Inherited source assertions, if any, stay active during optimized replay.
    exec(compile(path.read_bytes(), str(path), "exec", optimize=0), result.__dict__)
    return result


def authenticate(root=ROOT):
    manifest = json.loads((root / "PREDECESSOR.json").read_text())
    need(len(manifest["files"]) == 1, "one exact predecessor input")
    row = manifest["files"][0]
    need(row["source_commit"] == "b12bbaeb5ca2e83f15433fc2dd0ba3b766595281" and
         row["source_pr"] == 3033 and row["local"] == "vendor/lifting.py", "source identity")
    source = root / row["local"]
    need(not source.is_symlink(), "regular source file")
    raw = source.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == row["sha256"], "predecessor SHA256")
    need(hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest() == row["git_blob"],
         "predecessor Git blob")
    return module(source, "predecessor_lift")


def typed_equal(first, second):
    if type(first) is not type(second):
        return False
    if isinstance(first, dict):
        return first.keys() == second.keys() and all(typed_equal(first[k], second[k]) for k in first)
    if isinstance(first, list):
        return len(first) == len(second) and all(typed_equal(a, b) for a, b in zip(first, second))
    return first == second


def result():
    model = module(ROOT / "model.py", "primary_model")
    predecessor = authenticate()
    need(all(65537 % divisor for divisor in range(2, 257)), "prime65537")
    pair_cases = 0
    for ar, ai, br, bi in itertools.product(range(-2, 3), repeat=4):
        value = [ar, ai, br, bi]
        pair = predecessor.pair((ar, ai), (br, bi))
        need(model.lift(value, 1) == [component for z in pair for component in z],
             "signed literal pair source")
        error = (ai-bi) % 2 - (ar-br) % 2
        need(model.defect(value, 1) == [error, -error, error, -error], "local error identity")
        pair_cases += 1
    rows, source_cases, delivery_cases, dirty_cases = [], 0, 0, 0
    for rank in range(1, 8):
        n, dimension = 1 << rank, model.shape(rank)
        invoice = model.invoice(rank)
        wanted = 2*n-model.fibonacci(rank+3)
        need(invoice["real_channels"] == wanted, "mode-count Fibonacci formula")
        basis, witnesses, source_values = model.ModularBasis(65537), [], []
        for candidate_count, (description, value) in enumerate(model.candidates(rank), 1):
            defect, spectrum = model.defect(value, rank), model.spectral(value, rank)
            channels = model.pack(spectrum, rank)
            need(model.decode(channels, rank) == defect, "integer channel decode")
            need(model.walsh(defect, rank) == [n*c for c in spectrum], "integer spectrum relation")
            for mask in range(n):
                bound = (n//2)*(rank-mask.bit_count())
                need(all(abs(x) <= bound for x in spectrum[2*mask:2*mask+2]), "spectral range")
            need(max(map(abs, defect)) <= invoice["full_scaled_defect_component_bound"], "full defect range")
            pivot = basis.append(defect)
            if pivot is not None:
                witnesses.append([description, pivot])
                source_values.append(value)
            if len(basis.rows) == wanted:
                break
        need(len(basis.rows) == wanted, "attained real-linear dimension")
        # Compare independently generated full-word inputs with the unchanged source.
        identity = [(j, 0) for j in range(n)]
        fixtures = [source_values[0], source_values[-1]]
        fixtures += [[(-1 if i % 3 else 1)*((1 << bits)+3*i+1)
                      for i in range(dimension)] for bits in (0, 13, 101, 4090)]
        for value in fixtures:
            gaussian = list(zip(value[::2], value[1::2]))
            source = predecessor.kernel(gaussian, rank, identity, identity)
            need(model.lift(value, rank) == [v for z in source for v in z], "signed full-word source")
            source_cases += 1
            channels = model.encode(value, rank)
            original = list(channels)
            decoded = model.defect(value, rank)
            output_width = invoice["full_scaled_defect_signed_width"]
            packed = model.signed_bits(decoded, output_width)
            for target in (0, (1 << (dimension*output_width))-1):
                work = [[0]*dimension for _ in range(rank+1)]
                actual = model.delivery_oracle(channels, target, work, rank)
                need(actual == target ^ packed and channels == original and
                     not any(any(bank) for bank in work), "arbitrary-target delivery and literal cleanup")
                delivery_cases += 1
            # Credited immutable-source dirty-buffer consumer, now using channel decode.
            numerator = model.numerator(value, rank)
            wanted_lift = model.lift(value, rank)
            for dirt in (-10003, -1, 0, 17, 10003):
                scratch = [dirt+7*i for i in range(dimension)]
                target = [11-3*i for i in range(dimension)]
                before = list(scratch)
                target = [y-b//n for y, b in zip(target, scratch)]
                scratch = [b+a+d for b, a, d in zip(scratch, numerator, decoded)]
                target = [y+b//n for y, b in zip(target, scratch)]
                scratch = [b-a-d for b, a, d in zip(scratch, numerator, decoded)]
                need(scratch == before and target == [11-3*i+x for i, x in enumerate(wanted_lift)],
                     "dirty consumer restoration")
                dirty_cases += 1
        operations, widths = model.delivery_program(rank)
        histogram = Counter(str(operation[-1]) for operation in operations)
        need({k: 2*v for k, v in histogram.items()} ==
             invoice["reversible_delivery_modular_add_width_histogram"], "complete delivery ADD histogram")
        need(2*len(operations) == invoice["reversible_delivery_modular_adds"], "delivery ADD total")
        need(dimension*sum(widths) == invoice["reversible_delivery_clean_bank_bits"], "all layer backing")
        rows.append({**invoice, "prime": 65537, "candidate_count": candidate_count,
                     "witnesses_and_pivots": witnesses,
                     "witness_input_sha256": hashlib.sha256(json.dumps(source_values, separators=(",", ":")).encode()).hexdigest()})
    return {"status": "PASS_P104_DEFECT_OUTPUT_CHANNELS_NO_NEW_KAPPA", "ranks": rows,
            "signed_pair_source_cases": pair_cases, "signed_full_word_source_cases": source_cases,
            "arbitrary_target_delivery_cases": delivery_cases, "arbitrary_dirty_consumer_cases": dirty_cases,
            "coverage": "All-integer upper proof; finite exact rank1..7 independence certificates and macro-delivery fixtures. No rank8+ attainment, direct encoded producer, bit ADD lowering, physical/tape or recursive supplier admission."}


def main():
    need(typed_equal(result(), json.loads((ROOT / "RESULT.json").read_text())),
         "typed exact result mismatch")
    print("PASS_P104_DEFECT_OUTPUT_CHANNELS_NO_NEW_KAPPA")


if __name__ == "__main__":
    main()
