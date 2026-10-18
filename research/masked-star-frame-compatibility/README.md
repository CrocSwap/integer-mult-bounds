# Independent finite verification of the P112 masked root-star floor

**Independent verification of a scoped negative result: the minimum
copied-information cost is 64.**
This holds for the P112 masked complex decoder whose paid terms have exactly
the untrimmed or self-trimmed root-star supports defined below, with arbitrary
complex coefficients and any finite number of terms. The usual eight coordinate
stars attain 64. No new supplier or kappa is claimed.

The final overlap refresh found **David Arias's concurrent
[PR1236](https://github.com/CrocSwap/integer-mult-bounds/pull/1236)**, at
`ee8437bd9879272094e20c024cd34a53c4e84cd8`, which had already submitted the
same conclusion. Our initial claim and both implementations preceded reading
that PR. This package therefore contributes independent corroboration, with
the same scope and no priority claim. Its distinctive check generates roots
by Weyl reflections and exhausts maximal cliques by pivoted Bron-Kerbosch;
PR1236's second checker instead uses lattice coordinates and a quadratic-form
obstruction. We also give a Python 3.12 replay of its pinned registered package,
the runtime that its initial validation receipt said was untested.

[Navinor's PR1226](https://github.com/CrocSwap/integer-mult-bounds/pull/1226)
computes the sharp value `784/13` of an aggregate frame-covering relaxation and
leaves open whether cheap trimmed atoms can actually assemble at cost 63.
That relaxation and its census remain correct. The strengthening retains
**which frames each atom misses**: two missed terms already defeat a nine-term
decoder on a common frame. The resulting compatibility condition excludes
cost 63, without a coefficient search or a root-linearity assumption.

## Model and exact scope

Let `R` be the 120 norm-two E8 root lines, choosing one sign for each line.
Let `F0 = {e0 +/- e1, e2 +/- e3, e4 +/- e5, e6 +/- e7}` and
`L = R - F0`, the 112 live lines. Write `G[i,j] = <r_i,r_j>` and
`B[i,j] = (G[i,j] + 1) mod 2` for the binary label pairing.
For any root line `a`, define

```text
C(a) = {i in L : <r_i,a> != 0},       N(a) = C(a) - {a}.
```

There are 240 labeled supports and 232 distinct subsets: for the eight
punctured normals, `C(a) = N(a)`. Each paid term is `d_k t_k^T`, where
the **actual nonzero supports** of `d_k` and `t_k` each equal one of these
subsets. Its price is `beta_k = rank_F2 B[supp(d_k), supp(t_k)]`, and prices
add separately across terms. Coefficients can be arbitrary complex numbers;
transpose is ordinary transpose, with no conjugation.

The masked identity requires `sum_k d_k(i)t_k(j) = 2G[i,j]` only when
`G[i,j]` is even: the diagonal entries are 4 and orthogonal off-diagonal
entries are zero. Any number of rank-zero terms may also be included.
For example, the unrestricted odd entries can be repaired by free singleton
terms. Rank-zero terms vanish on every frame used below.

The result does **not** cover further deletions inside a star, arbitrary
subsets contained in a star, unions of stars, other punctures, a different
label pairing, or a pricing scheme that jointly charges several terms.

## Written proof and checked finite premises

A live frame is eight pairwise orthogonal lines in `L`. Its masked target
is `4 I_8`, of complex rank eight. Every paid term restricts to a matrix of
rank at most one. A rank-zero term has `B[S,T]=0`; if both supports met a
frame, a pair in `S x T` on that frame would instead have binary pairing
one. Thus rank-zero terms contribute nothing on every frame. At least
eight paid terms must be nonzero on each frame.

The executable finite premises are:

1. **Atom classification.** All 57,600 ordered labeled support pairs have
   rank 7, 8 or 9, with counts 7,616, 37,440 and 12,544. Rank seven occurs
   exactly when the two normals have inner product `+/-1` and both supports
   are effectively self-trimmed: a live normal must use `N`, while a
   punctured normal may use either label. Since the punctured normals are
   pairwise orthogonal, every rank-seven atom has at least one live trimmed
   normal.
2. **Annihilation and extension.** There are 1,260 live frames; each live
   line belongs to 90. The support `N(a)` misses exactly the frames
   containing `a`; an untrimmed `C(a)` misses none. Every orthogonal pair
   of distinct live lines extends to a live frame: 2,856 pairs have ten
   extensions and 448 have fifteen.
3. **Compatibility cap.** A pairwise nonorthogonal set of live lines has
   size at most eight. The primary implementation exhausts every clique
   of this graph, with no depth cutoff. The counts for sizes zero through
   eight are
   `1, 112, 2912, 25088, 88704, 161280, 145152, 55296, 4032`;
   there are no larger cliques. A separate maximal-clique implementation
   finds 896 maximal triples, 23,040 maximal seven-cliques and 4,032
   maximal eight-cliques. An eight-line witness is in the certificate.

These facts imply the claimed floor. Suppose the total price is below 64,
and let `n` be the number of paid terms. Premise 1 gives `n <= 9`, while
the frame rank argument gives `n >= 8`.

If `n = 8`, at least one term has rank seven. Choose a live trimmed normal
of that term and a frame containing it. The term is zero on that frame,
leaving at most seven rank-one matrices to produce a rank-eight target:
a contradiction.

If `n = 9`, every term has rank seven and the total price is 63. Choose
one live trimmed normal `a_k` from each term. No two choices can coincide:
a frame containing the repeated normal would annihilate two terms.
Nor can two choices be orthogonal: their common live-frame extension would
again annihilate two terms. The nine choices must therefore be distinct and
pairwise nonorthogonal, contradicting premise 3. This exhausts the term counts.

Finally, for the eight normals `f` in `F0`, the coordinate terms
`d_f(i) = t_f(i) = <r_i,f>` satisfy
`sum_f <r_i,f><r_j,f> = 2<r_i,r_j>` on all live pairs. Each term costs eight,
so the bound 64 is attained. The checker tests all 12,544 entries and all
eight prices.

This is a written finite-geometric proof with exhaustive exact checks of
its premises. It is not proof-assistant verification, independent human
review, or a proof of the full asymptotic multiplication theorem.

## Reproduce

From the repository root, Python 3.10+ and the standard library:

```sh
python3 -I -B research/masked-star-frame-compatibility/test_package.py
```

Expected: both checker markers below, successful corruption controls, and
`PASS_MASKED_STAR_PACKAGE`. All subprocesses have bounded timeouts. The
package runs offline and does not regenerate predecessor artifacts.

```text
PASS_MASKED_STAR_FRAME_COMPATIBILITY atoms=57600 frames=1260 max_clique=8 cost_floor=64 controls=7
PASS_INDEPENDENT_MASKED_STAR weyl_roots=240 atoms=57600 frames=1260 maximal_cliques={3: 896, 7: 23040, 8: 4032} cost_floor=64
```

The primary checker reconstructs roots directly, uses binary row elimination,
enumerates all cliques, and compares every field with
[CERTIFICATE.json](CERTIFICATE.json). `verify.py --write` regenerates that
certificate. The separate checker instead generates the 240 roots by Weyl
reflections, uses binary column elimination and pivoted Bron-Kerbosch
maximal-clique enumeration, with cyclic vertex offset 36. It imports neither
the primary checker nor predecessor code. Both recompute the full atom census,
frame annihilation/extension facts, graph cap and cost-64 construction.
This is implementation independence within one AI-assisted contribution.

Controls cover a wrong decoder coefficient, the diagonal condition, a
synthetic nine-clique, a rank-one singleton outside the support family,
repeated and orthogonal normal collisions, and free odd-entry patches.
The package runner also corrupts the rank census, clique cap and a clique
witness, requires nonzero exits, tests a path containing spaces, and checks
that verification preserves the committed certificate.

[VERIFY.json](VERIFY.json) opts into the repository's bounded Python 3.12
package workflow. With Python 3.12 installed, the registered equivalent is:

```sh
python3.12 scripts/research_package.py --package research/masked-star-frame-compatibility
```

## Provenance, overlap and accounting

Base: `49b3157d1d89adcef16df8be98445451672be5ba`. Assignment seed **36**,
complex-supplier track; [CLAIM.json](CLAIM.json) records three candidates,
the live overlap check and stopping rule. No pinned coordination issue was
present, so the claim is local, as requested. [TASK.json](TASK.json) records
the refined `complex-masked-decoder` card and the final corroboration status;
[SOURCES.json](SOURCES.json) pins
historical context and predecessor sources. None is an imported executable
dependency. [VALIDATION.json](VALIDATION.json) records the completed checks.

At this base, the selected conditional kappa is
`836330098538459/500000000000000000`, from the reviewed #1094 construction,
and the complex primitive is binding. This result rejects a proposed
cost-saving route even in the favorable relaxation that gives all source
access, helper preparation, frame changes, restoration and physical hosting
zero additional cost. It does not price or construct a new recursive
supplier. Nonnegative implementation charges cannot rescue a decoder whose
copied-information price already fails to improve 64. The selected bit
supplier, recursive invoice and frontier are unchanged; no new assembly
or complete cold replay is claimed. All inherited compiler, realization,
hosting, precision/tape, recovery and analytic-transfer obligations remain.

Credit:

- **David Arias / DavidAriasC, PR1236**, at the head above: the concurrent
  cost-64 theorem, primitive-integer-dependence proof and two finite checkers.
  The theorem and complete-clique counts here independently agree with that
  earlier submission. The maximal-clique/Weyl-orbit check is separately written;
  PR1236's code and parity proof are not imported into either new checker.
- **Navinor, PR1226**, head
  `8b10989e4e45f0f9ce41004d7898a21a32f87e11`: the exact root-star census,
  the aggregate `784/13` covering bound and the explicit unresolved assembly
  question. This package independently reconstructs that census and adds
  simultaneous frame compatibility; it does not correct the predecessor's
  valid relaxation.
- **DreamingOfClouds, PR717/595/604**: the B14 label model, masked reduction,
  copied-information accounting and mixed-beta problem.
- **themilkman216, PR968**, **woklerx, PR1077**, and
  **Joel Pulikkan / GamingPuzzled, PR620**:
  preceding all-pairs decoder floors, root geometry and the coordinate
  cost-64 construction.
- Concurrent **burntout76, PR1212**, **David Arias, PR1213**, and
  **Philipp / mightyOil, PR1191** address eight-term or one-root-linear-factor
  masked classes. Their theorems are not premises here; our support-restricted
  result permits any term count and neither factor needs to be root-linear.
  **joaqcoo, PR1224** studies nine-term all-pairs normal forms, a different
  exactness requirement.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex
assistance** in the proof, implementations, experiments and documentation.
New work is Apache-2.0. No predecessor source files are copied into this package.

## Open next questions

Can deleting one additional live line from a trimmed support create a
cost-saving masked decoder? Such supports are outside this theorem and could
change both the minimum atom rank and its missed-frame pattern. A feasible
first check is an exact census of their ranks and frame signatures before
attempting coefficient synthesis. No favorable complete supplier budget or
legal realization for that enlarged family is currently established here.
The structured question, relevance, first step and blocker are in
[TASK.json](TASK.json).
