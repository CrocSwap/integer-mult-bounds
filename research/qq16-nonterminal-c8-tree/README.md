# QQ16's first genuine nonterminal C8 band

**Scoped source-tree result, not a complete cost sign or new κ.** At the
historical #4177 root family `p=2^8500`, the first nonterminal removed C8
occurs at **λ=45**, not merely when its width exceeds 73. Precisely
**45≤λ≤72** gives one generation of selected-C children below each removed
C8, while every added C1 and every such grandchild is terminal.

That generation has **510,662 Γ selected child calls** per C8. Removing the
sixteen C8 calls per outer cover therefore removes **8,170,592 Γ² internal
parking pairs**. These are inside the removed complete C8 bodies, not the
already credited generic outer-call parking optimisation. A literal subtrace
alone contributes at least

```
(reads, writes, unit moves)
  >= (16,341,184, 40,852,960, 40,852,960) Γ² v,
```

where `v` is one complete C8 input bank's bit length. This is a lower bound on
one removed expense, **not a lower bound on the whole improvement**. Remaining
candidate costs and original nonchild/native costs prevent a sign conclusion.

## Exact boundary and proof

The predecessor's genuine descriptor family has

```
p = 2^8500, d = floor(sqrt(2^16949)), K = floor(d^(1/500)) = 126519,
G = 34006, H = dG, F = 14336 Γ,
Γ = 2^1296 product(j=1..36, 2^(2j)-1).
```

The actual source tests `w<73 OR w^1000<d` **before** dividing by 73. Exact
integer inequalities give `355^1000<d≤356^1000`. Hence C8 of width `8λ`
is nonterminal exactly from λ=45 in this neighbourhood. Write
`8λ=73q+δ`, with `0≤δ<73`. The source applies a δ-axis remainder leaf,
shifts `before` by `δK`, and then executes its complete selected program at
width `73q`. It does **not** repeat the global-height test after this shift.
At λ=45 the reached selected program has width 292, although a fresh width-292
call would be terminal. Pruning this reached program is an invalid shortcut.

Every selected child has width `rq`, where `r` belongs to the actual source
rank histogram below. Its maximum is attained at r=48. Thus the condition for
all grandchildren to be terminal is `48 floor(8λ/73)<356`. Combining the two
conditions gives exactly 45≤λ≤72. At λ=44 C8 is terminal; at λ=73 its rank-48
child has width 384 and is nonterminal. These adjacent witnesses make the band
sharp for this descriptor family. All added C1 widths in the band are below
73 and hence terminal. Ordinary/native internals are not selected-C children
and are not pronounced terminal by this argument.

The verifier independently rederives the source census from the authenticated
literal local words, all 482 global events and every idle-family suffix:

| Rank r | Occurrences per Γ |
| --- | ---: |
| 1 | 349604 |
| 2 | 60192 |
| 3 | 62585 |
| 4 | 20448 |
| 5 | 11808 |
| 7 | 7 |
| 8 | 1152 |
| 48 | 4866 |

Each local `climb`/`center` is bound to its directed native recipe. Idle
remainders are bound to the actual source family and residual axes, and each
is consumed exactly once. No prior verifier or receipt is imported. The
aggregate agrees with #4166's existing census; **the census itself is prior
work**. Its use for the first nonterminal removed-body tree is the new result.
The complete event-by-event census is retained in RESULT.json.

## Root entry, stock and physical volume

For each λ in the band, use the unchanged RootPlan construction with
`selected=q0+qF+qB+73λ`, where `q0=D ceil(log2 F)`,
`qF=ceil(2H/K)`, `qB=ceil(H/K)` and D is the actual coarse depth of d under
`w -> 48 floor(w/73)`. Exact arithmetic checks `selected≤d`, strict fast entry,
`d≤(73λ)^1000`, guard residues, and the complete root address rectangle.
These are descriptor/admission arithmetic, not production payload execution.
The source/numerical/native/hosting/long-record premises of #4166/#4177 remain
inherited; the selected result is unchanged.

Root rows are padded to a positive multiple of `F^D`. The outer selected node
consumes one F; a nonterminal C8 consumes one further F. D≥2 supplies both
positive divisions. Terminal grandchildren do not divide the stock again.
This explains exact divisions on the reached tree; it installs no smaller
root stock and does not replace the conservative all-root coarse envelope.
The giant `2^(q0K)` row count is kept symbolic, never allocated.

Let R be C8's incoming rows and let
`v=P R 2H_b c 2^b` be its whole physical input volume. The C8 remainder leaf
preserves b by moving δ active axes into `before`. A rank-r grandchild moves
`(73-r)q` active axes into `after`; it also preserves b. However its rows are
**R/F**, so each selected grandchild's volume is **v/F**, not v. Consequently

