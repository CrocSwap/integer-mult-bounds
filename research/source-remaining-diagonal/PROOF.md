# The actual remaining Gaussian diagonal on the common grid

Prepared for **@CubeJerry**, with substantial OpenAI assistance. Apache-2.0.
Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
**A source-specific conditional service theorem; no new kappa.**

## 1. The implication supplied here

The public [group scale ledger](https://github.com/CubeJerry/integer-mult-bounds/tree/76a84e1c4bfa4035e5ee85410dbfc4541f0da168/research/core-group-scale-ledger)
leaves its equation (4) as a concrete missing implication. After the actual
Core/halo bridge returns an approximation to

`B=2^-U tensor H_i^-1`, `U=sum u_i`,

the source's existing completed-map normalizer K must be spent by applying

`A=2^(U-K) Dtilde_G`.                                         (1)

On original selected coordinate `q_i(j)=j+floor(e_i j/S_i+1/2)`, the actual
diagonal is `D_i=exp(pi alpha_i^2 beta_i(j)^2)`, with
`beta_i(j)=e_i j/S_i-floor(e_i j/S_i+1/2)`. At a hole, Dtilde_i is 1.
These are exactly the source definitions in `unconditional-batched-crt/PROOF.md`
and the original `rational-unitary-fft/gaussian_reference.py` coordinates.
The field remains the complete padded target field, before final extraction.

This package produces those coefficients, invokes the unchanged physical
Full diagonal implementation with the public exact FFT scalar owner, and
returns through the public format codec with **zero additional normalization**.
For every actual input z on the component q-grid with
`||z||_* = max_k (|Re z_k|+|Im z_k|) <= R_w`, it proves

`||Ahat(z)-Az||_* <= (R_w+2) 2^-q`.                          (2)

All original coordinates and spectator records participate. The service
returns to that same q-grid. Its actual output even satisfies
`||Ahat(z)||_*<=||z||_*`. This last pointwise radius bound does not assert
linearity or a Lipschitz property of the rounded routine.

The exact source/physical premises below remain necessary. In particular,
this does not independently discharge a native supplier theorem, prove the
rational H versus ideal Gaussian N comparison, implement final extraction,
or establish whole integer recovery. It consumes one identified open service
in a conditional ledger.

### Prior work and exact pins

The global scalar service is the unchanged public package
[2882d441](https://github.com/CubeJerry/integer-mult-bounds/tree/2882d4414e95a6884f7b588d9da7ca893f800cbf/research/full-fft-scalar-join),
whose full physical source is pinned to
`d51859e7816771f627033b23db0f9786ada863f8`.
CrocSwap/integer-mult-bounds#6898 supplies that owner; #3787 supplies its exact
`FftWord` scalar; #3709 supplies the retained signed arithmetic/inner product
lineage. The independent scalar numerical review and source lifecycle
premises are inherited as stated in the retained FFT proof. The external
codec is unchanged public
[73d5adab](https://github.com/CubeJerry/integer-mult-bounds/tree/73d5adaba2b7dc662e86eb901e81369a3f73be9f/research/core-halo-source-bridge).
The complete Core numerical family is cited at
[6fb9ab77](https://github.com/CubeJerry/integer-mult-bounds/blob/6fb9ab776b7d0956b8bcc2d3cfde0f3034421630/research/complete-core-physical-join/NUMERICS.md).

#3851 already has physical C selection and Gaussian normalization, #6894 has
the original global Full physical service, and #6895 has a different complete
FFT product recovery boundary. The source GAUSSIAN.md already describes
cached axis-prefix products with O(1) average word products per record.
`gaussian-origin-diagonals` concerns source Schur diagonals;
`encoded-twiddle-diagonal-pass` concerns signed packet rotations. We do not
claim a new cache, generic diagonal multiplier, or exponential algorithm.
The new implication binds (1), including its changed scale, actual original
Reference coordinates, all-input radius, exact q-grid codec and complete paid
physical calls to the ledger's remaining service.

## 2. Finite admissions and their source-family consequence

Let the original target sides be `N_i=S_i+e_i=2^ell_i`, with `0<e_i<S_i`,
and the actual alpha_i positive integers. The objects are the same immutable
canonical References used by the bridge; code authenticity and source object
identity are premises, not merely matching labels. Their certified gaps
delta_i are positive, and the original dyadic exponents satisfy
`2^u_i delta_i>=1`. K is the actual already-declared completed normalization.

The new sufficient finite admission is

`K-U >= L_exp := 2 sum_i alpha_i^2`.                         (3)

Nearest half-up rounding gives `-1/2<=beta_i(j)<1/2`. Put
`F_max=sum alpha_i^2/4`, so L_exp=8F_max is an integer. At every complete
coordinate, with hole contributions zero, define
`F=sum_selected alpha_i^2 beta_i(j)^2`; then `0<=F<=F_max` and
`A_k=2^(U-K) exp(pi F)`. The elementary strict inequalities
`pi<4` and `log 2>1/2` give `pi<8 log 2`. Therefore

`0<A_k<=2^(U-K+8F_max)<=1`.                                 (4)

No floating-point inequality or exact transcendental floor is needed.

For an arbitrary caller, (3) is an explicitly additional sufficient condition;
it is not silently deduced from the ledger's weaker norm test. For the
conservative source family it follows from the declared ample normalizers.
Retain the source admission `pi alpha_i^2<=5 log(16p)`, p>=2, and let
`l=ceil(log2 p)`. Then, using `pi>3` and `log2<1`,

`2 alpha_i^2 <= (10/pi) log(16p) < 4(l+4)`,

so `2 alpha_i^2<=4l+16`. The least dyadic source normalizer and
`delta_i>=1/(16p^2)` give `u_i<=2l+4`. Thus the public ledger's concrete
`k_i=100l` has

`k_i-u_i-2 alpha_i^2 >=94l-20>0`.                           (5)

Even a dyadic completed bound merely at least p^100 suffices: for l>=2,
`k_i>=100 log2 p>100(l-1)>=6l+20`; at l=1 and p>=2 one has p=2 and k_i>=100.
Summing proves (3). This implication inherits the source's eventual alpha
and gap admissions; it does not prove those admissions. Oversized caller
normalizers u_i must pass the actual finite inequality.

## 3. Certified coefficients without a separation assumption

The producer calls the original `Reference.exp.relative(F,F_max,q+4)`.
Let `w=exp(-pi F)`, `s=2^(U-K)`, and let its certified receipt supply
`0<l_w<=w<=u_w`. That unchanged routine has

`absolute_error <= 2^(-L_exp-q-6)`.

Its floor value is at or below l_w, so both the enclosure width and its lower
endpoint deficit from w are no larger than this absolute error. By (4),
`w>=2^-L_exp`, `s/w<=1`. With `epsilon_q=2^(-q-6)`,
`l_w>=w(1-epsilon_q)`. Hence the exact rational reciprocal enclosure

`a_lo=s/u_w`, `a_hi=s/l_w`

contains A_k and has width at most

`s (u_w-l_w)/(l_w u_w) <= epsilon_q/(1-epsilon_q) < 2^-q`.    (6)

The implementation checks positivity and this width directly as well.
The unchanged relative-exponential routine computes a fixed prescribed
precision; it never loops until the transcendental value has a unique grid
floor.

Let h_q=2^-q and encode

`c_k = min(1, h_q floor(a_hi/h_q))`.                        (7)

Without clipping, `c_k-A_k<=a_hi-a_lo<=h_q` and
`A_k-c_k<h_q`, because `A_k<=a_hi`. Clipping to 1 cannot enlarge the distance
from A_k in [0,1]. Thus `0<=c_k<=1` and `|c_k-A_k|<=h_q`. Coefficients whose
true value is below a grid unit may become zero; the same bound applies.

Using the lower endpoint's floor would not give this bound. For example an
enclosure `[0.9h_q,1.9h_q]` allows A=1.9h_q, while that floor gives 0. The
checker retains this explicit failure control. Equation (7) is not claimed
to equal the exact correctly rounded exponential.

## 4. Full original-period stock and literal source event

Let `n_addr=sum_all_axes ell_i`, `T=2^n_addr`, and
`h_G=sum_(i in G) ell_i`. The stock has exactly `P=2^h_G` coefficients.
Here h_G uses every bit of each **original** selected target side, rather
than only the low bits of a polynomial Core microbox.

`RemainingProgram` binds the actual Reference classes, object identities,
immutable specification hashes, original target sizes, original normalizer
exponents and every literal selected-coordinate/beta value. It seals the
complete allocation and coefficient page. Preparation checks actual inverse
membership against the forward nearest-half-up formula. The separate checker
independently enumerates source j values, rather than trusting that inverse.

A support-local permutation moves the full original selected bit positions,
in the declared low-first source-axis order, to bits 0 through h_G-1. Complete
the partial bijection by matching the sorted unused target/source positions.
It fixes all positions outside the union and has support at most 2h_G. This is
an actual whole-field physical gather, followed by its inverse; no coordinate
relabeling is free. Spectator values can change their intermediate labels but
the coefficient is independent of those labels and all are restored.

After packing, the already-computed full tensor coefficient period is one
page of an **original** `Diagonal` event with `axes=1`, `axis_bits=h_G`,
`coarse_bits=n_addr-h_G`. This is an explicit new source producer for the
original event protocol, not a fictitious FullRoot or a modified Full source
program. Its one real page is repeated for all `2^(n_addr-h_G)` original
spectator labels. The unchanged `PreparedFull` validates and emits each page
and its metadata. The complete code length is exactly

`2T(q+2)+4` bits.                                          (8)

All repetitions and full code scans are paid. The inherited
`coefficient_field` has one axis, so its first-page copy supplies each
coefficient exactly: it performs **zero rounded coefficient products**.
The stock construction already computed the complete true product diagonal
with the single certified exponential in (6).
The literal repeated-page container in `events()` also has
`2^(n_addr-h_G)` references. Its construction and metadata/storage are
explicitly O(2^(n_addr-h_G)), absorbed only by the charged O(Tq) term.

## 5. Actual physical service, rounding and common-grid return

Choose integer R_w>=1 and

`r=ceil(log2 R_w)+ceil(n_addr/2)`, `W=q+r+2`.

Every admitted field has Euclidean norm at most R_w sqrt(T)<=2^r. The actual
native Full routine checks this with all 2T exact component squares and the
complete accumulator; no local-field radius replaces the full one. Set
`incoming_bits=fractional_bits=q`, `incoming_width=data_width=W`, coefficient
and cache widths q+2, and temporary width 2W+3. Factors in [0,1] fit; signed
products and full sums fit the temporary width. Component magnitudes after
truncation cannot exceed their incoming magnitudes, so the W output carrier
and the original external carrier fit.
For the maximum squared-radius exponent
`2q+2ceil(log2 R_w)+n_addr`, the difference from temporary width 2W+3 is
`2ceil(n_addr/2)-n_addr+7>=7`. The radius accumulator itself is an actual
Count whose complete width/cost is charged; this margin is not a claim that
the accumulator is stored in the complex-product temporary. The checker
compares all 16 encoded native metadata positions with their stated values.

`RemainingOwner` surrounds unchanged `FastFullPhysical.run` by the two actual
global routes, using one already constructed composed root. The code has
exactly one D event and no H events. Its data operation is the original four
exact real products and exact complex sums, followed once by componentwise
toward-zero division by 2^q. Because the coefficient imaginary part is zero,
the result is precisely

`(Q_q(c_k Re z_k), Q_q(c_k Im z_k))`.

The coefficient error contributes at most R_w h_q in component-l1 norm and
the two component roundings contribute strictly less than 2h_q. This proves
(2) and the pointwise radius bound. The native implementation really pays
four real products even when two involve the zero coefficient component.

The retained external/native codec has
`native_grid=external_grid=q`, `normalizer_bits=0`, hence `lift=drop=0`.
Its incoming sign-magnitude/two's-complement conversion is exact. Its return
absolute-value conversion discards zero digits and is exact too; this is a
source-level fact of its literal drop loop, corroborated by the actual
negative and mixed-sign witness. There is no second final q truncation and
no second factor 2^-U. A caller choosing another native grid or an additional
normalizer falls outside this specific wrapper and needs its own error bill.

## 6. Ownership and full physical invoice

All owners, scalar children, formats and role inventories are constructed
before sealed execution. Private pools and every nested protected output are
forbidden borrowed ports. The parent copies its complete input into owned
state, suspends its scope at the route and D-child boundaries, copies and
consumes each protected child return, and restores every borrowed head.
It returns one protected original-order result. The codec protects a complete
external result and uses the unchanged original input as its record clock.
Consumption clears the codec input/work and native outputs; it does not claim
to shrink retained tape backing. This is a successful legal-call theorem
under the predecessor native/Count/ownership contracts, not a theorem of
arbitrary interruption recovery.

Let `F_scalar(w)=O(w log^2(w+2))` be the inherited exact FFT scalar tariff,
with the fixed production cutoff 4096 and all setup, carries, copies and
cleanup included. Let C_route be the actually admitted complete route bill
at `precision=W+h_G`, support at most 2h_G, position width
`max(1,ceil(log2 n_addr))`, complete record width 2W, and T records. Let S_ref
denote source Reference construction/retained state already required by the
caller; it is not made free if absent. A safe added service invoice is

`S_ref + 2^h_G poly(p) + O(Tq) + S_constructor + 2 C_route`
`  + O(T F_scalar(W+n_addr+1) + T W + poly(n_addr+log(q+R_w+2)))`. (9)

Before substituting a p-family, replace `2^h_G poly(p)` by the actual finite
coordinate/exponential/source-validation cost. The complete formula includes:

* all P coefficient evaluations and original source admissions, full spectator
  page validation/encoding, the O(2^(n_addr-h_G)) repeated-page container,
  route descriptor emission and metadata preparation;
* all 2T radius squares and the complete accumulator, T complex data products
  (four scalar calls each), exact sums, rounding, full lifts/copies/rewinds;
* both global routes, input/output sign codecs and every complete return copy,
  saved original input, protected output, disposal and fixed owner setup.

Neither a payload value nor a record index is decoded by the online code.
The source producer's host rational work is input-independent setup. Its
straight sequential fixed-tape simulation visits the P stock entries, with
g and all numerical heights polynomially bounded; a fixed polynomial overhead
is covered in (9). The prepared stock is then rewound/emitted once per
spectator page. It does not simulate a random-access T-entry numeric store.
Each source seal enumerates all original axis coordinates, costing
O(sum_i N_i poly(p))<=P poly(p); it is not a constant-time hash assumption.

The native fixed owner graph is the credited Full/FFT graph plus one fixed
global parent; the public codec uses 10 fixed roles. Its finite witness has
6080 distinct native roles, not 6080 fresh tapes per record. Added retained
backing comprises the maximum complete code(8), T W input/current/protected
buffers, codec buffers/formats, `2^h_G poly(p)` source stock, descriptor and
preparation peak, the scalar O(max_previous W) history and **all inherited
route/native backing**. Erased buffers still contribute their high-water
extent. Parent/child input references alias only through the stated borrowed
protocol; the saved original external input remains charged throughout.

## 7. Favorable complete family and ledger substitution

Use the published conservative family, with beta=39/40,
`epsilon=1-10^-30`, `g=Theta(p^beta)`, `d=Theta(p^epsilon)`, balanced groups
between g and 2g, `ell_original=O(p^(1-epsilon))`, and `n_addr=Theta(p)`.
The common q and `log R_w` are O(p) by the public group ledger. Then

`h_G=O(p^(beta+1-epsilon))=o(p)`, `W=Theta(p)`

when the incoming grid is Omega(p). The actual exponential factor height is
O(g log p); the rational coordinate description height is O(h_G+log p), and
the retained exponential working precision is O(q+g log p)=O(p). Its fixed
Taylor/range-reduction algorithms therefore take polynomial time per stock
entry. For every fixed polynomial degree, `2^h_G poly(p)=o(Tp)`; multiplying
by O(d/g) groups preserves this absorption. It is the full-period bound,
not the Core-side microbox count, that proves it.

The added scalar/codec/encoding bill over all groups is
`O(V (d/g) polylog p)`, V=Theta(Tp). The two complete routes must still be
admitted: n_addr=Theta(W+h_G), support<=2h_G<=(W+h_G)^.997 eventually, and
the actual native stock/free-space/reserve guards are inherited. Under the
same historical route tariff used by the public Core numerical family, its
all-group contribution is

`O(V p^(epsilon-beta+eta(beta+1-epsilon)) polylog p)`,
`eta=332353/332929`.                                      (10)

Keep 2 C_route if these admissions are absent. The public dense exponent is
`epsilon-(1-alpha)beta`, alpha=99827101/100000000. The exact rational inequality

`eta*10^-30 < (39/40)*(alpha-eta)`                         (11)

shows that (10) is strictly subordinate to that existing dense term. The
checker verifies (11) with exact fractions. The extra full-period route
factor is therefore not silently hidden in a logarithm. This is a compatible
conditional invoice, not a new accepted assembled kappa.

For the ledger set R_w=3R_0. Its existing precision guard is
`q>=z+ceil(log2 max(8,2 max_j L_j(2R_0)))`. Since each nonempty group has
`0<delta_i<=1` and W_i>=0, `L_j(2R_0)>=2R_0+2`. Thus
`2L_j>=4R_0+4>=3R_0+2`, and (2) gives `e_A,j<=2^-z=eta_ledger`.
No extra precision bit is needed for this specific upper-endpoint quantizer
and zero-drop native codec. The public actual-state recurrence and final
restoration can consequently consume this service directly, subject to all
their remaining hypotheses. The already-existing K normalizer is spent once;
the final restoration exponent gamma is unchanged.

## 8. Checks, limits and remaining obligations

The bounded replay authenticates all canonical and retained inputs, including
the unchanged source archive closure. Its independently coded positive
exponential oracle uses exact rational Machin bounds and a direct positive
Taylor tail. It does not import the retained negative-exponential interval
backend. It independently enumerates original source j coordinates, beta
and holes before checking 272 one/two-axis coefficients and 1904 signed-grid
trajectories. It also checks 1998 adversarial rational quantizer cases and
source/allocation corruption controls. These finite checks corroborate the
universal proof; they are not a substitute for it.

The actual 32-record physical witness uses one original 16-coordinate Gaussian
axis and a spectator bit. Both physical global routes are nontrivial. It
executes 64 actual input squares and 32 complete complex products, exactly 192
scalar calls, restores borrowed controls, preserves the external input and
consumes the protected result. All native values are below the fixed 4096
scalar cutoff, so this witness uses the existing base branch. The all-width
FFT bound is inherited from #6898/#3787, not inferred from this fixture.
The separate two-axis stock test covers the full 256-entry period and 512
original coordinates without claiming another 512-record native replay.

The checker disables the inherited host-decoding helpers during physical
execution and tests private-port aliases and protected-return reentry. These
are negative controls for the stated interface; no assertion claims complete
formal verification of Python or the simulator. Exact source objects and
files are frozen during execution, as in the predecessor contracts.

Remaining obligations are the complete production-context delivery and
reference/ideal-Gaussian comparison, native supplier and route/ownership
premises, the other side of the source transform, actual final selected
extraction/CRT/Fourier restoration and final rounding. This result supplies
only the particular missing remaining-diagonal service on the padded field.
