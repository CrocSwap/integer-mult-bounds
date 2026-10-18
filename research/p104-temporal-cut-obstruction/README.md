# A sharp temporal information cut for the native P104 channel

**Scoped obstruction: the frozen P104 frame schedule carries at most eight
independent source ports to its 104 targets, even after arbitrary same-frame
linear redesign. Its existing `G/2` channel attains this bound.** Completing
identity transfer requires a changed information-access schedule.

There is also a cost obstruction for a precise completion class: retain the
original events and storage lifetimes, and insert paid frame excursions that
return every register to its original frame before the next original event.
Any such completion needs at least **96 additional positive-rank transports**.
Under the retained fully hosted, four-pair, nine-stage coverage contract, even
their minimum mass makes the zero-saving moment at least **7659/7592 > 1**.
No packing of idle children can repair this deficit within that contract.

This answers the `p104-side-correction` card for these two classes. It is not a
general P104 impossibility theorem, an admitted supplier, or a new kappa.
Persistent frame changes across checkpoints, retiming, new storage and changed
coverage remain open. The selected result is unchanged.

## Exact object and contribution

The input is Rohan Arun's [PR1972](https://github.com/CrocSwap/integer-mult-bounds/pull/1972)
word at `fd82d172f46933fd253c2c6de4bd5eaff5429cfd`, retained byte-for-byte in
[PR1991's native package](../p104-native-channel/README.md), by Chafik Boukhalfa,
head `6e222517e182e98499239bc9a4009f540e1c5520`.
It has 4,058 events, 104 sources, 104 targets, 72 arbitrary dirty helpers and
eight separate lifetimes of one private copy register `C`.

The predecessor proves the existing word's endpoint. This package proves an
upper bound for **every linear program on its chronological common-frame
access graph**, allowing substantially more communication than the published
scalar word. It also derives a conditional cost lower bound for restoring
excursions inserted into that graph. These are new implications rather than
another native compilation or another endpoint audit.

The independent forward and backward graph checks identify exactly these
zero-based event indices as a separating cut:

```text
2463 2472 2479 2487 2495 2503 2510 2518
```

Each is a private `C` descent from a dimension-eight frame to dimension one,
charged native rank seven. Each edge has **information capacity one register**;
the information-capacity count eight and the native invoice COPY56 are different
quantities. The cut disconnects every source from every final target. Restoring
any one edge restores paths from 52 sources; restoring all eight restores paths
from all 104. Reachability counts do not themselves assert achievable ranks.

## 1. Temporal-cut theorem

At every cut before and after each frozen event, group all live registers by
their actual binary subspace, independently of the supplied basis. Grant
arbitrary linear mixing within every group. Retain the frozen transport order,
entry/exit frames, private allocations and discards. A transport carries the
register's information between two consecutive cuts; allocation starts with
no source information, and discard ends that lifetime. Literal additions and
copies are contained in the common-frame mixing relaxation.

The executable certificate deletes the eight edges above and propagates source
reachability through **every** common-frame group at **all 4,059 cuts**. None of
the targets is reached. A separately implemented reverse propagation starts
from all targets and reaches no source. This is a finite graph-cut certificate,
not a bounded search for favorable scalar coefficients.

**Cut lemma.** Fix all other inputs and let each register hold a vector of
dimension `D`. If `c` through-register edges separate the source inputs from the
target outputs of a linear chronological circuit, its source-to-target linear
map has rank at most `cD`.

To prove it, expose the `c` values crossing the deleted edges as separate
`D`-dimensional signals. Every output depends linearly on those signals and
on source-independent data: otherwise its dependency graph would contain an
uncut source-to-output path. Thus the source-to-output map factors through a
space of dimension at most `cD`. Same-cut mixing can be regarded as one linear
map per common-frame group; there is no requirement to execute cyclic graph
edges simultaneously. Giving that group arbitrary mixing only enlarges the
admissible class.

The certificate therefore bounds the P104 transfer rank by **8D**, even if
source/helper restoration is waived and all scalar coefficients are changed.
For scalar logical rows this is rank at most eight. For the finite native
nine-coordinate address space, `D=512`. Invertible intrinsic endpoint adapters
do not change the rank. This linear-algebra statement for arbitrary finite `D`
does not establish an all-size implementation or compiler theorem.

**Sharpness.** Reconstruct the 104 retained E8 root lines from doubled integer
coordinates, and write `A` for the matrix of ordinary root rows. Direct integer
arithmetic gives `A^t A = 26 I_8`, hence `G=AA^t` has rank eight and
`G^2=26G`. An independent rational replay of all 280 input columns confirms
the predecessor endpoint `y <- y+(G/2)x`, including dirty-helper restoration.
Its native realization is inherited from PR1991. It attains rank `8D`, so the
cut bound is sharp.

The desired endpoint `y <- y+x` has rank `104D` from source to target.
Consequently no coefficient changes, extra same-frame additions, helper/target
mixing or same-frame linear processing on this frozen timeline can complete it.
This conclusion does not follow merely from the existing decoder's rank eight;
the saturated temporal graph is what excludes other decoder choices.

For an explicit lost-information witness, `z_t=26 e_t-G e_t` satisfies
`G z_t=0` and `(I-G/2)z_t=z_t`, with coordinate `t` equal to 24. The checker
verifies all 104 such witnesses. It also checks

```text
(I-G/2)^(-1) = I-G/24.
```

Thus the correction itself has rank 104, despite its zero diagonal.

## 2. Restoring excursions need at least 96 added transports

The following additional hypotheses are essential:

1. Every original event, its frame endpoints and its order are retained.
2. Extra blocks may be inserted at any frozen cut, but **all live registers
   return to that cut's prescribed frames before the next original event**.
3. No additional storage lifetimes or external input channels are introduced.
4. Added frame changes are positive-rank nested transports, charged at least
   one each. No free cross-frame operation is introduced. Original paid
   transports are not removed, fused away or given an accounting credit.

Within these rules, scalar operations may be redesigned arbitrarily. Let `K`
be the number of added transport occurrences, summed over all insertion blocks.
Delete all `K` of these edges and the original eight cut edges. Every surviving
path through an inserted block stays in a single frame. Its entry and exit
registers therefore belonged to the same frozen common-frame group, so that
path contracts to an edge already granted in the original saturated graph.
The `8+K` edges consequently separate source and target in the augmented graph.

By the cut lemma, identity transfer requires `104D <= (8+K)D`, so **K >= 96**.
Since each added positive transport costs at least one rank, the added rank
mass is at least 96. This is a necessary bound, not an assertion that a
96-transport completion exists or that the bound is sharp.

**Why the checkpoint restriction matters.** A register that stays in a changed
frame across original events can receive source data later and retain it until
a target becomes available. Its data path can avoid both the transport into
that frame and the eventual transport back. Such persistent buffers can also
stream multiple forms. Deleting the added transport edges does not prove the
same bound for that model. No general long-lived-detour lower bound is claimed.

## 3. Conditional complete-mass screen

Use the retained width-73, nine-stage, four-pair template with 104 ports and
all helpers hosted on the live data families. This gives `W=8*104=832` families
and `N=9` calls per replica. Assume the original coverage is charged as

```text
baseline paid mass = 72 W + 56 N,
```

and every added local transport contributes excess mass without reducing that
baseline. This is the explicitly stated application of the coverage model in
[the packing-ceiling package](../complex-local-word-ceiling/README.md), with
COPY56 in place of the selected word's COPY64. It is an optimistic retained
hosting contract, **not** a claim to have constructed chronological owners for
P104. An alternative template or an accounting cancellation requires a new bill.

The exact integer calculation is:

| Quantity per replica | Value |
|---|---:|
| Baseline mass `72*832+56*9` | 60,408 |
| Available mass `73*832` | 60,736 |
| Baseline headroom | 328 |
| Minimum added mass `96*9` | 864 |
| Minimum completed mass | 61,272 |

There are only `328/9` spare ranks per call. At saving zero the normalized
moment is at least `61272/60736 = 7659/7592 > 1`. For every nonnegative saving
`a` and admissible child rank `0 < r <= 73`,
`(r/73)^(1-a) >= r/73`; therefore its moment is also greater than one.
The class fails before any exponential/logarithm approximation, regardless of
idle packing or how the extra mass is grouped into children. Positive overhead
charges can only worsen this favorable screen.

Do not put the added transports into a fixed-coverage calculator while silently
subtracting their mass from the idle remainder. These restoring excursions
retain the original paid word and add excess; they do not replace idle work.
For example, **208 added ranks per call** would give
`(60408+9*208)/60736 = 7785/7592 > 1` already at saving zero under this contract.
A favorable screen obtained by retaining COPY56 as the only excess charge while
increasing the local profile is pricing a different model: it implicitly
credits an equal reduction in idle mass. Such a reduction needs a construction
and proof; it does not follow from the completed local profile alone.

## Reproduce and inspect

Standard-library Python 3.10 or later; registered CI uses Python 3.12:

```sh
python3 -I -O -B research/p104-temporal-cut-obstruction/verify.py
python3 scripts/research_package.py --package research/p104-temporal-cut-obstruction --check-only
python3.12 scripts/research_package.py --package research/p104-temporal-cut-obstruction
```

The first command compares the complete recomputed receipt with
[RESULT.json](RESULT.json), authenticates all external inputs and writes nothing.
`--write` deliberately regenerates only this package's receipt. No network,
Git or predecessor producer/compiler is used by the direct replay. The generic
metadata check separately requires the pinned Git provenance.

Checks include actual frame subspaces, all 4,058 chronological operations,
private lifetimes, forward and independently implemented backward cuts, the
intact-graph positive control, all eight single-edge restorations, exact Gram
identities, 280-column dirty scalar replay and the rational budget. Mutations
remove dirty compensation, falsify a transport rank, falsify an endpoint and
insert a real two-transport source-to-target bridge; each is rejected for its
intended mathematical reason. The bridge control demonstrates that new paid
access really can invalidate the original eight-edge cut.

Native Clifford recipes, chronological owner assignment, precision/tape bounds,
all-size admission, outer transfer and the selected full cold replay are not
rerun or newly established here. None is needed to certify this finite access
obstruction. This is a written proof with finite exact certificates, not a
proof-assistant formalization.

## Open next questions

- **Can a persistent changed-frame schedule deliver the missing information
  within the full budget?** This is the direct escape from the theorem. Start
  with one source/helper kept at a useful frame across a frozen checkpoint and
  re-run the saturated reachability test. Then count total added and displaced
  transports and test arbitrary dirty-state restoration. A new graph, full
  invoice and physical realization are the blockers.
- **Can retiming replace existing transport work rather than adding restoring
  excursions?** Interleave correction reads with gather/delivery before sources
  finish. The first useful artifact is a changed timeline with a larger
  source-to-target cut and an explicit accounting of removed versus added
  children. The frozen proof cannot price these cancellations automatically.
- **Does a different global coverage contract admit a completed changed word?**
  Recompute families per call, unpaid coordinates, private-copy costs and all
  idle children before claiming a moment gain. A legal completed local word and
  chronological hosting remain prerequisites.

Structured scopes, exact provenance and overlap freshness are recorded in
[TASK.json](TASK.json) and [SOURCES.json](SOURCES.json).

## Credit and overlap

Rohan Arun / PR1972 owns the scalar/frame channel; Chafik Boukhalfa / PR1991
owns its concrete native realization; Adam Gall / PR1940
(`a9b7dfe2809092a9a4c90784d12bb60061e995e8`) owns the delivery schedule. The
P104 fixture and decoder come from Josie Elliston / PR1071 and Ali Romman /
PR1125, with the retained PR968/717/446/595/620 lineage. The global coverage
identity is PR1012's; the packing-ceiling exposition is Douglas Colkitt's.
No predecessor files are modified or copied into a new package.

At entry, [the concurrent final-query-cut claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18931651)
proposed a concrete side correction using added target excursions. Its
[terminal-cut update](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18931708)
and [a second terminal-cut claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18931718)
were also read before submission. This package does not construct or validate
those unpublished words. The 208-rank illustration above explains the complete
accounting condition that their favorable local-profile screens still need to
justify. The graph theorem and lower bound concern the broader precisely
defined classes above. Discussion claims remain provisional overlap evidence.

Prepared for David Arias with substantial OpenAI Codex assistance, including
separate mathematical derivations and independently written reverse checking.
Apache-2.0. No independent human review or literature-priority guarantee is
claimed.
