# Consume the current normalized Gaussian returns through exact recovery

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
**Conditional source-interface and scalar-endpoint result; no new kappa.**

## 1. The resolved identities and the genuinely changed caller

CrocSwap/integer-mult-bounds#4320 already audits the exact Gaussian Poisson
identity, the original frequency permutation, its opposite-sign cancellation,
and the two source-size recovery factors in #4100. We do not reprove or
claim those identities. #4415 already gives a generic one-M error ledger;
it does not bind the present normalized public returns, their q+3 external
carrier, the new source-first allocation or a deferred-restoration endpoint.

The actual current pieces are the expansion admission at
ceb3947872f996789072e37a56c0758c7720b844, the cached/Cyclic middle at
8db3cc1e98ba295cec4d752478431515e159c34f, the Reference/ideal join at
4509310a9a58d4c41c74029f899cbf36be1af9a1, the group ledger at
76a84e1c4bfa4035e5ee85410dbfc4541f0da168 and remaining diagonal at
b00d64b6204e83d468dde2db7480a2822e6940aa. Their complete proofs are retained
by exact public Git blob and SHA256. Their native/physical/analytic premises
remain premises; public availability is not canonical theorem acceptance.

These normalized endpoints naturally approximate lambda H_±, where
lambda=2^-Gamma and H_±=R F_s^±. The new channel keeps that normalization
through two forward calls, one q-grid pointwise product and one opposite
call. Its exact output is lambda^3 times the already normalized convolution.
We prove an explicit source-first precision admission and execute the paid
native scalar endpoints, including the exact enlarged recovery shift.

This is a changed channel. The canonical `Sandwich.recover` multiplies by S
twice and shifts by 2b+4, because its original Tensor already restores Gamma
at the boundary of each call. It cannot consume a deferred normalized
return unchanged. This is an interface mismatch, not a defect in its
original contract. No old Catalogue admission is invoked or waived.

## 2. Bind the same exact source target and original order

Let the original odd source periods s_i be pairwise coprime and target
periods t_i be the current dyadic periods, with axis zero fastest. Put
S=product s_i and T=product t_i. Use the original selected address
q_i(j)=floor(t_i j/s_i+1/2), not a microbox coordinate. The public Reference
join's exact matrix has entries

    N_i[r,s]=sum_l exp(-pi alpha_i^2
        ((rho_i(s+l s_i)-q_i(r))^2-beta_i(s)^2)),
    beta_i(s)=rho_i s-q_i(s), rho_i=t_i/s_i.

Its beta square belongs to the COLUMN. Thus it is exactly the source
N_i=C_i T_gauss,i D_i. The public expansion target is the same periodic
S_gauss,i, with every repeated original source occurrence. The public
middle is the normalized negative-sign Q_freq F_t, where
(Q_freq v)_k=v_(-s_i k_i mod t_i). These are the definitions audited in
#4320. No row-normalized or alias-deleted N is substituted.

The existing forward and compression dyadic exponents are K_f and K_c,
Gamma=K_f+K_c. Native inverse normalizers U_j are spent inside K_c by the
first policy, not added to Gamma. Before restoration the exact composition
therefore is

    A_-=C_N Q_freq F_t E = lambda R F_s^-,             (1)

where E=2^-K_f tensor S_gauss,i and C_N is the exact normalized ideal
compression including final extraction. Opposite sign is obtained by
complex conjugation before and after the SAME negative-sign composition.
All Gaussian matrices and lambda are real, so its target is
A_+=lambda R F_s^+. Signed q-grid conjugation is exact, including zero.
Its actual controller wiring remains a stated prerequisite, with paid
passes; the native carrier routine below supplies an exact sign operation.

#4320 proves, in these conventions,

    (R F_s^+)((R F_s^- u)*(R F_s^- v))=(u*v)/S^2.      (2)

Here * inside the parentheses is pointwise multiplication and the last
product is tensor cyclic convolution. R is the same multiplicative-index
permutation for both signs; it cancels in (2). This introduces no new
non-dyadic permutation. Gamma is only Gaussian normalization: it includes
neither S² nor the radix-digit scale.

## 3. A source-first finite allocation for the actual public contracts

Let b>=1 be the radix exponent, require 1<=S<2^b, and choose all original
source descriptors, group partition m>=1, K_f,K_c and Gamma BEFORE the
References. They do not depend on the Reference normalizer bits. Require
K_f>=D as in the public expansion admission. Put

    h_S=ceil(log2 S), a=2h_S+2b+7, epsilon=2^-a,
    tau=a+2Gamma+2, z=tau+Gamma+ceil(log2 m)+1.        (3)

