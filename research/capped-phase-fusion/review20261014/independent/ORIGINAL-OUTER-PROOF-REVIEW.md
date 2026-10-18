# Independent review of the original PR1673 outer proof

Review date: 14 October 2026. Scope: the capped phase-cell/Strassen theorem at published head `2569871ff906d2a2abfc86e97126ab9afe2e4a5a`, including its pinned T74 substitution. This is the original regime, with source-prime gaps of order `1/d`, not a later fine-prime or hybrid outer. The optional theorem assuming `omega_C <= 9/4` is outside this signoff.

**Conclusion.** The original outer construction supports the stated conditional final saving `0.001677160151714381` with the written qualifications below. The schedule, local circuit construction, Gaussian estimates, precision allowance and movement ledger can be proved independently of the parameter checker. There is a real citation/integration repair: the current T74 child list is mixed rank, so the literal uniform tree in `notes/compact-control-layout.tex` is insufficient. The weighted proof in `notes/endpoint-gauge-complex.tex` (the subsection beginning at line 186 at the reviewed head) and `notes/batched-complex-rows.tex` supplies the needed replacement. The full row stock must be used; a one-chunk row estimate is not justified. These are repairs to the proof's interface explanation, not a different exponent optimization.

This review does not independently admit the inherited T74/#1319 native supplier or prove its all-size semantic compiler. Those are separate prerequisites. In particular, finite replay of matrices or rational inequalities cannot prove the all-size theorem. The conclusion remains conditional on the exact common-frame mutable-source realization, whole-call hosting, linear semantic guard, fixed-tape kernels, prime packing and exact recovery stated in the published theorem. The reviewer request being addressed is [the PR1673 comment](https://github.com/CrocSwap/integer-mult-bounds/pull/1673#issuecomment-6172528048), fetched directly through the GitHub API. Its supplier admission part is handled separately in `../REVIEW-RESPONSE.md` and `../NATIVE-SUPPLEMENT.json`.

## Source boundary and pins

The primary object reviewed end to end is `research/capped-phase-fusion/phase_fusion_note.tex`. Its substantive publication commit is `d449b822c8a74ffa01b22058cfc042374b1a45cd`; the reviewed head adds the source/authorship presentation commit above. The package records publication base `a5d4f08ac102d1a6da301d89379c75285eca680e` and original research base `e6f9716621f4e01fc190617934cdfaf072bd976f`.

The complex supplier is PR1661 at `f852af5e178ce035cd46181a29d9330bcbcaa206`, source-manifest SHA256 `d90d49eaa68e48c6992a07972e736ef4b9cd80274361cbbc1ec980d43f29ad7f`. The published substitution uses the exact rational lower rate `b = 0.00167971337478`, not the displayed endpoint as an equality. Its native parameters are

```
m = 73, Wc = 66304,
H = {1:1559766, 2:337668, 3:278058, 4:84912,
     5:54612, 8:5328, 48:22748}.
```

The independent checker in this directory computes SHA256 for the actual proof and 22 supporting source files; see `source_sha256` in `ORIGINAL-OUTER-CONTROLS.json`. The package verifier runs it in a temporary copy, where it writes its own receipt. Source hashes bind this review to the files read, while Git pins bind their intended provenance. The new external layout review is pinned separately by the parent at philippeVV commit `d1e01310b92e9a9af90b89efe4f3f9aad466b8b1`; its row-stock invoice is explicitly distinguished below from our independently checked consequences.

The proof depends on the following specific source statements, rather than on the status label of an old receipt:

