# A scoped one-bank ceiling for PR4929's coded-port adapter

PR4929 removes eight rank-8 native children while retaining an autonomous
632-input supplier, but changes its main cross-transfer to an invertible
112-port code. This package identifies the actual physical recovery adapter
and proves that **a standalone single parallel Gaussian bank needs at least
112 rank-2 channels**. An H1-only bank cannot recover the uncoded interface.
The resulting optimistic two-call tariff already loses over
`C in [.0030217758,.0034]`. No complete caller or improved κ is supplied.

The producer is Dugongue's #4929, exact head
`361f5d4100640177d6a983dd2f336021c75bfd5e`; archival merging does not certify
its mathematics. Its all 632-input producer proof is inherited, not replayed
here. The native word is byte-identical to frozen #4610: compressed hash `7679daa4`,
decompressed hash `cfcd36b4`. [ORIGINS.json](ORIGINS.json) pins the full hashes,
Git blobs, commits and original paths for every vendored input.

## Result and exact boundary

Let U be the 112 actual distinct rank-1 X entrance frames. X exits share a
common full frame T, while Y exits are distinct rank-8 frames V_i. The source
main is `diag(T,V) Sy(A) diag(U*,I)`, with

    A^2+12A=13I,    Aii=0,
    A^-1=(A+12I)/13.

Forward recovery of the original uncoded offer needs entrance
`K=U A^-1 U*` and scalar exit A on X. Raw-dual recovery needs entrance
`bar(U) A^T bar(U)*` and scalar exit `A^(-T)` on X. Helpers are untouched.
The full-exit scalar maps have zero recursive Gaussian grade, with finite
ordinary arithmetic and storage still charged.

All 5824 supported off-diagonal transports `U_i U_j*` have actual Fourier
grade 2. Consequently `pi2(K)=U A U*/13` is invertible. The self-contained
[proof](PROOF.md) gives the one-bank rank obstruction over the full
phase-quotiented finite Clifford algebra, including rectangular free
monomial controls, clean buffers and a free identity bypass. It uses
sufficiently-large-width tensor faithfulness, not a width-1 matrix argument.
The scaled dyadic matrix 13K has the same grade requirement; denominator 13
is not used as a universal obstruction.

The naive decode/mix/restore route has two banks of 112 H1. One rank-2 bank
requires 112 H2. Even granting an unrealized target `224 H17+2H`, where every
one of 816 inherited helper jobs is retained once, the funded-C margins are:

| Added recursive bill | Exact outward margin at C=.0030217758 |
|---|---:|
| None; endpoint unproved |`[166.262158203082210620506138658847,166.262158203082210620506138658848]`|
|112 H1; not an implementation of K |`[54.262158203082210620506138658847,54.262158203082210620506138658848]`|
|224 H1; naive recursive bill |`[-57.737841796917789379493861341153,-57.737841796917789379493861341152]`|
|112 H2; necessary in the one-bank model |`[-57.269156882594712940928576503039,-57.269156882594712940928576503038]`|

Exact rational intervals, the upper-C endpoint and monotonic sign arguments
are in [RESULT.json](RESULT.json). These are complete stated recursive
relaxations; finite scalar/precision/stock/outer costs are not admitted.

## Reproduce

Python 3.12 or later, standard library only, from repository root:

```sh
python3 -I -W error -B research/coded-port-adapter-ceiling/verify.py
python3 -I -O -W error -B research/coded-port-adapter-ceiling/verify.py
python3 -B scripts/research_package.py --package research/coded-port-adapter-ceiling
```

Direct checks are read-only and Git-free after export. They authenticate the
vendored bytes before executing the exact Clifford or interval libraries,
verify the code inverse and all 5824 actual supported grades, recount the
changed Gaussian/precompensation profiles, recompute price intervals, and
reject semantic corruptions of grade, diagonal and matrix inverse/polynomial.
No producer 632 replay, Lean, native amplitude campaign, compiler or outer
replay is part of this package. [VALIDATION.md](VALIDATION.md) records actual
runs; [BUDGET.md](BUDGET.md) separates proved costs from open admission.

## Scope and overlap

This is a changed `supplier-boundary-audit` task, assigned specifically to
#4929 after the catalogue was written. #4929 supplies the producer and code;
we supply its physical adapter and a one-parallel-bank ceiling. #4694/#4698
supply the centre-free/coupled antecedents. #4712's dirty-helper and 120-head
query failures remain relevant; code rank-8 does not grant eight query heads.
#4920/#4928 have different two-FULL projection models and do not certify
this new coded caller. No repetitive seed or family search was run.

The theorem excludes multiple chronological banks, native absorption,
prefix access, approximate/border endpoints, noncolumnwise address grammar,
extra nonmonomial operations and direct coded consumers. It makes no claim
that a useful producer cannot exploit the code in another way.

## Open next questions

The priority question is a **collective coded three-original-bank consumer**
using one distinct original helper owner through both calls. Across 112 ports
the optimistic target is `336 H17+2H-224 H9` on 928 owners. It has a positive
raw relaxation, but its third H17 endpoint is unproved. The known #4698
pattern gives H16 on that third bank and loses even with free embedding.
Aii=0 and cross-port unequal headers prevent importing that one-port word.

The smallest useful step is an exact noncommutative, source-bound bypass or
other operator identity producing the missing third central factor while
preserving every arbitrary original input and all 592 unselected helper
jobs. It must include A and all native/header conjugations, and price any
extra query. Another 112 H1 already exceeds the optimistic allowance. Root's
ongoing prefix/consumer work owns this constructive question; no successful
bypass is claimed here.

A second question is whether the actual frozen 18-FULL caller can amortize
code boundaries through a literal chronological cancellation. Test one pinned
interstage boundary with its physical normalizers before expansion; do not
commute A through port-dependent Q or D by assumption. The full replacement
would have paid delta `-144H8+K_added` only after its original endpoint and
all added bills are independently established.

## Credit

Credit Dugongue #4929, Cinna Davis/1337isnot1337 #4694/#4698, Cao Yifan/intqwq
#4610, zxv's exact higher-moment/Clifford/compiler work, Jacob Alan Sussman's
mixed-target lineage and every retained upstream contributor. The parent
agent derived the one-bank rank argument and exact price screen; the
source/interface agent independently bound the actual headers, all supported
grades and raw-dual adapters. Prepared for Chris R/Clear1nsight with substantial
OpenAI Codex assistance. Apache-2.0; [ATTRIBUTION.md](ATTRIBUTION.md) and the
retained source notices distinguish source authorship, local checks and
unclaimed independent human/formal-kernel acceptance.
