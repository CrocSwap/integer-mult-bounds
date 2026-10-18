# Restored dirty borrowing cannot recover the cheap boundary invoice

This is a scoped, computer-assisted lower bound for exact scalar circuits.
It is not a formal verification of the multiplication theorem.

## Model and result

Each register initially contains an arbitrary, independently variable real
number. A specified permutation acts on `m` moved registers; any finite number
of other registers may be borrowed, but every one must finish with exactly its
own incoming value. There is no known-zero or disposable register. All prefixes
may contain arbitrary dyadic linear combinations. One paid primitive is:

- `x_t += x_s` or `x_t -= x_s`, with distinct registers;
- `x_t = -x_t`, `x_t = 2*x_t`, or `x_t = x_t/2`;
- `COPY x_t <- x_s` or `CLEAR x_t`.

There are no free signs, permutations, renamings, reads or restoration steps.
Non-unit macros must expand into these paid primitives. Self-COPY is an identity
and can be deleted. The class is one real component; joint real/imaginary
synthesis or nonlinear operations are not priced by this model.

**Result.** Even with arbitrarily many restored dirty borrowed coordinates,
the minimum costs are 4 for a two-cycle, 6 for a three-cycle, and between 9 and
10 inclusive for a disjoint two-plus-three-cycle. In particular, borrowing
preserved coordinates cannot attain the disposable-scratch prices 5 and 8 for
the last two cases. This generalizes PR1145's moved-coordinates-only result;
it is not another search in that closed register model.

## Reduction from unbounded dirty storage to at most one written donor

The required full map, including all borrowed coordinates, is invertible.
A distinct-register COPY or CLEAR is singular. Subsequent linear operations
cannot recover lost rank. Therefore a successful circuit contains neither.
All remaining prefix matrices are invertible, so every current register row
is nonzero. This argument fails for a known-zero or disposable coordinate;
that distinction is essential.

Call a primitive a **write** to its target coordinate. Every moved coordinate
must be written at least once, since reads do not change its own initial row.
Every restored borrowed coordinate that is written must be written at least
twice. To see the latter, suppose it is written exactly once. Before that write
its row is still its initial basis vector `e_j`. A scale by `-1`, `2` or `1/2`
changes it. An ADD/SUB changes it by a nonzero source row, because the entire
prefix is invertible. No later operation changes that row. Its final value
cannot be `e_j`, contradicting restoration.

Consequently a word of length `L` moving `m` coordinates writes to at most

```
k <= floor((L - m)/2)
```

borrowed coordinates. This is a lower count of writes, not a claim that these
writes alone suffice to implement the permutation.

There may still be arbitrarily many borrowed coordinates that are **read but
never written**. Set their independent input values to zero. The circuit's
universal endpoint identity must continue to hold on this specialization.
These coordinates now stay identically zero throughout. Delete every ADD/SUB
that reads one of them, and then delete the unused coordinates. Induction over
the literal word shows that every remaining register has exactly the same
value at every retained prefix. The result is a valid word of no greater length
on the moved coordinates and at most `k` written donors. No assumption about
bounded magnitudes or coefficient depth is needed. This is an existence
reduction for a lower bound, not permission to initialize actual dirty data
for free in a construction.

The three excluded budgets therefore reduce as follows:

| Target | Excluded length L | m | Maximum written donors | Finite dimension used |
|---|---:|---:|---:|---:|
| `(01)` | 3 | 2 | 0 | 3 (one extra idle donor is harmless) |
| `(012)` | 5 | 3 | 1 | 4 |
| `(01)(234)` | 8 | 5 | 1 | 6 |

A reduced circuit using fewer coordinates embeds into the listed dimension
by leaving the extra coordinate idle. Thus exclusion in these finite dimensions
proves the stated lower bounds for *every finite number* of dirty donors.
This is the mathematical argument connecting the finite calculation to the
unbounded donor statement; finite replay alone would not do that.

At length nine for the last target, two donors can be written. The present
six-coordinate certificate does not exclude that case. We make no claim to
resolve nine versus ten or an arbitrary longer-word stabilization theorem.

## Exact finite quotient and complete coverage

The ring homomorphism `Z[1/2] -> F_3` sends `a/2^r` to `a*2^r mod 3`.
ADD/SUB map to elementary row additions; NEGATE, DOUBLE and HALVE all map to
row negation. The resulting inverse-closed generating set has `n(2n-1)` gates.
Every exact length-L word reduces to a modular word of at most that length.
Modular **nonexistence** is therefore a sound lower bound. Modular existence
is not used as an exact upper witness. F_2 cannot support this argument because
2 is not invertible there; the tests enforce this control.

