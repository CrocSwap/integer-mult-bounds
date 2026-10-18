#!/usr/bin/env python3
"""Exact conditional application of four inherited cover contracts."""

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_SOURCES = {
    "schema_version": 1,
    "base_commit": "463113d675af7410ac91d53a4fed51ec6494eb9a",
    "files": [
        {
            "path": "certificates/selected-result.json",
            "usage": "provenance",
            "git_blob": "b1fea0c94436b236cc2b7d41a7be032811b94c81",
            "sha256": "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129",
        },
        {
            "path": "docs/research/agent-task-catalog.json",
            "usage": "provenance",
            "git_blob": "67f085acd86acd7d4e03922d9cf4b26bca66fed5",
            "sha256": "47b42433f5a85809a3aadd29c2c339da2c6ed728e4f7762df6b88bccb7874cf0",
        },
    ],
    "retained_files": [
        {
            "path": "vendor/PR3282-RESULT.json",
            "usage": "live-result",
            "commit": "9607079de93907d87e6430d6de154f21a66c03e4",
            "source_path": "research/p112-b6-t4-reconciliation/RESULT.json",
            "git_blob": "8c0fadc2f983e201b4b0a9d3d82d4af7247d07e8",
            "sha256": "ece30256291c3e9cace2c64dcc3b45f876d68198e30de072260f3e71b599dec2",
        },
        {
            "path": "vendor/PR3282-PROOF.md",
            "usage": "proof-contract",
            "commit": "9607079de93907d87e6430d6de154f21a66c03e4",
            "source_path": "research/p112-b6-t4-reconciliation/PROOF.md",
            "git_blob": "d1a2b2057f04120f2661f72bab9c3b1294d35448",
            "sha256": "66fad2325fb51fa6d04ef1787730b5cca915e82df5c5cf14b14e49b13e294025",
        },
        {
            "path": "vendor/PR3154-TWOSIDE.md",
            "usage": "proof-contract",
            "commit": "708f0ad8928c383de8294aea3c126e9461d2066d",
            "source_path": "research/p112-reduction-to-conjectures/checks/TWOSIDE/NOTES.md",
            "git_blob": "e3fd3f2b1dfd77b597f000b38ec2dbec3dbca931",
            "sha256": "226cd59ccc6bc065319e5e4c4768c889206169ff58f74ef4053eeadc5b2e03c8",
        },
        {
            "path": "vendor/PR3154-FINITE.md",
            "usage": "proof-contract",
            "commit": "708f0ad8928c383de8294aea3c126e9461d2066d",
            "source_path": "research/p112-reduction-to-conjectures/checks/FINITE/NOTES.md",
            "git_blob": "afbb86f136ff79d238bb3c38d58e7ea9b35845ac",
            "sha256": "d31b2a79a547d7159ce30fea3424c782771e3d786000bf7309301bd8619b06f4",
        },
        {
            "path": "vendor/PR3154-PROOF-MAP.md",
            "usage": "proof-contract",
            "commit": "708f0ad8928c383de8294aea3c126e9461d2066d",
            "source_path": "research/p112-reduction-to-conjectures/PROOF_MAP.md",
            "git_blob": "d7e099594afb18a0ad877dbaad140144610e5223",
            "sha256": "7e39cb92529a8b574712a3c9442fe1becf7bfefe0b2848c75f80dccc5d66022e",
        },
        {
            "path": "vendor/PR3154-full_b.txt",
            "usage": "recorded-evidence",
            "commit": "708f0ad8928c383de8294aea3c126e9461d2066d",
            "source_path": "research/p112-reduction-to-conjectures/evidence/full_b.log",
            "git_blob": "57f8ffa16638d17f7065eab9cfd8ad047d35be4b",
            "sha256": "f15d2f0ed834cdf6edf8f21f076df20f17d6d9ca94d0c67025e0660440d548a7",
        },
        {
            "path": "vendor/PR3161-PROOF.md",
            "usage": "proof-contract",
            "commit": "a1aba8389b87412e6f72ccf4d11f31e0ea232327",
            "source_path": "research/p112-mixed-rank-reduction/PROOF.md",
            "git_blob": "ea6b723fd1298521f8751be5ad8f7a7deba94f06",
            "sha256": "77cbd91916283e31c612c4a851d478eaa8e60e1c204e65e3e324c6770cc40358",
        },
    ],
}
CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
# id, first flat rank, second flat rank, deleted-line cap, span bound, residual rank
RULES = (
    ("alpha74", 7, 4, 0, 4, 7),
    ("beta7p2", 6, 6, 2, 4, 7),
    ("beta6p4", 6, 6, 4, 1, 6),
    ("beta6p8", 6, 6, 8, 3, 6),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    require(path.stat().st_size <= 500_000, "oversize input")
    return json.loads(path.read_text())


def sources(root):
    manifest = read_json(root / "SOURCES.json")
    require(
        json.dumps(manifest, sort_keys=True)
        == json.dumps(EXPECTED_SOURCES, sort_keys=True),
        "source inventory/schema/usage changed",
    )
    expected = {r["path"] for r in manifest["retained_files"]}
    actual = set()
    for index, entry in enumerate((root / "vendor").iterdir()):
        require(
            index < 8 and entry.is_file() and not entry.is_symlink(),
            "retained inventory bound",
        )
        actual.add(str(entry.relative_to(root)))
    require(actual == expected, "unexpected or missing retained input")
    for row in manifest["retained_files"]:
        file = root / row["path"]
        require(not file.is_symlink(), "source symlink")
        require(file.stat().st_size <= 500_000, "oversize source")
        raw = file.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "live input hash")
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source blob")
    return read_json(root / "vendor/PR3282-RESULT.json")