| Interface | Primary reviewed source and necessary content |
| --- | --- |
| Local reversible linear circuits | `SHALLOW-TOEPLITZ.md`: dirty Toeplitz shears, parallel triangular recursion, displacement generators, SPD extension and prefix bounds |
| Literal common tensor schedule | `TENSOR-COMPILER.md`: Beneš cycle coloring, fixed six-H words, direct Kronecker multiplication and odometer coefficient scans |
| Whole H call | `SUPPLIER-SUPPORT-AUDIT.md`, `SUPPORT-ADVERSARIAL-AUDIT.md`, `SUPPORT-ROUTER.md`: complete global ranges, support-local routing, dirty reservations, finite guard inequality and suffix construction |
| Mixed recursive widths | `notes/endpoint-gauge-complex.tex` and `notes/batched-complex-rows.tex`: residual rank concatenation, child volume `1/Wc`, actual longest depth and weighted stopped tree |
| Rounded narrow operator | `LOG-A-PHASE-SCHUR-AUDIT.md` and `references/semantic-bulk/rad20/reports/review-bulk-resampling.md`: one fixed structured rounding, strict row gap, locality, normalization and residual bounds |
| Broad operator | `BILATERAL-LDU.md`, `FORWARD-SMALL-A-AUDIT.md`: finite Gaussian conditioning, SPD Toeplitz core, identity-hole completion and forward-only Schur use |
| Capped factorization | `CAPPED-INTERIORS.md`, `CAPPED-GAUGE-AUDIT.md`: dyadic tail carving, unchanged rounded operator and anchored ratio range |
| Movement | `PHASE-LAYOUT-AUDIT.md`, `HALO-THEOREM.md`: complete extracted rectangles, two union windows, actual q-image ordering and source-driven sparse faces |

Some older supporting documents discuss the uncapped regime or label intermediate work prospective. They are used only for the identities actually cited. The new capped theorem must discharge the extra tensor, cap-gauge and layout steps; the proofs below do so. The `OUTER-AUDIT.md` ledger alone does not discharge them.

## 1. Exact scale and address model

Let `p = Theta(log n)` and let `V = Theta(n)` count **bits**, not coefficient records. Each record occupies `Theta(p)` bits. The inherited packing has `D=d-1=Theta(p^epsilon)` true source axes and dyadic target axes with

```
log s_i = Theta(p/d),
rho_i = t_i/s_i = 1+theta_i,
1/(4d) <= theta_i <= 1/(2d-1),
product_i t_i / product_i s_i < 2.
```

The true axes eventually exceed every fixed polynomial in `p`. Thus a `K=Theta(log p)` complete neighborhood at a selected local bit fits in one original axis, even when the group size `g` exceeds the bitlength of that axis. The total selected neighborhoods and control support are `O(g polylog p)=o(p)` because `beta<1`. No step needs `gK` bits within one axis.

Use `alpha=ceil(sqrt((4/pi) log(16p)))`, `u=alpha^2=Theta(log p)`, `a=pi u`, cap `B=2^floor(xi log2 p)`, core side `L=2^ceil(8 log2 p)`, group scale `g=floor(p^beta)`, physical bandwidth `W=O(sqrt(p) polylog p)` dominating **both** Gaussian maps, and locality radius `A=C_A p^3`. Constants `Wc` (supplier rows) and `W` (Gaussian bandwidth) are unrelated.

Partition the `D` axes into groups of size between `g/2` and `g`, for example by evenly splitting into `ceil(D/g)` consecutive groups. This harmless explicit choice avoids an unamortized last group of size one. All groups have `Theta(g)` axes because `beta<epsilon`. It changes no power in the ledger. Global one-axis coefficient setup is polynomial in `s_i,t_i,p`, hence `n^{o(1)}`. Per-coarse-block setup is polynomial in `p` and is charged to that block's `L^{Theta(g)}` payload, which is superpolynomial. One must not charge polynomial setup once globally and then access the resulting catalogue at no movement cost.

## 2. A simultaneous H call with the actual mixed tree

Set `G=4 ceil(log2 p)+6`, `K=128G`. The source finite guard actually needs `K >= G+4 ceil(log2 p)+10`; our choice satisfies it. It does not satisfy the stronger literal phrase `K/log p -> infinity`, so that phrase must not be cited as the hypothesis being used.

At current selected width `h`, expose complete neighborhoods by extending their prescribed placement to a permutation supported on at most `2hK` bit positions. The support router pays `O(V h^(1-a_eff) polylog p)`. Arbitrary intervening positions are spectators. A fixed coarse microbox lacks complete borrowed high bits; the H invocation must run on the complete global dyadic stream. Coarse labels may affect the diagonals between H stages, and are restored before those diagonal scans.

Reserve still-unprocessed chunks for the two front controls, one back control and complete row stock. Do not first transform their selected bits. At the admitted completed-call boundary, the active invocation is the desired tensor kernel on active bits and identity on all reserved/spectator coordinates, for arbitrary incoming data and dirt. This is exactly the property that allows reservation to be deferred. It is not a clean-work assumption. Row padding is added once for a phase, all descendants inherit it, and padding is removed after return and before another phase. Thus the temporary factor below two is not multiplied over axes or phases.

