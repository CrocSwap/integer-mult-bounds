"""Exact fixed-prime moments and finite outer assembly for PR244's profile."""
from decimal import Decimal, ROUND_FLOOR, localcontext
from fractions import Fraction as Q
import importlib.util
from pathlib import Path

PRIME = (1 << 127) - 1
M = 120
RHO = Q(2 * M**3, PRIME)
ETA = Q(1, 10**24)
BETA = Q(1, 10**9)
GRID = 10**18

def load(name, directory):
    path = Path(directory) / (name + ".py")
    spec = importlib.util.spec_from_file_location("source527_fixed_" + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def serial(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value

def fixed_moment(histogram, m, stock, saving, cost):
    lo, hi = cost.moment(histogram, m, stock, saving, False)
    log_lo, log_hi = cost.logarithm(Q(m))
    exp_lo, _ = cost.exponential(saving * log_lo, saving * log_lo)
    _, exp_hi = cost.exponential(saving * log_hi, saving * log_hi)
    fallback_weight = Q(32 * m * sum(histogram.values()), stock) * Q(2 * m**3, PRIME)
    return cost.floor(lo + fallback_weight * exp_lo), cost.ceil(hi + fallback_weight * exp_hi)

def certify_coarse(histogram, m, stock, cost):
    with localcontext() as ctx:
        ctx.prec = 80
        terms = [(Decimal(r*n) / Decimal(m*stock), (Decimal(m) / Decimal(r)).ln())
                 for r, n in histogram.items()]
        fallback = (Decimal(32*m*sum(histogram.values())) / Decimal(stock)
                    * Decimal(2*m**3) / Decimal(PRIME))
        log_m = Decimal(m).ln()
        lower, upper = Decimal(0), Decimal("0.003")
        for _ in range(240):
            candidate = (lower + upper) / 2
            total = sum(p * (candidate * log_r).exp() for p, log_r in terms)
            total += fallback * (candidate * log_m).exp()
            if total < 1:
                lower = candidate
            else:
                upper = candidate
        endpoint = Q(int(((lower + upper) / 2 * 10**24).to_integral_value(rounding=ROUND_FLOOR)), 10**24)
    next_endpoint = endpoint + Q(1, 10**24)
    assert fixed_moment(histogram, m, stock, endpoint, cost)[1] < 1
    assert fixed_moment(histogram, m, stock, next_endpoint, cost)[0] > 1
    return endpoint, next_endpoint

def second_engine_with_fallback(histogram, m, stock, saving, other):
    lower, upper = other.moment(m, stock, list(histogram.items()), saving)
    log_lo, log_hi = other.log_bounds(Q(m))
    exp_lo = other.exp_bounds(saving * log_lo)[0]
    exp_hi = other.exp_bounds(saving * log_hi)[1]
    fallback_weight = Q(32 * m * sum(histogram.values()), stock) * Q(2 * m**3, PRIME)
    return lower + fallback_weight * exp_lo, upper + fallback_weight * exp_hi

def grid_kappa(bit_saving):
    q = bit_saving * (1 - 2*ETA)
    minimum = (1 - ETA) * q / (1 + q)
    ticks = minimum * GRID
    return Q((ticks.numerator - 1) // ticks.denominator, GRID)

def bridge_template():
    return dict(
        proof="PROOF.md",
        representation="Exact powers with source-bound finite overcharges",
        semantic=dict(G=dict(base=2, exponent=30000), E=dict(base=2, exponent=100000),
                      B_upper=dict(base=2, exponent=100001), C0=dict(base=2, exponent=210000),
                      C1=1, strict_literal_gap=1, induction_gap_lower=1),
        rows=dict(coefficient=20161, degree=10**6, suffix_slope=4*10**6,
                  degree_gap=Q(10**6) - Q(51*20161, 25)))

def compute(base_certificate, base_root):
    cost = load("moment", base_root)
    other = load("base_two_moment", base_root)
    outer = load("outer", base_root)
    profile = base_certificate["bit_profile"]
    histogram = {int(k): int(v) for k, v in profile["histogram"].items()}
    m, stock = int(profile["m"]), int(profile["W"])
    assert (m, stock, profile["rank_mass"], profile["deficit"], profile["maxchild"]) == (
        120, 260987, 31265640, 52800, 50)
    assert profile["calls"] == sum(histogram.values())
    assert profile["normalization"] == 12 and profile["physical_replicas"] == 60
    baseline_kappa = Q(base_certificate["kappa"])
    complex_saving = Q(base_certificate["complex_coarse"])
    assert complex_saving == Q(747454944651775, 10**18)
    assert RHO == Q(3456000, PRIME) < Q(1, 10**16)

    coarse_endpoint, coarse_next = certify_coarse(histogram, m, stock, cost)
    coarse = Q((coarse_endpoint * GRID).numerator // (coarse_endpoint * GRID).denominator, GRID)
    assert fixed_moment(histogram, m, stock, coarse, cost)[1] < 1
    coarse_moment = fixed_moment(histogram, m, stock, coarse, cost)
    next_coarse_moment = fixed_moment(histogram, m, stock, coarse + Q(1, GRID), cost)
    assert coarse_moment[1] < 1 < next_coarse_moment[0]
    independent_coarse = second_engine_with_fallback(histogram, m, stock, coarse, other)
    independent_next = second_engine_with_fallback(histogram, m, stock, coarse + Q(1, GRID), other)
    assert independent_coarse[1] < 1 < independent_next[0]

    cap = grid_kappa(coarse)
    chain = [Q(384599, 10**10)]
    gap_records = []
    level = 0
    while True:
        old = chain[-1]
        new = (1 - coarse) * coarse + coarse * old
        assert old < new < coarse < 1 - new
        gaps = dict(atom=coarse-new, borrowing=1-new-coarse,
                    remainder=1-new-coarse*(1-old), stock=1-coarse)
        assert min(gaps.values()) > 0
        chain.append(new)
        level += 1
        candidate = grid_kappa(new)
        assert candidate <= cap
        gap_records.append(dict(level=level, gaps=gaps, minimum_gap=min(gaps.values())))
        if candidate == cap:
            break
        assert level < 20, "the finite chain did not reach the certified coarse grid cap"
    assert level == 5

    bridge = bridge_template()
    assert serial(bridge) == base_certificate["finite_bridge"]
    assembly = outer.assembly(chain[-1], complex_saving, bridge, cap, eta=ETA, beta=BETA)
    assert len(assembly["strict_constraints"]) == 47
    assert len(assembly["margins"]) == 7
    assert all(v > 0 for v in assembly["strict_constraints"].values())
    try:
        outer.assembly(chain[-1], complex_saving, bridge, cap + Q(1, GRID), eta=ETA, beta=BETA)
    except AssertionError:
        adjacent_rejected_at_finite_saving = True
    else:
        raise AssertionError("the adjacent final grid point passed at the finite saving")
    try:
        outer.assembly(coarse, complex_saving, bridge, cap + Q(1, GRID), eta=ETA, beta=BETA)
    except AssertionError:
        adjacent_rejected_at_coarse_cap = True
    else:
        raise AssertionError("the adjacent final grid point passed even at the coarse endpoint")

    exact_gain = cap - baseline_kappa
    assert exact_gain > 0, "fixed-prime refinement did not strictly improve the pinned base"
    return serial(dict(
        schema="source527-fixed-prime-exact-mathematics/1",
        base_candidate=dict(commit="a568d94f941929232ab393c7d33dc5a30e017892",
                            kappa=baseline_kappa, package="research/five-stage-source527-banks"),
        fixed_prime=dict(value=PRIME, greater_than=2**80, density=RHO,
                         density_formula="2*m^3/q", density_below_inherited_10_to_minus_16=True),
        bit_profile=profile,
        complex_profile=base_certificate["complex_profile"],
        coarse_rate=dict(exact_grid_rate=coarse, bracket=[coarse_endpoint, coarse_next],
                         first_engine_interval=coarse_moment,
                         first_engine_next_interval=next_coarse_moment,
                         second_engine_interval=independent_coarse,
                         second_engine_next_interval=independent_next),
        ordinary_bootstrap=dict(initial=chain[0],levels=level,chain=chain,gaps=gap_records,
                                grid_cap_from_coarse_endpoint=cap),
        finite_bridge=bridge,
        assembly=assembly,
        kappa=cap,
        kappa_decimal=cost.decimal(cap),
        baseline_kappa=baseline_kappa,
        exact_gain=exact_gain,
        adjacent_grid_point_rejected_at_finite_saving=adjacent_rejected_at_finite_saving,
        adjacent_grid_point_rejected_at_coarse_cap=adjacent_rejected_at_coarse_cap,
        binding="bit"))

def audit_finite_admission(mathematics, base_certificate, base_finite, base_root):
    finite = load("finite_check", base_root)
    profile = base_certificate["bit_profile"]
    m = int(profile["m"])
    literal_stock = int(profile["literal_stock"])
    literal_calls = 5 * int(profile["calls"])
    literal_mass = 5 * int(profile["rank_mass"])
    histogram = {int(k): 5*int(v) for k, v in profile["histogram"].items()}
    assert (literal_stock, literal_calls, literal_mass) == (1304935, 29455500, 156328200)
    coefficient = int(base_finite["q_power_bound"]["coefficient"])
    assert coefficient < 2**80 < PRIME
    assert literal_stock < PRIME
    coarse = Q(mathematics["coarse_rate"]["exact_grid_rate"])
    cost = load("moment", base_root)
    moment_at_coarse = fixed_moment(histogram, m, literal_stock, coarse, cost)
    delta_tau = 1 - moment_at_coarse[1]
    delta_linear = 1 - Q(literal_mass, m*literal_stock) - RHO * Q(32*m*literal_calls, literal_stock)
    assert delta_tau > 0 and delta_linear > 0
    cutoff_checks = []
    for row in mathematics["ordinary_bootstrap"]["gaps"]:
        gaps = {name: Q(value) for name, value in row["gaps"].items()}
        delta = min(gaps.values())
        log_cutoff = finite.cutoff_log2(delta, coefficient)
        assert Q(log_cutoff) * delta**2 >= 36
        assert Q(log_cutoff) * delta >= 2 * (4 + (coefficient-1).bit_length())
        cutoff_checks.append(dict(level=row["level"],minimum_gap=delta,log2_cutoff=log_cutoff))
    return serial(dict(
        status="PASS_FIXED_PRIME_FINITE_ADMISSION",
        q_power_coefficient=coefficient,
        q_power_coefficient_below_prime=True,
        literal_inventory=dict(stock=literal_stock,calls=literal_calls,rank_mass=literal_mass),
        moment_gaps=dict(delta_tau=delta_tau,delta_linear=delta_linear,
                         rare_density=RHO,full_fallback_kept=True),
        finite_cutoff_checks=cutoff_checks,
        inherited_costs=dict(extra_bank_selector_calls=base_finite["paid_inventory"]["extra_bank_selector_calls"],
                             complete_fallback_per_child=base_finite["paid_inventory"]["fallback_per_child"],
                             physical_replicas=base_finite["paid_inventory"]["physical_replicas"],
                             restored_internal_rows=base_finite["row_reserve"]["restored"]),
        scope="Exact fixed-prime density and five finite levels; inherited q-local, tape, row, selector, prime-supply and all-size interfaces remain conditional."))
