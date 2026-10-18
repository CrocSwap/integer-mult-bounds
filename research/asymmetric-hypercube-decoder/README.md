# Global-star decoding: sharp punctures and higher-target hierarchies

**Uniform structural theorems with exact replay; no new κ.** The higher-target
extension determines a complete hierarchy at `k=2`, the third generalized
weight for every `k>=2,q=p-k>=2`, the first five weights for every `q>=3`,
all fourth-weight optimizers, and all fifth-weight optimizers for `q>=4`.
At `q=2` it determines a five-weight prefix with all rank-three through
rank-five optimizers classified.
A generalized weight `d_r` measures the smallest support of r independent
observation rows. The exact deletion threshold for **some selectable r-target
set** is `d_r-r`; arbitrary prescribed target sets are a separate problem.

| Result | Parameter range | Proof |
| --- | --- | --- |
| Complete generalized-weight hierarchies, with and without the empty star | `k=2,p>=2`, every available rank | [HIGHER-GRAPH.md](HIGHER-GRAPH.md) |
| Exact prescribed-forest matching formula in `C-`, partition optimization in both codes, and every prescribed triple | `k=2,p>=2` | [GRAPH-TARGETS.md](GRAPH-TARGETS.md) |
| First two nonzero word weights are `2q+2` and `4q+2` | `k>=2,q>=3` | [HIGHER-WEIGHTS.md](HIGHER-WEIGHTS.md) |
| `d_3=6q+3`; every optimum is a triangle of minimum stars | `k>=2,q>=3` | [HIGHER-WEIGHTS.md](HIGHER-WEIGHTS.md) |
| `d_3=15` for `k=2,3`; `d_3=14` for `k>=4` | `q=2` | [HIGHER-WEIGHTS.md](HIGHER-WEIGHTS.md) |
| `(d_1,...,d_5)=(6,11,14,15,16)` | `q=2,k>=4` | [HIGHER-WEIGHTS.md](HIGHER-WEIGHTS.md) |
| `d_4=8q+2`; every optimum is a four-star clique | `k>=2,q>=3` | [FOURTH-WEIGHT.md](FOURTH-WEIGHT.md) |
| `d_5=10q`; every second-weight word is an adjacent-star sum | `k>=2,q>=3` | [FIFTH-WEIGHT.md](FIFTH-WEIGHT.md) |
| Every rank-five optimum is a five-star clique; exact prescribed-five-target criterion | `k>=2,q>=4` | [FIFTH-WEIGHT.md](FIFTH-WEIGHT.md) |
| Every optimal rank-three, four and five subcode is an affine four-flat code; exact prescribed-target criterion | `q=2,k>=4` | [CUBE-OPTIMIZERS.md](CUBE-OPTIMIZERS.md) |
| Exact ordinary-cube shortening to a Reed–Muller code, with the empty-star boundary distinguished | `k>=2,q>=0` | [CUBE-OPTIMIZERS.md](CUBE-OPTIMIZERS.md) |
| Exact original-pair-core shortening with unrestricted core signs; all extra layers have weight at least sixteen | `q=3,k>=2`, shortening `C+` on `k-2` original pairs | [CORE-SHORTENING.md](CORE-SHORTENING.md) |

The boundary is a real change in optimizer structure: every span of three
minimum stars needs at least fifteen ports, but a localized affine cube has
three independent rows on fourteen ports. At `q=2,k>=4`, three, four, or five
selectable targets therefore all need exactly **eleven deletions**. At `(p,k)=(8,4)`,
three selectable targets instead need exactly 24 deletions. Code results apply
to both proper-star spaces; overlap-class corrections are covered at
power-of-two k only. For `q>=3`, there are exactly
`2^(k+1) binom(p,k-2) binom(q+2,3)` optimal three-dimensional subcodes. A
prescribed triple attains `6q` deletions exactly when its three columns on
some triangle have rank three. The larger budgets required by triples
failing that criterion are not classified.

For `q=2,k>=4`, prescribed sets of three, four or five targets attain eleven
deletions exactly when they use the same original pairs and their sign vectors
are affinely independent. For `q>=3`, prescribed quadruples attain `8q-2`
deletions exactly when their columns are independent on an optimal four-star
clique. These statements concern the specified proper-star observation model.
For `q>=4`, prescribed five-target sets attain `10q-5` deletions exactly
when their columns are independent on a five-star clique. The rank-five
optimizer classification at `q=3` remains open in this milestone.

