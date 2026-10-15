# Independent Gaussian, precision, and sparse-layout audit

Candidate: `work/phase_assembly_ultra/phase_fusion_note.tex` (read in full).

Conclusion: **no new blocking gap found in the audited Gaussian, local-window,
precision, density, or sparse-layout arguments.** This is a conditional
mathematical audit. It does not verify the finite suppliers, semantic guard,
prime-packing interface, or the shallow-circuit construction delegated to the
parent reviewer. Existing PASS declarations were not treated as evidence.

The layout-specific independent subreview is in `layout_subreview.md`.

## 1. Narrow Gaussian and principal-window locality

Sources: candidate lines 138–149, 213–219, 264–281;
`work/gaussian_fast_ultra/LOG-A-PHASE-SCHUR-AUDIT.md` lines 9–45, 55–96;
`work/integer-mult-current/references/semantic-bulk/rad20/reports/review-bulk-resampling.md`
lines 21–55 and 86–106.

I re-derived the two-neighbor estimate rather than accepting its declared
review status. For a jump of size one, the nearest exponents are
`1+2 theta-2 beta_i` and `1+2 theta+2 beta_i`. A jump of size two only increases
the corresponding exponent because its occurrence forces the appropriate
endpoint condition on beta. Convexity on `[-1/2,1/2]` then bounds their sum by
`exp(-2 a theta)+exp(-2 a(1+theta))`. For `|h|>=2`, the exponent is at least
`h^2-|h|`; the two-sided tail is at most `4 exp(-2a)`. Thus the claimed
`exp(-2a theta)+5 exp(-2a)` bound follows. In particular, counting both nearest
neighbors separately at the larger bound would be invalid, but the supplied
argument does not do so.

The actual H is specified by globally fixed rounded weights and a globally
fixed truncated Toeplitz kernel inside each physical phase cell. Its diagonal
is one, with the omitted aliases included in the perturbation. The candidate's
perturbation budget is strictly below the displayed row-dominance gap. Principal
submatrices preserve this row gap. Adding identity hole rows/columns preserves
it as well, and increases the physical bandwidth by at most the q-image spacing
factor, which is bounded by two.

For `F=H_aug-I`, `||F||_infinity<=1-delta` with
`delta>=1/(16p)`. Powers through order J agree on a core row whose distance from
the principal-window edge exceeds J times the bandwidth. The two inverse tails
are bounded by `2(1-delta)^J/delta`. With `J=C p^2`, this is exponentially small
in p. The distance requirement is `O(p^(5/2) polylog p)`, below the candidate's
`A=C_A p^3` eventually. The preserved physical period cut and the fact that
true axes exceed every polynomial in p exclude spurious short wrap edges.

## 2. Broad Gaussian conditioning is a different argument, and it works

Sources: candidate lines 151–201;
`work/gaussian_fast_ultra/FORWARD-SMALL-A-AUDIT.md` lines 13–73 and 75–105;
`work/gaussian_fast_ultra/BILATERAL-LDU.md` lines 25–119.

For the finite LDU formulas, I checked the origin-shift correction and the
triangular inverse estimates. If `h=j-i`, the elementary-polynomial estimate
for the upper inverse reduces its exponential part to

`b[beta_j^2-beta_i^2-rho^2 h-2 rho sum_{k=i}^{j-1} beta_k]`.

Using `|beta_k|<=1/2` gives at most `b/4-b rho theta h`. The lower inverse uses
the corresponding expression with the other sign on the beta sum and has the
same decay. The factors `c_b^-1` and `c_b^-2` come from the explicitly bounded
products. This proves the stated uniform finite-interval bound; integrality of
the q-values is not needed, only gaps at least one and the beta bound.

The broad target-cell identity also checks directly. With
`q'_k=k+rho c`, `beta'_k=theta k-rho c`, and
`b=b0/rho^2`, one obtains

`K=alpha^-1 N_b diag(exp(-b beta'^2))`.

At a selected target index, `beta'_k` equals the original source beta. Therefore
the finite LDU bound really applies to the block K used in the candidate; it is
not a bound for a different narrow matrix. The product estimate
`log(c_b^-1)<=pi^2/(12 b rho)` gives
`c_b^-4<=exp(pi alpha^2 rho/3)=p^O(1)`. The reciprocal gap is also polynomial
because `theta^-1=poly(p)` and `alpha^2=O(log p)`.

