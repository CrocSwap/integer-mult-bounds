# Exact fixed-reader typed-window fusion cost

PR2595's repeated five-child example has a **56-record fusion penalty with
fixed readers**, and a **48-record saving with phase-indexed readers**. This
package proves the exact fusion formula for every finite nonempty pair in
its canonical typed-window model. The independently reconstructed fixed-reader
invoices are 1,616 separate versus 1,672 joint. They agree with PR2595's own
machine receipt, whose joint fixed-reader row is absent from its displayed
pivot table.

The distinction corrects any reading of PR2595's statement that the 48-record
residual is the same in both families as a statement about net cost. Both
families save 48 window records, but fixed readers also incur 104 extra frame
records. The legal per-call k=2 schedules, at 384 literal or 304 typed records,
remain valid in the declared scalar model. This result changes no selected
supplier, recursive histogram or kappa.

Source: [Aaron Wang's PR2595](https://github.com/CrocSwap/integer-mult-bounds/pull/2595)
at `533bb00517ad0e9206ec34d2026a3977a2dc9a16`. Its
[immutable machine receipt](https://github.com/CrocSwap/integer-mult-bounds/blob/533bb00517ad0e9206ec34d2026a3977a2dc9a16/research/z4-typed-window-schedule-seed25ad/RESULT.json)
is retained in `PR2595-RESULT.json`, with its Git blob and SHA256 in
`EXTERNAL-SOURCE.json`. Coordination is in [Discussion2610](https://github.com/CrocSwap/integer-mult-bounds/discussions/2610).
Canonical base is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.

## Model and exact tariff

A word `w` lists the octet read by each child, over `{0,1,2}`. Every child
reads eight work rows into the eight output rows, then advances all three
work octets by the order-four permutation `P`. The child costs 68 scalar
records, using Cinna Davis's PR1391 canonical words.

Between children, each work octet may independently receive a canonical
`P^u` word at cost `c(u)`, with `c=(0,20,16,20)` for `u=0,1,2,3`.
A used octet receives eight COPY and eight ERASE records. COPY may choose
one initial permutation of its source rows. Typed ERASE may remove the
copied content in its exit phase. The source bank stays read-only and
independent of all arbitrary dirty work and output inputs.

A call is exactly `COPY; body; ERASE; inverse(body)`. Count every record
literally, including both directions of the frame corrections and children.
Do not simplify across macro boundaries. This is the predecessor's fixed
macro family, not all possible ADD/NEG programs. The theorem minimizes
primitive count, not travel or descriptor costs among tied schedules.

Let `S(w)` be the used octets and `p[b,1] < ... < p[b,r]` their zero-based
read positions. Define the forward correction bill

```
F(w) = sum_b sum_(j=1)^(r-1) c((p[b,j] - p[b,j+1]) mod 4).
```

Then the exact minimum fixed-reader call cost is

```
L_fixed(w) = 136*len(w) + 16*|S(w)| + 2*F(w).
```

**Proof.** The phase at read position `i` is `i` plus the sum of corrections
before it. The freely chosen COPY permutation absorbs the first read's phase.
Consecutive reads at `p<q` therefore force total intervening correction
`-(q-p) mod 4`. Splitting this correction cannot reduce its tariff. Two
nonzero corrections already cost at least 32, while any single correction
costs at most 20. Zero corrections cost zero. Thus every such interval costs
at least `c((p-q) mod 4)`.

For each octet these intervals are disjoint. Put their one required correction
immediately before the later read. Corrections on different octets are
independent, so all interval minima are attained together. No leading or
trailing correction is necessary. Typed ERASE accepts every exit phase, and
the literal inverse restores the arbitrary initial workspace. Doubling the
forward correction and child bills, then adding the window bill, proves the
formula. This argument applies to every finite word, not only the tested sizes.

For the literal-window positive control, COPY and ERASE are row-aligned.
Add `c(-first_b mod 4) + c((last_b-len(w)) mod 4)` per used octet to `F`.
The same interval argument proves this variant, including the first and last
boundary intervals. The implementation checks both variants against a
separate four-phase dynamic program.

## Exact two-call fusion law

For nonempty words `a,b`, let

```
K(a,b) = sum_(x in S(a) intersection S(b))
           c(-(len(a) + first_b(x) - last_a(x)) mod 4).
```

Only octets used by both calls create a new consecutive-read interval on
concatenation. Hence `F(ab)=F(a)+F(b)+K(a,b)`. The exact saving, measured as
separate minus joint, is

```
L_fixed(a) + L_fixed(b) - L_fixed(ab)
    = 16*|S(a) intersection S(b)| - 2*K(a,b).
```

The first term saves copied and erased rows. The second pays the newly
required cross-boundary alignment in both directions. With phase-indexed
readers, each read retargets the output by the inverse current phase. The
reader then sees its original source coordinates without gap corrections,
so `F=0` and only the first term remains. This is an additional reader
contract, not a property of fixed readers.

For `a=b=(0,1,2,0,1)`, the three cross-boundary distances are `2,2,5`.
Their correction costs are `16,16,20`, so `K=52`, `F(a)=40` and `F(ab)=132`.

| Reader contract | Separate | Joint | Separate minus joint |
|---|---:|---:|---:|
| Fixed | 1,616 | 1,672 | -56 |
| Phase-indexed | 1,456 | 1,408 | 48 |

The fixed-reader differences in the other reported charges are -92 reads,
-5,160 travel row steps and -768 descriptor bits. Storage remains 4,088 cells.
These invoices reproduce the source's exact chosen schedules; primitive
minimality alone does not establish optimality of those other charges.

An even smaller counterexample is `a=b=(0)`. Fixed readers cost 304 separate
and 328 joint, a 24-record penalty despite 16 fewer window records. The
phase-indexed joint costs 288. A window-only lower bound cannot determine
the sign of the complete fusion saving.

## Verification and limits

```
python3.12 -B scripts/research_package.py --package research/typed-window-fusion-audit
```

The registered replay runs the checker, seven behavioral test groups, and
an optimized checker. It needs only the standard library, performs no network
access and writes no artifacts. `verify.py --emit` prints a regenerated
`RESULT.json` to stdout for an explicit comparison.

The source verifier is neither imported nor executed. The acceptance check
uses a separate four-state dynamic program on all 3,279 words of lengths
1 through 7, both typed and literal variants. It checks the fusion identity
on all 14,400 ordered pairs with component lengths 1 through 4. An independent
column interpreter reconstructs seven source invoices, checks every one of
the 56 arbitrary dirty input columns, verifies each legal call boundary and
executes the literal inverse of each complete schedule. Seven test groups
include wrong or missing ERASE, a wrong phase-indexed reader, premature
per-call delivery, a false invoice and malformed or over-capacity inputs.
A separate phase derivation and dynamic program also corroborated the proof.
Substantial AI assistance was used for derivation, implementation, verification
and prose. No independent human or formal-kernel review is claimed.

The written theorem is unbounded in word length. The executable deliberately
accepts at most 64 children per call and 40,000 records per replay. The
64-child boundary and rejection of 65 are checked. Python requires dynamic
allocation, a Power of Ten rule 3 deviation. The fixed 56-column state,
validated child limit and record cap bound its live data and loop work.
The record cap also bounds each exact integer to at most 40,001 bits, since
one allowed ADD can at most double the largest absolute coefficient. A replay
retains 56 by 56 coefficients. Streaming a new column would reduce that bound
if the fixed-width contract ever grows.
Rule 10 uses development mode, warnings as errors and static diagnostics
in validation; the registered commands retain runtime diagnostics. Every
function stays below 60 physical lines; the code has no recursive call path.
The standard-library replay environment does not install Ruff, so static
Ruff checks run locally rather than on each registered replay. The exact
diagnostic command is `uvx ruff check --target-version py312 --line-length 100
--select E,F,B,UP research/typed-window-fusion-audit/verify.py
research/typed-window-fusion-audit/test_verify.py`. Extend the registered
environment if recurring Ruff enforcement becomes a repository requirement.

This is a scalar macro tariff and source-receipt audit. A single joint window
still fails the pinned per-call delivery contract. No native embedding,
physical COPY interface, hosting, precision, all-size compiler, recurrence
or multiplication transfer is admitted. The selected cold supplier replay
was not run because no selected source or artifact changed. PR2500 separately
audits the unsupported inference from typed scalar savings to fewer recursive
children. This package does not redo that result.

## Open next questions

- Can a named native selected child expose the phase-indexed reader at the
  same fully charged cost? This determines whether the 48-record net saving
  can survive a physical embedding. Start by binding one source/sink reader
  and all frame conjugations to emitted records. The current blocker is the
  missing native child and complete-cost correspondence, as in PR2500.
- Can a legal transfer of shared window ownership preserve a saving without
  deferring per-call delivery? The exact formula now supplies the fixed-reader
  alignment charge that such a proposal must pay. Start with the smallest
  shared-octet pair and price COPY, ERASE and frame restoration. The immutable
  sequential-window contract remains a separate blocker.

## Credit

Aaron Wang supplied PR2595's legal window schedules, cost model, fixed and
phase-indexed receipts, and the window-sharing observation, following PR2464.
Cinna Davis supplied PR1391/1410 and the distinct-source phase-indexed family,
following Ross Richardson's PR1287 and Sagar Thakrar's PR1227. Ross Richardson's
PR2500 separates typed scalar savings from recursive-child savings. The
contribution here is the exact all-length fixed-reader fusion law, the
explicit net-cost qualification and a separately implemented replay.
Retained sources and canonical cycle words keep their predecessor credit.
New material is Apache-2.0. See `NOTICE.md`.
