# Independent proof review of the one-pass projected turn

The stated local turn is correct under the frame and stream hypotheses
of the accepted even and odd projector reviews. This is a proof review.
The producer checker was read, but it was not imported or run. Its 304
finite input-column checks are producer evidence only.

Let `LJ=I`, `JL=Pi`, and `Q=I-Pi`. Then `QJ=0` and `LQ=0`.
The three leaf updates give `(-b,a)` in their stated order. More
generally, for any invertible leaf operator `D`, the ordered updates
give `(-D^-1 b,D a)`. After both codes are inverted, the physical map is

    T = [[Q, -J D^-1 L], [J D L, Q]].

Direct block multiplication gives

    T^2 = diag(I-2Pi,I-2Pi),
    T^4 = I.

No commutation of `D` with a separate leaf operator is used. Every
detail coordinate is retained. Thus both complementary input parts
remain arbitrary, and both are unchanged by the final map.

For the physical frame claim, let the two full frames preserve `Pi`
and induce the displayed leaf frames `O_s,O_t`. The inherited interface
then gives the off-diagonal blocks of the completed-frame conjugate as
`J O_s O_t^-1 L` and `J O_t O_s^-1 L`. These are exactly the blocks
above for `D=O_t O_s^-1`. The order of the two inverses is correct.
This use requires the inherited frame hypothesis. It does not cover an
additional outer address map or a different projector at the next cut.

The guard uses the maximum absolute real or imaginary component of
the two input fields. Each code coefficient is a signed average, so
its magnitude is at most the initial maximum. An equal-frame leaf
turn has intermediate magnitude at most twice that maximum. Its final
leaf change has magnitude at most twice that maximum. Each decoded
coefficient is an original partial average plus a signed leaf change,
so its magnitude is at most three times the initial maximum. The code
uses at most `k` divisions by two. Thus `k` additional fractional bits
and two additional magnitude bits suffice, with saved operands.

At odd width, use the direct two-leaf-bit map, not a bound inferred
from three rounded kernels. A Gaussian unit times `C_u^j` has either
unit entries or half-integer Gaussian entries. Each new real component
is at most twice the initial maximum. Its unhalved four-term sum is
at most four times that maximum. The leaf change is at most three
times the maximum, so each decoded coefficient is at most four times
the maximum. One further fractional bit suffices. The four old complex
coefficients must be saved before either output pair is overwritten;
fixed arithmetic registers are also permitted. These are bounds for
the stated saved-operand arithmetic, not for an unspecified lowering.

The work count is two encodes, two decodes, and three leaf ADDs in the
equal-frame case. The different-frame direct map uses a fixed local
kernel. No uncompressed-owner scan is needed between leaf operations.
The claim of no new owner or complex native child uses this local
stream implementation and the inherited fixed-tape hypotheses. The
conditional recursive path bound remains conditional as stated in the
earlier amendment.

This review does not check `OWNER-BINDING.md`, a full finite primitive
invoice, a new machine implementation, the global controller, owner
admission, or a supplier improvement. Fourth power identity refers to
four uses with the same projector and frame pair. No producer or prior
review file was changed. No PR, push, or commit was made.

Before any eventual PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
