"""Run both original application gates at the prices of the two-word cycle."""

from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_bytes())


def module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    item = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(item)
    return item


def rank_interval(rank, scale):
    """Enclose scale times rank^(249/250) with integer powers."""
    target = scale**250 * rank**249
    low, high = 0, scale*rank+1
    while high-low > 1:
        mid = (low+high)//2
        if mid**250 <= target:
            low = mid
        else:
            high = mid
    return low, low + (low**250 != target)


def deficit(paid, targets):
    scale = 10**10
    low, high = 0, 0
    for histogram, sign in ((paid, 1), (targets, -1)):
        for rank, count in histogram.items():
            left, right = rank_interval(int(rank), scale)
            if sign < 0:
                left, right = -right, -left
            low += count*left
            high += count*right
    return Q(low, scale), Q(high, scale)


def homogeneous_separator(receipt):
    saving = Q(1, 258)
    exponent = 1-saving
    scale = 10**12
    intervals = {}
    with localcontext() as context:
        context.prec = 60
        for key in receipt["targets"].keys() | receipt["paid"].keys():
            rank = int(key)
            hint = int(scale*Decimal(rank)**(Decimal(exponent.numerator)/exponent.denominator))
            left, right = hint-1, hint+2
            target = scale**exponent.denominator * rank**exponent.numerator
            need(0 <= left and left**exponent.denominator < target < right**exponent.denominator,
                 "integer-power separation certificate")
            intervals[key] = (left, right)
    lower = (sum(n*intervals[r][0] for r,n in receipt["paid"].items())
             - sum(n*intervals[r][1] for r,n in receipt["targets"].items()))
    upper = (sum(n*intervals[r][1] for r,n in receipt["paid"].items())
             - sum(n*intervals[r][0] for r,n in receipt["targets"].items()))
    need(lower > 0, "homogeneous signed deficit")
    return saving, Q(lower,scale), Q(upper,scale)


def gate_at(backend, invoice, archived, price):
    result = backend.gate(invoice, archived["claim"], archived["tested"],
                          *archived["raw_bracket"], bit_pin=price)
    for key in ("claim", "tested", "raw_bracket", "H", "moment_margins", "outer"):
        need(result[key] == archived[key], f"changed caller evidence: {key}")
    need(Q(result["BIT_pin"]) == price and Q(result["BIT_margin"]) > 0, "service pin")
    need(result["outer"]["strict_count"] == 54 and result["outer"]["functional_count"] == 4,
         "incomplete outer gate")
    return {"kappa": result["claim"], "BIT_margin": result["BIT_margin"],
            "outer": result["outer"], "H": result["H"]}


