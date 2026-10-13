"""Independent exact arithmetic for the historical bit-compression screen.

Only the Python standard library is imported.  Circuit node classifications,
merge counts, and frame assertions are certificate inputs here, not independently
proved circuit facts.  In particular, this checker cannot turn finite replay
into a proof of the paired-template obstruction for every ground size.

The logarithm enclosure is derived from log(x) = 2*atanh((x-1)/(x+1)).
After writing n = 2**k * y with 1 <= y < 2, each series argument is in
[0, 1/3].  For N terms its nonnegative omitted tail is at most
2*z**(2*N+1)/((2*N+1)*(1-z*z)); this follows by replacing every omitted
denominator with 2*N+1 and summing a geometric series.  N=24 reproduces the
historical rational precision without calling or importing its log routine.
"""

from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb


TARGET = Fraction(1, 2**30)
SCOPE = (
    "Existing paired local template, arbitrary independent relabelings, "
    "equal-sum identification and pruning only; c+q compiler, separate "
    "partial outputs and original central losses retained."
)


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _integer(record, key, context):
    value = record[key]
    _require(type(value) is int and value >= 0,
             f"{context}.{key}: expected a nonnegative integer")
    return value


def _rational(record, key, context):
    value = record[key]
    _require(type(value) is str, f"{context}.{key}: expected a rational string")
    result = Fraction(value)
    _require(str(result) == value, f"{context}.{key}: noncanonical rational")
    return result


def _equal(actual, expected, context):
    _require(actual == expected, f"{context}: does not match independent arithmetic")


@lru_cache(maxsize=None)
def _log_bounds(n):
    """Return rational lower/upper enclosures without floating-point operations."""
    _require(type(n) is int and n > 1, "log argument must be an integer > 1")
    exponent = n.bit_length() - 1
    reduced = Fraction(n, 2**exponent)
    result = [Fraction(0), Fraction(0)]
    for multiplier, argument in (
        (exponent, Fraction(1, 3)),
        (1, (reduced - 1) / (reduced + 1)),
    ):
        lower = sum(
            (2 * argument**power / power for power in range(1, 48, 2)),
            Fraction(0),
        )
        remainder = 2 * argument**49 / (49 * (1 - argument**2))
        result[0] += multiplier * lower
        result[1] += multiplier * (lower + remainder)
    _require(0 < result[0] < result[1], "invalid independent log enclosure")
    return tuple(result)


def _network(h, roles):
    vertices = comb(h, 3)
    m = h**3
    width = 2 * vertices**2 * (vertices + roles + h)
    deficit = vertices**2 * (vertices - 6 * h**2)
    eta = Fraction(deficit, width * m)
    _require(0 < eta < 1, f"h={h}: deficit ratio is outside (0, 1)")
    log_lower, log_upper = _log_bounds(m)
    return eta, log_lower, log_upper


def _strict_integer_budget(h, log_lower):
    """Largest integer R satisfying the strict favorable saving requirement."""
    vertices = comb(h, 3)
    qlog = 5 * TARGET * log_lower
    # Cancel v**2 from D and W before solving the inequality for R.
    threshold = (
        Fraction(vertices - 6 * h**2, 2 * h**3) * (1 + qlog) / qlog
        - vertices - h
    )
    return (threshold.numerator - 1) // threshold.denominator


def _bound_row(row, h, context):
    _equal(_integer(row, "h", context), h, context + ".h")
    additions = _integer(row, "local_additions", context)
    unshareable = _integer(row, "unshareable", context)
    stars = _integer(row, "stars", context)
    frontier = _integer(row, "mandatory_frontier_stars", context)
    _equal(additions, unshareable + stars, context + ".classification partition")
    _require(frontier <= stars, context + ": frontier exceeds all star nodes")
    outputs = comb(h - 1, 2)
    _require(unshareable >= outputs, context + ": fewer unshareable nodes than outputs")
    roles = h * unshareable + (h * frontier + 1) // 2 + h * outputs
    _equal(_integer(row, "side_roles_lower", context), roles, context + ".side_roles_lower")
    eta, log_lower, _ = _network(h, roles)
    saving = eta / ((1 - eta) * log_lower)
    for field, expected in (
        ("bit_saving_upper", saving),
        ("kappa_upper", saving / 5),
        ("fraction_of_target", saving / (5 * TARGET)),
    ):
        _equal(_rational(row, field, context), expected, context + "." + field)
    _equal(_integer(row, "necessary_integer_role_budget", context),
           _strict_integer_budget(h, log_lower), context + ".necessary_integer_role_budget")
    _require(saving / 5 < TARGET, context + ": favorable bound reaches target")
    return saving


