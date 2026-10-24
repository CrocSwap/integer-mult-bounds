"""Two ordered CRT targets: protected unary geometry to a paid guard stencil.

The seven protected unary inputs are G,H,K,Y,J0,J1,B. The runtime accesses
tapes only through the passed PR4208 marker-driven helpers and read/write/
one-cell-move methods. It never reads host lengths, coordinates, action
counts or tape storage. The target blocks below are explicitly unrolled.

The caller supplies the authenticated retained helper module as base and a
Tape factory whose tapes have the permanent LEFT infrastructure. This module
does no loading or I/O. Normal success returns (eleven private roles, stencil).
All private data and END markers are blank; all heads are at LEFT. Inputs
remain protected on success and on grammar/arithmetic rejection.

ToikY's PR4208 supplies the unary arithmetic, emission and cleanup helpers;
PR4201 supplies the unchanged consumer and atom format; Cinna Davis supplies
the CRT guard predicate. Hiroki KUMAZAKI (@kumagi), with substantial OpenAI
Codex assistance. Apache-2.0. Full lineage and scope are in README/PROOF.
"""


def produce(G, H, K, Y, J0, J1, B, Tape, *, base,
            omit_second_digit=False, omit_second_guard=False):
    """Seven protected canonical unary words -> owned two-target stencil.

    Admits G>=1, H>=2G, K>=G+4, J1>=J0+K, Y>=J1+K. J0 and B
    are nonnegative by unary syntax. Entry and malformed-input contracts
    match the retained helper module, including the unique permanent LEFT
    and initially blank tails. The two fixed mutation flags preserve output
    length while removing digit1's test or the upper target's guard test.
    They are faulty verification programs, not alternative admitted modes.
    """
    HG, HGG, KG, THREE, A, TAIL, J0P, J10, GAP, YJ1, TOP = (
        Tape(), Tape(), Tape(), Tape(), Tape(), Tape(), Tape(), Tape(),
        Tape(), Tape(), Tape())
    stencil = Tape()
    work = (HG, HGG, KG, THREE, A, TAIL, J0P, J10, GAP, YJ1, TOP)
    for tape in work:
        base.empty_word(tape)
    base.empty_word(stencil)
    try:
        for tape in (G, H, K, Y, J0, J1, B):
            base.validate(tape)
        base.positive(G)
        base.difference(H, G, HG)
        base.difference(HG, G, HGG)
        base.difference(K, G, KG)
        base.three(THREE)
        base.difference(KG, THREE, A)
        base.positive(A)
        base.plus_one(G, TAIL)
        base.plus_one(J0, J0P)
        base.difference(J1, J0, J10)
        base.difference(J10, K, GAP)
        base.difference(Y, J1, YJ1)
        base.difference(YJ1, K, TOP)

        stencil.move(1)
        # MSB-first u field: inactive high part, digit1, then digit0.
        base.skip(HGG, stencil)
        if omit_second_digit:
            base.skip(G, stencil)
        else:
            base.digit(G, stencil)
        base.digit(G, stencil)
        # The independent t field has the same two separate digit intervals.
        base.skip(HGG, stencil)
        if omit_second_digit:
            base.skip(G, stencil)
        else:
            base.digit(G, stencil)
        base.digit(G, stencil)

        base.skip(TOP, stencil)
        # Upper target J1: K-1 higher guard bits, then its parity bit.
        if omit_second_guard:
            base.skip(A, stencil)
            stencil.write(base.SKIP)
            stencil.move(1)
            base.skip(TAIL, stencil)
        else:
            base.leading_guard(A, stencil, True)
            stencil.write(("G", False, False, "1", "1"))
            stencil.move(1)
            base.trailing_guard(TAIL, stencil)
        stencil.write(base.SKIP)
        stencil.move(1)
        base.skip(GAP, stencil)
        # Lower target J0: its separate guard and all lower/parity SKIP bits.
        base.leading_guard(A, stencil, True)
        stencil.write(("G", False, False, "1", "1"))
        stencil.move(1)
        base.trailing_guard(TAIL, stencil)
        base.skip(J0P, stencil)
        base.skip(B, stencil)
        stencil.write(base.END)
        base.rewind(stencil)
    except ValueError:
        # All arithmetic rejects before output construction. Every private
        # subtraction output is still a complete END-terminated word on an
        # underflow, so the retained eraser has a valid finite stop marker.
        for tape in work:
            base.erase(tape)
        base.erase(stencil)
        for tape in (G, H, K, Y, J0, J1, B):
            base.rewind(tape)
        raise
    for tape in work:
        base.erase(tape)
    for tape in (G, H, K, Y, J0, J1, B):
        base.rewind(tape)
    return work, stencil
