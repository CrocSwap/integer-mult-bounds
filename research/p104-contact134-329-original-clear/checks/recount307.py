"""Recount exact #7642 and its single #7612 contact edit under signed #7113."""
import argparse
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import alarm

INCUMBENT = "aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916"
CANDIDATE = "dcd797e45b6d4b74411a8a73a9b6e8247bb2ea8744924332b0dd43db3e219f02"
BASE_HEAD = "d7f82810689ed2cd649ec9aaaf3b1485b585c82e"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
SOURCE_7605_PACKAGE = "research/p104-timed-helper757"
SOURCE_7642_PACKAGE = "research/p104-main46-original-clear"
PINS = {
    "7642/checks/recount_main46.py": "4b6f8b625805290d4462ce8585c79be507b318d29b6f62ab3e476b476739d5ee",
    "7642/checks/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "7642/receipts/FINAL.json": "974fadc7c8e146936f5b4d29e4a4fda3f765f16c6be57f3f0e58ee2a5e507da2",
    "7642/receipts/SIGNED.json": "baecea5ce30dc1b75411506ef5f2233edd1906e149a81b6b6a9ddea054d85dc7",
    "7605/data/invoice-new.json": "b38afd7ca590b5c4c301ee4fbe0e123f0c7220c2bd1f40c66adf208652e3ce15",
    "7605/retained/role902/bench/inputs/7113-CALLER.json":
        "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "306/PHASE.json": "c94c05f493b3fe9c437187f0c5622870ec1ed25856c0cb896e382991b0e3940c",
}
EDIT = {
    41049: (["MOVE", 134, 3, 618, False], ["MOVE", 134, 3, 373, False]),
    41050: (["MOVE", 329, 373, 618, False], None),
    41051: (["ADD", 134, 329, "-1/2", 618], ["ADD", 134, 329, "-1/2", 373]),
    41142: (["MOVE", 329, 618, 733, False], ["MOVE", 329, 373, 733, False]),
    42086: (["MOVE", 134, 618, 913, False], ["MOVE", 134, 373, 913, False]),
}


def sha(data):
    return sha256(data).hexdigest()


def operands(e):
    return e[1:3] if e[0] in ("ADD", "COPY") else e[1:2]


def normalized(tape):
    """Operations in canonical chart coordinates, where MOVE is identity."""
    return [e[:-1] if e[0] in ("ADD", "COPY", "SCALE") else e for e in tape if e[0] != "MOVE"]