[COPY-OBSTRUCTION.md](COPY-OBSTRUCTION.md) addresses a much larger physical
class. An integral separating pairing with odd diagonal forces total copied
frame rank `C>=v`, even with arbitrary recoded linear observations, individually
readable corrections and chronological copy-to-zero reuse. Every even-size
paired-port geometry with intersection-one readability satisfies that condition.
Under the inherited odd-stage rank ledger, `C>=v` prevents a positive saving.
The actual selected E8 supplier has even diagonal and is outside this obstruction.

[ODD-NATIVE-COST.md](ODD-NATIVE-COST.md) gives a separate uniform ceiling
for acquiring every literal odd-degree proper star natively. For every odd
`k>=5`, its bit saving is less than `107/66606` under the inherited schedule
with at least five stages, even with favorable helper sharing and hosting.
A separately stated conditional three-stage extension excludes odd `k>=7`.
Both ceilings are below the campaign-start selected bound. Arbitrary recoded
observations and COPY-assisted innovations remain outside this result.

For prescribed graph targets, [GRAPH-TARGETS.md](GRAPH-TARGETS.md) goes
beyond selectable-target weights. Every forest T with r edges has exact
nonempty-star deletion budget
`2p(p-1)-r-binom(2p-r,2)+p-nu(T)`, where `nu(T)` is a capacity-matching
number between target-tree components and original coordinate pairs.
The empty star does not improve this budget when `p>=6,r<=p`.

The general incidence-code/cut connection is credited to Martínez-Bernal,
Valencia-Bucio, and Villarreal in the graph note. The uniform minimum distance
is inherited from Luke Mansoor's #732. Earlier one- and two-target results,
concurrent source credits, and the original obstruction remain below.

## Reproduce the current campaign milestone

From the repository root, Python 3.10+ with its standard library:

```sh
for check in shortening optimizer block copy_obstruction core_shortening graph_targets; do
  python3 -I -O -B "research/asymmetric-hypercube-decoder/${check}_verify.py" --self-test || exit
done
```

Each prints `PASS` followed by its filename after checking the saved receipt,
isolated optimized relocation, corruption rejection, and output preservation.

- [shortening_verify.py](shortening_verify.py): 42 full-generator shortenings,
  comparing both inclusions with independently generated Reed–Muller spaces and
  checking full ranks against the pinned PR #772 formula.
- [optimizer_verify.py](optimizer_verify.py): all 187 rank-three through
  rank-five subspaces of `RM(1,4)`, all 6,748 target sets of those sizes, and
  54,208 single-deletion restoration controls in that full cube code.
- [block_verify.py](block_verify.py): six complementary-block/four-cycle
  models at `q=2,k=3,4,5`; 4,196,424 complete codewords in the four models
  of dimension at most 22; exact syndrome matching over 1,296,438,900 logical
  complementary 4+4 support candidates; 139,776 alternating 3/4 cycle support
  candidates with separately fixed core signs in each block. Its 720
  support-fourteen subcode case instances overlap between models and are not
  a global distinct-subcode count. Nine adversarial controls reject false
  shortening and parity-only models.
- [copy_obstruction_verify.py](copy_obstruction_verify.py): eight exact
  binary/rational matrix checks at `k=2,p=3,...,6` and `k=4,p=4,...,7`, plus
  hypothesis-failure controls and a sequential copy fragment requiring the
  innovation argument. This is not a full physical supplier replay.
- [core_shortening_verify.py](core_shortening_verify.py): full-generator
  original-core shortenings at `q=3,k=3,...,6`, all thirty independent
  sign-polynomial components, all 1,048,576 words of the smallest shortened
  code, and exact residual-code and core-polynomial distance checks.
  Its negative controls detect the extra weight-sixteen layers omitted by
  a model that simply repeats the signed-core graph code.
- [graph_targets_verify.py](graph_targets_verify.py): all 4,112 target sets
  at `p=2,3`, all 73 triple/quadruple orbits at `p=4` covering 12,650 target
  sets, 4,329,472 actual decoder assignments, and 1,845 restoration controls.
  The exact forest formula is checked independently by capacity matching,
  root-choice dynamic programming, and full retained-graph or decoder oracles.