def compute():
    need(__debug__, "the two retained gates require enabled assertions")
    sources = read(HERE/"SOURCES.json")
    for item in sources["replay_inputs"]:
        path = ROOT/item["file"]
        contents = path.read_bytes()
        if item.get("gzip_copy"):
            contents = gzip.decompress(contents)
        need(sha256(contents).hexdigest() == item["sha256"], f"source bytes changed: {path.name}")

    selected = read(ROOT/"certificates/frontier7000/CLAIM.json")
    raw_a = read(ROOT/"research/paired-query-only-bit/EFREE-RESULT.json")
    repair = read(ROOT/"docs/research/pr-intake-evidence/pr7000-admission/bit-ambient.log")
    native_a = read(ROOT/"research/shared-wire-split-composition/FULL-RESULT.json")
    pending = read(HERE/"retained/pending-bit.json")
    primary = read(HERE/"retained/pending-primary.json")
    native_b = json.loads(gzip.decompress((HERE/"retained/pending-application.json.gz").read_bytes()))
    need(pending["word_sha256"] == native_b["binary_word"], "pending BIT source")
    need(repair["H"] == 296630000000000 and repair["corrected_log_power"] == 617,
         "selected corrected compiler")
    need(selected["uniform_templates"][1]["rank_encoding"] == f"2^{repair['H']}",
         "different selected template")
    need(pending["finite"]["H"] == 298610000000000, "pending independent template")
    a, b = Q(selected["covered_BIT_saving"]), Q(pending["covered_fraction"])
    need(a == Q(raw_a["covered_saving"]) and b == Q(".003879907846154"), "covered source")
    primary_price = Q(primary["covered"])
    need(primary["word_sha256"] == pending["word_sha256"] and
         primary["targets"] == pending["complete_productive"] and
         primary["paid"] == pending["complete_paid"], "primary signed word")
    need(Q(primary["ordinary_admitted"]) == Q(native_b["binary_ordinary"]) < primary_price,
         "actual ordinary price of the pending multiplier")
    loss = Q(primary["delayed_cover_loss"])
    independent = pending["finite"]
    sharper = primary["independent_directed_compiler"]
    need(loss == Q(primary["uniform_loss"]) == Q(1, 10**10), "two finite compiler losses")
    for profile, covered in ((independent, b), (sharper, primary_price)):
        need(Q(profile["trial"])-2*loss == covered and Q(profile["normalized_separation_slack"][0]) > 0,
             "source finite certification at the stated trial")
        need((profile["ambient_base"],profile["product_exponent"],profile["cutoff"],profile["productive_floor"])
             == (134,768,15,16), "paid compiler, ambient and productive floor")
        need(profile["H"]*loss == 29861 and 1+Q(64,2**45) < 2, "full good plus bad moment")
    need(primary["uniform"]["H"] == sharper["H"] and
         Q(primary["uniform"]["uniform_saving"]) == primary_price+loss, "primary uniform certificate")
    r, s = Q(99, 100), Q(1, 250)
    need(0 < b < primary_price < min(s, 1-s), "full fixed-block service guards")
    # The frozen cover also has slack for a finite predecessor comparison.
    raised_test = primary_price + loss/2
    need(primary["uniform"]["H"]*(loss/2) > 1 and 1+Q(64,2**45) < 2,
         "same cover at half its exponent debit")
    finite_primary_margin = (1-s**4)*raised_test - primary_price
    need(finite_primary_margin > 0 and raised_test < min(s,1-s),
         "four stages with a repriced fixed cover")
    price_a = ((1-r)*a + r*(1-s)*b)/(1-r*s)
    price_b = ((1-s)*b + s*(1-r)*a)/(1-r*s)
    need(price_a == (1-r)*a+r*price_b and price_b == (1-s)*b+s*price_a,
         "inconsistent mutual service prices")
    need(price_a < min(r, 1-r) and price_b < min(s, 1-s), "adapter or stock guard")
    neutral_r = Q(9999, 10000)
    coupled_b = (1-s)*b/(1-neutral_r*s)
    neutral = neutral_r*coupled_b
    need(neutral < neutral_r and coupled_b < min(s, 1-s) and
         (1-s)*b+s*neutral == coupled_b, "neutral controller or funded guards")
    raw_upper = Q(raw_a["raw_crossing"][1])
    cut, cut_low, cut_high = homogeneous_separator(raw_a)
    need(raw_upper < cut < price_a, "cycle does not cross the homogeneous separator")
    need(price_a > raw_upper > a and price_b > Q(native_b["application"]["compiler"]["tested"]),
         "downstream separation")
    guard_a = deficit(raw_a["paid"], raw_a["targets"])
    guard_b = deficit(pending["complete_paid"], pending["complete_productive"])
    need(57 < guard_a[0] <= guard_a[1] < 58 and 46 < guard_b[0] <= guard_b[1] < 47,
         "coarse exponent and transfer guard")

    selected_gate = module(ROOT/"research/shared-wire-split-composition/interval_gate.py")
    # Both application gates receive a separately proved ordinary service.
    pending_gate = module(HERE/"retained/supplier_gate.py")
    # The caller sets its service ceiling separately for each entry below.
    app = native_b["application"]
    fixed = native_b["caller_census"]
    invoice = {}
    for key, local, caller, side in (("T", "positive_helper_ranks", "fixed_root_targets", "targets"),
                                     ("P", "paid_native_ranks", "fixed_caller_paid", "paid")):
        terms = Counter({r: fixed["calls"]*n for r, n in native_b["native"][local].items()})
        terms.update(fixed[caller])
        need(dict(terms) == app["invoice"][side], "changed signed 48-call bill")
        invoice[key] = terms
    need(fixed["finite_binding"]["native_main_bindings"] == 19200, "pending main bindings")
    gates = {}
    for label, price in (("selected_entry", price_a), ("pending_entry", price_b),
                         ("neutral_entry", neutral), ("neutral_companion", coupled_b),
                         ("fixed_blocks_independent", b), ("fixed_blocks_primary", primary_price)):
        # Install exactly the service derived above, as the original driver installs its backend.
        pending_gate.BIT_PIN = str(price)
        gates[label] = {
            "selected": gate_at(selected_gate, native_a["invoice"], native_a["gate"], price),
            "pending": gate_at(pending_gate, invoice, app["compiler"], price)}
        # The historical gates hard-code the preceding atom exponent.
        # Replace the stock test with the conservative exponent of this cycle.
        stock_exponent = r if label in ("selected_entry", "pending_entry") else s
        for source, actual in ((native_a["gate"], gates[label]["selected"]),
                               (app["compiler"], gates[label]["pending"])):
            g = (Q(source["tested"])-Q(source["claim"]))/7
            beta = 1-3*g
            functional = [3*g, beta*(1-Q(3,1000)), 128-48-(1-g)-beta-1,
                          beta*(1-stock_exponent)]
            need(len(functional) == 4 and min(functional) > Q(actual["outer"]["minimum_margin"]),
                 "revised physical stock or functional inequality")
            actual["functional"] = list(map(str, functional))
    old_price = Q(selected["ordinary_BIT_saving"])
    pending_gate.BIT_PIN = str(old_price)
    need(old_price < Q(app["compiler"]["tested"]), "old entry should fail the tested service price")
    try:
        gate_at(pending_gate, invoice, app["compiler"], old_price)
    except AssertionError:
        pass
    else:
        raise ValueError("pending caller accepted the old selected ordinary rate")
    pending_use = gates["selected_entry"]["pending"]
    h = int(pending_use["H"])
    depth_scale = 1920 * 153**1920 * (h+1)**2
    for root, guard in ((app["common_root"], app["depth_guard"]),
                        (native_b["common_root"], native_b["common_depth_guards"]["tested"])):
        bits = (root["context_c"]*depth_scale).bit_length()
        need(bits < h and guard == {"argument_bit_length": bits, "compiler_H": h,
                                    "strict_guard_passed": True}, "pending root depth guard")
    need(native_b["caller_census"]["calls"] == 48 and pending["native_calls"] == 36,
         "incomplete pending caller")
    stage = Q(0)
    finite = []
    for _ in range(3):
        stage = (1-s)*a+s*stage
        finite.append(str(stage))
    need(stage > Q(selected["ordinary_BIT_saving"]), "finite predecessor comparison")
    x, y = Q(0), Q(0)
    for _ in range(4):
        x, y = (1-r)*a+r*y, (1-s)*b+s*x
    need(min(x,y) > Q(app["compiler"]["tested"]), "finite alternating comparison")
    need(price_a < Q(native_b["target"]) < price_b and price_b < Q(pending["ordinary_admitted"]),
         "separate enrolled target and historical ordinary service")
    return dict(covered=[str(a), str(b)], atom_powers=[str(r), str(s)],
                cycle=[str(price_a), str(price_b)], neutral=[str(neutral), str(coupled_b)],
                fixed_blocks={"block_count": 2, "independent_both_entries": str(b),
                              "primary_both_entries": str(primary_price),
                              "source_primary_ordinary": primary["ordinary_admitted"],
                              "finite_comparison_margin": str(finite_primary_margin),
                              "full_cover_fallback_multiplier_upper": str(1+Q(64,2**45)),
                              "log2_N_to_cover_loss": 29861},
                selected_raw_upper=str(raw_upper), selected_excess=str(price_a-raw_upper),
                homogeneous_separator=str(cut), separator_deficit=[str(cut_low), str(cut_high)],
                selected_coarse_guard=list(map(str, guard_a)), pending_coarse_guard=list(map(str, guard_b)),
                finite_elementary=finite, finite_four_stage_cycle=[str(x),str(y)],
                single_selected_seeded_by_pending=str((1-r)*a+r*Q(native_b["binary_ordinary"])),
                gates=gates)


if __name__ == "__main__":
    evidence = compute()
    need(evidence == read(HERE/"RESULT.json"), "scientific receipt mismatch")
    print("PASS_TWO_CALLERS prices=6 applications=12 strict=54 functional=4")
