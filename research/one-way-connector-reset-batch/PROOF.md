# Proof: one reset makes the five-source connector batch exactly 63 queries

Written proof with an exact finite certificate. No `kappa`, no supplier
admission. Produced by Nick Petalas.

## 1. Interface

Use Ross Richardson's universal connector contract as recorded in
`research/universal-connector-boundary/README.md` (PR #934 and the five-source
boundary package). Sources `x_0,...,x_{n-1}`, one connector row `z`, output
rows `y_i`, all over `F2`. All maps `B_j` and `A_i` are arbitrary `F2`-linear,
possibly noncommuting and noninvertible; sources are read-only; the connector
and the outputs are arbitrarily dirty. A *complete query* is either

    B_j:  z   += B_j x_j          (source call)
    A_i:  y_i += A_i z            (readout)

and the batch is correct when `y_i` ends as
`y_i + A_i (sum_{j in m_i} B_j x_j)` and every other row is restored.

Write `b_j = B_j x_j`. Two cited facts from the predecessor:

* **(P1) even incidence.** Restoration forces every `B_j` count even and every
  `A_i` count even. The predecessor proves this by specializing to `L = 1`,
  identity maps, independent source bits and an independent dirty connector
  bit.
* **(P2) exact restored five-source value.** The 945-canonical-word census
  excludes ten source calls, so the restored minimum is `T(5) = 12`, and the
  all-31-nonzero-mask batch costs exactly `74 = 12 + 2*31`. The four-source
  case is `38 = 8 + 2*15` with `T(4) = 8`.

Both are cited inputs. They are not replayed or re-audited here.

## 2. The extended alphabet

Add exactly one operation

    Z:  z := 0                    (reset, one complete query)

and change one boundary premise: **the connector is consumed**. Its exit value
is unconstrained, so no restoration of `z` is owed. Every other clause of the
contract is unchanged, including restoration of all other rows, read-only
sources, complete fixed-port calls and unit query prices. A caller that still
needs the old connector value must save and restore it, which is a separate
charged obligation and is not used below.

The reset is not free: it is one complete query in every count that follows.

## 3. Upper bound: the Gray schedule

Let `g_0,...,g_{2^n-1}` be the reflected Gray code of `F2^n`: `g_0 = 0`, every
consecutive pair differs in one coordinate, and every vertex occurs once. The
schedule is

    Z;  then for k = 1..2^n-1:   B_{j_k}  (the coordinate flipping into g_k)
                                A_{g_k}  (one readout of the row with mask g_k)

After the reset, `z = sum_{j in q} b_j` where `q` is the current prefix, so the
readout at `g_k` contributes exactly `A_{g_k} b_j` for `j in g_k`. Each row is
read once, at its own vertex, and no `A_i z_0` term survives because `z_0` was
destroyed by the reset. Row `i` therefore ends as
`y_i + A_i (sum_{j in i} B_j x_j)`, and `z` is left dirty, which the one-way
contract permits.

Counts: `1` reset, `2^n - 1` source calls, `2^n - 1` readouts, hence

    Q(n) = 2^(n+1) - 1.

At `n = 5` this is `1 + 31 + 31 = 63`. `verify.py` replays this schedule for
`n = 1..8` in a free symbol model and checks the three literal counts.

## 4. Lower bound

Let a legal schedule use `r` reset calls, `T` source calls and `R` readouts, so
`Q = r + T + R`. Since `Z` sets `z := 0` and no operation recreates `z_0`, the
coefficient of `z_0` in the connector is `1` before the first reset and `0`
after it. Call a readout *clean* when that coefficient is `0`. Let `S` be the
set of distinct nonzero clean single-readout values.

*Clean values are prefixes.* A clean readout sees `sum_{j in q} b_j` for a
prefix set `q` reached after the last reset. A walk of `T` steps visits at most
`T + 1` vertices including `0`, so `|S| <= T`.

