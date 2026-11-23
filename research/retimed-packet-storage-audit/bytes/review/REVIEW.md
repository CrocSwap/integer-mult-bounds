# Independent review of the local historical-byte bounds

## Decision

**Accept the source-local byte theorem, with the documentation correction and
explicit symbolic generic-API boundary recorded below.** The relevant proof is
`../PROOF.md`, SHA256
`8b5750458db4037166c677f62df68f4111fb5fd749343fad28ea12867b289805`.
The interrupted draft had SHA256
`d21a68af1cd9720b691fdd4866452c909955557e211a75f93ead381db88f64cc`.
Its local route, padding and production-repair arguments need no change.

The source is Ali Romman's PR #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`. All 26 resolved source modules
and the three retained documents/checkers remain byte-identical to the author
manifest. The current canonical base remains
`e54523517d0f03e58352e647c403a5af3e525a57`; the selected result remains
conditional κ = 0.00363005817 under its five listed premises.

The accepted statements concern a successful, valid **wide** owner route,
the padded type transpose, and repairs reached through the named successful
production headers. They count complete stored bytes at every fixed role's
historical maximum, including zero padding, retired contents and nonsimultaneous
maxima. They do not certify all ordinary work sites, the outer CRT allowance,
private descriptors, tape movement, analytic mass, an activation threshold,
or the advertised complete 297.6n ceiling. They do not remove one of the five
canonical assumptions or provide a new κ.

## 1. Route geometry and the historical sum

I checked the actual expressions in `Receiver.transition`,
`Receiver.compensate`, `OwnerBanks.route`, `quotient_right_route`,
`high_packet`, `affine_packet`, `unit_scale`, and `lower_tape`.
The actual wide receiver rejects rank below two. Its complete atom width and
positive column multiplicity give

\[
b=O3^{2Nfw}GS\ge3^{2N},\quad
Q=\prod_{j=1}^N(3^j-1)\ge16,\quad
R=3^{(d-1)N(N+1)/2}b,\quad P=QR,\quad V=UP.
\]

The high-packet callback receives the complete body size `b`, while the high
router retains its own `R`-byte packets separately. In compensation,
`pair_shape` leaves the product of the two complete atoms, prefixes, gaps,
and suffix equal to `b`. Each coefficient run repeats exactly the prefix
volume that it owns. The two named compensation pages and three local
`lower_tape` positions therefore add at most `5b`.

There are five payload positions and five tag positions in the quotient
sorter's ten-file tuple. Each low tag is the actual `N²` bytes emitted by
`bytes(...)`; the tag volume is `T=QN²`. A stable radix pass partitions a
complete group, empties the inputs, rejoins the three buckets and empties
them. The final copy empties the surviving inputs. This reasoning covers both
odd and even `N²`, and leaves both ping-pong positions empty before the next
group. Thus the historical sum is `5P+5T`, independent of the number of groups.

The high pair contributes `2R` and the affine triple `3R`. Inside the scaler,
`front·3^v·tail` remains its entering volume `R'≤R`. The three permanent
positions each have bound `R'`; every odd-step position has bound
`R'/3`, because its prefix slab consists of three distinct output branches;
and the carry temporary has bound `R'/3`. The odd and carry sites are distinct
fixed roles. Counting both maxima gives `17R'/3`, even though those sites are
not simultaneously open. The deferred finishes are descriptors and do not
keep nested same-stage scaler files open.

Adding the route output and these 31 other local role/page positions yields

\[
L\le V+5P+5T+(32/3)R+5b.
\]

For literal tags, `T/P=N²/(Hb)≤4/81`: the sequence
`N²/3^(2N)` starts at `4/81` and each ratio is at most `1/4` for `N≥2`.
Also `b≤R` and `R/P=1/Q≤1/16`. Consequently

\[
L\le V+(5+20/81+47/48)P
\le (9365/1296)V<8V.
\]

The looser `8V` statement is retained. For a sequence of calls with varying
shapes, apply each individual role bound at a common incoming-volume bound
before taking maxima. An empty word copies directly; zero groups must be
handled separately because division by `V=0` is unavailable.

Borrowed owner banks remain separately charged. For named pages the bound
is on the local suffix: the actual address also includes every suspended
prefix on that tape. The previously reviewed stack/same-stage lifetime
lemma supplies this composition. Any call to a completed preceding ordinary
stage has its own role set and charge. Neither the finite tests nor this local
sum convert that service to free storage or an unproved constant-time move.

## 2. Padded type route

The exact source pads `q` types to the least ternary power `τ≥q`. For `q≥2`,
`τ<3q`, so its complete padded byte volume is `V'<3V`. Its two full positions
have bound `V'`; each of three buckets contains at most one third of one
prefix slab, hence has bound `V'/3`. Prefix buckets are erased before reuse.
The sum of historical role maxima is therefore at most `3V'<9V` in both
directions. Input and output are external to this scratch sum. Zero rows,
zero suffix and the singleton-type path open no work files.

Counting padded cells as absent would fail even though their numerical values
are zero. The independent checks explicitly find such a failure when replacing
the padded scratch allowance `3V'` by the unpadded `3V`.

