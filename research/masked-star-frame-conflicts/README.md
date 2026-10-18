# Independent verification of PR1236's masked root-star floor

**Independent verification; no new supplier or kappa. The theorem is credited to PR1236.**
This package independently corroborates **David Arias's PR1236**, at
`ee8437bd9879272094e20c024cd34a53c4e84cd8`, including its exact certificate.
In the B14 model on P112, masked decoders with full or self-trimmed root-star
supports have sharp pairing-rank cost **64**, at any finite term count and
with arbitrary real or complex coefficients.

[PR1236](https://github.com/CrocSwap/integer-mult-bounds/pull/1236) already closes
the cost-63 assembly question left by Aaron Wang / Navinor's
[PR1226](https://github.com/CrocSwap/integer-mult-bounds/pull/1226). Its correct
averaged inequality `784/13` is strengthened by simultaneous missed-frame
constraints. The added evidence here is a different graph algorithm: enumerate
all maximal cliques, then reconstruct the entire clique census by deduplicated
subset closure. A separate norm-lattice root enumeration and row-span rank
calculation reproduce PR1236's committed geometry, frames and ordered atom
hashes. The Python 3.12 registered replay of this audit is also exercised here.

Concurrent [PR1242](https://github.com/CrocSwap/integer-mult-bounds/pull/1242)
also supplies an independent Weyl-root/maximal-clique replay and a Python 3.12
replay of the original PR1236 package. Those are credited separately. The
additional scope here is the complete source-bound comparison of the original
certificate sections, including its per-atom and frame hashes after index
translation, and reconstruction of its full clique spectrum by subset closure.

The initial investigation and both local checkers predate discovery of PR1236
in the final overlap refresh. Its earlier submission is credited, and this
package is presented as independent corroboration. The subsequent source-binding
adapter is intentionally based on its certificate schema; no predecessor
implementation is imported or executed.

Base: `49b3157d1d89adcef16df8be98445451672be5ba`. Structural decoder track,
OS-random assignment seed **41**. The seed also fixes the cyclic traversal
order for the complete graph search. [TASK.json](TASK.json) records the three
candidate tasks, bounded scope, stopping rule and overlap decision.
[SOURCES.json](SOURCES.json) pins the source commits, Git blobs and SHA256s.

## Reproduce

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 scripts/research_package.py --package research/masked-star-frame-conflicts
```

This runs the full checker, a separate implementation and source-bound audit,
and 17 controls under `-I -O -B`. Expected markers are
`PASS_MASKED_ROOT_STAR_FLOOR_64`, `PASS_INDEPENDENT_ROOT_STAR_PREMISES`,
`PASS_PR1236_SOURCE_BOUND_AUDIT`, 17 passing tests, and
`PASS_REGISTERED_RESEARCH_PACKAGE`. Direct replay also works with
Python 3.10 or later:

```sh
python3 -I -O -B research/masked-star-frame-conflicts/verify.py
```

Normal runs are read-only. To generate a candidate receipt, use
`verify.py --write /new/path.json`; to check a supplied receipt, use
`verify.py --check /path.json`. Every field is compared with a fresh computation.

## Model and exact scope

Use the 120 E8 root lines, with root norm squared two. Remove the eight lines
`e_(2a) +/- e_(2a+1)`, for `a=0,1,2,3`, to obtain P112. The checker stores
doubled integer coordinates, chooses each representative with first nonzero
coordinate positive, and sorts them lexicographically. Its indices therefore
need not match a predecessor's enumeration order.

Write `G_ij = <r_i,r_j>` and `B_ij = (G_ij+1) mod 2`. For each root normal alpha,
define

```text
C(alpha) = { i in P112 : <r_i,alpha> != 0 }
N(alpha) = C(alpha) minus alpha's own line, when that line is live.
```

There are 240 named support entries, with 232 distinct masks because the two
entries coincide for each removed normal. Each positive-cost rank-one term
`d t^T` has row and column supports chosen from these entries. Its price is
`beta = rank_F2 B[supp(d),supp(t)]`. The decoder must sum to `2G` on the 6,720
even-inner-product entries, including the diagonal. There is no constraint on
its remaining 5,824 entries. Coefficients use ordinary transpose, with no
conjugation, and may be real or complex.

The theorem allows repeated terms and arbitrary additional terms of pairing
rank zero. Such terms vanish on every orthogonal frame: if both supports met
a frame, their pairing matrix would contain an entry one. In particular, the
usual zero-cost singleton corrections on odd pairs cannot affect the argument.

The supports above are the **actual nonzero supports**, or declared supports
whose full rank price is charged. Allowing coefficients to vanish and then
charging a cheaper, deeper-trimmed support changes the hypothesis. General
supports, other punctures and other cost contracts are outside this result.

## Finite premises

The checker reconstructs the geometry and evaluates every ordered support pair.
It does not trust a predecessor's receipt or import predecessor code.

| Premise | Exact checked result |
|---|---|
| Orthogonal eight-frames in P112 | 1,260; every live line belongs to 90 |
| Distinct live pairs in a common frame | Exactly the orthogonal pairs; 2,856 pairs occur in 10 frames and 448 in 15 |
| Remaining distinct live pairs | 2,912 nonorthogonal pairs, in no common frame |
| Ordered support-pair prices | 7,616 of rank 7; 37,440 of rank 8; 12,544 of rank 9 |
| Frames missed by a rank-7 atom | 1,792 atoms miss 90; 5,824 miss 180 |
| Nonorthogonality graph on live normals | Clique number 8; no clique of size 9 |

The price census also verifies the full classification: two untrimmed live
stars have price nine; one such star and one effective trimmed star have price
eight; two effective trimmed stars have price
`8 - [<alpha,beta> is odd]`. A star whose normal is removed is effectively
trimmed because its self-line is absent.

For every named star, the checker verifies its complete missed-frame set.
`C(alpha)` meets every frame. A live `N(alpha)` misses exactly the frames
containing alpha; a removed normal's `N(alpha)` misses none. Consequently every
rank-seven atom has at least one live trimmed normal and misses all 90 frames
through that normal. Two removed normals cannot make a rank-seven atom because
the removed frame is orthogonal.

The primary clique checker enumerates strictly increasing prefixes and prunes
only when the remaining candidate count cannot reach the requested size. It
has no search timeout, random sampling or heuristic rejection. Its seed-41
traversal exhausts the size-nine question; an explicit size-eight witness is in
[CERTIFICATE.json](CERTIFICATE.json).

`independent_check.py` enumerates roots by the norm and congruence conditions of
the doubled E8 lattice, rather than the two explicit root families. It uses
set-based pivoted Bron--Kerbosch enumeration of **all maximal cliques**. The
compatibility census is 896 cliques of size three, 23,040 of size seven and
4,032 of size eight. It separately reproduces all 1,260 frames and the ordered
57,600 pairing-rank stream by taking row spans before restricting columns.
Every clique lies in a maximal clique, so repeatedly deleting vertices and
deduplicating reconstructs all clique sizes. This reproduces PR1236's entire
census `1,112,2912,25088,88704,161280,145152,55296,4032` without its ordered
all-clique traversal or its second checker's quadratic-form argument.
Hashes compare full ordered streams, not only their histograms. Both
implementations were prepared in this session; this is not independent human
review.

The verbatim [reference receipt](reference/PR1236-CERTIFICATE.json) is pinned
by commit, Git blob and SHA256. The adapter translates local P112 indices to
the original 120-line indexing before comparison. It checks every field in
`model`, `frames`, `atoms`, `odd_graph` and `sharp_decoder`, including the
original eight-clique witness and all 12,544 coordinate identity entries.
The original `assembly_cases` descriptions and `negative_controls` names are
retained by the immutable source pin; the original control implementations
are not executed. This package has its own failure controls below. The
reference is data under audit, not an imported supplier or trusted result.

## Why these premises give the sharp floor

On any orthogonal eight-frame F, the required decoder matrix is `4 I_8`.
Every rank-one term restricts to rank at most one, and a term missing F on
either side contributes zero. Thus at least eight positive-cost terms must
meet every frame. Let n be their number.

1. **n < 8:** impossible by this rank requirement.
2. **n = 8:** every term must meet every frame. A rank-seven term misses some
   frame, so all eight prices are at least eight. Total cost is at least 64.
3. **n = 9 and total cost < 64:** every price is an integer at least seven,
   so all nine must be seven and the total must be 63. At most one term may
   miss any frame, so the nine missed-frame sets must be pairwise disjoint.
   Choose one live trimmed normal from each term. Their 90-frame incidence
   sets must be disjoint as well. The chosen normals cannot repeat. Every
   orthogonal pair occurs together in a frame, so the nine normals must be
   pairwise nonorthogonal. This is a nine-clique in the compatibility graph,
   contradicting its computed maximum of eight.
4. **n >= 10:** the total cost is at least `7n >= 70`.

These cases exhaust every term count. For sharpness, take the eight removed
orthogonal normals `f_k` and use
`d_k(i) = t_k(i) = <r_i,f_k>`. The checker verifies all 12,544 entries of
`sum_k d_k t_k^T = 2G`, and independently prices each term at eight. This is the
existing coordinate construction, not a new construction claim.

## Verification and limits

The 17 controls exercise missing, duplicated and nonorthogonal frames; deletion
of a trimmed star's missed-frame obstruction; a falsely universal rank-seven atom;
loss of a required cheap-atom incidence; a broken graph/Gram relation; an actual
K9 and the K8 boundary; coordinate attainment and omission of one coordinate
term; odd versus even singleton repair prices; and certificate corruption.
The source-audit additions check deduplication of overlapping maximal cliques,
altered atom semantics, altered reference bytes and a missing reference receipt.
The independent graph algorithm also finds a supplied K9. Checks use explicit
exceptions and remain active under optimized Python.

This is a finite-census-supported proof for the stated support family. It is
not a failed heuristic search, a proof-assistant formalization or a theorem
about every multiplication algorithm. The result excludes the favorable
copy-cost-63 mechanism before any implementation: even giving helper creation,
source access, frame changes, restoration, recursive children and hosting zero
additional cost cannot make this alphabet's copied-information bill less than
64. No completed supplier invoice, moment improvement or runtime claim follows.

The selected record at the base remains the reviewed conditional
`kappa = 836330098538459/500000000000000000`. Only its source-binding baseline
was run here. The selected cold replay `make frontier1094-verify` was not run
for this disjoint research package. All-size/compiler, common-label and
mutable-source realization, hosting, precision/tape, analytic transfer and
bit H1-H5 obligations are untouched and are not discharged by this result.

## Credit and overlap

- **Hanson Sun (@bbMisk), concurrent PR1242**, head
  `7f31a561787864f26eb2242ef35179d07223accf`: Weyl-reflection roots, column ranks,
  maximal-clique corroboration and a Python 3.12 replay of PR1236. Its same
  maximal-clique counts are corroborated here; they are not claimed as new.
- **David Arias (@DavidAriasC), PR1236**, head
  `ee8437bd9879272094e20c024cd34a53c4e84cd8`: the earlier-submitted sharp-64
  theorem, simultaneous missed-frame proof, integer-dependence parity argument
  and certificate audited here. Its contribution retains theorem credit.
- **Aaron Wang / Navinor, PR1226**, head
  `8b10989e4e45f0f9ce41004d7898a21a32f87e11`: the exact trimmed-star census,
  the `784/13` averaged bound and the explicit remaining assembly question.
  PR1236 adds the integer term-count and missed-frame compatibility obstruction;
  this package independently checks it. The averaging bound is not contradicted.
- **DreamingOfClouds, PR717**, head
  `4a97676294f9fa413b65986e9984fddeda71e4cc`: the B14 model, masked reduction,
  pairing-rank pricing and mixed-beta question; PR595 supplies earlier format
  context. **Joel Pulikkan / GamingPuzzled, PR620**, supplies the retained
  coordinate decoder and earlier star floors; **icekylinx, PR514/P112**,
  supplies the 112-port puncture lineage.
- **themilkman216, PR968**, and **woklerx, PR1077**: the exact eight-term
  all-pairs floor and its complex-coefficient extension. The repository review
  ledger identifies their authors separately. Neither result is used as an
  unproved lower-bound dependency here.
- Concurrent **burntout76, PR1212** and **DavidAriasC, PR1213** address
  eight-term masked rigidity; **mightyOil, PR1191** addresses one-sided
  root-linear factors; **joaqcoo, PR1224** addresses nine-term all-pairs
  factorization. This package allows non-root-linear coefficients on both
  factors, any term count, and masked exactness, while restricting supports
  to the named stars. Exact overlapping heads are retained in TASK.json.

No pinned sprint issue existed at entry, so the claim was recorded locally as
the donor requested. The entry scan covered all 838 open PRs, including bodies,
and all six discussions with comments/replies; the completed claim in
discussion1210 had been released. The refresh at 20:57 UTC covered 843 open PRs
and 15 discussion records and found PR1236, submitted at 20:46:58 UTC. That
changed the contribution to source-bound independent verification. The tool's
coverage, limitations, exact heads and scope change are recorded in TASK.json.
Matching titles alone were not treated as proof of novelty.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex** assistance
in research, proof, implementation, verification and documentation. New work
is Apache-2.0. The retained PR1236 receipt is by David Arias with substantial
OpenAI Codex assistance, under the same repository license. No frozen
predecessor, selected certificate or upstream file is modified.

## Open next questions

Does the same argument recover a sharp floor of 63 for the root-star masked
family on one of PR717's pinned P111 fixtures? PR717 already provides a
cost-63 all-pairs construction there. A bounded first step is to regenerate
that fixture's frame and atom inventories and test the pair-completion and
cheap-normal-incidence premises. The changed puncture is a blocker to reusing
the P112 proof; no P111 verification is claimed here. The structured question
and its scope are in TASK.json.
