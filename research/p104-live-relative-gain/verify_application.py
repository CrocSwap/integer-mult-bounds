"""Replay the two native circuits and the finite conditional multiplication claim."""
import argparse
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import tarfile
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify_split_helpers import canonical, check, read, rebuild, reconstruct


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def source_tree(work, receipt):
    archive = HERE / "APPLICATION-SOURCES.tar.gz"
    check(sha256(archive.read_bytes()).hexdigest() == receipt["source_archive"], "public source archive")
    with tarfile.open(archive) as files:
        names = files.getmembers()
        check(len(names) == len({item.name for item in names}) == receipt["source_count"]
              and all(item.isfile() for item in names), "source file inventory")
        files.extractall(work, members=names, filter="data")
    package = work / "recipient"
    prefix = "research/p104-iterated-returns/"
    pins = {item["path"].removeprefix(prefix): item["sha256"] for item in read("SOURCES.json")["files"]
            if item["path"].startswith(prefix)}
    for path in package.rglob("*"):
        if path.is_file():
            check(sha256(path.read_bytes()).hexdigest() == pins[str(path.relative_to(package))],
                  f"recipient source {path.relative_to(package)}")
    prepare = module("locked_sources", package / "prepare_sources.py")
    check(prepare.sources(work) + 7 == len(names), "SHA-256 and Git blobs of all inherited files")
    return package


def ordinary_bit(work, package, result):
    finite = module("finite_bit", package / "binary/finite.py")
    source, parent = work / "source", work / "parent"
    for path, pin in finite.SOURCE_PINS.items():
        finite.pinned(source / path, pin)
    for path, pin in finite.PACKAGE_PINS.items():
        finite.pinned(parent / path, pin)
    literal = module("literal", parent / "binary/independent/literal.py")
    price = module("binary_price", parent / "binary/independent/price.py")
    compiler = module("credited_product", source / finite.FINITE)
    baseline = literal.candidate_word(parent / "binary/WORD.json.gz")
    caller = literal.pinned(source / finite.PAIRED / "EFREE-CALLER.json.gz", literal.CALLER_SHA)
    native = finite.candidate_receipt(literal, HERE / "BINARY-CANDIDATE.json.gz",
                                      result["binary_word"], baseline, caller)
    seed = Fraction(json.loads((source / finite.CLAIM).read_bytes())["admitted_BIT_saving"])
    proof = finite.ordinary_certificate(price, compiler, native, seed, None, None)
    summary = dict(public=native["public"], instructions=native["instruction_counts"],
                   productive=native["native_targets"], paid=native["native_paid"], calls=native["native_calls"],
                   paid_all=native["paid"], productive_all=native["targets"], ordinary=native["ordinary"])
    check(json.loads(json.dumps(summary)) == result["binary_native"], "binary native and complete bills")
    check(proof["raw_crossing"] == result["binary_raw"] and proof["ordinary_admitted"] == result["binary_ordinary"]
          and proof["independent_directed_compiler"]["H"] == result["binary_H"]
          and proof["finite_product_bound_bit_lengths"] == result["binary_product"], "finite ordinary BIT")
    check(native["native_calls"] == 36 and seed == Fraction("0.00385248"), "binary caller and ordinary seed")
    return Fraction(proof["ordinary_admitted"])


def rational_application(work, package, result, bit):
    sys.path.insert(0, str(package / "continuation"))
    import qualify

    qualify.check_sources(work, package)
    sys.path.insert(0, str(work / "parent"))
    import qualify_complex

    reference = qualify_complex.historical_checker(work / "peer")
    engine = work / "source/research/p104-dual-supplier-lift"
    sys.path.insert(0, str(engine / "complex"))
    import supplier
    import supplier_gate
    from closed_application import main_boundary, verify_caller

    parent, layout = rebuild()
    word, _ = reconstruct(parent, read("BANK-FACTORS.json.gz"))
    events = read("BANK-FACTORS-EVENTS.json")
    moves, rows = reference.graph_inputs(parent)
    net = supplier.Network(parent["first_output"], parent["initial"], parent["final"],
                           moves, {k: dict(row) for k, row in rows.items()})
    check(canonical(parent) == events["parent"], "bank change source")
    for name in ("public_split", "bank_split"):
        check(sha256((engine / "complex" / (name + ".py")).read_bytes()).hexdigest()
              == events[name + "_sha256"], f"bank change engine {name}")
    net = supplier.replay_events(net, events["events"])
    check(canonical(supplier.dump_graph(net, parent["frames"])) == events["word"] == canonical(word),
          "bank operations and coefficient journal agree")
    check((canonical(word), canonical(layout)) == (result["rational_word"], result["rational_layout"]),
          "rational program and public addresses")
    main_boundary(word, layout)
    owners = qualify_complex.owners(layout)
    caller = supplier.read(supplier.SOURCE / "data/CALLER.json.gz")
    phases = supplier.read(supplier.SOURCE / "data/CALLER-PHASE-BASES.json")
    signed, guard, census, coefficients = verify_caller(caller, word, layout, phases)
    check(census["readback"]["event_stream_sha256"] == qualify.CALLER_PIN
          and signed["calls"] == result["rational_calls"] == 48, "complete physical caller")
    moves, rows = reference.graph_inputs(word)
    native, conversion = qualify.native_replay(reference, supplier, word, layout, owners, moves, rows, caller)
    weights = reference.invoice(native, reference.count_caller(caller))
    claim, tested, lower, upper = qualify_complex.price(reference, weights, bit)
    # The upstream application sets this supplier input from an ordinary BIT proof.
    supplier_gate.BIT_PIN = str(bit)
    app = qualify.apply_expanded(native, signed, guard, coefficients, conversion, supplier.physical,
                                 claim, tested, lower, upper, bit)
    check(app["invoice"] == {"paid": weights["P"], "targets": weights["T"]}, "complete signed rational bill")
    check(app["claim"] == result["claim"] and app["bracket"] == result["rational_raw"], "claimed endpoints")
    parent = json.loads((work / "parent/evidence/application.json").read_bytes())
    previous = qualify.checked_json(package / "evidence/application.json", qualify.E40B_APP_PIN, compressed=False)
    cases = {"tested": {"native": native, "application": app}, "original_7781": parent, "current_7786": previous}
    root = supplier.physical.root_envelope({key: case["native"] for key, case in cases.items()}, guard)
    depth = {key: supplier.physical.check_depth_guard(root, int(case["application"]["compiler"]["H"]))
             for key, case in cases.items()}
    check(qualify.PREMISES == result["premises"], "five inherited premises")
    return word, layout, dict(application=app, native=native, conversion=conversion, common_root=root,
                              common_depth_guards=depth, caller_census=signed, caller_proof=census,
                              caller=qualify.CALLER_PIN, compiler_controls=qualify.controls(supplier.physical),
                              target_signed_margin=list(map(str, reference.dyadic_price(weights, qualify.TARGET))))