The target for EACH of expansion, middle and compression, measured after
a hypothetical mathematical restoration by 2^Gamma, is 2^-tau. We omit
that physical restoration, not its error charge. Their sum is strictly
less than 3*2^(-tau-Gamma)=3lambda^3 epsilon/4. Thus the actual normalized
map error is bounded by

    ||Ahat_±(x)-A_±x||_* <= eta=lambda^3 epsilon        (4)

for every admitted q-grid input in the quarter-disk. The norm is maximum
coordinate component-l1; (4) also bounds complex modulus. Exact carrier
changes, conjugations and extraction add zero arithmetic error. If an
implementation adds another rounded operation, it must fund that error
separately; (4) is not granted to such an unlisted interface.

For the compression ledger alone, make the parameter substitution explicit:
its own restoration exponent is gamma_c=K_c, and request its restored
target tau_comp=tau+K_f. Then tau_comp+gamma_c=tau+Gamma, so its z is
exactly (3). Equivalently the resulting raw compression error is at most
2^(-tau-Gamma), before any whole-transform restoration. We do not silently
replace a compression-only gamma by Gamma while retaining its old target.

Here is the precise ordering that obtains (4) from the public packages.

1. Set R_0=1, R_b=2, R_w=3 for the compression ledger. Choose legal source
   radii R_i covering its ACTUAL dense/source radius and satisfying R_i>=2.
   The whole-field native bound includes 2sqrt(T); source-prefix radius
   obligations remain explicit, not replaced by a local core volume.
2. Construct the unchanged References at target tgt_i=max(1,z+2), with those
   radii and original descriptors. Compute their actual delta_i,W_i,u_i.
   Set U_j=sum_(i in G_j)u_i and t_j=max(1,z+2-U_j). This is source-first:
   tgt_i>=t_j follows AFTER construction without a circular u_i choice.
3. Apply the public Reference join's finite gate (13), the group's
   K_j>=U_j+V_j test, and the remaining-diagonal producer's stronger finite
   coefficient guard. Retain all original-period, carve, halo, stock,
   complete-context, scalar and physical supplier admissions.
4. Let Lceil be any integer >=max_j sum_(i in G_j)(4W_i+4)/delta_i.
   Choose common q at least

       101, b+2, a+3Gamma+7, max_i u_i,
       z+ceil(log2(max(8,2Lceil))),
       max_i(alpha_i^2+1), bit lengths of s_i,t_i,alpha_i.           (5)

   The source period s_i and constructor target tgt_i are separate descriptors.
5. The public group tail guards are
   Lambda_j<=2^-z/(4R_b). Choose their exact encoded truncation lengths
   accordingly; the conservative J_i=16p0^4 works eventually under the
   inherited production gap and locality tests. The public diagonal
   service supplies e_A,j<=2^-z on the actual R_w input under (5).
6. For the middle set chi=Gamma+tau. With A=log2(T/t_0), M=2^A and D axes,
   choose its actual f by

       f=max(q,16,A+13,chi+1+ceil(log2(8M+9D+18)),ceil(log2(6D))),
       W_mid=f+3.                                                (6)

   Use that f when preparing the immutable phase bank and every Fourier
   child. No old q-grid bank receives these bits retroactively.
7. Build the explicit expansion pages at this q, P=32768q, sigma=4096q
   and radius alpha_i ceil(sqrt(q)), as proved in the public expansion
   package. Its source rule q>=Gamma+tau+5 is exactly a+3Gamma+7 in (5).
   Its final shift remains K_f-D. The public middle needs q>=chi+2, which
   is weaker. Compression uses the same z,t_j,q in its exact ledger.

The public middle returns component-l1 radius below one, so R_0=1 is its
actual entrance, not an arbitrary ideal radius. The group ledger then proves
the actual intermediate radius and its restored tolerance. The Reference
join includes the H-versus-N defect at the same targets, including aliases.
The public diagonal accounts for its coefficient, native product and final
grid errors. Hence these are actual source allocations for (4), not three
unnamed error constants.

For the conservative fine family, canonical PROOF.md's "Sizes, setup and
elementary fallback" sets p0=6b exactly. Its "Recovering the exact product"
gives eventual S<T<2^b; this is the finite S guard in the present endpoint.
With D=Theta(p0^(1-10^-30)), Gamma=O(D log p0)
=o(p0), log T=Theta(p0), alpha_i²=O(log p0), log R_i=O(p0),
delta_i>=1/(16p0²) and W_i=O(sqrt(p0)polylog p0). Thus (3)-(6) and every
online native width are O(p0). The source-target increase by 2Gamma is paid;
it is o(p0), not zero. Positive-weight setup still uses O(p0²log p0+p0)
bits. All effective finite source tests and potentially enormous onsets
remain required. No practical threshold or newly accepted kappa follows.

