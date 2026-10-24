# Rank-(8, 8) copy bill for every term count

**Negative result for one algebraic branch. No new κ.**

On the 120 real E8 root lines, every factorization
\(\sum_k a_k b_k^{\mathsf T}=2I_8\) whose factors lie in \(\mathbb R^8\) has
copy cost exactly \(9t\) after zero factors are deleted. Thus \(t\ge 8\), the
eight-term frame costs 72, and nine or more terms cost at least 81. After
deleting any set of at most 13 lines, the same identity costs at least
\(9t-p\). On a coordinate-frame puncture, the explicit nine-term split costs
79, which is above the floor \(73\) and above the eight-term floor \(64\).

The hypothesis is the factor rank. A one-coordinate excursion raises the left
factor rank to 9, preserves the Gram identity, and drops a term from 9 to 8
(total 80). The published ten-term rank-(9, 9) example in
`research/ten-term-copy-cost` costs 72 and is outside this theorem.

PR1212's Theorem 1 identifies every real rank-8 E-graph solution on P120 and
on a frame complement with a diagonal gauge of \(2G\). Rank-(8, 8)
factorizations of that matrix inherit the same supports and the same floors.
That is the root-span branch of the nine-or-more-term gap in
[the decoder scope map](../../docs/research/complex-decoder-scope-map.md).
Factor rank above 8, E-graph rank above 8, and complex coefficients stay open.
The argument is in [PROOF.md](PROOF.md). The selected frontier is unchanged.

## Scope and evidence

Original card: `complex-rank-shape-decoder`. Scope **changed**, as recorded in
[TASK.json](TASK.json). The card asks for a block-climb profile that beats the
selected word. The scope map instead leaves the copy bill of nine or more
costly rank-8 terms undetermined. This package prices the branch in which both
factor matrices have rank 8, and it exhibits a rank-9 term whose cost drops
below 9 so the branch boundary is visible.

Base: `ff3cc58e370d0f678e529246f8c73e8094e18fcf`, priority revision 7.
Pins are in [SOURCES.json](SOURCES.json). The catalogue card and the selected
record are historical provenance. The verifier recomputes its geometry from
the standard library and does not import a predecessor package.

| Check | Role |
| --- | --- |
| 511 violator sizes, kernel spans, Cartan determinant 1 | Label and lattice setup |
| 383 dominant vectors of norm at most 128 | Replaces an uncomputed orbit list inside this norm bound |
| All 120 root complements, profile (1, 24, 25) | Self-line reductions |
| Frame, nine-term split, seven-term failure, mutated split | Exact identities and the 72 / 81 costs |
| Frame puncture of the split, odd deleted pair, self-line drop | Puncture savings |
| Rank-9 excursion of cost 80 | Shows the rank hypothesis is necessary |

These finite checks are the census and the witnesses. Theorems 3 and 4 in the
proof are written arguments from that census. They are not an enumeration of
all real factorizations. The Weyl-chamber transport is cited from Bourbaki VI §1 and is not recomputed. PR1212's gauge theorem is cited and is not
recomputed. No Lean, Docker, or frontier replay was run.

## Reproduce

From the repository root, CPython 3.12 and the standard library:

```sh
python3 -B research/nine-costly-rank8-copy-floor/verify.py
python3 scripts/research_package.py --package research/nine-costly-rank8-copy-floor
```

The verifier prints one `PASS` line per check and exits 0 on

```text
PASS_NINE_COSTLY_RANK8_COPY_FLOOR rank88_cost=9t p120_nine=81 p112_nine=79 excursion_rank9_cost=80 no_new_kappa
```

Direct `python3 -O` keeps the same checks, because failures are explicit
exceptions rather than assertions. Runtime is about one second. The command
writes nothing.

## Open next questions

1. Can a factorization of \(2G\) with a factor rank at least 9 cost less than
   72? Theorem 3 stops at rank 8, and the rank-9 excursion only drops one term
   to 8 (total 80). The ten-term rank-(9, 9) example meets 72 without going
   under it. Start from that example, or from the explicit excursion in
   `verify.py`, and either cancel enough further label mass to go under 72 or
   isolate a defect that restores the floor. Nothing in this package forbids
   the attempt; the missing tool is a normal form once a column leaves the
   root span.
2. Can a real E-graph solution of rank at least 9, on P120 or on a frame
   complement, have costly-term copy cost below 72 or 64? PR1212's Theorem 1
   does not describe those solutions, so the support identification used here
   does not apply. Start by writing one exact rank-9 solution of the E-graph
   equations and pricing its terms. The blocker is the absence of a gauge
   form, not a computation inside this package.

## Credit

The E-graph model and the eight-term copy problem come from DreamingOfClouds
(PR717). The eight-term all-pairs floor, the label pairing, and the violator
calculus come from themilkman216 (PR968). The rank-8 gauge form comes from
Brett Halligan / burntout76 (PR1212). The scope map that isolates the
nine-or-more-term gap was prepared by Arham Tahir, with the masked-rigidity
navigation update by starship-s. The contrasting ten-term rank-(9, 9) cost-72
example is the factorization recorded in `research/ten-term-copy-cost`
(conorholds' construction; package notes by jwr). Nick Petalas's
`research/e8-one-extra-direction` prices binary factorizations of the pairing
matrix and is a different field; it is not a premise here. Unpaidmoon's earlier
E8 label-rank and k8/u2 child-count notes bound child rank; they do not price
this Gram factorization.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent
human review or proof-assistant verification is claimed. New work is
Apache-2.0.
