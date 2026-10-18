# Uniform P112 column completions retain COPY64 with all nine factors free

**Scoped proof and exact finite evidence; no new kappa.** Rescaling all 52
free entries in one P112 column creates a rank-nine masked completion, but
allowing every factor term to change still cannot improve the separate COPY
bill. For every column, every nonzero complex parameter and every exact
nine-term factorization,

    sum rho_j >= 64,
    sum rho_j^q >= 8*8^q for every 0<q<=1.

Both bounds are attained. There is also a sharper result: when all nine
factor pairs have nonzero projections on both original coordinate spaces,
the sharp floor is **71**, with rank profile `(7,8,8,8,8,8,8,8,8)`.

The changed family is

    s = X[v,:]^T,  w = Xs - 4e_v,
    K_lambda = XX^T + lambda*w*e_v^T,  lambda != 0.

Here X is the standard P112 coordinate matrix and XX^T=2G. The vector w
is supported exactly on the 52 odd neighbors of v, so only unconstrained
entries change. Lambda=-1 clears them; other complex values rescale them.
The transpose gives the corresponding row family. All nine factors vary,
including arbitrary complex basis changes; no six- or five-term exterior
is frozen.

## What this adds

[Arham Tahir's PR1591](https://github.com/CrocSwap/integer-mult-bounds/pull/1591),
pinned at `264b8dcfc56584797ebf36d69ee35de18313fd27`, handles **one changed
odd entry** with all nine factors free. Its complete punctured support
classification is credited and independently replayed here, without claiming
priority for that lemma. The new object changes 52 entries simultaneously.
Its two factor spaces have the **same anchor**, so a pure singleton can pair
at cost zero; the previous distinct-anchor singleton charge cannot be reused.

The [proof](PROOF.md) resolves those zero-cost branches by the actual
rank-nine coefficient matrix. One residual is the original all-pairs
decoder; the other is a reciprocal row/column scaling with unchanged
supports, and cannot occur at lambda=-1. A further cross-duality identity
permits at most one cost-seven mixed term and gives the sharp 71 bound.

PR1468 allows arbitrary free column amplitudes with two mixed coordinate
modes. [Hanson Sun's PR1613](https://github.com/CrocSwap/integer-mult-bounds/pull/1613),
head `a34723742801f877c9636ed72f176a7ffa7bf005`, extends that mode count to
three and credits Andrey Mas's parallel claim. This package restricts the
amplitude pattern but permits all nine factors to change. The results have
different quantified domains. PR1473's multiline rectangle result and the
preceding correction/compensation lineage are also retained in the credit.

## Evidence

The primary checker constructs canonical doubled E8 roots and binds them to
the pinned PR845 geometry, including signs, coordinate order and all binary
pairings. Fraction-free rational elimination classifies every puncture and
nonzero binary character. The independent checker constructs the geometry
from weight-four frame coordinates and verifies ranks by modular minors
plus exact integer null vectors. It imports neither the primary code nor a
predecessor executable.

- All **57,232** puncture/character cases: **1,008** exact one-dimensional
  complex kernels and **56,224** full-rank constraints. The unpunctured
  511-character classification is also checked.
- All **13,552** support-class pairing entries, including the essential
  zero-cost same-anchor boundary and every original coordinate direction.
- **14** exact Gaussian-rational factorizations, checking **175,616** matrix
  entries: ordinary transpose, nonreal and rational parameters, dense
  factor changes, both zero-cost branches, the lambda=-1 boundary and
  attaining COPY64/COPY71 profiles.
- A separate integer implementation checks **37,632** entries for three
  paid-compensation examples. Removing the final rank-one term lowers the
  apparent COPY sum to 63 but removes four from a constrained diagonal.
- Mathematical controls reject omitted paid compensation, Hermitian
  substitution, singular factor changes, zero parameters outside the
  rank-nine scope and the impossible left-zero branch at lambda=-1.
  A complex isotropic normal provides a further boundary check.
- Package controls test optimized read-only relocation, false bounds,
  incomplete puncture coverage, source drift and malformed receipts.

The quantified conclusions come from the written coefficient and
support-space argument. The finite fixtures support its implementation;
they do not enumerate arbitrary complex factor matrices. Separate code is
not independent human review or a proof-assistant verification.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py \
  --package research/p112-uniform-column-rank9
```

The explicit replay runs `verify.py`, `independent.py` and `test_package.py`.
All guards remain active with `-O`. Normal replay is read-only;
`verify.py --write-expected` explicitly regenerates EXPECTED.json.
The two checkers also run from a relocated package with its retained inputs.
The registered replay passed under Python 3.12. Both checkers also passed
under Python 3.14 with `-I -O -B`, from a read-only copy outside the checkout,
with unchanged package files and the same canonical receipt. The package
controls passed all eight deliberate corruptions as well as relocation.
Exact source commits, SHA256 hashes and Git blobs are in SOURCES.json and
REMOTE-SOURCES.json. The primary imports the retained, unmodified PR845
geometry only for source binding; its new classification is computed locally.

Expected main marker:

```text
PASS_P112_UNIFORM_COLUMN_RANK9 floor=64 nine_mixed=71 hyperplanes=57232
```

## Cost meaning and limitations

The complete **separate COPY component** includes every factor, including
compensation. At unchanged width, normalization and multiplicity, its power
sum cannot improve even if all new preparation, frame changes, helper
reservation, source access, restoration, hosting and precision/tape costs
are granted zero. Rank concentration within these nine COPY terms therefore
does not evade the bound.

No physical supplier, complete local paid profile or favorable whole moment
is constructed. The theorem does not exclude savings in other frame or
schedule work. Arbitrary nonuniform column amplitudes, multiple changed
columns, ten or more factors, different label sets and shared COPY billing
remain outside scope. No selected cold replay, compiler theorem, analytic
transfer, Lean result or new exponent is claimed.

At q=1, the only equality rank multisets are `(0,8,8,8,8,8,8,8,8)` and
`(1,7,8,8,8,8,8,8,8)`. For 0<q<1 only the first can attain equality.
This classifies rank profiles, not all attaining factor bases.

## Assignment and coordination

Published as [PR1652](https://github.com/CrocSwap/integer-mult-bounds/pull/1652).
The mathematical contribution is commit
`6b05c428fcfdc5d860c30baa00d3b6fdc41da050`; later publication metadata
does not change its proof, checkers, sources or receipt.

Single random nonce `c3d61d9333f4d9682ef1c24c486cd260`, complex mechanisms,
revision-2 `complex-masked-decoder`; no reroll. Both prescribed starting
checks passed. Work began from current main
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.
[Discussion1639](https://github.com/CrocSwap/integer-mult-bounds/discussions/1639)
records the precise scope and result.

On resumption, upstream `858771bcca3b8dd5d4ef4aa682a13cc9b7e23920` had
adopted priority revision 3 while preserving the selected result and these
mathematical inputs. The existing assignment was retained. Its new emphasis
on rank shape is addressed by the COPY-power obstruction; this package
does not claim the stronger-budget acceptance gate for a new local profile.
The incumbent ceiling calculator would need such a profile and its hosting
contract; it is not applied to a factorization-only object outside that input
model. Final overlap and validation details are recorded in TASK.json.
The final upstream check at `1f7a934975e5eacaf83511c9ac870263bf095e05`
found these mathematical inputs, selected record and replay hook unchanged.
The refreshed search covered 594 open PRs and 293 discussion records with
complete pagination; the two pinned closest predecessor heads were unchanged.
PR1612's separate COPY71 result fixes nine simplex normals and uses all-pairs
exactness, so it does not cover this masked rank-nine completion.

## Open next questions

1. **Arbitrary amplitudes on the same free column.** This would bridge the
   restricted-mode results and the full-factor family here. Start with
   `u=lambda*w+eta*h`, where h is supported on the odd neighbors but lies
   outside `col(X,e_v)`. The left factor space changes, so the present
   same-anchor classification no longer applies.
2. **Ten terms for the same rank-nine completion.** This tests whether one
   redundant term changes the COPY-power bill. First use the rank inequality
   to constrain which factor space must remain inside `col(X,e_v)`, then
   analyze repeated V directions. Invertibility of both nine-column bases
   is essential to the present cross-duality argument and is the blocker.
3. **A complete frame-path saving with COPY unchanged.** Pin a concrete
   per-call profile and all helper/restoration obligations, then apply the
   current ceiling screen where its hypotheses hold. This theorem controls
   only COPY; no admitted frame path or whole-supplier invoice is supplied.

## Credit

Prepared by **Gareth Davidson (@bitplane)** with substantial **OpenAI Codex
assistance**. Credit Arham Tahir, Hanson Sun, Andrey Mas, Mihir Srivastava,
DreamingOfClouds, GamingPuzzled, themilkman216, woklerx and the retained
community lineage. See NOTICE.md and the unchanged source notices.
New work is Apache-2.0; no independent human review is asserted.
