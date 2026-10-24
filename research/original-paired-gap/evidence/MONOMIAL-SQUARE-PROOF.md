# Complementary gaps from a monomial square

The paired phase-gap construction does not require a fourth root of the
identity or a port-diagonal phase. It applies to an invertible data
operator whose square has legal monomial access. The original complex
phase and the earlier paired Walsh phase are special cases.

This theorem supplies an exact local protocol and removes all later
centre feedback when the stages share one transported phase operator.
It does not supply its final odd-phase boundary operations or a complete
supplier invoice.

## Hypotheses

Let Q be an invertible operator on the data fields. Put `S=Q^2`. Assume
that S and S inverse are legal monomial maps with known costs. Let F be
the common productive output operator, with `FQ=QF`. Thus F also commutes
with S. Assume the following exact physical interface is available:

    source X: Q -> F,
    target Y: I -> FQ^-1,
    mode u:   I -> F.

The two raw content words are

    forward:  y'=y+(I-KR)x-Ku,   u'=-u-2Rx,   x'=x;
    backward: x'=x-(I+KR)y-8Ku,  u'=-u-Ry/4,  y'=y.   (1)

R and K need not commute with Q or S. Their coefficient operations must
have legal pointwise scalar or monomial access at the displayed physical
endpoints. They must intertwine the productive frames:

    F_mode R=R F_data,       F_data K=K F_mode.       (1a)

Here F_data and F_mode are the copies of the stated common F on their
respective field types. Scalar field matrices satisfy (1a). An arbitrary
monomial R or K need not satisfy it. Without (1a), the output physical
coefficients must instead be the conjugates `F_mode R F_data^-1` and
`F_data K F_mode^-1`, and their legal access is a new hypothesis.
The protocol below uses (1a).

All input fields, including the modes and ordinary borrowed
helpers, can be arbitrary. The raw words must have their stated helper
restoration contracts.

Use two replicas of this interface in the same chart. Extend Q, F, R,
and K by the replica identity. Define, on the paired data type,

    A=[[0,I],[S^-1,0]],
    T=Q A=[[0,Q],[Q^-1,0]].                          (2)

A is monomial. Direct multiplication gives

    AQ=QA,       T^2=I,       S A Q^-1=T.            (3)

There is no hypothesis `Q^4=I`. The A in (2) acts on data fields; in
general it cannot act on the centre index or move through R or K.

## Ordered physical protocol

For the forward word, apply `u-=R A X_physical` before both raw cores.
Its logical input is `u=z-RTx`. After both cores, apply
`u+=R X_physical`, then `Y_physical+=A K U_physical`. The exact result is

    v=-z-Gx,       x'=x,       y'=y+x+Hv,
    G=R(I-T),      H=(I+T)K.                         (4)

For the backward word, first apply

    X_physical-=8 S A K z,
    u=z-RY_physical/8.

After both raw cores, apply `u+=R S A Y_physical/8`. The exact result is

    v=-z-Gy/8,     y'=y,       x'=x-y-8Hz.           (5)

The input source conversion is `Q^-1 S A=T`. The output target
conversion is `S A Q^-1=T`. These identities and (1) prove (4)--(5),
with the displayed operator order. No R/K phase commutation is used.

Only monomial access to S or its inverse is added to the scalar graphs.
For example, the forward input graph reads the other replica directly
in one direction and through S inverse in the other. The backward
input graph uses S in one direction and the identity in the other.
Every translated or reindexed source view is restored after its ADDs.
The costs of those maps remain part of the implementation invoice.

## All-stage consequence

Suppose the actual stage charts transport their phases to the same Q
on one global data space. For any legal mode gauges N_s, set

    G_s=N_s^-1 R_s(I-T),
    H_t=(I+T)K_t N_t.

Then for every pair of stages,

    G_s H_t=N_s^-1 R_s(I-T^2)K_t N_t=0.             (6)

No relation between the centre images at the two stages is needed.
The same cancellation holds with a data bridge B between the two gaps
when B commutes with T. Thus the existing complementary-gap controller
and its arbitrary-mode decoder apply. If stages have unrelated T_s,
equation (6) does not follow and is not claimed.

## Actual original-complex specialization

The actual native phase has `S=diag_p(X_p^tensor(lambda))=S^-1`. Every
actual route fixes its port direction and transports Q to the same
global cover operator. The emitted pair in `ORIGINAL-PAIRED-GAP.md`
uses the existing replica indices and no extra replica. Its two cores
retain 10,112 native events and paid rank 11,044. Each pair adds 2,688
physical ADDs and 448 translation maps, but no native child. The complete
explicit scalar bounds are 433,924 forward and 442,884 backward.

For this unit-modulus specialization, the forward wrapper prefix has
infinity norm at most 57, and its suffix has norm at most 58. The
backward bounds are 9 and 8. These follow from `||R||_infinity=56` and
`||K||_infinity=1`, in the literal operation order. They bound only the
extra wrappers; the raw core, native children, global controller, and
recursive precision still need their own bounds. All new scalar
coefficients are dyadic. No new odd denominator occurs.

Independent native review of the actual paired payload is in
`coherent-port/ORIGINAL-PAIRED-GAP-NATIVE-REVIEW.md`. The general
abstraction in this note is an algebraic consequence, not a claim that
an unspecified Q already has an admitted native core.

The coordinating agent supplied the monomial-square abstraction.
The raw interfaces and physical graph method come from history-encoding;
the complementary-gap argument comes from coherent-port and the global
decoder from encoded-controller. This note and the actual paired
emission were written with substantial OpenAI Codex assistance under
the user's direction. No selected-frontier change is claimed.
