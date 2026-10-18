# A cost-six term at 25 punctures forces a 67-copy completion

**Scoped negative result: written proof and exact finite certificates. No new
kappa or physical supplier.**

The exact eight-term complex E8 decoder floor extends from `p<=24` to
`p<=25`. At 25 punctures the minimum, over puncture choices and decoders, is
**56 copies on 95 ports**. Parallel root normals can already give an individual
term of cost six, but every exact eight-term completion containing it costs
**at least 67**, and 67 is attained. The cheaper term does not lower the total.

For **nonparallel** normals with nonzero ordinary bilinear product, including
arbitrary complex normals, the first cost-six puncture size is **26**.
PR1020 already supplies the attaining root-pair witness at 26. This result
extends its lower bound beyond root normals and classifies the parallel
exception; it does not contradict PR1020's distinct-root statement.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/complex-general-normal-boundary
```

The registered command runs the primary replay, separate Gram-minor checker
and scoped mutation tests. Expected final wrapper line:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/complex-general-normal-boundary outcome=negative-result
```

Both mathematical checkers also support direct Python 3.10+ execution:

```sh
python3 -I -O -B research/complex-general-normal-boundary/verify.py
python3 -I -O -B research/complex-general-normal-boundary/check_gram.py
```

Expected markers: `PASS_COMPLEX_GENERAL_NORMAL_BOUNDARY` and
`PASS_GENERAL_NORMAL_GRAM_CHECK`. Ordinary replay recomputes and compares
[CERTIFICATE.json](CERTIFICATE.json); `verify.py --write-certificate` deliberately
regenerates only that file.

Coverage is **7,560** distinct boundary punctures, **63** for each of 120
distinguished roots, with explicit symmetry transport. All **32,193** rational
matrices (`63*511`) in the representative slice are checked. Two full decoder
examples are checked on **18,050** ordered live pairs. The primary controls
include an incorrect dual scale, the omitted unit label, the parallel-root
counterexample and all 25 single-line restorations.

## Model and theorem

Use PR717/PR968's 120 real E8 root lines, with norm-squared-two representatives
`r_i`, and label pairing `N_ij=(r_i dot r_j+1) mod 2`. Delete a common set `P`
of `p` lines; `R` denotes the live-root matrix. Complex matrices `D,T`, each
with eight columns, must satisfy **every entry** of

`D T^transpose = 2 R R^transpose`.

Transpose is ordinary transpose. Each term costs the F2 rank of `N` on the
two column supports. Masked identities, arbitrary outside-code overcomplete
factorizations and different label pairings are excluded.

**Theorem, with the inherited real root-flat classification F6.**

1. At `p<=25`, normals with nonzero bilinear product can have term cost at most
   six only at `p=25`, with both normals proportional to one real root `alpha`
   and `P` one of its 63 boundary cuts. The cost is exactly six. Each of the
   7,560 cuts has a unique distinguished root.
2. For every such puncture, every exact eight-term decoder containing the
   cost-six term costs at least 67. The certificate supplies attaining frames
   for all representative cuts and verified transport to every root.
3. The exact minimum at `p=25`, over punctures and decoders, is 56. Combined
   with PR968/PR1077, `cost>=max(72-p,56)` holds through `p=25`, and the best
   copy/port ratio remains `7/13` at `p=16`.
4. Nonparallel normals with nonzero product first attain cost six at `p=26`,
   using PR1020's witness.

Statement 3 does not say every puncture admits 56. Statement 2 concerns
decoders containing a cost-six term, not all decoders on that puncture.

## Proof

### Reduce an arbitrary complex support to the first boundary

The label space has nondegenerate dimension nine. For support spans `U,V`,

`rank(N|U x V) >= dim(U)+dim(V)-9`.

A term of cost at most six has one side of dimension at most seven. A generic
real combination of a complex normal's real and imaginary parts preserves
its exact root-zero pattern, as in PR1077. This is a support statement; it
does not independently replace two dual normals by real representatives.

Extend a root basis of the real zero flat to seven independent roots. The
resulting root-spanned hyperplane has a normal `omega` with
`C(omega) subset C(a)`. Its surviving support also has dimension at most seven.

The inherited **F6 classification of real root-spanned E8 hyperplanes** says
that every such hyperplane is Weyl-conjugate to one of eight fundamental
types. The primary checker recomputes their complete two-functional census:

| Hyperplane root lines | Minimum deletions for label dimension at most seven |
|---:|---:|
| 63, root-normal E7 | 25 |
| 42 | 42 |
| 37 | 51 |
| 28 | 56 |
| 23 | 61 |
| 22 | 62 |
| 16 | 68 |
| 14 | 70 |

Thus `p<=25` forces `p=25` and `omega` proportional to a root `alpha`.
Let `V_lambda` be the root set where a nonzero label functional evaluates to
one. Two independent functionals annihilating the surviving support require

`C(alpha) intersect (V_lambda union V_mu) subset P`.

All 130,305 independent functional pairs are enumerated. Minimum size 25
occurs for 189 pairs, producing 63 distinct sets. Since `|P|=25`, containment
is equality. All 120 root censuses and their transport by eight explicit root
reflections are checked. Their 7,560 punctures are distinct; transitivity is
verified rather than assumed.

### Recover every possible reduced normal, including complex ones

For each cut and each of the 511 nonzero functionals, form `Z_lambda` with
the live roots in `V_lambda` as rows. A normal `b` has support label dimension
at most eight exactly when it belongs to the complex kernel of some
`Z_lambda`.

For each of the 63 representative cuts, **483** matrices have rank eight and
**28** have rank seven. Every rank-seven kernel is a single real root
direction, extended to complex scalars. The 28 kernels represent **26**
distinct directions: only `alpha` has support dimension seven; the other
25 have dimension eight. Exactly one reduced direction, `beta`, lies in
`alpha^perp`.

