# Restored target basis for the selected JP8 compensation

This is a finite local circuit construction over the rationals, which therefore
also holds over the complex numbers. It supplies no new recurrence exponent.
The exact selected source and the executable recipe are pinned in SOURCES.json
and RECIPE.json. Subscripts below name the canonical register numbers.

## Boundary identity

Immediately after the unchanged zero-frame precondition, let `y` be the 112
target registers and `h` the 492 helper registers. Both may be arbitrary and
correlated. The original compensation implements

    (y, h) -> (y + C h, h).

The source, precondition and subsequent native word are fixed. Every nonzero
column of C belongs to a cold helper with start frame zero and full final
frame. In particular, compensation does not read an entering or cold-ended
helper before its wrapper. This restriction is checked from the actual word.

For each recipe pair `(t,d,q)`, with t and d distinct targets, put
`E = e_t e_d^T`. Then `E^2 = 0`, so `T = I - q E` has inverse `I + q E`.
Execute the following three operations on the **whole** boundary:

1. Prepare `y <- T y`, paying `y_t -= q y_d`.
2. Accumulate `y <- y + (T C) h`. Only row t changes: `C_t - q C_d`.
3. Restore `y <- T^-1 y`, paying `y_t += q y_d`.

The result is `T^-1(T y + T C h) = y + C h`. No zero-target or clean-helper
assumption occurs. Helpers are only read, never written. All source data
registers are untouched by this replacement.

The 56 recipe pairs are disjoint: each of the 112 targets appears exactly
once. Their elementary matrices have pairwise zero products, so all preparations
commute, all restorations commute, and each modified row uses its **original**
donor row. This justifies the shipped schedule: 56 preparations, all transformed
compensation rows in canonical target/source order, then 56 restorations. It
does not justify applying that schedule to overlapping pairs; the verifier
rejects such recipes.

Every target starts at frame zero. Added gates touch only two targets at that
same frame; the remaining helper reads use the existing unwrapped cold sources.
Thus no extra frame change, child, helper, wrapper or center is required. The
entire replacement ends before the existing entry adapters. This endpoint
identity consequently composes with all subsequent gates and wrappers.

The repository's backward program replaces each scalar gate by its inverse
transpose in the same chronological order. The operation `M -> M^-T` preserves
products; hence equal forward boundary operators give equal backward boundary
operators. The executable package checks both boundaries and both complete
programs as additional finite evidence.

## Complete scalar price

For a reduced nonzero dyadic addition coefficient `a / 2^b`, the inherited
binary-Horner implementation costs, for each real component,

    3 + floor(log2(abs(a))) + popcount(abs(a)) + b.

The three fixed operations are the initial private-work clear, signed target
accumulation and final private-work clear. The other terms pay every doubling,
source accumulation and halving needed to prepare the coefficient. There are
two real components. The source reads and private erasure are therefore included;
this is not a count of unit-cost arbitrary rational multiplications.

For a pair, its exactly scored saving is

    price(C_t) - price(C_t - q C_d) - 2 price(q).

The donor's original accumulation is retained. Both basis changes are charged.
All nominated q equal +1, so the 112 basis gates themselves cost **896 real
primitives**. The transformed matrix contains 4,484 nonzero entries, and the
complete replacement contains **4,596 additions**. Its price is 51,872 real
primitives versus 100,272 originally: a saving of **48,400**. The executable
primitive test checks the complete target/source/work map for both signs,
non-unit numerators and dyadic denominators. A cancelling pair is accepted as
an identity but still charged 16 real primitives.

In the emitted full program the macro count falls from 22,693 to 18,489.
Forward scalar primitives fall from 257,232 to 208,832; backward primitives
fall from 257,280 to 208,880. These are scalar instruction prices, not wall-clock
measurements. Existing adapters and recursive calls retain their own costs.

The unchanged local child profile is

    {1:2512, 2:400, 3:448, 4:160, 5:70, 6:8, 8:8}.

Thus the recursive part `sum_r H_r * child_cost(r)` and every non-scalar event
are identical. Only the paid local scalar term changes. No stronger kappa can
be inferred from this count: the inherited asymptotic moment is unchanged, and
no changed global invoice or outer assembly is submitted.

## Precision and verification boundary

The inherited positive-prefix calculation includes coefficient-work growth.
The forward bound remains exactly

    4536094588619580433782972610869617 / 281474976710656.

The backward bound increases from

    16753412757380464429924108070201913461 / 8388608

to

    16831962624931826245647201899142257011 / 8388608.

Both use the same 64 / 101 bit upper bounds and remain below the inherited
192-bit local allowance. There is no prefix-domination claim in the backward
direction and no claim to reuse the old global finite invoice unchanged.

The package performs full boundary replay, a separately written integer-matrix
replay of both original and changed scalar programs, and the pinned unmodified
native emitter and frame/wrapper auditor on the changed word. All 716 source,
target and helper input columns are covered, including all 492 dirty helpers.
Private centers are cleared; coefficient-work clearing uses the inherited
Horner implementation, with the focused symbolic primitive check as a control.
The ten local rejection controls and 25 native controls are listed in EXPECTED.

This is exact finite linear algebra and a written substitution proof, not a
proof-assistant formalization of integer multiplication. All-size compilation,
common-label/mutable-basis realization, physical and pooled hosting, residual
interfaces, uniform precision/tape/recovery and analytic transfer remain
inherited assumptions. Production integration would need a typed construction
step accepting the alternative compensation circuit and fresh source bindings,
hosting/invoice and assembly admission. The raw constructor's compensation
generator is not modified by this package.