The square identity-hole completion has block form `[A 0; R I]`. Its inverse is
`[A^-1 0; -R A^-1 I]`. Hence bounded Gaussian row sums and the selected-row
inverse bound give a polynomial full inverse bound. Dividing the completion
by four is contractive even on numerical hole errors. Its extra factor of
one half per axis is exactly compensated by the stated `2^D` shift.

For the Toeplitz core, the Poisson symbol bound supplies a polynomial lower
eigenvalue, since its exponent is `O(alpha^2)=O(log p)`. An exponentially small
truncation/rounding perturbation preserves that bound. The extension from
these SPD cores to shallow circuits is outside this subreview, but the
Gaussian side supplies the conditioning claimed for that extension.

## 3. Capping changes the runtime gauge, without changing H

Sources: candidate lines 203–221 and 273–283;
`work/gaussian_fast_ultra/CAPPED-GAUGE-AUDIT.md` lines 31–107;
`work/phase_assembly_ultra/CAPPED-INTERIORS.md` lines 13–29 and 68–70.

Within a fixed narrow phase cell,

`log(a_i/a_j)=a(i-j)(beta_i+beta_j)`.

Its absolute value is at most `a|i-j|`. Taking exact ratios of the already
rounded positive weights at one local anchor cancels the same common scalar
from both sides of the similarity, so the matrix is unchanged. Relative
rounding error of the original weights remains small because their minimum
is `exp(-O(ad))` and the absolute setup precision is `Cp`, with `ad=o(p)`.
Thus the local circuit sees range `O(aB)`, not the original `O(ad)`.

For the broad split, expansion of the displayed exponents gives exactly
`-b0(delta+x-lambda y)^2`. The two logarithmic derivatives are
`-2 b0 lambda beta'_i` and `2 b0 lambda^2 beta'_k`; each is bounded in absolute
value by b0. Changing anchor changes the two ideal diagonals by reciprocal
constants. Applying the same exact reciprocal change to previously rounded
diagonals preserves their product with the Toeplitz core. Thus the broad
rounding scheme can consistently use the same global matrix and locally
recenter its capped restrictions.

The number of pieces does not multiply the norm of their direct sum. The
group logarithmic range is consequently `O(gaB+g polylog p)`. The inherited
absolute weight accuracy adds `O(ad)` once to the precision requirement, rather
than once for every tensor axis. The candidate's condition
`beta+xi+r0=1-zeta`, with `a=O(log p)<=p^r0` eventually, makes this range o(p).
The total precision is therefore `p+O(ad+gaB+g polylog p)=O(p)` in both parameter
families. This conclusion concerns asymptotics; no reasonable finite cutoff
is supplied or required by the statement.

## 4. Boundary factorization and rounding do not introduce a window-count factor

Sources: candidate lines 225–240;
`work/gaussian_fast_ultra/LOG-A-PHASE-SCHUR-AUDIT.md` lines 78–98;
`work/integer-mult-current/references/semantic-bulk/rad20/reports/review-phase-cell-inverse.md`
lines 203–301.

The five-factor identities check by ordinary block multiplication. The shears
use B and C from the original banded matrix. They do not use the generally
dense products `A^-1 B` or `C A^-1`. For forward expansion, F is only applied;
its inverse is not required by that formula.

For a strictly row-diagonally-dominant matrix, one elimination step gives

`gap_i(new)>=gap_i(old)+|a_ik/a_kk| gap_k(old)`.

Its absolute row norm does not increase. Thus the narrow Schur matrix retains
the polynomial gap and bounded row norm. A noncyclic cut of its banded matrix
also retains row dominance. In its LU factors, U has bounded row norm and the
unit-lower factor has only O(W) entries per row, each bounded by the reciprocal
pivot gap. Therefore `||L||=poly(p)`. The identities
`L^-1=U A^-1` and `U^-1=A^-1 L` then give polynomial inverse-factor norms.
The periodic correction has rank O(W) and is controlled by the full completed
inverse, as in the retained identity `K^-1=I-V A^-1 U`.

The exact partial right-hand sides are consequently polynomially bounded.
Rounding a completed block update creates a row residual bounded by
`poly(p) 2^-P`. Equivalently, rounding and coefficient error can be treated as
a perturbation whose norm is small enough to close the same bound on computed
values. Applying the polynomial full inverse bounds the output error by that
residual. Infinity norm takes the maximum over windows rather than summing
their count. Strassen's fixed recursion contributes polynomial W growth and
O(log W) guard bits, already covered by the precision allowance.

## 5. Density, stream layout, and global calls