These are exhaustive linear constraints on arbitrary complex coefficients.
A rational matrix has the same rank over Q and C. The separate checker uses
exact integer Gram determinants: positive 8-by-8 determinants certify rank
eight; a positive 7-by-7 principal minor and an explicitly annihilated root
vector certify rank seven. These Gram matrices come from the **real rational
rows** of `Z_lambda`; no complex positive-definiteness assumption is made.

The cheap term's smaller side must therefore be proportional to `alpha`.
If the other side has dimension nine, its cost is at least seven. Otherwise
it is one of the 26 directions. Exact binary ranks show that among directions
with nonzero product with `alpha`, only `alpha` has cost at most six, and its
cost is six. This proves statement 1 and excludes all nonparallel normals
through 25 punctures.

### Charge the seven remaining terms

At least 95 roots survive. F6 also gives a maximum of 63 lines in a real root
hyperplane, so the live-root matrix has rank eight. The all-pairs identity
implies `D=RA`, `T=RB` and

`A^transpose B = A B^transpose = 2I`.

The two normal lists are bases with paired products two. If one term uses
parallel `alpha` normals, the seven others on each side lie in `alpha^perp`
and are independent. At most one on either side can be reduced: it must be
proportional to the unique `beta`. Each side's support-dimension sum is at
least `8+6*9=62`. The remaining seven term costs sum to at least

`62+62-7*9 = 61`.

Including the cost-six term yields **67**. No blanket prohibition on complex
parallel cross-terms is used; duality and same-side independence suffice.

Every representative cut has an explicit orthogonal root frame beginning with
`alpha,beta`. Using that frame on both sides gives
`(6,7,9,9,9,9,9,9)`. All frames and costs are checked, and the displayed
seed-selected example is checked entrywise on all 9,025 live pairs. Verified
symmetries transport these constructions, proving sharpness.

If no term costs six, all eight cost at least seven. Otherwise 67 applies.
Hence the total is always at least 56. A second example extends PR968's
frame-pair construction by nine explicit punctures, with costs
`(7,7,7,7,7,7,7,7)` and all 9,025 entries checked. PR1020's nonparallel
26-puncture witness is independently reranked. Statements 2--4 follow.

## Budget and limits

The hypothesis was that the first seven-dimensional support could beat the
copy/port objective `7/13`. Even the favorable copy-only price fails:
`67/95 > 56/95 > 7/13`. Physical synthesis stopped at this budget gate.
This is the full **eight-term copy invoice**, not a recursive supplier
invoice. Source access, helper work, frame changes, restoration, recursive
children, hosting, precision/tape and assembly costs have not been priced or
removed. A different contract could change the comparison.

F6 is cited, not proved here; the primary replay recomputes its eight-type
table. The written argument quantifies over arbitrary complex normals, while
the finite checks establish its stated premises and examples. Neither is a
formal proof of multiplication. The Gram checker imports no producer or
predecessor code, but both implementations were prepared in the same
AI-assisted session; no independent human review is claimed.

No physical word, native admission, full selected-supplier cold replay,
all-size compiler proof, bit H1--H5 proof or analytic transfer is supplied.
The selected record remains unchanged at the base's conditional kappa
`836330098538459/500000000000000000`.

## Provenance, overlap and credit

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. OS assignment seed **31**
selected the complex-supplier track, candidate `31 mod 3 = 1`, root line 31
and witness index `31 mod 63`. Randomization is not evidence of novelty.
The declared census is complete and has no randomized optimizer.
[TASK.json](TASK.json) records the three candidates, overlap and scope change
from the catalogue's masked-decoder card. No pinned sprint issue existed;
the donor's local-claim fallback was used.

[SOURCES.json](SOURCES.json) binds base Git objects and exact byte hashes.
The selected record and catalogue are historical provenance. Proof sources
and the retained witness are explicit inputs in [VERIFY.json](VERIFY.json).

- **DreamingOfClouds, PR717:** B14 label pairing and decoder cost model.
- **themilkman216, PR968:** eight-type census, F6 premise, floor through 24
  punctures and the frame-pair attaining construction.
- **woklerx, PR1077:** arbitrary-complex support bridge and isotropic caution.
- **woklerx, PR1020**, head `bf4ee95df4ee6e3101a88f5d015c8aa85b688b6d`:
  distinct odd-root threshold 26 and its attaining witness. This package
  extends its lower-bound scope and credits the existing witness.
- **PR1180:** overlapping factor-linear overcomplete work through `p<=24`;
  its exact pending head is recorded for overlap, not used as a premise.
- **PR1187/PR1455:** thresholds and aggregate drops for a fixed P104 decoder,
  with a different prescribed decoder and puncture range; no proof dependency.
- **Rohan Arun, Jeremy Kothe, Hao Yan and the PR1094/1087/k8/T16,
  PR589/PR555 lineage:** reviewed supplier context.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in task selection, research, proof, both implementations, verification and
writing. New material is **Apache-2.0**; predecessor sources remain unchanged.

## Open next questions

1. **What is the least complete eight-term cost at 26 punctures?** The known
   nonparallel term costs six, but its retained completion costs 69. Start
   with its annihilator-kernel inventory and an optimistic full copy bill.
   Dual-basis compatibility beyond one cheap term is the blocker; this
   package does not enumerate 26-line punctures.
2. **Can F6 be replaced by a self-contained root-flat certificate?** That
   would remove the cited classification premise. Start with a canonical
   exact enumeration of maximal root-spanned hyperplanes modulo the verified
   reflections. Completeness and certificate size remain open here.
