#!/usr/bin/env python3
"""Boundary controls for the audit adapter. Nick Petalas. Apache-2.0."""

import runpy
import tempfile
from pathlib import Path

AUDIT = runpy.run_path(str(Path(__file__).with_name("verify.py")))


def main():
    sources = AUDIT["authenticated_sources"]()
    subject = sources[AUDIT["SUBJECT"]]
    rejected = 0
    # Only the three documented sites may be substituted, each exactly once.
    for site in (
        "++stats.compositions;",
        "if (!capacity(gaps)) return;",
        "search(domains_for(gaps), true);",
    ):
        for bad in (subject.replace(site, "", 1), subject + "\n// " + site):
            try:
                AUDIT["adapted_source"](bad)
            except ValueError:
                rejected += 1
            else:
                raise ValueError("ambiguous or missing adapter site accepted")
    with tempfile.TemporaryDirectory(prefix="caller-source-controls-") as directory:
        root = Path(directory)
        for name, content in sources.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        AUDIT["authenticated_sources"](root)
        for name, content in sources.items():
            path = root / name
            path.write_text(content + "\n")
            try:
                AUDIT["authenticated_sources"](root)
            except ValueError:
                rejected += 1
            else:
                raise ValueError("corrupted scientific source accepted")
            path.write_text(content)
        AUDIT["authenticated_sources"](root)
    AUDIT["need"](rejected == 9, "boundary control count")
    print("PASS_CONNECTOR_AUDIT_BOUNDARIES 9")


if __name__ == "__main__":
    main()
