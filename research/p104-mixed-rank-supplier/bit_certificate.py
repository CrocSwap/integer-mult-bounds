# SPDX-License-Identifier: Apache-2.0
"""Paid tensor partition, strict finite moments, and the ordinary BIT cap."""

from collections import Counter
from fractions import Fraction as Q

TRIAL = Q("0.003879928046148")
UNIFORM_LOSS, COVER_LOSS = Q(1, 400_000_000_000), Q(8, 10**12)
POWER, FLOOR, AMBIENT = 480, 16, 134
CLASSES = (("grades_1_to_4", 10, Q(11, 50)), ("grades_above_4", 11, Q(13, 50)))
FLOOR_TILT = Q(17, 50)
THETA, LOG_POWER, HORIZON = Q(13, 15), 64, 3213
RHO = Q(1, 250)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def paid_class(first_grade):
    check(first_grade >= 1, "positive first paid rank")
    return CLASSES[int(first_grade > 4)][0]


def physical_paid_jobs(word, caller, charts):
    """Yield each raw paid grade with its literal occurrence label."""
    moves = [(clock, bank, charts.leg(*frames))
             for clock, (op, bank, *frames) in enumerate(word["program"]) if op == "MOVE"]
    for clock, (op, *args) in enumerate(caller["events"]):
        if op == "LOCAL":
            for native_clock, bank, grade in moves:
                yield grade, (clock, native_clock, bank)
        elif op in ("QUERY", "IDLE_ONE"):
            grade = 1 if op == "QUERY" else 7 * len(args[1])
            for port in range(caller["ports"]):
                yield grade, (clock, -1, port)


def subdivide(rank, cutoff):
    """Describe the consecutive disjoint axis blocks of a single paid job."""
    full_blocks, remainder = divmod(rank, cutoff)
    return full_blocks, remainder, full_blocks + int(remainder > 0)


def validate_partition(expected, assigned):
    check(Counter(assigned) == Counter(expected), "exactly one classification for each paid tuple")


def physical_witnesses(literal, binary_word, caller, paid):
    charts = literal.Charts(binary_word["frames"])
    actual = Counter()
    labels = set()
    samples = {grade: [] for grade in (4, 5, 14, 21)}
    for grade, label in physical_paid_jobs(binary_word, caller, charts):
        check(label not in labels, "unique raw paid occurrence label")
        labels.add(label)
        actual[grade] += 1
        if grade in samples and len(samples[grade]) < 2:
            samples[grade].append(label)
    check(actual == paid and len(labels) == sum(paid.values()), "complete physical paid inventory")
    check(all(len(rows) == 2 for rows in samples.values()), "two actual labels for each witness grade")

    # Include same-grade distinct jobs so grade-only checking cannot pass.
    sample = [(grade, label) for grade, rows in samples.items() for label in rows]
    tagged = [(head, tail) for head in sample for tail in sample]
    groups = {label: [] for label, _, _ in CLASSES}
    for row in tagged:
        groups[paid_class(row[0][0])].append(row)
    assigned = [row for group in groups.values() for row in group]
    validate_partition(tagged, assigned)
    check(assigned[0][1][0] == assigned[1][1][0] and assigned[0] != assigned[1],
          "same-grade mutation control")
    for bad in (assigned + [assigned[0]], assigned[1:], assigned[1:] + [assigned[1]]):
        try:
            validate_partition(tagged, bad)
        except ValueError:
            continue
        raise ValueError("lost or doubly classified paid tuple survived")

    tail_grade, tail_label = 14, samples[14][0]
    out = []
    for first_grade, (label, cutoff_base, _) in zip((4, 5), CLASSES, strict=True):
        check(paid_class(first_grade) == label, "actual class boundary witness")
        rank = first_grade * tail_grade**(POWER - 1)
        cutoff = cutoff_base**POWER
        full, last, calls = subdivide(rank, cutoff)
        other_cutoff = CLASSES[int(first_grade <= 4)][1]**POWER
        wrong_calls = subdivide(rank, other_cutoff)[2]
        check(full * cutoff <= rank == full * cutoff + last < (full + 1) * cutoff
              and 0 < last < cutoff and calls > 1 and wrong_calls != calls
              and rank < 14**POWER, "correct physical split and different grade-14 count")
        out.append(dict(
            class_name=label, first_grade=first_grade, first_label=samples[first_grade][0],
            repeated_tail_grade=tail_grade, repeated_tail_label=tail_label, repeated_tail_factors=POWER - 1,
            full_blocks=full, residual_rank=str(last), calls=calls, misclassified_calls=wrong_calls,
            grade14_calls_at_same_tensor_power=1,
        ))
    check(out[0]["calls"] != out[1]["calls"], "the two jobs have distinct subdivisions")
    # Keep every factor and transpose the positions of the grade-4 and
    # grade-14 labels. The same product rank must cross the call boundary.
    powers = {4: 182, 14: 134, 21: 164}
    check(sum(powers.values()) == POWER, "same-rank witness has the complete tensor power")
    head_first_rank = 4**powers[4] * 14**powers[14] * 21**powers[21]
    low_cut, high_cut = (cutoff**POWER for _, cutoff, _ in CLASSES)
    check(low_cut < head_first_rank < min(2 * low_cut, high_cut)
          and subdivide(head_first_rank, low_cut)[2] == 2
          and subdivide(head_first_rank, high_cut)[2] == 1, "same-rank split with a different first label")
    return out, dict(
        raw_paid_occurrences=len(labels), sample_paid_tuples=len(tagged), duplicate_rejected=True,
        missing_rejected=True, replaced_same_grade_occurrence_rejected=True,
        equal_rank_control=dict(factor_powers=powers, labels={grade: samples[grade][0] for grade in powers},
                                swap_first_grades=[4, 14], calls=[2, 1]),
    )