For T74 the longest recursive child is `48 floor(e/73)`. In particular, two child steps shrink at least by half since `2*48^2 < 73^2`; the actual depth `Dc(h)` is at most `2 log2 h+O(1)`. The row count must be divisible by the **product** of complex and nested bit stock factors sufficient for their respective depths. A maximum of the two stocks is insufficient. The corrected external invoice uses 2644 stock bits and 490 physical rows beyond live storage, giving row coefficient 19545 below 20161. These are fixed native quantities; they must not be mistaken for a proof of a 39-chunk aggregate row prefix before mixed and nested depths have been included.

For the asymptotic proof no small row constant is needed. Each supplier has a fixed stock factor and logarithmic depth. Even the conservative product over every nested bit depth along a complex stack has `log2(Q_rows)=O(log^2(hG))`. A complete K-bit row chunk supplies K binary row digits, so its chunk reservation is

```
q_rows = ceil(log2(Q_rows)/K)
       = O(log(h+1)+log log(p+2)+1),       h<=p,
R(h) <= 3h/128+O(log(h+1)+log log(p+2)+1).
```

Thus `R(h)<=h/16` above a fixed polynomial in log p; for example an adequately large fixed multiple of `(log p+1)^2` suffices. Process the smaller remaining selected width elementarily at polylogarithmic cost. The independent checker illustrates this consequence for an arbitrary conservative fixed stock coefficient and checks actual depth samples; it does not assert the unproved specific 39-chunk or 1050 threshold. Native row hosting and the physical invoice remain in the separate supplier admission. Nothing requires the erroneous one-row-chunk estimate.

Here is the required mixed-tree argument. At a node of width `e`, first process the `e mod 73` remainder axes individually; this costs `O(V_node)` and returns those axes as complete spectators. A rank-r residual creates a recursive call of width `r floor(e/73)` on one role with `V_node/Wc` volume. Signs and inverse slots use the admitted exact wrappers; they do not change the child rank. Let

```
Psi(t) = sum_r (H_r/Wc) (r/73)^t.
sigma = 1-b, tau=1-a_eff, delta=10^-9.
```

For each level, the sum of `V_node * e_node^sigma` is at most `Psi(sigma)` times the preceding level. Floors only decrease that sum. If `Psi(sigma)<1`, summing all levels is a geometric series, and the total stopped-leaf sigma-mass is at most `V_root h^sigma`. Leaves have width `<h^delta`, hence total elementary leaf cost is at most

```
O(V_root h^[sigma+delta(1-sigma)]).
```

For internal movement cost `O(V_node e_node^tau polylog p)`, if `sigma<=tau`, monotonicity gives `Psi(tau)<=Psi(sigma)<1`, so all internal costs total `O(V_root h^tau polylog p)`. If `sigma>tau`, every internal width is at least `h^delta` and `e^tau <= h^[delta(tau-sigma)] e^sigma`; the total exponent is therefore

```
chi = tau+(1-delta) max(sigma-tau,0).
```

This proves the bound for unequal depths. It does not replace every rank-r child by a rank-one child or apply a uniform-tree estimate to rank 48. In the original and T74 published choices `a_eff=b-5e-11`, so `sigma<tau` and `chi=tau`. The independent exact ledger verifies `(1-delta)b>a_eff>q`, including the strict leaf margin. Consequently a whole active phase costs `O(V h^(1-q) polylog p)`. The deferred widths satisfy `h_next<=h/16`, and summing this bound plus support routing over phases is geometric. Thus a complete global selected-bit call costs

```
O(V g^(1-q) polylog p),
```

including exposure, all internal adapters, row preparation, spectators, dirt and restoration under the native premises. The admitted kernel is `H0=H/2`; one exact `2^g` binary shift after the call supplies the raw H used below, at `O(V)` work and `O(g)` guard. The independent rational Taylor enclosure checks `Psi(1-b)<1` for the stated T74 rate, and rejects a specified rate just above the endpoint. This arithmetic supports the hypothesis but does not prove native admission.

