# Exact dense wrappers and the original paired lifting collector

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance,
including analysis subagents. Apache-2.0. I give a conditional construction;
I have not formalized its all-size machine refinement.

## 1. Statement and inherited boundary

Retain PR2287's completed exact spaced-axis C-layer algorithm and its named
bit-interchange, compiler, precision and parking premises. Retain PR3109's
implementation of an ordered integer lifting map from that baseline.
The latter uses

    epsilon=997/1000, s=1/500, sigma=599/600,
    d=floor(p^epsilon), K=floor(d^s), ell=ceil(p/d).

The scaled-linear subcalls use the exact C endpoint before Hadamard
normalization or truncation. I do not replace any primitive inside that
earlier baseline with the new wrappers below.

For the first paired P104 collector, use the two fixed native recipes
from PR2586 events 2031/2033, as bound by Tekalign's PR3025. At multiplicity
lambda>=1, let n=9lambda, N=2^n, and r=7lambda. Use the explicit field-major
address convention

    index=sum_(i=0)^8 v_i*2^(i lambda),
    v_i=sum_(j=0)^(lambda-1) x_(i,j)*2^j.

The repeated nine-dimensional recipe acts on each column j. Its core
acts on the first seven fields, hence on axes 0,...,r-1 in the original
consecutive order. A caller using copy-major serialization must separately
price conversion to this interface.

Suppose the five source arrays and query have Gaussian-integer numerators
on grid 2^-f. Fix upper bounds w_in+beta=O(lambda) and bitlength(f)=O(lambda),
where w_in bounds their signed component widths and beta>=0 is requested
relative accuracy. Constants in these O bounds are fixed before input.
Choose a working width w=Theta(lambda) large enough for the derived
intermediates, and a fixed p=Theta(w+n). The native calls use the same
declared parameters on return.

Under the retained premises, I construct the original consecutive-order
lifting map with time

    O(N lambda^(2-8003/6000000))

and additional clean space

    O(N lambda^(5991997/3000000))+F.

F is the baseline's fixed compilation allowance. I include the four
exact native monomial wrappers, source/query access, grid processing and
private cleanup. The five source arrays remain unchanged; the private
collector returns to literal zero. The query retains the working grid.
The numerical output equals the credited paired floor program at that
grid, rather than merely approximating its changed-order successor.

The finite executable checks the actual lambda=1 collector and synthetic
tensor wrappers. It uses a direct exact semantic oracle in place of the
fast C algorithm. The uniform time and space conclusion follows from the
written source-bound construction, not timing those finite tests.

## 2. A generalized batched call on a contiguous interval

PR3109 fixes a permanent low-ell-bit coefficient suffix and processes
complete K-bit chunks, one offset at a time. Extend its selected prefix
to a contiguous active interval I of k axes. Keep the same low suffix.
The part of I above that suffix is contiguous; split it into complete
K-bit chunks beginning at its own first position. Group at most d chunks,
then traverse offsets rho=0,...,K-1. Defer I's suffix intersection and
the fewer than K high leftover axes to direct lifts.

Every active axis occurs once. Every fast block contains at most d axes
at one common offset in complete K-bit chunks. Preceding, intervening and
following coordinates remain complete spectators. The number of blocks
is at most k/d+K, and the direct count is below ell+K. This uses the source
contract for arbitrary complete spectators; it does not transpose data.
The same flat low suffix supplies 2^ell Gaussian coefficients per record.

Here p can exceed k: require n=O(p), component widths O(p), n>=ell for
the suffix, and charge direct axes when I meets it. If n<ell, use the
direct branch; this affects only a finite initial range in the stated
actual family. There is no
need to assume n=Theta(k). The proof of PR3109 gives the uniform full-batch
tariff, with V=Theta(Np),

    T_inner(k)=O(Np(k/d+K)d^sigma + Nkd + Np(ell+K)).

The k/d term counts full groups; K retains the short-group allowance.
Do not replace the uniform d^sigma source tariff by k^sigma. Narrow
histories and the wide source history give a conservative space bound

    O(Np + Np d^sigma + Nd^2)+F.

Polynomial header preparation fits the long-record allowance. For finite
initial parameters where the retained asymptotic layout inequalities fail,
execute the same ordered pair word directly and enlarge the fixed bound.

## 3. Exact dense scaled linear maps from scalar-period inputs

For any order of k distinct axes, write L_I for its literal integer lift
and U_I for the ideal C tensor. Tekalign's PR3033 split, retained in
PR3109, gives for g=floor(k/2)+1:

    L_I(2^g q+s)=2^g U_I q+L_I(s).

The inverse has the same identity with the reverse pair order and U_I^-1.
At s=0 this proves

    L_I(2^g q)=2^g U_I q,
    L_I^-1(2^g q)=2^g U_I^-1 q.

Thus the changed inner order disappears from this exact linear endpoint.
No approximation or rounding-recovery argument is necessary.

