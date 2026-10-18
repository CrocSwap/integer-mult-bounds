# A chronological P104 schedule attains the known 32-chain bound

**New constructive attainment and a scoped tail invoice, not a new lower
bound, restored supplier, or kappa.**

Ali Romman's [PR1125](https://github.com/CrocSwap/integer-mult-bounds/pull/1125)
already proves that monotone P104 fixed-term delivery needs at least
**32 paths**, including the eight seeds. Its proof explicitly does not
construct a schedule attaining that bound (PROOF lines 204–206).
This package supplies that missing **globally executable 32-chain
attainment for the exact fixture from Josie Elliston's
[PR1071](https://github.com/CrocSwap/integer-mult-bounds/pull/1071)**.

Allowing independent target read orders reduces that fixture's witnessed
delivery bank from PR1071's **55 under a global order** to **32**, or
**24 additional arrays instead of 47**. `SCHEDULE.json` executes all
**416 reads on 104 targets**, and its conditional supplied-copy tail
profile improves componentwise. The existing 32-path antichain bound is
rechecked as a credited special case, not claimed anew. The supplied-copy
boundary does **not** form or restore copies: those costs remain unknown,
not free work.

## Exact object and retained restrictions

The fixture is `section4_explicit_P104` of the hash-pinned
`research/biframe-decoder-ladder/RESULTS.json`. The eight pairs `(a_k,b_k)`
are doubled-coordinate E8 roots. On the 104 live root lines,

```
D[t,k] = <r_t,a_k>,   T[s,k] = 2 <r_s,b_k> / <a_k,b_k>,
D T^transpose = 2 G.
```

Each centre gathers in an eight-dimensional binary label hyperplane and has
a rank-seven drop to its one-dimensional survivor `span(u_a_k)`. Its 52
readers are orthogonal to that survivor. All eight survivor labels are
independent over F2. These are predecessor facts, independently rechecked
here for this fixture, including all 10,816 decoder entries and all eight
pairing ranks. The copied-information charge **56 is not a new result**.

Let `K_t` be the nonzero positions in row `D[t]`. A target chooses any
permutation of `K_t`; immediately after its j-th read its frame is **exactly**
the span of those j survivor labels. There are no additional spectator
frame directions. A delivery array carries one fixed centre value throughout
its lifetime, follows nested read frames, and has no subsequent drop, reload,
or mixing with another centre. Equal-frame reads may share the same array.

Compared with PR1071 this changes the global-order restriction. Compared
with PR1125 it adds an explicit chronological attaining witness and tail
invoice, not a stronger obstruction. PR1125's lower bound covers all 7168
mixed decoders and permits additional frame directions and paid downward
moves; our witness concerns one pinned decoder with exact prefix frames.
It does not optimize other decoders, dynamic centre mixing, additional
drops, or an admitted physical P104 compiler. Its target frames stay inside
their final hyperplanes because each read survivor is orthogonal to that
target's label.

## Proof of the sharp minimum

### Credited lower bound: 32 incomparable final reads

The following is the minimal-prefix special case of PR1125's terminal-read
theorem (PROOF sections 1 and 4). The independent replay rederives its finite
premises on this fixture; the bound and antichain idea belong to PR1125.
The exact target support distribution is

| Number of centres read | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|
| Targets | 12 | 24 | **32** | 24 | 12 |

The 104 support masks are distinct. In particular, each of the 32 four-read
targets has a final read at its four-dimensional support span. Because all
eight survivor labels are independent, those 32 subspaces are distinct.
Distinct subspaces of equal dimension are incomparable. Any monotone
fixed-centre delivery chain can visit at most one of them, regardless of
which centre supplies the final read. Therefore **at least 32 arrays/chains
are necessary** for every allowed collection of target permutations.

This lower bound does not assume a common prefix tree, a bound on program
length, or the particular search algorithm used for the witness.

### Upper bound: exact schedule and chronological feasibility

`SCHEDULE.json` contains 116 parent edges on the eight-bit subset lattice.
An entry `[S,k]` means that the chosen path into `S` adds bit `k` to
`S without k`. Following parents to zero gives each target's read order.
Every parent edge is used by at least one target. Each centre's used read
frames are explicitly partitioned into nested chains:

```
centre                 0  1  2  3  4  5  6  7
number of chains       5  3  4  4  4  3  4  5     total 32
```

The replay checks every frame, chain assignment, omitted/duplicate read,
and the full scalar coefficient matrix. It then executes events in increasing
`(frame dimension, frame mask, centre, target)` order. Each target dependency
strictly increases dimension. Each strict copy-chain dependency also increases
dimension; all reads at one fixed frame are consecutive within that chain.
Thus the event order satisfies both sets of dependencies and cannot contain
a chronological cycle. This is more than a disconnected collection of
minimum path covers. The receipt also exhibits two targets with incompatible
centre precedences, confirming that the changed hypothesis is actually used.

The schedule plus the antichain lower bound proves **exactly 32**, in the
precise minimal-prefix, fixed-centre, no-redrop geometry above.

## Complete invoice at the declared supplied-copy boundary

This section deliberately does not call its subtotal a complete supplier
profile. Its boundary is:

* one exact centre value is already available on each of the 32 arrays at
  its singleton survivor frame;
* each target enters at frame zero with arbitrary target value;
* every array is completed to the full rank-nine frame after its last read;
* every target is completed to its rank-eight final hyperplane after its
  last read.

All positive frame increments at this boundary are counted. Rank-r transports
are denoted `H_r`.

| Contribution | New per-target schedule | Replayed best-global-order witness |
|---|---|---|
| Delivery arrays, singleton entry to rank-nine exit | `85H1 + 17H2 + 19H3 + 20H4` | `101H1 + 27H2 + 24H3 + 28H4 + 11H5 + 4H6 + 2H7 + H8` |
| Delivery-array rank mass | **256** | **440** |
| Targets, zero entry to final hyperplane | `416H1 + 12H2 + 24H3 + 32H4 + 24H5 + 12H6` | same |
| Target rank mass | **832** | **832** |
| Scalar centre reads | **416**, coefficients `D[t,k]` | same |

The new delivery subtotal is smaller **componentwise**: its saved histogram
is `{1:16, 2:10, 3:5, 4:8, 5:11, 6:4, 7:2, 8:1}`. Therefore its tail cost is
strictly smaller for every positive rank-cost function, not just at a sampled
exponent. The comparator is one explicit, independently reconstructed
55-chain cover of the predecessor's best global order. We do **not** claim
that its tail histogram minimizes the moment among all global-order covers.
The predecessor's exhaustive 40,320-order minimum is credited, not rerun;
its 55-chain witness and its single-cut 19-chains-per-centre control are
reproduced here.

`RESULT.json` additionally gives certified rational intervals for the
normalized child subtotal `sum n_r (r/73)^(1-a)` at `a=0`,
`a=3351/2000000`, and `a=1/99`, using the pinned interval arithmetic engine
from `complex-local-word-ceiling`. There is **no role denominator W** in
this subtotal. The incumbent coverage-law ceiling is not applied to this
unfinished, changed interface.

### What is not free or implemented

The eight original gather-to-survivor drops still have rank charge 56. The
24 additional supplied centre values require a legal formation mechanism.
An ordinary addition into an arbitrary dirty helper produces `centre+dirty`,
not the boundary value required above. The verifier injects one independent
dirty symbol into **every** supplied copy in turn; all 32 contaminations
have a nonzero target response. Thus arbitrary dirty-copy formation or
cleanup cannot be silently omitted.

A completed construction would have to charge, and prove compatibility of,

```
C_complete = C_gather + C_original_drops + C_form_24_exact_copies
           + C_delivery_tails + C_target_tails + C_416_scalar_reads
           + C_restore + C_side_corrections + C_hosting_and_precision.
```

Only the two tail profiles, the exact scalar read map, and the original
rank-seven drop geometry are established here. Source formation, dirty
lifetime restoration, phase/frame compatibility with the side corrections,
whole-call hosting, precision/tape work, and the all-size recursive interface
remain unresolved. The original 5%-above-selected complete-profile gate of
the chooser card is **not passed**. This is an explicitly declared changed-scope
result on a central missing delivery lemma, not a supplier improvement or
an updated frontier.

PR1125's separate budget warning is unchanged: two extra ranks per call
already exceed its T37/T16 P104 knob budgets **if the remaining paid moment
retains or exceeds that knob profile**. Its theorem does not establish that
cost premise for every new word. Our 32-carrier witness does not evade the
at-most-26-path screen or discharge the remaining-cost premise; it only
attains the previously unconstructed monotone path threshold.

## Reproduce and evidence

From the repository root, CPython 3.12, standard library only:

```sh
uv run --python 3.12 --no-project python -I -O -B research/p104-target-order-delivery/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/p104-target-order-delivery
```

Expected verifier marker:

```
PASS_P104_TARGET_ORDER_DELIVERY chains=32 extra_arrays=24 reads=416 lower_bound=32 controls=8 no_new_kappa
```

Default replay does not modify files; `--write` regenerates only this
package's `RESULT.json`. Assertions are not used for acceptance. Negative
controls reject an omitted read, duplicate read, omitted chain, wrong
survivor frame, reversed chain, broken target path, and decoder coefficient
mutation. The eighth control verifies nonzero dirty sensitivity for all
copies. Positive controls rederive the exact decoder, 55-chain best-order
witness, and eight single-cut chain numbers equal to 19.

Actual focused checks ran on **CPython 3.12.12**: exact receipt generation,
isolated optimized replay, and the registered package replay passed with
the markers above and `PASS_REGISTERED_RESEARCH_PACKAGE`. The planning
control printed `PASS_COMPLEX_LOCAL_WORD_CEILING`. No full selected-supplier
cold replay, native compiler, hosted CI or proof assistant was run.

The witness was discovered with OR-Tools CP-SAT 9.14.6206, one worker and
search tie-break seed 3. An initial 180-second unrestricted optimization
found 70 chains, not an improvement. Adding the proved rank-four lower
bound and asking for its exact attainment produced the 32-chain certificate.
No solver optimality report or floating-point calculation is used for
acceptance; neither OR-Tools nor its dependencies are needed for replay.
The universal statement is the written antichain proof plus this exact
finite attainment, not a claim inferred from an unsuccessful search.

## Provenance, novelty and credit

* Exact baseline: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
* Independent chooser seed: `4e1451a884a6979cb599a332ccc7ad40`, track
  `complex-mechanisms`; original card `complex-rank-shape-decoder`.
  The full original draw is in `SELECTION.json`; `TASK.json` declares the
  changed scope before synthesis.
* Precise claim:
  [round-two discussion 1929](https://github.com/CrocSwap/integer-mult-bounds/discussions/1929#discussioncomment-18925825).
* Ali Romman / **PR1125**, head
  `9f7c0679d64bab954b7161d8586dc626a59b92ee`: the 32-path terminal-read
  lower bound, uniform cube-support classification across 7168 decoders,
  and the paid-downward-move and retained-cost budget qualifications.
  Its README and proof are pinned inputs. It explicitly does not construct
  a schedule at 32 paths; that constructive gap is the new contribution.
  Its substantial OpenAI Codex attribution is retained.
* Josie Elliston / **PR1071**, head
  `ce9531beba1ce115fdcdc44925ded995a29b8bac`: the pinned P104 fixture,
  survivor geometry, single-cut and global-order delivery bounds, and the
  explicit open per-target question. Its research credited substantial
  Claude Opus 5.5 assistance; that attribution is retained.
* themilkman216 / **PR968**, head
  `6a99e7240b961ac5e115ae6aa0301ec7c4a45d77`: frame-pair theorem and
  exact eight-term decoder floor. DreamingOfClouds / **PR717**, live head
  `4a97676294f9fa413b65986e9984fddeda71e4cc`: the decoder model, P104
  witnesses, and prior pricing questions. DreamingOfClouds / PR446 and
  PR595 supply the inherited copied-information model. GamingPuzzled /
  Joel Pulikkan / PR620 supplies the coordinate decoder lineage.
* Douglas Colkitt / **PR1240** supplies the pinned exact interval calculator
  and the selected-word planning control; no ceiling outside its hypotheses
  is inferred here. The selected PR1094/PR589 constructions are unchanged.
* Shared cached overlap coverage contained 579 open PRs and 547 discussion
  records with complete pagination at 2026-10-14 14:10/14:11 UTC. The initial
  narrow searches missed merged PR1125. A final live `P104` search over PR
  titles and bodies found it; its exact head, README and proof were read
  before publication, and the scope/claim was corrected to constructive
  attainment. Live heads of PR1071, PR968 and PR717 were also rechecked.
  This is a metadata overlap screen, not an exhaustive code-diff novelty
  certificate.
  The final targeted offline search used the parent's refreshed cache:
  584 open PRs at 14:27:47 UTC and 565 discussion records at 14:29:09 UTC,
  both with complete pagination; it recovered PR1125's local package.

Prepared for Adam Gall with substantial OpenAI Codex (gpt-6-astra)
assistance in research, proof, implementation and writing. Apache-2.0.
No independent human proof review or formal proof-assistant verification
is claimed. No frozen predecessor, selected record, or shared index changes.

## Open next questions

1. **Can the 24 extra exact copies be formed and restored cheaply on arbitrary
   dirty arrays?** This determines whether the chain reduction survives a real
   invoice. Start by compiling one of the rank-four-ending chains, including
   its dirty-state correction and full cleanup. The blocker is an admitted
   P104 copy/restoration interface, not the path-cover combinatorics.
2. **Can side corrections coexist with the layer-by-layer target order?**
   The schedule proves only the centre delivery. The first experiment is to
   splice its actual 416 reads into a fully specified P104 correction word
   and check each physical frame and chronological dependency. No such
   complete correction word is supplied here.
3. **What is the minimum complete tail moment at 32 chains?** The chain count
   is sharp, but our profile is only an attaining witness. Optimize chain
   assignments with exact rank costs while retaining the same support paths;
   any result still needs the physical contracts above before supplier use.