The same deferred argument applies to the retained main synthetic transform: there are `Theta(p/d)` common rounds and the paid global coordinate layout. Its total is `O(V[p^(1-a_eff)+p d^-q] polylog p)`. The old power-width reservation constraint is removed. Retaining an old per-axis `Vd` movement or scalar pass would invalidate the stronger result; it is an explicit rejecting control below.

## 3. Local linear circuits and tensorization

The new dense work is on the existing `L` wires of each local axis. The local compiler needs no clean data coordinate. For a dirty shear `y+=T x`, split Toeplitz `T` into circulant and negacyclic parts, use FFTs on the two existing vectors, pointwise shears and inverse FFTs. No inverse Fourier multiplier is taken, so singular T is permitted.

For triangular Toeplitz multiplication, split `f(z)=e(z^2)+z o(z^2)`. Its block matrix is `[[E,ZO],[O,E]]`, with the commuting block LDU factors using `k=o/e` and child `s=e-z o^2/e`. Both child multiplications run in parallel. This gives depth `O(log^2 L)` rather than a sequential recurrence. For a full Toeplitz block, balanced elimination raises child displacement rank by at most one. A rank-`O(log L)` displacement representation yields `T=sum L(g_j) U(h_j)`. For a generator term choose `gamma>=2||h_j||_1`, set `P=I+U(h_j)/gamma` and perform

```
x <- P x; y += gamma L(g_j) x;
x <- P^-1 x; y -= gamma L(g_j) x.
```

The net is `y+=L(g_j)U(h_j)x` and x is restored. The triangular map P is uniformly close to I. Partial sums of generators are bounded additively, so their prefix bound is polynomial, not a product of one bound for every generator. Balanced recursion gives `O(log^4 L)` two-wire layers with polynomial prefix/inverse-prefix norms for near-identity matrices. For SPD `mu I<=G<=M I`, principal and Schur descendants retain these bounds. When `M` and `1/mu` are polynomial in p the logarithmic prefix bound is `O(log^2 p)`, also sufficient.

For arbitrary pair matchings, the degree-two bipartite graph of input and output pairs is a union of even cycles. Alternating edge colors gives the first/last Beneš switches and recurses on half as many wires. Thus every matching is routed by `2m-1` switch stages at `L=2^m`. The routing and reverse routing use `4(2m-1)` H factors. Every allowed local two-wire gate has a fixed six-H diagonal word, including identities and zero shears. In particular,

```
diag(-1/8,-1/6) H diag(2,1) H diag(-3,1) H = U(5/4).
```

For `U(t)`, write `U(t)=U(t+c)U(-c)` with a known `c>2|t|+1`; no division by t occurs, and both factors have controlled inverses. Therefore each original matching layer uses `8m+2` common H stages. Completed route/padding words are exact endpoint identities or permutations. At a compiled prefix only one constant-length gate word is partial, so its bound multiplies the original circuit prefix by a polynomial, not that polynomial raised to the number of layers.

The g axis circuits may differ by axis and coarse label. Pad their **operations** to the common schedule, tensor corresponding H factors and multiply the corresponding diagonal factors. This is the exact Kronecker product identity, not a sum over branches; data dimension remains `L^g`. There is no `2^g` data padding.

For each tensor diagonal `product_i d_i(x_i)`, cache suffix products in lexicographic odometer order. A carry of depth k occurs at most `L^g/L^k` times and recomputes O(k) products. The geometric sum `sum k/L^k` is finite. The coefficient tape visits and rewinds have sum `sum k L/L^k=O(1)` per record. Hence diagonal scans cost `O(V polylog p)`, not `Vg`. Regenerate each polynomial page from its actual coarse origin and amortize it over that block. No random catalogue access is assumed.

There are only polylog(p) compiled H calls. Section 2 prices each at `O(V g^(1-q) polylog p)` and each gather at `O(V g^(1-a_eff) polylog p)`. This is the dense group cost. The global completeness restriction survives coarse-dependent diagonals because placement is undone before each such scan.

## 4. The two Gaussian maps and the fixed rounded operator

The narrow inverse and broad forward matrix require different arguments. Treating them as the same near-identity matrix would be an error.

For narrow compression let `q_j=floor(rho j+1/2)` and `beta_j=rho j-q_j`. The retained selected normalized Gaussian N has

