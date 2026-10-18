#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact arithmetic refinement; finite receipt checks do not rerun native chains.

Credit the PR3054/3042 construction and both retained rational engines.
Substantial OpenAI Codex assistance. No independent arithmetic invention claimed.
"""

import hashlib
import importlib.util
import json
import ast
from fractions import Fraction as Q
from pathlib import Path
from pathlib import PurePosixPath

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
PROFILE = {
    1: 16376940,
    2: 4741920,
    3: 1594737,
    4: 719280,
    5: 137085,
    8: 53280,
    48: 281903,
}


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def read(p):
    return json.loads(p.read_bytes())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p, name):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def authenticate():
    for r in read(P / "SOURCES.json")["files"]:
        if r["usage"] == "input":
            need(sha(ROOT / r["path"]) == r["sha256"], "source drift: " + r["path"])


def check_outer_gap_edit(edits=None):
    edits = read(P / "PRECISION-EDITS.json") if edits is None else edits
    precision = next(e for e in edits if e["old"].startswith("PRECISION = dict("))
    assignment = ast.parse(precision["new"]).body[0]
    digits = {
        keyword.arg: ast.literal_eval(keyword.value)
        for keyword in assignment.value.keywords
    }["endpoint_digits"]
    gap_power = digits + 80  # same R0 exponent used by outer/check_ledger.py
    gap = next(e for e in edits if e["old"].startswith("dict(b=str("))
    claim = next(e for e in edits if e["old"].startswith("b='certified complex_lower"))
    need(f"10**{gap_power}" in gap["new"], "B gap must match the outer R0 exponent")
    need(f"1e-{gap_power}" in claim["new"], "outer claim text must name the exact B gap")
    kappa = next(e for e in edits if e["old"].startswith("kappa == C-Q("))
    need(
        f"10**{digits + 46}" in kappa["new"]
        and f"10**{digits + 22}" in kappa["new"],
        "fixed-grid kappa slacks must follow endpoint precision",
    )


def calculate():
    authenticate()
    check_outer_gap_edit()
    root = load(ROOT / "research/rank7-joint-endframes/tools/root.py", "credited_root")
    other = load(
        ROOT / "research/two-sided-helper-extraction/tools/audit_moment.py",
        "credited_other",
    )
    lo, hi = root.kappa_from_profile(PROFILE, 740, digits=45)
    c = Q((lo * 10**35).__floor__(), 10**35)
    k = c - Q(1, 10**57) - Q(1, 10**81)
    old = Q(
        read(ROOT / "research/rank7-t740-carrier-skips/evidence/ADMISSION-RESULT.json")[
            "kappa"
        ]
    )
    latest = Q("0.001729737950064278551242895823") - Q(1, 10**52) - Q(1, 10**76)
    need(k > old and k > latest and c <= lo < hi < c + Q(1, 10**35), "strict gain over PR3054 and PR3115; 35-digit root bracket")
    need(sum(r * n for r, n in PROFILE.items()) == 65088 * 740, "complete rank mass")
    for engine in (root, other):
        need(engine.moment(PROFILE, c, 896 * 740)[1] < 1, "accepted endpoint")
        need(
            engine.moment(PROFILE, c + Q(1, 10**35), 896 * 740)[0] > 1,
            "next grid rejected",
        )
        for rank in (1, 48):
            bad = dict(PROFILE)
            bad[rank] += 1
            need(engine.moment(bad, c, 896 * 740)[0] > 1, "unpaid child rejected")
    return {
        key: str(v)
        for key, v in dict(
            kappa=k,
            previous=old,
            gain=k - old,
            latest=latest,
            gain_over_latest=k-latest,
            complex_lower=c,
            root_lower=lo,
            root_upper=hi,
        ).items()
    }


def completion(e):
    need(
        e["baseline_complete"] is True and e["candidate_complete"] is True,
        "both actual complete releases required",
    )
    need(
        e["status"] == "PASS_T740_SIX_SKIP_PRECISION35_COMPLETE_RELEASE",
        "complete refinement",
    )


def expected_adapter_hashes():
    original = ROOT / "research/two-sided-helper-extraction/tools/admit_channel408.py"
    record = read(
        ROOT / "research/rank7-t740-carrier-skips/evidence/ADAPTER-DERIVATION.json"
    )
    inherited = record["changes"]["admit_extension.py"]
    need(sha(original) == inherited["before_sha256"], "original strict source adapter")
    body = original.read_text()
    for edit in inherited["replacements"]:
        need(body.count(edit["old"]) == 1, "inherited exact source preimage")
        body = body.replace(edit["old"], edit["new"])
    baseline = hashlib.sha256(body.encode()).hexdigest()
    need(
        baseline == inherited["after_sha256"],
        "complete published adapter reconstructed",
    )
    for edit in read(P / "PRECISION-EDITS.json"):
        need(body.count(edit["old"]) == 1, "exact precision source preimage")
        body = body.replace(edit["old"], edit["new"])
    return baseline, hashlib.sha256(body.encode()).hexdigest()


def check_derivation(data):
    baseline, candidate = expected_adapter_hashes()
    need(
        data["reference_sha256"] == baseline and data["candidate_sha256"] == candidate,
        "exact complete source derivation hashes",
    )
    need(
        data["replacements"] == read(P / "PRECISION-EDITS.json"),
        "exact seven declared precision/outer-gap/selector changes",
    )


def expected_command(stage, baseline, python):
    recipe = read(ROOT / "research/rank7-t740-carrier-skips/evidence/RECIPE.json")[
        "commands"
    ]
    derive = [command for name, command in recipe if name == "derive-closed-adapters"]
    selected = [command for name, command in recipe if name == stage]
    need(len(derive) == len(selected) == 1, "unique source-pinned recipe stage")
    prefix = str(PurePosixPath(derive[0][2]).parents[2])
    command = [arg.replace(prefix + "/", str(baseline) + "/") for arg in selected[0]]
    command[0] = python
    return command


def check_evidence(e, arithmetic):
    completion(e)
    for k in ("kappa", "previous", "gain", "latest", "gain_over_latest"):
        need(Q(e[k]) == Q(arithmetic[k]), "exact evidence " + k)
    need(
        e["controls"]
        == dict(admission=139, bit=12, controller=25, independent_owner=8, geometry=6),
        "all actual inherited release controls",
    )
    need(
        len(e["controller_controls"]) == len(set(e["controller_controls"])) == 25,
        "all25 actual controller rejections, not the inherited summary count",
    )
    expected_controls = read(
        ROOT / "research/rank7-t740-carrier-skips/evidence/ASYNC-AUDIT.json"
    )["mutations_rejected"]
    need(
        e["controller_controls"] == expected_controls,
        "every named original controller control retained",
    )
    need(
        e["inherited_supplier_summary_controls"]
        == dict(admission=139, bit=12, controller=15, independent_owner=8, geometry=6),
        "disclosed unchanged inherited supplier summary",
    )
    for key, point in (
        ("baseline", arithmetic["previous"]),
        ("candidate", arithmetic["kappa"]),
    ):
        projection = e[key + "_release_projection"]
        need(
            projection["status"] == "PASS_RELEASE"
            and Q(projection["kappa_decimal"]) == Q(point),
            "actual complete terminal projection: " + key,
        )
        need(
            projection["manifest_sha256"] == e[key + "_package_manifest_sha256"],
            "actual admitted manifest: " + key,
        )
    need(
        e["baseline_native_receipt_sha256"] == e["candidate_native_receipt_sha256"],
        "same authenticated unchanged native receipt",
    )


def check_ledger(ledger, kappa):
    row = ledger["rows"]["struct_boundary_radix_union"]
    need(Q(row["kappa"]["rational"]) == Q(kappa), "actual outer point")
    need(
        len(row["strict_checks"]) == 63
        and all(Q(v["rational"]) > 0 for v in row["strict_checks"].values()),
        "all63 strict rows",
    )
    bad = ledger["rejecting_controls"]["struct_boundary_radix_union"]
    need(
        len(bad) == 17
        and all(
            v and all(Q(x["rational"]) <= 0 for x in v.values()) for v in bad.values()
        ),
        "all17 original outer controls",
    )


def run():
    arithmetic = calculate()
    e = read(P / "evidence/VALIDATION.json")
    check_evidence(e, arithmetic)
    need(
        set(e["files"]) == {"OUTER-LEDGER.json", "DERIVATION.json"},
        "complete declared evidence inventory",
    )
    for name, h in e["files"].items():
        need(sha(P / "evidence" / name) == h, "evidence digest " + name)
    check_derivation(read(P / "evidence/DERIVATION.json"))
    check_ledger(read(P / "evidence/OUTER-LEDGER.json"), arithmetic["kappa"])
    print("PASS_T740_SIX_SKIP_PRECISION35", arithmetic["gain"])


if __name__ == "__main__":
    run()