## 4. Actual-input radius and final error, including Gamma=0

Take original scaled digit fields u,v with complex modulus at most 1/4.
Exact CRT permutations and zero insertion preserve that bound. Let
U=A_-u, V=A_-v, Uhat=Ahat_-u and Vhat=Ahat_-v. Since normalized Fourier
maps contract maximum complex modulus,

    |U|,|V|<=lambda/4, |Uhat|,|Vhat|<=lambda/4+eta.    (7)

No contraction of the rounded program is used. The native pointwise routine
forms the exact complex product and truncates each component once toward
zero on the q grid. Its complex error delta is <sqrt(2)2^-q<2*2^-q, so

    |what-UV| <= (lambda/2)eta+eta²+delta.             (8)

Because a>=9, epsilon<=1/512, eta<=epsilon and q>=a+3Gamma+7, (7) is below
1/2, while

    |what| <= (1/4+1/512)^2+1/32768
            =16649/262144 <1/4.                     (9)

Thus the opposite call really receives an admitted quarter-disk input,
including Gamma=0. Its normalized output has modulus at most
lambda*16649/262144+eta<1/2. The physical endpoint radius tests are therefore
funded for all three returned fields. The implemented pointwise routine
also checks the weaker half-disk inputs directly; inward exact products
then have quarter-disk outputs even without a numerical oracle.

Compare the actual opposite call first with A_+ at the ACTUAL what. The
operator A_+ has complex-supremum norm at most lambda. The final normalized
error from (2) is therefore at most

    e_norm <= eta(1+lambda²/2+lambda eta)+lambda delta. (10)

After deferred restoration by lambda^-3, using eta=lambda³epsilon and
2^-q<=lambda³epsilon/128,

    e_norm/lambda³
      < epsilon(1+lambda²/2+lambda^4 epsilon+lambda/64)
      <= epsilon(3/2+1/512+1/64) <2epsilon.             (11)

This is a bound on the final REAL error as well. It covers all source,
middle, compression and scalar errors explicitly admitted above. The exact
digit convolution is recovered after multiplying by

    K_deferred=S² 2^(2b+4+3Gamma).                    (12)

Indeed (11) and S<=2^h_S give

    error_after_(12) <2epsilon S² 2^(2b+4)<=1/4.       (13)

Nearest-integer rounding is unambiguous. There is a strict margin below
1/2, independent of the native tie convention. Omitting either S, replacing
3Gamma by Gamma or omitting it entirely does not implement this channel.
Imaginary projection is exact and contractive; the ideal coefficient is
real. No additional numerical rounding precedes native `nearest`.

## 5. The actual endpoint carriers and exact widths

The public group/diagonal external format on declared radius 2 or 3 uses
q+radius.bit_length()+1=q+3 bits PER sign-magnitude component. The canonical
Sandwich routines instead read native signed q+2-bit words. These formats
cannot be silently identified. The public zero-drop Codec at
Format(q+3,q,q+3,q,0) gives an exact native q+3 carrier. The new `carrier`
routine then reads it, checks the ACTUAL half-disk by two exact squares and
writes the identical numerator in q+2 bits. It may also conjugate exactly.
No fractional bit is discarded. The reverse q+2-to-q+3 route is exact too.

Narrowing is justified AFTER the whole normalized transform and extraction,
when (7)/(9) proves its radius. It is not granted to an arbitrary intermediate
Core/halo field of declared radius 2 or 3. A larger incoming external format
needs an explicitly corresponding exact adapter; this package binds q+3.
All codec, carrier, sign and native/external copies are paid full S-field
passes. The finite witness runs the real public wide codec and both exact
carrier directions, including conjugation and canonical signed zero.

`DeferredTail` accepts borrowed encoded S,b,q,Gamma. Its constructor checks
S<2^b and q>=b+2, copies the Counts, and computes the actual shift and width
using encoded operations. It does not receive a host record count or decode
payload values. The uniform recovery carrier is

    W=q+3Gamma+4b+6.                                  (14)

For every allowed recovery input, the real integer numerator satisfies
|x|<=2^(q-1). Therefore

    |xS|<2^(q+b-1), |xS²|<2^(q+2b-1),
    |xS² 2^(2b+4+3Gamma)|<2^(q+4b+3Gamma+3).           (15)

The signed W-bit capacity is 2^(W-1)=2^(q+4b+3Gamma+5), leaving two full
margin bits in (15). Both exact S multiplications, all Count intermediates,
the shifted numerator and final nearest integer fit the charged O(W)
extent. No relation between log S and b is hidden: S<2^b is checked.

