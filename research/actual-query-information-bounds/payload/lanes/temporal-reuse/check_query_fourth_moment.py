"""Check exact routed query moments from the actual port bases."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parent
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
ARCHIVE_PIN = "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754"
PHASE_MEMBER = "t16/global/base/work/complex-nine-native/DATA-PHASES.json"
PHASE_PIN = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
WORD_MEMBER = "slots/local/CANONICAL-WORD.json.gz"
WORD_PIN = "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"
INTERFACE_PIN = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
R_REVIEW_PIN = "9639db0bdbc82255ef85273ac15a0aff68d5c659190557bf331d260eb714964f"
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
DIM = 33


def need(ok, message):
    if not ok:
        raise ValueError(message)


def checked(raw, pin):
    need(sha256(raw).hexdigest() == pin, "Source pin differs")
    return raw


def apply(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length()-1]
        vector ^= bit
    return result


def compose(left, right):
    """Return the product left*right. Vectors meet right first."""
    return tuple(apply(left, x) for x in right)


def transpose(columns):
    return tuple(sum(((x >> i) & 1) << j for j, x in enumerate(columns))
                 for i in range(len(columns)))


def route(basis, stage, dimension=DIM):
    columns = [1 << i for i in range(dimension)]
    if not stage:
        return tuple(columns)
    start = 9+8*(stage-1)
    q = basis[0]
    for i in range(9):
        columns[i] = q*((q >> i) & 1)
        for j, b in enumerate(basis[1:]):
            columns[i] ^= ((b >> i) & 1) << (start+j)
    for j, b in enumerate(basis[1:]):
        columns[start+j] = b
    return tuple(columns)


def phase_form(axes):
    linear, quadratic = [0]*73, [0]*73
    for axis in axes:
        for i in range(73):
            if (axis >> i) & 1:
                linear[i] = (linear[i]+1) % 4
                quadratic[i] ^= axis & ~((1 << (i+1))-1)
    return linear, quadratic


def alignment_translation(left_axes, right_axes):
    left, lq = phase_form(left_axes)
    right, rq = phase_form(right_axes)
    need(lq == rq and all((x-y) % 2 == 0 for x, y in zip(left, right)),
         "The frame alignment has a nontranslation phase defect")
    return sum(1 << i for i, (x, y) in enumerate(zip(left, right)) if (x-y) % 4 == 2)


def source():
    checked((HERE/"SPECTRAL-BOUND-REVIEW.json").read_bytes(), R_REVIEW_PIN)
    interface = json.loads(checked((LANES/"circuit-interface/INTERFACE.json").read_bytes(), INTERFACE_PIN))
    upstream = LANES.parent / "upstream"
    phases = json.loads(checked((upstream / "DATA-PHASES.json").read_bytes(), PHASE_PIN))
    word = json.loads(gzip.decompress(checked((upstream / "CANONICAL-WORD.json.gz").read_bytes(), WORD_PIN)))
    need(interface["ports"] == word["ports"] == [x["q"] for x in phases["recipes"]],
         "Port orders differ")
    U = sorted(set(range(112))-set(A)-set(T))
    roots = [tuple(int(row.get(str(p), 0)) for row in interface["R"]) for p in U]
    bases = []
    for p in U:
        entry = phases["recipes"][p]
        axes = entry["idle_children"][0]["orthogonal_axes"]
        need(axes[8:] == [1 << i for i in range(9, 17)], "The source complement axes differ")
        basis = (entry["q"], *axes[:8])
        need(all((x & y).bit_count() % 2 == (i == j)
                 for i, x in enumerate(basis) for j, y in enumerate(basis)),
             "A source basis is not orthogonal")
        bases.append(basis)
    dots = [[sum(x*y for x, y in zip(a, b)) for b in roots] for a in roots]
    need([dots[p][p] for p in range(96)] == [4]*96, "A root norm differs")
    need(all(sum(r[i]*r[j] for r in roots) == 48*(i == j)
             for i in range(8) for j in range(8)), "The ordinary Gram differs")
    full = [[route(basis, s, 73) for basis in bases] for s in range(9)]
    identity = tuple(1 << i for i in range(73))
    for s in range(9):
        for p in range(96):
            need(transpose(full[s][p]) == full[s][p] and
                 compose(full[s][p], full[s][p]) == identity, "A route is not an orthogonal involution")
    alignment_checks = 0
    for p, actual_port in enumerate(U):
        q = bases[p][0]
        for s in range(9):
            image = full[s][p]
            exterior = [1 << i for i in range(9, 9+8*s)]
            before = [q] if s == 0 else image[:9+8*(s-1)]
            after = image[:9+8*s]
            pre = apply(image, alignment_translation(before, [q]+exterior))
            post = apply(image, alignment_translation(after, [1 << i for i in range(9)]+exterior))
            need(phases["recipes"][actual_port]["stage_alignment"][s] ==
                 {"entry_X": pre, "entry_Y": pre, "exit_X": post, "exit_Y": post},
                 "A full-payload native alignment differs")
            alignment_checks += 1
    pairs = []
    for s in range(9):
        for t in range(s+1, 9):
            relative = [compose(full[s][p], full[t][p]) for p in range(96)]
            need(len(set(relative)) == 96, "Relative port routes collide")
            pairs.append([s, t, len(set(relative))])
    # All positive-stage permutations are common coordinate permutations.
    conjugacy_checks = 0
    for t in range(2, 9):
        swap = list(identity)
        for j in range(8):
            swap[9+j], swap[9+8*(t-1)+j] = swap[9+8*(t-1)+j], swap[9+j]
        for p in range(96):
            need(compose(swap, compose(full[1][p], swap)) == full[t][p],
                 "Positive-stage conjugacy fails")
            conjugacy_checks += 1
    fresh_checks = 0
    for p in range(96):
        for q in range(96):
            fixes = all(apply(full[1][p], bases[q][j+1]) == 1 << (9+j) for j in range(8))
            need(fixes == (p == q), "Fresh-block port test fails")
            fresh_checks += 1
    ordered = apply(compose(full[1][0], full[2][0]), 1 << 9)
    reversed_order = apply(compose(full[2][0], full[1][0]), 1 << 9)
    need(ordered == bases[0][1] and reversed_order == 1 << 17 and ordered != reversed_order,
         "The route-order control does not distinguish the two products")
    return roots, bases, dots, {"regular_cover": "The actual orthogonal cover group",
            "ordinary_ports": U, "archive_sha256": ARCHIVE_PIN,
            "phase_member_sha256": PHASE_PIN, "canonical_word_sha256": WORD_PIN,
            "interface_sha256": INTERFACE_PIN, "source_matrix_review_sha256": R_REVIEW_PIN,
            "full_payload_alignment_checks": alignment_checks,
            "route_order_control": {"port": U[0], "input_axis": 512,
                                     "rho1_rho2_image": ordered,
                                     "rho2_rho1_image": reversed_order},
            "relative_pairs": pairs, "positive_stage_conjugacy_checks": conjugacy_checks,
            "fresh_block_port_checks": fresh_checks}


def covariance(s, t, roots, bases, dots):
    """Store coefficients of (B_s B_t*)(B_t B_s*) without scale factors."""
    identity = tuple(1 << i for i in range(DIM))
    relative = [compose(route(b, s), route(b, t)) for b in bases]
    terms = {identity: None}
    support = 0
    for p in range(96):
        for q in range(96):
            if p == q or not dots[p][q]:
                continue
            key = compose(relative[p], transpose(relative[q]))
            need(key not in terms, "A supported ordered pair has a group collision")
            terms[key] = (p, q, dots[p][q])
            support += 1
    identity_matrix = [[sum(4*r[i]*r[j] for r in roots) for j in range(8)] for i in range(8)]
    need(identity_matrix == [[192*(i == j) for j in range(8)] for i in range(8)],
         "Identity coefficient differs")
    square = sum(x*x for row in identity_matrix for x in row)
    square += sum(dots[p][q]**2*dots[p][p]*dots[q][q]
                  for entry in terms.values() if entry is not None for p, q, _ in [entry])
    need(support == 4224 and square == 565248, "Fourth pair count differs")
    return terms, {"stages": [s, t], "nonidentity_terms": support,
                   "collision_multiplicities": {"1": support},
                   "integer_frobenius_square": square,
                   "alternating_trace_per_cover": str(Q(square, 48**4))}


def inner_coeff(left, right, dots):
    total = 0
    common = left.keys() & right.keys()
    for key in common:
        a, b = left[key], right[key]
        if a is None or b is None:
            need(a is None and b is None, "Only one coefficient is the identity term")
            total += 8*192**2
        else:
            p, q, x = a
            r, s, y = b
            total += x*y*dots[p][r]*dots[q][s]
    return len(common), total


def trace_word(word):
    """Reduce fourth-order words by idempotence and the singleton lemma."""
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
        need(w[0] == w[2] and w[1] == w[3], "An unreduced pair word is not alternating")
        return Q(23, 216)
    unique = next((i for i, s in enumerate(w) if s and counts[s] == 1), None)
    need(unique is not None, "An unsupported trace type remains")
    w.pop(unique)
    return trace_word(w)/12


def moments():
    rows = []
    for k in range(1, 10):
        mm = [sum((trace_word(w) for w in product(range(k), repeat=j)), Q(0))
              for j in range(1, 5)]
        m1, m2, m3, m4 = mm
        det = m2*m4-m3*m3
        if det:
            rank = (m1*m1*m4-2*m1*m2*m3+m2**3)/det
        else:
            rank = m1*m1/m2
        fields = (rank.numerator+rank.denominator-1)//rank.denominator
        rows.append({"charts": k, "moments_per_cover": list(map(str, mm)),
                     "quadratic_rank_per_cover": str(rank),
                     "whole_fields": fields, "eight_field_cohorts": (fields+7)//8})
    need(rows[-1]["moments_per_cover"] == ["72", "120", "244", "1649/3"], "Nine-chart moments differ")
    need(rows[-1]["quadratic_rank_per_cover"] == "4104/73", "The quadratic bound differs")
    return rows


def main():
    roots, bases, dots, binding = source()
    cache, pairs = {}, []
    for s, t in ((0, 1), (0, 2), (1, 0), (1, 2), (1, 3)):
        cache[s, t], row = covariance(s, t, roots, bases, dots)
        pairs.append(row)
    mixed = []
    for s, t, u in ((0, 1, 2), (1, 0, 2), (1, 2, 3)):
        count, total = inner_coeff(cache[s, t], cache[s, u], dots)
        need(count == 1 and total == 294912, "Mixed-three support or trace differs")
        mixed.append({"word": [s, t, s, u], "common_group_support": count,
                      "integer_coefficient_inner_product": total,
                      "trace_per_cover": str(Q(total, 48**4))})
    result = {"status": "PASS_ACTUAL_QUERY_FOURTH_MOMENT", "source_binding": binding,
              "route_product": "B_s B_t* uses rho_s(p) rho_t(p); vectors meet t first.",
              "pair_cases": pairs, "mixed_three_cases": mixed,
              "distinct_stage_trace": "96/12^k for 1 <= k <= 9",
              "singleton_rule": "A positive stage occurring once can be deleted at trace factor 1/12.",
              "fixed_source_bounds": moments(),
              "nine_chart_optimizing_polynomial": "13 lambda - 4 lambda^2",
              "scope": "Simultaneous linear queries of one arbitrary fixed source in the full logical regular-cover module, with any payload multiplicity.",
              "not_claimed": ["A native-child lower bound", "A bound on changing controller sources",
                              "A supplier or kappa improvement"]}
    (HERE/"QUERY-FOURTH-MOMENT.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "nine_chart_moments": ["72", "120", "244", "1649/3"],
                      "rank_per_cover": "4104/73", "whole_fields": 57, "eight_field_cohorts": 8}))


if __name__ == "__main__":
    main()
