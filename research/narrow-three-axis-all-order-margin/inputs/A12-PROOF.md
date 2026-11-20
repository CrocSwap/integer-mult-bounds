# A quantitative all-order margin at two extremal source phases

## 1. Scope and quantified claim

This is a fixed **two-axis** theorem for a deterministic extremal-phase selector. It narrows A11's good-index set. Arbitrary A11-good indices, larger dimensions and full source matrices remain open. The matrix is the retained column-normalized narrow coefficient array, with its phase/chirp coefficients retained.

Let integer `p>=4096`, let `s_1,s_2` be distinct odd primes with `s_l>=p^4`, and let dyadic targets satisfy

    (1-1/(2p^2))t_l < s_l <= (1-1/(4p^2))t_l.             (1)

Set `delta_l=t_l-s_l`, `rho_l=t_l/s_l`, and

    L=ln(16p), alpha=ceil(sqrt(4L/pi)), a=pi alpha^2,
    n_l=-(s_l-1)/2,
    i_l=delta_l^-1 n_l mod s_l, in {0,...,s_l-1}.         (2)

Use the literal source coefficients

    q_j=floor(rho*j+1/2), beta_j=rho*j-q_j,
    G_jk=exp(-a[(rho*k-q_j)^2-beta_k^2]).                  (3)

The selected indices satisfy `i_l<=s_l-2` and `q_(i_l+1)=q_(i_l)+1`. Put

    C_l=G^(l)[{i_l,i_l+1},{i_l,i_l+1}], C=C_1 tensor C_2,
    w=exp(-2a), E(A)=A-Z A Z^T,                         (4)

where `Z` is the ordinary four-by-four lower one-step nilpotent shift. For all 24 simultaneous vertex orders `P`,

    |det E(P C P^T)| >= w^2/16,
    sigma_min(E(P C P^T)) >= 2^-10 w^2,
    sigma_min(E(P C^-1 P^T)) >= 2^-19 w^2.               (5)

The factors are nonsymmetric; singular values use the Euclidean operator norm, without an SPD premise. If a possibly unstructured complex `C_hat` has maximum entry error at most `2^-32 w^2`, it is invertible and every order satisfies

    sigma_min(E(P C_hat P^T)) >= 2^-11 w^2,
    sigma_min(E(P C_hat^-1 P^T)) >= 2^-20 w^2.            (6)

It suffices to perturb each factor entry by at most `2^-34 w^2` before forming the tensor. A sufficient factor-table precision, for absolute entry error `<=2^-b`, is

    b >= ceil(34+36 log2(16p)).                           (7)

In particular `b=p` suffices for `p>=4096`, and any fixed positive `Cp` suffices eventually. Section 6 adds the exact matched periodic alias sum with a separately paid two-bit error allowance. No existing production routine is asserted to meet the entry-error contract. Its old-domain admission mismatch is explicit there. Inverses are of the selected four-by-four tensors, never sections of larger inverses. No kappa or complete multiplication claim is made.

## 2. The legal extremal source pair

The coefficient and finite period `0<=j<s` are in `inputs/BILATERAL-LDU.md`; the prime interval and integer alpha are in `inputs/FINE-PRIME-PADDING.md`. A11, retained as `inputs/A11-PROOF.md`, derives the phase identities, restated here.

The integers `n_j=s beta_j=tj-sq_j` bijectively realize the balanced residues `[-(s-1)/2,(s-1)/2]`, since `n_j=delta*j mod s`. Hence (2) gives the unique smallest centered phase. Its next step is same-cell because `n+delta<=(s-1)/2`. Direct substitution in (3) gives

    C_l=[[1,U_l],[V_l,1]],
    U_l=exp(-a A_l/s_l), V_l=exp(-a B_l/s_l),
    A_l=2delta_l+1, B_l=2s_l-1, A_l+B_l=2t_l.            (8)

