#!/usr/bin/env python3
"""Authenticate the preserved science, review snapshots and source inputs.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
SPDX-License-Identifier: Apache-2.0
"""
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    dependencies = json.loads((ROOT/"DEPENDENCIES.json").read_text())
    for row in dependencies["files"]:
        data = (ROOT/row["local"]).read_bytes()
        require(len(data) == row["bytes"] and sha256(data).hexdigest() == row["sha256"],
                "scientific source changed: "+row["local"])
    bindings = json.loads((ROOT/"REVIEW-BINDINGS.json").read_text())
    adapted = 0
    for row in bindings["files"]:
        data = (ROOT/row["file"]).read_bytes()
        require(len(data) == row["bytes"] and
                sha256(data).hexdigest() == row["packaged_sha256"],
                "frozen reviewed file changed: "+row["file"])
        if "portability_replacements" in row:
            original = data.decode()
            for edit in reversed(row["portability_replacements"]):
                require(original.count(edit["after"]) == 1,
                        "nonunique portability edit: "+row["file"])
                original = original.replace(edit["after"], edit["before"])
            require(sha256(original.encode()).hexdigest() == row["original_sha256"],
                    "adaptation does not reconstruct reviewed script")
            adapted += 1
        else:
            require(row["original_sha256"] == row["packaged_sha256"],
                    "undocumented reviewed-source change")
    review = json.loads((ROOT/"review/classification/RESULT.json").read_text())
    for name, expected in review["reviewed_source_sha256"].items():
        require(sha256((ROOT/name).read_bytes()).hexdigest() == expected,
                "independent review no longer binds current science: "+name)
    require(adapted == 1, "exactly one documented portability adapter")
    print(json.dumps({
        "status": "PASS_NARROW_ALL_ORDER_PACKAGE_BINDINGS",
        "authenticated_scientific_sources": len(dependencies["files"]),
        "bound_reviewed_files": len(bindings["files"]),
        "documented_portability_adapters": adapted,
        "proof_sha256": sha256((ROOT/"PROOF.md").read_bytes()).hexdigest(),
        "scope": "Source and reviewed-byte identity; scientific checks are separate registered commands."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
