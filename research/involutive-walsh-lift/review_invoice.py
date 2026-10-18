"""Check the dilation bill by exact differences from the selected bill.

This reviewer does not import the invoice producer. It derives each change
from the pinned selected complete bill. New code uses Apache-2.0 and
OpenAI Codex assistance.
"""

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import argparse
import sys


PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import sources


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=PACKAGE.parents[1])
    parser.add_argument('--out', type=Path, default=PACKAGE / 'evidence')
    args = parser.parse_args()
    old, owners = sources.load_invoice(args.repo)
    pins = sources.INVOICE_MEMBERS
    claimed_path = args.out / 'DILATION-INVOICE.json'
    claimed = json.loads(claimed_path.read_text())
    n, helpers, live, physical = 704, 480, 14336, 14826
    require(owners["rank_mass"] == 1041408, "The selected mass changed.")
    require(old["live"] == live and old["physical"] == physical, "The stock changed.")
    require(2 * n + 2 * helpers <= 4 * n, "Local map reserve is too small.")
    require(2 * live + 2 * physical <= 4 * physical, "Global map reserve is too small.")
    calls = len(old["selected_calls"])
    require(calls == 144, "The complete-call count changed.")
    parent_live, parent_physical = 23408, 23922
    bridge = 2 * 112 * old["bridge_sweeps"]
    shift = 4 * 112 * 16
    fixed = (old["selected_real_component_primitives"] + bridge + 3 * shift
             + parent_live + 64 * parent_physical)
    old_compiler = old["compiler"]
    require((old["unhosted_pervertex"] - fixed) % old_compiler == 0,
            "The old compiler charge is not integral.")
    old_outside = (old["unhosted_pervertex"] - fixed) // old_compiler - calls * old["local_adapters"]
    group = 1 << 1296
    for j in range(2, 73, 2):
        group *= (1 << j) - 1
    stock = group * physical
    rows = []
    require([row["factor"] for row in claimed["dilations"]] == [2, 4],
            "The dilation inventory changed.")
    for row in claimed["dilations"]:
        factor = row["factor"]
        m = 73 * factor
        compiler = 64 * (m + 1) ** 3
        adapters = old["local_adapters"] + 64 * (m - 73) + 4 * n
        primitive = old["local_primitive_bound"] - old["local_adapters"] * old_compiler
        primitive += adapters * compiler
        old_wrappers = old["wrapper_elementary_factors_charged"]
        require(old_wrappers % 144 == 0, "The old wrapper count is not integral.")
        new_wrappers = old_wrappers // 144 * (2 * m - 2)
        outside = old_outside + 8 * (new_wrappers - old_wrappers) + 64 * (m - 73) + 4 * physical
        fresh = fixed + (calls * adapters + outside) * compiler
        rebased = fresh + 65 * (physical - parent_physical) + live - parent_live
        used = max(fresh, rebased, old["retained_prior_overcharge"]["previous_pervertex_allowance"] + fresh)
        mass = sum(factor * int(r) * count for r, count in owners["paid_profile"].items())
        require(row["profile"] == {str(factor * int(r)): count
                                   for r, count in owners["paid_profile"].items()},
                "The complete child profile changed.")
        for r, count in owners["paid_profile"].items():
            require(row["profile"][str(factor * int(r))] == count, "A child count changed.")
            require(Fraction(factor * int(r), m) == Fraction(int(r), 73), "A moment base changed.")
        streamed = group * mass
        logical = group * used + 64
        router = compiler * (logical + 1) * (stock + 1) ** 2
        total = streamed + (1 << 100000)
        literal = 2 * (1 << 30000) * stock ** 2 + 8 * streamed + 4 * stock + 4 + 32 * m
        prefix = 68 + (m + 1) // 2 + calls + old["bridge_sweeps"] + 4
        expected = {
            "compiler": compiler, "local_adapters": adapters,
            "local_primitive_bound": primitive, "unhosted_pervertex": fresh,
            "hosted_rebased_pervertex": rebased, "conservative_pervertex_used": used,
            "wrapper_elementary_factors_charged": new_wrappers,
            "rank_mass": mass, "rank_deficit": live * m - mass,
            "global_prefix_bits": prefix, "logical_bits": logical.bit_length(),
            "router_bits": router.bit_length(), "literal_bits": literal.bit_length(),
            "required_C0_bits": (32 * m * total ** 2).bit_length(),
            "physical_row_coefficient": 2 * stock.bit_length() + 9909 + 252 + 1024,
        }
        for key, value in expected.items():
            require(row[key] == value, "The independent value differs: " + key)
        guards = {
            "local_primitive_bound": primitive < 1 << 48,
            "logical": logical < 1 << 6050, "router": router < 1 << 30000,
            "literal": literal < 1 << 100000, "mass": total < 1 << 100001,
            "precision": 32 * m * total ** 2 < 1 << 210000,
            "tape": 2 * total + 18 < 1 << 210000,
            "row": expected["physical_row_coefficient"] < 20161,
            "halving": m * m > 2 * (48 * factor) ** 2,
            "prefix": prefix < 512,
        }
        require(guards == row["strict_checks"], "A finite guard differs.")
        rows.append({"factor": factor, "checked_values": expected, "guards": guards})
    require(all(rows[0]["guards"].values()), "The twofold bill failed.")
    require(not rows[1]["guards"]["local_primitive_bound"], "The fourfold control did not reject.")
    result = {
        "status": "PASS_INDEPENDENT_DILATION_ARITHMETIC_AND_SOURCE_BINDING",
        "source_commit": sources.BASE, "source_archive": sources.SELECTED_ARCHIVE,
        "source_archive_sha256": sources.SELECTED_ARCHIVE_SHA256, "source_members": pins,
        "reviewed_receipt_sha256": sha256(claimed_path.read_bytes()).hexdigest(),
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "local_extra_map_reserve": {"required_upper": 2 * n + 2 * helpers, "charged": 4 * n},
        "global_extra_map_reserve": {"required_upper": 2 * live + 2 * physical, "charged": 4 * physical},
        "rows": rows,
        "scope": "Same scalar word and the specified monomial wrapper substitution. Native lowering and cover transport are separate proof dependencies.",
        "not_claimed": ["Modified phase-gap or decoder invoice", "A complete emitted supplier", "A new kappa"],
    }
    (args.out / "DILATION-INVOICE-REVIEW.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
