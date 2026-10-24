# A physical normalized Gaussian compression core

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
I implement one principal-window compression map under the retained
Gaussian analytic premises. I use Chafik Boukhalfa's PR489 local inverse,
the RaD phase-cell/microbox construction, and PR3787's concrete word
multiplier. I retain their exact sources and notices in SOURCES.json.
I distinguish this algorithmic argument from the finite author checks
in EVIDENCE.md and from the enclosing tensor/CRT construction.

## Contract and production domain

Write rho=t/s=1+theta, u=alpha², and let p be the target precision.
The caller supplies canonical encoded parameters and complete tapes at
their origin heads. I require the retained production conditions

    p>=101, 1<rho<2, u>=ceil(log2(8p)), u*d<=p,
    1/(4d)<theta<1/(2d-1),
    w=ceil(sqrt(16p/u))+2, d-2>4w, P=32768p.

`ProductionPlan` checks these inequalities with encoded arithmetic and
derives w and P. I bound s,t by p-bit descriptors and the lifted interval
descriptors by p+2 bits. These bounds hold in the intended outer domain
and make the rational Gaussian arguments O(p)-bit descriptions.

For the target halo [a,b), I compute the exact source interval I=[A,B):

    A=ceil(s*(2a-1)/(2t)), B=ceil(s*(2b-1)/(2t)).

Indeed q_j=floor(t*j/s+1/2) lies in [a,b) exactly for these integers j.
I check the first/last included selections and the adjacent excluded
selections. I retain a core K=[c,e) inside I. Put m=B-A and J=512p².
The production wrapper requires

    s-m>w, c-A>J*w, B-e>J*w.

The strict margin follows the source's stated convention. The weak
inequalities with J*w would also suffice for paths of length below J.
The caller supplies the complete target halo with complex p-grid values
of modulus at most one. I validate that disk bound during the first
selection scan. I return the core in increasing lifted source order,
with p+2 signed bits per real/imaginary component, preserve borrowed
values and origin heads, and restore owned scratch. The caller must
consume protected preparation and core outputs before reusing their owners.

`Preparation.run_production` passes its derived P,w to the same
`run_explicit` implementation. The explicit method permits smaller finite
grids for algorithm checks; it does not supply the production error
guarantee outside the hypotheses above. I never infer that guarantee
from a small successful packet.

## One global rounded matrix

I fix q_j, beta_j=rho*j-q_j, and

    F_j=u*(1/4-beta_j²)/theta, a_j=exp(-pi*F_j).

I use one deterministic coefficient rule for the global axis, independent
of the window. With eta=2^-P, it supplies positive downward a_hat_j and
downward G_hat_delta approximating exp(-pi*u*rho*delta²), with error
below 2eta. I set G_hat_0=1 and G_hat_delta=0 beyond w. I also prepare
the directed cross-cell coefficients and

    D_norm,j=2^(-2u)*exp(pi*u*beta_j²).

Within a global phase cell I retain the exact rational entry
`a_hat_j*G_hat_(j-l)/a_hat_l`. Across cells I use the directed dyadic
entry for cyclic distance at most w. I set the diagonal exactly to one
and the remaining entries to zero. I call this matrix H.

The retained phase proof gives `a_j>2^-8p`. The stronger coefficient
error below implies `a_hat_j>2^(-8p-1)`. I therefore retain the source's
ratio, row-dominance and perturbation estimates:

    ||H-N|| < e_p = p*2^(16p+7)*eta +2^(-46p),
    gap(H)>=1/(8p), ||H||<2, ||H^-1||<=8p.

I construct H on the global residues before restricting a window. When
lifting across a period, I cut cells by both the global phase and the
physical period. I do not merge the last and first global cells merely
because their lifted phase names agree. `Axis` can serve several window
pages. Separate explicit preparations deterministically reproduce its
same coefficients; even recomputation over all polynomially many axis
origins remains polynomial setup. I charge that setup separately.

## Certified coefficient generation

