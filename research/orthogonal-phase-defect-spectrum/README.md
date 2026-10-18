# Every orthogonal chart phase defect, with one-transvection normalization

**Scoped all-dimension theorem and independent finite verification; no new κ.**

For the normalized complex residual in Gareth Davidson's [PR1255](https://github.com/CrocSwap/integer-mult-bounds/pull/1255), the attainable binary phase defects of an orthogonal `n`-axis rebase are **exactly the vectors whose weight is divisible by four**. Every defect has the same number of orthogonal realizations. An explicit involution `T_d = I + d dᵗ` realizes each defect and gives the algebraic factorization `S = T_d H`, where `H` preserves the exact complex residual.

This completes the defect spectrum behind PR1255's criterion and independently reconstructs its dimensions 1–6 census using an orbit/stabilizer transversal. It supplies closed counts for widths 7, 8 and 9 without enumerating tens of billions of matrices. It does **not** add a physical phase repair or a supplier admission: the selected controller still binds literal routes/charts, and its normalized helper endpoint is inherited.

| Active width n | Orthogonal matrices | Attainable defects | Matrices per defect / exact preservers |
|---:|---:|---:|---:|
| 1 | 1 | 1 | 1 |
| 2 | 2 | 1 | 2 |
| 3 | 6 | 1 | 6 |
| 4 | 48 | 2 | 24 |
| 5 | 720 | 6 | 120 |
| 6 | 23,040 | 16 | 1,440 |
| 7 | 1,451,520 | 36 | 40,320 |
| 8 | 185,794,560 | 72 | 2,580,480 |
| 9 | 47,377,612,800 | 136 | 348,364,800 |

The source-bound PR1255 receipt identifies selected widths **4, 5, 7, 8, 9**. These are counts of mathematical bases, not counts of admitted controller alternatives. The group theory and quadratic-refinement principles are classical; no literature-wide priority is claimed. The contribution is the constructive spectrum at this exact residual boundary, its elementary proof and the independent executable certificate.

## Reproduce

