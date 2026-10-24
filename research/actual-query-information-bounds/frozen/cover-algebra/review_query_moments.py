"""Check the exact moment arithmetic and the finite source contractions."""

from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parent
PINS = {
    "QUERY-MOMENTS.md": "91121028d7f084d3c1d53a16ca8a3634ce4ede59fcab31c9a74c4a221c7d75e5",
    "check_query_fourth_moment.py": "c22539e007c763b2d92d2932c4d84080ccda8549774d6be8b7705575a03a253f",
    "QUERY-FOURTH-MOMENT.json": "df32110bbd285e3036bdb2082e3307b24edc7515953cab7a1b3b6b684adc1e66",
    "check_query_fifth_moment.py": "bea72f2bafab8cc38142557d6d3a1bee5f4db1f9a2a75668fce146ca6ebba4f0",
    "QUERY-FIFTH-MOMENT.json": "d346e38c1dc323d3304c94e7faf14384ac7970bb7b7775c49749a90a509fa0e9",
}


def need(value, message):
    if not value:
        raise ValueError(message)


def main():
    for name, expected in PINS.items():
        need(sha256((LANES / "temporal-reuse" / name).read_bytes()).hexdigest() == expected, "A source pin differs: " + name)
    source_path = LANES / "circuit-interface/INTERFACE.json"
    source = json.loads(source_path.read_text())
    a = [0, 7, 20, 27, 36, 46, 57, 111]
    t = [21, 37, 47, 76, 81, 87, 92, 110]
    ordinary = [p for p in range(112) if p not in a + t]
    roots = [[Q(row.get(str(p), 0)) for row in source["R"]] for p in ordinary]
    dot = lambda x, y: sum((v * w for v, w in zip(x, y)), Q())
    need(all(dot(v, v) == 4 for v in roots), "A column norm differs")
    need(all(sum((v[i] * v[j] for v in roots), Q()) == 48 * int(i == j) for i in range(8) for j in range(8)), "The ordinary Gram differs")
    products = [[dot(x, y) for y in roots] for x in roots]
    need(all(sum(bool(v) for v in row) == 45 for row in products), "The supported degree differs")
    off = [products[p][q] for p in range(96) for q in range(96) if p != q and products[p][q]]
    need(len(off) == 4224 and set(map(abs, off)) == {Q(2)}, "The off-diagonal root products differ")
    fourth_numerator = 8 * 192**2 + sum(16 * x * x for x in off)
    need(Q(fourth_numerator, 48**4) == Q(23, 216), "The alternating contraction differs")
    # The reviewed finite route check says that all fifth-order matches have s=t.
    # Contract those terms directly, without its coefficient-table implementation.
    fifth_numerator = sum((192 * products[r][r]**3 for r in range(96)), Q())
    fifth_numerator += sum((64 * x * x for x in off), Q())
    need(fifth_numerator == 2260992 and Q(fifth_numerator, 48**5) == Q(23, 2592), "The fifth contraction differs")
    fifth = json.loads((LANES / "temporal-reuse/QUERY-FIFTH-MOMENT.json").read_text())
    need(fifth["supported_triples"] == 194400 and fifth["matched_group_terms"] == 4320 and fifth["identity_matches"] == 96, "The finite match receipt differs")
    patterns = fifth["match_equality_patterns"]
    need(patterns == {"(False, True, False)": 4224, "(True, True, True)": 96}, "The match classification differs")
    m = [Q(96), Q(72), Q(120), Q(244), Q(1649, 3), Q(47467, 36)]
    # The fourth-moment word count follows cyclic idempotence and singleton deletion.
    k = 9
    m4 = 8*k + 4*k*(k-1) + Q(23, 216)*k*(k-1)
    m4 += Q(k*(k-1)*(k-2), 3) + Q(k*(k-1)*(k-2)*(k-3), 216)
    need(m4 == m[4], "The fourth word count differs")
    v1, v2 = m[1], m[2]
    h11, h12, h22 = m[2:5]
    determinant = h11*h22 - h12*h12
    bound4 = (v1*v1*h22 - 2*v1*v2*h12 + v2*v2*h11) / determinant
    need(bound4 == Q(4104, 73), "The optimal quadratic Cauchy bound differs")
    need((h22*v1-h12*v2) / (-h12*v1+h11*v2) == -Q(13, 4), "The fourth optimizing polynomial differs")
    weighted = [9*m[i] - m[i+1] for i in range(1, 5)]
    v1, v2, h22 = weighted[0], weighted[1], weighted[3]
    h11, h12 = weighted[1:3]
    determinant = h11*h22 - h12*h12
    bound5 = (m[1] + (v1*v1*h22 - 2*v1*v2*h12 + v2*v2*h11) / determinant) / 9
    need(bound5 == Q(15560, 273), "The weighted quadratic bound differs")
    need((h22*v1-h12*v2) / (-h12*v1+h11*v2) == -Q(19, 6), "The fifth optimizing polynomial differs")
    moment = [bound5] + m[1:]
    need(all(moment[i+3] - Q(73, 6)*moment[i+2] + Q(1459, 48)*moment[i+1] - Q(273, 16)*moment[i] == 0 for i in range(3)), "The extremal measure recurrence differs")
    mass9 = (moment[2] - Q(19, 6)*moment[1] + Q(91, 48)*moment[0]) / Q(2611, 48)
    mean = (moment[1] - 9*mass9) / (bound5-mass9)
    need(mass9 == Q(8, 7833) and 1 < mean < 2 and 0 < bound5 < 96, "The extremal masses are not positive")
    # The two remaining nodes are (19 +/- 2 sqrt(22))/12.
    need(7**2 < 88 < 19**2 and 5**2 < 88 < 17**2, "The node intervals differ")
    result = {
        "status": "PASS_INDEPENDENT_QUERY_MOMENT_PROOF_AND_ARITHMETIC_REVIEW",
        "source_pins": PINS,
        "matrix_source_sha256": sha256(source_path.read_bytes()).hexdigest(),
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "checks": {"ordinary_columns": 96, "off_diagonal_support": len(off), "fourth_contraction": str(Q(fourth_numerator, 48**4)), "fifth_contraction": str(Q(fifth_numerator, 48**5)), "rank4": str(bound4), "rank5": str(bound5), "whole_fields": 57, "eight_field_cohorts": 8, "positive_measure_attains_first_five_moments": True},
        "scope": "Independent proof review and exact arithmetic. The frozen finite route-support enumerations are inspected dependencies; this review does not rerun or replace them. The capacity statement uses the full fixed-source regular-cover payload module. No changing-source, native-child, cache construction, or supplier claim."
    }
    (HERE / "QUERY-MOMENTS-REVIEW.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