I give the new encoded interval routine explicitly. Let F>=1 be an
integer upper bound for every nonnegative rational argument f used by
one axis, and let B_f bound its descriptor bit lengths. The axis uses
the ceiling of the larger of

    u/(4theta), u*(rho*w+1/2)².

This also bounds the kernel and normalized-diagonal arguments. Under
the production domain, F<=256p and B_f=O(p).

I reuse weight and normalization coefficients at reflected source indices.
For integer t, the nearest-grid offsets obey beta_(s-j)^2=beta_j^2;
at a half-integer tie both offsets equal-1/2. Once s-j<j, I copy the
earlier two coefficients after checking equality of the encoded squares.
I still compute each row's phase and nearest index separately. This uses
the same deterministic coefficient rule and preserves the global H.

Set X=4F, k=ceil(log2(8(X+1))), H0=P+X+k+16, c=ceil(log2 H0), and

    R=P+4X+4k+2c+64,
    J_pi=ceil(R/4)+8, N=ceil(R/3)+8, h=2^-R.

I compute a directed Machin interval on the R grid. Its width is at
most `(20J_pi+40)h`. The alternating tail fits one R-grid unit since
`25^J_pi>=16^J_pi>2^R`; the second Machin denominator gives a smaller
tail. I retain the inherited integer Machin implementation and its signs.

I multiply the interval by the exact rational f, round outward, then
divide by 2^k with directed rounding. For P,F>=1, I have H0>=27,
R>=115, R<5H0, N<=R/2 and

    width(pi)<=7R h,
    width(x)<=(7RF+2)h,
    width(y)<=(7R+65)h/32 <=R h/4,
    0<=y_lower<=y_upper<=1/8.

For the last inequality, `2^k>=8(X+1)` and `h<=2^-k` absorb the
outward shift. The Machin enclosure and pi<16/5 give x_upper<X.

I sum N positive Taylor terms for exp(y), starting with the exact
constant one. For each degree j I compute the lower recurrence by
flooring the product to the R grid and then dividing downward by j;
I use ceilings in the upper recurrence. Nested floors/ceilings preserve
the required rational quotient bounds. Every upper term remains at
most one. With Delta_y the argument width, the term widths obey

    d_j <= d_(j-1)/8 +Delta_y+4h <=2Delta_y+5h.

I stop earlier if the current upper term is at most one raw R-grid
unit, after adding that term to both sums. The current exact term is
then at most h for every enclosed y. Subsequent term ratios are at
most1/8, so the remaining positive tail is at most h/7<h. I explicitly
close the encoded loop iterator on early exit to release its scratch.
If I complete all N terms, the omitted tail is below `(8/7)*2^(-3N)<h`.
In either case I add one upper grid unit. With at most N updates,
summing the widths gives E_0<=R²h. The accumulated upper
rounding error is below `(16/7)Nh+h<=3Nh`, so
`log(u_0)<=y_upper+3Nh`.

I perform k outward-rounded squarings. Since each lower endpoint is at
least one, the widths satisfy `E_(i+1)<=2u_i E_i+2h`. The product of
these amplification factors is at most `2^k exp(X+1)`: the accumulated
rounding contribution to its exponent is below one because
`2^k(3N+2)h<1`. Therefore

    E_k <=2^k exp(X+1)(R²+2)2^-R
        <2^(-P-2X-3k-57) <=2^(-P-83).

Here I used `R²+2<=32H0²` and `exp(X+1)<2^(2X+2)`.
For decay I invert this positive enclosure, then round outward on the
R grid. Inversion cannot increase its width on [1,infinity), and this
last rounding adds less than 2h. Both growth and decay enclosures thus
have width below eta/2.

A further factor 2^-sigma, sigma>=0, decreases width. Final outward
P-grid rounding gives an endpoint gap at most two units and a downward
coefficient error below 2eta. I need an approximation, not the exact
irrational floor. The production diagonal uses sigma=2u=O(p). I charge
the final shift scan; I make no bit-length-only cost claim for an
arbitrary enormous sigma in the explicit API.