```
||N-I||_infinity <= exp(-2 a theta)+5 exp(-2a).
```

The two nearest directions must be paired in deriving this bound. Since `a>=4 log(16p)` and `theta>=1/(4p)`, there is row gap at least `1/(8p)` eventually. Set the diagonal to one and choose one global structured rounding: downward weights `omega_hat_j`, one rounded Toeplitz kernel `G_hat` within physical cells, exact entries `omega_hat_j G_hat_(j-k)/omega_hat_k` within a cell and the rounded original cross-cell entries elsewhere. With the retained `P=32768p` coefficient accuracy, the perturbation bound

```
p 2^(16p+7) 2^-P + 2^-46p < 1/(16p)
```

gives a rounded H with row gap `1/(16p)`, row norm below two and inverse norm at most `16p`. All principal submatrices inherit the gap. H is not silently replaced by an infinite or freshly rerounded Toeplitz matrix.

On the complete target grid use `Haug=EHC+(I-EC)`, where E injects at the increasing q-image and C selects it. This is permutation-similar to `H direct_sum I`, so holes are genuine identity coordinates and all inverse bounds persist on arbitrary signed input, including numerical hole errors. Physical target bandwidth is at most twice the source bandwidth plus two.

For broad expansion the actual rectangular map is `S_kj=alpha^-1 exp[-b0(j-lambda k)^2]`, `b0=pi/alpha^2`, `lambda=1/rho`. Complete it to a square target map M by giving each hole input an identity column. In selected/hole order M is block triangular with lower block `[R,I]`. Gaussian lattice-sum bounds give `||M||<3` eventually; `M/4` is contractive even on hole errors. The additional `2^-D` versus the old `S/2` normalization is compensated once by an exact `2^D` shift.

Inside a physical phase cell, a selected block has entries `alpha^-1 exp[-b0(i-c-lambda k)^2]`. The finite Gaussian LDU estimate in `BILATERAL-LDU.md` applies to every contiguous subblock: its ordered q'-coordinates have unit gaps and its phase beta' remains within one half, even when q' is not integral. The product `c_b=product_(m>=1)(1-exp(-2 b rho m))` obeys

```
log(c_b^-1) <= pi^2/(12 b rho),
||K^-1|| <= alpha exp(3b/4) c_b^-4 /(1-exp(-b rho theta))^2.
```

Here `b=pi/(alpha^2 rho^2)`, `alpha^2=O(log p)` and `theta^-1=poly(p)`, so this is polynomial in p. The anchored Toeplitz kernel `G_yx=exp[-b0 lambda(x-y)^2]` has symbol between `sqrt(pi/gamma)exp[-pi^2/(4gamma)]` and `1+sqrt(pi/gamma)`, with `gamma=b0 lambda`. Both bounds are polynomial in p. Symmetric sufficiently accurate rounding and truncation preserve SPD and its polynomial condition bound. This is the SPD case of the local compiler. For the complete broad forward factorization only the application of its Schur complement is required; no forward Schur inverse is needed.

For narrow elimination, the absolute row gap cannot decrease at a scalar Schur step:

```
gap_i(new) >= gap_i(old)+|a_ik/a_kk| gap_k(old).
```

The absolute row sum cannot increase, by the same triangle inequality and the pivot row gap. Pivots remain positive. Thus the narrow Schur complement and principal interior inverses have polynomial bounds; rounding below `1/(32p)` preserves them. Keeping whole neighboring boundary groups avoids an unjustified prefix-solve gap assertion.

## 5. Capped gauge, five factors and the two sparse windows

Within each original phase cell reserve W endpoints; greedily take dyadic interiors of size at most B separated by W; finish by halving the residual tail until O(W) remains. There are `O(d/B+log B)` pieces, so boundary fraction is `O((W/B) polylog p)`. Eliminating an interior connects only its two neighboring O(W) boundary groups. Therefore Schur bandwidth is O(W), independent of the number of caps. All holes and physical period cuts are boundary coordinates. Interiors are actual consecutive selected coordinates, not a masked Toeplitz matrix.

