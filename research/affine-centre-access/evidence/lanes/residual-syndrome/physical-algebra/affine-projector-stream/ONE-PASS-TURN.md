# A projected quarter turn with one code at each boundary

Three complete projector shears need not encode and decode their owner
fields three times. This note gives the exact combined operation.
It uses the same fixed affine projector and the same two physical
owner cuts as `STREAM.md` or `ODD-WIDTH.md`. It does not combine
different projectors or assume equal internal owner frames.

Let `L=EBP` be the leaf map and `J=P^-1 B^-1 E^T` its zero-detail
inverse. Thus `JL=Pi` and `LJ=I`. Encode both fields once, retain every
detail, and write their leaf values as `a,b`.

If the two physical frames are equal, perform these three leaf updates:

    b += a,
    a -= b,
    b += a.

Their exact result is `(a,b)=(-b_old,a_old)`. Invert both codes once.
The complete physical map is

    x'=(I-Pi)x-Pi y,
    y'=(I-Pi)y+Pi x.                                  (1)

Both arbitrary complements are retained. The operator has fourth power
identity. The intermediate leaf sum is at most twice the initial
maximum. During decoding, each value is its original partial average
plus the change of its leaf value. Its magnitude is at most three
times the maximum of the two original fields. Thus `k` fractional bits
and two magnitude bits suffice, with saved local operands. In
particular the `3k` bound for three separately implemented shears is
not needed for this combined word.

The code work is two encodes and two decodes. The leaf work is three
ADDs per leaf record. There is no new owner, no new complex native
child, and no extra scan of an uncompressed owner between the three
leaf operations. The fixed-tape and conditional recursive hypotheses
are exactly those in the earlier stream proof and its amendment.

## Different completed frames

Suppose the source and target frames induce the known leaf operators
`O_s` and `O_t` from the even or odd stream interface. Set

    D=O_t O_s^-1.

The correct logical quarter turn is implemented by the physical leaf
map

    (a,b) -> (-D^-1 b,D a).                            (2)

This follows either by direct substitution or by the ordered leaf
shears `b+=Da`, `a-=D^-1 b`, `b+=Da`. Do not replace `D` by the
identity merely because both fields use the same code shape.

At even width, `D` is a Gaussian unit. The three ordered updates can
therefore be used with the same `k` fractional bits. At odd width,
`D` is a Gaussian unit times `C_u^j` on the retained leaf bit. Use
the direct map (2): read the four source and target coefficients at
the two values of `u` into fixed registers, compute the two outputs,
then write them. Each output uses at most one half-integer kernel.
Thus `k+1` fractional bits and two magnitude bits suffice. The
temporary four-term component sums and the decoded values are at
most four times the initial maximum. This direct implementation does
not infer an intermediate precision bound for three separately
rounded leaf kernels.

The added physical operator in (2) is the completed-frame conjugate
of (1). Hence its fourth power is also identity. At the concrete
initial and final cuts in `OWNER-BINDING.md`, the two frames are
equal, so the first version applies at every tensor width.

`check_one_pass_turn.py` checks full finite input columns, all arbitrary
complements, the direct projected map, and fourth power identity.
It reuses the frozen producer's code primitives and is a producer
check, not an independent review. No new controller or finite supplier
invoice is claimed.

The parent proposed the one-code implementation. Research and checks:
OpenAI Codex under the user's direction. No PR, push, or commit was
made. Before any eventual PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