def audit(work, package, result, bit, word, layout, proof):
    import audit_expanded as review

    reader, interval, _ = review.pinned_context(work)
    engine = work / "source/research/p104-dual-supplier-lift"
    graph = reader.Graph.parse(word)
    spans = [reader.span(frame) for frame in graph.frames]
    expected, mains = reader.public_operator(graph, layout, spans)
    grid = review.basis_grid(graph, expected, proof["native"], proof["conversion"])
    counts, plans = review.audit_plans(word, proof["conversion"]["scalar_cases"])
    fixture = review.replay_grid(graph, expected, proof["native"], plans)
    check(fixture["native_independent_wide_incidences_executed"] == 4 * counts["expanded_terms"],
          "four signed components for every wide scalar incidence")
    check((grid, counts, fixture) == (result["rational_grid"], result["plans"], result["fixture"]),
          "precision and dirty-stream audit")
    signed = review.signed_readback(reader, interval, engine, graph, layout, mains, spans, proof)
    ordinary = review.audit_ordinary(word, proof, counts, signed)
    check(ordinary == result["ordinary"], "ordinary records and selected transfers")
    review.audit_root(work, engine, word, layout, proof, package / "evidence/application.json")

    # Check the input-lift derivative independently through the new supplier cap.
    pos, neg = {7: 1, 3: 1, 5: 1}, {9: 1, 4: 1, 1: 2}
    slope = sum(Fraction(interval.log(r)[1], interval.B) * r * n for r, n in pos.items())
    slope -= sum(Fraction(interval.log(r)[0], interval.B) * r * n for r, n in neg.items())
    curvature = sum(Fraction(interval.log(r)[1], interval.B)**2 * r * n for r, n in neg.items())
    check(slope + bit * curvature < 0, "signed derivative through the admitted cap")
    gate = review.load("independent_outer", engine / "complex/supplier_gate.py", review.SUPPLIER_GATE_SHA)
    gate.BIT_PIN = str(bit)
    claim = Fraction(result["claim"])
    tested = claim + Fraction(7, 10**14)
    check(0 < claim < tested < bit <= Fraction("0.0069"), "strict ordinary headroom")
    outer = gate.gate({"T": signed["productive"], "P": signed["paid"]}, claim, tested,
                      *signed["candidate_raw_bracket"], bit)
    for key in ("H", "minimum_log_power", "written_log_power", "compiler_gap", "moment_margins", "outer"):
        check(outer[key] == proof["application"]["compiler"][key], f"independent compiler {key}")
    check(outer["outer"] == result["outer"] and outer["H"] == result["H"], "complete outer receipt")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the full physical application receipt")
    args = parser.parse_args()
    check(__debug__, "proof checks require assertions")
    result = read("APPLICATION.json")
    with TemporaryDirectory(prefix="p104-application-") as name:
        work = Path(name)
        package = source_tree(work, result)
        bit = ordinary_bit(work, package, result)
        print("PASS binary map, both literal directions, credited product and finite ordinary cap", flush=True)
        word, layout, proof = rational_application(work, package, result, bit)
        # The independent reader takes the public JSON representation of each histogram.
        proof = json.loads(json.dumps(proof))
        audit(work, package, result, bit, word, layout, proof)
        if args.out:
            args.out.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")
    print("PASS complete conditional multiplication claim", result["claim"], flush=True)


if __name__ == "__main__":
    main()
