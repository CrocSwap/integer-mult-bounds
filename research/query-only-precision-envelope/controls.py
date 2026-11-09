"""Bounded adverse controls for source guards and the numerical contract seam.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as F
from source_binding import need, sources
from envelopes import validate_word, native_envelope, caller_envelope, native_adjoint


def run():
    caller, word = sources()
    rejected = []

    def reject(label, f):
        try:
            f()
        except ValueError:
            rejected.append(label)
            return
        raise ValueError("negative control was accepted: " + label)

    mutant = deepcopy(word)
    mutant["program"][37476][2] = 3
    reject("wrong_actual_MOVE_source_frame", lambda: validate_word(mutant))
    mutant = deepcopy(word)
    mutant["program"][37476][4] = True
    reject("public_MOVE_mislabelled_owned", lambda: validate_word(mutant))
    mutant = deepcopy(word)
    mutant["frames"][0].append(mutant["frames"][0][0])
    reject("dependent_chart_basis", lambda: validate_word(mutant))
    mutant = deepcopy(word)
    cut = next(i for i, e in enumerate(mutant["program"]) if e[0] == "CLEAR")
    mutant["program"][cut][1] = 0
    reject("CLEAR_erases_public_field", lambda: validate_word(mutant))
    wp, _ = native_envelope(word)
    mutant = deepcopy(caller)
    cut = next(i for i, e in enumerate(mutant["events"]) if e[0] == "J")
    mutant["events"][cut][1] = 2
    reject("joint_stage_order_changed", lambda: caller_envelope(mutant, wp, word))
    mutant = deepcopy(caller)
    cut = next(i for i, e in enumerate(mutant["events"]) if e[1] == "QUERY")
    mutant["events"][cut][1] = "QSELF"
    reject("nonretained_QSELF_reintroduced", lambda: caller_envelope(mutant, wp, word))
    # Adjoint unit tests expose exactly which operation injects a residual. These
    # tiny words do not pretend to satisfy the full frozen-source lifecycle.
    tiny = dict(public=2, owned_fields=0, program=[["ADD", 0, 1, "1/2", 0]])
    mass, error, active = native_adjoint(tiny, dict(register=0, factor="1", cut=1))
    need((mass, error, active) == (F(3, 2), F(1), 1), "noninteger ADD site retained")
    tiny["program"].append(["CLEAR", 0, 0])
    need(native_adjoint(tiny, dict(register=0, factor="1", cut=2)) == (0, 0, 0),
         "zeroing kills every earlier error channel")
    # Exact Gaussian arithmetic represented by (real, imaginary) rational pairs.
    def add(z, w): return (z[0] + w[0], z[1] + w[1])
    def mul(z, w): return (z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0])
    def norm2(z): return z[0] ** 2 + z[1] ** 2
    c00, c01 = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))
    need(norm2(add(c00, mul(c01, (0, 1)))) == 2,
         "unitary Gaussian can amplify coordinate-sup norm")
    need(norm2(c00) + norm2(c01) == 1, "same Gaussian row has Euclidean norm one")
    # Q=(3+4i)/5 is unitary but not order four. Lambda need not be unitary.
    q = (F(3, 5), F(4, 5))
    lam = add(c00, mul(c01, mul(q, q)))
    need(norm2(q) == 1 and norm2(lam) == F(49, 25), "Q^4 premise is necessary for Lambda norm one")
    need((F(1) + -1) / 2 == 0, "projector Lambda vanishes in q=i sector")
    def rdiv(a, b, m): return (a * m + b // 2) // b
    need(rdiv(1, 2, 1) == 1 and rdiv(1, 2, -1) == 0,
         "nearest RDiv with upward ties is not odd")
    return dict(source_mutants_rejected=rejected,
                exact_controls=["noninteger_ADD_residual_channel", "CLEAR_kills_earlier_residual",
                                "unitary_is_not_coordinate_sup_contractive", "Lambda_requires_Q_fourth_power",
                                "projector_is_not_Lambda", "RDiv_tie_rule_is_not_sign_symmetric"],
                physical_and_precision_controls="BOUNDARY.json and GUARDS.json include further rejection controls")