The routine keeps a fixed number of O(R+X+B_f)-bit carriers. Its
conservative ordinary-arithmetic cost is O(R³+(R+B_f)²), with
O(R+B_f) space. Production P=32768p, F=O(p), B_f=O(p) give polynomial
setup and linear working precision. I also check the interval width
at runtime; the inequalities above establish that check for the domain.

## Exact old-H Schur setup

I intersect I with the original global cells. Pieces of length at most
4w are entirely boundary. For each longer piece I retain its first and
last w rows as boundary. The two w-row interior-edge buffers are then
disjoint. I preserve increasing source order in both position lists.

Write A=D_a G D_a^-1 for an old interior block, where G uses the
independently rounded, truncated kernel above. I invert this exact G
during setup. For two boundary rows in the same cell, I compute the
Schur correction as

    (a_hat_b/a_hat_c) * G_bI G_II^-1 G_Ic.

The intervening similarity weights cancel exactly. For rows in different
cells the correction is zero, because no two cell interiors interact.
This computes precisely `H_BI H_II^-1 H_IB` for the original H. I never
use PR489's dense local q-model in this calculation.

I form exact rational S=H_BB-H_BI H_II^-1 H_IB, round S to P-grid
dyadics, compute exact LU of that rounded matrix, and only then round
the online factors and reciprocal pivots. The source's dominance
induction supplies positive pivots. Original width-w edges cannot
increase their index separation when I remove interiors; each new fill
joins the two boundary groups of one cell. Thus the boundary half
bandwidth is at most 2w, including clipped pieces. I check zero fill
outside that band before emitting it.

I reduce each setup rational after arithmetic. For a k-by-k matrix
with B-bit numerators/denominators, clearing denominators per row gives
integer entries of at most (k+1)B bits. A coarse minor bound is

    D=k(k+1)B+k*ceil(log2 k)+2.

Reduced elimination entries are ratios of such minors. Temporary
products have polynomial bit length; unreduced repeated fractions would
not justify this statement. Ordinary binary division and Euclidean gcd
give a conservative O(D³) arithmetic bound. Repeated full matrix scans
remain polynomial. For example, O(k^10(B+log k)^3) time and
O(k^4(B+log k)) scratch safely cover this implementation. I exploit
the exact similarity cancellation to reduce finite execution cost,
without changing the matrix or its error analysis.

The protected page contains selection offsets, cell descriptors,
rounded local factors/couplings/normalization and the two ordered
boundary-factor banks. `Preparation` clears its dense matrices before
returning the page. An isolated window retains the stated setup-time
and setup-space terms; I do not absorb them into its payload alone.

## Online local inverse and exact convolution

I retain PR489 at head8922e3b3f0fd7772b0fb42028eb2532984c3ab42.
For downward q approximating exp(-pi*u*rho), define

    f_j=product_(k=1..j)(1-q^(2k)), h_j=(-q)^j/f_j.

The classical q-calculus factorization gives
`G_q^-1=D_f^-1 T(h)^T D_f T(h) D_f^-1`. Chafik Boukhalfa specializes
and bounds it in the retained proof. I compute exact rational f,h
offline, round their factors/reciprocals to P, and execute

    a_hat^-1, 1/f, T(h), f, T(h)^T, 1/f, a_hat.

This uses two triangular convolutions and five diagonal passes. PR489
bounds its error against the OLD A inverse by `2^-36p*max(1,||b||)`;
it does not identify the two matrices. I retain its local-model
perturbation allowance and all stated hypotheses.

For each signed convolution I split both integer sequences into positive
and negative parts and execute four actual nonnegative word products.
If a,b bound the measured coefficient bit lengths and n is the length,
I use slots of

    S=a+b+ceil(log2 n)+1 bits.

Every nonnegative convolution coefficient is strictly below 2^(S-1).
Thus no radix carry crosses a slot. I accumulate all four signed terms
exactly in S+3 signed bits and truncate once by P after completing each
coordinate. I consume the complete 2nS-bit child returns, including the
unused high convolution coefficients. Reversal changes record order
while preserving each record's internal bit order. The reversed upper
convolution therefore has the source's stated orientation.

