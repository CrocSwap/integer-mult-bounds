"""Finite rounded-leaf checks for the space-bounded echo scheduler.

The leaf and independently assembled dense operator are pinned PR628 code.
These generic factors do not certify kernel preparation or a multiplication bound.
"""

from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path

from schedule import compose, optimal_plan


def need(condition, message):
    if not condition:
        raise ValueError(message)


def inherited_leaf():
    path = Path(__file__).resolve().parent / "vendor" / "pr628" / "dirty.py"
    spec = importlib.util.spec_from_file_location("space_budget_pr628_dirty", path)
    need(spec is not None and spec.loader is not None, "missing pinned rounded leaf")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PhaseTable:
    """Immutable phase entries with counted indexed reads."""

    def __init__(self, values):
        self.values = tuple(values)
        self.reads = 0

    def __len__(self):
        return len(self.values)

    def __getitem__(self, index):
        self.reads += 1
        return self.values[index]


def factor_multiplicities(plan, weight=1):
    if not plan.children:
        return [weight]
    return [
        count
        for i, child in enumerate(plan.children)
        for count in factor_multiplicities(
            child, weight * (2 if i in (0, len(plan.children) - 1) else 4)
        )
    ]


def factors_for(count):
    coefficients = (
        (F(1, 4), F(1, 8)),
        (F(-1, 8), F(1, 4)),
        (F(3, 16), F(-1, 16)),
        (F(-1, 4), F(-1, 8)),
    )
    return [
        (i % 2 == 0, coefficients[i % len(coefficients)], F(3 if i == 0 else 1))
        for i in range(count)
    ]


def ceiling_log2(value):
    if value == 0:
        return None
    need(value > 0, "positive error required")
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    power = F(2) ** exponent
    return exponent + int(value > power)


def rejected(name, action):
    try:
        action()
    except ValueError as error:
        return {"name": name, "rejected": str(error)}
    raise ValueError("negative control accepted: " + name)


def negative_controls(dirty):
    c = dirty.c
    controls = []
    plan = optimal_plan(3, 2)
    for alias in ("source", "target", "scratch"):
        source = [c.ONE, (F(1, 2), F(1, 4))]
        target = [(F(7), F(1)), c.ONE]
        scratch = [[(F(j + 2), F(i + 1)) for i in range(2)] for j in range(plan.scratch)]
        arrays = [source, target, *scratch]
        before = [array[:] for array in arrays]
        phases = {"source": source, "target": target, "scratch": scratch[0]}[alias]
        calls = []

        def forbidden_leaf(src, dst, factor, sign):
            calls.append(factor)
            raise ValueError("leaf ran before alias rejection")

        control = rejected(
            "readonly_phase_alias_" + alias,
            lambda: compose(plan, source, target, scratch, forbidden_leaf, readonly=(phases,)),
        )
        need(not calls and arrays == before, "phase alias was not rejected before mutation")
        controls.append({**control, "leaf_calls": 0, "arrays_unchanged": True})

    phases = PhaseTable((c.ONE, (F(3, 5), F(4, 5))))
    source = [c.ONE, (F(1, 2), F(1, 4))]
    target = [(F(7), F(1)), c.ONE]
    controls.append(rejected(
        "underprecision",
        lambda: dirty.leaf(source, target, factors_for(1)[0], phases, F(1, 2), 2, 1, 1, None),
    ))

    factors = factors_for(3)
    factors[1] = (False, c.ONE, F(1))
    scratch = [[(F(j + 2), F(i + 1)) for i in range(2)] for j in range(plan.scratch)]
    stats = {"leaves": 0, "scalar_steps": 0}

    def late_invalid_leaf(src, dst, factor, sign):
        dirty.leaf(src, dst, factors[factor], phases, F(1, 2), 128, 1, sign, stats)

    control = rejected(
        "late_unstable_coefficient",
        lambda: compose(plan, source, target, scratch, late_invalid_leaf, readonly=(phases,)),
    )
    need(stats["leaves"] > 0, "late coefficient control did not reach a prior valid leaf")
    controls.append({**control, "prior_completed_leaf_calls": stats["leaves"]})
    return controls


