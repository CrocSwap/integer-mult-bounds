# Outer reduction: deferred reservations and batched Gaussian solves

**Status: two scoped construction refinements, one explicit conjectural route; no new final multiplication exponent.** The selected conditional exponent remains `0.001672660197076918`. The proposed target `0.00167498` below depends on a tensor-resampling lemma that is not proved here. This package does not change a selected certificate.

Base checkout: `work/integer-mult-current`, commit `e6f9716621f4e01fc190617934cdfaf072bd976f`. Prepared with substantial GPT-6.1-sol assistance. Apache-2.0; original sources and contributor credit are retained by reference.

## 1. Where the present loss occurs

Write `a` for the effective bit saving, `b` for the complex saving, `q` for the strict implemented complex-layer saving, `d=p^epsilon`, and `u=alpha^2=p^r`. The selected endpoint data are

```
b = 0.001675462676808103522925
a = 0.001733427039589844234749
kappa = 0.001672660197076918.
```

The current balanced outer construction has, up to strict backoffs, the two costs `V p^(1-epsilon*q)` and `V p^epsilon`; the second comes both from reserved/extra axes and from scalar/bulk-resampling passes. In addition, its reserved-axis treatment uses `K=d^c`, requires `c>q`, and requires `dK=o(p)`. Thus even if all Gaussian work disappeared, retaining that reservation argument would still force `epsilon<1/(1+q)`. It is insufficient to erase just the Gaussian row from a ledger.

The selected outer logic was read in `research/complex-pr615-ceiling/vendor/multicold/engines/outer.py`; its seven margins and 47 slacks match the current 1094 assembly. The underlying detailed interfaces are in upstream sections 02, 04, 05, 06, 07, 08, 09, 10 and the cited `references/semantic-bulk/rad20/reports/` transfer notes. In particular, the current bulk Gaussian proof already uses local principal windows and short fields; proposing that same improvement again would not change the selected result.

## 2. Deferred reservations: removing the power-width reservation condition

This is an all-size **conditional transfer argument**, assuming the retained complete rectangular compact gadget, exact common-frame circuit, arbitrary coordinate router, and linear semantic guard. It does not require a new finite supplier identity.

Let `G=4 ceil(log2 p)+6`, and choose `K=128G`. At a layer on `h` still-unprocessed selected bits, reserve enough complete K-bit chunks to provide the two front H-bit fields, one back H-bit field, and row bits, where `H=hG`. The number of reserved chunks is

```
R(h) = ceil(3hG/K) + O(log h).
```

For `h` above a fixed polynomial in `log p`, `R(h) <= h/16`. Select those chunks from the still-unprocessed axes. Apply the retained compact circuit to the other `h-R(h)` bits, borrowing all three dirty fields from the reserved subset. At the completed-call boundary it is exactly `C` on the active bits and identity on every reserved or spectator bit, for arbitrary initial coefficients and arbitrary dirty addresses. Therefore all reserved bits retain their original complete ranges and can be processed next.

Repeat on the reserved subset. The processed subsets are disjoint. Stop once `h=polylog(p)` and apply those remaining kernels individually. This is **not** a recursive call on a truncated record or a clean-scratch claim: the entire original stream is still present, with the same full polynomial suffix, and every previously processed coordinate is an untouched spectator. Completed kernels on disjoint selected bits commute. All row padding is removed before moving to the next phase, so temporary factor-two padding never multiplies across phases.

To establish the time bound, retain the original `m,W,s` recurrence and stop its internal recursion at `d^beta`. With `sigma=1-b`, any `lambda>max(1-a,sigma)` gives, with logarithmic factors suppressed,

```
F(h) <= O(h^lambda + h^sigma d^(beta*(1-sigma)) + 1).
```

This follows because a packed local basis change has width `O(hG)` and hence cost `O(V h^(1-a) polylog p)`. The term formerly written `(h d^c)^(1-a)` is now `h^(1-a) polylog p`. All compact-gadget exceptional fractions remain polynomially small with K=128G; the retained repair proof uses the current call's O(p)-bit address and is not replaced by a global exception count.

Since `h_j <= d/16^j` above the polylogarithmic tail,

```
sum_j F(h_j)
  = O((d^lambda + d^(sigma+beta*(1-sigma))) polylog p).
```

