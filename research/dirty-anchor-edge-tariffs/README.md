# Dirty-output fanout with directed complete tariffs

**An exact local tariff theorem, with finite checks. No physical supplier or
new kappa.** PR3063's destination-only prices do not cover source-dependent
routing. This package proves that a rooted directed forest remains optimal
among all allowed interleaved straight-line words in the specified XOR model.

There are q arbitrary-dirty required rows. A complete call P_i toggles row i
by the same arbitrary p from preserved disjoint sources, at stationary finite
price mu_i>0. ADD(i,j) toggles destination i by source j, at stationary finite
price c_ij>0. There is no additional helper, CLEAR, COPY, free basis change or
intermediate observer; all entry dirt must be preserved at the endpoint.

The exact common-value work is

    min over directed rooted spanning forests F
        [sum_{roots i} mu_i + 2 sum_{arcs j->i} c_ij].

Independent private row calls add their fixed complete bill. Every edge is
paid twice, including preparation and restoration. A literal inverse has the
same cost and must be paid separately if the caller requires it. Complete
tariffs include source access, routing, frames, scratch cleanup and physical
head return as applicable; this theorem does not manufacture those prices.

## Why arbitrary interleavings cannot beat the forest

For every subset S with no common-call destination, zero incoming ADDs cannot
deliver arbitrary p. Exactly one incoming ADD cannot restore the span of the
independent entry-dirt rows, even with outgoing feedback. There are therefore
at least two incoming occurrences for every such S. The finite prescribed-root
disjoint-branching theorem of Edmonds packs two paid spanning forests in the
ADD occurrence multigraph and gives the lower bound. Children-before-parent
preparation, one call per root, and literal reverse preparation attain it.

[PROOF.md](PROOF.md) states all premises, the external graph-theorem dependency,
the inverse and private-call arguments. The graph-only dummy root converts
the price optimizer into a minimum directed spanning arborescence. It is not
a free physical register. For destination-only c_ij=alpha_i the formula
reduces exactly to PR3063's earlier subset optimum.

The directed chain 0->1->2, with mu=(1,100,100), c_10=c_21=1 and all other
edges costing 100, has optimum 5. The best height-one forest costs 103, the best
single-root star 203, and direct calls 201. These are abstract complete tariffs,
not measured prices. A separate cheap-cycle fixture shows why substituting
each row's cheapest incoming edge into the old formula can falsely return 5
when directed root reachability forces 103.

## Exact coverage and reproduction

The primary checker verifies every rooted forest through q=6 (18,248 total),
560 structured forests through q=112, exact symbolic forward/inverse maps on
all dirt/common/private columns, 3,400 exhaustive one-bit assignments through
q=4, 340 heterogeneous destination-price reductions, the subset-cut lemma
over every GL(q,2) prefix through q=4 (46,372 eligible crossing cases), its
four original defect controls, and six further semantic or pricing defects.
It uses no predecessor executable.

The separately implemented [independent.py](independent.py) constructs the
full affine-state graphs through q=3 and uses unrestricted weighted shortest
paths, rather than assuming a forest-shaped word. Its exact finite domains
and limitations are in [INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md).

The all-parameter statement is a written proof using Edmonds' finite theorem,
as stated in [Attila Joo's paper, pp.1-2](https://arxiv.org/pdf/1705.00471v1).
Finite tests corroborate the ingredients; they do not prove that external
theorem or provide formal-kernel or independent-human verification.

From the repository root with standard-library Python 3.12:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/dirty-anchor-edge-tariffs
```

The registered replay includes the primary normal/optimized runs and the
separate independent checker. Direct primary replay is read-only, comparing
every RESULT.json field. `--write` creates an absent result and refuses
overwrite; `--output PATH` writes an absent external result. The partial
cut_check.py stages also accept explicit absent external outputs. Full Git
history is needed for package provenance; direct scientific checking needs
the declared pinned source files but no network, solver or native build.

Source hashes, Git blobs and scientific base
997e6a9ca7b4f95d50e366f61412fd640d72a88a are in [SOURCES.json](SOURCES.json).
The selected record and catalogue are historical provenance; the explicit
predecessor inputs must match their pins. Managed Python objects are checking
tools, not an all-size tape-machine realization.

## Open next questions

Bind one operand-compatible caller with legal unobserved target lifetimes to
complete directed tariffs. Then charge changed child ranks, routing, helper/
idle stock, precision, restoration, hosting and the complete outer recurrence
for both suppliers. No selected-provider placement or physical tariff matrix
is supplied here. State-, path- or frame-dependent prices need another model;
the exact stationary optimum cannot be substituted for them. The concrete
first step and blockers are recorded in [TASK.json](TASK.json). Stop here
until such a physical caller can change the recursive-cost decision.

## Credit

Ross Richardson/PR3063 head 3f384b8b7daccb2c8e12013fd81a738202ce0f8d supplies
the destination-only boundary, building on Cinna Davis/PR1944's dirty echo.
PR1968's several-common-term accumulation retains separate credit.
Anthony/PR774 and Oscar Fennell/PR759 give earlier forest compensation
synthesis, including their credited tree-synthesis literature. No priority
for forest synthesis or graph optimization is claimed. The new implication
is the subset cut and branching lower bound for unrestricted edge-priced
single-common-value words. Edmonds and Joo retain credit for the external
graph theorem and its stated formulation.

New proof and checkers by Ross Richardson with substantial OpenAI Codex
assistance (GPT-6.1 Sol, Max), Apache-2.0. One automated recursive-interface
specialist independently audited the proof and finite model. The investigation
is coordinated in [Discussion3061](https://github.com/CrocSwap/integer-mult-bounds/discussions/3061#discussioncomment-18987651).
