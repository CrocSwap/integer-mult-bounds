# Proof sketch: b = Z Q Y is not in the retained span

Notation as in `research/coupled-query-transport/PROOF.md` (#5415):
`X = Dx − Ry + RWh`, `Y = Dy`, `R = DQ`, `b = Z Q Y = Z R y`.

## Native level

In the row model of `research/kappa-owned-relation-20261023/native.py` a field
value is a pair (row, frame). The row is a finite rational combination of
(input role, warp word); a paid climb or centre changes only the frame; free
operations are same-frame ADD and SCALE with dyadic coefficients, owned COPY and
CLEAR, and warps. Two fields can be combined for free only in the same frame.

`Y_k` ends in an 8-dimensional frame with row `y_k`, and the rank-one query
moves it to the unique full frame. So `Q Y_k` is the value (row `y_k`, full
frame), and `R y_k` is the `y` part of the endpoint `X_k = (x_k − y_k, full)`.
A free producer of `b` must output combinations of `Q Y_k` from values that
existed in the full frame at some time; owned copies make every time available,
so the available rows are exactly the span `V` of all full-frame versions.
`verify.py` computes `V` and shows `V ∩ span{y_k with any warp word} = 0`.
Hence no combination of the `Q Y_k`, in particular no coordinate of `b`, is
available without a new paid frame change.

## Caller level

Rows are noncommutative words over `Q, D_s, W_s, Z_s` with `Q D_s = D_s Q`
(#5415 `word_normal`). Free operations: scalar ADD of versions, left factors
`Q^{±2}` (Q_POWER), `W_t`, signed swaps, and `Z_s` applied to a whole bank. No
version word begins with `Z`; a left factor that does not begin with `Z_s`
produces words that do not begin with `Z_s`, and every word of `b = Z_s Q Y`
begins with `Z_s`. Removing the leading `Z_s` is injective, so `b` is a free
combination iff `Q Y` lies in the span of the free images of the versions.
`verify.py` shows it does not, at each of the 18 backward FULL returns, and also
with every version of the whole caller history.

## Arithmetic

All coefficients are dyadic. Reduction modulo the odd prime `2^61 − 1` is a
ring map on such rationals, so a rational identity `target = Σ c_i v_i` maps to
an identity modulo p. The computed non-membership modulo p therefore implies
non-membership over the rationals.

## Part 2: response reuse

Native: with the same rows and frames, a paid climb of f (A → B) producing row r
can be removed iff (r, B) can be built for free before f is next read or written.
Free values in B are the span of the versions that stood in B, kept by owned
copies. f itself can always be emptied by COPY C←f, f −= C, CLEAR C, followed by a
zero-retag A → B. The test of r against that span is therefore exactly the
removal criterion in this grammar (EARLY: versions before the climb; LATE:
versions before the next touch of f). To exclude f's own new value from the LATE
span, it enters as r + e_tag with a fresh coordinate. Then e_tag is in the span
iff r is a combination of the other versions. Within LATE, other climbs' results
also carry their own tags. A reuse of another climb's raw result is then seen by
the EARLY test of whichever of the two climbs comes later.

Caller: a paid caller output can be removed iff it is a free image of earlier
versions. Free left factors are `Q^{±2}`, `W_t` and `Z_t`; combinations use
scalar ADD.