Sources: candidate lines 207–211, 242–271, and 368–385;
`work/phase_layout_audit_ultra/AUDIT.md` lines 15–188;
`work/phase_layout_audit_ultra/CAPPED-SIGNOFF.md` lines 7–65;
`work/phase_layout_audit_ultra/MATRIX-LAYOUT-SIGNOFF.md` lines 16–58;
`work/halo_layout_ultra/HALO-THEOREM.md` lines 88–196.

The capped carve contributes O(d/B+log B) separators per physical phase cell.
Retaining W-wide separators ensures distinct interiors are uncoupled. Each
elimination only joins adjacent O(W)-sized boundary groups, so the Schur
bandwidth remains O(W). The extra clipped-endpoint term in an L-core is
O(W polylog p), negligible relative to `L W/B polylog p`.

For the union U, every sparse factor changes its own axis only inside E_i;
therefore it preserves U. The dense A stage does not preserve U, and the
candidate explicitly scatters and regathers around it. For one sparse axis,
`U_i=E_i x [L]^(g-1)` is a complete rectangle inside U. Extracting it in order,
transposing only its polynomial-width axis field, processing, undoing the
transpose, and merging back needs no full g-axis key sort. The full union
scan is charged once per sparse axis, producing the stated g-squared factor
per group. The matrix corollary cannot afford an extra full-key union sort,
but this algorithm does not require one.

The q-image predicate checks the exact half-open interval
`s(2k-1)<=2tj<s(2k+1)`, including tie behavior. Because its product map is
increasing in every coordinate, source records are consumed and extracted
in ordinary lexicographic order. Doing embeddings before the global gather
and extractions after its inverse avoids a hidden long-axis transpose.

The global H call temporarily exposes the images of the selected original
K-bit neighborhoods under the known gather permutation. It need not retain
them as contiguous fields in the current layout. Under the stated supplier
endpoint contract, every completed call restores all borrowed/coarse bits.
Consequently local coefficient pages can be generated and scanned in restored
coarse-block order between calls; no random catalogue access is inferred.

The face-halo copy lemma uses only interval incidence and source provenance;
its volume and stream-order arguments do not require constant Gaussian
coefficients. In this use, local principal Gaussian maps replace the scalar
convolution arithmetic on the copied rectangles. They retain unprocessed
input halos until the relevant axis is evaluated, which is essential to the
tensor error estimate. The candidate explicitly avoids recycling inaccurate
dense edge outputs as halos.

## Audit boundary

The layout subreview independently checked 2,144 q-image parameter pairs,
1,831 capped partitions, and 2,368 corrected outputs of a position-dependent
three-axis band map using 11,712 halo copies. Its separate fixed-tape micro-review
found no missing transpose or batch-I/O factor. One nonblocking evidence limit
remains: `check_union.py` uses dictionaries rather than executing the tape
transposes, and its advertised two-window reuse is supplied by the closure
argument rather than by the script. This does not invalidate the written
implementation or change its exponent.

No candidate file was modified. The review found no counterexample requiring
the theorem or corollary to be blocked on Gaussian, density, precision, or
sparse-layout grounds. The conclusion remains conditional on the explicitly
stated supplier, endpoint-restoration, fixed-tape primitive, and semantic
precision interfaces. Arithmetic receipts and old PASS declarations alone
would not have established any of the arguments above.

## Reviewed source identities (SHA-256)

```
08ecb1876695beee25484158e14cfd57c3d48f551a8a41d5abc998d71d674555  work/phase_assembly_ultra/phase_fusion_note.tex
e05d6b8596c80b6e8676569a0ff464a29fa704c3304143f58914f47cdf38b272  work/gaussian_fast_ultra/LOG-A-PHASE-SCHUR-AUDIT.md
0d65e66d227464dda1a19f781ae0a0be671cbfd347c41e37ec954f3d629d8a77  work/gaussian_fast_ultra/BILATERAL-LDU.md
e37aaa30b15671a1dff00676b14572213efaaac99df202dbba5e09f57af487c0  work/gaussian_fast_ultra/FORWARD-SMALL-A-AUDIT.md
1030a34922709ab8d3434a4c57a4a58934ae268c237fb598cb415697da411c9f  work/gaussian_fast_ultra/CAPPED-GAUGE-AUDIT.md
54aafc7afd09fe1a5312e69fad09c87422690543ab75c6ae35f6cbcc26b3eb8a  work/phase_layout_audit_ultra/AUDIT.md
cb9e1da38400b658f9209e465b4e5896fadd17dc66afa862f38bae8d8c1f2058  work/halo_layout_ultra/HALO-THEOREM.md
```
