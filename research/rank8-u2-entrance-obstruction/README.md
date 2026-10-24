# Monotone entrances miss the rank-8/u2 16-child cell

**Negative result. No new κ.** The selected conditional exponent stays
`60403/20000000` (`0.00302015`). This package does not touch that record.

The integer cell in ToikY's `research/lever-integer-twins` puts paid mass
5586 at `{8:698, 2:1}` on every call, with two unpaid coordinates and centre
charge 64. On nine calls its pooled idle is `{51:272, 46:1}`, and the moment
at `a = 1/98` still passes after 16 added rank-1 children and fails at 17.
That 16-child margin is a budget for a physical producer, not a producer.
The question left open by `research/rank8-u2-split-boundary` is whether any
literal local word has this paid profile. On the selected register file, no
monotone nested frame word of mass 5586 and rank at most 8 meets the moment
at all.

## Contract

Frames are subspaces of \(\mathbb{F}_2^9\). A monotone register chain climbs
from its pinned entrance to an exit inside the legal terminal, and the climb
ranks are positive integers summing to at most \(\dim(\mathrm{exit}) -
\dim(\mathrm{entrance})\). One chain therefore holds at most one part of size
8, because the room is at most 9. The selected local word fixes the entrances
and the register file:

| Registers | Count | Entrance | Maximum exit | Room |
|---|---:|---|---|---:|
| Sources | 112 | the port line, dimension 1 | FULL, dimension 9 | 8 |
| Targets | 112 | 0 | the port parity hyperplane, dimension 8 | 8 |
| Helpers with entrance 0 | 288 | 0 | FULL | 9 |
| Helpers with entrance 1 | 136 | dimension 1 | FULL | 8 |
| Helpers with entrance 4 | 32 | dimension 4 | FULL | 5 |
| Helpers with entrance 5 | 24 | dimension 5 | FULL | 4 |

There are 648 rooms of size at least 8, 32 of size 5 and 24 of size 4.
Raising a target exit from the parity hyperplane to FULL adds residual room
but no eighth rank-8 slot, and it does not change the histogram below.

## Result

The minimum-cost histogram of mass 5586 with parts at most 8 that fits these
rooms is

```text
{8:648, 5:32, 4:24, 1:146}.
```

Its nine-call moment at `a = 1/98`, with the optimal pooled idle
`{51:272, 46:1}`, has certified bounds strictly above 1. The ideal cell is
not among the feasible histograms: it needs 698 rank-8 children and the file
has 648 monotone slots. The same checker reproduces the published control on
`{8:698, 2:1}`: 16 added rank-1 children still pass and 17 fail.

A comparison that is not a monotone word grants each of the eight centre
registers three rank-8 steps (room 24 instead of 8 or 9). The cheapest
histogram in that larger model is `{8:664, 5:32, 4:24, 1:18}`. Its bare
pooled moment is below 1, and one added rank-1 child on the nine-call total
pushes it above 1. The 16-child margin is not available there either.

## Why this histogram is the monotone minimum

Let \(f(r) = (r/73)^{97/98}\) for \(r \ge 1\) and \(f(0) = 0\). The child cost
at \(a = 1/98\) is \(f(r)\). The pinned enclosures separate two strict
inequalities on \(\{1,\ldots,8\}\):

- merging: \(f(x) + f(y) > f(x+y)\) whenever \(x, y \ge 1\) and \(x+y \le 8\);
- transfer: \(f(x) + f(y) > f(x-1) + f(y+1)\) whenever \(1 \le x \le y\) and
  \(y+1 \le 8\), with \(f(0) = 0\) when \(x = 1\).

Every composition of 8 into at least two positive parts is therefore strictly
more expensive than one part of size 8. Any feasible assignment that uses
fewer than 648 eights still has at least 8 units of mass in smaller parts and
a large register that is not holding an 8. Gathering those units into one 8
strictly lowers the cost. So every minimum uses exactly 648 eights, and the
remaining mass is 402.

That remainder has to sit in the 32 rooms of size 5, the 24 rooms of size 4,
and the single leftover slot of a room that already holds an 8. No leftover
slot has size greater than 1, and a room of size 5 or 4 cannot hold a 7.
Filling the size-5 and size-4 rooms with one part each, then placing the last
146 units as ones, is the unique minimum: splitting a 5 or a 4 raises the
cost by the merge inequality. The resulting moment is already above 1, before
any additive rank-1 surcharge and before integer idle is replaced by anything
worse than the pooled histogram.

## What was not shown

Non-monotone paths, extra registers, changed entrances and a different
template are outside this certificate. Unknown restoration, precision and
consumer costs are not zero. The three-step centre comparison is only an
upper model on the same eight centre indices; it is not a scalar word. The
obstruction is about this entrance file and the older \(u = 2\) planning cell.
It is not a statement about the #4470 productive-helper invoice, and it does
not move the selected exponent.

The family split in `research/rank8-u2-split-boundary` still applies to the
ideal histogram. It does not create a 649th monotone rank-8 slot.