def historical(weights):
    n = len(weights)
    if sum(w - 2 for w in weights) >= 36:
        return False
    distance = (0, 53, 78, 92, 100, 106, 109)
    for level in range(1, 7):
        kept = weights[: n - 6 + level]
        general = sum(CAP[w] for w in kept)
        local = sum(min(CAP[w], 32) for w in kept)
        if level == 1 and local < 53 and general < 73:
            return False
        if level == 2 and local < 78 and general < 82:
            return False
        if level >= 3 and general < distance[level]:
            return False
    basis = weights[: n - 6]
    if sum(CAP[w] for w in basis) >= 53:
        return True
    if sum(basis) <= 7:
        return False
    for bits in itertools.product((0, 1), repeat=len(basis)):
        if all(
            sum(w for w, bit in zip(basis, bits, strict=True) if bit == k) <= 6
            for k in (0, 1)
        ):
            return False
    return True


def validate_witness(weights, rule, witness):
    _, a, b, budget, span, residual = rule
    groups = witness["groups"]
    require(len(groups) == 3, "three cover roles required")
    chosen = [i for group in groups for i in group]
    require(all(type(i) is int and 0 <= i < len(weights) for i in chosen), "index")
    require(
        len(chosen) == len(set(chosen)) == len(weights) - 6, "quotient basis partition"
    )
    require(sum(CAP[weights[i]] for i in chosen) < 53, "quotient injectivity")
    require(sum(weights[i] for i in groups[0]) <= a, "first flat rank")
    require(sum(weights[i] for i in groups[1]) <= b, "second flat rank")
    require(sum(CAP[weights[i]] for i in groups[2]) <= budget, "common line cap")
    exceptions = sum(
        weights[i] > residual for i in range(len(weights)) if i not in chosen
    )
    require(
        witness["exceptional_endpoints"] == exceptions, "exceptional endpoint count"
    )
    require(
        witness["direction_bound"] == span + exceptions < 6,
        "six independent directions",
    )


def attempts(weights, rule):
    _, a, b, budget, span, residual = rule
    count, witness = 0, None
    for chosen in itertools.combinations(range(len(weights)), len(weights) - 6):
        if sum(CAP[weights[i]] for i in chosen) >= 53:
            continue
        extra = sum(
            weights[i] > residual for i in range(len(weights)) if i not in chosen
        )
        if span + extra >= 6:
            continue
        for roles in itertools.product(range(3), repeat=len(chosen)):
            groups = [
                [i for i, role in zip(chosen, roles, strict=True) if role == k]
                for k in range(3)
            ]
            if (
                sum(weights[i] for i in groups[0]) > a
                or sum(weights[i] for i in groups[1]) > b
            ):
                continue
            if sum(CAP[weights[i]] for i in groups[2]) > budget:
                continue
            count += 1
            if witness is None:
                witness = dict(
                    groups=groups,
                    exceptional_endpoints=extra,
                    direction_bound=span + extra,
                )
    if witness is not None:
        validate_witness(weights, rule, witness)
    return dict(count=count, witness=witness)


def calculate(root):
    old = sources(root)
    domain = [
        w
        for n in range(6, 11)
        for w in itertools.combinations_with_replacement(range(2, 8), n)
    ]
    rows = [list(w) for w in domain if historical(w)]
    require(len(domain) == 7546 and len(rows) == 69, "historical domain")
    require(
        rows == [row["weights"] for row in old["rows"]], "predecessor historical rows"
    )
    require(
        sum(row["primary"] is not None for row in old["rows"])
        == old["certified"]
        == 62,
        "predecessor inventory coverage",
    )
    output = []
    for weights, previous in zip(rows, old["rows"], strict=True):
        found = {rule[0]: attempts(weights, rule) for rule in RULES}
        output.append(
            dict(
                weights=weights,
                previous=previous["primary"],
                attempts=found,
                covered=previous["primary"] is not None
                or any(x["count"] for x in found.values()),
            )
        )
    new = [r["weights"] for r in output if r["previous"] is None and r["covered"]]
    remaining = [r["weights"] for r in output if not r["covered"]]
    return dict(
        schema=1,
        domain=7546,
        historical=69,
        previous=62,
        combined=sum(r["covered"] for r in output),
        newly_accounted=new,
        inventory_uncertified=remaining,
        rows=output,
    )


def main():
    result = calculate(ROOT)
    require(result == read_json(ROOT / "RESULT.json"), "result receipt mismatch")
    print(
        "PASS_ORIGINAL_COVERS",
        result["combined"],
        "of",
        result["historical"],
        "newly_accounted",
        len(result["newly_accounted"]),
    )


if __name__ == "__main__":
    main()
