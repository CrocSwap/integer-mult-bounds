#!/usr/bin/env python3
"""Failure controls for the port-dependent chart-pair classification."""

from verify import (
    DIM,
    I_UNIT,
    NEG_I,
    ONE,
    c_eigenvalue,
    classify,
    closed_transport,
    failures,
    parity,
    phase_forgotten_matches,
    transport,
)


def expect(condition, message):
    if not condition:
        raise SystemExit(message)


def main():
    row = classify()
    expect(row["matching_pairs"] == 16, row)
    expect(row["failing_pairs"] == 240, row)
    expect(failures(0, 0) == [], "identity pair must match")
    expect(len(failures(1, 0)) == 8, "nonzero exit against I must miss half the characters")
    expect(c_eigenvalue(0, 7) == ONE, "C_0 is the identity")
    expect(c_eigenvalue(1, 1) == I_UNIT, "odd character of C_1 is i")
    expect(transport(1, 0, 1) == NEG_I, "C_0 C_1^{-1} multiplies an odd character by -i")
    expect(closed_transport(3, 1, 2) == transport(3, 1, 2), "closed form drifted")
    false_matches = phase_forgotten_matches()
    expect(false_matches == 256, false_matches)
    expect(false_matches != row["matching_pairs"], "phase-blind witness must not equal the theorem")
    # Disagreement is exactly the odd set of one nonzero linear form.
    for gap in range(1, DIM):
        odd = [z for z in range(DIM) if parity(gap, z)]
        expect(len(odd) == 8, gap)
        expect(failures(0, gap) == odd, (gap, failures(0, gap), odd))
    print(
        "PASS_P104_PORT_CHART_PAIR_CONTROLS "
        "controls=counts,identity,half_fail,eigenvalues,closed_form,phase,odd_set"
    )


if __name__ == "__main__":
    main()