No similarity has been removed. If `i=s-1` and the step is same-cell, `n_s=0` forces `n=-delta` and hence `A=s`; but `A=2delta+1<s` under (1). Thus the pair lies inside `[0,s)` without wrapping, and its nearest target indices lie in `[0,t)`.

The selector belongs to A11's degree-four good set. Equation (1) gives `delta>s/(4p^2)` and `delta/s<=1/p^2`; thus `A>4` and `4A+4=8delta+8<s`. Since `B=-1 mod s`, the map `(u,v)->uA+vB mod s` on `[0,4]^2` is injective: its unreduced values lie in `[-4,4A]`, a range shorter than `s`; equality gives `(u-u')A=v-v'`, forcing both differences zero. The proof below does not need transcendence or CRT.

Extended Euclid and (2) select each starting index in `O(poly(log s))` bit work and `O(log s)` local arithmetic scratch. Both output indices are charged. This is index selection, not coefficient-page construction or full-source traversal.

## 3. A uniform four-by-four determinant lemma

Let `eta=2^-10`, `0<w<=2^-11`,

    1-eta <= u,x <= 1,  w <= v,y <= 2w,
    H=[[1,u],[v,1]] tensor [[1,x],[y,1]],
    q1=uv, q2=xy.                                       (9)

The four vertices are labelled `0=00,1=01,2=10,3=11`. Vertex translation means applying the same XOR mask to the four labels of an order. It accounts for the first 16 of the 24 orders in the following complete classification:

| Representative and its four translations | Determinant of E in that order |
| --- | --- |
| `(0,1,2,3)` | `x^2 y^2 (1-q1)^2` |
| `(0,2,1,3)` | `u^2 v^2 (1-q2)^2` |
| `(0,1,3,2)` | `F_x F_y`, where `F_z=q1(1-q2)-(1-q1)z^2` |
| `(0,2,3,1)` | the preceding expression with the two axes exchanged |

The table follows by expanding a four-by-four determinant. Translation interchanges `u,v` or `x,y`; the displayed expressions are invariant under those interchanges. The first two classes have determinant at least `w^2/16`, since the large entries are at least `1/2`, the small entries are at least `w`, and `1-q_l>=1/2`.

For the third class, `w/2<=q_l<=2w` gives

    F_x <= 2w-(1/2)(1/4) <= -1/16,
    F_y >= (w/2)(1/2)-4w^2 >= w/8.

Here `w<=1/32` suffices. Hence `|F_x F_y|>=w/128>=w^2/16`. The fourth class has the same bound by exchanging axes.

The remaining eight orders begin with opposite vertices. Compare with

    H0=[[1,1,1,1],[0,1,0,1],[0,0,1,1],[0,0,0,1]],

obtained from `u=x=1, v=y=0`. Direct integer determinants give:

| Order | det E(P H0 P^T) |
| --- | ---: |
| `(0,3,1,2)` | 1 |
| `(0,3,2,1)` | 1 |
| `(1,2,0,3)` | -1 |
| `(1,2,3,0)` | -1 |
| `(2,1,0,3)` | -1 |
| `(2,1,3,0)` | -1 |
| `(3,0,1,2)` | 1 |
| `(3,0,2,1)` | 1 |

Each factor entry differs from its reference by at most `eta`, because `2w<=eta`. Tensor entry errors are at most `2eta`. Displacement entry errors are at most `4eta`. Entries of both displacements have absolute value at most one. Telescoping each four-factor product in the determinant expansion bounds the total change by

    24 * 4 * 4eta = 384eta = 3/8.

These eight determinants therefore have absolute value at least `5/8`. Together the classes prove `|det E(P H P^T)|>=w^2/16` for all 24 orders and all real parameters in (9). The finite order table exhausts the order domain; the inequalities cover a continuous parameter box, not just sampled values.

All displacement entries have absolute value at most one, so `||E(PHP^T)||_2<=4` by the Frobenius norm. The product of the four singular values is the determinant magnitude. Thus

    sigma_min(E(P H P^T)) >= w^2/(16*4^3)=2^-10 w^2.    (10)

