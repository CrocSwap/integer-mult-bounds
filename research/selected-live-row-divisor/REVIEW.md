# Independent review of the live-row divisor

The changed-format claim is correct as a conditional cardinality and recursive
interface statement. It does not establish compatibility with an arbitrary
physical-slot caller. The minimality claim is correct only within the stipulated
format of independently complete layers, with positive integral leftover stock.

The initial complete-layer review and first implementation of `independent.py`
were developed from the two predecessor proofs before reading the primary
implementation. The review uses no primary-checker imports. It was produced by
a separate OpenAI Codex recursive-interfaces agent;
this is independent agent analysis, not independent human or formal-kernel review.
After the first independent implementation passed, its SHA256 was recorded as
`84159659e77081ab921ab1e361562edf0063e50ec94921b666bf7fb906c1e48f` before
reading the primary checker for a final consistency review. That review found
no conflict with the conditional theorem or these independent finite fixtures.
The exact two-format acceptance characterization below was added afterward
from its separate cardinality proof, without importing or copying primary code.

## Pinned sources and what was audited

The inspected source material is the README and PROOF from each of:

* Jose Manuel (`jmbarrancoml`), PR2195 at
  `3a1cf78a1ba6322129e42d80c50d21765524d612`, especially
  [PROOF section 5](https://github.com/CrocSwap/integer-mult-bounds/blob/3a1cf78a1ba6322129e42d80c50d21765524d612/research/selected-bit-local-ring-sweeps/PROOF.md).
* Jose Manuel (`jmbarrancoml`), PR2234 at
  `d047ef86fbc5b1614d3d8e2b8d3441413beab73f`, especially
  [PROOF sections 1, 6 and 8](https://github.com/CrocSwap/integer-mult-bounds/blob/d047ef86fbc5b1614d3d8e2b8d3441413beab73f/research/selected-bit-recursive-closure/PROOF.md).

PR2195 already separates live payload from private work, gives the volume
denominator `WN`, and explicitly identifies its physical-compatible choice as
an overreserve. The observation here is a small refinement of that construction;
the live/work separation and complete-packet method are inherited. The source
credits DreamingOfClouds, eumemic, alephnan and its further predecessors for the
selected word and proof infrastructure. No broader novelty is asserted.

In the inspected prose, `P` enters the row induction through the choice
`M=lcm(W,P)` and the additional compatibility observation. All live decodes,
packet volumes and fresh-stock arguments use `W,N,H`. In particular:

* PR2195 section 5 places all original payload in live rows, allocates private
  and selector work outside that split, and requires unused coordinates and
  row labels to be restored. Its later `P`-divisibility statement is an added
  compatibility property. It explicitly leaves PR2084's physical
  interpretation premise unresolved.
* PR2234 section 6 repeats that live decode and uses `W+4` role slots for its
  unequal-buffer parking bound. It does not divide the active volume by `P`.
  Section 8 borrows and pads to the chosen reserve, then removes padding only
  after a completed endpoint. Its cardinality step does not require `P`.

Thus no indispensable `P`-divisibility consumer appears in those inspected
steps. This is an audit of the supplied prose, not a search or verification of
every linked predecessor implementation, and it does not remove an independently
specified physical caller's premise.

A subsequent limited text inspection of the pinned `owner_packets.py` confirms
that its `row_layout` fixture chooses the `lcm` reserve and tests that choice;
it does not prove the smaller format. The pinned `recursive_plan.py` checks
proper child widths in a macroplan. No predecessor Python was executed in this
independent audit, and those inspections do not certify a whole-code allocator.

## Exact conditional theorem and proof

Let `W,N,H,t` be positive integers, let `B=WNH`, and let `D>=0`. The changing
format consists of a complete original row interval of cardinality `t B^D`.
Every original row carries arbitrary live payload; no original row is assumed
zero. At an active node the format consumes one independently complete
`[W] x [N] x [H]` layer. Children may require any depth `D'<=D-1`.

Assume the completed operations have these boundary contracts:

1. Packet primitives accept arbitrary complete unused ranges of the stated
   size, and leaves accept every positive row multiplicity. A call accepts
   all payload values, including correlated dirty values. This is an explicit
   changed-interface hypothesis: an old API promising only `K^D` multiples
   does not automatically satisfy it for the smaller reserve.
2. Current-header routes fix the unused row coordinate. Generated descriptors
   read only exposed ancestors, not the child's fresh family, matrix or
   leftover coordinates.
3. A child acts on the entire packet with old high coordinates as complete
   spectators; it restores the row and spectator coordinates pointwise.
4. Private copies, selectors and other work are allocated separately, with
   their full source shapes, preparation, scans, parking, cleanup and return
   costs. They are not relabelled arbitrary input rows to be zeroed.

At `D=0`, the leftover row interval has cardinality `t` and no fresh layer is
needed. At `D>=1`, mixed-radix decoding gives the exact bijection

    [t B^D] = [W] x [N] x [H] x [t B^(D-1)].

For a child of depth `D'<=D-1`, write

    U=t B^(D-1) = (t B^(D-1-D')) B^D'.

The first factor is a positive integer, so the child receives an admissible
complete range with multiplicity `t B^(D-1-D')`. For every fixed old high
coordinate, this is the identical whole range `[U]`. Old high values remain
complete spectators of the one child call; they are not a separate loop of
child invocations. Induct on the remaining depth. The route and restoration
hypotheses preserve the complete range after each call, so sequential reuse
is permitted. After `k` active levels, the unused cardinality is exactly
`t B^(D-k)`, with no compatibility-factor residue.

This proves sufficiency at every finite depth. It supplies fresh cardinality
only; all completed-child, causality, ownership and work contracts remain
hypotheses. It is a modification of the source's format, not an invocation of
a theorem whose declared input still requires the larger divisor.

For the source's width function, `D(n)=0` below 64 and
`D(n)=1+D(42 floor(n/64))` otherwise. Its argument is strictly smaller than
`n`; induction makes `D` well-defined and monotone. For an active parent,
`n'<=42 floor(n/64)` implies `D(n')<=D(n)-1`. The same inequality applies to
positive fallback widths at most `floor(n/64)`. This supplies the depth
hypothesis above without claiming anything about a different recurrence.

For minimality, suppose a positive reserve `S` itself has the fixed complete
format of `D` independent `W,N,H` layers and a nonempty integral leftover
range `[u]`. Cardinalities force `S=B^D u`; therefore `B^D` divides `S` and
`S>=B^D`. The displayed construction attains equality with `u=1`. The same
conclusion applies to a reserve promised to work for every multiplicity,
because that promise includes `t=1`.

This does not prove minimality among compressed, reused, correlated, adaptive
or non-Cartesian layouts. A promise of only a shorter actual execution path
need not consume `D` layers. For one specially chosen multiplicity `t`, its
factors might supply some required stock; uniformity over all positive `t`
must not be dropped from the reserve interpretation.

## Volume, costs and the physical format

A complete fixed-family/low packet includes every high and unused coordinate.
If `c` is the payload volume per original row, then

    V=c W N H U,                 v=c H U=V/(WN).

The separate four-buffer boundary and source parking expression therefore
retain their forms at the actual volume:

    occupied <= V+4v,
    parking <= 5V+19v+9(W+4)-2,

excluding the child and retaining all separately stated control and dispatch
charges. This algebra does not verify that the source's machine implements
those bounds, or evaluate a selected numerical invoice. It does not erase
the work bill or assert a numerical runtime saving at a different `V`.

For `W=28416` and `P=28425`, `gcd(W,P)=3` and

    lcm(W,P)=269241600,
    lcm(W,P)/W=9475,
    lcm(W,P)/P=9472.

Consequently the historical stock is `K^D=9475^D B^D`. At depth one and
`t=1`, `PNH` cannot divide `B=WNH`, since cancellation would require `P|W`.
This remains true for the actual positive selected `N,H`; no small-field
approximation is involved in that cancellation. The exact condition for an
unchanged depth-`D` physical format is stronger and can be characterized fully.

### Exact acceptance by an unchanged physical format

For any positive `W,P,N,H,t` and integer `D>=0`,

    (P N H)^D divides t (W N H)^D
        if and only if
    (P/gcd(P,W))^D divides t.

To prove this, cancel the common positive factor `(NH)^D` from the first
divisibility statement. Set `g=gcd(P,W)`, `a=P/g`, and `b=W/g`, so that
`gcd(a,b)=1`. Cancelling `g^D` leaves `a^D | t b^D`. The powers `a^D` and
`b^D` are coprime, so Euclid's lemma gives `a^D | t`. The converse follows
by multiplication. At `D=0` both sides say `1|t`.

Every cardinality compatible with both fixed complete formats must be a
positive multiple of `B^D`. The equivalence proves that its least possible
multiplicity is `(P/g)^D`; hence its least positive cardinality is exactly

    lcm((W N H)^D, (P N H)^D)
        = (lcm(W,P) N H)^D
        = K^D.

Thus the historical reserve is minimal for simultaneous cardinality
compatibility with both fixed depth-`D` formats. Calling it an overreserve
is relative to the changed live-only format, not to that two-format promise.
The smaller reserve is usable only when the physical-format consumer is
removed or its additional premise is proved unnecessary, or when the incoming
multiplicity independently passes the exact gate above.

For the selected constants, `b=9472` and `a=9475` are coprime. Therefore an
unchanged depth-`D` physical consumer accepts `t B^D` exactly when
`9475^D | t`. In particular `t=1` fails at every positive depth. The statement
concerns the full depth-`D` physical power; accidental divisibility by only
one `PNH` factor at a larger depth would not establish that contract.
This acceptance gate is a cardinality condition, not a proof of an adapter,
simultaneous layout ownership, charged work, or a completed physical caller.

For an arbitrary incoming cardinality `R>=S=B^D`, rounding upward to
`ceil(R/S) S` is less than `2R`. Removing padding is valid once the completed
endpoint restores every row coordinate and performs the desired action
within each row. Intermediate permutations may mix genuine and padded rows;
premature restriction can destroy genuine payload. Pointwise restoration is
a sufficient condition. Merely preserving a multiset of row values does not
establish it.

## Independent finite evidence

Reproduce from the repository root:

```sh
python3 -I -O -B research/selected-live-row-divisor/independent.py
```

Normal and optimized runs passed under Python 3.14.6; the first optimized run
took approximately 1.1 seconds. The
checker uses Python's Cartesian-product enumeration as an oracle independently
of its integer encoding and decoding routines. Its complete finite domains are:

* `W,N,H in {1,2,3}`, `D in {0,1,2,3}`, `t in {1,2}`: 216 formats,
  148,929 rows and 585,945 exposed-prefix/unused-suffix checks; 648 complete
  old-high/child-depth domains and 162 volume/parking identities.
* Six fully enumerated payload fixtures `(W,N,H,D,t)`:
  `(2,3,2,2,1)`, `(2,2,3,3,1)`, `(3,2,2,2,2)`, `(1,3,2,3,1)`,
  `(2,1,3,3,1)`, `(3,2,1,3,2)`. They contain 24,192 distinct formal input
  symbols, including an extra complete spectator and two binary data
  coordinates. Literal suffix cycles, data interchange and inverse cycles
  give 69,120 pointwise endpoint comparisons at 30 complete child boundaries.
  Equality on distinct symbols is an exact permutation identity, hence it
  allows every substitution of correlated Boolean payload values.
* Widths `0..4096`: 169,386 positive rank-child checks and 129,088 fallback
  checks. These are finite checks using the source recurrence directly, not
  an independently derived depth algorithm. The Cartesian-product and
  distinct-symbol tests provide the independent layout/endpoint coverage.
* 116 complete padding cases for stocks `{1,2,3,4,6,8,12,18}` and each
  `R` from `S` through `3S`, plus 108 finite base/depth cardinality cases.
* 18,000 exact acceptance equivalences for `W,P in {1,...,12}`,
  `D in {0,...,4}`, `t in {1,...,25}`, using `N=2,H=3` in the direct
  full-power divisor. A direct ascending search, independent of the lcm
  formula, establishes all 720 least common reserves in that domain.
  At the actual selected `W,P`, depths `0..8` test acceptance of `t=9475^D`
  and rejection of the positive `t=9475^D-1` boundaries. The depth-zero
  latter value is `t=0`, explicitly outside the positive-multiplicity domain;
  it is not counted as a failed divisibility case.

Eleven controls distinguish: omitting high stock at the first level; omitting
it only in descendants despite a successful root decode; absent physical-slot
divisibility in a small model and at the selected depth-one constants; COPY
pollution from arbitrary dirty private input; noninjective clearing of that
input; row-multiset preservation without pointwise restoration; spectator
drift; removal of padding before restoration; applying the factor-two bound
without `R>=S`; and allowing a child the unconsumed parent depth.

The payload fixture is a generic complete-call probe, not the selected scalar
word, GL64 cover, weighted residual or physical tape machine. The finite tests
do not establish every-parameter claims; the written arguments above do.
Neither is a formal-kernel proof.

## Open obligations

The parent package owns exact predecessor-file authentication, selected-record
status and publication. Separate machine/circuit review would be needed to
replace the stock in an actual caller, check all generated descriptor paths
and separately allocated work, and retain pointwise restoration at every
recursive boundary. No physical `P`-slot contract, selected finite invoice,
ordinary-supplier implementation, multiplication exponent or new kappa is
certified by this review.

This file and the independent checker are Apache-2.0, with substantial OpenAI
Codex assistance; predecessor attribution and source-specific licenses remain
with the inherited materials.