def as_json(path, obj):
    with path.open("x") as stream:
        stream.write(json.dumps(obj, indent=2) + "\n")


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    for n in ("baseline", "candidate", "source-7605", "source-7642", "phase", "output"):
        parser.add_argument(f"--{n}", type=Path, required=True)
    args = parser.parse_args()
    alarm(30)
    sources = {}
    for key in PINS:
        number, subpath = key.split("/", 1)
        roots = {"7605": args.source_7605 / SOURCE_7605_PACKAGE,
                 "7642": args.source_7642 / SOURCE_7642_PACKAGE}
        sources[key] = args.phase if number == "306" else roots[number] / subpath
    inputs = {key: path.read_bytes() for key, path in sources.items()}
    assert {key: sha(blob) for key, blob in inputs.items()} == PINS
    raw = [decompress(p.read_bytes()) for p in (args.baseline, args.candidate)]
    assert list(map(sha, raw)) == [INCUMBENT, CANDIDATE]
    old, new = map(json.loads, raw)
    signed = json.loads(inputs["7642/receipts/SIGNED.json"])
    final = json.loads(inputs["7642/receipts/FINAL.json"])
    phase = json.loads(inputs["306/PHASE.json"])
    caller_pin = "7605/retained/role902/bench/inputs/7113-CALLER.json"
    caller = json.loads(inputs[caller_pin])
    assert signed["price"]["new_native"] == final["candidate_canonical_sha256"] == INCUMBENT
    assert signed["caller_sha256"] == final["caller_sha256"] == PINS[caller_pin]
    assert phase["status"] == "PASS_LITERAL_CONTACT_AND_SIGNED_PHASE"
    assert (phase["incumbent_head"],phase["incumbent_canonical_sha256"],phase["candidate_canonical_sha256"]) == (BASE_HEAD, INCUMBENT, CANDIDATE)
    tape = old["program"]
    assert all(tape[i] == row[0] for i, row in EDIT.items())
    trial = [r for i, e in enumerate(tape) if (r := EDIT.get(i,(e,e))[1]) is not None]
    assert new == {**old, "program": trial}
    basis = normalized(tape)
    assert basis == normalized(trial)
    p = old["public"]
    owned = [[e for e in w if any(r >= p for r in operands(e))] for w in (tape, trial)]
    assert owned[0] == owned[1]
    own_counts = Counter(e[0] for e in owned[0])
    assert own_counts["INIT"] == own_counts["CLEAR"] == 74 and own_counts["MOVE"] == 47
    assert old["public"] == 1501 and old["owned_fields"] == 68
    engine = run_path(str(sources["7642/checks/recount_main46.py"]))
    before, after = [engine["invoice"](w, caller) for w in (old, new)]
    d = engine["difference"]
    assert all(before[k] == after[k] for k in
               ("owned_rise", "life", "peak", "targets", "native_targets", "caller_paid",
                "caller_targets", "scalar_counts", "scalar_upper", "calls"))
    assert before["calls"] == 17 and after["life"] == 74 and after["peak"] == 50
    assert d(after["events"], before["events"]) == {"MOVE": -1}
    assert d(after["native_paid"], before["native_paid"]) == {1:-2,2:2,3:-1,4:-1,5:1}
    delta = d(after["paid"], before["paid"])
    assert delta == {int(k):v for k,v in phase["paid_delta"].items()}
    for label, short in (("paid","P"), ("targets","T")):
        assert before[label] == {int(r):n for r,n in signed["price"]["after"][short].items()}
    masses = [{k: sum(r*n for r,n in row[k].items()) for k in ("paid","targets")} for row in (before,after)]
    assert masses[0] == masses[1] and masses[0]["targets"]-masses[0]["paid"] == final["surplus"] == 1424
    populations = [sum(row["paid"].values()) for row in (before, after)]
    assert populations == [final["paid_calls"],110332] and sum(after["targets"].values()) == final["productive_calls"] == 22461
    ordinary_before = final["ordinary_bound"]
    ordinary_after = ordinary_before - 17*1000
    assert ordinary_after == 782668204 < 10**9
    pricing = run_path(str(sources["7642/checks/pricing.py"]))
    floor = Fraction(final["raw_crossing"][1]) + Fraction(1,10**8)
    signed_margins = []
    for row in (before, after):
        profile = row["targets"].copy()
        profile.subtract(row["paid"])
        signed_margins.append(pricing["cost"](profile, floor))
    assert signed_margins[0][1] < 0 < signed_margins[1][0]

    schema = json.loads(inputs["7605/data/invoice-new.json"])
    packet = {k: schema[k] for k in ("schema", "contract")}
    paths = {"before": args.output/"invoice-old.json", "after": args.output/"invoice-new.json"}
    for side, row in (("before",before),("after",after)):
        rec = {**packet, **{name: dict(sorted(row[name].items())) for name in ("paid","targets")}}
        as_json(paths[side], rec)
    as_json(args.output/"RECOUNT.json", {
        "status":"PASS_COMPLETE_LITERAL_INVOICE_NO_FULL_APPLICATION",
        "canonical_word_pins":{"old":INCUMBENT,"new":CANDIDATE},"input_pins":PINS,
        "benchmark_head":BASE_HEAD,"caller_head":CALLER_HEAD,"native_calls":17,
        "paid_delta":delta,"old_paid":before["paid"],"new_paid":after["paid"],
        "old_targets":before["targets"],"new_targets":after["targets"],
        "native_old_paid":before["native_paid"],"native_new_paid":after["native_paid"],
        "native_targets":after["native_targets"],"static_caller_paid":after["caller_paid"],
        "static_caller_targets":after["caller_targets"],"paid_counts":populations,"target_count":22461,
        "rank_masses":masses,"surplus":1424,"normalised_identical_operations":len(basis),
        "owned_event_counts":own_counts,"owned_peak":50,"public_endpoints_inherited":1501,
        "owned_clear_rows_inherited_by_identical_normalized_equations":74,
        "ordinary_baseline":ordinary_before,"ordinary_projected":ordinary_after,
        "ordinary_move_delta":-17000,"same_scalar_charge":after["scalar_upper"],
        "old_raw_crossing":final["raw_crossing"],"test_floor":str(floor),
        "directed_signed_moments":[list(map(str,i)) for i in signed_margins],
        "invoices_sha256":{side:sha(path.read_bytes()) for side,path in paths.items()},
        "pending":["full native/signed replay","precision/tape and compiler/outer gate at new claim"],
    })
    alarm(0)
    print("PASS_COMPLETE_LITERAL_INVOICE_NO_FULL_APPLICATION")


if __name__ == "__main__":
    main()