## 3. Repair bytes and the production entrance

For `M=2^(L-z)`, grouped payload `a=c2^z` and byte tag width
`t=max(1,ceil((L-z)/8))`, the source writes exactly `E` bad groups. Its dirty
spool has length `E(a+t)`; either binary bucket can reach that same bound at
a different radix pass. Its clean spool has `(M-E)a` bytes. Subsequent passes
overwrite prefixes and use the actual current counts. The scratch context
clears the complete old physical file extent on return, so stale tails stay
within the historical bound and cannot be omitted. With the input and one
replacement included, the resulting bound is `5V+3Et≤8V` when `t≤a`.

The production implication does not assume that an arbitrary field has wide
records. The successful `Product` constructor enforces `b≥5`, `P≥6b` and
`prod(sides)≤2^b`; every accepted side has `width=(side-1).bit_length()`.
The elementary inequality `2^width≤side²` implies `sum(widths)≤2b`.
`spectator_layout` only removes bits, while `h_pack` supplies component size
`wide=floor((2P+47)/8)≥b`. The slab entrance reduces address dimension and
preserves record size. `Positive.hadamard` widens records before execution;
the descended positive arenas reduce dimension and retain that wider size.
Every repair on this path therefore has `L≤2b≤c` and `t≤c≤a`. The extra
widened root field remains a separately charged allocation.

### Corrected generic-API wording

The original README described the 17-bit, one-byte-component example as if
it refuted the same complete `8V` statement. Its exact evidence only showed
`t=3>a=2` and `dirty=655360>2V=524288`. I narrowed that wording.
In fact the complete sum for that all-bad identity case is **7V**.

There is a precise unrestricted complete-bound counterexample, now added
to the proof. For any all-bad identity repair with `L≥1,z=0`, all binary
labels occur once. Every radix pass places exactly `M/2` tagged records into
each bucket. The exact historical sum, including input and replacement, is

\[
2V+M(a+t)+2(M/2)(a+t)=(4+2t/a)V.
\]

At `L=33`, one-byte components give `a=2,t=5`, hence **9V**. This is a
symbolic complete-label source-loop census, not a claimed execution of
`2^33` records. It exposes the need for a production hypothesis without
contradicting the production bound.

## 4. Independent evidence and regression evidence

`check.py` uses source-extracted function bodies and a separately written
in-memory stream interpreter that records every visited endpoint. It does
not import the author's byte meter or call any author checker. Its companion
oracles use direct array indexing, modular multiplication and lexicographic
sorting. The previous ordinary swap is supplied by a direct-index oracle,
so its correctness and resource bill are explicitly outside this test.

The completed independent checks are:

- 195 type-route cases, both directions, non-power-of-three type counts,
  several true row/suffix extents and zero/singleton boundaries;
- 96 unit scalers covering digits zero through seven, all three work sites,
  392 previous-swap oracle calls and direct modular permutation equality;
- nine successive sorter groups with both four-pass and nine-pass parity,
  all ten original positions empty between groups and exact lexicographic
  output;
- six repair cases including no errors, all errors, mixed errors, zero
  address dimension and a nonidentity permutation of the bad groups;
- a bucket-erasure mutation and omission-of-padding control, both rejected;
- exact symbolic total-volume boundary calculations at dimensions 17 and 33.

These are finite discrimination checks; the all-size result is the source
argument above. Source extraction does not prove the installed dependency
resolution or the entire caller. Separately, I reran the author's complete
`verify.py` in an isolated copy against the exact restored runtime. It passed
all 26 resolved-source bindings, the 20 named/91 work-position inventory,
full-high owner traces, 142,599 exact header cases, and its three source
mutations. The complete-high fixture used 2,834,352 bytes per owner and the
rank-three fixture tested odd sort parity. Those actual-runtime executions
are regression evidence; the separate checker and proof review provide the
additional independent method. See `AUTHOR-REPLAY.log` and `../evidence/`.

Reproduce the independent review from the byte package directory:

```sh
python3 -B review/check.py
```

Expected marker: `PASS_INDEPENDENT_LOCAL_BYTE_REVIEW`.
The exact source commit, proof hash, counts and symbolic boundaries are
recorded in `review/RESULT.json`. Runtime restoration for the author replay
is provided by the enclosing storage package and its own immutable sources.

## Open next questions

Complete the remaining local ordinary-role byte obligations, beginning with
`direct_body.scale_atom`, the root rectangle/pad and complete compiler-bank
occupancy, then compose their legal adapter nesting with the outer CRT and
control allocations. The inherited factors 256, 32, 80 and `2^1024` require
their own complete-source justification. The accepted Gaussian owner census
provides the slot-count input; its production exponent still explicitly
uses the universal mass enclosure. These missing items prevent promoting
the local result to a complete storage or multiplication theorem.

Credit Ali Romman and all retained source authors, the interrupted byte-audit
author and owner-census reviewers. This completion is independent
model-assisted review with substantial OpenAI assistance for @CubeJerry,
not independent human approval or formal-kernel acceptance. Apache-2.0.