def run_rounded_checks():
    dirty = inherited_leaf()
    c = dirty.c
    units = (c.ONE, (F(0), F(1)), (F(3, 5), F(4, 5)), (F(-5, 13), F(12, 13)))
    beta, r = F(1, 2), F(3)
    a, growth = 13 * (r + 1) / beta**3, 2 + r / beta
    records = []
    cases = 0
    for count in range(1, 9):
        factors = factors_for(count)
        need(all(c.norm2(b) <= (1 - beta)**2 and abs(scale) <= r
                 for _, b, scale in factors), "invalid stable factor fixture")
        for budget in range((count - 1).bit_length(), 6):
            plan = optimal_plan(count, budget)
            multiplicities = factor_multiplicities(plan)
            need(sum(multiplicities) == plan.calls, "plan call count disagrees with multiplicities")
            bits = 128 + 3 * plan.calls
            unit_roundoff = F(1, 1 << bits)
            need(a * unit_roundoff <= 1 and unit_roundoff <= beta**2 / 2, "uniform precision")
            maximum_bound = F(0)
            maximum_error_l1 = F(0)
            reads_by_length = {}
            for length in (1, 3, 5):
                phase_values = tuple(units[(i + count) % len(units)] for i in range(length))
                need(all(c.norm2(value) == 1 for value in phase_values), "nonunit fixture phase")
                for direction in (-1, 1):
                    dirt = -13 if direction == -1 else 7
                    source = [(F(2 * i - 3, 8), F(5 - i, 16)) for i in range(length)]
                    target = [(F(dirt + i, 4), F(dirt - i, 8)) for i in range(length)]
                    scratch = [
                        [(F(dirt + 2 * i + j, 4), F(dirt - 3 * i - j, 8)) for i in range(length)]
                        for j in range(plan.scratch)
                    ]
                    source_before, target_before = source[:], target[:]
                    scratch_before = [array[:] for array in scratch]
                    initial_norm = max(abs(re) + abs(im) for array in [source, target, *scratch]
                                       for re, im in array)
                    bound = plan.calls * a * (initial_norm + 1) * unit_roundoff * growth**(plan.calls - 1)
                    need(bound <= F(1, 1 << 96), "complete execution bound exceeds test tolerance")
                    maximum_bound = max(maximum_bound, bound)
                    phases = PhaseTable(phase_values)
                    stats = {"leaves": 0, "scalar_steps": 0}
                    observed = [0] * count

                    def leaf(src, dst, factor, sign):
                        observed[factor] += 1
                        dirty.leaf(src, dst, factors[factor], phases, beta, bits, direction, sign, stats)

                    compose(plan, source, target, scratch, leaf, readonly=(phases,))
                    need(source == source_before and scratch == scratch_before, "rounded dirty restoration")
                    need(phases.values == phase_values, "phase values changed")
                    need(stats["leaves"] == plan.calls and observed == multiplicities, "rounded leaf counts")
                    expected_reads = sum(
                        calls * ((6 if inside else 5) * length - 2)
                        for calls, (inside, _, _) in zip(multiplicities, factors)
                    )
                    need(phases.reads == expected_reads, "rounded phase read count")
                    reads_by_length[str(length)] = expected_reads
                    expected = dirty.exact_operator(source_before, factors, phase_values, direction)
                    for actual, initial, exact in zip(target, target_before, expected):
                        error = c.sub(c.sub(actual, initial), exact)
                        need(c.norm2(error) <= bound**2, "complete rounded target differs from dense operator")
                        maximum_error_l1 = max(maximum_error_l1, abs(error[0]) + abs(error[1]))
                    compose(plan, source, target, scratch, leaf, sign=-1, readonly=(phases,))
                    need(source == source_before and target == target_before and scratch == scratch_before,
                         "rounded complete word inverse")
                    need(phases.values == phase_values and phases.reads == 2 * expected_reads, "inverse phase reads")
                    need(stats["leaves"] == 2 * plan.calls and observed == [2 * n for n in multiplicities],
                         "inverse leaf counts")
                    need(stats["scalar_steps"] == 6 * length * plan.calls, "inherited three-pass counter")
                    cases += 1
            records.append({
                "factors": count,
                "scratch_budget": budget,
                "scratch_used": plan.scratch,
                "leaf_calls": plan.calls,
                "factor_multiplicities": multiplicities,
                "working_bits": bits,
                "phase_reads_by_cycle_length": reads_by_length,
                "maximum_complete_error_bound": str(maximum_bound),
                "maximum_observed_error_l1_le_2_pow": ceiling_log2(maximum_error_l1),
            })
    return {
        "status": "passed",
        "cases": cases,
        "cycle_lengths": [1, 3, 5],
        "orientations": [-1, 1],
        "initial_dirt": [-13, 7],
        "beta": str(beta),
        "multiplier_bound_r": str(r),
        "execution_error_formula": "N*a*(D+1)*2^-w*G^(N-1), a=13*(r+1)/beta^3, G=2+r/beta",
        "plans": records,
        "controls": negative_controls(dirty),
        "scope": "Finite generic stable factors, mixed inner/outer for n>=2; r bounds multipliers only. "
                 "The complete rounded word is compared with PR628's independently assembled dense operator. "
                 "Preparation, phase generation/storage, routing, and arithmetic workspace remain inherited costs; "
                 "no kernel preparation or multiplication theorem is certified. "
                 "Only outer alias rejection is checked before mutation; a later leaf failure has no rollback guarantee.",
    }


if __name__ == "__main__":
    print(json.dumps(run_rounded_checks(), indent=2))
