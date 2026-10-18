#!/usr/bin/env python3
"""Small behavioral controls for the D10 package."""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_SPEC = spec_from_file_location("d10_verify", Path(__file__).with_name("verify.py"))
verify = module_from_spec(_SPEC)
_SPEC.loader.exec_module(verify)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL_D10_PACKAGE_TEST: " + message)


def main() -> None:
    require(len(verify.PROJECTORS) == 28, "rank-one idempotent census")
    require(verify.GROUP_TABLE[verify.S][verify.T] == verify.R, "st=r relation")
    require(verify.GROUP_TABLE[verify.T][verify.S] == verify.R_INV, "ts=r^-1 relation")
    require(verify.group_mul(verify.S, verify.S) == verify.E, "s involution")
    require(verify.group_mul(verify.T, verify.T) == verify.E, "t involution")

    labels, projectors = verify.direct_four_call()
    direct = verify.word_state(labels, projectors)
    require(direct == verify.TARGET, "four-call direct endpoint")
    for drop in range(4):
        short_labels = labels[:drop] + labels[drop + 1:]
        short_projectors = projectors[:drop] + projectors[drop + 1:]
        require(verify.word_state(short_labels, short_projectors) != verify.TARGET,
                "one-call omission control " + str(drop))

    wrong_labels = list(labels)
    wrong_labels[1] = verify.S
    require(verify.word_state(tuple(wrong_labels), projectors) != verify.TARGET,
            "wrong-label control")
    swapped_target = tuple((1 << 0) if g == verify.R_INV else
                           (1 << 4) if g == verify.R else
                           (1 << 8) if g == verify.E else 0
                           for g in range(verify.NGROUP))
    require(direct != swapped_target, "role-swap corruption control")
    require(verify.word_state((verify.T, verify.S, verify.S, verify.T),
                              (1, 1, 16, 16)) == swapped_target,
            "role-swapped positive control")
    require(verify.word_state((verify.S, verify.T, verify.S),
                              (1, 1, 1)) != verify.TARGET,
            "proposed three-call supersequence control")
    print("PASS_D10_PACKAGE_CONTROLS projectors=28 direct_calls=4 mutations=6")


if __name__ == "__main__":
    main()