The campaign remains active. [CAMPAIGN-18H.json](CAMPAIGN-18H.json) records
its scope and minimum research period. These completed mathematical milestones
do not settle the remaining higher-rank and odd-size physical questions.

## Reproduce the earlier higher-target results

From the repository root, Python 3.10+ with its standard library:

```sh
for check in higher cube boundary; do
  python3 -I -O -B "research/asymmetric-hypercube-decoder/${check}_verify.py" --self-test || exit
done
```

Expected output prefixes: `PASS_HIGHER_GRAPH`, `PASS_CUBE`, and `PASS_K3_BOUNDARY`.
The independent checks compare their deterministic receipts before reporting
success. Every self-test also checks relocation, optimized execution,
corruption rejection, and preservation of an existing output on failure.

- [higher_verify.py](higher_verify.py): all labeled vertex partitions and all
  internal cuts at `p=3,...,6`; 8,224 literal edge restrictions at `p=2,3`;
  all 449,606 nonzero subspaces of the two graph codes at `p=3,4`; all
  7,135,750 rank-three subspaces at `p=5`, including exactly eighty optima
  in each code, matching the triangle count; complete weight distributions for 523,776 words
  at `p=5,...,9`; 68 optimal simultaneous-decoder witnesses with 1,511
  full-code restoration controls.
- [cube_verify.py](cube_verify.py): fifteen literal three-, four-, and five-target
  decoders, evaluated on every port at `q=2,k=4,...,8`; 165 restoration controls
  within the displayed subcodes; 25 three-star constructions at `k,q=2,...,6`.
  The smallest cube certificates include the actual proper-star expansions,
  targets, deletions, and decoder coefficients in [CUBE-RESULTS.json](CUBE-RESULTS.json).
- [boundary_verify.py](boundary_verify.py): all five shortening spaces of the
  full `p=5,k=3` code, 90 basis vectors, and all 1,024 words of its residual
  extension E. This checks the exceptional boundary lemma; it does not
  enumerate all global three-dimensional subcodes.

These finite checks support the separate written proofs. They do not replace
them or constitute a proof-assistant verification. [HIGHER-CLAIM.json](HIGHER-CLAIM.json)
records the continuation base `8bcbaafe8590d30eff9c0ae5fd9e49479c84038c`,
source pins, review coverage, and stopping rule. [HIGHER-COST.md](HIGHER-COST.md)
prices the displayed scalar evaluation and explains the unresolved supplier
interface. There is no changed multiplication bound or selected certificate.

## One- and two-target geometry

**Uniform structural theorems; no new κ.** Put `q=p-k`. For every `k>=2`
and `q>=2`, this package now proves:

- Every minimum nonzero proper-star evaluation vector is a single
  `(k-1)`-star. There are exactly `2^(k-1) binom(p,k-1)` such vectors.
- The smallest support of a two-dimensional proper-star subcode is exactly
  `4q+3`. Every attaining subcode is generated by two adjacent `(k-1)`-stars;
  there are exactly `2^k binom(p,k) binom(k,2)` attaining subcodes.
- For any two distinct prescribed targets T,T', the exact number of deletions
  required to decode both from proper-star observations is

  ```text
  4q+1   if |T intersect T'| >= k-2,
  4q+2   otherwise.
  ```

The intersection counts **signed coordinates**, not just original pair
indices. The code statements hold with or without the empty star. For
power-of-two k they also cover the uniform overlap corrections in (1) below;
those corrections already belong to the nonempty-star span. Arbitrary exact
postprocessing of these same linear observations cannot improve the thresholds.
The inputs at all other surviving ports remain unrestricted.

[MINIMUM-WORDS.md](MINIMUM-WORDS.md) proves minimum-word rigidity and the
second generalized weight. [EQUALITY-PAIR.md](EQUALITY-PAIR.md) classifies
all optimal two-dimensional subcodes and proves the prescribed-pair formula,
including the boundary `q=2`. These are proofs for the whole stated parameter
range; the finite checker below provides separate, reproducible evidence.

