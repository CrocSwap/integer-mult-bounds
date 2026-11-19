#!/usr/bin/env python3
"""Cold independent 680-input BIT, paired caller and finite ordinary replay."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


GOAL = "goal-e6198eb08f2d4bceae61ce995ab9d599"
RECEIPT = "progress.goal-e6198eb08f2d4bceae61ce995ab9d599.00000006"
TARGET = Fraction("0.00387981257853")
WORD = "d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d"
WORD_GZIP = "d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9"
R2_SOURCE = "c38f1881fa87f9b9e4a27e6ba8f4ce1a608a6d6ab014648bbe758d3c48a353d9"
LITERAL = "4021766d87fa791a43a78a6665c9260b7ba3772d8b2db6e9c84b6a3d51a1305c"
PRICE = "d720df6f3f7a22554e83d0c29243af3ee04fa036073404926bab7bc2f2687e1b"
CALLER = "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b"
SELECTED = "3f8add8252adb223b60418ec69351a69b6b5edfe601ec1c6b4b65cd9e2afd9b2"


def need(value, message):
    if not value:
        raise ValueError(message)


def pinned(path, expected):
    data = path.read_bytes()
    need(sha256(data).hexdigest() == expected,"pinned " + str(path))
    return data


def load(path, name, digest):
    pinned(path,digest)
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def fixed(q, precision=13):
    assert (q * (10**precision)).denominator == 1
    units = int(q*(10**precision))
    return f"{units//10**precision}.{units%10**precision:0{precision}}"


def qualification(word_path, independent_path, source_root):
    literal = load(independent_path / "literal.py","literal",LITERAL)
    prices = load(independent_path / "price.py","quotient_prices",PRICE)
    caller = json.loads(gzip.decompress(pinned(source_root / "research/paired-query-only-bit/EFREE-CALLER.json.gz",CALLER)))
    selected = json.loads(pinned(source_root / "certificates/frontier7000/CLAIM.json",SELECTED))
    raw = gzip.decompress(pinned(word_path,WORD_GZIP))
    word = json.loads(raw)
    need(literal.canonical(word) == WORD and word["public"]==680,"exact qualified binary word")
    charts = literal.Charts(word["frames"])
    need(charts.main_contacts(word["start"],word["final"]) == 111,"all main physical contacts")
    forward, ordinary_f, _ = literal.tape(word,charts)
    reverse, ordinary_r, _ = literal.tape(word,charts,adjoint=True)
    need(forward == literal.expected_rows(680,False) and reverse == literal.expected_rows(680,True),
         "680 independent input and output rows in each orientation")
    native_paid = ordinary_f["paid"]
    need(ordinary_r["paid"] == native_paid,"the independently reversed rank bill")
    native_targets = Counter(charts.leg(a,b) for a,b in zip(word["start"][222:],word["final"][222:]))
    events = Counter(row[0] for row in caller["events"])
    paid, targets = literal.paired_invoice(caller,native_paid,native_targets,events)
    ordinary = literal.ordinary(word,caller,events,paid,targets)
    need(ordinary["ordinary_records"] < 10**12 and ordinary["owned_backing"] < 10**7,"ordinary allowances")

    # Remove the single ADD of owner 411 feeding its dedicated paid leg.
    paid_fields = {field for op,field,*args in word["program"] if op=="MOVE"}
    bridge_clock, = [clock for clock,(op,field,*args) in enumerate(word["program"])
                     if op=="ADD" and args[0]==411 and field in paid_fields]
    for adjoint,expected in ((False,forward),(True,reverse)):
        damaged,_,_ = literal.tape(word,charts,adjoint=adjoint,omit=bridge_clock)
        need(literal.different(damaged,expected) == ((411,),1),"the isolated owner's sole coefficient is essential")
    try:
        literal.tape(word,charts,omit=len(word["program"])-1)
    except ValueError as err:
        need("complete private retirement" in str(err),"omitting an owned CLEAR must fail")
    else:
        raise ValueError("missing CLEAR accepted")

    bins = prices.signed_profile(targets,paid)
    margin = prices.moment(bins,TARGET)
    need(margin[0]>0,"independent signed target acceptance")
    crossing = prices.crossing(bins)
    trial = Fraction(crossing["bracket"][0]) - Fraction(1,50_000_000)
    need(trial>TARGET,"finite operating point has strictly positive target headroom")
    covered = trial - 2*prices.LOSS
    finite = prices.compiler(paid,targets,trial)
    old = Fraction(selected["admitted_BIT_saving"])
    rho = Fraction(1,250)
    grid = 10**13

    def below(envelope):
        return Fraction((envelope*grid).__floor__()-1,grid)

    one = below((1-rho)*covered + rho*old)
    two = below((1-rho)*covered + rho*one)
    admitted, stages = prices.bootstrap(old,covered,(one,two))
    need(admitted>TARGET,"two exact ordinary stages clear the binary target")
    return dict(status="PASS_BINARY_TARGET_INDEPENDENT_FINITE_ORDINARY",goal=GOAL,receipt=RECEIPT,word_sha256=WORD,
                word_gzip_sha256=WORD_GZIP,r2_source_word_sha256=R2_SOURCE,target="0.00387981257853",
                complete_paid=paid,complete_productive=targets,native_paid=native_paid,native_productive=native_targets,
                native_calls=events["LOCAL"],paid_positions=sum(paid.values()),productive_fields=sum(targets.values()),
                rank_surplus=sum(k*(targets[k]-paid[k]) for k in set(paid)|set(targets)),
                paid_route_geometries_each_direction=len(ordinary_f["routes"]),rational_frames=len(charts.frames),
                main_contacts=111,native_full_coefficients_each_orientation=680**2,caller_coefficients_each_orientation=38**2,
                owned_nonzero_forward=ordinary_f["erase_dirty"],owned_nonzero_adjoint=ordinary_r["erase_dirty"],
                peak_owned_fields=[ordinary_f["peak"],ordinary_r["peak"]],ordinary=ordinary,
                omission_controls=dict(bridge_add_clock=bridge_clock,offending_owner=411,missing_clear="private retirement"),
                signed_margin_at_target=prices.decimal_interval(margin),raw_crossing=crossing,
                finite=finite,trial_fraction=str(trial),covered_fraction=str(covered),ordinary_bootstrap=stages,
                ordinary_admitted=fixed(admitted),caller_file_sha256=CALLER,selected_claim_sha256=SELECTED,
                limitations="Conditional on the retained physical BIT, compiler, tape and owned-erasure model.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word",required=True,type=Path)
    parser.add_argument("--independent",required=True,type=Path)
    parser.add_argument("--source-root",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    cli = parser.parse_args()
    result = qualification(cli.word,cli.independent,cli.source_root)
    cli.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(result["status"],result["word_sha256"],result["raw_crossing"]["bracket"],result["ordinary_admitted"])