For narrow weights `omega_j=exp[-a(1/4-beta_j^2)/theta]`, one-step logarithmic variation is `2a beta_j+a theta=O(a)`. Recenter on the cap anchor using the **same rounded weights**: the common `omega_hat_m` cancels exactly from the similarity. The range is `O(aB)`, while the old absolute `O(ad)` scale is paid once in coefficient construction. For broad row/column gauges, the anchored exponent range is `O((B+B^2/d)/alpha^2)=O(B/alpha^2)`, bounded by O(aB). Direct sums of capped blocks take the maximum depth and range, not the sum over caps.

Write `Q=[[A,B1],[C1,D1]]`, `F=D1-C1 A^-1 B1`. Direct block multiplication proves

```
Q^-1 = diag(A^-1,I) E_-B1 diag(A,F^-1) E_-C1 diag(A^-1,I),
Q    = diag(A,I) E_C1 diag(A^-1,F) E_B1 diag(A,I).
```

These use the original banded B1,C1, not dense A^-1 B1 or C1 A^-1 disguised as sparse shears. In execution there are three dense A/A^-1 rounds and two sparse windows; the middle dense and boundary diagonal commute. Define Ei to include boundary Ji and all interior coordinates incident to original B1,C1. Then `|Ei|/L=O((W/B) polylog p)` and every sparse factor is identity off Ei. The union `U={x: some xi in Ei}` is invariant under every sparse factor and contains the complete rectangle `Ui=Ei x [L]^(g-1)` for each i. It is not invariant under dense A. Scatter before the middle dense stage and regather afterward.

Keep U in its native local lexicographic order. For axis i, scan U and extract Ui, relabel Ei by increasing stream-counter ordinal, transpose only this at-most-L-valued field, apply the boundary operation, undo the small-field transpose and ordered-merge it back. No missing values are invented as zero. Only the current polynomial field is padded below factor two, and padding is deleted before the next field. One window costs `O(V g^2 W/B polylog p)` per group; two windows only change the constant. Across `Theta(d/g)` groups the charge is `O(V d g W/B polylog p)`. Forming and scattering U costs a fixed number of full scans per group.

For boundary arithmetic batch independent right-hand sides in a dyadic width between W and 2W. The remaining coordinates provide superpolynomially many RHS. A width-W triangular block update uses two W-square products; original boundary couplings and the broad Schur application use the same batched products. Strassen's exact seven-product identity has `omega=log2 7<45/16`, proved here by integer comparison `7^16<2^45`. The number of boundary rows is `O((W/B)L polylog p)`. Hence the whole d-axis boundary charge is

```
O(V (d/B) W^(omega-1) polylog p).
```

V is bit volume, so a scalar product's `M(p)` cost is divided by the `Theta(p)` record width: the short-arithmetic multiplier is `M(p)/p=polylog p`. No improved integer multiplication result is used recursively here. The factor pages and RHS batches are read sequentially with a fixed number of tapes, and only the polynomial row/batch fields are transposed.

Round after each completed block update. A fixed-depth seven-product recursion has polynomial growth in W; exact dyadic products need O(p+log W)=O(p) bits. The residual of each completed local system is `poly(p)2^-P(1+||X||)`. Polynomial inverse bounds then control the solution error uniformly. This is a residual argument for each polynomial-size local window, not a claimed stable floating-point algorithm and not a product of amplification over the global number of windows.

## 6. Embedding order, halos and precision closure

The q-image scan is exact and monotone. For target k put `j=max(0,ceil(s(2k-1)/(2t)))`; it is in the image exactly when `j<s` and `2tj<s(2k+1)`. These inequalities include half-integer ties correctly. The tensor product preserves lexicographic order of its image. A target-group scan therefore consumes the ordered source stream or writes zero, with no source permutation. Every intermediate expansion has volume at most the final factor below two.

Do **all** forward group embeddings in native axis-major order before the low-bit microbox gather. Retain the full target coordinate ranges during every Gaussian/H operation. Do all compression extractions after the inverse gather. This is what makes both the ordered embedding and global complete H calls legal. It does not require gathering complete long-axis fields inside a fixed microbox. Grouped chirps and normalizations use the same product-diagonal scan as Section 3.

For locality, let `F=Haug-I` with row norm at most `1-1/(16p)`. At distance more than JW from a principal cut, the first J powers of F in the global and principal matrices agree. The tail difference is at most `32p exp[-J/(16p)]`. Choose `J=C p^2`; since `W=O(sqrt(p) polylog p)`, a sufficiently large fixed `A=C_A p^3` dominates JW and gives exponential accuracy. Physical period cuts are actual boundaries and the true axis is much longer than the local window. Broad expansion has direct truncated-band locality.