```
sum of all grandchild payload volumes = (510662 / 14336) v.
```

The owner factor Γ cancels here because F contains it. It does **not** cancel
from the count of parent parking operations. Spectator axes, prefixes,
coefficient width and coefficient count are retained throughout.

## What is priced, and what still needs a price

The B* boundary is pinned to the literal #4167 adapter retained inside
#4177's PR4172 archive. `RootLayer` first constructs the original `Machine`.
`install` saves that object as `original`, passes it as `native_child` to the
new external parent, and replaces only `root_layer.machine`. The parent's
`enter_child` calls `self.native_child.run`; the adapter does not patch that
original object's `run` or `enter_child`. The adoption flag controls the
parent's returned packet. Thus the C8 body and its descendants still use the
original embedded `Machine.enter_child`, even for B*. The verifier authenticates
both nested archives/member bytes and checks these literal bindings without
executing predecessor code. This is a callgraph argument, not an assumption
that an outer optimisation recursively applies.

The original `Machine.enter_child` parks all controller roles, including the
entire current bank; `BankPackets.gather` borrows that bank and preserves it.
Each successful selected child performs one park and one matching restore.
For every dense symbol of a parked role, the literal `Parking.park` loop alone
performs two reads, five writes and five unit moves. Rewinds, delimiters,
other roles and the entire restore contribute additional nonnegative work.
Since the current bank contains v bits, each pair has this conservative
componentwise lower bound `(2,5,5)v`. Multiplying by all `16·510662·Γ²` reached
pairs gives the bound at the top. This deliberately does not rederive or claim
#4167's stronger exact `56S+22r+11` full parking formula.

A complete source partition for **one** external C8 call is

```
E8 = entry/setup + remainder-leaf + nonchild-work + final-return/cleanup
     + sum(j over 510662 Γ selected children)
         [prepare_j + park_j + complete-leaf_j + restore/return_j].
```

The nonchild term includes all selected scalar, copy, monomial, native/Ordinary,
bank acquisition/publication and control work. Child bodies are terminal on
this band, but their argument geometry is v/F. Native internals remain inside
the appropriate nonchild term. The parent-call startup/return is outside the
sum; the remainder leaf precedes it. This partitions successful execution and
omits no source interval; most terms are **unpriced**.

Substitute this E8, once, in the inherited fair comparison

```
T_D - T_B = ΔN + Δshell + 14298088 Γ + 368 Γ E1 - 16 Γ E8.
```

For B* retain its additional, already proved return-adoption credit against D.
The internal parking term is already inside `16ΓE8`: adding it again would
double count. The known positive cost of this removed subtrace cannot be
compared with a lower bound on candidate work to infer a winning sign.
This is a useful new bill boundary; it is not a supplier or κ claim.

## Reproduction and scope

```
python3.12 -B scripts/research_package.py --package research/qq16-nonterminal-c8-tree
```

The standard-library verifier authenticates all inputs before data loading,
checks source control order, rederives all 482 event rows, proves the exact
integer descriptor band, and exercises ten rejecting controls. It runs in
normal and optimized modes without artifact writes. Only explicit `--write`
regenerates RESULT.json. No predecessor executable is imported.

This is an exact host certificate and written source argument. It does not
execute the enormous root, a complete physical C8, embedded parking at that
geometry, native internals or a full RootLayer. The positive action bound is
proved from the source loop, not timed. It does not claim full numerical or
independent human/formal-kernel acceptance.

Canonical investigation: [Discussion #4744](https://github.com/CrocSwap/integer-mult-bounds/discussions/4744).
Base main `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
Entry overlap: 506 open PRs, 3650 Discussion records and 5860 base local notes;
exact nonterminal queries found the predecessor's open question and audit
limits. Closed histories/code and unpublished work were not exhaustively searched.

## Open next questions

- Bound the candidate's **complete** unmatched nonchild/shell work above and
  the removed C8 work below at the same full geometry. The explicit internal
  parking floor is a starting term, not an affordability decision.
- Build a source-action evaluator for the reached one-generation C8, retaining
  monomial/native calls and before/after spectators. Small payloads require a
  separately labelled reduced binding; they cannot certify production cost.
- Beyond λ=72, derive the next selected-C generation with unchanged global d
  and fresh-row divisions. First recheck live work and a full favorable budget;
  deeper enumeration by itself is not a reason for another construction round.

Credit Chris R / Clear1nsight's #4166/#4167/#4172/#4177; Jose Manuel's original
physical C, Ordinary and Compact machinery; ywz65, Sagar Thakrar, Tekalign,
Ali Romman, Arham Tahir and the retained source/native lineage. Prior census,
root family, generic parking optimisation and terminal exclusion retain their
attribution. New source-tree audit and proof: JoyboyBrian, with substantial
OpenAI Codex assistance. Apache-2.0.
