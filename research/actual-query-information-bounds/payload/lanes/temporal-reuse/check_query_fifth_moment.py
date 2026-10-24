"""Check the remaining fifth-order route word and its exact rank bound."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import importlib.util
import json


HERE = Path(__file__).resolve().parent
FOURTH_CHECKER_PIN = "e7ff30dfdc23dd929599c05aa037a082060906021d5e9a40e9f586e680d0449e"
FOURTH_RECEIPT_PIN = "df32110bbd285e3036bdb2082e3307b24edc7515953cab7a1b3b6b684adc1e66"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def trace_word(word):
    w = list(word)
    while len(w) > 1:
        remove = next((i for i in range(len(w)) if w[i] == w[(i+1) % len(w)]), None)
        if remove is None:
            break
        w.pop(remove)
    if len(w) == 1:
        return Q(8)
    if len(w) == 2:
        return Q(2, 3)
    counts = Counter(w)
    if len(w) == 4 and len(counts) == 2:
        return Q(23, 216)
    unique = next((i for i, s in enumerate(w) if s and counts[s] == 1), None)
    if unique is not None:
        w.pop(unique)
        return trace_word(w)/12
    need(len(w) == 5 and counts[0] == 1 and sorted(counts.values()) == [1, 2, 2],
         "An unsupported fifth-order word remains")
    return Q(23, 2592)


def composition_sum(moments, total, factors):
    if factors == 0:
        return Q(total == 0)
    return sum((moments[i]*composition_sum(moments, total-i, factors-1)
                for i in range(total+1)), Q(0))


def free_moment_comparison():
    """Check only the finite noncrossing moment recurrence."""
    alpha = Q(1, 12)
    bernoulli = [Q(1)]+[alpha]*5
    cumulants = [Q(0)]
    for n in range(1, 6):
        cumulants.append(alpha-sum((cumulants[k]*composition_sum(bernoulli, n-k, k)
                                    for k in range(1, n)), Q(0)))
    moments = [Q(1)]
    for n in range(1, 6):
        moments.append(sum((9*cumulants[k]*composition_sum(moments, n-k, k)
                            for k in range(1, n+1)), Q(0)))
    expected = [Q(72), Q(120), Q(244), Q(1649, 3), Q(47467, 36)]
    need([96*x for x in moments[1:]] == expected, "The finite free-moment comparison differs")
    return list(map(str, expected))


def main():
    path = HERE/"check_query_fourth_moment.py"
    need(sha256(path.read_bytes()).hexdigest() == FOURTH_CHECKER_PIN, "Fourth checker changed")
    raw = (HERE/"QUERY-FOURTH-MOMENT.json").read_bytes()
    need(sha256(raw).hexdigest() == FOURTH_RECEIPT_PIN, "Fourth receipt changed")
    spec = importlib.util.spec_from_file_location("independent_fourth", path)
    fourth = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fourth)
    roots, bases, dots, _ = fourth.source()
    terms, _ = fourth.covariance(1, 2, roots, bases, dots)
    r1 = [fourth.route(b, 1) for b in bases]
    r2 = [fourth.route(b, 2) for b in bases]
    relative = [fourth.compose(a, b) for a, b in zip(r1, r2)]
    neighbors = [[j for j in range(96) if dots[i][j]] for i in range(96)]
    need(all(len(x) == 45 for x in neighbors), "The supported degree differs")
    total = triples = matches = identity_matches = 0
    match_patterns = Counter()
    for r in range(96):
        for s in neighbors[r]:
            left = fourth.compose(relative[r], r2[s])
            for t in neighbors[s]:
                triples += 1
                key = fourth.compose(left, r1[t])
                if key not in terms:
                    continue
                matches += 1
                match_patterns[str((r == s, s == t, r == t))] += 1
                coefficient = terms[key]
                if coefficient is None:
                    identity_matches += 1
                    value = 192*dots[r][t]
                else:
                    p, q, scalar = coefficient
                    value = scalar*dots[r][p]*dots[q][t]
                total += dots[r][s]*dots[s][t]*value
    need((triples, matches, identity_matches, total) == (194400, 4320, 96, 2260992),
         "The fifth-order coefficient aggregation differs")
    fifth = Q(total, 48**5)
    need(fifth == Q(23, 2592), "The new cyclic trace differs")
    rows = []
    for k in range(1, 10):
        moments = [Q(x) for x in json.loads(raw)["fixed_source_bounds"][k-1]["moments_per_cover"]]
        moments.append(sum((trace_word(w) for w in product(range(k), repeat=5)), Q(0)))
        m1, m2, m3, m4, m5 = moments
        v1, v2 = k*m1-m2, k*m2-m3
        h11, h12, h22 = k*m2-m3, k*m3-m4, k*m4-m5
        determinant = h11*h22-h12*h12
        if determinant:
            rank = (m1+(v1*v1*h22-2*v1*v2*h12+v2*v2*h11)/determinant)/k
        else:
            rank = Q(8)
        fields = (rank.numerator+rank.denominator-1)//rank.denominator
        rows.append({"charts": k, "fifth_moment_per_cover": str(m5),
                     "weighted_quadratic_rank_per_cover": str(rank),
                     "whole_fields": fields, "eight_field_cohorts": (fields+7)//8})
    need(rows[-1]["fifth_moment_per_cover"] == "47467/36", "The nine-chart fifth moment differs")
    rank = Q(rows[-1]["weighted_quadratic_rank_per_cover"])
    need(rank == Q(15560, 273) == 57-Q(1, 273), "The fifth-moment rank bound differs")

    # A positive four-atom measure attains the moment relaxation.
    moment = [rank, Q(72), Q(120), Q(244), Q(1649, 3), Q(47467, 36)]
    for i in range(3):
        need(moment[i+3]-Q(73, 6)*moment[i+2]+Q(1459, 48)*moment[i+1]
             -Q(273, 16)*moment[i] == 0, "The extremal cubic recurrence fails")
    mass9 = (moment[2]-Q(19, 6)*moment[1]+Q(91, 48)*moment[0])/Q(2611, 48)
    need(mass9 == Q(8, 7833), "The top atom mass differs")
    interior_mass = rank-mass9
    interior_mean = (moment[1]-9*mass9)/interior_mass
    need(1 < interior_mean < 2 and 0 < mass9 < rank < 96,
         "The extremal measure is not positive")
    # Its interior nodes are (19 +/- 2 sqrt(22))/12, one in (0,1), one in (2,3).
    need(7*7 < 4*22 < 19*19 and 5*5 < 4*22 < 17*17,
         "The interior node intervals differ")
    result = {"status": "PASS_ACTUAL_QUERY_FIFTH_MOMENT",
              "fourth_checker_sha256": FOURTH_CHECKER_PIN,
              "fourth_receipt_sha256": FOURTH_RECEIPT_PIN,
              "new_word": [1, 2, 1, 2, 0], "supported_triples": triples,
              "matched_group_terms": matches, "identity_matches": identity_matches,
              "match_equality_patterns": dict(sorted(match_patterns.items())),
              "integer_trace_numerator": total, "trace_denominator": 48**5,
              "new_word_trace_per_cover": str(fifth), "fixed_source_bounds": rows,
              "finite_free_moment_comparison": free_moment_comparison(),
              "nine_chart_optimizing_weight": "9-lambda",
              "nine_chart_optimizing_polynomial": "19 lambda - 6 lambda^2",
              "moment_relaxation_attainment": {
                  "nodes": ["0", "(19-2 sqrt(22))/12", "(19+2 sqrt(22))/12", "9"],
                  "nonzero_mass": str(rank), "mass_at_9": str(mass9),
                  "interior_mass": str(interior_mass), "interior_mean": str(interior_mean),
                  "recurrence": "x^3-(73/6)x^2+(1459/48)x-273/16",
                  "ambient_total_mass": 96},
              "scope": "The full fixed-source logical regular-cover module. No freeness assumption.",
              "not_claimed": ["Equality of higher moments", "A cache construction", "A native-child bound",
                              "A result for changing source histories", "A supplier or kappa improvement"]}
    (HERE/"QUERY-FIFTH-MOMENT.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "m5": "47467/36",
                      "rank_per_cover": "15560/273", "whole_fields": 57,
                      "moment_relaxation_is_sharp": True}))


if __name__ == "__main__":
    main()