def separated_moments(price, exact, paid, targets):
    """Cross-check fixed-point and rational interval bounds for each class."""
    t = 1 - TRIAL
    wanted, source_wanted = price.moment(targets, TRIAL), exact.moment(targets, t)
    normalized = {"alpha": price.divide(price.moment(paid, TRIAL), wanted)}
    source = {"alpha": exact.divide(exact.moment(paid, t), source_wanted)}
    inventories = {label: Counter({r: n for r, n in paid.items() if paid_class(r) == label})
                   for label, _, _ in CLASSES}
    check(sum(inventories.values(), Counter()) == paid and all(inventories.values()),
          "the two classes are exhaustive and both nonempty")

    for label, cutoff, tilt in CLASSES:
        check(tilt >= TRIAL and 1 < cutoff < FLOOR, "paid tail inequality hypotheses")
        den = price.mul(price.exp_log(cutoff, tilt), wanted)
        source_den = exact.mul(exact.power(cutoff, tilt), source_wanted)
        for name, hist in (("first", inventories[label]), ("rest", paid)):
            normalized[f"{label}_{name}"] = price.divide(price.moment(hist, TRIAL, tilt), den)
            source[f"{label}_{name}"] = exact.divide(exact.moment(hist, t + tilt), source_den)

    w = FLOOR_TILT
    normalized["discarded_targets"] = price.divide(
        price.mul(price.exp_log(FLOOR, w), price.moment(targets, TRIAL, -w)), wanted)
    source["discarded_targets"] = exact.divide(
        exact.mul(exact.power(FLOOR, w), exact.moment(targets, t - w)), source_wanted)
    grid = 10**22
    bounds = {}
    for key, interval in normalized.items():
        first_lo, first_hi = (Q(value, price.GRID) for value in interval)
        second_lo, second_hi = source[key]
        check(max(first_lo, second_lo) <= min(first_hi, second_hi), f"directed interval agreement {key}")
        hi = max(first_hi, second_hi)
        bound = Q(price.ceiling(hi.numerator * grid, hi.denominator), grid)
        check(0 < hi <= bound < 1, f"strict rational cap {key}")
        bounds[key] = bound

    lift = {name: 2 * bounds[f"{name}_first"] * bounds[f"{name}_rest"]**(POWER - 1)
            for name, _, _ in CLASSES}
    discard = bounds["discarded_targets"]**POWER
    volume = 1 / (1 + POWER * (1 - bounds["alpha"])) + sum(lift.values()) + discard
    check(1 - volume > Q("0.0000000000012309863319385"), "strict normalized split-and-discard surplus")
    return inventories, dict(
        trial=str(TRIAL), power=POWER, productive_floor=FLOOR, target_tilt=str(w),
        normalized={key: price.decimal_interval(value) for key, value in normalized.items()},
        exact_source_normalized={key: exact.display(value) for key, value in source.items()},
        upper_caps={key: str(bound) for key, bound in bounds.items()},
        uplift_upper={name: price.rational_display(value, 25) for name, value in lift.items()},
        target_debit_upper=price.rational_display(discard, 25),
        normalized_surplus=price.rational_display(1 - volume, 25),
    )


