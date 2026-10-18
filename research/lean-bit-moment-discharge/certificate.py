"""Untrusted dyadic certificate proposals and exact source/step checks.

Lean proves the Real interpretation independently. This module uses only
integer square roots and rational arithmetic, never logs, exp or floats.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import isqrt
import json
import re

HERE = Path(__file__).resolve().parent
GRID, NUMERATOR, BITS = 10**12, 130849, 17
EXPONENT = Q(9983, 10000)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def fraction(q):
    return f"{q.numerator}/{q.denominator}"


def profile(root=HERE):
    read = lambda name: json.loads((root / "sources" / name).read_bytes())
    global_record, expected, assembly = (read(n) for n in ["GLOBAL.json", "EXPECTED.json", "ASSEMBLY.json"])
    counts = {int(k): v for k, v in global_record["profile"].items()}
    need(counts == {int(k): v for k, v in expected["nine"]["profile"].items()}, "profile source agreement")
    need((global_record["m"], global_record["live"], global_record["maxchild"]) == (64, 28416, 42),
         "selected dimensions")
    need(assembly["bit_lower"] == expected["nine"]["bit_lower"], "selected assembly binding")
    formal = (root / "lean/Selected.lean").read_text()
    def vector(name):
        match = re.search(r"def " + name + r"[^\n]*:= !\[([^]]+)\]", formal)
        need(match is not None, "literal formal vector")
        return [int(x.strip()) for x in match[1].split(",")]
    need(list(zip(vector("ranks"), vector("counts"))) == sorted(counts.items()), "formal profile binding")
    need("counts r / 28416" in formal and "118606528512 / (10000000000000000 * 28416)" in formal
         and "9983 / 10000" in formal, "formal scalar binding")
    need(all(type(c) is int and c > 0 and 0 < r < 64 for r, c in counts.items()), "proper positive profile")
    need(32 * 64**2 * sum(counts.values()) == 118606528512, "fallback count")
    return counts


def propose_chain(x, numerator, bits, grid):
    need(0 < x <= 1, "base domain")
    need(type(bits) is int and bits > 0 and type(numerator) is int and 0 <= numerator <= 2**bits,
         "exponent domain")
    need(type(grid) is int and grid > 0, "positive grid")
    # Endpoint one has an exact direct certificate, rather than a lost top bit.
    if numerator == 2**bits:
        raise ValueError("unit exponent uses a direct bound")
    previous, values = Q(1), []
    for i in range(bits):
        target = previous * (x if numerator >> i & 1 else 1)
        a, b = target.numerator * grid**2, target.denominator
        n = isqrt(a // b)
        if n * n * b < a:
            n += 1
        values.append(n)
        previous = Q(n, grid)
    return values


def propose(counts):
    return {"schema": "bit-dyadic-moment/1", "grid": GRID, "numerator": NUMERATOR, "bits": BITS,
            "exponent": fraction(EXPONENT), "base_denominator": 64,
            "rows": [{"rank": r, "count": c, "upper_numerators": propose_chain(Q(r, 64), NUMERATOR, BITS, GRID)}
                     for r, c in sorted(counts.items())]}


def check(data, counts):
    need(data["schema"] == "bit-dyadic-moment/1", "certificate schema")
    need(type(data["grid"]) is int and data["grid"] == GRID, "certificate grid")
    need(type(data["numerator"]) is int and data["numerator"] == NUMERATOR
         and type(data["bits"]) is int and data["bits"] == BITS, "dyadic exponent binding")
    need(data["exponent"] == fraction(EXPONENT) and type(data["base_denominator"]) is int
         and data["base_denominator"] == 64, "selected real exponent and base")
    need(Q(NUMERATOR, 2**BITS) <= EXPONENT, "exponent must round down")
    need([(r["rank"], r["count"]) for r in data["rows"]] == sorted(counts.items()), "complete ordered profile")
    uppers = {}
    for row in data["rows"]:
        rank, count = row["rank"], row["count"]
        need(type(rank) is int and type(count) is int, "integer profile types")
        values = row["upper_numerators"]
        need(len(values) == BITS, "complete square chain")
        previous, exponent = Q(1), Q(0)
        for i, n in enumerate(values):
            need(type(n) is int and 0 <= n <= GRID, "nonnegative bounded square root")
            bit = NUMERATOR >> i & 1
            target = previous * (Q(rank, 64) if bit else 1)
            bound = Q(n, GRID)
            need(target <= bound**2, "square certificate inequality")
            previous, exponent = bound, (exponent + bit) / 2
        need(exponent == Q(NUMERATOR, 2**BITS), "binary digit orientation")
        uppers[rank] = previous
    bad = Q(118606528512, 10**16 * 28416)
    ordinary = sum((Q(count, 28416) * uppers[rank] for rank, count in counts.items()), Q(0))
    total = ordinary + bad * uppers[1]
    need(total < Q(9999, 10000), "full moment margin")
    return {"square_steps": BITS * len(counts), "rounded_exponent": fraction(Q(NUMERATOR, 2**BITS)),
            "exponent_gap": fraction(EXPONENT - Q(NUMERATOR, 2**BITS)),
            "ordinary_upper": fraction(ordinary), "fallback_upper": fraction(bad * uppers[1]),
            "moment_upper": fraction(total), "margin": fraction(Q(9999, 10000) - total),
            "upper_numerators": {str(r): int(u * GRID) for r, u in uppers.items()}}


def lean_fraction(q):
    q = Q(q)
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator} / {q.denominator}"


def render_lean(data, counts):
    result = check(data, counts)
    lines = ["import DyadicPower", "import Selected", "", "/-! Generated, untrusted certificate proposals; every inequality is proved by Lean.",
             "Gareth Davidson with OpenAI Codex assistance. Apache-2.0. -/", "",
             "open scoped BigOperators", "open DyadicPower SelectedStoppedRecurrence", "",
             "namespace SelectedBitMoment", ""]
    for row in data["rows"]:
        rank, values = row["rank"], row["upper_numerators"]
        base = f"({rank} / 64 : ℝ)"
        lines.extend([f"theorem rank_{rank}_upper : {base} ^ (9983 / 10000 : ℝ) ≤ {values[-1]} / {GRID} := by",
                      f"  have h0 : {base} ^ (0 : ℝ) ≤ 1 := by norm_num"])
        previous, exponent = Q(1), Q(0)
        for i, n in enumerate(values):
            bit = NUMERATOR >> i & 1
            next_exponent = (exponent + bit) / 2
            lines.extend([f"  have h{i+1} : {base} ^ ({lean_fraction(next_exponent)} : ℝ) ≤ {n} / {GRID} := by",
                          f"    convert half_step (x := {base}) (e := {lean_fraction(exponent)}) (b := {bit})",
                          f"      (u := {'1' if i == 0 else str(values[i-1]) + ' / ' + str(GRID)}) (v := {n} / {GRID})",
                          f"      (by norm_num) h{i} (by norm_num) (by norm_num) using 1; norm_num"])
            previous, exponent = Q(n, GRID), next_exponent
        lines.extend(["  exact upper_of_rounded_exponent (by norm_num) (by norm_num) (by norm_num) h17", ""])
    values = [row["upper_numerators"][-1] for row in data["rows"]]
    lines.extend(["noncomputable def upper : Fin 8 → ℝ := ![" + ", ".join(f"{n} / {GRID}" for n in values) + "]", "",
                  "theorem per_rank_upper : ∀ r, ((ranks r : ℝ) / 64) ^ exponent ≤ upper r := by",
                  "  intro r", "  fin_cases r"])
    for row in data["rows"]:
        lines.append(f"  · simpa [ranks, exponent, upper] using rank_{row['rank']}_upper")
    total = lean_fraction(Q(result["moment_upper"]))
    lines.extend(["", f"theorem fractional_moment_upper : fractionalMoment ≤ {total} := by",
                  "  calc", "    fractionalMoment ≤ (∑ r, weight r * upper r) + bad * upper 0 := by",
                  "      unfold fractionalMoment", "      apply add_le_add",
                  "      · exact Finset.sum_le_sum fun r _ => mul_le_mul_of_nonneg_left (per_rank_upper r) (by unfold weight; positivity)",
                  "      · apply mul_le_mul_of_nonneg_left _ (by norm_num [bad])",
                  "        simpa [exponent, upper] using rank_1_upper",
                  f"    _ = {total} := by norm_num [Fin.sum_univ_succ, weight, counts, upper, bad]", "",
                  "theorem fractional_moment_strict : fractionalMoment < 9999 / 10000 :=",
                  "  lt_of_le_of_lt fractional_moment_upper (by norm_num)", "", "end SelectedBitMoment", ""])
    lines.extend("#print axioms SelectedBitMoment." + name for name in
                 [*(f"rank_{r}_upper" for r in sorted(counts)), "per_rank_upper", "fractional_moment_upper", "fractional_moment_strict"])
    return "\n".join(lines) + "\n"


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True, help="new directory for untrusted proposals")
    args = parser.parse_args()
    counts = profile()
    data = propose(counts)
    args.out_dir.mkdir(exist_ok=False, parents=True)
    (args.out_dir / "DYADIC.json").write_text(json.dumps(data, indent=2) + "\n")
    (args.out_dir / "SelectedMoment.lean").write_text(render_lean(data, counts))
    print("PROPOSALS_ONLY_KERNEL_NOT_RUN", args.out_dir)


if __name__ == "__main__":
    main()
