"""Complete reference/fused audit equivalence and deliberate bad inputs.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance; Apache-2.0.
"""

import argparse
import copy
import gzip
import hashlib
import io
import json
import random
import tarfile
import tempfile
from contextlib import redirect_stdout
from fractions import Fraction as F
from pathlib import Path

import importlib.util

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


adapter = load("adapter")
kernel = load("kernel")
require = adapter.require


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def stable(report):
    report = dict(report)
    elapsed = report.pop("elapsed_seconds")
    require(type(elapsed) in (int, float) and elapsed >= 0, "invalid timing")
    return report


def word_bytes(root=ROOT):
    pins = adapter.source_pins(root)
    item = pins["benchmark_word"]
    with tarfile.open(root / item["archive"]) as archive:
        members = [m for m in archive.getmembers() if m.name == item["member"]]
        require(len(members) == 1 and members[0].isfile(), "ambiguous benchmark member")
        raw = archive.extractfile(members[0]).read()
    require(hashlib.sha256(raw).hexdigest() == item["compressed_sha256"], "immutable word bytes")
    require(hashlib.sha256(gzip.decompress(raw)).hexdigest() == item["payload_sha256"], "word payload")
    return raw


def expected_report(root=ROOT):
    pins = adapter.source_pins(root)
    return stable(json.loads((root / pins["reference_receipt"]).read_bytes()))


def run_case(directory, name, raw, root=ROOT):
    folder = directory / name
    folder.mkdir()
    word = folder / "FULL-WORD.json.gz"
    word.write_bytes(raw)
    outcomes = []
    for engine in ("reference", "fused"):
        out = folder / (engine + ".json")
        try:
            with redirect_stdout(io.StringIO()):
                adapter.run(word, out, root, engine)
        except (RuntimeError, ValueError, ZeroDivisionError, IndexError) as exc:
            require(not out.exists(), "failed audit left a success receipt")
            outcome = {"accepted": False, "error_type": type(exc).__name__, "error": str(exc)}
        else:
            outcome = {"accepted": True, "report": stable(json.loads(out.read_bytes()))}
        outcomes.append(outcome)
    require(canonical(outcomes[0]) == canonical(outcomes[1]), "engine disagreement: " + name)
    return outcomes[0]


def mutations(word):
    def changed(name, edit):
        w = copy.deepcopy(word)
        edit(w)
        return name, w

    add_index = next(i for i, e in enumerate(word["A"]) if e[0] == "add")
    scale_index = next(i for i, e in enumerate(word["A"]) if e[0] == "scale")
    yield changed("wrong_geometry", lambda w: w["report"].__setitem__("v", 111))
    yield changed("non_dyadic", lambda w: w["A"][add_index].__setitem__(4, 3))
    yield changed("zero_scale", lambda w: w["A"][scale_index].__setitem__(2, 0))
    yield changed("non_unit_scale", lambda w: w["A"][scale_index].__setitem__(2, 3))
    yield changed("self_add", lambda w: w["A"][add_index].__setitem__(2, w["A"][add_index][1]))
    yield changed("foreign_register", lambda w: w["A"][add_index].__setitem__(2, 100000))
    yield changed("wrong_coefficient", lambda w: w["A"][add_index].__setitem__(3, w["A"][add_index][3]+2))
    yield changed("missing_cleanup", lambda w: w["cleanup"].pop())
    yield changed("missing_precondition", lambda w: w["precondition"].pop())
    yield changed("wrong_paid_profile", lambda w: w["report"]["local_profile"].__setitem__("1", 1))
    yield changed("wrong_width_inventory", lambda w: w["report"]["width_inventory"].__setitem__("9", 1))
    yield changed("bad_center_frame", lambda w: w["center_frames"][0].pop())
    yield changed("duplicate_early_cleanup", lambda w: w["early_cleanup"].append(w["early_cleanup"][0]))
    yield changed("zero_gate_frame", lambda w: w["A"][-1].__setitem__(-1, []))
    yield changed("invalid_parent_ports", lambda w: w["ports"].__setitem__(0, w["ports"][1]))