def uniform_carrier(price, exact, paid, targets):
    upper_cut = max(cutoff for _, cutoff, _ in CLASSES)
    num, den = THETA.as_integer_ratio()
    check(max(paid) < max(targets) <= AMBIENT and upper_cut < FLOOR < AMBIENT,
          "full working ambient and separated jobs")
    check(upper_cut**den < FLOOR**num
          and 2**(den - num) * upper_cut**(POWER * den) <= AMBIENT**(POWER * num),
          "strict exit and shifted-log inequalities using the larger cutoff")

    ambient_power = price.raise_interval(price.exp_log(AMBIENT, TRIAL), POWER)
    eta = price.scale(price.invert(ambient_power), 1 - TRIAL)
    source_power = exact.power(AMBIENT, POWER * TRIAL)
    source_eta = exact.scale(exact.power(AMBIENT, -POWER * TRIAL), 1 - TRIAL)
    p = LOG_POWER
    check(THETA**p < min(Q(eta[0], price.GRID), source_eta[0])
          and max(Q(eta[1], price.GRID), source_eta[1]) <= THETA**(p - 1)
          and max(Q(ambient_power[1], price.GRID), source_power[1]) < 2**p,
          "two interval engines verify the logarithmic majorant")
    step = UNIFORM_LOSS.denominator
    H = step * HORIZON
    check(UNIFORM_LOSS == Q(1, step) and (H + 1)**p < 2**HORIZON
          and (H - step + 1)**p >= 2**(HORIZON - 1), "exact uniform carrier and preceding grid point")
    alternative_step, alternative_j = 10**15, 3954
    alt_H = alternative_step * alternative_j
    check((alt_H + 1)**p < 2**alternative_j
          and (alt_H - alternative_step + 1)**p >= 2**(alternative_j - 1),
          "uniform sensitivity at a separately priced loss")
    return dict(
        gap=str(UNIFORM_LOSS), uniform_saving=str(TRIAL - UNIFORM_LOSS), H=H, N=f"2^{H}",
        theta=str(THETA), log_power=p, integer_grid_exponent=HORIZON, ambient_base=AMBIENT,
        maximum_paid_base=upper_cut, minimum_productive_base=FLOOR, ambient=f"{AMBIENT}^{POWER}",
        ambient_power=price.decimal_interval(ambient_power), eta=price.decimal_interval(eta),
        alternative_uniform_only=dict(gap=str(Q(1, alternative_step)), H=alt_H, integer_grid_exponent=alternative_j),
    )


def delayed_cover_and_stock(price, uniform, selected):
    # Freeze the rational matchers and their witnesses before choosing q.
    # The retained whole-cover surcharge is bounded by 64*N^5/q.
    d = COVER_LOSS
    good_decay_exponent = uniform["H"] * d
    check(0 < d < TRIAL - UNIFORM_LOSS and 2**45 * d > 256,
          "whole-cover surcharge strictly below one quarter of the cover loss")
    check(2**int(good_decay_exponent) >= 1 + d / 2,
          "actual N to the cover loss covers the bad-class multiplier")
    multiplier = (1 + d / 4) / (1 + d / 2)
    check(multiplier < 1, "covered complete moment strictly below one")
    covered = TRIAL - UNIFORM_LOSS - d
    steps, previous = [], selected
    for _ in range(5):
        envelope = (1 - RHO) * covered + RHO * previous
        ticks = int(envelope * 10**15) - 1
        steps.append(f"0.{ticks:015d}")
        previous = Q(steps[-1])
    admitted, stages = price.bootstrap(selected, covered, steps)
    check(admitted == Q("0.003879928035646") and admitted == Q(steps[-1]) < covered,
          "five exact stock stages")
    stock_gaps = []
    for row in stages:
        old, new = Q(row["previous"]), Q(row["claim"])
        envelope = (1 - RHO) * covered + RHO * old
        gap = min(RHO - new, envelope - new, 1 - RHO - new)
        check(gap > 0, "strict positive room for counted ordinary work")
        stock_gaps.append(str(gap))
    last_envelope = (1 - RHO) * covered + RHO * Q(stages[-1]["previous"])
    check(last_envelope < Q("0.003879928035648"), "too-high fifth-stage stock cap rejected")
    return dict(
        loss=str(d), covered=str(covered), H_times_cover_loss=str(good_decay_exponent),
        q_criterion="odd prime q > 2^45*N^5 avoiding the frozen finite catalogue determinants, denominators and rank witnesses",
        relative_bad_surcharge_upper=str(Q(64, 2**45)), relative_bad_surcharge_budget=str(d / 4),
        covered_moment_upper=str(multiplier), seed=str(selected), rho=str(RHO),
        stages=stages, minimum_ordinary_gaps=stock_gaps, admitted=steps[-1],
        fifth_stage_overclaim_rejected="0.003879928035648",
        stock=dict(atom_width="w=ceil(e^(1/250))", d="max(1,ceil(e/w))",
                   depth="2+ceil(log_N(d))", reserve="W(w)^depth*S_old",
                   W="B*|GL_N(F_q)|*q^(N^2*(w-1))", high_digits="O_fixed(w log e)",
                   coarse_child="at most floor(d/N) at every recursion",
                   low_width="use the completed preceding backend",
                   threshold="freeze at 2^j with j>4*degree/slack and C*(j+1)^degree<=2^(slack*j)"),
    )


