"""Exact source constants, threshold comparisons and conditional tariff census.

No floating point and no construction of 2**H. This does not install RDiv.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
import json
from source_binding import ROOT, need, oddpart, sources

V = 1920
H_STEP = 10 ** 14
H_INDEX = 141616
H = H_STEP * H_INDEX
LP = 2226


def scalar_surcharge(q):
    """Declared optimistic model: one offset scan and three extra odd scans."""
    q = F(q)
    if q.denominator == 1:
        return 0
    return 4 * (q.denominator.bit_length() + 1) * (1 + 3 * (oddpart(q.denominator) > 1))


def run():
    caller, word = sources()
    # The source strictification uses the gap 10**-14 and LP=2226.
    need((H + 1) ** LP < 1 << H_INDEX, "current exact H threshold")
    need((H_STEP * (H_INDEX - 1) + 1) ** LP >= 1 << (H_INDEX - 1), "preceding H index fails")
    m = 153 ** V
    kstar = V * m * (H + 1) ** 2
    need((4096 * kstar).bit_length() <= H, "4096 Kstar < 2**H, by bit length")
    need(m * (H + 1) + H + 8 * V <= kstar, "positive noncontext path overhead")
    # ((153/11)**v+1)((12/11)**v+2) < 2**(6v), rationally.
    left = (153 ** V + 11 ** V) * (12 ** V + 2 * 11 ** V)
    right = (1 << (6 * V)) * 11 ** (2 * V)
    need(left < right, "split/completion factor < 2**(6v)")
    need(344 * 8 < 4096 and 357 * 8 < 4096, "both path exponents below D/8")
    need(max(576, (m + 2).bit_length()) < H, "all nonwrapper node Sigma below N")
    need(4 * 16 + 7 <= 1 << (16 - 3), "large-D log lemma base")
    # The induction step is 4(k+1)+7 <= 2(4k+7) for k>=16.
    need(4 * 17 + 7 <= 2 * (4 * 16 + 7), "large-D log lemma step")
    small = []
    for d in range(1, 20):
        g = 5 if d < 19 else 0
        need((d + 3) ** 4 <= 1 << (d + 2 * g - 1), "small-rank grid guard")
        need((d + 3) ** 2 <= 1 << (d + 3), "small-rank radius guard")
        small.append(dict(D=d, extra_fractional_bits=g))
    need(23 ** 4 < 2 * 22 ** 4, "large small-rank induction ratio at D=19")
    # The function (D+4)/(D+3) decreases, hence the guard continues for all D>=19.
    need(6 ** 4 > 1 << (3 + 2 * 4 - 1), "negative control: g=4 fails at D=3")
    native = sum(scalar_surcharge(e[2] if e[0] == "SCALE" else e[3])
                 for e in word["program"] if e[0] in ("SCALE", "ADD", "COPY"))
    outer = Counter()
    for e in caller["events"]:
        if e[0] == "J":
            continue
        multiplicity = len(caller["types"][e[0]]["ports"])
        if e[1] in ("ADD", "SCALE"):
            outer["scalar_offset_model"] += multiplicity * scalar_surcharge(e[3] if e[1] == "SCALE" else e[4])
        elif e[1] == "LAMBDA":
            outer["lambda_offset_model"] += multiplicity * scalar_surcharge(F(1, 2))
    baseline = json.loads((ROOT / "reference/QUERY-RESULT.json").read_bytes())["invoice"]["full_after"]
    surcharge = 18 * native + sum(outer.values())
    need(native == 941128 and baseline == 826265904, "current source invoice pins")
    need(baseline + surcharge < 10 ** 9, "optimistic declared tariff model only")
    nums = [abs(F(e[2] if e[0] == "SCALE" else e[3]).numerator)
            for e in word["program"] if e[0] in ("SCALE", "ADD", "COPY")]
    dens = [F(e[2] if e[0] == "SCALE" else e[3]).denominator
            for e in word["program"] if e[0] in ("SCALE", "ADD", "COPY")]
    need(max(nums) < 1 << 24 and max(dens) < 1 << 19, "temporary numerator/denominator limits")
    need(max(nums) >= 1 << 16, "negative control: inherited 16-bit numerator premise fails")
    return dict(parameters=dict(v=V, ambient=153, LP=LP, H=H, H_index=H_INDEX,
                                Kstar_bits=kstar.bit_length(),
                                scaled_Kstar_bits=(4096 * kstar).bit_length()),
                conditional_path_bounds=dict(gain_bits_per_context=344, radius_bits_per_context=357,
                                              Sigma_node_bound="2**H * (D+3)",
                                              format="F=p+D+g; W=p+h+2D+3+g; temporary W+26"),
                small_rank_guards=small,
                temporary=dict(numerator_bits=24, denominator_bits=19, extra_signed_bits=26),
                optimistic_tariff_model=dict(baseline=baseline, retained_exact_conversion_charge=2734992,
                    per_native_call_surcharge=native, native_call_count=18,
                    all_native_surcharge=18 * native, outer=dict(outer), total_surcharge=surcharge,
                    conditional_total=baseline + surcharge,
                    conditional_margin=10 ** 9 - baseline - surcharge,
                    status="Declared extra-scan model, not a physical tape-cost certificate"))
