# SPDX-License-Identifier: Apache-2.0
"""Rebuild the unchanged #8027 supplier and apply a certified delayed-cover debit."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

HEAD = "fb9b6a7b0d27da1cf98430893a3016bf811e2aa4"
PRIMARY = "228b7c47572c9b1c7568db2f59248af454296a1e3ad094da585073bbd594f5cb"
INDEPENDENT = "5c723ea9c6b085b6e0aa792f34cfa64daed551a9bf2f629efc54d219008596d2"
BRIDGE = "9731b93026717f5fa15851e3633cbb4bdc76eba2bffb9d6b4a3b69f7dd502443"
PEER_FILES = {
    "APPLICATION-SOURCES.tar.gz": "d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968",
    "APPLICATION.json": "587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f",
    "AUDIT.json": "91c998e6f651f06435cde50f1f731867528fbce0a48db3de32e8b6f0f39bd824",
    "BANK-FACTORS-EVENTS.json": "7ecfb07e694204802f603cb620689a81b353a4fcb4b41bf10cc08dd5459fff0f",
    "BANK-FACTORS-RECEIPT.json": "bdb3052152bdd15ae36c30c98877dcebf864fc2c58a7b1fa66f2d5affa149288",
    "BANK-FACTORS.json.gz": "b009cd6bb13036879214cb6d43beb923578ef7fb4c83f36a1cc971ab4ea23543",
    "BIDIRECTIONAL-QUOTIENT-RECEIPT.json": "459f519593242a3e8ecf42817f178fb214a6833e0df0e1ce727c5809035d02de",
    "BIDIRECTIONAL-QUOTIENT.json.gz": "ed725d5c69a507352efc6a18f3e4f7e5c20592a655a7b80193034232feb43d6f",
    "BIDIRECTIONAL-RECEIPT.json": "e17c36ad4cd9e317fa56812e8d23a6b5dcf50e24389ea7ee59a6aff6d15fd541",
    "BIDIRECTIONAL.json.gz": "baf07c7085f588ce06201e2a6bf4f5f58632801202783ca195d3b8369ff74836",
    "BIDIRECTIONAL.md": "40ee0492d911f0d290557133ddc99e9c6d576c2f872186122631b53311920c99",
    "BINARY-CANDIDATE.json.gz": "74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326",
    "CALLER-CENSUS.json": "6a685bdc50aeba01a79fa437490190568513d62e0765844e7f3e8fa29a913e16",
    "EVENTS.json": "544840ed2aa50dc16788708c6828fedb667e0c129edd3e3aac09652a056e7b6e",
    "HELPER-SPLITS-RECEIPT.json": "712b783baf1463b738bd5c5ad3023bf42681d7d0105dd550ba3549c02674f711",
    "HELPER-SPLITS.json": "f70ba89a9ed5839476bbe298d4cb8f4d9eeb703621d5f478c884861cdd91fb20",
    "LAYOUT.json.gz": "84cd1d11ff454eecf3504e4b3f26adc371539b17553bfce1bcfda7a331811998",
    "LICENSE": "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
    "PARENT-NOTICE": "b213998c8dae6d88e4a1f0fd17c81dd78c31ef35bc9460fa16ca692326f1a02b",
    "RATIONAL-RECEIPT.json": "603358c1bc198d689dedb4b591a684170be41ac7b242a50ebd5a12a05ec5c97a",
    "README.md": "a12df934c00eacd04464847ceac920e7b860b79446f87aa81ab3ae2c50750e1f",
    "SOURCES.json": "4dd42ee240925ae1bc1ffa3b885b33eb66ab4d323695d106c00ce7519dffd9bb",
    "TASK.json": "258b6f9f7f5e6eb831d785cfa8d5ad14ff7623a078ab8ce5f99dd142000f0443",
    "VERIFY.json": "58bbce9050ae72c7bdb1460e88c033e33988a39fec00935673f79c74394cabd0",
    "WORD.json.gz": "731246c085638706bdb97e7e88618f8923e27ee4ce8eb4869f0847f8f4699f7c",
    "replay.py": "9c847a1242e730acf1dfd3a83f4801470e3e2da6c3079f53ccb7ada620b37a7b",
    "verify_application.py": "f774304804e705ac576459cca725b348f09e67e6020fe6165df9b7d39c605c54",
    "verify_bidirectional.py": "ef85db5c6f348b55e0db4d61517dde6a58b027737037e14b9fdea04f8b96e716",
    "verify_component.py": "163b1ca3a35531da94ef454229f040592c754675f59dfb805d0a9aadb33b8d65",
    "verify_split_helpers.py": "6a0b59657bd1902d19b9c0f8badef2caa13c8ba84e0311550d6391360bdf186b",
}


def check(value, label):
    if not value:
        raise ValueError(label)


def locked(path, expected):
    data = path.read_bytes()
    check(sha256(data).hexdigest() == expected, "content hash for "+path.name)
    return data


def save(path, data):
    path.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")


def normalize(obj):
    return json.loads(json.dumps(obj))


def gate_cap(proposed, certified):
    check(Q(proposed) == Q(certified), "unproved ordinary cap")


def stages(old, proposed, independent, initial, covered):
    rho = Q(1,250)
    check(len(proposed) == len(independent) == 4, "four original stage services")
    last = initial
    for left,right in zip(proposed,independent,strict=True):
        upper = (1-rho)*covered+rho*last
        new = Q((upper*10**15).__floor__()-1,10**15)
        margin = min(upper-new,rho-new,1-rho-new)
        check(last == Q(left["previous"]) == Q(right["old"])
              and upper == Q(left["endpoint"]) == Q(right["bound"])
              and new == Q(left["admitted"]) == Q(right["new"])
              and margin == Q(left["charged_minimum_slack"]) == Q(right["margin"])
              and last < new < upper < rho < 1-upper, "reconstructed charged stage")
        last = new
    check(last == Q(old), "admitted ordinary cap")
    return last


def certify(primary, independent, peer_result):
    c, old = primary["candidate"], primary["comparator"]
    check(primary["decision"] == "ADVANCE_ONE_COMPLETE_SIGNED_REPLAY" and old["head"] == HEAD,
          "positive fixed-case component")
    check(independent["bridge_sha256"] == BRIDGE, "certified cover theorem")
    H = int(peer_result["binary_H"])
    gap = Q(1,10**10)
    debit = Q(1,H*2**38)
    check(H == int(old["H"]) == int(independent["H"]) == 299610000000000
          and Q(c["cover_loss"]) == Q(independent["delayed_cover_loss"]) == debit
          and Q(c["uniform_loss"]) == Q(independent["uniform_loss"]) == Q(old["uniform_loss"]) == gap,
          "fixed carrier and uniform loss; new cover only")
    # The source theorem bounds the old full fallback strictly below 2^-39;
    # (2^H)^debit > 1 + H*debit/2 by exp(x)>1+x and log(2)>1/2.
    surcharge = Q(1,2**39)
    check(Q(c["surcharge_strict_upper"]) == Q(independent["surcharge_upper_strict"]) == surcharge
          and Q(c["N_to_d_strictly_above"]) == 1+surcharge
          and Q(independent["power_growth_lower_strict"]) == H*debit/2 == surcharge, "delayed cover")
    trial = Q(old["trial"])
    seed = Q(old["seed"])
    check(trial == Q(independent["trial"]) == Q(peer_result["binary_raw"][0])-Q(1,10**11)
          and seed == Q("0.00385248") and Q(old["old_cover_loss"]) == gap, "unchanged trial and seed")
    current = Q(old["cap"])
    check(current == Q(independent["old_cap"]) == Q(peer_result["binary_ordinary"])
          and Q(old["claim"]) == Q(independent["old_claim"]) == Q(peer_result["claim"]), "known-good peer cap")
    stages(current,old["stages"],independent["old_rows"],seed,trial-2*gap)
    covered = trial-gap-debit
    check(covered == Q(c["covered"]), "full changed cost")
    cap = stages(c["cap"],c["stages"],independent["new_rows"],seed,covered)
    gate_cap(cap,independent["cap"])
    tick = Q(1,10**14)
    claim = (min(cap//tick,Q(peer_result["rational_raw"][0])//tick)-8)*tick
    tested = claim+7*tick
    generous = Q(peer_result["binary_raw"][1])-2*gap
    check(claim == Q(c["claim"]) == Q(independent["candidate"]) and tested == Q(c["tested"]) == Q(independent["tested"])
          and Q(peer_result["claim"]) < generous == Q(independent["relaxed_old_ceiling"]) < claim < tested < cap
          and claim-generous == Q(independent["separation"]), "directed old separation and tested grid")
    try:
        gate_cap(cap+tick,independent["cap"])
    except ValueError as error:
        check(str(error) == "unproved ordinary cap","cap control reason")
    else:
        raise ValueError("unsafe extra cap accepted")
    return cap


def peer_copy(peer, supplied):
    peer.mkdir()
    for name, expected in PEER_FILES.items():
        (peer/name).write_bytes(locked(supplied/name,expected))
    spec = importlib.util.spec_from_file_location("registered_peer_8027",peer/"verify_application.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def binary(peer, work, package, baseline, component):
    # Repeat verify_application.ordinary_bit's literal entry points and retain the
    # actual finite proof, including the selected atom and ordinary service ledger.
    parent,source = work/"parent",work/"source"
    finite = peer.module("finite_bit",package/"binary/finite.py")
    for root,pins in ((source,finite.SOURCE_PINS),(parent,finite.PACKAGE_PINS)):
        for name,pin in pins.items():
            finite.pinned(root/name,pin)
    literal = peer.module("literal",parent/"binary/independent/literal.py")
    price = peer.module("binary_price",parent/"binary/independent/price.py")
    compiler = peer.module("credited_product",source/finite.FINITE)
    word = literal.candidate_word(parent/"binary/WORD.json.gz")
    caller = literal.pinned(source/finite.PAIRED/"EFREE-CALLER.json.gz",literal.CALLER_SHA)
    native = finite.candidate_receipt(literal,peer.HERE/"BINARY-CANDIDATE.json.gz",baseline["binary_word"],word,caller)
    seed = Q(json.loads((source/finite.CLAIM).read_bytes())["admitted_BIT_saving"])
    old = finite.ordinary_certificate(price,compiler,native,seed,None,None)
    summary = dict(public=native["public"],instructions=native["instruction_counts"],productive=native["native_targets"],
                   paid=native["native_paid"],calls=native["native_calls"],paid_all=native["paid"],
                   productive_all=native["targets"],ordinary=native["ordinary"])
    check(normalize(summary) == baseline["binary_native"] and native["native_calls"] == 36, "literal signed binary bill")
    check(old["raw_crossing"] == baseline["binary_raw"] and old["ordinary_admitted"] == baseline["binary_ordinary"]
          and old["independent_directed_compiler"]["H"] == baseline["binary_H"]
          and old["finite_product_bound_bit_lengths"] == baseline["binary_product"], "complete peer finite control")
    old_data, new_data = component["comparator"],component["candidate"]
    check(list(old_row["claim"] for old_row in old["ordinary_bootstrap"]) == [s["admitted"] for s in old_data["stages"]]
          and Q(old["tested_saving"]) == Q(old_data["trial"]) and Q(old["uniform_loss"]) == Q(old_data["uniform_loss"])
          and Q(old["delayed_cover_loss"]) == Q(old_data["old_cover_loss"]) and seed == Q(old_data["seed"]),
          "original finite ordinary bootstrap and stock control")
    admitted, bootstrap = price.bootstrap(seed,Q(new_data["covered"]),[s["admitted"] for s in new_data["stages"]])
    check(admitted == Q(new_data["cap"]), "credited bootstrap at new covered rate")
    return dict(peer_finite=old, delayed_cover_debit=new_data["cover_loss"], covered=new_data["covered"],
                candidate_stages=bootstrap, admitted=new_data["cap"])


def outer_prices(peer, work, baseline, candidate, physical):
    import audit_expanded as review
    gate_path = work/"source/research/p104-dual-supplier-lift/complex/supplier_gate.py"
    g = review.load("separate_candidate_outer",gate_path,review.SUPPLIER_GATE_SHA)
    invoice = physical["application"]["invoice"]
    weights = {"T":invoice["targets"],"P":invoice["paid"]}
    raw = baseline["rational_raw"]
    tick = Q(1,10**14)

    def gate(cap, claim):
        g.BIT_PIN = str(cap)
        return g.gate(weights,Q(claim),Q(claim)+7*tick,*raw,Q(cap))

    # Both points are computed from the new replay's immutable original 48-call bill.
    old = gate(baseline["binary_ordinary"],baseline["claim"])
    check(old["H"] == baseline["H"] and old["outer"] == baseline["outer"], "known-good signed outer control")
    result = gate(candidate["binary_ordinary"],candidate["claim"])
    check(result["outer"]["strict_count"] == 54 and result["outer"]["functional_count"] == 4,
          "new signed strict and functional checks")
    # A real extra paid unit must break the directed lower crossing sign.
    damaged = weights["P"].copy()
    damaged["1"] = damaged.get("1",0)+1
    left = Q(raw[0])
    good = g.sub(g.moment(weights["T"],left),g.moment(weights["P"],left))
    bad = g.sub(g.moment(weights["T"],left),g.moment(damaged,left))
    check(good[0] > 0 > bad[1], "one extra paid rank breaks the raw lower crossing")
    return result


def main():
    cli = ArgumentParser(description=__doc__)
    for name in ("peer-package","primary","independent","out"):
        cli.add_argument("--"+name,required=True,type=Path)
    args = cli.parse_args()
    check(sys.version_info[:2] == (3,12) and sys.implementation.name == "cpython" and __debug__,
          "requires CPython 3.12 with assertions")
    primary = json.loads(locked(args.primary,PRIMARY))
    independent = json.loads(locked(args.independent,INDEPENDENT))
    args.out.mkdir(parents=False,exist_ok=False)
    with TemporaryDirectory() as cache:
        work = Path(cache)
        peer = peer_copy(work/"peer-code",args.peer_package)
        baseline = peer.read("APPLICATION.json")
        cap = certify(primary,independent,baseline)
        package = peer.source_tree(work,baseline)
        print("PASS authenticated peer closure and both cover certificates",flush=True)
        record = binary(peer,work,package,baseline,primary)
        save(args.out/"BINARY.json",record)
        print("PASS original literal binary, peer stock, new covered bootstrap",flush=True)
        result = dict(baseline)
        result.update(binary_ordinary=primary["candidate"]["cap"],claim=primary["candidate"]["claim"])
        word,layout,proof = peer.rational_application(work,package,result,cap)
        # Both producer and independent reader consume the public JSON representation of all indices.
        proof = normalize(proof)
        check(proof["caller_proof"]["readback"]["event_stream_sha256"] == proof["caller"]
              and proof["caller_census"]["calls"] == baseline["rational_calls"] == 48, "literal paired rational caller")
        print("PASS rational word, native/converted plans, signed price and physical application",flush=True)
        outer = outer_prices(peer,work,baseline,result,proof)
        result.update(H=outer["H"],outer=outer["outer"])
        peer.audit(work,package,result,cap,word,layout,proof)
        check(result["premises"] == baseline["premises"] and len(result["premises"]) == 5
              and Q(result["claim"])-Q(baseline["claim"]) == Q(independent["gain"]),
              "complete signed gain and inherited premises")
        save(args.out/"PHYSICAL.json",proof)
        save(args.out/"APPLICATION.json",result)
        names = ("APPLICATION.json","PHYSICAL.json","BINARY.json")
        save(args.out/"REPLAY.json",dict(peer_head=HEAD,source_archive=baseline["source_archive"],
             source_count=baseline["source_count"],primary_sha256=PRIMARY,independent_sha256=INDEPENDENT,
             cap=result["binary_ordinary"],tested=independent["tested"],claim=result["claim"],
             old_claim=baseline["claim"],difference=independent["gain"],percent_gain=independent["percent_gain"],
             old_relaxed_ceiling=independent["relaxed_old_ceiling"],strict_separation=independent["separation"],
             outer=outer["outer"],caller=proof["caller"],rational_raw=result["rational_raw"],
             controls=["original_four_stage_stock_and_cap","original_outer_on_rebuilt_48_calls",
                       "tampered_cap_rejected","one_extra_rank_one_paid_rejected"],
             premises=baseline["premises"],output_sha256={n:sha256((args.out/n).read_bytes()).hexdigest() for n in names}))
        print("PASS_COMPLETE_PEER_COVER_APPLICATION",result["claim"],independent["tested"],independent["gain"],flush=True)


if __name__ == "__main__":
    main()