Dense work acts on L-cores only. Discard outputs within O(A) of any core face. Partition discarded outputs by their first exceptional axis and side. The exact source-rectangle copy volume, in tile units, is

```
6A sum_(j=0)^(g-1) L^j (L+2A)^(g-1-j)
   = 3[(L+2A)^g-L^g].
```

Since gA/L tends to zero, the total copied volume is O(V gA/L), including corner duplication. The source-driven copying uses actual interval geometry, so it also works for position-dependent Gaussian coefficients: on each rectangle use the true origins, coefficients and physical cuts. Unprocessed axes keep their halo until their pass, then crop. Incorrect dense-edge outputs are never used as halo input. Temporary padding is for the current short field only; there is no `(2L)^g` allocation.

Sparse radix keys have O(g log s) bits. Each key pass, copy and short-field transpose is paid. A generous bound p^2 polylog(p) per record per sequential one-axis correction pass yields, over all groups,

```
O(V (d/g)(gA/L) g p^2 polylog p)
 = O(V p^(epsilon+beta-3) polylog p).
```

The copy-enumeration overhead and key-square metadata arithmetic also fit this generous polynomial. This is a stated bounded power, not permission for an unspecified polynomial to be free. The core side p^8 was chosen to make this sparse path negligible.

The online group prefix/suffix logarithmic range is `O(g a B+g polylog p)`. Since `beta+xi+r0=1-zeta` and `a=O(log p)<=p^r0` eventually, that range is o(p). The inherited absolute coefficient range `ad` is also o(p) because `epsilon+r0<1`. Therefore

```
P = p+O(ad+g a B+g polylog p) = O(p)
```

is sufficient with a fixed large constant. The ad term is not charged once for every tensor factor; symbolic anchoring of the same rounded operator is essential. Completed normalized groups are contractive, so local errors add across polynomially many groups/stages, giving the retained loose `d p^2 2^-p` error interface after allocating a sufficiently small per-operation tolerance. The scalar normalization exponent is `O(d u)=o(p)`, including the extra D forward shift. The retained exact arithmetic/recovery interface then applies.

There is a minor inherited constant worth making explicit. `review-bulk-resampling.md` gives `j_scale=ceil(log2(32p))` and old compression bounds 1/4 and 1/8 using old inverse constants. The new H bound is 16p. The same 32p denominator still makes the map at most 1/2, which suffices for contraction. To retain the literal stronger constants, choose 64p or 128p instead. This adds only O(d) normalization bits and changes no exponent. The published theorem does not fix the obsolete 1/8 constant, so its contraction assertion is repairable by this explicit choice.

Membership calculations cost `O(g(log s)^2 polylog p)` per p-bit record, with exponent `beta+2(1-epsilon)<1`; all are absorbed by one record scan. Sparse keys also fit O(p) bits. Local coefficient generation uses centered exponents and O(p/d)-bit origins, never raw unbounded global exponentials as data values. These facts close the precision and movement interfaces used in the ledger.

## 7. Complete original ledger and its exact closure

Up to fixed polylogarithms, the charges after division by V are the following. Every row has a constructive source above; none is deleted solely because an inequality checker passes.

| Paid component | Normalized cost | Exponent in p |
| --- | --- | --- |
| Main synthetic transform | `p d^-q` | `1-epsilon q` |
| Global coordinate layout | `p^(1-a_eff)` | `1-a_eff` |
| Dense fused Gaussian groups | `d g^-q` | `epsilon-q beta` |
| Grouped bit routing | `d g^-a_eff` | `epsilon-a_eff beta` |
| Group scans, q-images, scalar products | `d/g` | `epsilon-beta` |
| Batched boundary products/solves | `(d/B) W^(omega-1)` | `< epsilon-xi+29/32` |
| Two sparse-union windows | `d g W/B` | `epsilon+beta+1/2-xi` |
| Optional conservative union key sort | previous row times `g log s` | `2beta+3/2-xi` |
| Packed polynomial products | retained packing term | `1-epsilon` |
| Source-driven face corrections | `(d/g)(gA/L)g p^2` | `epsilon+beta-3` |

