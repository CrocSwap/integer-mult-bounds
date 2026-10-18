"""Check real package validation without foreign predecessor Git objects."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(PACKAGE))

import research_package
import verify


def main():
    sources = verify.read_json(PACKAGE / "SOURCES.json")
    verify.require(len(sources["files"]) <= 16, "cold source inventory capacity")
    real_blobs = research_package.git_blobs

    def ancestor_only_blobs(root, specs):
        # A full-history checkout supplies ancestors, not unrelated pending heads.
        # Allowed objects still go through the real Git/SHA256 provenance validator.
        specs = tuple(specs)
        verify.require(len(specs) <= 16, "cold source inventory capacity")
        for spec in specs:
            commit = spec.split(":", 1)[0]
            ancestry = subprocess.run(
                ["git", "-C", str(root), "merge-base", "--is-ancestor", commit, "HEAD"],
                capture_output=True, check=False, timeout=10)
            if ancestry.returncode != 0:
                raise ValueError("missing or non-blob Git source: " + spec)
        yield from real_blobs(root, specs)

    unavailable = "0" * 40 + ":" + sources["files"][0]["path"]
    try:
        tuple(ancestor_only_blobs(REPO, (unavailable,)))
    except ValueError as error:
        verify.require(str(error) == "missing or non-blob Git source: " + unavailable,
                       "cold-source rejection changed")
    else:
        raise ValueError("unavailable source commit was accepted")
    with patch.object(research_package, "git_blobs", ancestor_only_blobs):
        research_package.validate(REPO, "research/p112-a3-six-flat")
    verify.source_check()
    print("PASS_P112_A3_COLD_SOURCES ancestor_git_only archived_bytes_authenticated")


if __name__ == "__main__":
    main()