def _config_key(config):
    _require(type(config) is dict, "configuration must be an object")
    _require(all(type(key) is str for key in config), "configuration keys must be strings")
    _require(all(type(value) in (str, int) for value in config.values()),
             "configuration values must be strings or integers")
    return tuple(sorted(config.items()))


def _block(k=2, leaf=4, vec="prefix", order=0, assoc=0):
    return _config_key(dict(family="block", k=k, leaf=leaf, vec=vec,
                            order=order, assoc=assoc))


def _expected_local_configs():
    result = {_config_key(dict(family="filter", kind=kind))
              for kind in ("balanced", "vertex")}
    result.update(_block(k=k, leaf=leaf, vec=vec)
                  for k, leaf, vec in product((2, 3, 4, 6, 8), (3, 4, 6, 8),
                                              ("prefix", "tree", "paired")))
    result.update(_block(order=order, assoc=assoc)
                  for order, assoc in product(range(3), range(4)))
    return result


def _indexed_rows(rows, expected_configs, context):
    _require(type(rows) is list, context + ": expected a list")
    indexed = {}
    for row in rows:
        key = _config_key(row["config"])
        _require(key not in indexed, context + ": duplicate configuration")
        indexed[key] = row
    _equal(set(indexed), expected_configs, context + ".configuration coverage")
    return indexed


