# SPDX-License-Identifier: Apache-2.0
"""Check the fixed normalized proof, saved physical data and original signed supplier gate."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys
from tarfile import open as open_tar
from tempfile import TemporaryDirectory


def check(truth, label):
    if not truth:
        raise ValueError(label)


def digest(data):
    return sha256(data).hexdigest()


def unique(items):
    result = dict(items)
    check(len(result) == len(items), "repeated JSON key")
    return result


def read(path, expected):
    data = path.read_bytes()
    check(digest(data) == expected, path.name + " digest")
    return json.loads(data, object_pairs_hook=unique)


def load_run(root, receipt):
    result = read(root / "REPLAY.json", receipt)
    files = result["output_sha256"]
    return (result, *(read(root / name, files[name]) for name in
                      ("BINARY.json", "PHYSICAL.json", "APPLICATION.json")))


def differences(first, second):
    return sorted(k for k in first.keys() | second.keys() if first.get(k) != second.get(k))


def require_rejection(operation):
    try:
        operation()
    except (AssertionError, ValueError):
        return
    raise ValueError("expected gate rejection")


def verify(args):
    base = read(args.peer / "APPLICATION.json", "587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f")
    bank = read(args.peer / "BANK-FACTORS-RECEIPT.json", "bdb3052152bdd15ae36c30c98877dcebf864fc2c58a7b1fa66f2d5affa149288")
    census = read(args.peer / "CALLER-CENSUS.json", "6a685bdc50aeba01a79fa437490190568513d62e0765844e7f3e8fa29a913e16")
    prior_digest = "419d4bdfb95c4484d0ddc81f34c89ee45bdefc0955a85dd496c1043396260e37"
    new_digest = "9b00a17913efb76995b01c7b75f5b00aab394a0531e26490ab02a5940adcac3c"
    prior, prior_bit, old_physical, old_app = load_run(args.prior_run, prior_digest)
    final, bit, physical, app = load_run(args.run, new_digest)
    primary = read(args.primary, "ef3f829625b03c09f1cdff2440ef92b9869b4cb4d0821bf9c0fd5910c9d6ad3c")
    indep = read(args.independent, "523d6dc93a7cd34bf6183a66d03b624ab2f0dfcf18b7e95032b7d0ab695fa24f")
    check(final["prior_receipt_sha256"] == prior_digest and final["peer_head"] == prior["peer_head"], "previous supplier")
    check(bit["peer_finite"] == prior_bit["peer_finite"] and
          bit["prior_binary_sha256"] == prior["output_sha256"]["BINARY.json"], "actual stock and original 36 calls")
    check(differences(app, old_app) == differences(app, base) == ["binary_ordinary", "claim"], "physical application invariant")
    check(differences(physical, old_physical) == ["application"] and
          differences(physical["application"], old_physical["application"]) == ["claim", "compiler"], "exact physical change scope")
    case = indep["case"]
    H, h, p, J = (case[k] for k in ("H", "h", "p", "J"))
    check((H,h,p,J) == (299610000000000,1024,623,23731) and
          h**p * 2**(J-1) <= (h+H)**p < h**p * 2**J and
          (h+H)*J > 2*H*p and 15**43 < 16**42 and
          2**h * 15**(768*43) <= 134**(768*42) and
          Q(42,43)**p < Q(indep["eta_lower"]), "all-height uniform bounds and adjacent failed J")
    loss = Q(J, H)
    cover = Q(1, H*2**38)
    covered = Q(case["C"])-loss-cover
    check(Q(bit["uniform_loss"]) == Q(primary["uniform_loss"]) == Q(indep["uniform_loss"]) == loss and
          Q(bit["delayed_cover_debit"]) == Q(prior_bit["delayed_cover_debit"]) == cover and
          Q(bit["covered"]) == Q(indep["covered"]) == covered, "charged uniform + inherited cover")
    previous = Q("0.00385248")
    slacks = []
    check(len(bit["candidate_stages"]) == 4, "four stock stages")
    for emitted, separate in zip(bit["candidate_stages"], indep["new_stages"], strict=True):
        envelope = (249*covered + previous)/250
        cap = Q((envelope*10**15)//1 - 1, 10**15)
        slack = min(envelope-cap,Q(1,250)-cap,Q(249,250)-cap)
        check(previous == Q(emitted["previous"]) == Q(separate["previous"]) and cap == Q(emitted["claim"]) == Q(separate["cap"]) and
              Q(separate["bound"]) == envelope and Q(separate["slack"]) == slack > 0, "literal ordinary stage")
        slacks.append(slack)
        previous = cap
    check(cap == Q(app["binary_ordinary"]) == Q(bit["admitted"]) == Q(primary["candidate"]["cap"]) == Q(indep["cap"]), "complete BIT")
    native = physical["native"]
    actual = physical["application"]
    check(all(physical["caller_census"][k] == census[k] for k in census) and census["calls"] == 48 and
          physical["caller"] == physical["caller_proof"]["readback"]["event_stream_sha256"] == final["caller"] and
          app["binary_native"]["calls"] == 36, "caller chronology and population")
    check(native["retired_and_guards_restored"] and native["all_public_inputs_preserved_until_final_installs"] and
          native["same_owner_complete_fixture_outputs"] == native["exact_source_columns"] == native["exact_all_public_rows"] == bank["public"], "ownership and recovery")
    invoice = {}
    for key, local, caller, reference, emitted in (
        ("T","positive_helper_ranks","fixed_root_targets","productive","targets"),
        ("P","paid_native_ranks","fixed_caller_paid","paid","paid"),
    ):
        tally = Counter({r:n*census["calls"] for r,n in native[local].items()})
        tally.update(census[caller])
        check(dict(tally) == bank[reference] == actual["invoice"][emitted], "reconstructed "+key)
        invoice[key] = dict(tally)
    archive = args.peer / "APPLICATION-SOURCES.tar.gz"
    check(digest(archive.read_bytes()) == base["source_archive"], "original source bundle")
    with open_tar(archive) as packed:
        source = packed.extractfile("source/research/p104-dual-supplier-lift/complex/supplier_gate.py").read()
    check(digest(source) == "3796b2e5a27f3caa142d16364154788e60d0099f1e24a8dcd028e4fbd35a84ca", "original gate")
    with TemporaryDirectory() as work:
        gate_file = Path(work)/"gate.py"
        gate_file.write_bytes(source)
        gate = runpy.run_path(str(gate_file))["gate"]
    tick = Q(1,10**14)
    def signed(summary, weights, admission):
        claim = Q(summary["claim"])
        gate.__globals__["BIT_PIN"] = str(Q(summary["binary_ordinary"]))
        return gate(weights,claim,claim+7*tick,*summary["rational_raw"],admission)
    for summary in (base,old_app,app):
        g = signed(summary,invoice,Q(summary["binary_ordinary"]))
        check(g["outer"] == summary["outer"] and g["H"] == summary["H"], "historical and current signed gates")
    check(g == actual["compiler"] and g["outer"]["strict_count"] == 54 and g["outer"]["functional_count"] == 4, "complete signed receipt")
    claim, tested = Q(app["claim"]), Q(final["tested"])
    check(claim == Q(indep["claim"]) == Q(primary["candidate"]["claim"]) and tested == claim+7*tick < cap, "signed endpoints")
    damaged = {"T":invoice["T"], "P":dict(invoice["P"])}
    damaged["P"]["1"] += 1
    require_rejection(lambda: signed(app,damaged,cap))
    require_rejection(lambda: signed(app,invoice,tested))
    gain = claim - Q(old_app["claim"])
    peer_gain = claim - Q(base["claim"])
    gap = claim - (Q(base["binary_raw"][1]) - Q(1,10**10))
    check(gain == Q(final["difference"]) == Q(indep["gap_vs_old"]) and gap == Q(indep["separation"]) > Q(1,10**11), "strict prior ceiling")
    return dict(outcome="PASS_COMPLETE_INDEPENDENT_NORMALIZED_ACCEPTANCE",peer_head=final["peer_head"],prior_replay_sha256=prior_digest,
                replay_sha256=new_digest,outputs=final["output_sha256"],invoice=invoice,caller=physical["caller"],native_calls=[36,48],
                cap=final["cap"],claim=app["claim"],tested=final["tested"],gain_vs_previous=str(gain),percent_vs_previous=str(100*gain/Q(old_app["claim"])),
                gain_vs_peer=str(peer_gain),percent_vs_peer=str(100*peer_gain/Q(base["claim"])),previous_ceiling_separation=str(gap),
                minimum_ordinary_slack=str(min(slacks)),outer=g["outer"],known_good=["8027","R347"],rejections=["J_minus_one","extra_paid_rank_one","cap_equals_tested"],
                premises=app["premises"])


if __name__ == "__main__":
    check(sys.version_info[:2] == (3,12) and __debug__, "CPython 3.12 with assertions")
    parser = ArgumentParser()
    for key in ("peer","prior-run","run","primary","independent","out"):
        parser.add_argument("--"+key,type=Path,required=True)
    opts = parser.parse_args()
    result = verify(opts)
    with opts.out.open("x") as stream:
        json.dump(result,stream,sort_keys=True,indent=2)
        stream.write("\n")
    print(result["outcome"],result["claim"],result["gain_vs_previous"])