## 4. Inverse and perturbation bills

Each two-point factor in (9) has determinant `1-q_l>0` and inverse

    (1-q_l)^-1 [[1,-U_l],[-V_l,1]].

Its Euclidean norm is at most `2/(1-q_l)<=4`, by its Frobenius norm. Therefore `||H^-1||_2<=16`, `||E(P H^-1 P^T)||_2<=32`, and

    0 < det H = (1-q1)^2 (1-q2)^2 <= 1.

For any invertible `A`, the two determinant Schur complements of `[[A,Z],[Z^T,A^-1]]`, followed by the same identity for `A^-1`, give

    det E(A^-1) = det E_rev(A)/(det A)^2,
    E_rev(A)=A-Z^T A Z=J E(JAJ) J,                       (11)

where `J` reverses indices. Reversal is another allowed order and `det(J)^2=1`. Section 3 and (11) yield inverse displacement determinant magnitude at least `w^2/16`. Hence

    sigma_min(E(P H^-1 P^T)) >= w^2/(16*32^3)
                                  =2^-19 w^2.           (12)

This is a determinant and norm transfer for nonsymmetric matrices, not a persymmetry assumption.

For a four-by-four perturbation `F` with maximum entry magnitude `delta`, `||F||_2<=4delta` and `||E(F)||_2<=8delta`. If `delta<=2^-32 w^2`, then `||H^-1 F||_2<=64delta<1/2`. The Neumann identity gives invertibility of `H_hat=H+F` and

    ||H_hat^-1-H^-1||_2 <= 2*16^2*4delta=2048delta.

Consequently its inverse displacement changes by at most `4096delta<=2^-20 w^2`. Singular-value perturbation proves the inverse lower bound in (6). The forward change is at most `8delta`, which also leaves at least half the bound (10). Every factor of four from entry error to the matrix norm is included.

If the two factor tables instead have maximum entry error `zeta<=1`, their tensor entry error is at most `2zeta+zeta^2<=3zeta`. Thus `zeta<=2^-34 w^2` implies the required matrix error `delta<=2^-32 w^2`. The inverse in this conclusion is the exact inverse of the tensor of the perturbed factor tables. It is not computed for free. Any additional arithmetic/rounding during inverse construction needs its own error and cost bill.

A separately supplied approximate inverse with maximum entry error `<=2^-23 w^2` also retains full displacement rank: its displacement error is at most `2^-20 w^2`, half of (12). This is a separate approximation contract, not an assertion that a given inverse routine achieves it.

## 5. Source parameters enter the uniform box

Write `L=ln(16p)`. Since `L>=pi` for `p>=4096`, the retained integer-alpha definition gives

    4L <= a <= 4L+4sqrt(pi L)+pi <= 9L.                  (13)

Also `L<=p/8` on this range: the function `p/8-ln(16p)` is increasing for `p>=8`, and at 4096 its value exceeds `512-16>0`, using `ln2<1`. Thus `a<=9p/8`.

Equations (1) and (8) imply

    a A_l/s_l <= a(2/p^2+1/p^4)
              <= 27/(8p) <= 27/32768 < 2^-10.

Using `exp(-x)>=1-x` gives `1-eta<=U_l<=1`. Moreover

    V_l = w exp(a/s_l),  a/s_l<=a/p^4<eta,

so `w<=V_l<=2w`; the elementary bound `exp(eta)<=1/(1-eta)<2` suffices. The lower bound in (13) gives

    w<=exp(-8L)=(16p)^-8<=2^-128<2^-11.

The source pairs therefore satisfy every hypothesis of (9). This proves (5) and the perturbation statements.

Finally `w^2=exp(-4a)>=(16p)^-36` by (13), so (7) ensures the required factor entry error. To see that `b=p` suffices, at `p=4096` the right side before taking the ceiling is `34+36*16=610`; the difference `p-178-36 log2 p` is increasing thereafter, since `ln2>1/2`. The claim for any fixed positive `Cp` is the elementary limit `log p=o(p)`. This is a stable mathematical coefficient-table statement; it does not by itself validate a production program or its setup precision.

