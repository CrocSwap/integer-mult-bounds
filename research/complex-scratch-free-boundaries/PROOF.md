# Scratch-free permutation boundaries with mixed intermediate rows

This is a scoped computer-assisted negative result about exact scalar circuits,
not a formal proof of the integer-multiplication theorem.

## Exact interface and price

There are exactly `n` available registers containing arbitrary independent
real inputs. The required map is a specified permutation of these inputs.
One primitive costs one, with the PR696 real-component alphabet:

- `x_t += x_s` or `x_t -= x_s`, with distinct registers;
- `x_t = -x_t`, `x_t = 2*x_t`, or `x_t = x_t/2`;
- `COPY x_t <- x_s` or `CLEAR x_t`.

No other register may be read, written, borrowed or supplied with a known value.
Intermediate rows may be arbitrary dyadic combinations; there is no monomial,
coefficient-height, denominator-depth or prefix-magnitude restriction. There
are no free permutations, renamings or sign changes. Each source access in an
ADD/SUB is part of that charged primitive. Non-unit coefficient macros must
be expanded into their paid primitives. The class is a single real-component
circuit; it excludes cross-component complex arithmetic and nonlinear gates.

COPY between distinct registers and CLEAR have singular matrices. Rank cannot
increase under subsequent linear maps on the same `n` registers. Therefore
neither can occur in a successful circuit whose endpoint is an invertible
permutation. A self-COPY is an identity and can simply be removed. This leaves
only invertible ADD, SUB, NEGATE, DOUBLE and HALVE.

## Sound finite quotient

The ring homomorphism `Z[1/2] -> F_3` sends `a/2^k` to `a*2^k mod 3`, because
`2^{-1}=2` in `F_3`. ADD and SUB reduce to their corresponding elementary row
operations. NEGATE, DOUBLE and HALVE all reduce to row negation. Thus every
successful exact circuit of length at most `L` gives a word of length at most
`L` in the following inverse-closed generating set of `GL(n,3)`:

```
row[t] += row[s], row[t] -= row[s]     (t != s)
row[t] = -row[t]
```

There are `n(2n-1)` generators. Passing to the quotient can make a circuit
shorter or identify different exact matrices. Consequently modular
**nonexistence** is a lower bound for exact circuits; modular existence is
never used alone as an exact upper bound. The exact upper bounds below are
separately executed over rational numbers. Reduction modulo two would be
unsound for HALVE and is explicitly rejected by a control.

## Complete short-word certificate

Both implementations generate the entire radius-four ball `B` about identity
by breadth-first search, retaining minimum distances. Let `P` be the target
permutation matrix, with row `i` equal to `e_{p[i]}`. A word of length at most
eight exists if and only if there is `A` in `B` with `A P` also in `B`.

For the forward implication, split a length-at-most-eight word into two
subwords of length at most four: `P = U V`; put `A = U^{-1}`. Inverse closure
gives `A in B`, and `A P = V in B`. Conversely `P = A^{-1}(A P)` is a word
of length `dist(A)+dist(A P) <= 8`. Minimizing that sum over intersections
also yields the actual minimum whenever it is at most eight.

| Dimension / target | Radius-four layer counts | Minimum through length eight |
|---|---|---|
| 2 / `(01)` | 1, 6, 17, 22, 2 | 4 |
| 3 / `(012)` | 1, 15, 135, 787, 3000 | 6 |
| 5 / `(01)(234)` | 1, 45, 1250, 26830, 477045 | no intersection |

There are 509,157 states across the three balls. Python represents each row
as a base-three integer and uses row lookup tables; a separate C++ program
stores two bits per coefficient and computes every row operation directly.
They use different generator orders. Every state and every minimum distance
is compared exactly in a canonical binary encoding, not merely by counts or
hashes. The hashes in EXPECTED.json summarize this full comparison.

This exhausts the stated short-word domain, without a timeout, random sample,
heuristic pruning, solver status or unverified cached search result.
Assignment seed 24 rotates the generator presentation only. Search class
novelty comes from allowing mixed intermediate rows while removing scratch,
not from that seed. The independent implementation is also AI-written; no
independent human review is claimed.

## Upper bounds and remaining one-operation gap

An exact swap uses four primitives:

```
x += y; y -= x; x += y; y = -y
```

An exact three-cycle `(x,y,z) -> (y,z,x)` uses six:

```
z -= y; x -= z; y += z; z += x; x -= z; x += y
```

Taking their direct sum gives ten for the 2+3-cycle. The verifier applies
these literal words to every independent input column and checks their
literal inverses. Therefore the exact scratch-free minima are **4**, **6**,
and **between 9 and 10 inclusive**, respectively. We do not resolve nine
versus ten for the last case. No longer-word search was performed.

With one disposable scratch register, PR971's construction needs `n+c+1`
primitives for `c` cycles: save one coordinate, rotate each cycle by COPY,
then CLEAR scratch once. For the same cases these prices are **4**, **5**,
and **8**. Incoming scratch may be arbitrary; the circuit overwrites and
eventually clears it. The comparison does not assume a free initial clear or
ignore final restoration work. Every operation is executed on all `n+1`
input columns, including arbitrary scratch dirt. All 37 single-primitive
omissions from the six displayed witnesses are detected.

## Actual historical CK/JP8 boundaries

An independently written exact two-coordinate recognizer scans all scalar
runs of both orientations of each frozen PR626 CK and JP8 word. A run ends
at every non-scalar event or frame change. It reconstructs the pending
permutation after all recognized swaps, including the fixed coordinates,
and matches every event interval, frame, swap position, mapping and cycle
against PR971's complete retained receipt. All source bytes are pinned.

Each of the four programs has 28 two-cycle boundaries and 14 boundaries of
type 2+3. Register conjugation preserves the gate alphabet and price, so the
canonical modular exclusions apply to every actual coordinate labeling and
to inverse cycle direction. Some mappings also list a fixed coordinate:
it is **not available as scratch** in this result.

If each boundary must implement its arbitrary-input permutation using exactly
its moved coordinates, the per-component boundary bill is at least

```
28*4 + 14*9 = 238,
```

compared with the retained scratch circuit's `28*4 + 14*8 = 224`. The explicit
scratch-free witnesses cost 252. Doubling for the separate real/imaginary
components gives a penalty of at least **28 real primitives per orientation**.
This favorable comparison charges no extra disposal of a removed scratch
cell; requiring an existing dirty work cell to clear would need further work.

No frame change, copy, source access, restoration or recursive child is silently
saved. We propose no supplier substitution: the bound says that a particular
attempt to eliminate boundary scratch cannot tie the existing boundary bill.
Other scalar operations still use coefficient work, so this result by itself
does not eliminate a row from a complete supplier or change a recurrence.

## Exclusions and inherited obligations

The result does not cover borrowing another fixed coordinate, optimizing the
surrounding run jointly, changing the incoming-state contract, carrying a
permutation across a frame/event barrier, additional scratch, different
primitives, or cross-component arithmetic. It does not prove an optimum for
circuits with scratch. PR1095's monomial-prefix optimum for that different
class is credited as prior work, not reproved or imported here.

Full-word native/phase/wrapper admission, physical arrays and tape, precision,
hosting, all-size compilation and analytic transfer are not executed or
discharged. Exact local witnesses are not a rounded-arithmetic guarantee.
The selected supplier and kappa are unchanged.
