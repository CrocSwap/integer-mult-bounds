"""Reprice the source-bound six-stage comparator and test the seventh paid receiver."""

from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

from activation import full_entrance
from calibration import COMPLEX_C
from check_activation_space import receipt as powered_stock
from installations import BINARY_C, RESOLUTION
from outer_budget import margins, qualify
from ordinary_carrier import stage_for_width_log
from staged_carriers import entrance_logs

HERE = Path(__file__).resolve().parent


def powered_refit(trial, debit, final_height, count, ratio=6):
    """Use the old intermediate rounding and its actual stock and signed tests."""
    heights = tuple((final_height+ratio**j-1)//ratio**j for j in reversed(range(count)))
    profile = RESOLUTION
    gap = Q(1, profile.positive_stop_denominator)
    ordinary = profile.ordinary
    numerical = 1 + int(10 / (COMPLEX_C - ordinary))
    previous = Q()
    for index, height in enumerate(heights):
        limit = min(profile.eta, (249*(trial-Q(debit,height))+previous)/250)
        rate = ordinary if index+1 == len(heights) else Q(int(10**18*limit)-1,10**18)
        assert previous < rate < limit
        previous = rate
    qualify(profile.kappa, gap, ordinary, COMPLEX_C-Q(10,numerical))
    cuts = entrance_logs(heights)
    assert all(cut+2 < h for cut,h in zip(cuts[:-1],heights[1:],strict=True))
    assert min(heights) >= 512*430 and numerical >= 512*128
    assert min(heights) >= 2+(134**430).bit_length()+(127**430).bit_length()+71
    stock = powered_stock(heights,numerical,cuts[-1],1024*max(heights)+(len(heights)+1).bit_length(),
                          430,complex_power=128)
    # The published 430-factor bridge requests direct coverage at each first entrance.
    first_s = stock["initial_s"]
    for i,h in enumerate(heights):
        quotient_cut = (Q(2*h+64)/(1-profile.eta)).__ceil__()
        assert (1-profile.eta)*quotient_cut >= 2*h+64 and quotient_cut < 3*h < 8*h
        top = cuts[i+1] if i+1 < len(cuts) else first_s
        floor = cuts[i-1] if i else 0
        assert top-floor <= 8*h
        if i+1 < len(cuts):
            parent = cuts[i+2] if i+2 < len(cuts) else first_s
            assert parent+250 < 250*top and cuts[i]+1 < top
    h = max(numerical,*heights)
    levels = (13*h+4*430-1)//(4*430)+2
    local = 4*stock["raw_structural_nodes_log2_upper"]+8*h.bit_length()+512
    assert 19+2*stock["raw_structural_nodes_log2_upper"]+levels.bit_length()<local<stock["native_volume_log2_upper"]
    return {"heights":list(heights),"numerical_H":numerical,
            "A":stock["log2_sufficient_public_precision"],
            "all_size_stripe_margin":stock["all_size_margin_lower_at_entrance"]}


def expanded_open_floor(height):
    """Count a family of actual labelled OPEN records of the old powered installer."""
    from powered import PoweredWord
    from strong_binary import graph, caller
    from tagged_sources import binary_ports

    raw = binary_ports(graph(),caller())
    v = 430
    word = PoweredWord(raw.ambient, raw.targets, raw.paid, v, 15, 12, 12)
    target_ids = [j for j,port in enumerate(word.targets) if port.rank == 15]
    paid = next(j for j,port in enumerate(word.paid) if port.rank == 56)
    assert word.ambient == 134 and len(target_ids) == len({word.targets[j].tag for j in target_ids}) == 444
    for j in (target_ids[0],target_ids[-1]):
        assert word.target((j,)*v).rank == 15**v
    assert next(word.blocks((paid,)*v)).rank == 12**v
    assert height >= 512*v and height-2-9*v > 70
    assert 134 < 2**8 and Q(15,12) < 2 and 444 > 2**8
    from band_compiler import make_planner
    from epoch_tape import OPEN, Image, epoch
    from itertools import product

    class Rule:
        ambient = 8
        targets = (6,6,6)
        paid = (2,3)

    plan = make_planner(Rule,2)(272)
    first = plan.forest.layers[(1,)]
    assert plan.forest.height == 4 and {u.future for u in first} == set(product(range(3),repeat=3))
    assert all(kind == "source" for u in first for kind,_ in u.ports) and (1,) in plan.forest.prefixes
    records = tuple(epoch(Rule,plan))
    opens = sum(row[0] == OPEN for row in records)
    image = Image(Rule,plan)
    try:
        assert tuple(image.rows()) == records and opens >= plan.copies*len(first)
        assert (len(first),plan.copies,opens,image.records,image.size) == (27,17,1428,8568,66397)
    finally:
        image.stream.close()
    return 8*(height-2-9*v)


def compare_resolution():
    spec = json.loads((HERE/"SOURCES.json").read_bytes())["six_stage_comparator"]
    raw = (HERE/"predecessor"/spec["file"]).read_bytes()
    assert sha256(raw).hexdigest() == spec["sha256"]
    prior = json.loads(raw)
    profile = RESOLUTION
    k = profile.kappa
    gap = Q(1,profile.positive_stop_denominator)
    trial = Q(prior["trial"])
    assert Q(prior["kappa"]) == k and Q(prior["gap"]) == gap
    assert prior["power"] == 430 and prior["bit_debit"] == 31 and prior["numeric_debit"] == 10
    from installations import GAUSSIAN_C
    positive = GAUSSIAN_C-Q(39,256*profile.complex_log)
    strict,functional,paid = margins(k,gap,profile.ordinary,positive)
    scale = profile.positive_stop_denominator**2
    assert len(strict) == 54 and len(functional) == 4
    assert all((x*scale).denominator == 1 for x in (*strict,*functional))
    assert (paid*scale).denominator == 19
    assert max((x*19*scale).numerator.bit_length() for x in (*strict,*functional,paid)) <= 186
    # Removing all the earlier debits and keeping the original five grid roundings
    # only increases the possible sixth limit. Use the outward raw endpoint.
    previous = Q()
    crossing_upper = Q(prior["raw_interval"][1])
    for _ in range(5):
        previous = Q(int(10**18*(249*crossing_upper+previous)/250)-1,10**18)
    upper = (249*crossing_upper+previous)/250
    assert upper == Q(prior["six_stage_upper_fraction"])
    # This weaker bound even allows the competitor to change its stop margin.
    old_H_floor = 1 + int(Q(249*31,250)/(upper-k))
    assert 0 < old_H_floor <= prior["minimum_last_height_with_profile_debit"]
    # At our own binary price, six costless, unrounded stages already miss k.
    ceiling = BINARY_C*(1-Q(1,250)**6)
    assert ceiling < k
    cuts = entrance_logs(profile.rank_logs)
    for index, cut in enumerate(cuts,1):
        assert stage_for_width_log(cut-1,7,profile.rank_logs) == index-1
        assert stage_for_width_log(cut,7,profile.rank_logs) == index
        assert stage_for_width_log(cut,index-1,profile.rank_logs) == index-1
    # Any funded retimed chain has at least seven stages. Apply Cauchy to its last seven
    # widths and drop the cold term. This bound also grants all possible further stages.
    root_lower = Q(63_245_553_203,10**12)
    assert root_lower**2 < Q(1,250)
    weight = sum(root_lower**j for j in range(7))
    all_counts = 1+int(Q(249,250)*Q(11,8)*weight**2/(BINARY_C-profile.ordinary))
    min_positive = 1+int(Q(39,256)/(GAUSSIAN_C-profile.ordinary))
    old = prior["complete_requirements"]
    assert max(x.bit_length() for x in old["binary_entrance_logs"]) <= 81
    assert old["raw_structural_nodes_log2_upper"] == 12973 and prior["local_exponent"] == 53044
    assert 19 + 2*12973 + prior["G_plus_1_upper"].bit_length() < 53044 < prior["native_q"]
    assert Q(9*16,15*32) == Q(3,10)
    A = full_entrance(cuts[-1],profile.complex_log)
    assert old["log2_sufficient_public_precision"] > 13_000_000*A
    # Reprice common tape/access units. The larger stop uses the uniform 1,600 allowance.
    old_E = 1 + max(84_500_000, 1600+100*old["complex_rank_log"]+40+16384*sum(old["binary_rank_logs"])+1)
    exact_floors = []
    for count in (6,7):
        limit = Q()
        for _ in range(count-1):
            limit = Q(int(10**18*(249*trial+limit)/250)-1,10**18)
        final = (249*trial+limit)/250
        exact_floors.append(1+int(Q(249*31,250)/(final-profile.ordinary)))
    # Five zero-debit stages miss the target. Cauchy--Schwarz over the last six
    # positive deficits bounds the sum of widths of every funded longer chain.
    assert trial*(1-Q(1,250)**5) < k
    weight = sum(Q(1,16)**i for i in range(6))
    cost = Q(249*31,250)*weight**2
    six_floor = 1 + int(cost/(trial-profile.ordinary-trial/250**6))
    any_count_floor = 1 + int(cost/(trial-profile.ordinary))
    row_sum = sum(prior["complete_requirements"]["binary_rank_logs"])
    assert row_sum > six_floor >= any_count_floor > 21*A
    return {"retimed_any_stage_count_A_floor":all_counts+min_positive,
            "prior_head":spec["head"], "old_six_A_floor":six_floor,
            "old_any_stage_count_A_floor":any_count_floor, "prior_binary_H":old["binary_rank_logs"],
            "prior_numerical_H":old["complex_rank_log"], "prior_A":old["log2_sufficient_public_precision"],
            "prior_log2_S_le":old["log2_all_fixed_setup_upper"],
            "prior_installed_OPEN_log2_gt":expanded_open_floor(old["binary_rank_logs"][-1]), "prior_log2_C_le":old_E,
            "old_powered_last_H_strict_integer_floor":old_H_floor,
            "old_exact_trial_last_H_floors":exact_floors,
            "old_minimum_sixth_height_witness":powered_refit(trial,31,exact_floors[0],6,ratio=3),
            "old_powered_six_refit":powered_refit(trial,31,181_000_000_000_000_000_000,6),
            "old_powered_seven_price_sensitivity":powered_refit(trial,31,1_980_000_000_000_000_000,7),
            "retimed_zero_debit_six_stage_upper":str(ceiling), "retimed_six_stage_deficit":str(k-ceiling),
            "stop_absorption_log2_le":((17*profile.positive_stop_denominator)**16-1).bit_length()}