## 6. Matched periodic aliases and the unproved production interface

The exact source in `BILATERAL-LDU.md`, section 4, defines

    N_source(j,k)=sum_(m in Z) G_(j,k+ms), 0<=j,k<s.      (14)

For the selected same-cell adjacent pair, `|rho*k-q_j|<=3/2` and `|beta_k|<=1/2`. Since beta is s-periodic, for `m!=0` and `t>=3`,

    |rho*k-q_j+mt| >= |m|t-3/2 >= |m|t/2,
    G_(j,k+ms) <= exp(-a m^2 t^2/8).

Summing both tails geometrically gives the per-entry alias error

    |N_source(j,k)-G_jk| <= 4 exp(-a t^2/8).             (15)

Indeed `m^2>=|m|` and `a t^2/8>=9/8>ln2`. For `t>=32` and `a>=1`,

    4 exp(-a t^2/8) <= 2^-36 exp(-4a)=2^-36 w^2,        (16)

because `a(t^2/8-4)>=124>38 ln2`. Our source range satisfies these guards. Therefore the tensor of the two **selected principal sections of N_source** is within the proved perturbation budget. Its own inverse retains the all-order rank margin. A further factor-table entry error at most `2^-36 w^2` still leaves total factor error at most `2^-35 w^2<2^-34 w^2`. A sufficient precision for this matched periodic-factor error contract is `b>=ceil(36+36 log2(16p))`; `b=p` still suffices for `p>=4096`.

This is a direct bound on the particular normalization (14), not an identification of every matrix called a physical Gaussian. It does not identify a principal section of `N_source^-1` with the inverse of a principal section. The selector does not construct the alias sum or its rounded table; setup and production costs remain separate.

In particular, the tempting canonical #6099 theorem (`inputs/PRODUCTION-GUARD.md`) is for a different admitted production domain. It requires `u>=1`, `u d<=p` and `4d theta>1`. Our fine gap has `theta<=p^-2`. Together these would force `d>p^2/4` and `p>=u d>p^2/4`, impossible for `p>=4`. Thus that named production-plan/error theorem cannot be imported to this family. Its target is also the retained-band `N_w`, not automatically (14). A current producer must separately identify its matrix, prove a compatible entry-error estimate and pay its setup precision. An abstract fine-prime error statement is insufficient to skip those bindings.

## 7. Meaning, controls and open obligations

All 24 order types are exhausted algebraically in fixed dimension four. The rational checks corroborate the continuous-box inequalities and perturbation accounting; they are not a finite parameter substitute for the proof. Coarse rounding and balanced equal factors can destroy the rank, demonstrating why an entry-error premise and the chosen phase box matter.

The continuous-box lemma does not tensorize to three axes. For `B=[[1,1],[w,1]]`, `0<w<=2^-11`, and `H=B tensor B tensor B`, take order `(0,1,2,4,3,6,7,5)`. Columns 2 and 5 (zero-based) of its ordinary Stein displacement are identically `(1,w-1,0,0,0,0,0,0)^T`. The nonzero vector with entries -1 at index 2 and +1 at index 5 is therefore in the kernel for every such w. These factors lie in the same continuous box, so the whole-box full-rank claim fails in dimension eight. This is not a counterexample at actual distinct-prime source parameters: `U=1` is a boundary value outside their strict positive-decay entries. It is only a precise obstruction to extending this fixed-dimensional box lemma unchanged.

Full rank four requires at least four ordinary lower/upper Toeplitz generator products in every ordering, if that exact representation is used. No general algorithmic lower bound follows. Larger dimensions, arbitrary A11-good phases, scheduled larger tiles, full source inverse sections, coefficient-production admission and complete costs remain open. All five framework assumptions and the accepted conditional multiplication bound are retained. No new kappa is claimed.