The extra physical rearrangements of complete existing fields cost
`O(V p^(1-a) polylog p)` by the retained arbitrary coordinate router, over O(log d) phases. Its polynomial descriptor work is paid by the unchanged superpolynomial polynomial-record suffix, at every internal call. This is additive, not free routing.

Consequently, for every fixed `q < min(a,(1-beta)*b)`, the whole layer has

```
O(V [d^(1-q) + p^(1-a)] polylog p).
```

The common guard remains O(d): each completed phase changes semantic numerator/denominator bounds by O(h_j), and `sum h_j=O(d)`. Only the currently active phase contributes its internal excess. There is still exactly one truncation after the entire normalized layer. No power K=d^c and no condition c>q remains. K=o(ell) now follows from `ell=p^(1-epsilon)` for every fixed epsilon<1.

The extra top round on the long axes can use the same layer after a paid coordinate rearrangement collecting its selected bits and K-bit complete neighborhoods. The common rounds use a single paid global layout router, rather than `p/K` separate K-swaps. Thus the transformed version of the synthetic cost is

```
O(V [p^(1-a) + ell*d^(1-q)] polylog p).
```

This is the strongest positive transfer established by the present note. It removes the geometric source of `q/(1+q)` in the compact compiler. It does not remove the independent O(Vd) Gaussian and scalar costs.

### Checks

`check_constructions.py` checks 1,000 exact reservation schedules and 5,460 entries of actual Gaussian-rational `C` tensor matrices. Every axis is processed once; the phasewise output equals the independently calculated closed tensor matrix. Omitting the deferred subset is a retained failing control. These checks support the written argument; they are not an all-size compiler implementation.

## 3. Batched right-hand sides for the Gaussian boundary inverse

This refinement applies to the precomputed noncyclic banded L/U factors in the retained principal-window solver. It uses the many spectator lines carrying the same axis matrix.

For a triangular matrix with scalar bandwidth w, group consecutive rows into blocks of a power-of-two width `B in [w,2w)`. There is only one preceding block in a lower solve (one following block for an upper solve). Precompute each diagonal-block inverse. For B simultaneous right-hand sides, the update is

```
X_j = L_jj^-1 * (Y_j - L_j,j-1 * X_j-1).
```

Two B-by-B products implement each update. The seven-product identity gives `O(B^omega)` scalar operations, `omega=log_2(7)`. For z boundary rows and R>=B right-hand sides, splitting the columns into B-column batches gives

```
O(z R B^(omega-2))
```

scalar work. Incomplete edge blocks and the last RHS batch are zero-padded only for the current product; this is a constant temporary volume increase, not a tensor-axis padding factor. The matrices may vary from row block to row block. No Toeplitz assumption is made.

The original boundary has `z=O(M w/d + w)` rows in a length-M local window. Summed over axes and lines, the old regular contribution `V w^2` becomes

```
O(V w^(omega-1) polylog p).
```

The artificial-end contribution is handled by a polynomial-size microbox L; it is
`O(V d w^(omega-1)/L polylog p)`. The O(Vd polylog p) local field motion and interior-convolution cost is still paid and is still present.

### Tape layout

Expose the same axis and factor page used by the retained solver. Gather B adjacent RHS indices with a B-valued local field, moving that O(log p)-bit field across the current row field by the retained small-field transposition. It costs O(V log p) per axis. This charge belongs to the existing d-pass term. Read factor pages and RHS row blocks sequentially. Keep the immediately preceding solved B-by-B block on a fixed work tape. Products use a depth-first seven-product recursion, parking/restoring the other finitely many matrices at each node; scanning and quadrant rearrangement is O(B^2) per level and is dominated by B^omega. There is no random factor lookup and no separate tape for every RHS.

### Precision

Keep the retained O(p)-bit rounded factor entries and compute each B-by-B product exactly as a dyadic matrix product before one component rounding. An individual seven-product recursion has depth log B. Additions grow integers by only O(log B) bits at every product boundary, so exact products and their sums have O(p+log B)=O(p) bits. A block inverse is precomputed at the retained high precision, with its row-norm perturbation charged explicitly.

Round after a completed block update, not between scalar products. The residual of the completed triangular system is bounded rowwise by `poly(p)*2^-P*(1+||X||)`, with P the retained large constant multiple of p. The retained inverse-norm bounds then give a uniform global solution error after absorption, independent of the number of row blocks. This is the same residual closure used by the original banded solver; it must be instantiated with new block-factor rounding constants in any adoption. An unproved claim of numerical stability of fast floating-point multiplication is unnecessary.

