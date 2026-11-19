"""Rebuild the finite P104 word and check its complete conditional application."""

import argparse
from fractions import Fraction
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from prepare_sources import sources
import rebase_pr7767 as bridge


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value):
    return sha256(canonical(value)).hexdigest()


def read(path):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def exact_edit(net, delta):
    """Apply one charged change, checking original endpoints and rational coefficients."""
    moves = net.moves.copy()
    forms = net.forms.copy()
    for token, before, after in delta["moves"]:
        require(moves.get(token) == (None if before is None else tuple(before)), f"paid preimage {token}")
        if after is None:
            del moves[token]
        else:
            moves[token] = tuple(after)
    for token, existed, kept, edits in delta["forms"]:
        require((token in forms) == existed, f"form preimage {token}")
        row = forms.get(token, {}).copy()
        for column, old, new in edits:
            require(row.get(column) == (None if old is None else Fraction(old)),
                    f"coefficient preimage {token}/{column}")
            if new is None:
                del row[column]
            else:
                value = Fraction(new)
                require(value and str(value) == new, f"noncanonical coefficient {token}/{column}")
                row[column] = value
        if kept:
            forms[token] = row
        else:
            require(not row, f"unpriced leftover terms in retired row {token}")
            del forms[token]
    result = type(net)(net.first_output, net.initial, net.final, moves, forms)
    result.schedule()
    return result


def check_omissions(network, journal, expected, journal_hash):
    """Price an actual lost output coefficient for each omitted final paid repair."""
    require(expected["graph"] == journal["final_graph"] and expected["journal_sha256"] == journal_hash,
            "omission witnesses belong to this exact word and journal")
    repairs = {token for edit in journal["ordered_edits"]
               for token, old, new in edit["delta"]["moves"] if old is None and new is not None}
    witnesses = expected["witnesses"]
    require(len(repairs) == len(witnesses) == len(journal["ordered_edits"])
            and repairs == {witness["paid_slot"] for witness in witnesses}, "omission coverage")
    require(all(not repairs.intersection(row) for token, row in network.forms.items()
                if token < network.first_output), "terminal-only use of the charged repairs")
    order = network.schedule()
    for input_role in sorted({witness["input_role"] for witness in witnesses}):
        values = {~input_role: Fraction(1)}
        for token in order:
            value = sum(scale * values[donor] for donor, scale in network.forms[token].items()
                        if donor in values)
            if value:
                values[token] = value
        for witness in witnesses:
            if witness["input_role"] == input_role:
                token = witness["paid_slot"]
                output = network.first_output + witness["output_role"]
                lost = -network.forms[output][token] * values[token]
                require(lost and str(lost) == witness["omitted_minus_qualified_coefficient"],
                        f"omission of paid repair {token} changes its cited public output")