For pointwise data, each exact real product has magnitude at most
2^(2q-2); each signed component sum is at most 2^(2q-1). The unchanged
word multiplier returns its complete product and signed sums use Counts;
these pre-drop extents are O(q), before one division by 2^q. The resulting
quarter-disk numerators fit q+2 bits. This accounts for complete products,
not only the small post-drop output.

## 6. Extraction, CRT, ownership and full invoice

The scalar endpoints require a COMPLETE compact S-record field in the
original source-coordinate order. A padded T-record field is not such a
return even when its extra coordinates are zero: the actual extent check
rejects it. Final C must select the original q_i(j) tensor image in order,
with all preceding maps bound to the same original axes and holes. The
projection is exact and has norm at most one. Its actual encoded controller,
full T scan, metadata, movement and output storage remain separate paid
prerequisites; they are not implemented by this endpoint package.

Likewise use the original CRT map k -> (k P_i^-1 mod s_i)_i, and its inverse
on the recovered W-bit integer records. Both initial CRT calls and the final
inverse are separate actual-caller prerequisites. The source validity set,
record order, padding and record width W must be bound to those calls. The
already proved permutation cancellation in (2) does not eliminate CRT.
Require S>=2Ndigits-1 to prevent cyclic wrap. Exact ordinary coefficient
and carry bounds, carry flushing and final bit order remain the credited
canonical/#4320 endpoint; this package does not execute a carry scan.

The new owner uses the unchanged authenticated `Arithmetic`, signed-word
operations and `FftWord(base_bits=4096)` fixed scalar engine. Legal pointwise
calls pay 10S exact real products: four input-radius squares, four complex
products and two output-radius squares per coordinate. Recovery pays 4S:
two input squares and the two S products. Each carrier pass pays 2S radius
squares plus exact read/write. All metadata, constructors, Count powers,
full input scans, EOF checks, copies, child returns, cleanup and canonical
head restoration are charged. There is no data-dependent role allocation.

Let M_word(W) denote the retained COMPLETE scalar tariff, including its
setup and backing. For a fixed number of required codecs/carriers, the
new scalar endpoint bill is

    O(S M_word(W)+S W+poly(q+Gamma+b+log S)),           (16)

plus all inherited historical scalar backing. Under the named all-size
scalar contract M_word(W)=O(W log²(W+2)), W=O(p0); this is O(Sp0 polylog p0).
The small witness uses only the fixed engine's base branch; it does not
establish its FFT branch or the all-size scalar theorem.

Keep three complete costs of the actual expansion, cached/Cyclic middle,
compression, extraction and native/external interfaces, plus two forward
and one inverse CRT cost, (16), carry storage and final output work. Every
middle still contains its full three Fourier calls at actual f and P=f+A.
Their suppliers, source preparation, routes, stock, restoration and all
active/inactive historical extents remain charged. The only supplied
expansion reference already has an Omega(Tq log T) route, so this assembled
numerical allocation is NOT a new fast multiplication bound. Improving it
requires a separately admitted grouped implementation and complete costs.

The construction-only alias-exclusion inventory contains both owned roles
and the original borrowed descriptor tapes reachable through `self.borrowed`.
Those original descriptors are protected members, not owned erasable stock;
only this owner's Count copies are closed. External payloads must be disjoint
from both categories. Calls preserve borrowed bytes and origins, protect
one pending return, consume scalar children and erase owned scratch. Counts
and scalar owners are prepared before sealed execution. No production
transform, extraction or CRT controller is supplied by a numerical callback.

## 7. Evidence and remaining obligations

The independently written exact rational checks include Gamma=0, positive
Gamma, S=1, b=1, strict final error, actual source-order allocations and the
full pre-drop width bound. Native fixtures use S5/b3 with Gamma=0,q26,W44
and Gamma=2,q32,W56. They run genuine scalar products, the public q+3 codec,
exact native carrier/conjugation, the deferred shift and nearest recovery.
Both recover [28,38,51,32,5]. The actual zero-Gamma endpoint on the latter
deferred return yields [0,1,1,0,0], distinguishing the missing scale.
These are endpoint fixtures, outside the q>=101 expansion-source domain;
they do not execute the hypothetical three transform returns they model.

Finite supporting checks and written universal proof have separate roles.
Production transform/context delivery, T-to-S extraction, CRT, all native
and scalar supplier premises and the final complete fast cost remain open.
This discharges the named normalized-channel allocation/scalar endpoint
implication under those contracts, not the full analytic_recovery assumption
or any unconditional multiplication theorem.