I call the authenticated FftWord implementation, with a fixed crossover
4096. Its internal ring multiplier remains Karatsuba. The dependency is
acyclic, and the word bound is O(N log²(N+2)) for N-bit arguments.
Since n<=5p and each slot has O(p) bits, each local convolution costs
O(n p log²(p+2)). Packing, extraction and reversal add O(np).

## Both interior passes and the boundary solve

I execute the complete source composition:

    y_I=approx_A_inverse(b_I),
    r_B=round_P(b_B-H_BI*y_I),
    x_B=approx_S_inverse(r_B),
    x_I=approx_A_inverse(round_P(b_I-H_IB*x_B)).

I gather C-selected input once per real/imaginary component. For each
cell I retain its two short edge buffers for coupling rows; I do not
rescan its full interior for each coefficient. I scan the prepared
factor page in order and repeat it for the second pass.

For the lower solve I accumulate a complete row at 2P fractional bits
and truncate once. For the upper solve I multiply the unrounded row
residual by the stored pivot reciprocal and then truncate from 3P to P.
I use bounded O(w)-record buffers, forward/backward factor banks and
complete row reversals. These operations match the source's residual
analysis; repeated row-wise relative-error estimates would be incorrect.

I merge x_I and x_B into the original source order, multiply by the
stored D_norm, divide by 2^j with j=ceil(log2(32p)), and truncate once
to the p grid. I retain only the declared core rows. I repeat the same
real operator on the imaginary component and interleave the results.

## Explicit stored-value guard and error

Analyze the rounded algorithm with unbounded integer carriers first.
The retained factor bounds give

    ||L||<=65p², ||L^-1||<=32p, ||U||<2, ||U^-1||<=1040p³.

With rounded lower factors and the effective upper diagonal defined by
the stored reciprocal, perturbations are at most 2p eta and 3p eta.
The product perturbation is below 200p³eta. Neumann perturbation gives
`||L_tilde^-1||<=64p`, `||(L_tilde U_eff)^-1||<=32p`, and
`||L_tilde||<=66p²`. The forward/effective-backward residuals are below
2eta and 8eta. The combined residual is below530p²eta<1.

I obtain the following conservative magnitude bounds:

| Completed stage | Bound |
|---|---:|
| First interior | 9p |
| Boundary right-hand side | 28p |
| Forward solve | 2^11 p² |
| Boundary solution | 2^10 p² |
| Second interior right-hand side | 2^12 p² |
| Second interior | 2^16 p³ |

Each rounded central local factor has norm below two, the first weight
reciprocal has norm at most 2^(8p+1), and the final weight has norm at
most one. Local interpreted prefixes and partial convolution sums are
below 2^(8p+18)p². Forward-row partial sums are below2^18 p^4;
backward numerators and post-reciprocal values are below2^13 p² and
2^17 p³. Therefore

    G=8p+8ceil(log2(p+2))+32, W=P+G+2

supplies signed storage with at least twelve spare magnitude bits under
these bounds. Exact double/triple-fraction products and packed words
retain their separate widths until rounding. The finite tests check
headroom failures; these inequalities supply the all-size justification.

I use PR489's whole old-H composition bound and the smaller original
unbatched boundary allowance. Conservatively, its complex completed
inverse error is below2^-32p. The retained resolvent bound gives
`||H^-1-N^-1||<=32p²e_p<2^-42p`.

For locality, a bandwidth-w path of length below J stays inside I for
each core row. The complement gap rules out a short cyclic edge between
the artificial ends. With g=1/(16p), the two Neumann tails give

    ||R_K H^-1-R_K H_I^-1 P_I||
      <=2(1-g)^J/g <=32p*2^-32p <2^-16p.

The normalized diagonal error contributes less than18p eta, and final
complex p-grid truncation contributes at most sqrt(2)*2^-p. Selection
and exact normalization do not enlarge the other bounds. Their sum

    sqrt(2)*2^-p +2^-16p +2^-32p +2^-42p +18p eta

