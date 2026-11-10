# A smaller constant for the stopped complex recursion

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped all-size written proof with exact finite corroboration. Under the same
node, leaf, placement and child-volume premises as Brian / JoyboyBrian's
[PR4965](https://github.com/CrocSwap/integer-mult-bounds/pull/4965), the complete
stopped complex layer satisfies

    layer <= V Lambda h^(1-q)
      [1,209,000(c_N+c_L)+73^b c_L+2c_P].

The predecessor's sufficient adapter/remainder coefficient is reported above
7e27. The new coefficient is below 1,209,000. The leaf and placement terms
are unchanged. This is a theoretical constant improvement under a cited
recursion contract. No new kappa, runtime improvement or supplier admission
is claimed.

## Result and evidence

[PROOF.md](PROOF.md) gives a weighted-tree lemma. For critical exponent beta,
strict width contraction rho, stop width s and lower-order toll gap delta,

    sum_internal v e^(beta-delta)
      <= V h^beta s^(-delta)/(1-rho^delta).

Normalize a child's volume by its critical width potential. The resulting
weights have sum at most one, even when child volume exceeds parent volume.
Each realized path has a bounded geometric toll when summed backward from
its last internal node. For 0<delta<=1, concavity gives

    1/(1-rho^delta) <= 1/[delta(1-rho)].

For the cited recursion, beta=1-b, delta=a2-b and rho=48/73. The rational
coefficient 73/[25(a2-b)] lies strictly between 1,208,771 and 1,209,000.
The source's critical moment inequality is a cited premise; no predecessor
moment enclosure, source instance or scientific verifier is replayed.

The new standard-library verifier checks 1,536 floor-recursion trees by both
literal path expansion and a separately evaluated bottom-up recurrence.
It also checks 96 rational-square trees, where half-integer powers remain
exact. These visits enumerate 38,296 and 1,352 nodes respectively. Critical
and subcritical moments, unequal child widths, child-volume expansion and
leaf roots are included. Eleven controls reject invalid premises or exhibit
failure without a positive toll gap, critical mass or width contraction.
The written proof establishes the universal result; finite cases corroborate
only their declared domains.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/stopped-tree-contraction-constant/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/stopped-tree-contraction-constant/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/stopped-tree-contraction-constant
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/stopped-tree-contraction-constant --check-source-history
```

Another machine can substitute its CPython 3.12 path. The direct command also
works in a Git-free copy of these six files and writes nothing. It emits
`PASS_STOPPED_TREE_CONTRACTION_CONSTANT` in a generated JSON receipt with
exact counts, the rational coefficient and SHA256 hashes of all six files.
No receipt is handwritten. The registered runner executes warning-strict
normal and optimized checks. Explicit guards remain active under optimization.

## Sources, scope and credit

Scientific base is canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected
PR6030. [SOURCES.json](SOURCES.json) binds the predecessor proof and README,
the original card and selected record as historical provenance. PR4965's
retained head is `9e00ff1f7baa8352339f36277389cb1f06a5a58a`. No predecessor
executable is imported. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362923)
records the proposed result. The uniform-transfer-audit card is explicitly
changed to this quantitative analytical side result; no selected framework
assumption is discharged.

Main README and merged/all-state PR searches, recent account work, local
reservations and live Discussion claims were checked. The overlap snapshot
covered 407 open PRs and 6,360 Discussion records with complete remote
pagination. Sparse local notes were incomplete, so relevant source notes
were also read directly from canonical main. Neither that coverage nor a
no-match result proves absence of unpublished overlap.

Credit Brian / JoyboyBrian for PR4965's recurrence and old cost theorem;
Cinna Davis for PR4100 and PR4088's mixed construction and histogram; Jose
Manuel / jmbarrancoml for PR4178's height context; Matarener for PR4424's
cover/stock analysis; unpaidmoon for PR4375's whole-child versus factorwise
distinction; and the retained native/compiler/outer lineage. Weighted path
probabilities, geometric summation and concavity are classical. No global
literature priority is claimed for those methods. The explicit smaller
coefficient under this source contract is the contribution.

Node tariffs, complete child-volume realization, local suspension, arbitrary
dirty restoration, native/all-column identities, compiler closure, storage,
precision/tape and analytic recovery remain premises or separate obligations.
No physical program, new exponent, complete multiplication theorem, selected
cold replay, Lean build or Docker run is supplied. Independent human and
formal proof-kernel review are unclaimed.

## Open next questions

Can this smaller analytical coefficient reduce a concrete finite cutoff for
an actual completed physical supplier? First supply numerical node, leaf
and placement constants and one realized whole-child interface, then compare
the complete old and new cutoff inequalities. Unknown local suspension and
implementation costs block that operational claim. Optimizing the remaining
constant alone does not supply those missing routines. [TASK.json](TASK.json)
records this question and its first step.

## Verifier constraints

Functions have fewer than 60 lines. There is no recursion, subprocess, network,
dynamic code generation or file output. Floor fixtures use widths at most 96;
square fixtures use root sides at most 12 and stop sides at most four. Every
tree traversal has an 8,191-node cap, depth at most 12 and two children per
internal node. Six file reads each stop after 128 KiB plus a guard byte.
All observed capacities pass the registered normal and optimized checks.

Power-of-ten rule 3 deviation: CPython allocates managed integers, Fractions
and containers during this terminating finite command. The fixed domains,
depth/node caps and bounded file reads limit live storage. A steady-runtime
or unbounded-input reuse would require a separate allocation design.
Rule 9 deviation: the tree iterator calls one of two local branch constructors
whose targets and two-child results are fixed by the test loops. No caller
supplies executable code. Inlining them or introducing an explicit data
grammar is required before exposing the iterator as a general library.
Warning-strict normal/optimized execution and in-memory syntax inspection
provide Python diagnostics; no separate static analyzer is claimed.