Both implementations compute the complete breadth-first radius-four ball B
around identity. Let P have row i equal to `e_{p[i]}`. There is a word of length
at most eight for P exactly when some A in B also has `A P` in B. Indeed split
`P = U V` with each factor of length at most four, and take `A = U^-1`.
Conversely `P = A^-1 (A P)` constructs such a word. Minimum distances in B give
the exact minimum through length eight by minimizing `d(A)+d(A P)`.

| Dimension and permutation (last coordinate fixed) | Layers 0 through 4 | Minimum through 8 |
|---|---|---:|
| 3, `(01)(2)` | 1, 15, 135, 787, 3000 | 4 |
| 4, `(012)(3)` | 1, 28, 486, 6272, 62885 | 6 |
| 6, `(01)(234)(5)` | 1, 66, 2655, 83270, 2213925 | no intersection |

Exactly **2,373,527 states** are enumerated, with no sampling, pruning, timeout
or unverified cached solver result. Python represents rows as ternary integers
and uses exact row tables. C++ computes coefficients directly in a two-bit
encoding with a 128-bit working key: the 6x6 state needs 72 bits. Canonical
ternary matrices fit in uint64 since `3^36 < 2^64`. Every sorted matrix and
minimum distance is compared byte for byte, not merely by counts or hashes.
The recorded hashes summarize that full comparison.

The two implementations are adaptations of PR1145's separately represented
checkers, with source pins and attribution retained. They do not read each
other's tables or intermediate results. Both are AI-assisted; this is not a
claim of independent human review. A further dense-matrix oracle checks small
balls and direct pair products, including high donor-coordinate operations.

## Exact upper witnesses and contract controls

The following words use only the moved coordinates, so all donors are restored
by remaining untouched. Every independent input column and each literal inverse
is checked over Fraction arithmetic.

```
# (x,y) -> (y,x), four primitives
x += y; y -= x; x += y; y = -y

# (x,y,z) -> (y,z,x), six primitives
z -= y; x -= z; y += z; z += x; x -= z; x += y
```

Their direct sum gives ten for the disjoint target. Taking any number of unused
donor coordinates extends these exact witnesses without extra cost.

With a *disposable* incoming workspace w, saving one coordinate of each cycle,
rotating by COPY, and finally clearing w costs 4, 5 or 8. The resulting data
permutation is correct but the incoming w column is destroyed. The verifier
explicitly demonstrates that a data-only check accepts these circuits while
the restored-donor contract rejects them. All 37 single-gate omissions in the
six restored/disposable witnesses are detected. Additional tests demonstrate
the read-only zero-specialization reduction and catch its illicit application
without specializing the dirty input.

## Application and complete favorable price

The actual predecessor is **ToikY's PR969**, at
`d1ee3f46a6167ea54913e070af3161c71a99e1f2`, retained in
`research/complex-swap-runs-seed37/`. PR1145's narrative mistakenly called this
PR971; PR971 is a different decoder-audit contribution. This package binds the
correct PR and retained bytes and does not alter either frozen package.

The inherited exact boundary recognizer is replayed on all four frozen CK/JP8
orientations. All 168 event intervals, frame labels, swap positions, complete
permutations and cycle decompositions match the retained PR969 receipt. Each
orientation has 28 two-cycles and 14 disjoint two-plus-three-cycles. Conjugating
coordinate labels preserves the operation alphabet and price; reversing cycle
direction has the same cost by inverse closure.

If each boundary must realize its arbitrary-input permutation while restoring
all borrowed state, its per-component bill is at least

```
28*4 + 14*9 = 238,
```

versus `28*4 + 14*8 = 224` with the existing disposable coefficient work. The
explicit upper witnesses cost 252. Separate real and imaginary lowering thus
incurs at least **28 additional real primitives per orientation**. The lower
bound generously ignores geometry restrictions on donors: charging any needed
frame or source transport cannot create a cheaper circuit in this relaxation.
No copy, source access, helper initialization or restoration is silently free.

This is a failed mechanism under a specified exact interface, not a search
failure, a new supplier or a kappa improvement. Other operations still need
coefficient work. No whole supplier row is eliminated, no paid recursive child
profile is changed, and no native/phase/hosting/invoice/outer assembly replay is
claimed. Joint optimization with neighboring scalar runs, different input
promises, disposable or clean workspace, alternative primitives and joint
complex-component synthesis remain outside this result. Inherited precision,
tape, realization, all-size and analytic assumptions remain open.