To implement a source-preserving XOR oracle for D_I=2^g U_I, copy q into
a private bank with g low zeros, run L_I, XOR its signed output encoding
into the separate target, run the literal L_I^-1 and uncopy the shifted
source. For D_I^-=2^g U_I^-1 interchange the two directions. Both accept
arbitrary signed Gaussian integers. They are not mutual integer inverses:
D_I^-D_I=2^(2g)I.

The two inner calls, embedding, output transfer and uncopy are charged.
For k=O(p), added width g+O(k)=O(p) preserves the baseline domain. Use a
predeclared working-width margin so p and the inner plan do not depend
on an observed value. Remove the baseline's temporary precision guard
before returning the caller's integer words; do not enlarge p again at
each nested call. Sequential oracle calls close and reuse history.

## 4. Preserve the original nonlinear stage order

Define L_orig as the literal pair stages in the original consecutive
order. Partition them into consecutive outer blocks of at most h axes.
For each block, use PR3033's residue split and PR3072's protected evaluation
and in-place cleanup, with the exact D_I or D_I^- oracle from section 3.
The narrow residue calculation uses that block's original order. Therefore
each completed block equals its original integer map. Reversing the outer
blocks and their literal narrow words implements L_orig^-1 exactly.

Each in-place block uses four scaled-linear XOR oracle calls, including
their cleanup. Its original narrow word has O(h) component width and
O(Nk^2) time on k<=h axes. I allow a conservative O(Nk^2) clean history
for that routine too; I do not erase a nonzero temporary by fiat.
The same source-preserving evaluation pattern clears the old bank before
the in-place swap.

Summing over at most r/h+1 outer blocks gives the complete bound

    T_orig = O(Np [r*d^(sigma-1)
                    +(r/h+1)*K*d^sigma
                    +(r/h+1)*(ell+K)]
               +Nrd+Nrh)+F.

The Nrd term accounts for the inner narrow work; Nrh accounts for the
outer narrow work. Copies, grid shifts, output consumption, head returns
and scalar scans fit these terms. Binary countdowns implement whole-array
pair splits in O(N times component-width) per axis; the construction uses
no per-butterfly random address. Header setup and countdown reinitialization
remain charged as in PR3109.

Set

    q=epsilon*(sigma+s)=2991997/3000000,
    gamma=(1+q)/2=5991997/6000000,
    h=max(1,min(r,floor(p^gamma))).

In the large linear-precision regime p=Theta(r), h=Theta(r^gamma).
The leading short-group backend term and outer narrow term both have
power 1+gamma of r after removing N. The other powers are

    full inner groups: 2-epsilon*(1-sigma),
    outer tail: 1+q,
    inner narrow: 1+epsilon,
    suffix scans: 3-gamma-epsilon,
    chunk scans: 2-gamma+epsilon*s.

Each is strictly smaller. Since 1-gamma=8003/6000000, the time bound in
section 1 follows. I use the actual inequality
epsilon<gamma<epsilon*(1+s)<1; an outer block can be shorter than dK,
so omitting its K short-group calls would give an unjustified stronger rate.

The complete clean-space ledger is

    O(Np + Np d^sigma + Nd^2 + Nh^2)+F.

The last term dominates at linear precision because
2gamma>max(1+epsilon*sigma,2epsilon,1). This proves the stated exponent
2gamma=5991997/3000000. It is not linear space. Calls reuse the same
workspace after their private outputs and histories return to zero.

## 5. Exact dense Gaussian monomial wrappers

For lambda matched control and target axes, define diagonal phases

    Q(c,t)=(-1)^(sum_j c_j t_j),
    P(c)=i^(sum_j c_j),
    U=C^tensor-lambda on the target field.

Direct two-by-two multiplication gives CZC^-1=-iXZ. For control bit one,
C Z C^-1 Z=-iX; for control zero it is I. Thus

    CNOT_(c->t)=P U Q U^-1 Q.

This is standard character conjugation. Douglas Colkitt's
`direct-selected-xor/REPORT.md` already gives the corresponding Fourier
reduction and its earlier cost boundary; I claim a new source instantiation
and tariff, not a new conjugation identity.

Put g=floor(lambda/2)+1 and embed q as 2^(2g)q. Replace U/U^-1 by the
corresponding L/L^-1 from section 2. The first L^-1 is exact on this
lattice. Its output retains divisibility by
2^(2g-ceil(lambda/2)), hence by 2^g. Q preserves that divisibility, so
the second L is exact too. Consequently

    R(2^(2g)q)=2^(2g) CNOT(q),
    R=P L Q L^-1 Q.

Extract the output by one exact 2g-bit shift, XOR it into the protected
target, reverse the literal R and uncopy the fine source. This uses four
L-family calls per source-preserving oracle. Applying the involution's
oracle twice implements an in-place gate with the old bank cleared,
using eight L-family calls. For a whole-field toggle, use U^2=X_all and
the same construction with L^2. These statements apply to arbitrary
Gaussian integer payloads, including negative values.

