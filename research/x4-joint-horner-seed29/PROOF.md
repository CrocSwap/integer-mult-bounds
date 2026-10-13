# Joint two-source Horner preparation in fixed X4 frames

This is a finite scalar circuit construction. The selected conditional exponent
is unchanged. The independently checked claim is the exact linear map and cost
of the declared replacement class, not the full integer multiplication theorem.

## Circuit identity and full bill

Consider two adjacent scalar additions at the same frame:

```
T <- T + a S1
T <- T + b S2
```

The three registers are distinct and neither source is modified. Let
`a=A/2^K`, `b=B/2^K`, with the least common dyadic denominator, and nonzero
signed integers A and B. Set `L=max(bitlength(|A|),bitlength(|B|))`.

Choose sigma as the sign of the first occupied leading digit, breaking a
leading-digit tie in favor of S1. Copy that source into the existing coefficient
work register W. For the remaining leading source digit, if present, add or
subtract its source according to its sign relative to sigma. For each lower
position, double W once and add/subtract each occupied source digit. After all
positions, `W=sigma*(A*S1+B*S2)`. Halve W K times, then add or subtract W into T
according to sigma, and clear W.

Induction over digit positions proves the displayed value of W. Therefore the
complete arbitrary-input boundary map is

```
(T,S1,S2,W) -> (T+a*S1+b*S2,S1,S2,0).
```

The initial copy erases arbitrary prior W, rather than assuming it is clean.
The sources are unchanged throughout, so there is no restoration debt. The
target is updated once after both sources have been consumed; its earlier
update cannot affect S2 because target/source aliasing is excluded.

Every primitive is charged. Per real component the count is

```
1 copy + (L-1) doubles + (popcount(|A|)+popcount(|B|)-1) signed source reads
       + K halves + 1 target accumulation + 1 clear
= L + popcount(|A|)+popcount(|B|) + K + 1.
```

Complex values execute the same real-coefficient map separately on real and
imaginary components, doubling this count. There is one existing coefficient
work register per component, no new helper, source cache, persistent copy,
frame transition or recursive child. All instructions are at the common frame.
The source-read count is the total popcount and equals the two separately
lowered reads, including unit coefficients. Doublings, halvings, target
accumulations and clears account for the savings.

For example, `a=b=1/2` becomes `copy S1 to W; add S2 to W; halve W;
add W to T; clear W`: five primitives, compared with eight under PR696's
separate copy/Horner/accumulate/clear circuits. Removing only one redundant
clear would cost seven. This is a shared preparation across two *different*
sources, not just a changed clearing boundary.

## Finite domain and optimal disjoint selection

The input is the PR799 X4 backward event list, selected at the starting base and source-bound to its
SPEC and the committed integrated replay. Exactly 6,112 adjacent event pairs
have scalar ADDs, equal nonzero frame IDs, a common target, distinct sources,
and no register alias. No commutation, frame-zero compensation, reordering,
larger block or new parameter value is searched.

For each pair i, compute the above circuit and its exact saving d_i over
separately applying the accepted PR696 lowering. Retain only `d_i>1`, ensuring
that each candidate beats deletion of one work clear. There are 2,764 such
candidates. Selecting pair i consumes events i and i+1.

With `D[N]=D[N+1]=0`, the suffix recurrence is

```
D[i] = max(D[i+1], d_i+D[i+2])   if pair i is retained,
D[i] = D[i+1]                   otherwise.
```

Every admissible matching either omits i or consumes i and i+1, proving the
recurrence by induction. The witness attains `D[0]=6536` per component using
1,586 pairs. Ties skip the earlier pair. The code-disjoint verifier instead
uses a forward longest-path recurrence and checks the submitted nonoverlapping
witness attains its bound. This certifies only the stated disjoint pairing
class with this binary circuit and the `d_i>1` restriction. It is not general
circuit optimality, nor optimality over all coefficient-work schedules.

All 6,112 candidate four-register matrices are checked, including unselected
and losing ones. The Fraction and separate integer-grid implementations agree;
the latter checks all 97,792 matrix entries. Neither uses floating point.

## Composition, frames and private work

Each accepted pair has exactly the original two-macro boundary map. Every
surrounding event therefore receives the same logical inputs. Induction over
the event list proves scalar composition. The main checker evaluates every
primitive and checks each single-macro or pair boundary, followed by the full
backward endpoint `L_i <- L_i-L_(112+i)` for `0<=i<112`, with all other logical
registers restored. Its 737 independent formal columns cover 728 logical
registers (including 504 arbitrary helpers), eight arbitrary center inputs,
and arbitrary coefficient work. All private outputs clear.

A pair cannot cross a non-scalar event or frame change. Every source and target
already participates in an addition at the common frame. The primitive model
uses the existing private coefficient stream at that frame. The scalar
interpreters preserve, but do not execute, the physical phase/Clifford, frame,
wrapper or recursive operations. Production admission must still represent
the fused block's larger clearing boundary explicitly and rebind its receipts.

## Prefixes and complete conservative accounting

Joint W can have a larger *local* intermediate than either original W. There
is no general per-macro prefix-domination claim. For the particular full X4
backward word, exact replay checks every updated row after every primitive:

- maximum scalar row-l1: 5,338,828 before and after;
- maximum dyadic fractional depth: 19 before and after;
- propagated nonnegative envelope: `48299247699832632898063/16` before and after,
  still within the inherited 192-bit local magnitude allocation.

These finite scalar quantities do not certify the complete recursive physical
precision/tape interface. In particular, a magnitude allowance alone is not
a proof of a rounding or recovery contract.

The full backward primitive bill changes from 143,674 to 130,602 under PR696,
saving 13,072. Non-work source reads remain 39,446; total arithmetic operand
reads change from 146,392 to 136,492. These counts include both real components;
they are not hardware traffic or runtime measurements.

The forward PR696 count is retained at 143,658. The existing conservative local
invoice uses the maximum of the two orientations, so that maximum changes
only from 143,674 to 143,658. Retaining all 19,197 original macro charges,
3,574 recursive children, 728 logical registers and eight centers gives

```
adapters = 16*(19197+3574+728+8)+64*73 = 380784,
compiler = 64*74^3 = 25934336,
local bound = max(forward,backward) + adapters*compiler.
```

It changes from **9,875,380,343,098** to **9,875,380,343,082**, a reduction of
**16** under that conservative arithmetic recount. No adapter credit is taken
for fusion. This is not a run of the global invoice or outer assembly. The paid
profile, width/owner construction and analytic supplier exponents are unchanged;
no new kappa follows from a primitive-count improvement.

## Attribution and inherited obligations

The X4 checkpoint source is Jeremy Kothe's PR799, extending Chafik Boukhalfa's
PR741 frames and icekylinx's scalar/factory architecture. Sagar Thakrar's
accepted PR696 supplies the baseline lowering. See README for related searches
and the retained DreamingOfClouds, Rohan Arun, eumemic and predecessor credits.

All-size compilation, common-label/mutable-source realization, whole-call
hosting, recursive precision/tape, exact recovery, analytic transfer and the
bit-supplier assumptions remain inherited. Nothing here formalizes or improves
the complete multiplication theorem. Written for Ross Richardson with
substantial OpenAI Codex assistance, under Apache-2.0.