The actual union rectangle method needs no union sort; this original regime can afford even the conservative optional row, so keeping it is safe. All microhalo sorts remain charged. Whole-row padding has constant factor below two per phase and is removed; current single-field/RHS product padding has constant factor and is also removed. There is no volume factor raised to g. The setup terms are n^{o(1)} or amortized polynomial pages, as explained in Section 1.

Put `q=b-10^-10`, `a_eff=(b+q)/2`, `r0=10^-6`, `zeta=10^-8`, `s0=10^-5`, `c0=3/32`. Solve

```
epsilon q = 1-epsilon+q beta,
1-epsilon+xi-29/32 = epsilon q+s0,
beta+xi+r0+zeta=1.
```

This gives exactly the published formulas

```
epsilon=(1+q+q(c0-s0-r0-zeta))/(1+q)^2,
xi=epsilon(1+q)-c0+s0,
beta=1-xi-r0-zeta.
```

All other paid rows have strictly greater saving. The independent rational checker reconstructs these equations and both published cases without importing the published ledger:

| Input | Derived final kappa after decimal truncation and 1e-11 backoff |
| --- | --- |
| Original selected `b=0.001675462676808103522925` | `0.001672922349588871` |
| Pinned T74 lower `b=0.00167971337478` | `0.001677160151714381` |

For T74, `(epsilon,xi,beta)` is approximately `(0.998480030429031142,0.906417190590745524,0.093581799409254476)`. The minimum saving is exactly epsilon*q. The rational final kappa is more than 1e-11 below this minimum, absorbing every fixed polylogarithm and unconditional short-arithmetic factor. Floors, ceilings and cap dyadicization change constants only; the explicit balanced grouping from Section 1 handles the final group. Below the eventual common cutoff, elementary multiplication changes only the asymptotic constant. The proof gives no useful numerical cutoff.

## 8. Controls and outstanding boundary

Run from the repository root:

```sh
python3 -B research/capped-phase-fusion/review20261014/independent/check_original_outer.py
```

When installed at `research/capped-phase-fusion/review20261014/independent`, the script's default package is `HERE.parent.parent`, so no workspace path is embedded. Package-internal sources resolve directly beneath the selected package. The six inherited notes/reports default to the portable snapshots in `HERE/source/`, with their original repository-relative paths and enforced SHA256 pins. An explicit `--repository-root` may select another copy only if all six hashes still agree. Thus a registered replay may copy only the package to a temporary `package` directory, without reading mutable upstream notes. It writes only its own receipt beside the checker. The historical published-head pin is retained as provenance; regenerated hashes bind the actual package and repository sources used after integration.

It produces `ORIGINAL-OUTER-CONTROLS.json` and checks:

- 34 positive exact inequalities in each of the original and T74 regimes, including every row of the conservative cost table, gauge/normalization powers, support, membership and stopping margins;
- six rejecting variants per regime: an unreplaced Vd scan, an unrecentered full-cell tensor gauge, zero group spare, zero boundary slack, equality at the complex endpoint and an excessive stopping exponent;
- an independent rational logarithm/exponential enclosure of the T74 mixed moment and a rate-overshoot rejection;
- 24 varied four-by-four systems, with 768 exact entries checking both five-factor orientations, plus rejection of a missing middle dense stage;
- 502 one-axis q-image cases on 173740 target addresses and a distinct 2275-record three-axis monotonicity control;
- complete sparse rectangles, union closure and an explicit dense-stage leakage witness;
- exact source-face volume identities and disjoint first-face partitions;
- the actual maximum-child depth bound and illustrative conservative product-stock reservations above a polynomial-log tail, without asserting a specific unproved row-chunk constant.

The JSON is reproducible evidence for finite algebra, rounding enclosures and bookkeeping. The all-size conclusions rest on Sections 1–7 and the explicitly inherited premises. In particular, this signoff does not promote pre-existing native receipts to freshly regenerated admission. The inherited controller, geometry, physical invoice, semantic regeneration and their negative fixtures are recorded separately in `../REVIEW-RESPONSE.md` and `../NATIVE-SUPPLEMENT.json`. The mixed-tree citation and complete row-stock reservation are now explicit in the main note. This review changes no source supplier or selected certificate.