From the repository root, with standard-library Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/orthogonal-phase-defect-spectrum
```

Expected: `PASS_ORTHOGONAL_PHASE_DEFECT_SPECTRUM matrices=23817 literal_coefficients=187868 controls=9 no_new_kappa`, passing package tests, and `PASS_REGISTERED_RESEARCH_PACKAGE`. The verifier itself can also run with `python3 -I -O -B research/orthogonal-phase-defect-spectrum/verify.py`. It reads committed evidence and does not rewrite it unless explicitly given `--write`.

## Precise contract

Work over `V = F₂ⁿ`, with the standard dot product, Hamming weight `wt`, and `q(x) = wt(x) mod 4`. Let `O(n,2) = {S : SᵗS = I}`. Binary column matrices in the implementation represent the same linear maps as the formulas below.

The inherited elementary gate is

`C_u^(s) = ((1+si) I + (1-si) X_u)/2`, where `X_u f(x)=f(x+u)` and `s=±1`.

For orthonormal columns `U`, the normalized product has kernel

`K_U^(s)(Uz) = ((1+si)/2)^n (-si)^wt(z)`.

All these coefficients are nonzero. If `V=US`, the old and new active projectors agree, and PR1255 defines the **row-convention** defect

`d(S)_j = (wt(Sᵗe_j)-1)/2 mod 2`.

In particular, the implementation must transpose a stored column matrix before reading those weights. Orthogonality and the polarization identity

`q(x+y) = q(x)+q(y)-2(x·y) mod 4`

give, for every `x`,

`q(Sᵗx)-q(x) = 2 d(S)·x mod 4`.

Consequently `K_US^(s)(Ux)=(-1)^(d(S)·x) K_U^(s)(Ux)`. The exact residual is preserved iff `d(S)=0`. These kernel and phase facts are credited to PR1255; they are restated to fix conventions. The new result classifies the image and fibers of `d`.

## Proof of the spectrum and factorization

**Necessity.** Since `Sᵗ` is a permutation of `V`,

`Σ_x i^q(x) = Σ_x i^(q(x)+2d·x)`.

The left sum is `(1+i)^n`, nonzero. Separating coordinates gives the right sum as `(1+i)^(n-w) (1-i)^w`, where `w=wt(d)`. Their ratio is `(-i)^w`; equality therefore forces `w ≡ 0 (mod 4)`. This is an exact Gaussian-integer argument, without a numerical phase test.

**Sufficiency.** For any even-weight `v`, define `T_v x=x+(v·x)v`. Since `v·v=0`, direct multiplication gives `T_vᵗ=T_v`, `T_v²=I`, and `T_vᵗT_v=I`. Put `a=v·x∈{0,1}`. Polarization gives

`q(T_vx)-q(x)=a(q(v)-2) mod 4`.

If `wt(v) ≡ 0 (mod 4)`, this is `2 v·x mod 4`, so `d(T_v)=v`. This includes `v=0`, where `T_v=I`. If instead `wt(v) ≡ 2 (mod 4)`, the same orthogonal transvection has **zero** defect. Thus merely requiring even weight does not characterize the defect image.

**Cocycle and equal fibers.** In the fixed row convention,

`d(AB) = d(A) + A d(B)`.

Indeed, apply the phase formula first to `BᵗAᵗx`, then to `Aᵗx`, and use `(d(B)·Aᵗx)=(A d(B))·x`. Let `d=d(S)`. Its weight is divisible by four, so `T_d d=d`. Therefore

`d(T_d S)=d+T_d d=0`.

Writing `H=T_d S` gives `S=T_d H` with a uniquely determined `H` for this canonical representative. Conversely, every zero-defect `H` gives `d(T_d H)=d`. Thus multiplication by `T_d` is a bijection from the zero-defect subgroup to the `d` fiber. There are exactly

`A_n = Σ_{0≤4j≤n} binom(n,4j)`

fibers, each of size `|O(n,2)|/A_n`.

The attainable-defect set is generally **not** a binary subspace: at `n=5`, masks 15 and 23 have weight four but their XOR has weight two. Treating `d` as an ordinary group homomorphism, or its image as a linear code, would be wrong. The transported term in the cocycle is essential.

## Elementary order recurrence and complete enumeration

This proof also avoids assuming a tabulated classical-group order. Put `O₁=1`. For `n≥2`,

`O_n = (2^(n-1) - [n odd]) O_(n-1)`.

Every orthogonal matrix fixes the characteristic vector `j=(1,…,1)`, because `x·x=j·x` for every binary `x`. A first column must have odd weight. When `n` is odd and `n>1`, it cannot be `j`: if `S e₁=j` and `S j=j`, invertibility would force `e₁=j`. In even dimension `j` already has even weight.

Every remaining odd vector `u` is attainable as a first column by an explicit orthogonal map `L_u`:

- If `u=e₁`, use the identity.
- If `u₁=0`, use `T_(u+e₁)`.
- Otherwise choose an index `k>1` with `u_k=0` (possible because `u≠j`) and use `T_(u+e_k) T_(e_k+e₁)`.

Each transvection here has an even-weight parameter; direct substitution shows `L_u e₁=u`. Every orthogonal `S` with first column `u` has a **unique** representation `L_u diag(1,B)` with `B∈O(n-1,2)`: `L_u⁻¹S` fixes `e₁`, and orthogonality then forces both the first row and column to be `e₁`. Counting first-column choices gives the recurrence. The verifier implements exactly this transversal, independently of PR1255's pairwise-orthogonal-column backtracking. Its finite enumeration is a check of the written recurrence, not the justification for all dimensions.

## Evidence and limits

`CERTIFICATE.json` records:

- All **23,817** matrices in dimensions 1–6, with unique transversal generation, exact phase identity on every vector, complete defect histograms matching PR1255's separately implemented census, and `S=T_dH` checked for every matrix.
- Every attainable defect in dimensions 1–9, with an explicit symmetric orthogonal involution. Literal Gaussian-integer convolution checks **187,868** coefficients across both signs. This includes every defect at all five selected active widths.
- A direct character sum for every binary defect candidate in dimensions 1–9, independently verifying the Gauss-sum obstruction.
- All 2,304 ordered matrix pairs in dimension four and 500 deterministic seed-75 larger-dimension pairs for the **twisted** cocycle. The latter are samples, not a complete larger-group census.
- Nine semantic controls: odd transvections, impossible weight-two/out-of-range defects, dependent matrices, the unextendible characteristic first column, even-weight confusion, the equal-square phase blind spot, an untwisted cocycle, and the false linear-image assumption.

The companion tests independently enumerate all binary matrices through dimension four; they also check every first-column transversal through dimension nine, distinguish row and column conventions, and reject actual on-disk receipt/source corruptions under optimized Python. The source pin binds the inherited `C`-gate semantics; its executable module is not imported. No predecessor executable code is reused.

The universal statement has a written proof, **not a Lean/formal-kernel proof**. Counts for dimensions 7–9 follow from that proof; no exhaustive matrix census in those dimensions is claimed. We do not rerun PR1255's emitted-chart admission, the selected native/scalar replay, or whole-supplier cost and precision checks. Local normalized endpoints, physical compiler/hosting, precision/tape, all-size and analytic transfer remain inherited assumptions. No defect in the selected construction, cost reduction, new supplier or new κ is established.

## Pins, task and overlap

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Selected source at that base: PR1094 `0fc329d0bec93ca7cd288eaea1295172e8789810`, conditional `κ=836330098538459/500000000000000000`. `SOURCES.json` pins the actual inherited gate file and historical base provenance. `PREDECESSOR.json` pins the retained PR1255 receipt at `add1e2673ef000c097ec0fd70058e644af048d6b`; its author, source-specific notice and unchanged original receipt are retained.

The donor's OS-random assignment seed was **75**, independent verification. The repository audit card is explicitly marked **changed** in `TASK.json`: the selected source admission already has PR1255, so this contribution instead resolves its all-dimension attainable-defect structure. Other considered candidates were PR1227's restoration optimum (recent cyclic extension PR1287) and PR540's literal source binding (covered by PR1273). Initial body-level overlap covered 792 then-open PRs and the current discussion claims; the live count changed during selection as upstream integrated other work. PR1255 is the direct predecessor; PR1282/1291 concern signed norms, and PR1294 concerns dirty block-phase products, different obligations. Search absence is not a novelty proof. No pinned sprint issue existed; the claim was recorded locally as permitted by the donor.

## Open next questions

Can one **named selected helper** use a phase-preserving `H=T_d S` with a lower complete physical cost? First write the literal route, frame/gate invoice and exact admission checks for one width-seven role. The obstacles are the current fixed chart/route contract, physical compiler and a fully priced implementation. The algebraic factorization alone implies no saving. The structured question is also in `TASK.json`.

## Credit and license

Prepared by **Philipp / mightyOil**, with substantial **OpenAI Codex GPT-6 Astra** assistance in proof development, implementation, verification and writing. No independent human review is claimed.

Credit **Gareth Davidson (@bitplane)** for PR1255's exact phase criterion, counterexample, convolution contract and source-bound census, with substantial OpenAI Codex assistance as disclosed there. Credit **Rohan Arun, Jeremy Kothe, Hao Yan, Josie Elliston, Douglas Colkitt**, and the inherited Clifford/normalization and supplier lineage. Existing source material remains under its retained notices. New work is Apache-2.0 under the repository license.
