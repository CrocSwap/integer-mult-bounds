# Cached source chirps through actual cyclic convolution and grid conversion

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
This closes one concrete prefix interface, not the complete Gaussian prefix
or a multiplication theorem. No new kappa or selected-result change.

## 1. Exact source boundary and overlap

Canonical source pin: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The unchanged cached consumer, producer and serializer are from
CrocSwap/integer-mult-bounds#6906, public head
`3c0443b2aa721ce692199ff31abc18e8d917596a`. That package implements certified
chirp/conjugate payload passes and explicitly leaves full chirp convolution
and payload-grid conversion open. We supply those connections here.

The actual `Cyclic` child is canonical
`research/physical-chirp-middle/cyclic_engine.py` (#3763). Its unchanged
twist/ring/narrow/untwist sequence already implements normalized cyclic
convolution. The original #3763 chirp consumer uses a different numerical
kernel producer; we do not claim its Fourier identity or cyclic algorithm
anew. #4325/#5987 and #6906 already prove cached phase error and movement.
#5295/#5325 already supply the old expansion/error telescopes; they do not
implement this cached convolution/grid seam or replace the old Tensor
catalogue. The broad fine-family Core is outside this package and remains
separate concurrent work.

The canonical `tensor_sources.bind_chirp` function is used unchanged to bind
the two runtime families. The Gaussian/FFT-word loader and the chirp loader
authenticate the same corrected ring export (SHA256
`c03d4b056ccd3db860c93579f6525e0bb1baea31cff879eb07135c99432ef159`).
The binder compares every ring-package byte before supplying the existing
state token. No numerical routine, scalar owner or validation is replaced.
Actual `Tape` and `Count` identities are checked before importing the join.
The old Tensor catalogue and its inadmissible fine-theta production guards
are not invoked or waived.

## 2. Field, source and grid contracts

Let D>=2, r=2^ell>=4, t_0=r and t_i in {r/2,r}; put
T=product t_i, M=T/r=2^A. Each original slope s_i is odd with 0<s_i<t_i.
Axis zero is fastest, and its r adjacent coefficients form one polynomial
record. All T original padded coordinates are processed, including every
coordinate called a hole by the Gaussian maps. There is no Core-size phase
period, skipped hole, extraction or transpose.

The exact source chirp is

    a(x)=product_i exp(-pi*i*s_i*x_i^2/t_i).

The q-grid external field uses the public Core/halo bridge's signed-magnitude
format: q+2 bits per real component, a complex record separator, and its
fixed sentinels. Let ||z||_* = max_x(|Re z_x|+|Im z_x|); let ||z||_abs be
maximum complex modulus. Admit an actual supplied q-grid field x with
||x||_abs<=1/2. The join checks this condition by exact squared-radius
products on every lifted input, not by inspecting its source history.

Let h=2^-f. The certified cached producer at radius one supplies inward
unit-disk per-axis table entries on this f grid, with each component error
<=2h, and exact entries a_i(0)=1. Its immutable source specification binds
each original (t_i,s_i) pair. `Prepared` emits the cached shape in fastest-first
order and the Cyclic flags in reversed remaining-axis order, with the maximal
axis last as required by the original Cyclic ABI. Both describe the same
axis-zero-fastest flattened field: the inherited FourierPlan.natural_axes
visits flags from the right at increasing low-bit offsets, while each ring
record already contains axis zero. These source-preparation and no-concurrent-
mutation premises are retained; structural parsing alone does not establish
phase semantics for arbitrary tables.

The cached carrier is W=f+3; the Cyclic carrier is f+2. The public codec uses
`external_grid=q, native_grid=f, normalizer_bits=0`. Entrance is an exact
dyadic lift. Same-grid conversions check signed representability and copy
the exact integer; they neither discard fractional bits nor introduce a
normalization. The final public codec truncates each component once from
f to q, contributing <2^(1-q) in ||.||_* when f>q and zero when f=q.
All conversions scan the complete T-record field and are paid below.

## 3. The same rounded kernel at all three occurrences

Let A(x) be the *fresh rounded suffix expression* defined by #6906's actual
cache at x. It is not the exact irrational a(x). The predecessor proves

    |A(x)|<=1,
    |A(x)-a(x)| <= (3D-1)sqrt(2)h =: e_a.               (1)

The same unchanged source bank and f/W fields are used for three cached
calls. First run the forward cached pass on a literally produced all-ones
field. Multiplication of the dyadic A(x) by exact one, followed by f-grid
truncation, is exact, so its returned kernel is A(x), with no fourth error
term. The second call applies the conjugate pass to the exactly lifted x.
The third applies it to the actual Cyclic return. The cache recurrence
depends only on original coordinates and tables, never on payload values;
fresh initialization and completed cleanup therefore give the identical
A(x) at every occurrence. In particular conjugating before the first
endpoint, using A as convolution kernel, and conjugating the last endpoint
are all necessary sign conventions.

The actual computation at the f grid is thus

    x0 = trunc_f(conj(A)*x),
    z  = actual_Cyclic(A,x0),
    yf = trunc_f(conj(A)*z),
    yq = component_trunc_q(yf).                         (2)

Kernel and endpoint calls execute real CachedChirp owners. The join copies
and consumes every protected child return before reuse. The Cyclic child
executes two twists, its actual ring convolution, exact signed-width
narrowing and one untwist. Its ring consumer already performs its exact
M restoration; the join performs no additional M, r, T or gamma scale.

## 4. Actual-input defect and radius

Retain #3763's exact cyclic and primitive/coefficient contracts. For
f>=16 and f-A>=13, on disk inputs whose smaller norm is <=.7, its actual
returned normalized cyclic convolution C obeys

    ||actual_Cyclic(v,w)-C(v,w)||_abs
      < (4sqrt(2)M+12)h,
    ||actual_Cyclic(v,w)||_abs
      <= min(||v||_abs,||w||_abs)+4sqrt(2)Mh.            (3)

The strict numerical radius consequence is sufficient here; (3) is the
retained written theorem, not a new proof of the Fourier backend. By
inwardness, ||x0||_abs<=1/2. With ||A||_abs<=1, (3) is admitted at the actual
computed x0. Since `32*1000^2<2^26`, f-A>=13 gives 4sqrt(2)Mh<.001.
Every returned z and final yf,yq consequently has norm <.501. Cached
endpoint truncation and the final external projection cannot increase
complex modulus. Thus all cache payload calls are within their radius-one
source contract. Both narrower f+2 carriers hold all converted components;
no discarded high bit is justified by approximate cancellation.

For a fixed supplied dyadic A define the exact map
F_A x=conj(A)*C(A,conj(A)*x). Bilinear contraction of C and |A|<=1 imply
that the two endpoint rounding errors in (2) contribute <2sqrt(2)h in
modulus. Adding (3),

    ||yf-F_A x||_abs < (4sqrt(2)M+12+2sqrt(2))h.        (4)

Now replace the three A occurrences with a by a three-term telescoping
identity at exact operands. Each term is bounded by (1)*||x||_abs, so
`||F_A x-F_a x||_abs<=3e_a/2`. This uses exact bilinear maps only; no
linearity or nonexpansiveness of the rounded program is assumed.
The retained chirp identity gives F_a=Q_freq F_t, the normalized Fourier
map with `(Q_freq v)_x=v_(-s_i x_i mod t_i)`.

Convert the *one final global* modulus estimate to component-l1 using
||.||_*<=sqrt(2)||.||_abs. There is no sqrt(2)^D factor. Since
12sqrt(2)<17, (1),(4) and the final q projection prove

    ||yq-Q_freq F_t x||_*
      < (8M+9D+18)2^-f + 2^(1-q).                     (5)

This is a bound at the actual supplied x. Its prior expansion error is
not assumed zero and is handled separately in Section 6. The returned
component-l1 radius is <.501sqrt(2)<1, suitable for a radius-one compression
entrance subject to that compression's separate dense/source admissions.

## 5. Explicit sufficient precision, with no new normalization

For an integer target chi>=0, set C=8M+9D+18 and choose

    q>=chi+2,
    f=max(q,16,A+13,chi+1+ceil(log2 C),ceil(log2(6D))),
    W=f+3.                                             (6)

The final term permits the unchanged cached preparer's radius-one,
target-zero allocation to keep precisely this f. Then the first term of
(5) is <=2^(-chi-1), and the second is <=2^(-chi-1), with strict total
error <2^-chi from the actual rounding bounds. The W value is exactly the
unchanged producer's chosen width: A>=ell-1 and A>=D-1, so f>=A+13
also covers its ell+2 and ceil(log2(D+1))+2 metadata-width clauses. All counts and shifts are constructed
before online payload processing and remain encoded thereafter.

For the fine family, A=O(p0), D=poly(p0), q,chi=O(p0), and ell=o(p0).
Thus f,W=O(p0); indeed f=O(q+A+log(D+1)+1). This explicitly funds the cyclic
M-amplification rather than assuming that a compression-only q rule already
covers it. It is an added sufficient internal grid, not a claim that every
previously prepared phase bank or frozen prefix already used these bits.
Grid lifting preserves represented values. No normalizer is introduced and
the actual existing total Gaussian gamma is unchanged.

## 6. Precisely reduced prefix obligation

Let e be the exact normalized broad expansion field and ehat its computed
q-grid field in the same original padded coordinates. Assume the actual
ehat passes the radius guard above, and ||ehat-e||_*<=epsilon_exp. The exact
normalized Fourier map contracts maximum complex modulus, hence

    ||Q_freq F_t(ehat-e)||_* <= sqrt(2) epsilon_exp.

The new actual middle output yhat therefore satisfies

    ||yhat-Q_freq F_t e||_*
       < sqrt(2)epsilon_exp + delta_mid,
    delta_mid=(8M+9D+18)2^-f+2^(1-q).                  (7)

Use the public Reference/ideal join's exact normalized compression C_N,
its actual existing total restoration exponent Gamma, and its separately
proved restored compression error <=2^-tau on yhat. Its caller contribution
is now explicitly

    ||completed_output-2^Gamma C_N Q_freq F_t e||_*
      < 2^-tau + 2^Gamma ||C_N||_*
                    (sqrt(2)epsilon_exp+delta_mid) + e_extra.       (8)

For example, if the actual normalized C_N contracts this norm and the
middle's assigned restored allowance is 2^-tau_mid, choosing
chi>=Gamma+tau_mid and (6) funds its term. A separate allowance must fund
the expansion term and every extra interface error e_extra. No rounded-map
contraction or automatic equality of old/new gammas is imported. No
complete RF_s, opposite source transform, CRT or integer recovery is
claimed: (8) leaves precisely the source-bound broad expansion, its reached
radius/error and all remaining backend/production assumptions open.

## 7. Full source, movement and arithmetic invoice

All fields have full volume T. In addition to three unchanged cached calls
and one unchanged Cyclic call, the join pays:

- exact q-to-f entrance and f-to-q return in the public codec;
- 2T exact real products for the physical input-radius checks;
- one T-record all-ones bank, three exact W<->f+2 field conversions;
- owned kernel/endpoint/current fields, the final external output copy,
  every child return consumption, all rewinds and cleanup.

These add O(TW+T M_word(W)) online work, including conversions whose grids
agree but signed carrier widths differ. Use the unchanged complete scalar
invoice M_word(W)=O(W log^2(W+2)) only under its inherited all-size contract.
The cached update count per call is U=sum_k(T/product_{i<k}t_i-1)<2T;
three calls cost 12(T+U) real products. The radius check adds 2T.
These products are additional to every scalar operation inside Cyclic.

Retain the complete canonical cyclic envelope, including all three full
Fourier calls T_F, normalized ring products, twists and exact recovery.
Here T_F means each inherited call at its actual encoded shape, row count
and internal precision (including P=f+A), with its source and retained
backing charges; no original-grid frontier is substituted for those calls.
A conservative valid total is

    3T_F + O(T(ell+1)f^(8/5) + r f^3 + (A+f)^3
             + T M_word(W) + TW + D^2W + C_setup).      (9)

The canonical *whole* old chirp invoice is an upper bound for its Cyclic
subprogram, so (9) safely keeps its scalar/twiddle/setup terms without
claiming a new optimized coefficient. No child is priced as a rank count or
a free normalized convolution. No multiplication theorem is inferred from
the scalar terms being nonbinding. In particular the historical T_F frontier
has not been re-admitted for the fine-family dimensions here.

`C_setup` is #6906 SOURCE.md's paid preparation and serialization: with
m=sum_i t_i, B=O(f+ell+log(D+1)) in this source family, and historical source
storage H_prev, let H=O(H_prev+(m+D)B+B^4). The explicit sequential simulation
bill is O((m+D)B^12 H+Wm+sum ell_i+D). The actual serializer's integer
unit-disk checks are also covered (or charged as O(mW^2) explicitly).
The current flags/Counts add O(D ell+A+f) bits and polynomial preparation.
The all-ones bank is full-volume online work, not subexponential setup.
For fresh source history, m=2^o(p0) and these source costs are 2^o(p0);
unbounded retained history cannot be silently discarded.

Storage is a constant number of full O(TW) fields and codec buffers, the
O(mW+DW) cached tables/state, source setup H, all active/inactive cyclic and
scalar child backing, and encoded metadata. Every role's historical largest
extent remains charged after erasure. Output consumption is part of the
invoice. Structural/source preparation is not advertised as a literally
metered elementary coefficient generator.

## 8. Evidence and limits

The physical witness uses T8, radices (4,2), original slopes (3,1),
external q10, internal f16/W19 and chi7. It exercises nonzero grid lift/drop,
both cached conjugate endpoints, kernel-on-ones, actual complete Cyclic,
its three actual Fourier calls, exact width narrowing, the full original
coordinate order and protected-return cleanup. It uses the predecessor's
declared q2 finite provider and exact small metadata specialization; no
production GL64/O73 or full fine-family invocation is claimed.

The independent integer oracle imports no predecessor checker. It derives
the eighth roots with integer square root, computes the two-point Fourier
butterflies, signed negacyclic polynomial product, exact M restoration and
twists, then compares against a separate exact Gaussian-rational dense
Q_freq F_t sum. Scale/conjugation/grid controls distinguish the critical
seams. Allocation checks are finite corroboration of (6), not a universal
proof. Full receipts and the bounded attempt history belong in `evidence`.
The exact source proof and inherited contracts establish the all-size
conditional statement; model-assisted lead review is not human or
proof-kernel acceptance.