def arithmetic_controls(root=ROOT):
    reference = adapter.auditor(root, "reference")
    rng = random.Random(93)
    pairs = 0
    # Dyadic and general rational values include cancellation, zero, missing
    # destinations, large signed numerators and unequal denominator scales.
    values = [F(0), F(1), F(-1), F(3, 2), F(-7, 32), F(1, 3), F(5, 7),
              F(2**129+1, 2**140), F(-(2**90+3), 2**16)]
    for q in values:
        for x in values:
            for y in [None] + values:
                require(kernel.fused(q, x, y) == (F(0) if y is None else y) + q*x,
                        "fused arithmetic mismatch")
                pairs += 1
    gates = 0
    for case in range(64):
        rows = [{j: rng.choice(values) for j in range(7) if rng.randrange(3)} for _ in range(5)]
        for dual in (False, True):
            a, b = copy.deepcopy(rows), copy.deepcopy(rows)
            for _ in range(80):
                t, s = rng.sample(range(5), 2)
                if rng.randrange(4):
                    q = rng.choice(values)
                    e = ["add", t, s, q.numerator, q.denominator]
                else:
                    q = rng.choice(values[1:])
                    e = ["scale", t, q.numerator, q.denominator]
                reference.apply(e, a, dual)
                kernel.apply(e, b, dual)
                require(a == b, "scalar prefix state mismatch")
                require(all(type(v) is F for row in b for v in row.values()), "row type changed")
                gates += 1
    bad = [["add", 0, 0, 1, 2], ["scale", 0, 0, 1], ["alien", 0]]
    for e in bad:
        errors = []
        for apply in (reference.apply, kernel.apply):
            try:
                apply(e, [{0: F(1)}], False)
            except RuntimeError as exc:
                errors.append(str(exc))
        require(len(errors) == 2 and errors[0] == errors[1], "scalar rejection mismatch")
    return {"fused_cases": pairs, "complete_state_prefixes": gates,
            "seed": 93, "invalid_gate_controls": len(bad)}


def trace_equivalence(directory, raw, root=ROOT):
    """Compare the actual target row at every native auditor update.

    Source snapshots also check immutability. No state or gate is sampled.
    All other rows are untouched by either source-inspected implementation.
    This extra differential pass is outside the timed production adapter.
    """
    module = adapter.auditor(root, "reference")
    reference_apply = module.apply
    calls = 0
    stream = hashlib.sha256()

    def compared(e, rows, dual=False):
        nonlocal calls
        target = e[2] if dual and e[0] == "add" else e[1]
        candidate = list(rows)
        candidate[target] = dict(rows[target])
        source = (e[1] if dual else e[2]) if e[0] == "add" else None
        source_before = dict(rows[source]) if source is not None else None
        reference_apply(e, rows, dual)
        kernel.apply(e, candidate, dual)
        require(rows[target] == candidate[target], "actual native scalar prefix mismatch")
        if source is not None:
            require(rows[source] == candidate[source] == source_before, "actual native source changed")
        stream.update(canonical([dual, e, [[k, a.numerator, a.denominator]
                                         for k, a in sorted(rows[target].items())]]).encode() + b"\n")
        calls += 1

    module.apply = compared
    word = directory / "FULL-WORD.json.gz"
    word.write_bytes(raw)
    out = directory / "trace.json"
    with redirect_stdout(io.StringIO()):
        module.run(word, out, root)
    require(canonical(stable(json.loads(out.read_bytes()))) == canonical(expected_report(root)), "trace receipt mismatch")
    return {"all_actual_updates": calls, "exact_updated_row_stream_sha256": stream.hexdigest(),
            "all_sources_unchanged": True}


def verify(root=ROOT):
    raw = word_bytes(root)
    original = expected_report(root)
    controls = {}
    with tempfile.TemporaryDirectory(prefix="fused scalar checks ") as temporary:
        directory = Path(temporary)
        first = run_case(directory, "original", raw, root)
        require(first["accepted"] and canonical(first["report"]) == canonical(original), "original receipt mismatch")
        for name, word in mutations(json.loads(gzip.decompress(raw))):
            data = gzip.compress(canonical(word).encode(), mtime=0)
            outcome = run_case(directory, name, data, root)
            require(not outcome["accepted"], "negative control accepted: " + name)
            controls[name] = outcome
        # A changed compressed container must still pass the actual auditor.
        data = gzip.compress(gzip.decompress(raw), compresslevel=1, mtime=17)
        positive = run_case(directory, "recompressed", data, root)
        require(positive["accepted"], "gzip packaging rejected")
        report = dict(positive["report"])
        report["compressed_sha256"] = original["compressed_sha256"]
        require(canonical(report) == canonical(original), "gzip packaging changed semantics")
        trace = trace_equivalence(directory, raw, root)
    return {"base_commit": adapter.source_pins(root)["base_commit"],
            "complete_report": original, "negative_controls": controls,
            "arithmetic": arithmetic_controls(root), "native_trace": trace,
            "gzip_positive_control": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="new receipt path; refuses overwrite")
    args = parser.parse_args()
    if args.write:
        require(not args.write.exists(), "output already exists")
    result = verify()
    if args.write:
        with args.write.open("x") as output:
            json.dump(result, output, indent=2, sort_keys=True)
            output.write("\n")
    else:
        require(canonical(result) == canonical(json.loads((HERE / "EXPECTED.json").read_bytes())), "differential receipt mismatch")
    print("PASS_FUSED_DYADIC_AUDIT columns=" + str(result["complete_report"]["checked_columns"]) +
          " complete_receipts=identical controls=" + str(len(result["negative_controls"])) +
          " native_updates=" + str(result["native_trace"]["all_actual_updates"]) +
          " scalar_prefixes=" + str(result["arithmetic"]["complete_state_prefixes"]))


if __name__ == "__main__":
    main()
