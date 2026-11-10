"""Independent five-stage source/error/transition observer.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Payloads here are externally observed words. This module is never an online
service and must not manufacture a physical stage's output.
"""
from fractions import Fraction as Q
from hashlib import sha256
from independent_numerics import (
    apply_axis, canonical_json, column_norm, decode_pairs, exact_complete_target,
    five_factors, fraction_digest, need, pow2, row_norm, squared_error, squared_norm,
)

KINDS = ("dense_inverse_1", "sparse_lower", "dense_forward",
         "sparse_upper", "dense_inverse_2")


def product(values):
    answer = Q(1)
    for value in values:
        answer *= value
    return answer


def check_words(values, width):
    need(type(width) is int and width >= 2, "declared physical signed width")
    need(all(len(z) == 2 and all(type(x) is int and -(1 << (width - 1)) <= x
                               < 1 << (width - 1) for x in z) for z in values),
         "every observed component fits its actual signed width")


def stage_target(family, previous, stage):
    axes, side = len(family[0]), len(family[0][0]["target"])
    volume = side ** axes
    answer = []
    for c in range(len(family)):
        state = tuple(previous[c * volume:(c + 1) * volume])
        for axis in range(axes):
            state = apply_axis(family[c][axis]["factors"][stage], state, axis, axes)
        answer.extend(state)
    return tuple(answer)


def check_stages(source_contexts, interiors, initial_words, initial_precision,
                 observations, local_error_bounds, final_target, *, broad=False,
                 common_precision=None):
    """Compare all actual transitions and independently reconstruct source targets.

    Context axes are LOW-coordinate-first; reverse the router's source list
    explicitly. Each observation has kind,input,output,input_precision,
    output_precision,input_width,output_width. Optional input_radius is a
    whole-field Euclidean promise. local_error_bounds must come from source
    certificates prepared before payload execution, not observed error fitting.
    """
    need(len(observations) == len(local_error_bounds) == 5,
         "all five actual stage observations and source budgets")
    need(len(source_contexts) == len(interiors) > 0, "all actual source contexts")
    family = []
    for source, ids in zip(source_contexts, interiors):
        need(len(source) == len(ids) > 0, "every actual axis and partition")
        family.append(tuple(five_factors(q, part, broad=broad)
                            for q, part in zip(source, ids)))
    axes, side = len(family[0]), len(family[0][0]["target"])
    records = len(family) * side ** axes
    need(len(initial_words) == records, "complete observed initial field")
    original = decode_pairs(initial_words, initial_precision)
    previous = original
    norms = tuple(max(product(max(row_norm(axis["factors"][s]),
                                 column_norm(axis["factors"][s])) for axis in context)
                      for context in family) for s in range(5))
    allowances = tuple(map(Q, local_error_bounds))
    need(all(e >= 0 for e in allowances), "nonnegative source error certificates")
    rows = []
    for stage, observed in enumerate(observations):
        need(observed["kind"] == KINDS[stage], "actual five-factor stage order")
        need(len(observed["input"]) == len(observed["output"]) == records,
             "no omitted context or row at service boundary")
        check_words(observed["input"], observed["input_width"])
        check_words(observed["output"], observed["output_width"])
        pin, pout = observed["input_precision"], observed["output_precision"]
        if common_precision is not None:
            need(pin == pout == common_precision, "unchanged common grid")
        current, returned = decode_pairs(observed["input"], pin), decode_pairs(observed["output"], pout)
        need(current == previous, "actual current field survives adapters without boundary reset")
        if "input_radius" in observed:
            radius = Q(observed["input_radius"])
            need(radius >= 0 and squared_norm(current) <= radius ** 2,
                 "actual complete input satisfies declared provider radius")
        exact = stage_target(family, current, stage)
        error = squared_error(returned, exact)
        need(error <= allowances[stage] ** 2,
             "actual stage defect fits its precomputed source certificate")
        drift = 0
        if stage in (0, 2, 4):
            volume = side ** axes
            for c, context in enumerate(family):
                for local in range(volume):
                    digits = tuple((local // (side ** a)) % side for a in range(axes))
                    if all(digit in axis["J"] for digit, axis in zip(digits, context)):
                        index = c * volume + local
                        need(exact[index] == current[index], "exact dense all-boundary identity")
                        drift += int(returned[index] != current[index])
        rows.append(dict(kind=KINDS[stage], error_squared=fraction_digest(error),
                         source_allowance=fraction_digest(allowances[stage]),
                         actual_boundary_drift_records=drift,
                         input_sha256=sha256(canonical_json(observed["input"]).encode()).hexdigest(),
                         output_sha256=sha256(canonical_json(observed["output"]).encode()).hexdigest(),
                         input_width=observed["input_width"], output_width=observed["output_width"]))
        previous = returned
    propagated = sum((allowances[s] * product(norms[s + 1:]) for s in range(5)), Q())
    need(propagated <= pow2(-final_target), "complete source-certified five-factor error invoice")
    exact_final = exact_complete_target(source_contexts, original, broad=broad)
    error = squared_error(previous, exact_final)
    need(error <= propagated ** 2, "output fits independently propagated source budget")
    nonidentity = sum(int(axis["A"] != tuple(tuple(Q(i == j) for j in range(len(axis["A"])))
                                               for i in range(len(axis["A"]))))
                      for context in family for axis in context)
    return dict(status="PASS_INDEPENDENT_FIVE_STAGE_NUMERICS", records=records,
                contexts=len(family), axes=axes, nonidentity_interior_axes=nonidentity,
                stages=rows, source_bound=fraction_digest(propagated),
                final_error_squared=fraction_digest(error), target_bits=final_target,
                original_matrix_target=True, actual_transition_continuity=True)