def product_account(native, inventories):
    caps = native["ordinary"]
    paid, targets = native["paid"], native["targets"]
    p, b = sum(paid.values()), sum(targets.values())
    m = sum(r * n for r, n in paid.items())
    check((p, b, m) == (107460, 20706, 291360) and native["native_calls"] == 36
          and 0 < caps["ordinary_records"] < caps["raw_ordinary_allowance"] == 10**12
          and 0 < caps["owned_backing"] < caps["raw_owned_allowance"] == 10**7,
          "all-call raw record and owned bounds")
    occurrences = sum(b**(POWER - 1 - i) * p**i for i in range(POWER))
    partition = {}
    class_tuple_sum, class_mass_sum, call_sum = 0, 0, 0
    for name, cut, tilt in CLASSES:
        count = sum(inventories[name].values())
        mass = sum(r * n for r, n in inventories[name].items())
        class_tuples = count * p**(POWER - 1)
        class_mass = mass * m**(POWER - 1)
        upper = min(class_mass, class_tuples + class_mass // cut**POWER)
        class_tuple_sum += class_tuples
        class_mass_sum += class_mass
        call_sum += upper
        partition[name] = dict(first_paid_count=count, first_paid_rank_mass=mass, cutoff_base=cut,
                               tail_tilt=str(tilt), histogram=inventories[name],
                               tuple_count=f"{count}*{p}^{POWER - 1}",
                               rank_mass=f"{mass}*{m}^{POWER - 1}",
                               split_calls_upper_bit_length=upper.bit_length())
    check(class_tuple_sum == p**POWER and class_mass_sum == m**POWER and call_sum < m**POWER,
          "both paid classes account for every original position and its grade")
    precompile = dict(
        source_occurrences=occurrences, raw_paid_tuples=p**POWER, all_possible_targets=b**POWER,
        raw_record_instances=occurrences * caps["ordinary_records"],
        raw_owned_instances=occurrences * caps["owned_backing"],
        split_calls_upper=call_sum, added_block_adapter_sides_upper=2 * call_sum,
        discarded_target_allocation_and_retirement_pairs_upper=b**POWER,
    )
    return dict(
        paid_partition=partition, physical_schedule="chronological tensor product with an ordered original label per factor",
        raw_occurrences=f"sum(20706^({POWER - 1}-i)*107460^i for i=0..{POWER - 1})",
        product_count_bit_lengths={key: value.bit_length() for key, value in precompile.items()},
        retained_targets=f"every independent tuple with rank at least {FLOOR}^{POWER}",
        removed_targets="each remaining complete target is a tagged owned zero at both endpoints; every interior job remains",
        split_execution="original wrapper retained; lexicographic disjoint axis blocks, complete spectators, restored boundary",
        final_owned_bound="O = 6998544*U + O_aux; count fresh target, split, adapter, primitive and compiler banks for their full lifetimes",
        final_record_bound="G = 10^12*U + 8*R + G_aux; R counts completed routing and G_aux all further lifted, split, target and compiler services",
        final_height="Z=W+O; E0=64*(Z+N+P+G+1)^3; B0=P+E0; C0=32*N*B0^2",
        product_materialized=False, uniform_materialized=False,
    )
