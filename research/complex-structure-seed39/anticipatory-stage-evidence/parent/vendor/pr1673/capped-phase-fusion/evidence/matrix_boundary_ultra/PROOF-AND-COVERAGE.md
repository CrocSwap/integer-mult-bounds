# Matrix boundary transfer: full-source audit and interface signoff

Status: the supplied 9/4 source supports the matrix boundary substitution, with strict exponent slack. This is a theorem-level, computable asymptotic transfer. It is not a numerical finite-size rank certificate and it does not remove any supplier or computational-interface assumptions in the outer integer-multiplication argument.

The independent reader for this note read all 1,022 lines of
`/Users/vlado/Downloads/math-main/preprints/Matrix-Multiplication-Nine-Fourths-October-2-2026/build/paper.tex`
in order, including the full character-existence appendix and all bibliography entries, and also read the README. The companion 2.258 paper is unnecessary for this transfer and is not claimed as read in this new audit.

## 1. Source coverage

| Source lines | Material read | Audit result |
|---|---|---|
| 1–36 | Preamble, title, abstract | Establishes complex arithmetic setting. |
| 37–141 | Introduction, theorem and proof route | Explicitly promises an asymptotic exponent, not a competitive finite size. |
| 142–203 | Tensor semiring, rank, characters, detecting lemma | Uses exact rank and mutual restriction. Rank need only be subadditive; no false additivity assumption. |
| 204–235 | Oriented dot-product exponents | Monotonic completely multiplicative functions give power laws; tensor product of the three orientations is square matrix multiplication. |
| 236–269 | Degenerations and interpolation | Fixed degeneration degree is handled before the tensor-power limit. No uniform-in-power degree assumption is made. |
| 270–349 | Finite shared-leg separation | Fourier relation is exact since the phase has absolute size below 5M. Surviving weights equal `(g-h)^2`; the retained auxiliary dot index is distinct from the direct-sum block index. |
| 350–391 | Shared-leg entropy | The factor M cancels correctly before the N-th-root limit. Fixed-frequency counts and continuity cover every probability vector. |
| 392–432 | Polynomial multiplication and symmetrized profile | Rank is exactly a+b−1 by interpolation and output flattening. All six leg permutations are needed for the later middle branch. |
| 433–523 | Determinant filtration and discrete concavity | Fixed input/output bases work for every first-input slice. Multiplication preserves the determinant submodule; the forbidden upper-right block vanishes. The residual lower-left block receives positive weight. |
| 524–604 | Three sectors and shifted tripling | Outer sectors equal C(a,h); the middle is obtained by reversing the first basis and exchanging its second/third legs. This is an identification of an individual block and does not apply incompatible maps to the shared first leg. |
| 605–651 | Diagonal growth | Concavity gives the stated two-increment recurrence; H_a grows at least as a^(1/3). |
| 652–689 | Spectral bound, rank bound, recursion | Detecting characters may depend on d. The conclusion is `nu<=9/4`; selecting a fixed rank scheme requires a strict larger exponent. Rectangular block substitution preserves product order. |
| 690–699 | Algebraic-coefficient remark | The source explicitly allows replacing a complex solution of rational rank equations by a point over Qbar. |
| 700–769 | Appendix: invariant state family and multiplicativity | The fixed-point map is continuous, not asserted affine. Freezing its scalar eigenvalue produces a compact convex invariant subset, permitting finite intersections. |
| 770–905 | Appendix: detecting state existence | Finite rational separation gives an additive catalyst. Reuse keeps one s factor; no tensor cancellation is assumed. Amplification with a second multiplication tensor gives the contradiction to k<d^nu. |
| 906–1022 | Complete bibliography and document ending | Cited items below are attribution or standard background; no unprovided local proof dependency is silently assumed. |

## 2. Dependency closure of the supplied argument

The paper's proof of the exponent does not require trusting another local preprint's new theorem. It proves its own required interpolation statement, finite shared-leg separation, entropy passage, determinant compatibility, tripling, diagonal growth, and detecting-character lemma.

The historical Bini citation is accompanied by the complete coefficient-interpolation argument. The Kowalski citation is accompanied by the exact determinant sequence and its compatibility proof. The Strassen/CVZ spectral citations are accompanied by the full special existence argument in the appendix. The Le Gall citations identify the familiar counting and leg-balancing ideas; the needed counting limit and application are given explicitly.

Remaining standard mathematical ingredients are polynomial interpolation over C, flattening rank, Stirling's factorial estimate, finite-dimensional separation/rational feasibility, compactness of products, Schauder–Tychonoff, and the weak Nullstellensatz over the algebraic closure of Q. None conceals an algorithmic or bit-complexity claim. The fixed-point and compactness arguments are used solely to prove that a finite rank decomposition exists. The effective selection below does not attempt to numerically approximate their characters.

## 3. Effective finite selection and approximate bit arithmetic

`ALGEBRAIC-STABILITY-INDEPENDENT.md` gives the full standalone proof. The decisive points are:

