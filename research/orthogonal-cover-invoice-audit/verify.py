#!/usr/bin/env python3
"""Exact, scoped audit of the binary dot-product cover in the #626 invoice.

Prepared for theon199 with substantial OpenAI Codex assistance. Apache-2.0.
Standard library only; no construction or production verifier is imported.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
BASE = "66849e1475c930fd7732b1a0067ffee7e1e95f60"
REPLAY = "research/community-k492-audit/pr626/replay/"
SELECTED = "certificates/selected-result.json"
ASSEMBLY = REPLAY + "ASSEMBLY.json"
INVOICE = REPLAY + "mixed-global/audit/PREFIX-AND-INVOICE.json"
OWNERS = REPLAY + "mixed-global/audit/OWNERS-AND-PROFILE.json"
MANIFEST = "research/community-k492-audit/SELECTED-SOURCE.json"
CODE = "research/complex-k492-owner-repair/code/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_sources(root):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    require(pins["base_commit"] == BASE, "unexpected base commit")
    raw = {}
    for name, digest in pins["sha256"].items():
        data = (root / name).read_bytes()
        require(sha256(data) == digest, "source hash mismatch: " + name)
        raw[name] = data
    selected = json.loads(raw[SELECTED])
    assembly, invoice, owners = (json.loads(raw[p]) for p in (ASSEMBLY, INVOICE, OWNERS))
    manifest = json.loads(raw[MANIFEST])
    require(selected["certificate"] == ASSEMBLY, "selected certificate path")
    require(selected["certificate_sha256"] == sha256(raw[ASSEMBLY]), "selected assembly hash")
    require(selected["source_manifest"] == MANIFEST, "selected source manifest")
    require(selected["audited_source_head"] == pins["reviewed_heads"]["626"], "selected source head")
    for pr, head in pins["reviewed_heads"].items():
        require(selected["reviewed_dependency_heads"][pr] == head, "reviewed head: " + pr)
    for name in (CODE + "invoice_allcold.py", CODE + "assemble.py"):
        require(manifest["files"][name] == sha256(raw[name]), "selected code binding: " + name)
    require(assembly["input_sha256"]["fresh_invoice"] == sha256(raw[INVOICE]), "assembly invoice binding")
    require(assembly["input_sha256"]["owner_audit"] == sha256(raw[OWNERS]), "assembly owner binding")
    require(invoice["owner_audit_sha256"] == sha256(raw[OWNERS]), "invoice owner binding")
    require(assembly["template_sha256"] == invoice["template_sha256"] == owners["template_sha256"], "template binding")
    require(assembly["kappa"] == selected["kappa"], "selected kappa binding")
    return selected, invoice, owners


def symplectic_order(dimension):
    """Count ordered hyperbolic bases by the successive pair choices."""
    require(type(dimension) is int and dimension >= 0 and dimension % 2 == 0,
            "symplectic dimension must be a nonnegative even integer")
    count = 1
    for remaining in range(2, dimension + 1, 2):
        count *= ((1 << remaining) - 1) * (1 << (remaining - 1))
    return count


def dot_group_order(dimension):
    require(type(dimension) is int and dimension >= 1, "positive integer dimension required")
    if dimension % 2:
        return symplectic_order(dimension - 1)
    # The even characteristic line has 2^(dimension-1) orthogonal lifts.
    return (1 << (dimension - 1)) * symplectic_order(dimension - 2)


def enumerate_bases(dimension):
    """Visit every ordered orthonormal prefix, with no group/order formula.

    Bits of `available` index actual binary vectors. Appending v intersects
    with its orthogonal complement. Unit norm makes v exclude itself; the
    identity Gram matrix makes every prefix linearly independent.
    """
    require(type(dimension) is int and 1 <= dimension <= 7, "enumeration domain is 1..7")
    unit_vectors = [v for v in range(1 << dimension) if v.bit_count() % 2]
    orthogonal = {
        v: sum(1 << w for w in unit_vectors if (v & w).bit_count() % 2 == 0)
        for v in unit_vectors
    }
    initial = sum(1 << v for v in unit_vectors)
    prefixes = [0] * (dimension + 1)
    prefixes[0] = 1

    def visit(depth, available):
        prefixes[depth] += 1
        if depth == dimension:
            return 1
        total, siblings = 0, available
        while siblings:
            bit = siblings & -siblings
            siblings -= bit
            v = bit.bit_length() - 1
            total += visit(depth + 1, available & orthogonal[v])
        return total

    completions = {v: visit(1, initial & orthogonal[v]) for v in unit_vectors}
    return {
        "dimension": dimension,
        "complete_bases": sum(completions.values()),
        "prefix_counts": prefixes,
        "first_column_completion_histogram": {
            str(k): v for k, v in sorted(Counter(completions.values()).items())
        },
        "characteristic_vector_completions": completions.get((1 << dimension) - 1),
    }


def audit_inputs(invoice, owners):
    for name in ("physical", "live", "compiler", "local_primitive_bound", "conservative_pervertex_used"):
        require(type(invoice[name]) is int and invoice[name] > 0, "invalid invoice field: " + name)
    require(invoice["physical"] == owners["physical"] == 7670, "physical stock")
    require(invoice["live"] == owners["live"] == 7168, "live stock")
    require(invoice["compiler"] == 64 * 74**3, "compiler charge")
    profile = {int(r): count for r, count in owners["paid_profile"].items()}
    require(all(0 < r < 73 and type(c) is int and c > 0 for r, c in profile.items()), "rank domain")
    require(sum(r * c for r, c in profile.items()) == owners["rank_mass"] == 520704, "rank mass")
    require(73 * owners["live"] - owners["rank_mass"] == owners["deficit"] == 2560, "deficit")
    require(invoice["charged_prefix_bits"] == 512 and invoice["row_prefix_extra"] == 1024, "prefix reserve")
    return profile


def invoice_metrics(group, invoice, owners):
    """Re-evaluate only the finite guards, holding the admitted invoice fixed."""
    require(type(group) is int and group > 0, "positive integer group order required")
    stock = group * invoice["physical"]
    streamed = group * owners["rank_mass"]
    logical = group * invoice["conservative_pervertex_used"] + 64
    router = invoice["compiler"] * (logical + 1) * (stock + 1)**2
    literal = (1 << 30001) * stock**2 + 8 * streamed + 4 * stock + 4 + 32 * 73
    mass = streamed + (1 << 100000)
    precision = 32 * 73 * mass**2
    tape = 2 * mass + 18
    row = 2 * stock.bit_length() + 9909 + 252 + 1024
    maxchild = max(map(int, owners["paid_profile"]))
    guards = {
        "local_primitive_bound": (invoice["local_primitive_bound"], 48),
        "logical": (logical, 6050), "router": (router, 30000),
        "literal": (literal, 100000), "mass": (mass, 100001),
        "precision": (precision, 210000), "tape": (tape, 210000),
    }
    checks = {name: value < (1 << exponent) for name, (value, exponent) in guards.items()}
    checks.update(row=row < 20161, halving=73**2 > 2 * maxchild**2)
    finite = {
        "physical_stock_bits": stock.bit_length(), "router_bits": router.bit_length(),
        "literal_bits": literal.bit_length(), "physical_row_coefficient": row,
        "retained_row_coefficient": 20161, "required_C0_bits": precision.bit_length(),
        "halving_integer_inequality": [73**2, 2 * maxchild**2],
        "G_exponent": 30000, "E_exponent": 100000, "C0_exponent": 210000,
    }
    return {
        "group_bits": group.bit_length(), "finite": finite, "strict_checks": checks,
        "guard_bits": {name: {"actual_bits": value.bit_length(), "bound_exponent": exponent}
                       for name, (value, exponent) in guards.items()},
    }


def require_correct_cover(group):
    require(group == dot_group_order(73), "wrong binary dot-product cover order")


def run(root):
    selected, invoice, owners = load_sources(root)
    audit_inputs(invoice, owners)
    small = [enumerate_bases(n) for n in range(1, 8)]
    for row in small:
        require(row["complete_bases"] == dot_group_order(row["dimension"]), "enumeration/order disagreement")
    group = dot_group_order(73)
    # A different exact product, plus the direct enumeration above. No floats.
    classical_product = (1 << 36)
    for j in range(36):
        classical_product *= (1 << 72) - (1 << (2 * j))
    require(group == classical_product, "alternative order product")
    actual = invoice_metrics(group, invoice, owners)
    require(actual["finite"] == invoice["finite"], "finite receipt mismatch")
    require(actual["strict_checks"] == invoice["strict_checks"], "strict receipt mismatch")
    require(all(actual["strict_checks"].values()), "selected guard failed")

    # These are intentionally invalid models; they do not mutate production.
    mutants = {
        "omit_cover_multiplicity": 1,
        "use_even_dimension_72": dot_group_order(72),
        "omit_last_symplectic_pair": symplectic_order(70),
        "omit_powers_of_two": group >> (36 * 36),
        "use_all_invertible_matrices": 1,
    }
    for j in range(73):
        mutants["use_all_invertible_matrices"] *= (1 << 73) - (1 << j)
    controls = {}
    for name, wrong_group in mutants.items():
        try:
            require_correct_cover(wrong_group)
        except ValueError:
            rejected = True
        else:
            rejected = False
        require(rejected, "group control escaped: " + name)
        metrics = invoice_metrics(wrong_group, invoice, owners)
        controls[name] = {
            "cover_binding_rejected": rejected,
            "group_bits": wrong_group.bit_length(),
            "failed_guards": [k for k, ok in metrics["strict_checks"].items() if not ok],
            "physical_row_coefficient": metrics["finite"]["physical_row_coefficient"],
        }
    require(all(not controls[name]["failed_guards"] for name in mutants if name != "use_all_invertible_matrices"),
            "undercount control should demonstrate guards alone are insufficient")

    # Monotone one-parameter stress test: this changes only cover multiplicity.
    last = (20160 - actual["finite"]["physical_row_coefficient"]) // 2
    before = invoice_metrics(group << last, invoice, owners)
    after = invoice_metrics(group << (last + 1), invoice, owners)
    require(all(before["strict_checks"].values()), "last safe inflation failed")
    failures = [k for k, ok in after["strict_checks"].items() if not ok]
    require(failures == ["row"], "first inflation failure is not row-only")
    return {
        "status": "PASS_ORTHOGONAL_COVER_INVOICE_AUDIT",
        "base_commit": BASE, "assignment_seed": 65,
        "scope": "Binary dot-product cover order and finite invoice only; no new kappa or full theorem proof.",
        "selected_kappa_unchanged": selected["kappa"],
        "enumeration": small,
        "dimension_73": {"exact_group_order": str(group), **actual},
        "negative_controls": controls,
        "cover_only_inflation": {
            "last_passing_power_of_two": last,
            "last_passing_row_coefficient": before["finite"]["physical_row_coefficient"],
            "first_failing_power_of_two": last + 1,
            "first_failing_row_coefficient": after["finite"]["physical_row_coefficient"],
            "first_failed_guards": failures,
            "scope": "All other admitted invoice quantities fixed; not a construction or supplier improvement.",
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=HERE.parents[1])
    parser.add_argument("--write-certificate", type=Path)
    args = parser.parse_args()
    result = run(args.root)
    if args.write_certificate:
        args.write_certificate.write_text(json.dumps(result, indent=2) + "\n")
    else:
        expected = json.loads((HERE / "CERTIFICATE.json").read_text())
        require(result == expected, "certificate mismatch")
    print(result["status"] + " dimensions=1..7 guards=9 controls=5 kappa=unchanged")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print("FAIL_ORTHOGONAL_COVER_INVOICE_AUDIT: " + str(exc), file=sys.stderr)
        sys.exit(1)