For `u=p^r`, `w^2=O(p^(1-r))`. The revised regular boundary exponent is

```
((omega-1)/2)*(1-r),
```

whose saving at r=0 is `(3-log_2 7)/2 > 0.096`. Thus an implemented version could remove the old requirement r>kappa while keeping `epsilon+r<1`. It cannot remove the separate O(Vd) scan term by itself.

### Exact checks and remaining check

The script independently compares seven-product multiplication against classical multiplication, then compares 60 varied-size blocked triangular solves against exact Gaussian-elimination inverses (1,976 output entries). A dropped-predecessor-block control fails. This establishes finite algebraic orientation, padding and dependencies. A complete adaptation of the original numerical residual constants is still required before adopting the changed analytic interface.

## 4. A concrete route toward tensor Gaussian fusion

This section is **conjectural construction work**, not an established algorithm. The missing step is stated so it can be attacked.

A possible way to avoid d separate Gaussian passes is to compute the tensor Gaussian on a microbox through one tensor convolution. For `rho=s/t`, a real Gaussian row has the exact scalar identity

```
exp[-a(j-rho*k)^2]
 = exp[-a(1-rho)j^2]
   exp[+a*rho(1-rho)k^2]
   exp[-a*rho(j-k)^2].
```

Integer translations of j and k add only linear factors, so each local rectangle is a diagonal, Toeplitz convolution, diagonal. Across axes, the diagonal factors fuse into one per-record multiplication. The central convolution is a tensor cyclic convolution after sufficient halos.

With the current theta≈1/d, a local Gaussian halo has radius
`A=O(alpha*sqrt(p))`. To keep product halo volume constant, the core needs length `L=Omega(dA)`. But the fused diagonal logarithmic range is then
`O(d*theta*L^2/alpha^2)=O(d^2 p)`, not O(p). Thus the most obvious tensor-chirp fusion fails its precision ledger. This explicit failure should prevent a false positive.

One changed hypothesis makes that favorable: choose source primes much closer to t, with `theta=Theta(d^-3)`. Then at `L=Theta(dA)`, that logarithmic range is O(p), and the product halo overhead is still constant. Such prime lengths are available eventually for every fixed epsilon<1: the explicit prime-counting error from Fiori–Kadiri–Swidinsky, Corollary 22, is `O(x sqrt(log x) exp(-c sqrt(log x)))`; on an interval of width `x/d^3`, with `log x=Theta(p^(1-epsilon))`, its error is o(x/(d^3 log x)). The interval contains far more than d primes, so distinct choices and `S/T=1-o(1)` follow. Trial division setup remains `n^o(1)`. This is an asymptotic existence argument with an enormous cutoff, not a practical prime-search claim.

However two serious costs remain unproved:

1. A power-of-two convolution window N has a useful core N-2A. Reinterpreting an axis by these variable non-dyadic cores is not the known binary-coordinate router. Padding every N-2A field to the next power of two costs 2^d. Performing the known small-field reshape one axis at a time costs Vd. A new simultaneous variable-core gather/scatter is needed, with full payload movement charged.
2. The inverse Gaussian correction is not itself one convolution. With theta=d^-3, the current phase-cell similarity weights range like `exp(O(u/theta))`, too large for its old O(p)-bit proof. The generic banded solve can avoid those enormous weights, but the present batched bound still has a d factor outside its favorable structured regime. The tensor inverse needs a different stable factorization or a sparse-boundary construction with a fully paid ledger.

Therefore “choose closer primes” plus “use a multidimensional FFT” is not a proved bypass. It is an explicit construction program with two specified lemmas.

## 5. Exact optimistic target and fully paid comparison

Assume a new tensor-resampling interface gives

```
O(V [p^(1-a) + d^(1-q) + w^(omega-1)] polylog p)
```

for the complete expansion and inverse, including variable-core layout, coefficient factors, stable inverse, all restoration and only O(p)-bit records. Combine it with Section 2. The complete normalized saving is at least

```
min(a, epsilon*q, 1-epsilon*(1-q),
    1-((omega-1)/2)*(1-r), epsilon),
```

with strict `epsilon+r<1`, `q<min(a,(1-beta)b)`, and sufficiently small fixed logarithmic absorption margins. The selected endpoints admit the exact sample

