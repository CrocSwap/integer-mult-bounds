"""Exact fixed-prime refinement on PR259's 518-entrance multicut word."""
from decimal import Decimal, ROUND_FLOOR, localcontext
from fractions import Fraction as Q
import importlib.util
from pathlib import Path

PRIME = (1 << 127) - 1
M = 120
RHO = Q(2 * M**3, PRIME)
ETA = Q(1, 10**24)
BETA = Q(1, 10**9)
GRID = 10**27
COMPLEX_SAVING = Q(747454944651775, 10**18)
BASE_COMMIT = "a53ec0ca4d59634f16630dd16adf035c9f12595c"
BASE_KAPPA = Q(142205877210807, 2 * 10**17)
BASE_COARSE = Q(177883827203061, 250000000000000000)
INITIAL_LEAF = Q(384599, 10**10)


def load(name, path):
    spec = importlib.util.spec_from_file_location("cohort_fixed_prime_" + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_path(repository, name):
    candidates = [
        repository / "upstream" / (name + ".py"),
        repository / "research/source527-five-stage-crossover/references/source527" / (name + ".py"),
        repository / "research/coordinated-crossover-pr200-v2/baseline/geometry" / (name + ".py"),
    ]
    return next(path for path in candidates if path.is_file())


def serial(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def bridge_template():
    # Literal retained bridge from source527 math_check.py, itself pinned in SOURCE.json.
    return dict(
        proof="PROOF.md",
        representation="Exact powers with source-bound finite overcharges",
        semantic=dict(G=dict(base=2, exponent=30000), E=dict(base=2, exponent=100000),
                      B_upper=dict(base=2, exponent=100001), C0=dict(base=2, exponent=210000),
                      C1=1, strict_literal_gap=1, induction_gap_lower=1),
        rows=dict(coefficient=20161, degree=10**6, suffix_slope=4*10**6,
                  degree_gap=Q(10**6) - Q(51*20161, 25)))


def fixed_moment(histogram, m, stock, calls, saving, cost):
    lo, hi = cost.moment(histogram, m, stock, saving, False)
    log_lo, log_hi = cost.logarithm(Q(m))
    exp_lo = cost.exponential(saving * log_lo, saving * log_lo)[0]
    exp_hi = cost.exponential(saving * log_hi, saving * log_hi)[1]
    fallback_weight = Q(32 * m * calls, stock) * RHO
    return cost.floor(lo + fallback_weight * exp_lo), cost.ceil(hi + fallback_weight * exp_hi)


def second_engine_with_fallback(histogram, m, stock, calls, saving, other):
    lower, upper = other.moment(m, stock, list(histogram.items()), saving)
    log_lo, log_hi = other.log_bounds(Q(m))
    exp_lo = other.exp_bounds(saving * log_lo)[0]
    exp_hi = other.exp_bounds(saving * log_hi)[1]
    fallback_weight = Q(32 * m * calls, stock) * RHO
    return lower + fallback_weight * exp_lo, upper + fallback_weight * exp_hi


def certify_coarse(histogram, m, stock, calls, cost, other):
    with localcontext() as ctx:
        ctx.prec = 80
        terms = [(Decimal(r*n) / Decimal(m*stock), (Decimal(m) / Decimal(r)).ln())
                 for r, n in histogram.items()]
        fallback = (Decimal(32*m*calls) / Decimal(stock)
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
        endpoint = Q(int(((lower + upper) / 2 * GRID).to_integral_value(rounding=ROUND_FLOOR)), GRID)
    next_endpoint = endpoint + Q(1, GRID)
    first = fixed_moment(histogram, m, stock, calls, endpoint, cost)
    first_next = fixed_moment(histogram, m, stock, calls, next_endpoint, cost)
    second = second_engine_with_fallback(histogram, m, stock, calls, endpoint, other)
    second_next = second_engine_with_fallback(histogram, m, stock, calls, next_endpoint, other)
    assert first[1] < 1 < first_next[0]
    assert second[1] < 1 < second_next[0]
    return endpoint, next_endpoint, first, first_next, second, second_next


def grid_kappa(bit_saving, eta=ETA):
    q = bit_saving * (1 - 2*eta)
    minimum = (1 - eta) * q / (1 + q)
    ticks = minimum * GRID
    return Q((ticks.numerator - 1) // ticks.denominator, GRID)


def compute(native_price, repository):
    cost = load("moment", source_path(repository, "moment"))
    other = load("independent_moment", source_path(repository, "base_two_moment"))
    outer = load("outer", source_path(repository, "outer"))
    profile = native_price["cohort_candidate"]
    histogram = {int(k): int(v) for k, v in profile["histogram"].items()}
    m, stock, calls = M, int(profile["stock"]), int(profile["calls"])
    rank_mass, deficit = int(profile["rank_mass"]), int(profile["deficit"])
    assert (stock, calls, rank_mass, deficit) == (173435, 3956840, 20777000, 35200)
    assert sum(histogram.values()) == calls
    assert sum(r*n for r, n in histogram.items()) == rank_mass
    assert max(histogram) == 50 < m//2
    assert Q(profile["coarse"]) == BASE_COARSE
    assert Q(profile["kappa"]) == BASE_KAPPA
    assert RHO == Q(3456000, PRIME) < Q(1, 10**16)
    assert PRIME > 2**80

    coarse_endpoint, coarse_next, first, first_next, second, second_next = certify_coarse(
        histogram, m, stock, calls, cost, other)
    cap = grid_kappa(coarse_endpoint)

    # Reproduce PR259's published three-level bit bound before extending it.
    base_chain = [INITIAL_LEAF]
    for _ in range(3):
        base_chain.append((1 - BASE_COARSE) * BASE_COARSE + BASE_COARSE * base_chain[-1])
    assert [str(x) for x in base_chain] == profile["bootstrap_chain"]
    assert Q(profile["ordinary_bit"]) == base_chain[-1]

    chain = [INITIAL_LEAF]
    gap_records = []
    level = 0
    while True:
        old = chain[-1]
        new = (1 - coarse_endpoint) * coarse_endpoint + coarse_endpoint * old
        assert old < new < coarse_endpoint < 1 - new
        gaps = dict(atom=coarse_endpoint-new, borrowing=1-new-coarse_endpoint,
                    remainder=1-new-coarse_endpoint*(1-old), stock=1-coarse_endpoint)
        assert min(gaps.values()) > 0
        chain.append(new)
        level += 1
        candidate = grid_kappa(new)
        assert candidate <= cap
        gap_records.append(dict(level=level, gaps=gaps, minimum_gap=min(gaps.values())))
        if candidate == cap:
            break
        assert level < 20, "finite ordinary chain did not reach the coarse grid cap"
    assert level == 8

    bridge = bridge_template()
    assert bridge["rows"]["degree_gap"] > 0
    old_eta = Q(1, 10**12)
    old_eta_cap = grid_kappa(coarse_endpoint, old_eta)
    old_eta_chain = [INITIAL_LEAF]
    while grid_kappa(old_eta_chain[-1], old_eta) != old_eta_cap:
        old_eta_chain.append((1 - coarse_endpoint) * coarse_endpoint
                             + coarse_endpoint * old_eta_chain[-1])
        assert len(old_eta_chain) < 20
    old_eta_assembly = outer.assembly(old_eta_chain[-1], COMPLEX_SAVING, bridge,
                                     old_eta_cap, eta=old_eta, beta=BETA)

    base_assembly = outer.assembly(base_chain[-1], COMPLEX_SAVING, bridge, BASE_KAPPA,
                                   eta=Q(1, 10**12), beta=BETA)
    assert len(base_assembly["strict_constraints"]) == 47
    assert len(base_assembly["margins"]) == 7
    assembly = outer.assembly(chain[-1], COMPLEX_SAVING, bridge, cap, eta=ETA, beta=BETA)
    assert len(assembly["strict_constraints"]) == 47
    assert len(assembly["margins"]) == 7
    assert all(v > 0 for v in assembly["strict_constraints"].values())
    assert all(v > cap for v in assembly["margins"].values())
    for bit_saving in (chain[-1], coarse_endpoint):
        try:
            outer.assembly(bit_saving, COMPLEX_SAVING, bridge, cap + Q(1, GRID),
                           eta=ETA, beta=BETA)
        except AssertionError:
            continue
        raise AssertionError("adjacent 10^-27 kappa point passed")

    gain = cap - BASE_KAPPA
    assert gain > 0
    assert cap == Q(711029389987426878345881, 10**27)
    assert gain == Q(3933391878345881, 10**27)
    return serial(dict(
        schema="multicut-kernel-condensation-fixed-prime-mathematics/1",
        base_candidate=dict(commit=BASE_COMMIT,
                            kappa=BASE_KAPPA, package="research/multicut-kernel-condensation"),
        fixed_prime=dict(value=PRIME, greater_than=2**80, density=RHO,
                         density_formula="2*m^3/q", density_below_inherited_10_to_minus_16=True),
        bit_profile=dict(m=m, stock=stock, calls=calls, rank_mass=rank_mass, deficit=deficit,
                         maxchild=max(histogram), histogram=histogram, physical_replicas=40,
                         literal_stock=867175, normalization=5),
        complex_saving=COMPLEX_SAVING,
        coarse_rate=dict(exact_grid_rate=coarse_endpoint, bracket=[coarse_endpoint, coarse_next],
                         first_engine_interval=first, first_engine_next_interval=first_next,
                         second_engine_interval=second, second_engine_next_interval=second_next),
        ordinary_bootstrap=dict(initial=chain[0], levels=level, chain=chain, gaps=gap_records,
                                grid_cap_from_coarse_endpoint=cap,
                                prior_three_level_chain=base_chain,
                                eta_1e_12_levels=len(old_eta_chain)-1,
                                eta_1e_12_kappa=old_eta_cap,
                                eta_1e_12_chain=old_eta_chain,
                                eta_gain=cap-old_eta_cap,
                                eta_1e_12_assembly=old_eta_assembly),
        finite_bridge=bridge, base_assembly=base_assembly, assembly=assembly,
        kappa=cap, baseline_kappa=BASE_KAPPA, exact_gain=gain,
        adjacent_grid_point_rejected_at_finite_saving=True,
        adjacent_grid_point_rejected_at_coarse_cap=True, binding="bit"))


def ceil_fraction(value):
    assert value >= 0
    return (value.numerator + value.denominator - 1) // value.denominator


def audit_finite_admission(mathematics, profile, invoice, repository):
    m = int(mathematics["bit_profile"]["m"])
    stock = int(profile["stock"])
    calls = int(profile["calls"])
    mass = int(profile["rank_mass"])
    coefficient = int(invoice["full_counted_primitive_coefficient"])
    assert coefficient == 62639910650427201
    assert coefficient < 2**80 < PRIME
    assert stock < PRIME
    assert invoice["normalized_stock"] == stock == 173435
    assert invoice["literal_stock"] == 5 * stock == 867175
    assert invoice["physical_replicas"] == 40
    assert int(invoice["literal_rank_mass"]) == 5 * mass
    literal_calls = sum(int(v) for v in invoice["literal_histogram"].values())
    assert literal_calls == 5 * calls
    assert int(invoice["literal_deficit"]) == 5 * int(profile["deficit"])
    assert invoice["extra_selector_calls"] == "626937381600"
    assert invoice["new_chart_factor_max"] == 200
    assert invoice["normalizer_factor_bound"] == 787
    assert invoice["external_complex_row_coefficient"] == 20161
    assert invoice["internal_row_coefficient"] == 14401
    assert int(invoice["payload_signed_prefix_upper"]) == 288331034813990688642823008000
    assert int(invoice["payload_signed_prefix_upper"]) < 2**104

    coarse = Q(mathematics["coarse_rate"]["exact_grid_rate"])
    hist = {int(k): int(v) for k, v in profile["histogram"].items()}
    cost = load("moment", source_path(repository, "moment"))
    at_coarse = fixed_moment(hist, m, stock, calls, coarse, cost)
    delta_tau = 1 - at_coarse[1]
    delta_linear = 1 - Q(mass, m*stock) - RHO * Q(32*m*calls, stock)
    assert delta_tau > 0 and delta_linear > 0

    log_coefficient = (coefficient - 1).bit_length()
    cutoffs = []
    for row in mathematics["ordinary_bootstrap"]["gaps"]:
        gaps = {name: Q(value) for name, value in row["gaps"].items()}
        delta = min(gaps.values())
        log_cutoff = max(1, ceil_fraction(Q(36, 1) / delta**2),
                         ceil_fraction(Q(2 * (4 + log_coefficient), 1) / delta))
        assert Q(log_cutoff) * delta**2 >= 36
        assert Q(log_cutoff) * delta >= 2 * (4 + log_coefficient)
        cutoffs.append(dict(level=row["level"], minimum_gap=delta,
                            log2_cutoff=log_cutoff))

    return serial(dict(
        status="PASS_FIXED_PRIME_FINITE_ADMISSION",
        q_power_coefficient=coefficient,
        q_power_coefficient_below_prime=True,
        literal_inventory=dict(stock=invoice["literal_stock"], calls=literal_calls,
                               rank_mass=invoice["literal_rank_mass"], replicas=40),
        moment_gaps=dict(delta_tau=delta_tau, delta_linear=delta_linear,
                         rare_density=RHO, full_fallback_kept=True),
        finite_cutoff_checks=cutoffs,
        inherited_costs=dict(extra_selector_calls=invoice["extra_selector_calls"],
                             max_new_chart_factors=invoice["new_chart_factor_max"],
                             normalizer_factor_bound=invoice["normalizer_factor_bound"],
                             external_complex_row_coefficient=invoice["external_complex_row_coefficient"],
                             internal_row_coefficient=invoice["internal_row_coefficient"],
                             signed_prefix_upper=invoice["payload_signed_prefix_upper"]),
        scope="Exact fixed-prime density and finite levels on PR259's 518-entrance multicut word; inherited public all-size, address, compiler, row and complex interfaces remain conditional."))
