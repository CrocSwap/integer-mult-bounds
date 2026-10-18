"""Bind the named profile to PR3154's unchanged, top-level table program."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vendor.bk2b import feasible, killed

PROFILE = (2, 2, 2, 5, 6, 6, 6, 7, 7, 7, 7)
print(
    "PASS_HISTORICAL_CALLER",
    feasible(PROFILE, 6),
    killed(PROFILE, 6),
    sum(w - 2 for w in PROFILE),
)
