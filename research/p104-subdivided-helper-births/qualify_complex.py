"""Qualify the complex application with a completed ordinary BIT supplier.

The pinned PR 7776 scalar, caller, chart and compiler engines are used unchanged.
PR 7774 supplies its independent directed-root and exact product-grid routines.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys

BASE_NATIVE = "934b7d4d792a5771bbcd28053d7797a9938f6b23faddaafe46451158eec81849"
BASE_LAYOUT = "d233f9ba1fc39c4be51685a45da1940fe43dc3a3fd7699a8b27339e1e063b489"
BINARY_WORD = "861f5181e4f34db638ab0c573c319fe26ff034d63b21242d67220a4a5d6433ff"
BASE_UPPER = "0.00385896184248"
GOAL = "0.00386380485468"
TICKS = 10**14
HERE = Path(__file__).resolve().parent


def need(ok, text):
    if not ok:
        raise ValueError(text)


def json_file(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


def digest(item):
    return sha256(json.dumps(item, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def historical_checker(path):
    spec = importlib.util.spec_from_file_location("p7774_product_grid", path / "qualification.py")
    need(spec and spec.loader, "PR 7774 product-grid and directed-root source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def histogram(rows):
    return {int(rank): count for rank, count in rows.items()}


def tick(n):
    return f"{n // TICKS}.{n % TICKS:014d}"


def price(program, weights, bit_cap):
    def signed(i):
        return program.dyadic_price(weights, tick(i))

    left, right = 1, 690000000000
    need(signed(left)[0] > 0 and signed(right)[1] < 0, "bracket endpoints")
    while right - left > 1:
        mid = (left + right) // 2
        lo, hi = signed(mid)
        if lo > 0:
            left = mid
        else:
            need(hi < 0, "directed root sign")
            right = mid
    k = min(left, int(bit_cap * TICKS)) - 8
    need(signed(k + 7)[0] > 0 and k > 0, "finite slack")
    return tick(k), tick(k + 7), tick(left), tick(right)


def owners(layout):
    h = layout["hosted"]
    main = set(layout["live"]) | {r + 112 for r in layout["live"]} | set(h["X2"]) | set(h["Y2"])
    need(len(main) == 400 and len(set(layout["source_labels"])) == layout["public"], "independent owners")
    return main, set(h["Dports"]), list(zip(h["X2"], h["Y2"], strict=True))


def command(args):
    need(__debug__, "run with Python assertions enabled")
    reference = historical_checker(args.peer.resolve())
    supplier_dir = args.supplier.resolve() / "complex"
    sys.path.insert(0, str(supplier_dir))
    import supplier
    import supplier_gate
    from closed_application import apply, main_boundary, verify_caller

    base, layout = (json_file(args.base_graph), json_file(args.base_layout)) if args.base_graph else supplier.build()[:2]
    need(digest(base) == BASE_NATIVE and digest(layout) == BASE_LAYOUT, "exact published base")
    graph = json_file(args.candidate) if args.candidate else base
    candidate_layout = json_file(args.layout) if args.layout else layout
    if args.candidate:
        need(digest(graph) == args.sha, "canonical candidate pin")
    for key in ("ports", "live", "hosted"):
        need(layout[key] == candidate_layout[key], "same native main bindings")
    main_boundary(graph, candidate_layout)
    role_sets = owners(candidate_layout)
    caller = supplier.read(supplier.SOURCE / "data/CALLER.json.gz")
    moves, rows = reference.graph_inputs(graph)
    if args.chart is not None:
        sys.path.insert(0, str(args.upstream.resolve() / "research/shared-wire-split-composition/frozen"))
        import catalogue
        from network import Network
        net = Network(graph["first_output"], graph["initial"], graph["final"], moves, {i:dict(row) for i,row in rows.items()})
        catalogue.build = lambda: (graph, candidate_layout, net)
        result = catalogue.verify(args.chart)
        if digest(graph) == BASE_NATIVE:
            need(result == json_file(supplier_dir / f"CHARTS-{args.chart}.json"), "published physical charts")
        return {"native_sha256":digest(graph), "charts":result}
    need(args.binary_finite, "supply the completed binary finite certificate")
    bits = json_file(args.binary_finite)
    bit_cap = Fraction(bits["ordinary_admitted"])
    need(bits["word_sha256"] == BINARY_WORD and Fraction(BASE_UPPER) < bit_cap < Fraction("0.0069"),
         "completed ordinary BIT receipt and its frozen native")
    native = supplier.physical.graph_bounds(graph, moves, rows, role_sets[0])
    fixed = reference.count_caller(caller)
    weights = reference.invoice(native, fixed)
    claim, tested, lo, hi = price(reference, weights, bit_cap)
    need(Fraction(claim) > Fraction(BASE_UPPER), "candidate below conservative joint comparator")
    print("directed complex crossing",lo,hi,"finite claim",claim,flush=True)
    signed, guard, proof, coefficients = verify_caller(caller, graph, candidate_layout, supplier.read(supplier.SOURCE / "data/CALLER-PHASE-BASES.json"))
    need(histogram(signed["fixed_root_targets"]) == dict(fixed[0]) and
         histogram(signed["fixed_caller_paid"]) == dict(fixed[1]) and signed["calls"] == 48,
         "regenerated signed caller")
    conversion = reference.native_replay(supplier, graph, candidate_layout, role_sets, moves, rows, native, caller)
    # The retained gate's old public BIT ceiling is the only input replaced.
    # Read the new ceiling from the completed finite ordinary construction.
    old_cap = supplier_gate.BIT_PIN
    try:
        supplier_gate.BIT_PIN = str(bit_cap)
        application = apply(native,signed,guard,coefficients,conversion,supplier.physical,claim,tested,lo,hi,bit_cap)
    finally:
        supplier_gate.BIT_PIN = old_cap
    need(application["invoice"] == {"paid":weights["P"],"targets":weights["T"]}, "physical signed invoice")
    base_data = json_file(supplier_dir / "RESULT.json")
    common = supplier.physical.root_envelope({"candidate":native,"comparator":base_data["native"]},guard)
    guards = {key:supplier.physical.check_depth_guard(common,int(app["compiler"]["H"]))
              for key,app in (("candidate",application),("comparator",base_data["application"]))}
    return {"schema":"p104-subdivided-joint-application/v1", "native_sha256":digest(graph),
            "layout_sha256":digest(candidate_layout),"binary_word_sha256":BINARY_WORD,
            "ordinary_binary":str(bit_cap),"finite_lower":claim,"complex_crossing":[lo,hi],
            "comparator_joint_upper":BASE_UPPER,"target":GOAL,
            "gain_above_upper":str(Fraction(claim)-Fraction(BASE_UPPER)),
            "remaining_to_target":str(max(Fraction(0),Fraction(GOAL)-Fraction(claim))),
            "native":native,"conversion":conversion,"caller":signed,"caller_proof":proof,
            "caller_guard":guard,"application":application,"common_root":common,"joint_depth_guards":guards}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("upstream","supplier","peer","out"):
        parser.add_argument("--"+name,type=Path,required=True)
    for name in ("base-graph","base-layout","candidate","layout","binary-finite"):
        parser.add_argument("--"+name,type=Path)
    parser.add_argument("--sha")
    parser.add_argument("--chart",type=int,choices=(0,1,2))
    args = parser.parse_args()
    need(bool(args.base_graph)==bool(args.base_layout) and bool(args.candidate)==bool(args.sha), "paired pins")
    result = command(args)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("PASS", result.get("finite_lower", "physical chart shard"))

