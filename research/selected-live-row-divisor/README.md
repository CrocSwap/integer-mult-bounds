# Exact compatibility of live-row and physical-slot reserves

This is an independently checked **corollary of Jose Manuel's PR2195/PR2234
live/work separation**, with an explicit row codec and a written all-depth
proof. It is not a new separation mechanism or an unconditional supplier.
PR2195 already calls its least-common-multiple layout an overreserve.

For the same fixed complete live-packet format, replace the sufficient divisor

```
K_lcm = lcm(28416,28425) * |GL64(F_q)| * q^(4096(w-1))
```

by

```
B = 28416 * |GL64(F_q)| * q^(4096(w-1)).
```

At coarse depth D, the reserve changes from `K_lcm^D` to `B^D`, a factor
`9475^D`. This is a row-divisibility reduction. **All private/selector work,
COPY/ERASE operations, occupied volume and parking charges remain required.**
The nine physical work slots are not turned into live input or deleted.
The per-volume paid profile, selected invoice and kappa are unchanged.

The new format need not satisfy a consumer's old P-based divisor. The exact
acceptance gate is `9475^D | t` for incoming live-format stock `t B^D`.
Consequently **the old reserve remains minimal when both fixed formats are
required**. Using the smaller reserve requires a caller admitting the complete
live-packet contract below. The
literal historical `row_layout` test still asserts the old constants and is
retained unchanged. This package does not substitute its codec into a complete
selected recursive machine.

## Source binding and exact delta

Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
Selected record SHA256:
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