## Scope

Card `complex-new-helper-inventory`, priority revision 7, base
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`. Scope status is **refined**. The
card asks for a new inventory with a favorable full bill. The bounded question
here is the literal rank-at-most-8 producer inside the 16-child slack. The
answer on these entrances is that the monotone minimum already fails
\(a = 1/98\).

Ordered eligible list for session r31, rebuilt on 2026-10-23 against
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`. The order is the one recorded in
`research/f2-six-difference-basis`: open handoffs from the 19 October index,
then priority-table rows whose stated next decision is still open, then
catalogue cards that are not already one of those rows. Dropped before the
cut: work this account already delivered, questions closed on current main,
questions covered by an open pull request, and topics already on a fork
`cursor/*` branch.

1. Consumer of `(w, q, v_N)` (discussion comment 19030045), distinct from the
   encoded-exit and `(N-P)⊗M` consumers.
2. Fresh T385 wrapper completion (comment 19030047), distinct from the reverse
   coefficient and from the merged compiler integration.
3. Six-tape head-move bill for the `L546` addition (comment 19030049),
   distinct from the F0 magnitude ledger and from #4162.
4. `BIT.md` weighted-leaf and fixed-tape induction. The `2^{-4p}` sentence,
   the row-field pad, the uniform evaluator constant and the shared-arena axis
   are already delivered.
5. Four-provider ordinary/outer rebind. The idle-cost block is recorded; the
   four-id rebind is not.
6. Matched park/restore bill for the #4166 caller. Open #4167 does not price
   that comparison.
7. R437 fixed-tape and parking bill. The reverse coefficient is excluded.
8. `#4091` model equivalence on the later 1090-call fill.
9. This package.

The retiming handoff (comment 19030053) stays dropped because #4122, #4128 and
open #4567 already address it. `p104-side-correction` is not a separate row:
item 1 is that consumer, and the slot, chart, encoding and fiber gaps are
certified. `formal-interface-lemma`, `bit-helper-contract`,
`bit-new-register-model`, `complex-rank-shape-decoder`, `centre-path-sharing`,
`connector-alphabet-change`, and the stock, census, replay, packing and
scalar-itinerary cards stay dropped for the same reasons already recorded on
the difference-basis package, plus this account's later deliveries through
#4651.

This is open question 2 of `research/rank8-u2-split-boundary`. Question 1 of
that package, the census of family splits that still pass 16 extra rank-1
children, is a different refinement of #4151 and is not answered here.
`research/rank8-u2-plane-port-slack` and `research/selected-k8-child-rank-bound`
likewise leave the literal producer open. A cached overlap search on
2026-10-23 (307 open pull requests, 4479 discussion records) did not find
another note stating the histogram `{8:648, 5:32, 4:24, 1:146}`. Same-day
fork branches for the L546 six-tape bill, the R437 parent blank-return, the
shared chart-1 centre visit, the SOURCE87 fibre count and the #4091 1090-call
ceiling price other rows of this list.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B research/rank8-u2-entrance-obstruction/verify.py
python3 -B scripts/research_package.py --package research/rank8-u2-entrance-obstruction
```

Expected line:

```text
PASS_RANK8_U2_ENTRANCE_OBSTRUCTION slots=648 monotone=GT/0 centre3=LT/0/GT/1 ideal=LT/16/GT/17 no_new_kappa
```

The checker hashes the word gzip, the decompressed word and `ceiling.py`,
rebuilds the 704 entrance rooms, packs both histograms, and separates every
merge and transfer inequality on ranks `1..8` by the pinned outward
enclosures. Not run: Lean, Docker, the selected cold replay, and any search
for a non-monotone scalar word.

## Open next questions

1. Can one centre register legally emit three rank-8 steps without an added
   rank-1 child? The arithmetic room of that comparison is zero: the bare
   moment passes and one aggregate rank-1 child fails. A legal trace would
   still need a changed path law. The first step is one explicit up, down, up
   frame trace and its own paid histogram. The standing monotone contract is
   the blocker.
2. Do the #4470 productive-helper frames have at least as many monotone
   rank-8 slots as that invoice demands? This certificate does not read that
   word. The first step is the same entrance count on the #4470 complex
   frames, and the blocker is that the two templates must not be mixed.

## Credit

The 16/17 integer boundary and the cell `{8:698, 2:1}` are ToikY's
`research/lever-integer-twins`, following Nick Petalas's PR #3874. The
entrance fields and the \(\mathbb{F}_2^9\) frame contract are the selected k8
word in `research/r480-owner-optimum`, as read by the frame-ceiling line
(PR #1671, Gareth Davidson, using navinor's frame method). The child-cost
enclosures are Douglas Colkitt's `research/complex-local-word-ceiling`, with
Claude assistance. The coverage identity is PR #1012. The split dependence of
the ideal slack is `research/rank8-u2-split-boundary`; this note does not
recompute those three family splits. The plane-port screen that already misses
the same slack is `research/rank8-u2-plane-port-slack`.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