is below2*2^-p for p>=101. The exact normalized global compression has
norm at most1/8, and the principal normalized map has norm at most1/4.
I therefore retain the disk-grid return and the source's looser scalar
p² error interface. For outer restoration I count the actual resampled
axes explicitly. Each expansion S_i/2 and compression normalization
contributes 2u_i+j_i+1 to gamma. Thus gamma=sum_i(2u_i+j_i+1), or
D(2u+j+1) for D axes with common parameters. The bulk tape report uses
D=d-1; the phase-spacing parameter d here does not count those factors.
The outer caller must implement the later 2^gamma restoration and retain
both final integer-recovery S factors.

## Complete bill and ownership

Let n_B be the boundary count, n_I the total interior count, and c the
number of long pieces. The source gives n_B<=4mw/d+12w and
c=O(m/d+1). Across both components the exact word-API call count is

    20n_I +16w²c +2n_B(4w+1) +2m +2n_target +2n_core +32c.

The last32c calls are packed products on O(cell_length*p) bits; the
others use O(p)-bit arguments. I include input/output disk checks and
normalization in this count. Selection, page copies, short buffers,
reversals, protected-return consumption and cleanup cost their scanned
volume. Thus the online time and space allowances are

    time O((m+mw²/d+w²)*p*log²(p+2)),
    space O((m+mw²/d+w²)*p).

The space bound includes copied factor banks; it is not a claim of
O(mp) space for an isolated window when w²/d grows. Add polynomial(t,p)
exact setup time and scratch. In the retained bulk domain,
log t=O(p^(1-epsilon)) and V>=2^(c0 p), so each fixed polynomial setup
and all catalogue pages have size/time2^o(p). The complete spectator
stock pays page setup/copying. Regeneration per input line would break
that allowance. This package implements one page and its consumer;
the enclosing catalogue/halo schedule remains a separate caller.

With epsilon=.997, rho_exponent=.002 and delta=.0001 to absorb logarithms,
the source's complete structured arithmetic has power .9981, below
the inherited full Fourier power .99827619697. I retain the positive
gap .00017619697 as an arithmetic allowance, not a selected exponent.

Each owner allocates a constant pool before execution. Numerical loops
borrow leases; matrices and position lists occupy serialized tape bodies.
The nested call graph has fixed depth apart from the inherited encoded
word stack. I seal physical constructors during completed macros, suspend
parent scopes around child calls, consume child returns and clear owned
bodies before returning. Diagnostic host counters do not choose data
operations and can be omitted. Host backing arrays retain their largest
prior blank extent across reuse; the high-water storage bound applies
to the largest retained packet/setup.

## Verification boundary and credit

I execute the full finite producer/consumer join, signed data, nonzero
couplings, both local passes, physical seams and clipped cells. I compare
the pages with independently computed old-H Schur factors and the output
with staged and dense exact models. I also test public preparation cleanup,
malformed packets, ownership, reuse and production metadata. I do not
execute an asymptotic production packet at P=32768p in these finite tests.

I credit Chafik Boukhalfa's PR489 and its PR481/486 predecessors, the RaD
project (hipotures) and its retained CC0 notices, Mason Hale's certified
interval reference, Dugongue's scalar ABI precedent, the classical
FFT/Karatsuba/q-calculus identities, and the inherited Harvey–van der
Hoeven, OpenAI manuscript and Douglas Colkitt framework. Codex assisted
the mathematics, code, source analysis and checks. I claim no independent
human or formal-kernel review. Gaussian expansion, the complete tensor
layout/catalogue integration and the CRT/integer join remain open.
For that next join, one exact expansion axis has norm below3/4, while
PR3763 requires input norm at most.6. Two axes give exact norm below9/16;
an accumulated expansion error below3/80 would suffice. I state this
only as a conditional handoff. The physical caller must establish its
error and restore the complete natural tensor order before that call.