1. Fix a rational exponent `tau` strictly between 9/4 and 5/2; `19/8` is sufficient. Exact-rank exponent `nu<=9/4` supplies integers u,r with `r<u^tau` and a rank-r decomposition of u-square multiplication.
2. The rank equations are finitely many polynomial equations over Z. A solution over C implies one over Qbar, with the same u,r. Arbitrary noncomputable complex constants are therefore unnecessary.
3. Enumerate u,r and algebraic coefficient tuples, dovetailing exact equality tests of all rank equations. For rational `tau=a/d`, the exponent check is the integer inequality `r^d<u^a`. Existence proves termination. The first successful tuple is a fixed, computable block formula; the search is independent of p and W.
4. Once that tuple is fixed, every coefficient has fixed degree, height, and root separation. Isolated simple-root Newton iteration at doubling precision computes all finitely many coefficients in `O(M(P))` total bit time under the ordinary regularity assumptions on M.
5. For W-square matrices, pad to the next u-power and recurse. Arithmetic count is `O(W^tau)`. If rank equals u², its logarithmic recursion overhead is absorbed by the strict exponent slack.
6. Fixed-depth-in-base recursive bilinearity implies a polynomial-in-W growth and error bound. In particular, the error envelopes satisfy `E_j <= K E_(j-1)+K u^(j-1)` for a fixed K. Thus E_j is at most a fixed constant to the j-th power, hence `W^O(1)`.
7. If input entries have magnitudes at most `2^h`, `p+2h+O(log W)` fractional bits suffice for absolute entrywise error `2^-p`. Integer width is `O(h+log W)`. Total working width is `O(p+h+log W)`.

For the present boundary interface, matrix entries have O(p)-bit encodings, `h=O(p)`, and `W=O(sqrt(p) polylog p)`. Therefore one W-square product costs

`O(W^tau M(p))`, with any fixed rational `tau>9/4`.

If the surrounding proof allows polylog p factors, the bandwidth's polylogs remain polylogs; no positive power of p is introduced by coefficient approximation or error amplification. The algorithm provides absolute accuracy, which is what local residual bounds use. It makes no relative-error promise for nearly canceled output entries.

The recursion can also be scheduled with sequential tapes. At one fixed-base node, its fixed number of input block combinations and output block sums require a fixed number of complete scans and fixed block permutations of `O(n^2)` records. Store child inputs consecutively, process children depth-first, and stream their returned blocks into accumulators. Copying a pending-child region or repositioning a finite set of tapes costs another `O(n^2)`-record pass at that node, already covered by the recurrence's addition term. Addresses and recursion descriptions add at most logarithmic factors. If any implementation retains an additional `polylog W` factor, choose the rank scheme first with exponent strictly between 9/4 and the stated target tau, leaving enough fixed exponent slack to absorb it. No algebraic unit-cost random-access assumption is needed for the target power tau.

## 4. Boundary substitution and the outer ledger

The existing capped boundary algebra uses W simultaneous right-hand sides. A square product costs `O(W^tau M(p))`; dividing by W² processed entries gives `O(W^(tau-2) M(p))` per entry. One axis has `O(V W/B)` boundary entries, and there are d axes. Its total is consequently

`O(V (d/B) W^(tau-1) [M(p)/p] polylog p)`

when V is the total bit volume, as in the phase-assembly notes. There are V/Theta(p) scalar entries, so the factor M(p)/p is the per-bit arithmetic charge. Equivalently, if V counts scalar entries instead, the formula has M(p) without the division. The retained quasi-linear short multiplier has M(p)/p=polylog p.

This retains the essential d/B factor. With `d=p^epsilon`, `B=p^b`, and `W=p^(1/2) polylog p`, its normalized exponent is

`epsilon-b+(tau-1)/2`.

Taking `tau=19/8` gives `(tau-1)/2=11/16` and boundary saving `5/16+b-epsilon`. This is already more than enough to put the basic sparse-union cost near the binding row at b near 3/4. Pushing tau down to the unattained endpoint 9/4 is unnecessary.

The changed matrix algorithm has the same input/output interface as the former Strassen product. It does not change the original Gaussian matrix, boundary support, anchored gauge, square-block inverse choice, or number of right-hand sides. The surrounding local-residual proof must still supply polynomial bounds on local exact inverses and partial right-hand sides. The new product's error is `poly(p)2^-P`, so that proof applies with a fixed larger guard constant.

The optional full-coordinate-key surcharge in the old arithmetic ledger would become binding if mechanically retained at b near 3/4. It is not part of the actual rectangle extraction/one-field transpose/ordered-merge algorithm, as confirmed by the separate phase-layout audit. Dropping it is a distinct layout fact, not a consequence of matrix multiplication. It must remain explicitly justified in the final outer ledger. All retained supplier assumptions remain in force.

No final improved outer exponent is claimed in this note; that requires the whole ledger and the independent group-layout/gauge checks.

## 5. Exact controls run in this audit

`check_source_constructions.py` uses only Python's exact rational arithmetic and writes `SOURCE-CONSTRUCTIONS.json`:

* Finite Fourier/separation support for M=1,...,12: the modular relation has no wraparound and zero weight is exactly g=h,u=v.
* Determinant change of basis for a=1,...,8 and b=2,...,8, for every first-input monomial: quotient and kernel diagonal slices are exactly the two claimed neighboring convolution tensors; the upper-right block vanishes.
* Three-sector identity for a,h=1,...,14: all weights are nonnegative and each of the three retained branches is exactly the claimed tensor after its permitted identification.
* Exact rational diagonal product lower bound through a=300.

All controls passed. They detect several relevant implementation mistakes but are not a finite substitute for the universal arguments above or for the theorem's nonconstructive rank-existence step.

## 6. Deliberate limitations

There is no generated competitive finite matrix scheme, no numeric claim about its constants, no use of a rank formula at exponent exactly 9/4, and no fast algorithm for finding the first successful algebraic tuple. The algorithm remains computable and uniform because the finite search halts under the proved existence statement and its cost is independent of the growing input. The outer conclusion remains conditional on exactly the previously retained supplier/computational assumptions.