def reconstruct(cache, out, claim):
    # The two starting graphs share the public #7756 export. Reproduce #7767 using
    # its own published verifier before applying this contribution's reversible patch.
    source = cache / "pr7767"
    spec = importlib.util.spec_from_file_location("p104_pr7767", source / "verify.py")
    pr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pr)
    donor = cache / "donor"
    sys.path.insert(0, str(donor))
    import supplier

    original = read(donor / "GRAPH.json.gz")
    require(digest(original) == pr.PARENT_GRAPH, "shared #7756 graph")
    nine = pr.apply_delta(original, read(source / "DELTA.json"))
    submitted = pr.apply_stack(nine, read(source / "STACK-DELTA.json"))
    submitted = json.loads(canonical(submitted))
    require(digest(submitted) == claim["submitted_base"]["word"], "submitted #7767 word")
    patch = read(HERE / "PR7767-TO-JOINT.json.gz")
    stage = bridge.apply(submitted, patch)
    require(canonical(bridge.apply(stage, patch, reverse=True)) == canonical(submitted),
            "reverse bridge recovers every #7767 coefficient and owner")

    public_graph, layout, network = supplier.build()
    require(digest(public_graph) == claim["public_supplier"]["word"], "released supplier word")
    retained = read(HERE / "RETAINED-EDITS.json")
    require(retained["source_graph_sha256"] == digest(public_graph), "retained edit source")
    frames = public_graph["frames"]
    for edit in retained["events"]:
        network = exact_edit(network, edit)
    from_donor = supplier.dump_graph(network, frames)
    require(canonical(stage) == canonical(from_donor), "two source paths agree on every intermediate row")
    require(digest(stage) == claim["joint_intermediate"], "ten retained edits")

    journal = read(HERE / "PAID-EDITS.json")
    require(journal["inherited_graph"] == digest(stage), "extra paid edits start at shared intermediate")
    for edit in journal["ordered_edits"]:
        if "input_graph_sha256" in edit:
            require(digest(supplier.dump_graph(network, frames)) == edit["input_graph_sha256"],
                    f"wrong source word before edit {edit['start']}")
        network = exact_edit(network, edit["delta"])
        if "output_graph_sha256" in edit:
            require(digest(supplier.dump_graph(network, frames)) == edit["output_graph_sha256"],
                    f"wrong word after edit {edit['start']}")
    candidate = supplier.dump_graph(network, frames)
    require(digest(candidate) == journal["final_graph"] == claim["candidate"]["word"], "final graph digest")
    check_omissions(network, journal, read(HERE / "evidence/omissions.json"),
                    sha256((HERE / "PAID-EDITS.json").read_bytes()).hexdigest())
    for name, value in (("public", public_graph), ("candidate", candidate)):
        (out / (name + ".json.gz")).write_bytes(gzip.compress(canonical(value), mtime=0))
    (out / "layout.json").write_bytes(canonical(layout))
    print(f"Rebuilt #7767 and the public supplier. Both paths reached {digest(stage)}.", flush=True)
    print(f"Candidate {digest(candidate)}", flush=True)


def run(name, *arguments):
    subprocess.run([sys.executable, "-I", "-B", str(HERE / name), *map(str, arguments)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True, type=Path, help="directory prepared by prepare_sources.py")
    parser.add_argument("--output", required=True, type=Path, help="directory for regenerated graphs and receipts")
    parser.add_argument("--part", choices=("build", "independent", "application", "charts-0",
                                          "charts-1", "charts-2", "all"), default="all")
    args = parser.parse_args()
    require(sys.flags.optimize == 0, "pinned supplier needs source assertions enabled")
    cache, out = args.cache.resolve(), args.output.resolve()
    require(out != cache and cache not in out.parents, "keep generated files outside the source cache")
    out.mkdir(parents=True, exist_ok=True)
    sources(cache)
    claim = read(HERE / "CLAIM.json")
    reconstruct(cache, out, claim)
    if args.part == "build":
        return
    word = claim["candidate"]["word"]
    candidate = out / "candidate.json.gz"
    if args.part in ("all", "independent"):
        run("verify_rows.py", out / "public.json.gz", candidate, out / "layout.json",
            "--candidate-sha256", word, "--output", out / "rows.json")
        run("verify_price.py", "--donor-dir", cache / "donor", "--price-oracle",
            cache / "upstream/scripts/evaluate_recursive_power.py", "--predecessor", out / "public.json.gz",
            "--candidate", candidate, "--candidate-sha", word, "--output", out / "prices.json")
        independent = read(out / "prices.json")["candidate"]
        require(independent["raw_bracket"] == claim["candidate"]["crossing"]
                and independent["claim_candidate"] == claim["candidate"]["lower"],
                "independent complete signed price matches claim")
    if args.part == "independent":
        return
    extra = []
    status = "passed"
    if args.part == "application":
        extra = ["--application-only"]
        status = "application_passed"
    elif args.part.startswith("charts-"):
        extra = ["--chart-shard", args.part[-1]]
        status = "chart_shard_passed"
    receipt = out / (args.part + "-qualification.json")
    run("qualification.py", "--donor", cache / "donor", "--repo", cache / "upstream",
        "--graph", candidate, "--graph-sha256", word, "--out", receipt, *extra)
    result = read(receipt)
    require(result["status"] == status and result["strict_candidate_gain"]
            and result["price"]["candidate"]["claim"] == claim["candidate"]["lower"]
            and result["price"]["candidate"]["bracket"] == claim["candidate"]["crossing"]
            and result["price"]["donor"]["bracket"] == claim["public_supplier"]["crossing"],
            "complete joint word, common BIT and both directed crossings")
    print(f"Passed {args.part} at conditional κ ≥ {claim['candidate']['lower']}.", flush=True)


if __name__ == "__main__":
    main()
