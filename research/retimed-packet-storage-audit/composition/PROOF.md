# Ordinary ancestor storage composes under explicit local envelopes

## Exact source and claim

This is a source-bound completion of the ancestor-composition step in
Ali Romman's PR #8042 at `dfd25d553a843a946ca0b94130a5ff8943e98fdd`.
The canonical comparison base is
`CrocSwap/integer-mult-bounds@e54523517d0f03e58352e647c403a5af3e525a57`.
The twenty-two retained source files and their hashes are in `SOURCE-BINDINGS.json`.
The installed path starts in `ordinary_carrier`, uses `binary_receiver.Receiver`,
and inherits the physical methods in `receiver.Receiver` and
`same_order_body.SameOrderBody`. In particular it uses `five_exchange`'s
`same_order_line`, not the older similarly named bodies in other modules.

The predecessor's `STAGE-STORE.md`, `ACTIVATION.md`, and `StageStore.historical`
already state the historical-allocation strategy. The existing packet audit
proves the complete caller equations, return fence and a conditional geometric
bound for one role. This contribution supplies an explicit coefficient for
all twenty named ordinary heads and composes the current stage's banks and
spools with every strictly earlier stage. It does not transfer an argument to
the older installation in PR #8048.

Coordinatewise historical accounting is prior work: Hiroki Kumazaki's
[PR #5286](https://github.com/CrocSwap/integer-mult-bounds/pull/5286), head
`b1577bd405f5c7ade3616486b5fe44478e0ba5cb`, bounds the literal interchange's
local history. [PR #5404](https://github.com/CrocSwap/integer-mult-bounds/pull/5404),
head `97df7e3dd5052d625a64bf5dbbd0a990fb2f14b0`, applies that principle to
nineteen modeled continuation tapes and leaves production path summability
open. This note specializes the principle to the current #8042 twenty named
heads, separately indexed work roles and actual predecessor callers. It does
not claim that generic principle as a new result or transfer the modeled
continuation-tape contract to this source.

The result is conditional in two precisely separated places:

1. At rank `N`, the binary owner's free-first capacity is at most `beta B`,
   where `B = core.owners`. The current source uses `beta=2`, retaining its
   binary raw-owner and mass-enclosure argument. The separately reviewed
   Gaussian owner census is not a proof of this binary premise.
2. The remaining transient ordinary work roles have uniform local byte
   envelopes, defined below. The composition theorem propagates those
   envelopes; it does not establish all of them or the complete movement,
   private-control, header or outer-numerical contracts.

No selected assumption, kappa, activation threshold or physical-machine
admission changes. This written proof and its finite regression checks are
not a formal-kernel or independent human acceptance of the multiplier.

## 1. True arguments, not scratch copies, recur

For a weighted activation let

\[
 W=A O\alpha^{2c}GS,\qquad c=Nf+r,
\]

where `A` is the available fresh cardinality, `O` the entire older cardinality,
`alpha=3**total_width(layout)`, and `G,S` the true gap and byte suffix.
Compilation requires `A=U B Q H`, with `Q=core.low` and `H=core.high`.
The two residual factors `alpha**r` enter the actual gap and suffix. Therefore
one `OwnerBanks` slot has exactly

\[
 V=UQHO\alpha^{2Nf}(G\alpha^r)(S\alpha^r)=W/B. \tag{1}
\]

The bank's whole historical extent can be `beta W`; equation (1) does not
replace that bank charge by one slot.

The direct empty-line child and the child between the two direct basis routes
receive exactly `V`. A covered child receives one complete low packet
`ell=V/Q`. In `five_exchange.same_order_line.child`, the exponent sum is

\[
 if+2f+((N+j)f-if-f)+(2Nf-(N+j)f-f)=2Nf.
\]

Consequently its high representatives, older coordinates, spectators, gap,
suffix and both coarse blocks all remain present. Preparatory and inverse
children have the same volume. They are serial, so the number of children
does not multiply a simultaneous stack charge.

In the installed binary receiver `transport.Recipe` sets
`width_log=92*rank_log`, hence `B=N**92`. The installed profile's ordinary
rank logs are all at least 5610. The theorem only needs `B>1`; the numerical
corollary below uses `B>=17`. A covered-to-direct dispatch shares its arena
and occurs before opening a second weighted scope, so it adds no uncharged
activation of volume `W`.

For the same stage, along any active chain,

\[
 W_d\le W_0 B^{-d}. \tag{2}
\]

This statement is production-specific. The source's small-rank branch uses
`recipe=None` and `B=1`. At a generic direct call with `N=2`, `A=1`, and
`c=2^D`, the successive complete volumes are all `W`, while `c` halves.
Already the first weighted head retains `(D+1)W` along this chain. No coefficient
independent of `D` follows if the premise `B>1` is removed. This is a
symbolic exact-source boundary, not a production counterexample or an
execution of the enormous corresponding field.

## 2. Every named ancestor role has a coefficient

On a named head a child starts at the parent's current end. Parent writes
and resizes are prohibited while a child is topmost. Erasure precedes
truncation, and release erases the complete retained child interval.
Pending and answer stacks restore their saved markers. Thus, for one fixed
role, its historical endpoint is at most the maximum, over the entire trace,
of the sum of that role's open local extents. Longer retired siblings are
included in that maximum, and later siblings reuse the parent base.

The following are **coordinatewise bounds**: each individual role satisfies
its row's bound in every invocation. They therefore remain valid when
different heads reach their maxima in different calls or modes. `V=W/B`.

| Fixed named role | Heads | Bound per head | Source reason |
|---|---:|---:|---|
| weighted | 2 | `W` | `pipe` copies and returns one complete argument |
| compiler backing | 1 | `beta W` | free-first capacity `<= beta B`, each slot `V` |
| compiler staging and result | 2 | `W` | complete stock transpose and final serial owner collection |
| issued-leaf | 1 | `V` | one complete returned owner |
| chart-line | 2 | `V` | full low split and full collected answer |
| chart-packet | 2 | `V/16` | one low packet; wide `Q>=16` |
| exposed-leaf | 2 | `V/16` | its complete low packet |
| direct-coordinate | 2 | `V` | full direct owner between basis routes |
| matcher | 2 | `V` | a direct route acts on one whole owner |
| triangular-body | 2 | `V/16` | one body `b=V/(UQH)`, with `U,H>=1` |
| pending and answers | 2 | `V` | each local stack suffix is at most one complete owner |

These are all twenty named heads in the installed source inventory. In wide
mode, `Q=product(3**j-1, j=1..N)>=2*8=16`. Covered-only roles are absent
in direct mode, so their `V/16` bounds hold uniformly across mixed modes.

The aggregate local coefficient is

\[
 C(B,\beta)=\beta+4+\frac9B+\frac6{16B}
             =\beta+4+\frac{75}{8B}. \tag{3}
\]

For each role separately, apply (2) to its coordinatewise coefficient and
then sum the twenty inequalities. This gives the complete named-head
historical cover

\[
 H_{named}\le G(B,\beta) W_0,
 \qquad
 G(B,\beta)=\frac{(\beta+4)B+75/8}{B-1}. \tag{4}
\]

For `beta=2`,

\[
 G(B,2)=6+\frac{123}{8(B-1)}.
\]

Thus `G<=171/8` for `B>=2`, and `G<7` for production `B>=17`.
The bank, every suspended compiler, both mode-specific wrapper families and
all inherited pending/answer prefixes are included. Small rank fixtures do
not certify this geometric consequence.

The two packet-stack heads must each be charged. During a complete line the
live pending and answer suffixes plus the active packet total `V`, but the
pending head can have historical maximum `V` before the first pop and the
answer head maximum `V` after the last append. Their historical sum is `2V`.
Replacing the sum of individual maxima by the maximum of the instantaneous
sum would invalidate (3).

## 3. Work spools survive earlier stages, not another paid edge of this stage

The exact source fence is relative to the persistent root and named roles.
`pipe` invokes one gate to completion before the next. A direct matcher,
quotient route, lower shear and raw clone/move/XOR operation return and close
their work-file scopes before a same-stage weighted child starts. Raw jobs
are yielded outside those scopes. A stopped `weighted_pair`, a direct
matcher exchange, a quotient affine exchange or `unit_scale` can retain
work spools across a **strictly earlier-stage** call.

Let `a_r` be a uniform local endpoint coefficient for transient work role
`r` inside a weighted activation: every use of that fixed call-site/tuple
position ends at most `a_r W`. The coefficients must hold for all shapes
and modes using that role. Set `A_stage=sum_r a_r`. Exclude the two public
rectangle files, five stage-root files, and eleven cold-interchange roles,
which are charged separately below.

Because a transient role is not reentered by a same-stage child while it is
open, and every descendant's true argument is at most `W_0`, its historical
maximum is at most `a_r W_0`. Hence

\[
 H_{transient}\le A_{stage} W_0. \tag{5}
\]

There is no geometric multiplier on (5). A parent's different-stage scratch
is still allocated; the earlier stage uses a different indexed role set,
whose charge is added in the next section.

This is the correct way to reuse a local byte result. A statement only of
the form “the sum of role peaks in this one invocation is at most `KV`” is
insufficient by itself across differently shaped invocations. Uniform
coordinatewise envelopes, or a separate bound on their sum over all call
shapes, are needed. The reviewed type-route proof gives such envelopes
`(3,3,1,1,1)W`, summing to 9. The reviewed wide-owner route proof also lists
individual role envelopes totaling less than eight actual owner volumes.
Their contribution can therefore be included as `9+8/B` in `A_stage`,
provided all uses outside those routes have their own separately added
envelopes. Shared roles may be conservatively counted in both groups.
The Gaussian repair bound belongs to a different service and is not inserted
into an ordinary-stage spool charge.

## 4. All earlier-stage caller volumes are bounded

The actual callback is `partial(ordinary_carrier.ternary,
maximum=stage-1, profile=profile)`. Its selected positive stage is strictly
smaller. No same-stage scratch reentry is hidden in the predecessor service.
Every preceding call below operates on its complete named input interval.

| Source call site | Complete volume passed to the preceding service |
|---|---|
| `weighted_pair.swap` | `prefix * 3**(2*width) * gap * suffix`, exactly the pair's incoming volume |
| `direct_route.exchange` | `p * 3**(2*width) * g * s`, exactly the whole matched owner |
| `affine_packet.exchange` | `side**fields * piece`, exactly the current affine packet |
| `unit_scale.schedule` | `front * 3**(2*v) * tail` at a halving step, exactly the scaler's incoming volume |

For a direct route, `pair_shape` leaves both selected atom axes out of the
prefix/gap/suffix product, and the callback reinstates those two axes.
For an affine exchange, the exponents add as
`left + 2 + (right-left-1) + (fields-right-1) = fields`.
Its packet is a suffix of one full high packet and therefore no larger than
the owner. For the scaler, an odd step replaces `v` by `v-1` and `tail` by
`3*tail`; an even step halves `v` and multiplies the tail by `3**v` for the
next iteration. Both preserve `front*3**v*tail`. The swapped double limb is
the whole current field before the latter tail update. Finishing descriptors
retain their exact saved shapes; they do not allocate a new full spool per
iteration. Thus every preceding argument is at most the current weighted
argument, including stopped pairs where equality holds.

The earlier stage takes one consecutive prefix slab at a time. If its
unpadded slab volume is `U`, `root_body` uses `extent=3**k>=rows` and
`padded=ceil(extent/rows)*rows<2*extent`. Its weighted entry is therefore

\[
 W_{new}<2U. \tag{6}
\]

The five root roles have individual peaks at most `W_new`: expanded/body
are padded, and genuine/high/trailing are at most the unpadded slab.
The root's two cold corrections are serial and use the same eleven roles.
In a cold interchange the two main spools are at most the input and each of
the nine trit buckets is at most one ninth of the input. The sum of their
uniform historical envelopes is at most three input volumes. This charges
all root return corrections by `3 W_new`. It also supplies the separate
terminal cold-stage bound used below.

## 5. Complete ordinary-stack coefficient

Let `m>=1` be the length of the installed ordinary rank list, at most seven.
Let `X` be the maximum unpadded binary prefix-slab volume at this public
ordinary entrance (the actual source uses the same shape for every slab),
and `T` the corresponding ternary rectangle. If the call enters a native
stage, `T<9X`. Public prefix slabs run serially, so the two public rectangle
roles have total historical extent at most `2T`.

Index stage roles by their actual installed index `j=1..m`, highest first
along a descending path. By (6), strict stage descent, and the nonexpansion
of every other true caller, the largest possible weighted entry of stage
`j`, over every branch and retired sibling, is bounded by

\[
 W_j^*<2^{m-j+1}T. \tag{7}
\]

This is an individual bound for each stage. It does not assume that different
stage or role maxima occur together. There is at most one root of each index
on an active path, and the next invocation of that index reuses its zeroed
role tapes. Its pages and packet stacks begin at the empty stage baseline.

The sum of every ordinary role's historical endpoint, excluding the borrowed
caller input/output backing, is bounded by

\[
 H_{ordinary}\le
 2T+\sum_{j=1}^m
   [G(B_j,\beta_j)+8+A_j]2^{m-j+1}T
   +3\,2^mT. \tag{8}
\]

Here 8 is the five persistent root files plus the three-volume cold-root
envelope. The last term charges the distinct cold terminal stage. Every
earlier stage's retained source/target intervals are existing parent pages
or spools, already counted by their parent coefficients; new earlier-stage
scratch is counted in its own summand. A coefficient such as `A_j` never
multiplies the next true argument in (7).

For the retained binary premise `beta_j=2`, production `B_j>=17`, and a
uniform remaining-work envelope `A_j<=A`, (8) yields

\[
 H_{ordinary}<
 [2+(15+A)(2^{m+1}-2)+3\,2^m]T. \tag{9}
\]

At seven stages this is

\[
 H_{ordinary}<(4196+254A)T
              <(37764+2286A)X. \tag{10}
\]

The coefficient is independent of same-stage depth, number of siblings,
number of served lows, number of prefix slabs and number of visits to an
earlier stage. A fixed delimiter/one-past-end allowance is additive per
reserved head. Outer Gaussian/CRT storage, native private control and
movement remain separately charged. The theorem does not instantiate `A`
with an unproved complete local tariff or infer a new global threshold.

## Evidence, limitations and next question

`check.py` authenticates the exact source bytes and checks source-extracted
caller geometry, actual page/packet-stack historical behavior, earlier-call
size invariants, stage-cap syntax and exact rational coefficients. Its
negative controls remove the stage descent, enlarge a scaler tail, omit a
low packet divisor, and substitute one simultaneous sum for two historical
maxima. A separate symbolic example records the `B=1` boundary. These finite
checks corroborate the written identities; they do not execute production
ranks or prove the retained binary owner/mass or remaining-work premise.

The useful next task is the uniform coordinatewise envelope `a_r` for the
remaining ordinary work sites, especially direct scaling and stopped
weighted-pair helpers. The first step is to list every use of a shared
call-site head, prove a bound relative to that use's complete true input,
then take the maximum across modes before summing. The present result
allows those local envelopes to be substituted without reopening ancestor
composition. Universal binary owner/mass, header/private-control, and
complete fixed-tape movement remain separate obligations.

Credit: Ali Romman and the retained predecessor authors; the existing packet,
owner and byte audit contributors. Prepared for Jerry Chen / @CubeJerry with
substantial OpenAI assistance. Apache-2.0.