def _check(certificate):
    _require(type(certificate) is dict, "certificate must be an object")
    _equal(_rational(certificate, "target", "certificate"), TARGET, "target")
    _equal(_rational(certificate, "current_bit_saving", "certificate"),
           Fraction(296, 10**11), "current_bit_saving")
    _equal(certificate["status"],
           "BOUNDED NEGATIVE SCREEN; NO NEW MULTIPLICATION WITNESS", "status")

    local = _indexed_rows(certificate["local_candidates"], _expected_local_configs(),
                          "local_candidates")
    _equal(len(local), 73, "local_candidates.count")
    for number, row in enumerate(certificate["local_candidates"]):
        context = f"local_candidates[{number}]"
        bound = row["optimistic_merging_bound"]
        _bound_row(bound, 50, context + ".optimistic_merging_bound")
        _equal(_integer(row, "local_roles", context),
               bound["local_additions"] + comb(49, 2), context + ".local_roles")

    global_expected = {_block(leaf=leaf, vec=vec, order=order)
                       for leaf, vec, order in product((3, 4),
                                                       ("prefix", "tree", "paired"),
                                                       range(3))}
    global_rows = _indexed_rows(certificate["global_candidates"], global_expected,
                                "global_candidates")
    _equal(len(global_rows), 18, "global_candidates.count")
    globals_with_local_counts = 0
    for number, row in enumerate(certificate["global_candidates"]):
        context = f"global_candidates[{number}]"
        roles = _integer(row, "side_roles", context)
        merged = _integer(row, "merged_additions", context)
        _require(roles >= 6 * comb(50, 3), context + ": violates distinct-output role floor")
        eta, log_lower, log_upper = _network(50, roles)
        _equal(_rational(row, "bit_saving_lower", context), eta / log_upper,
               context + ".bit_saving_lower")
        upper = eta / ((1 - eta) * log_lower)
        _equal(_rational(row, "bit_saving_upper", context), upper,
               context + ".bit_saving_upper")
        _require(upper / 5 < TARGET, context + ": favorable bound reaches target")
        key = _config_key(row["config"])
        if key in local:
            bound = local[key]["optimistic_merging_bound"]
            # Interning precedes liveness pruning.  Merges alone do not account
            # for every reduction in the final active-addition count.
            before_pruning = 50 * bound["local_additions"] - merged + 50 * comb(49, 2)
            _require(roles <= before_pruning, context + ": roles exceed unpruned count")
            _require(roles >= bound["side_roles_lower"], context + ": roles violate local bound")
            globals_with_local_counts += 1

    best = min(certificate["global_candidates"], key=lambda row: row["side_roles"])
    _equal(certificate["best_global"], best, "best_global")
    _equal(best["side_roles"], 509146, "best_global.side_roles")
    baseline = global_rows[_block()]
    _equal(baseline["side_roles"], 509194, "paired baseline roles")
    _equal(_rational(certificate, "role_improvement_ratio", "certificate"),
           Fraction(baseline["side_roles"], best["side_roles"]), "role_improvement_ratio")

    symbolic = certificate["best_global_symbolic_check"]
    expected_symbolic = dict(h=50, inputs=comb(50, 3),
                             partial_outputs=50 * comb(49, 2),
                             additions=best["side_roles"] - 50 * comb(49, 2),
                             roles=best["side_roles"], merged_additions=best["merged_additions"])
    for key, value in expected_symbolic.items():
        _equal(_integer(symbolic, key, "best_global_symbolic_check"), value,
               "best_global_symbolic_check." + key)
    for key in ("all_additions_disjoint", "all_partial_outputs_exact", "every_node_has_common_point"):
        _require(symbolic[key] is True, "recorded symbolic flag is not true: " + key)
    frames = certificate["best_global_frame_check"]
    _equal(_integer(frames, "roles", "best_global_frame_check"), best["side_roles"],
           "best_global_frame_check.roles")
    for key in ("forward_frames_nested", "reverse_complement_frames_nested"):
        _require(frames[key] is True, "recorded frame flag is not true: " + key)

    paired = certificate["paired_template_all_even_h"]
    _equal(paired["scope"], SCOPE, "paired_template_all_even_h.scope")
    finite = paired["finite"]
    _require(type(finite) is list, "paired finite coverage must be a list")
    _equal([row["h"] for row in finite], list(range(40, 112, 2)), "paired finite coverage")
    savings = [_bound_row(row, h, f"paired.finite[{number}]")
               for number, (h, row) in enumerate(zip(range(40, 112, 2), finite))]
    peak = finite[max(range(len(finite)), key=lambda index: savings[index])]
    _equal(paired["finite_peak"], peak, "paired.finite_peak")
    _equal(peak["h"], 52, "paired peak ground size")
    row50 = finite[5]
    _equal({key: row50[key] for key in (
        "unshareable", "mandatory_frontier_stars", "side_roles_lower", "necessary_integer_role_budget")},
        dict(unshareable=4389, mandatory_frontier_stars=2304,
             side_roles_lower=335850, necessary_integer_role_budget=317035), "paired h=50 checkpoint")
    _equal(row50, local[_block()]["optimistic_merging_bound"], "paired h=50 local correspondence")

    _equal(_integer(paired, "nonpositive_deficit_below", "paired"), 40,
           "paired.nonpositive_deficit_below")
    for h in range(6, 40, 2):
        _require(comb(h, 3) - 6 * h**2 <= 0, f"h={h}: positive small-ground deficit")
    _equal(_integer(paired, "tail_cutoff", "paired"), 112, "paired.tail_cutoff")
    log_lower, _ = _log_bounds(112**3)
    tail = 1 / ((14 * 112**3 - 1) * log_lower)
    _equal(_rational(paired, "tail_bit_saving_upper", "paired"), tail,
           "paired.tail_bit_saving_upper")
    _require(tail < 5 * TARGET, "paired tail endpoint does not exclude target")
    # The infinite-tail step is conditional on the written circuit argument:
    # distinct unshareable outputs give c >= 3v and output uses q = 3v, hence
    # R >= 6v. Then W >= 14v**3 and eta < 1/(14*h**3).  Both positive factors
    # of (14*h**3-1)*log(h**3) increase for h >= 112, so its reciprocal
    # decreases.  The rational check above establishes its endpoint estimate;
    # it does not establish distinctness/unshareability for all h by replay.
    return dict(
        status="PASS: independent arithmetic; circuit counts are certificate inputs",
        local_rows_checked=len(local), global_rows_checked=len(global_rows),
        global_rows_with_matching_local_count_rows=globals_with_local_counts,
        paired_finite_rows_checked=len(finite), paired_finite_range=[40, 110, 2],
        paired_peak_h=peak["h"], tail_cutoff=112,
        paired_h50_unshareable=4389, paired_h50_frontier=2304,
        paired_h50_role_floor=335850, target_h50_integer_role_budget=317035,
        baseline_roles=509194, best_roles=509146, role_reduction=48,
        log_method="24-term rational atanh series with geometric remainder",
        scope=SCOPE,
        limitations=[
            "U/F, local additions, and merge counts require circuit replay or separate proof.",
            "Recorded symbolic and frame flags are cross-checked, not proved by this module.",
            "Infinite-tail circuit hypotheses are a written argument, not finite replay.",
            "No all-size theorem, general optimality, or new multiplication witness is certified.",
        ],
    )


def check(certificate: dict) -> dict:
    """Return a deterministic JSON-compatible summary, or raise ValueError."""
    try:
        return _check(certificate)
    except (KeyError, TypeError, IndexError, ZeroDivisionError, OverflowError) as error:
        raise ValueError(f"malformed arithmetic certificate: {error}") from error
