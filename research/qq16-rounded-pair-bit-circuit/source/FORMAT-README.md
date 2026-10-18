# A finite dyadic register bound for the zero-retention QQ16 word

The nearest-even block-scale implementation in [PR2771](https://github.com/CrocSwap/integer-mult-bounds/pull/2771)
uses exact rational arithmetic and leaves finite formats open. For its fixed
3,823-event decoder, this package proves the sufficient common grid

```
t = b + 22
s = ceil_log2(lambda) + floor(h*lambda/2)
k = t + s
Qmax = Q0 + 3*k + 6
W = Qmax + E + 20 signed bits per real component.
```

Here `h, lambda >= 1`, `b, Q0, E >= 0` are integers. There are
`D=2^(h*lambda)` complex payload coordinates per owner. Each supplied current
X/Y array has maximum-per-owner payload Hilbert norm at most `B>0`, with
`B<=2^E`, and every input component belongs to `2^-Q0 Z`. Owned fields are
exclusive and may contain arbitrary representable dirt before their first
CLEAR. The 224 borrowed arrays are never written.

The written argument below, the exact 3,816-cut grid certificate and the
checked integer reference establish a finite arithmetic format for this direct
implementation. Exact quarter ADDs, maps and owned CLEARs have zero defect.
The signed lines have the predecessor's completed relative defect at most
`2^(-b-22)` on their actual operands. Inheriting PR2736's error theorem gives
strict all-cut error `< B*2^-b`. No favorable recursive price, complete physical
caller, precision minimum, supplier admission or new kappa is claimed.

## What this adds and inherits

The consumed source is Nick Petalas's PR2771 at
`e707681c3f6db70d0432501403e2122794a36ade`. Its byte-exact snapshots of ywz65's
PR2707 word and native proof, and Nick Petalas's PR2736 completed-error proof,
are authenticated by [SOURCES.json](SOURCES.json). No predecessor executable
is imported. The native/frame semantics and PR2736's norm constants are inherited;
this package checks the new grid recurrence and its finite arithmetic, rather
than claiming another independent native-semantic audit.

For example, `h=73, lambda=1, b=64, Q0=64, E=0` gives `k=122`,
`Qmax=436` and `W=456`. Simply charging every line and quarter in series
would give the much looser valid bound `Q0+336*k+1792=42848` fractional bits.
The smaller bound comes from the actual dependencies, not a changed decoder
or an observed runtime saving.

Ross Richardson's [floor-grid result](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727#discussioncomment-18957511)
already supplies whole-word direct rounding and finite-capacity estimates.
His [reversible lifting result](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727#discussioncomment-18958062)
addresses a different integer rounding/restoration contract. The present delta
is the source-specific denominator-depth bound for PR2771's relative block
scale, arbitrary declared entry grid and exact quarter ADDs. It does not claim
the first whole-word rounding or finite-range argument. It does not use the
floor implementation or silently transfer its error constants.

## Grid proof

Attach an integer `Qd>=0` to every initialized field, meaning all its
components are in `2^-Qd Z`. Set input and cleared fields to `Q0`. Zero belongs
to every such grid, so this choice for CLEAR is conservative. Preserve Q through
an exact coordinate permutation. For a unit ADD use `max(Qd,Qs)`, and for a
quarter ADD use `max(Qd,Qs+2)`.

For a nonzero actual line operand, let M be its largest absolute real or
imaginary component and `e=floor(log2 M)`. Since the operand is on its declared
grid, `e>=-Qd`. PR2771 rounds every factor to `delta=2^(e-k)`, so the new
components lie on the grid with bound `Qd+k`. A zero block returns zero exactly.
Identity projected directions can be skipped; counting them is conservative.
This reasoning concerns the perturbed operand, not an ideal input.

The [independent grid checker](grid.py) propagates affine rows `Q0+a*k+c`,
retaining all coordinatewise nondominated pairs. Every cut of this exact word
has one surviving pair. The global pair is `(3,6)` for every `k>=0`, including
the caller's `k>=22`. The first occurrence is event 3711,
`Z0 += F0/4`. A maximizing recurrence path has line events 559, 1935 and 2624
and quarter-ADD events 1584, 3317 and 3711. The full cut table and path are in
[RESULT.json](RESULT.json). This is an exact envelope of this conservative
recurrence, not an attained exponent or lower bound on necessary precision.

Now store every field on the single common grid `2^-Qmax`. A quarter source is
divisible by four in these integer units, since its event has
`Qs+2<=Qmax`. For a nonzero line, let m be its largest component magnitude in
common-grid integer units. Its rounding step is `2^d` common units, where

```
d = floor(log2 m) - k.
```

The pre-line invariant `Qd+k<=Qmax` gives `m>=2^k`, so `d>=0`.
No line needs a fraction of the common grid and no data-dependent field exponent
must be stored. The scan computes d once for the complete owner-local line.
A norm bound alone would not bound PR2771's adaptive exponent e: the inputs
`2^-j` have bounded norm and arbitrarily negative e. The entry-grid assumption
is explicit here; it is not a claim that norm-only absolute approximation is
impossible.

## Integer operations and overflow proof

For each pair of complex common-grid integers a,b, form

```
sr = ar+br; si = ai+bi; dr = ar-br; di = ai-bi
raw = (sr-sign*di, si+sign*dr, sr+sign*di, si-sign*dr)
output_component = round_even(raw_component / 2^(d+1)) * 2^d.
```

Both old values are read before either is overwritten. The two outputs are
exactly PR2771's rounded signed pair. The integer implementation uses signed
Euclidean quotient/remainder for nearest-even rounding, including negative
ties. It compares the remainder with `divisor-remainder` to avoid doubling a
large remainder. A quarter ADD divides its source exactly before adding; it
does not multiply its destination by four. CLEAR writes zero and never reads
the old dirt. Exact native wrappers and full-cover maps only permute stored
components, with no re-rounding. Their routing and address costs remain paid.

First define these operations over unlimited mathematical integers. PR2771's
unitary factor argument gives, for every internal completed factor, defect
at most `lambda*sqrt(D/2)*delta <= 2^-t * ||input||`. Exact ADDs/maps/CLEARs
and this line contract satisfy PR2736's relative premises. Its inherited
all-cut bound therefore gives

```
error <= B*2919388*u/(1-199144*u) < B*2^-b, u=2^(-b-22)
initialized completed-field norm < 32369*B < 2^(E+15).
```

This use of the unlimited reference prevents circular reasoning about overflow.
Within a line, every completed factor norm is at most
`(1+2^-t)` times its actual line-entry norm, hence less than `2^(E+16)`.
Each component in common-grid units is consequently smaller than
`2^(Qmax+E+16)` in absolute value. The pair's two-component sums and four-term
numerators are smaller than `2^(Qmax+E+18)`. Rounding divisors, quotients,
remainders, shifted outputs and exact ADD intermediates also fit within the
signed range of `W=Qmax+E+20` bits. The scan's absolute value fits with this
margin; the most negative signed integer is never a live initialized operand.
Uninitialized owned dirt is cleared without arithmetic. This proves that the
bounded implementation simulates the unlimited reference with no overflow or
underflow under the stated premises. W is sufficient, not optimal.

The shift counter is bounded by W and needs `ceil_log2(W+1)` unsigned bits.
Payload/owner address counters are separate. This is an arithmetic-register
bound under exact finite coordinate permutations, not a priced physical memory
or tape implementation. All dimensions and counter sizes are parameters; the
written proof applies to every positive finite h and lambda.

## Charges and family decision

This direct line implementation retains PR2771's scan of `2D` real components,
`4*lambda*D` real ADD/subtracts and `2*lambda*D` component rounding operations,
per owner per nontrivial line. There are 336 billed line occurrences, so upper
bounds are `1344*lambda*N*D` real ADD/subtracts and `672*lambda*N*D` rounding
operations across N owners. The 2,704 scalar ADD events add `5408*N*D` real
ADD/subtracts, with `1792*N*D` exact component quarter divisions. The 312 CLEARs
and 464 full-cover maps remain explicit. Scans, bit shifts, division, address
arithmetic, wrappers and movement are additional work. No original recursive
rank-one charge is attached to these direct loops.

There are 224 borrowed fields, 224 eventual output fields and at most sixteen
private fields. Arithmetic representation uses at most `2*464*N*D*W` data bits
for those fields, plus pair/scan scratch and separately paid permutation and
address workspace. This count is not a complete machine-storage bound.
Owned CLEAR is destructive, not reversible uncomputation of arbitrary dirt.
No exact reversal of the rounded decoder is claimed.

Revision-5 decision: narrow and stop at this finite-register lemma. The ideal
native identities and entry/F0/B1 error remain inherited or open, and the
physical routing, recursive child implementation, bit complexity, tape/control
and consumer bills are still unknown. Unknown costs are not zero; a finite
format alone does not justify supplier expansion.

## Reproduce and verification limits

From the repository root, use standard-library Python 3.12:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/qq16-finite-dyadic-format
```

Direct read-only replay also works in a Git-free export:

```sh
python3.12 -Werror -I -O -B research/qq16-finite-dyadic-format/verify.py
```

The checker authenticates the source bytes before numerical work. Exact affine
propagation covers every changed-field cut; a separately implemented scalar
recurrence checks 108 parameter tuples and 412,128 cut values. Six source/model
controls reject omitted events, borrowed writes, dirty reads and missing line
or quarter charges. Fifty-four integer line cases agree with a separate
Gaussian-rational oracle and have nonzero rounding errors. Twelve complete-word
small-payload fixtures check all cuts, exact quarter divisions and register
ranges; six use fine entry grids and have nonzero errors. Their deliberately
chosen noncommuting coordinate permutations exercise the isometry contract;
they do not implement or recertify the actual cover's native semantics.
Four arithmetic controls reject overflow, an overflowing pair, an insufficient
common grid and an inexact quarter. Artifact tests cover exported replay and
source/receipt corruption. No formal-kernel, physical-machine, selected cold
replay or independent human review is claimed.

Power-of-Ten scope: all new functions are bounded, validation stays active
under optimized Python, and no recursion or predecessor executable is used.
Rule 3 deviation: Python integers, Fractions and collections allocate during
this verification. Input files are capped at 400,000 bytes, the word at 3,823
events, live fields at 464, frontier size at 337, numeric fixtures at 1,024
coordinates and signed fixture registers at 8,192 bits. The recorded fixtures
are much smaller. These bounds constrain the checker, not the quantified
mathematical dimensions. A production fixed-allocation machine needs its own
implementation and budget; this verifier is not that machine. Rule 10 limits:
Python warning/compilation checks and available static diagnostics are run;
there is no static type checker or hardware integer build in this package.
The deterministic package-local grid import is explicit and works under `-I`.

## Open next questions

Can a recursively cheap native implementation meet the same relative contract
and finite range? Expose one child's actual integer operations and compare its
complete bit/movement invoice with these direct loops. The missing recursively
admitted implementation blocks that transfer.

Can an actual caller supply the stated entry norm and dyadic grid while
paying for its full physical schedule and consumer? Pin its post-B1 encoding
and propagate its range/error into B,E,Q0 before combining budgets. This
package does not establish that entry contract or a favorable total moment.
Structured questions and exact freshness records are in [TASK.json](TASK.json).

## Credit

New grid-depth argument and checked finite-format reference by Nick Petalas.
Credit ywz65's PR2707 and PR2540, Arham Tahir's PR2681, Ali Romman and the
retained QQ16/native/geometry lineage. Nick Petalas's PR2771/2736 supply the
inherited rounding and error arguments. Ross Richardson's linked public
floor-grid and lifting artifacts retain their prior rounding and range credit.
Source proofs retain their byte-exact notices. New material is Apache-2.0.