- [PR2195](https://github.com/CrocSwap/integer-mult-bounds/pull/2195), head
  `3a1cf78a1ba6322129e42d80c50d21765524d612`, PROOF section 5 and
  `owner_packets.py:151`: `W=28416`, `P=W+9=28425`, private work outside the
  row split, packet volume `V/(WN)`, and the old surplus quotient `9475`.
- [PR2234](https://github.com/CrocSwap/integer-mult-bounds/pull/2234), head
  `d047ef86fbc5b1614d3d8e2b8d3441413beab73f`, PROOF sections 5-8:
  recursive complete-row contract, four work buffers, depth and parking bill.
  `recursive_plan.py` is retained as inert evidence of the macroplan boundary.

The six copied files and their Git blobs/SHA256s are in `PREDECESSORS.json`.
The primary checker authenticates its manifest and every byte before use;
it never imports or executes predecessor code. The source audit covers these
named files, not every linked implementation. Source2195 explicitly retained
P-divisibility as compatibility, without identifying P-slot input with scratch.
Our delta is the replacement codec, its exact full-depth implication, controls,
and independent review of the resulting interface boundary.

PR2084/2120 supplied conditional parent-stock coefficients; PR2324/2343 supplied
cutoffs for their stipulated reserves. Their results are neither recomputed nor
changed. This package does not identify new selected fourteen-stage constants.

## Conditional full-depth theorem

For integers `W,N,H>=1`, set `B=WNH`. A complete live packet has coordinate
range `[W] x [N] x [H]`; `[a]` means the integers from 0 through a-1.
Fix an integer maximum active depth `D>=0` and multiplicity `t>=1`.
Assume the following contracts, independently of a P-based row format:

1. A parent can interpret the fixed source word on `[W] x [N] x [H] x [U]`
   for every positive integer U. All original rows carry arbitrary live payload.
   Private, source, target and route copies are additional paid work. No
   arbitrary live coordinate is cleared to supply that work.
2. Routes and descriptors preserve unused U and exposed ancestors. A child's
   existence, requested width and coefficients may depend on ancestors but do
   not select or inspect its fresh row fields. Each child receives its complete
   fresh range at every fixed ancestor value, including every parent high value.
3. A child with depth bound `D'<=D-1` restores its row and complete spectators
   pointwise, closes its local work and returns its heads. Leaves accept every
   positive integer row multiplicity; width zero is identity. The source's
   chronological, endpoint, parking and uniform primitive contracts are retained.

Then `t B^D` rows are sufficient for the entire depth-D live-row construction.
The row codec is a bijection

```
[t B^D]  <->  ([W] x [N] x [H])^D x [t].
```

**Proof.** At D=0 the row range is `[t]` and no packet is exposed. At D>=1,
ordinary Euclidean division gives

```
[t B^D] <-> [W] x [N] x [H] x [t B^(D-1)].
```

For every fixed family, low class and high value, the last coordinate is the
same complete range. For a child of depth D', it equals
`[t' B^D']`, with `t'=t B^(D-1-D')` a positive integer. Apply the induction
hypothesis to that child. It restores the row and all exposed fields, so the
next sibling reuses the same range; reserves do not multiply across sequential
calls. Inverse decoding restores the parent's row exactly. Iterating division
gives the displayed codec. Constant-weight descriptor resets do not reset the
consumed row depth or discard an exposed field. This proves the conditional
all-depth implication. It does not establish the physical premises.

**Fixed-format minimum.** A range that is the product of D complete independent
W,N,H layers and a nonempty integer leftover has cardinality `t B^D`. Hence
`B^D` is its least positive cardinality. This is only a minimum in the stated
product format. It is not a lower bound for adaptive, correlated, variable-depth
or otherwise changed row encodings, nor for arbitrary reversible algorithms.

**Exact two-format gate.** For any additional integer `P>=1`,

```
(PNH)^D | t(WNH)^D  <=>  (P/gcd(P,W))^D | t.
```

Cancel `(NH)^D`, write `P=ga`, `W=gb` with `g=gcd(P,W)` and coprime a,b,
and cancel `g^D`. The question is `a^D | t b^D`; Euclid's lemma makes this
equivalent to `a^D | t`. At D=0 both sides hold for every positive t.
Since every live-format cardinality is `t B^D`, its smallest positive value
also accepted by the fixed physical format is

```
lcm((WNH)^D,(PNH)^D) = (lcm(W,P)NH)^D = K_lcm^D.
```

For the selected constants, `g=3`, `a=9475`, `b=9472`. An unchanged
depth-D physical-format consumer therefore accepts `t B^D` exactly when
`9475^D | t`; in particular t=1 fails at every positive depth. This is the
full depth-D divisor, not just one PNH factor at a deeper depth. The old
reserve is an overreserve relative to the live-only format and is minimal
for the two-format cardinality promise. This gate establishes no paid
adapter, joint ownership or physical implementation.

**Selected depth.** The source recurrence is `D(n)=0` below 64 and
`D(n)=1+D(42 floor(n/64))` otherwise. The map `42 floor(n/64)` is monotone
and strictly below n at internal nodes. Strong induction therefore proves D
monotone. For every allowed rank `1<=r<=42`, and for fallback widths at most
`floor(n/64)`, child depth is at most `D(n)-1`. Thus the theorem applies at
every finite n under the retained caller contracts. No finite depth census
is being extrapolated to prove this fact.

For `N=|GL64(F_q)|`, `H=q^(4096(w-1))`, every fixed eligible odd prime q and
integer w>=1 gives the stated B. The high matrix fibers remain present. Since
`28416<q` and `N<q^4096` in the eligible domain `q>2^80`, the predecessor
per-level upper envelope `log_q B<4096w+1<=4097w` still holds. No sharper
coefficient, fit cutoff or moment is claimed.

## Padding, arbitrary payload and paid work

For a genuine row range Q>=S, where S=B^D, pad to
`R=ceil(Q/S)S`. Then `Q<=R<Q+S<=2Q`. Supply actual zero padding and run the
whole endpoint before restriction. Its row-independent body interchange and
pointwise restored row coordinate preserve the genuine `[Q]` subset, so
restriction is correct for every original payload. The two completed ordinary
wrapper calls reuse S. Row-multiset preservation alone does not imply this:
a permutation exchanging a genuine and a padded row can lose a dirty input
when the padded tail is removed. The controls demonstrate this failure.

At actual logical volume V, a fixed family/low class retains all H and U and
has volume `v=V/(WN)`. The source's four buffers give occupied volume `V+4v`.
With `B0=W+4` stream slots, its nonchild parking bound remains

```
5(V+4v)-v+9B0-2 = 5V+19v+9B0-2.
```

The source's nine physical work slots remain in its inventory. Reducing a
row divisor does not remove buffer allocation, the COPY/ERASE bill, scans,
primitive arithmetic, recursive-child costs or total machine memory. We check
the unchanged formula, not an independent all-size parking implementation or
a measured numerical runtime gain.

## Reproduction and evidence

Python 3.12, standard library:

```sh
python3.12 -I -B scripts/research_package.py --package research/selected-live-row-divisor
```

Direct scientific replay also works from a read-only Git-free copy of this
package using `verify.py` and `independent.py`. The registered metadata checker
requires Git history for its historical provenance pins.

- Primary: 32 complete formats / 54,840 rows; 624 fresh child-fiber checks;
  all 42 rank choices and both explicit fallback widths at widths 64..10000;
  64 inverse-depth boundary pairs; 57 padding cases / 40,508 distinct symbols;
  unchanged work formulas; 12 semantic/domain controls; 73,710 exact
  two-format equivalences, 2,457 common-reserve identities and selected
  compatibility boundaries through depth 12.
- Independent implementation: Cartesian-product enumeration, separate radix
  routines and symbolic payload routes; 216 formats / 148,929 rows, 648
  high-child domains, 24,192 distinct payload symbols, 69,120 endpoint
  comparisons, 116 padding cases, and 11 countermodels. It does not import
  the primary checker or its receipt; its finite domains differ deliberately.
  Its separate compatibility census covers 18,000 equivalences, 720 direct
  minimum-common-reserve searches and selected boundaries through depth eight.
- `test_package.py` exercises the public verifier under normal and optimized
  Python, read-only relocation, source/manifest/receipt faults, and an actual
  disabled row-restoration guard. A missing receipt fails without regeneration.

`RESULT.json` is the required canonical primary receipt. Explicit
`--write-receipt NEW_PATH` creates a separate new file without overwrite.
`REVIEW.md` records the independent mathematical scope review. The all-depth
statement is a written conditional proof; the finite checks are corroboration,
not a formal-kernel proof. No complete selected payload, cold supplier replay,
physical caller admission, independent human review or hosted CI pass is claimed.

## Open next questions

1. Can a complete caller instantiate the new codec while satisfying arbitrary
   U, ancestor-only access, pointwise row restoration and paid workspace?
   Connect one full selected residual and its child boundary to the row schema;
   the global family/owner interpreter and physical primitive contracts remain
   the blockers. PR2405/Discussion2319 supply adjacent field-schema work.
2. Does any intended downstream consumer genuinely require P-based divisibility?
   Trace the exact consumer before integrating this format. If it does, retain
   the old compatibility reserve or prove a paid adapter. An arithmetic divisor
   check cannot establish that adapter or erase arbitrary input roles.

## Credit and license

Jose Manuel (`jmbarrancoml`) supplied PR2195's live/work split and explicitly
identified the overreserve; PR2234 supplies the recursive caller and charges.
Their results are the mathematical premises of this corollary. Credit remains
with DreamingOfClouds/PR589, eumemic/PR555 and the GL construction, alephnan/PR1627,
source527, commdata2338's parking/descriptor work, and the contributors retained
in `sources/pr2234/NOTICE.md`. Adam Gall, Nick Petalas, Josie Elliston, ToikY,
Sricharan Vagvala, Aakash and Sagar Thakrar supplied the adjacent stock audits.

Prepared for Ross Richardson with substantial OpenAI Codex assistance, including
an independent recursive-interface specialist. This is AI-assisted review,
not independent human review. Apache-2.0; copied sources and notices are unchanged.