*Every mask needs a readout.* Row `i` ends as a sum of the values it read; with
no readout it cannot change, so `R >= 2^n - 1`.

*Masks outside `S` need two readouts.* A readout with the `z_0` coefficient `1`
leaves `A_i z_0` in row `i`, which the generic requirement forbids (row `i`
must not depend on the dirty connector content). So a single readout realizes
a mask only when it is clean and equals that mask, i.e. only for masks in `S`.
Hence

    R >= (2^n - 1) + #{ m != 0 : m not in S } >= 2(2^n - 1) - |S|
      >= 2(2^n - 1) - T.

**Case `r >= 1`.** `Q = r + T + R >= 1 + T + 2(2^n - 1) - T = 2^(n+1) - 1`.
The `T` cancels: a longer walk buys no discount, because every extra prefix
value is paid for by one extra source call.

**Case `r = 0`.** There is no clean readout, so (P1)'s parity argument gives an
even number of readouts per active row, hence `R >= 2(2^n - 1)`. Also `T >= 1`
for every `n >= 1`, since a nonzero mask needs two distinct prefix values that
differ by it. Therefore `Q >= 2^(n+1) - 1`. Equality needs `T = 1` and exactly
two readouts per mask; for `n >= 2` one source call cannot supply the
`2^n - 1 >= 3` distinct masks, so the inequality is strict.

Combining both cases with Section 3:

    exact optimum = 2^(n+1) - 1   for every n >= 1,

attained by the Gray schedule. `verify.py` recomputes this optimum completely
for `n = 2, 3` by enumerating every visited vertex set, its shortest walk and
its cheapest readout assignment, and obtains `7` and `15`.

## 5. What restoration costs

The two contracts differ only in whether `z` must be restored, and in the one
reset call. Their exact values are:

| sources `n` | restored, cited | one-way, this package | saving |
|---|---:|---:|---:|
| 4 | 38 = 8 + 30 | 31 | 7 |
| 5 | 74 = 12 + 62 | 63 | 11 |

In both rows the saving is exactly `T(n) - 1`: the restored minimum source-call
count minus the single reset. The `2(2^n - 1)` readout term is identical. So
the restoration requirement costs the *pairing* structure, not a readout per
mask: a naive comparison would predict a saving of `2^n - 1` (31 at five
sources), and the exact answer is `T(n) - 1` (11), because the pairing contract
can only afford a 12-call walk while single readouts need a 31-vertex walk.

For general `n` the same comparison gives a lower bound of `2n - 1` on the
saving, since (P1) forces `T(n) >= 2n`.

## 6. The reset is essential at five sources

Dropping restoration but keeping the reset forbidden is not enough to reach 63.
Without a reset every readout is dirty, so every row needs an even read count
and `R >= 62`; a row with mask `m` then needs two visited prefixes differing by
`m`. A walk of `T` steps supplies at most `T + 1` vertices, and `|P| = 8` gives
`C(8,2) = 28 < 31` pairs, so `|P| >= 9`.

If `|P| = 9` the walk has at least 8 steps, and exactly 8 makes it a simple
path. `verify.py` enumerates **all 70,846 simple 8-step paths from `0` in the
5-cube** and finds maximum pairwise-difference coverage **28 of 32**; the
predecessor's closed ten-call census reaches 31 with eleven vertices, which is
outside this family. Hence `T >= 9`, and every reset-free five-source schedule
costs at least `9 + 62 = 71 > 63`.

## 7. Scope

This is a scoped exact result in the abstract query alphabet at unit prices. It
is not a `kappa` improvement, not a supplier admission, and not a claim about
physical arity-four or arity-five source operators, nonuniform per-port
tariffs, routing, or word-dependent storage. It does not assert that a caller
can freely discard a shared connector: that is the changed premise, charged as
one reset query, and a caller needing the old value pays a separate save and
restore. The 74 and 38 values and the `T(5) = 12`, `T(4) = 8` counts are cited
from the predecessor, not recomputed here.
