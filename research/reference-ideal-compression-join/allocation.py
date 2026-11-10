"""Exact rational part of the stated source/interface invoice.

This is a bounded research checker, not a replacement physical constructor.
The analytic alpha law, source ownership and primitive services remain the
written theorem's explicit premises. Prepared for @CubeJerry with OpenAI
assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from functools import reduce
from operator import mul


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pow2(exponent):
    need(type(exponent) is int, "integer binary exponent")
    return Q(1 << exponent) if exponent >= 0 else Q(1, 1 << -exponent)


def ceil_log2(value):
    value = Q(value)
    need(value > 0, "positive rational logarithm")
    k = value.numerator.bit_length() - value.denominator.bit_length()
    return k + int(pow2(k) < value)


def source_target(group_count, tau, gamma):
    need(type(group_count) is int and group_count > 0 and
         type(tau) is int and tau >= 1 and type(gamma) is int and gamma >= 0,
         "source-first external descriptors")
    z = tau + gamma + ceil_log2(group_count) + 1
    return {"z": z, "eta": pow2(-z), "target_bits": z+2}


def bind_reference(ref, p, initial_radius, core_target):
    """Check exact source parts; the alpha law is separately certified."""
    need(type(p) is int and p >= 2 and initial_radius >= 1,
         "positive source family/radius")
    need(Q(1, 4*p*p) <= ref.theta <= Q(1, p*p), "actual fine theta")
    need(ref.allocation is not None, "actual immutable for_cap source")
    need(Q(ref.allocation["radius"]) >= 2*initial_radius,
         "source radius covers the bridge input radius")
    need(ref.allocation["target_bits"] >= core_target,
         "source target covers actual Core target")
    delta, error = ref.narrow_gap, ref.errors["narrow"]
    need(Q(1, 16*p*p) < delta < 1 and 0 <= error < 1-delta,
         "literal positive reference and ideal inverse certificate")
    bits = ref.allocation["error_bits"]
    source_bits = ref.allocation["target_bits"]
    need(bits >= source_bits+46+ceil_log2(initial_radius*p*p),
         "actual cap allocation pays incoming radius")
    need(error <= pow2(-bits), "actual full periodic reference error")
    return {"gap": delta, "reference_error": error,
            "ideal_gap": delta+error, "normalizer_bits": ceil_log2(1/delta),
            "error_bits": bits, "source_target_bits": source_bits}


def group_invoice(gaps, errors, normalizer_bits, diagonal_bits, caller_bits):
    size = len(gaps)
    need(size > 0 and all(len(x) == size for x in
                         (errors, normalizer_bits, diagonal_bits)), "matched complete axes")
    need(all(0 < d < 1 and 0 <= e < 1-d for d, e in zip(gaps, errors)),
         "same-certificate inverse margins")
    need(all(type(u) is int and u >= 0 and pow2(u)*d >= 1
             for u, d in zip(normalizer_bits, gaps)), "actual inverse normalizers")
    need(all(type(v) is int and v >= 0 for v in diagonal_bits), "diagonal norm exponents")
    u, v = sum(normalizer_bits), sum(diagonal_bits)
    need(type(caller_bits) is int and caller_bits >= u+v,
         "remaining diagonal and complete group contract")
    c = pow2(u+v-caller_bits)
    mu = pow2(v-caller_bits) * reduce(mul, (1/Q(d) for d in gaps), Q(1))
    xi = mu * sum((Q(e)/(d+e) for d, e in zip(gaps, errors)), Q())
    need(mu <= c <= 1, "exact normalized group contraction")
    need(mu*size*pow2(u) <= pow2(42), "unmodified-target reference slack")
    return {"normalizer_bits": u, "diagonal_bits": v, "caller_bits": caller_bits,
            "remaining_norm": c, "complete_norm": mu, "reference_defect": xi,
            "slack_gate": mu*size*pow2(u)}


def combined_invoice(budget, groups, initial_radius):
    """Consume the unchanged public ledger's allocation, not a new t/q rule."""
    eta, q = budget["local_bridge_allowance"], budget["grid_bits"]
    need(len(groups) == len(budget["core_targets"]), "same actual groups")
    diagonal_error = (3*initial_radius+2)*pow2(-q)
    need(diagonal_error <= 3*eta/4, "actual remaining service leaves reference room")
    physical = sum((g["remaining_norm"]*eta+diagonal_error for g in groups), Q())
    reference = initial_radius*sum((g["reference_defect"] for g in groups), Q())
    need(reference <= len(groups)*eta/4, "actual source comparison fits old allocation")
    total = physical+reference
    need(total <= 2*len(groups)*eta, "complete old normalized allowance")
    restored = pow2(budget["final_restoration_bits"])*total
    need(restored <= budget["restored_total_allowance"], "unchanged final restoration")
    return {"physical_bound": physical, "reference_bound": reference,
            "normalized_bound": total, "restored_bound": restored,
            "wrapper_bound": diagonal_error, "source_budget": eta/4}