```
q       = 67/40000       = 0.001675
epsilon = 99999/100000   = 0.99999
r       = 1/200000       = 0.000005
beta    = 1/100000
kappa   = 83749/50000000 = 0.00167498.
```

Here `epsilon*q-kappa = 13/4000000000 > 0`, the complex endpoint exceeds q by `0.000000462676808103522925`, and the gamma gap is `0.000005`. The target exceeds the selected kappa by `0.000002319802923082` (about 0.1386894%). Letting epsilon approach one and q approach b would recover the complex saving itself, up to arbitrary strict slack.

**Fully paid ledger today:** without the unproved tensor-resampling interface, the unchanged Vd term remains. It imposes `kappa<1-epsilon`, so maximizing the proven/reused terms still gives at most `b/(1+b)`. Sections 2 and 3 alone do not improve final kappa. Under the displayed sample, the paid Gaussian margin is only `0.00001`, so that sample FAILS the current interface. It is deliberately not emitted as a passing outer certificate.

## 6. Reproduction and evidence

Run from the parent workspace:

```
python3 work/radical_reduction_ultra/check_constructions.py
python3 work/radical_reduction_ultra/check_ledger.py
```

`CONTROLS.json` contains exact finite controls. `LEDGER.json` contains the optimistic row and the correctly rejected fully paid row. Neither imports a producer or mutates the source checkout.

## Open next questions

- Instantiate Section 2 against the exact current compact field-layout code and reject malformed reservoir choices. This is a bounded integration task; it could remove a real interface restriction even before a new final exponent is obtained.
- Carry the block residual argument in Section 3 through the retained P=32768p constants and factor-page format. The algebraic and layout reductions are explicit; numerical certification is the remaining bounded task.
- For the fusion program, first prove or disprove a simultaneous variable-core gather/scatter with O(V p^(1-a) polylog p) cost and no 2^d padding. This isolates the data-layout bottleneck before more analytic effort.
- Seek a stable tensor inverse for near-identity Gaussian resampling with theta≈d^-3 that avoids both enormous diagonal similarities and d sequential full scans. A finite small-d result is not enough; require the exact operator, record width and mass recurrence.

## Primary sources and attribution

- CrocSwap/integer-mult-bounds pinned upstream and transfer reports, in particular 02-streams, 04-swap, 05-layers, 06-transforms, 07-resampling, 08-assembly, 09-exact-arithmetic, 10-transposition; reviewed contributions by Douglas Colkitt and the cited independent contributors are retained unchanged.
- Harvey and van der Hoeven's original Gaussian resampling and multiplication interfaces are inherited through those source proofs.
- V. Strassen, *Gaussian Elimination is Not Optimal*, Numerische Mathematik 13 (1969), 354–356, DOI `10.1007/BF02165411`. The seven-product identity is reproduced and independently checked here; no modern matrix multiplication exponent is needed.
- A. Fiori, H. Kadiri, J. Swidinsky, *Sharper bounds for the error term in the prime number theorem*, arXiv:2206.12557v2, Corollary 22: https://arxiv.org/pdf/2206.12557 . Used only for the clearly marked close-prime construction program.

## Later constructive developments

The positive interpolation-tree and global two-tail results are in `STABLE-POSITIVE-TREE.md`, with exact controls in `POSITIVE-TREE-CONTROLS.json`. They provide bounded gauges for every signed-data intermediate and show that all high-level rank-one contributions collapse to two global running sums. Its Section 6 gives a normalized Sylvester factorization into a dirty Toeplitz shear, one well-conditioned full Toeplitz map, and one triangular Toeplitz map; `SYLVESTER-CONTROLS.json` checks that identity.

The stronger fixed-width Gaussian norm theorem is independently audited in `FIXED-A-PERIODIC-NORM-AUDIT.md`, with `FIXED-A-LDU-CONTROLS.json`. It replaces the earlier sufficient logarithmic-width condition: for any fixed admissible a>=1, the periodic inverse has norm O(theta^-2). This is an analytic parameter improvement, not a completed fast inverse.

The outer partial-fusion candidate in `PARTIAL-FUSION.md` remains prospective. Neither the stable, shallow in-place algebra for plain Toeplitz matrices nor bounded final Gaussian conditioning alone proves that the curved Gaussian coefficient gauges can be processed with only O(p) total guard bits when many axes are fused. That interface, and the actual halo movement cost, must be resolved before claiming a new kappa.
