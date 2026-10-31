# Caller compatibility and cost scope

The 52-bit optimum is an information statement for the changed function
`H_U(x)=K(U K(2x))`, with the full final 112-owner output available to the
decoder. It does not by itself price a physical implementation or change the
selected multiplication bound.

## Exact boundary for a linear consumer

Write the explicit frame as `U=I+VE`, with `EV=0` and `M^T V=0`. For every
integer z, mode preservation gives exactly

    K(Uz)-K(z)=VEz.

Consequently, for the identity-frame baseline `H_I(x)=K(K(2x))`,

    H_U(x)-H_I(x)=VE K(2x).

A fixed real- or complex-linear observer O therefore sees the same output for every integer
input if `OV=0`. For this particular frame, the condition is also necessary.
The four integer inputs `x=26e_a`, for `a in (0,1,2,4)`, give the columns
of

    E K(2x):  52I_4-G,   G=E M M^T E^T=2I_4+2J_4,

where J_4 is the all-one matrix. Thus `52I-G=50I-2J` has eigenvalues
42,50,50,50 and determinant 5,250,000. These four columns span all of R^4.
If `O H_U=O H_I` on every integer input, then `OV(52I-G)=0`, hence `OV=0`.
This also proves necessity on any finite input range containing those four
witnesses. It does not assert necessity for every smaller reachable set.

In particular, `O=M^T` is compatible. A consumer whose complete use of the
output factors through an observer annihilating V has a possible interface
route to the new function. **The full H_U output must still be retained or
otherwise supplied to the 52-bit decoder.** If only `O H_U` is retained,
its fiber count must be analyzed again; for example, M^T alone discards an
unbounded native-mode kernel: adding n v_0 to x changes H_U by 2n v_0 and leaves M^T H_U unchanged. Thus no finite tag recovers arbitrary inputs from that observation alone.
No actual selected caller with this observer and retention contract is
identified here, and physical access to the full output remains charged.

## An inverse endpoint frame does not restore the old output

For `q=R(M^Tz/52)`, the other exact identity is

    U^-1 K(Uz)-K(z)=V E M q.

It is generally nonzero. With `m=row_0(M)^T`, the actual source input
`x=(52e_0-13Mm)/2` is integral, has sup norm 13, and satisfies
`K(2x)=52e_0`. It gives

    U^-1 H_U(x)-H_I(x)=4v_0+2v_1+2v_2+2v_3 != 0.

Thus a caller requiring the complete old output needs a further,
quotient-dependent correction, rather than just U^-1. If this correction
restores exactly H_I and retains no additional observation, the old A_2
maximum fiber and 56-bit tag lower bound return. The identity-frame zero
fiber is already attained inside the coarse sup-norm bound 168. A smaller
actual input range needs its own analysis. Any retained correction or side
observation belongs in the combined recovery alphabet and storage bill.

## Optimistic complete invoice and remaining obligations

The four sources are disjoint from all sixteen destinations, and the four
update columns have disjoint supports. Hence U and U^-1 each have a literal
schedule of sixteen signed full-word additions per real coordinate, with
coordinate sup-norm amplification at most two. This algebraic schedule
requires no extra coordinate, but does not make physical delivery or carry
scratch free.

A complete forward-and-recovery invoice must include

    source access + relative-grid provision + first K + U + second K
      + tag encoding + live quotient/tag storage
      + unranking + output-mode access + two M lifts + U^-1
      + exact halving + scratch/tag cleanup + downstream consumption.

The declared direct arithmetic has 896 signed additions and eight
round-by-52 operations per K call; its owned zero-writing is destructive.
A direct fresh output projection M^Ty requires 448 signed additions and
the two reconstruction lifts require 896, per real coordinate. Any reuse
of already available modes needs a chronological retention schedule.
The current interface codec's forward replay is verification; if retained
in an operational decoder, it adds two K calls and a forward frame.
Reversible rank/unrank, finite word widths, source movement, quotient and
carry lifetimes, and eventual cleanup have no supplied physical tariff.
Retaining or rereading the original input is a competing interface whose
access/storage must also be priced.

For a coarse input bound H, one conservative forward range envelope is

    Q(B)=floor((56B+26)/52),   k(B)=B+4Q(B),
    B0=2H, B1=k(B0), B2=2B1, B3=k(B2).

Kernel mode accumulators can reach 56B; partial reconstruction lifts and
codec arithmetic need additional prefix bounds. The theorem does not
establish that a selected caller's existing registers cover these bounds.

The four-bit packed-tag reduction compares interfaces already supplying
the same one-bit relative refinement. Counting only added fractional
positions and a separately packed tag gives 112+56=168 positions for the
parity-I baseline and 112+52=164 for this frame, per real coordinate. A
same-grid two-call interface needs 60 tag bits; introducing the refinement
would instead add 104 positions before magnitude, scratch and movement.
Absolute working precision alone does not establish a relative grid gain.
For multiple coordinates packed jointly, use the ceiling of the logarithm
of the complete product alphabet, rather than assuming four saved bits
per coordinate after arbitrary pooling.

No selected paid rank, productive target, complete caller invoice or
precision/tape premise changes here. The complex supplier remains binding
under the selected certificate. All five assumptions remain:
`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and
`analytic_recovery`. **No new κ.**

This scope analysis builds on the relative-grid and physical-caller
limitations of CrocSwap/integer-mult-bounds#5444, the same-grid recovery
result in #5323, and the source arithmetic in #5035. Prepared for @CubeJerry
with substantial OpenAI Codex assistance, including separate source-bound
compatibility and cost review.