For example, `(p,k)=(8,4)` has 1,120 ports. One target has exactly four optimal
nine-deletion patterns. Two prescribed targets need 17 deletions when they
share at least two signed coordinates, and 18 otherwise. Decoding **every**
surviving port is a separate rank question: the nonempty-star threshold of
673 deletions is inherited from ellipsi2's
[PR #772](https://github.com/CrocSwap/integer-mult-bounds/pull/772), not a new
claim here. No helper, source-access, copy, frame, restoration, recursive-child
or assembly cost is inferred from these scalar identities.

## Reproduce the extension

From the repository root, using Python 3.10+ and only its standard library:

```sh
python3 -I -O -B research/asymmetric-hypercube-decoder/global_verify.py --self-test
```

Expected: a `PASS_GLOBAL_EQUALITY` line after comparison with
[GLOBAL-RESULTS.json](GLOBAL-RESULTS.json). The replay checks:

- Four complete `q=2` equality-support models, `k=2,...,5`: 123,774,104
  possible supports with fixed common pair indices, exactly 30 literal stars.
  This is an exact meet-in-the-middle census of the reduced models, not an
  enumeration of every word in the full codes. The proof supplies the reduction.
- All 2,979,201 two-dimensional subcodes in the full empty-allowed `k=2`
  codes at `p=4,5,6`, including their minima and attaining weight patterns.
- 25 literal two-target decoders, `k=2,...,6` and `q=2,...,6`, with all 425
  single-port restorations rejected.
- All 202,136 prescribed target pairs for `k=2,3,4` and `q=2,3`, checked
  against adjacent-star coverage and explicit decoders for both distance cases.
- Corrupted supports, omitted cross-block constraints, the genuine `q=1`
  nonstar exception, redundant coefficient representations, and an incorrect
  unsigned-intersection criterion. The self-test also checks isolated optimized
  replay, receipt corruption detection, and preservation of existing output
  when a receipt check fails.

The finite domains are exhaustive and fixed in the script; there is no random
or timed search. Seed 48 is the original track assignment. The new checker
uses integer coordinate masks and does not import the earlier verifier or a
predecessor's implementation. To export a checked receipt, add
`--check research/asymmetric-hypercube-decoder/GLOBAL-RESULTS.json --write /tmp/global-star-results.json`.

The exact original base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
[EXTENSION-CLAIM.json](EXTENSION-CLAIM.json) pins the concurrent source texts
and the later main-branch snapshot. Luke Mansoor's #732 already proves the
global minimum distance; Sagar Thakrar's #725 treats the `q=1` exception;
Alishan Ladhani's #747 classifies the finite `(6,4)` minimum words; #772 gives
the uniform ranks. This extension credits and builds on those results. It
adds uniform equality classifications and the exact two-target geometry.

## Original result: the unpunctured obstruction and target-local punctures

**Scoped negative result; no new κ.** The symmetric-coefficient result in
[PR #231](https://github.com/CrocSwap/integer-mult-bounds/pull/231), by
Joel Pulikkan / GamingPuzzled, extends to arbitrary target-dependent coefficients
on **all stars of degree less than k, including off-target stars**. For the
smaller target-local star family, the exact minimum number of deleted ports
needed to decode one retained target at a power-of-two k is **2(p − k) + 1**.

The first result closes an algebraic escape route: asymmetric reweighting or
off-target proper stars cannot rescue an unpunctured 4- or 8-dimensional paired
hypercube decoder. The second quantifies how fragile that obstruction can be
under puncturing, without claiming a construction for all remaining targets.

## Model and predecessor

Let p ≥ k ≥ 2. The coordinates are p disjoint pairs. A port is a k-element set
containing one coordinate from each of k distinct pairs. Write P for all
2^k binom(p,k) ports. The independent input symbols x_S take values in F₂.
For a surviving family F ⊆ P containing a fixed target T, define

```text
star_L(F) = sum_{S in F, L subset S} x_S
C_j(T,F) = sum_{S in F, |S intersect T| = j} x_S.
```

All sums and coefficients below are in F₂. A global proper-star decoder has
the form

```text
x_T = sum_{L: 0 < |L| < k} a_(T,L) star_L(F)
      + sum_{j=1}^{k-1} b_(T,j) C_j(T,F).                 (1)
```

Here L may use any coordinates; sets containing both coordinates of a pair
give a zero star and can be omitted. Coefficients may depend independently on
T and L. Within each correction C_j, the same coefficient applies to every
source of that intersection size. The target-local family additionally
requires L ⊂ T. Degree-k stars and the j=0 and j=k correction classes are
excluded. A degree-k star would directly supply x_T; the j=k correction would
do the same. Allowing an empty-set star does not change the unpunctured
obstruction below.

[The retained #231 note](../hypercube-decoder-parity/README.md) restricts to
target-local stars with a_(T,L) = a_|L| and establishes existence exactly when
k is not a power of two. We retain that result and attribution. The new points
are the larger coefficient/support class in Theorem 1 and the sharp local
puncture threshold in Theorem 2. This is not a repeat of #231's coefficient
enumeration. Pending [#631](https://github.com/CrocSwap/integer-mult-bounds/pull/631)
studies E8 root-line punctures, a different port geometry.

## Theorem 1: arbitrary global proper stars, full port family

For F=P, a decoder of form (1) exists if and only if k is not a power of two.

**Necessity, without a symmetry assumption.** Fix T. Let Q_T be the 2^k ports
obtained by independently flipping the chosen coordinate in each of T's k
pairs. XOR the coefficient equations of (1) for all source ports S ∈ Q_T.

For a star_L with |L|<k, the number of such ports containing L is either zero
(if L uses an outside pair or incompatible coordinates) or 2^(k−|L|). Thus
every allowed star contributes zero to the summed equation. The same holds
for the empty star. The correction C_j contributes binom(k,j), since exactly
that many sign-flip ports intersect T in j coordinates.

If k is a power of two, every binom(k,j), 0<j<k, is even. The right side
therefore sums to zero, whereas the desired coefficient vector of x_T sums
to one: **0=1**. This is an explicit binary linear inconsistency certificate,
not an argument that averages coefficients over symmetries.

**Sufficiency, inherited from #231.** If k is not a power of two, choose
0<l<k with binom(k,l) odd. Set all local size-l star coefficients to one and
other star coefficients to zero; set b_(T,j)=binom(j,l) mod 2. For a source
with j<k intersections, the two coefficients cancel (and j=0 contributes
zero); at S=T the coefficient is binom(k,l)=1.

For completeness, the binomial parity criterion follows in F₂[z] from
(1+z)^k = product_{r: bit_r(k)=1}(1+z^(2^r)). With one set bit there are no
interior terms. With at least two set bits, the least set bit gives an odd
interior coefficient. The proof applies to every p≥k, not only checked sizes.

## Theorem 2: sharp puncture threshold for target-local stars

Let k≥2 be a power of two, p≥k, and retain a specified T. Restrict to
0<|L|<k with L⊂T in (1). The smallest possible deletion set D⊆P\{T} for
which T admits a decoder on F=P\D has size

```text
min |D| = 1 + 2(p-k).                                  (2)
```

Both stars and corrections are defined over the surviving family F. This
statement does **not** cover off-target stars after puncturing.

**Cell sizes.** For J⊂T, |J|=j<k, let P_J be the ports with S∩T=J. Put
d=k−j and q=p−k. To complete J to such a port, select a of the remaining d
target pairs (using their opposite coordinates), then d−a outside pairs,
with two signs each. With out-of-range binomial coefficients taken as zero,

```text
|P_J| = N_j = sum_{a=0}^d binom(d,a) binom(q,d-a) 2^(d-a)
            = sum_{u=0}^d binom(d,u) binom(q,u) 2^u.
```

For every nonempty proper J, d≥1. The u=0 and u=1 terms give
N_j≥1+2dq≥1+2q, with equality at j=k−1. Thus fewer than 1+2q deletions
leave at least one representative in every nonempty proper intersection cell.

**Why surviving cells force local symmetry.** For each such J, the coefficient
equation is

```text
sum_{empty != L subset J} a_(T,L) = b_(T,|J|).          (3)
```

Induction on |J| forces a_(T,J) to depend only on |J|: singletons all equal
b_(T,1); thereafter (3) expresses a_(T,J) as b_(T,|J|) plus the already
level-constant contributions of proper subsets of J. Write the resulting
coefficients a_l. The target coefficient must then be
sum_{l=1}^{k-1} binom(k,l)a_l=0, contradicting the required value one.
This proves the lower bound in (2). It also shows that any successful local
puncture must empty at least one entire nonempty proper intersection cell.

In fact, emptying **any** such cell P_J suffices for local decoding of T:
use the sum of star_L over J⊆L⊊T. Its source coefficient is one precisely
when S∩T is J or T. For J⊆K⊊T this follows from
sum_{J⊆L⊆K}1=2^(|K|−|J|); at K=T the excluded term L=T changes the parity
to one. With P_J deleted this is x_T. Thus the cell criterion characterizes
local feasibility; a smallest deletion set uses |J|=k−1.

**Sharpness.** Choose a fixed (k−1)-subset J⊂T and delete exactly P_J. These
are the 1+2(p−k) ports other than T that contain J. Among surviving ports,
star_J(F)=x_T. Use that single star with coefficient one and set every other
coefficient to zero. This attains (2).

For comparison, on the full family the same induction proves that all local
decoders are level-constant at each target. For a non-power-of-two k, the
k−1 level coefficients satisfy one nonzero binary equation, so there are
exactly 2^(k−2) local decoders per target. The correction coefficients are
then determined. This count does not apply to the larger global-star class.

## Verification

Run from the repository root, using only the Python 3.10+ standard library:

```sh
python3 -B research/asymmetric-hypercube-decoder/verify.py --negative-controls --write /tmp/asymmetric-hypercube.json
cmp research/asymmetric-hypercube-decoder/results.json /tmp/asymmetric-hypercube.json
```

The expected result is a PASS message and an identical deterministic receipt.
The committed receipt covers 9 compressed coefficient systems, 11 actual port
families, all 131,336 coefficient vectors in its three small cases, all 3,413
deletion sets in its four bounded puncture cases, and five negative-control
categories. Fresh runs on Python 3.11.13 and 3.14.5, including Python 3.14.5
with `-O`, produced identical receipts; no check relies on Python assertions.
The checker generates actual ports independently of the cell-count formula,
forms unrestricted target-local coefficient systems, and performs exact F₂
elimination. It also checks the global-star XOR certificate directly on
actual sign-flip cubes. Finite coverage and negative controls are enumerated
in [results.json](results.json); they support the written all-parameter proofs
above and are not a formal proof of the multiplication theorem.

The experiment domain and stopping rule are fixed by the verifier's case lists:
complete finite cases, no heuristic search or time-dependent stopping. Seed 48
selects the structural track and focuses on k=4 and k=8; the verifier records
its deterministic target choices. Source pins and the starting accepted
construction are in [SOURCES.json](SOURCES.json), with the sprint scope in
[CLAIM.json](CLAIM.json). Neither the selected certificate nor `upstream/` is
changed. The full supplier cold replay is outside this standalone decoder
result; no new supplier profile is asserted.

## Interpretation and limits

- For the full paired-port family at power-of-two k, arbitrary asymmetric
  proper-star preparation already fails at the scalar identity. Giving every
  helper, copy, source read, frame change, restoration and recursive child
  zero cost cannot repair that failure. There is therefore no positive
  complete-cost candidate to price or claim as a κ improvement here.
- The local puncture upper bound decodes only one specified target. Its
  isolated-star witness says nothing about simultaneously decoding all live
  ports, restoring arbitrary scratch inputs or improving copied-information
  cost. It supplies neither a paid recursive profile nor an assembly bound.
- The original Theorem 2 is restricted to target-local stars; the extension
  linked above covers global stars after puncturing and exact postprocessing
  of the same observations. Other correction classes, source-dependent
  coefficients within a class, degree-k totals, nonlinear helper observations,
  restricted inputs and different port geometries remain outside these results.
  In particular this is not an E8 decoder ceiling.
- The selected construction at the base commit has conditional
  κ=51110230636731/31250000000000000. Its compiler, physical realization,
  hosting, precision/tape and analytic assumptions are neither used to prove
  these finite algebraic statements nor discharged by them.

## Attribution and license

Prepared by Sam Sung (@the-missionary-company), with substantial OpenAI Codex
assistance in the proofs, implementation and independent review. The prior
symmetric obstruction and parity criterion are Joel Pulikkan / GamingPuzzled's
#231 contribution, building on icekylinx's #144 paired-cube work and eumemic's
paired-cube bit identity. The repository preserves those predecessor notices.
The selected-frontier context credits Chafik Boukhalfa's #626, Jeremy Kothe's
#622/#623 and eumemic's #543, with the cumulative lineage in its maintainer
review; this note does not independently re-certify that construction.
The extension additionally credits Luke Mansoor (#732), Sagar Thakrar (#725),
Alishan Ladhani (#747) and ellipsi2 (#772), as detailed in the proof notes and
the pinned extension claim.

New files are licensed under the repository's Apache-2.0 license.