The existing `binary_word` compiler factors each fixed invertible binary
matrix into a fixed finite word of field CNOTs and toggles. A field has
lambda contiguous address axes in the declared layout, so section 2's
offset extension applies. Matrix size nine is fixed; the number of gates
does not grow with lambda.

Evaluate each recipe's phase before its affine word:

    lambda*phase + sum_columns(linear_Z4 + strict-upper quadratic terms).

For an inverse, reverse the affine word first and evaluate the negative
phase on the recovered input address. A sequential n-bit address counter
and nine field tapes suffice to scan column bits and accumulate this Z4
phase. Copy/scan/erase those tapes costs O(n) per address; applying the
Gaussian unit costs O(w). Thus all phase and control scans cost O(N(n+w)).
No addressed lookup table or physical tensor transpose is granted.

At n=9lambda and w=Theta(lambda), the wrapper guard and intermediate
headroom add O(lambda) bits. The total wrapper time is
O(N lambda^(2-997/600000)), with PR3109's explicit history charge. This
is smaller than the original-core bound in section 4. A width-one Boolean
payload would pay an additional nonconstant precision factor; I claim no
new Boolean interchange exponent.

## 6. The actual collector, grid and cleanup

The source-bound interval is PR2586 events 2025–2039. It gathers
D31,D30,D29,D28,D27 into zero C, applies the rank-seven outbound transport,
adds C to Q7, applies the paired return, subtracts those sources in reverse
order and erases zero C. The native recipes at events 2031/2033 are exact
linear inverses. For the numerical return, follow PR3025: invert the
outbound wrappers and the same original lifting word, rather than
independently lower the old return recipe with floors.

The outbound right wrapper compiles to 11 CNOTs and seven toggles; the
left compiles to eight CNOTs. Forward plus paired inverse therefore uses
52 in-place field gates, or 416 inner L-family calls, plus phase scans.
These fixed counts do not grow with lambda.

Let S be the gathered sum on grid 2^-f. The original pair-error argument
gives c=r sqrt(N/2) as an absolute error constant. Set

    gamma_grid=ceil(log2 r)+ceil((n-1)/2).

Then c<=2^gamma_grid. If S=0 use F=f. Otherwise let M be the maximum
absolute integer component of S, h_S=floor(log2 M)-f, and choose

    F=max(f,beta+1+gamma_grid-h_S).

This is the credited adaptive policy with its all-size guard. At lambda=1,
gamma_grid=7 and it equals PR3025's beta+8 policy. Embedding S and Q7
on grid F is exact. The wrappers are exact, and the new core equals the
old floor word, so its outgoing error e satisfies

    ||e|| <= c*2^-F <= 2^(-beta-1)||S||.

The paired return gives S exactly. Against the ideal inverse, its absolute
defect is the same ||e||; its relative defect is at most
2^(-beta-1)/(1-2^(-beta-1)) <= 2^-beta. These are paired-execution
contracts, not a uniform relative bound on arbitrary inverse inputs.
Nonlinear query error does not vanish merely because C restores.

Keep F with the query. The returned private C is the embedded S, so its
downshift to f is exact; five ungathers leave literal zero. Sources remain
read-only. Since F-f<=beta+1+gamma_grid, a predeclared width
w_in+beta+O(n+log r) covers the gather, lift prefixes, query and all guards.
This explains the linear-precision hypothesis in section 1. Larger requested
precision or grid-description length needs its own bound.

The complete collector pays two original cores, four wrappers, five gathers,
one query ADD, five ungathers, grid promotion/downshift, initialization,
magnitude and zero scans, metadata and cleanup. These additional scans
cost O(Nw) and the wrappers have the smaller exponent already proved.
The time and space claims therefore cover this complete standalone
collector, under the stated source premises and field-major input contract.

## 7. Supplier stopping decision and evidence

I retain the frozen P104 consumer audit. Its unmodified five-forward/four-dual
bill satisfies

    M(0)>=(5*3070+4*3542+32778)/(73*832)=599/584>1.

This numerical implementation does not remove its paid child ranks or
change coverage. Private clean history is not a productive family and
cannot enlarge the moment denominator. The stronger 416-per-dual forgiveness
screen also rejects the selected saving, but its linear lower bound does
not reject the smaller 8003/6000000 core saving by itself. I keep those
different conclusions separate.

The replay binds the fifteen events, all four native recipe records,
all 512 ideal round-trip columns and their affine maps. It checks exact
guarded CNOT/toggle operations, arbitrary-field offsets, original-order
lifting through 257-bit inputs, and four complete lambda=1 collectors
against the literal predecessor, including dirty cancellation and zero.
Synthetic three-field tensor fixtures cover multiplicities one through
three. I do not claim an actual lambda>1 collector payload replay.

The finite model imports PR3109's direct semantic oracle. Its macro counts
are not machine-step benchmarks. The all-size physical refinement,
clean-space hosting inside a larger caller and the full multiplication
theorem remain open. Reopen the supplier route only with a changed complete
profile, coverage law or consumer whose full bill passes.
