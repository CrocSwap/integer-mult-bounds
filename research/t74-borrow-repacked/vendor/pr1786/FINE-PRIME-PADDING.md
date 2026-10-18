# Fine prime padding with separate setup and online precision

This extends the capped phase-cell construction of PR1673 and the
fractional-shift interiors and radix-union schedule of PR1758. The finite
supplier is the unchanged signed-554 T74 supplier admitted in PR1699.
The new mechanism is a finer choice of source primes. Its smaller phase
increment changes the chirp budget, provided coefficient setup is allowed
more precision than the online records. The boundary uses the retained
explicit Strassen format; no structured-solver stability claim is needed.

The exact ledger gives conditional
`kappa=0.001679754788150048`, rounded strictly below the derived saving.
The conclusion retains the all-size hypotheses listed in section 8 below.
Finite checks do not prove those hypotheses, the cited prime theorem or the
complete multiplication theorem. No practical cutoff is claimed.

## 1. A source-prime interval finer than 1/d

Retain the dyadic target box of the assembly construction. Its dimension is
`d=Theta(p^epsilon)`, `0<epsilon<1`, its target side lengths are r or r/2,
and `log r=Theta(p/d)=Theta(p^(1-epsilon))`. For integer p set

    eta_p = 1/(4p^2).

Choose distinct primes s_i in

    (1-2 eta_p) t_i < s_i <= (1-eta_p) t_i.

Here is an unconditional replacement for the old source-prime interval
lemma; it does not require a new prime-gap conjecture. Trudgian, *Updating
the error term in the prime number theorem*, arXiv:1401.2689v2, theorem 2,
proves for x>=229 that

    |pi(x)-li(x)| <= 0.2795 x (log x)^(-3/4)
                         exp(-sqrt(log x/6.455)).

[Primary source, theorem 2](https://arxiv.org/html/1401.2689v2#S2).
This theorem is a cited mathematical input, not re-proved by the verifier.

Apply it at the two endpoints of the requested interval about x=t_i.
The logarithmic-integral difference is at least `eta_p x/log x`. The sum
of the two errors divided by this main term is bounded, for a fixed C, by

    C p^2 (log x)^(1/4) exp(-c sqrt(log x)) -> 0.

Indeed `log x=Theta(p^(1-epsilon))` and epsilon<1 is fixed, so its positive
power dominates log p. Consequently the interval contains eventually at
least `x/(8p^2 log x)` primes. This exceeds d, since x is exponential in
`p^(1-epsilon)` and the denominator and d are polynomial in p. Both target
sizes satisfy the estimate. Their intervals are disjoint, so all d source
primes can be made distinct, odd and coprime to their dyadic targets.

The deterministic search used by the assembly still works: scan the
intervals and test candidates by trial division. Even scanning all O(r)
candidates with O(sqrt r) divisors and polynomial bit overhead costs
`O(d r^(3/2) poly(p))`. Its logarithm is `O(log p+p/d)=o(p)`, hence setup
is `n^o(1)=o(n)`. No unknown threshold is used as a claim of practicality.
The algorithm can fall back on the retained multiplier for smaller inputs.

Let `rho_i=t_i/s_i=1+theta_i`. The interval gives

    1/(4p^2) < theta_i <= 1/(2p^2-1) <= 1/p^2.

Also `S/T > (1-1/(2p^2))^d >= 1-d/(2p^2) > 1/2` eventually, since
d<=p. Thus the same capacity bound `T/2<S<T`, permutations, distinct-prime
packing and source/target side sizes are preserved. The changed lower
bound on theta is explicit; we do not reuse the old `theta>=1/(4d)`.

## 2. Polynomial conditioning survives the smaller increment

Keep `alpha=ceil(sqrt((4/pi) log(16p)))` and `a=pi alpha^2`. Eventually
`4 log(16p)<=a<=5 log(16p)` and alpha^2=Theta(log p). The sharp row estimate
of PR1673, LOG-A-PHASE-SCHUR-AUDIT section 1, is valid for every theta>0:

    ||N-I||_infinity <= exp(-2 a theta)+5 exp(-2a).

For theta>=1/(4p^2), its row gap is at least `1/(8p^2)` eventually; for
example `1-exp(-2a theta)>=1/(4p^2)` while the second term is O(p^-8).
Omitting the exponentially small nonzero diagonal aliases and setting the
diagonal exactly to one preserves a polynomial gap. Exponentially accurate
band truncation and coefficient rounding preserve half of it. Every principal
narrow block has the same row gap, and its Schur complements retain that gap.

The broad bound in FORWARD-SMALL-A-AUDIT sections 1-3 already states its
dependence on theta explicitly:

    ||K^-1|| <= O(alpha^5 rho^2 theta^-2 exp(a rho/3)).

This is polynomial for the new theta. Since rho=1+O(p^-2), the exponential
factor is at most p^2 eventually, theta^-2<=16p^4, and alpha^5 is
polylogarithmic. The finite and bilateral LDU entry bounds are geometric
in index distance and bound both row and column sums. The same estimates
apply to the finite contiguous sections used by elimination. The augmented
forward matrix adds identity hole columns and a Gaussian coupling of bounded
row and column sums. Thus a conservative common eventual bound p^10 covers
the relevant matrices and their inverse norms, in both induced row/column
norms and spectral norm. Polynomially small perturbations preserve it with
slightly larger constants. This bound is independent of the number of cells.

Physical-prefix elimination still consists of one contiguous prefix and
disjoint future interiors separated by at least the bandwidth. The eliminated
matrix is a direct sum of such sections. A Schur inverse is a principal block
of the corresponding full inverse; its norm is therefore polynomial too.
Schur norms follow from `D-C A^-1 B`. These are the same prefix geometries
used in the retained dense no-pivot boundary argument, with new polynomial
constants. No general stability assertion for structured generators is used.

## 3. Setup precision must increase; online precision need not

The old absolute weight precision cannot be retained. For the narrow weights

    w_i=exp(-a(1/4-beta_i^2)/theta),

the negative logarithm can now be as large as `a/(4 theta)=O(p^2 log p)`.
Rounding these weights absolutely to Cp bits can produce zero. The finite
checker includes a concrete underflow witness; this is a required change.

Let `L_p=ceil(log2 p)` and let C be a sufficiently large fixed constant.
Use setup precision

    P_setup = C p + 64 p^2 L_p.

Eventually `a<=16 L_p`, so `a/(4 theta)<=16 p^2 L_p`. Since log 2>1/2,
rounding a weight downward with absolute error at most `2^-P_setup` gives

    |w_hat_i-w_i|/w_i
      <= 2^-P_setup exp(a/(4 theta))
      < 2^(-C p).

The weights remain positive. Increasing C by a fixed amount supplies any
additional polynomial slack needed below. Computing these polynomially many
bits, exponentials, exact anchored ratios and local inverse/factor pages takes
polynomial time in p. Schoolbook arithmetic and ordinary convergent series
already suffice; no use of the improved multiplier at a larger precision is
required for this setup bound.

Define one globally fixed rounded reference matrix H as in the retained
audit: within each original phase cell use positive rounded weights and a
single rounded, truncated Toeplitz kernel, and across cells use rounded
Gaussian entries, with diagonal exactly one. The weights use P_setup, while
the kernel and the actual online pages need only a sufficiently large
constant times p bits. For distances at most W, weight ratios have logarithmic
range O(aW)=o(p). The truncation tail is bounded directly in the Gaussian
entries, independently of the full-cell weight range. Hence H differs from
the exact Gaussian matrix by `poly(p) 2^(-(C-o(1))p)` in row and column norm.
This preserves the polynomial conditioning in section 2. All actual Schur
and inverse tables are computed for this H, with the same perturbation budget.

The data circuit never multiplies by the full-cell weights. Use PR1758's
exact fractional-shift identities, whose algebra holds for every theta>0.
On a capped block of length at most B, the narrow remaining chirp has
logarithmic range O(a theta B^2); the broad chirp and its leftover linear
term have range O(b0 theta B^2+b0 theta B), where b0=pi/alpha^2. Each is at
most O(a B^2/p^2). The shifted Toeplitz kernels remain accretive: their shift
gap is at least theta/2, and the explicit symbol bound of PR1758 gives
polynomial inverse norms when theta^-1=O(p^2). Its accretive shallow-circuit
theorem therefore has polylog(p) guard bits per axis, as before.

The ideal shifted representation and H need not have identical stored
coefficients. Their difference has the bound just established: replace the
old raw `Cp` weight precision by P_setup in the comparison in PR1758 section
2. Local shifted kernels and anchored chirps are generated directly, then
rounded at online precision. Across g axes the uncompleted amplification is

    exp(O(g a B^2/p^2 + g polylog p)).

Thus O(p)-bit records suffice whenever

    beta + 2 xi - 2 < 1,    beta < 1.

The inverse comparison also stays within the error budget. If an ideal
interior A and the rounded reference H_II differ by Delta, then
`H_II^-1-A^-1=-H_II^-1 Delta A^-1`. Both inverse norms are polynomial;
the error changes only by a polynomial factor. Telescoping through the
constant number of completed factor stages, and through g tensor axes,
uses the stated chirp/prefix guard. Exact identity of their rounded
coefficient lists is neither assumed nor needed.

Setup arithmetic at P_setup is separate from these records. It is not placed
inside an online motif call or multiplied into the per-record data cost.
PHASE-LAYOUT-AUDIT already permits polynomial coefficient/page generation
per complete microbox and axis, amortized by the superpolynomial inner and
spectator payload. Replacing its polynomial by another fixed polynomial
preserves that argument: `L^g` and every full unused source-axis range exceed
every fixed polynomial in p. The number of pages, capped pieces, axes and
required bits is polynomial. This is an asymptotic amortization, not a claim
that P_setup or the eventual cutoff is practical.

## 4. Normalize completed maps with powers of two

The exact Gaussian resampling identity and the coprime source/target
permutations do not require theta to be of order 1/d. They require the
positive separation and invertibility established above. The completed
forward, inverse and diagonal factors can have larger polynomial norms
than in the old parameter family. Divide each such completed map by an
additional dyadic factor of at most `2^ceil(100 log2 p)`. The conservative
p^10 bounds above are then below one. Restore the product of these exact
normalizers at the final scalar shift, together with the retained Gaussian
normalization. This preserves the exact transform identity.

There are O(d) factors; the added shift has O(d log p)=o(p) bits because
epsilon<1. This also bounds the extra accuracy needed before exact recovery.
At a sufficiently large fixed C, data precision is `C p+o(p)=O(p)`.
Completed groups can be treated as contractions, while their uncompleted
prefixes/suffixes use the chirp and circuit guards of section 3. None of
these changes increases the semantic online dimension exponent C1=1.
Offline arithmetic is paid through the setup amortization, not that interface.
The normalizer is scalar: combine its powers into the group coefficients or
apply one scalar per completed group, rather than introducing a full scan per
axis. A constant number of these operations per group is absorbed by the
retained group-scan row. Global restoration is one already-paid exact shift.

## 5. A larger but still polynomial locality window

The old literal row-gap and locality constants must not be reused. A
conservative generic locality argument suffices. For a banded reference
matrix with `||H||_2,||H^-1||_2<=p^10`, put

    Q=I-p^-20 H* H.

Its eigenvalues lie in `[0,1-p^-40]`. With `J=ceil(p^42)`, the polynomial
inverse `p^-20 sum_(j<J) Q^j H*` has error at most `p^10 exp(-p^2)`, below
`2^-Cp` for every fixed C eventually. The bandwidth is at most `2WJ+W`.
Since W=O(sqrt(p) polylog p)<p eventually, a halo `A=C_A p^48` covers it.
The same statement holds for the relevant periodic matrices and finite
sections: the norm bounds are uniform in their length. Polynomial factors
from changing induced norms on a polynomial-size halo are absorbed by
exp(-p^2). This proves a usable replacement for the old Cp^3 locality scale.

Choose dyadic core length `L=2^ceil(128 log2 p)`. Then gA/L tends to zero.
The retained single-face/core correction layout has the same formula with
halo exponent 48 and core exponent 128. Its paid cost power is
`epsilon+beta+48-128+2`; its halo-volume margin is `128-48-beta>0`.
The locality polynomial is used in the proof and coefficient setup. The
online algorithm still uses the capped factorization and compiled circuits;
it does not perform J Neumann iterations on each data record.

An original phase cell now has length Theta(p^2). Capped dyadic carving still
has boundary density `O((W/B) polylog p)`: the additional end-cell contribution
is `O(W log B/p^2)`, dominated when B<=p^2. Clipped physical period cuts and
holes remain boundary. Scalar Schur bandwidth stays O(W), since an eliminated
interior joins only its two neighboring O(W)-size separators. Larger cores
and halos change only fixed powers in offline setup and O(log p) address
fields. Their source axes are still superpolynomial in p.

## 6. Retained Strassen boundary, circuit and union costs

Use the explicit Strassen circuit, with `7^16<2^45`, so choose fixed matrix
target exponent `tau=45/16` and `c=(3-tau)/2=3/32`. PR1673's dense boundary
proof and fixed-format absolute-precision argument apply to the new polynomially
conditioned pages. Block scans, permutations, rewinds and linear combinations
remain charged. Boundary density is still W/B, so its cost power remains
`epsilon-xi+(tau-1)/2` and its saving is `c+xi-epsilon`. This applies to general
rounded blocks and needs no structured inverse algorithm.

The interiors use PR1758's shifted Toeplitz representation and accretive
shallow-circuit theorem, with the smaller theta substituted in the explicit
symbol bound and with section 3's setup precision. Circuit algebra and depth
are unchanged; the condition guard remains polylog(p) per axis because all
inverse norms and theta^-1 are polynomial.

Retain PR1758's radix-distributed union schedule. Complete lines stay in one
flag class and axis operators commute on distinct tensor factors. Its incidence
identity is `sum_r |S_r|=sum_x |F(x)|=sum_i |U_i|<=g mu V`. Each visit already
moves an O(p)-bit record; flag extraction and O(g log L)-bit headers are absorbed
when beta<1. We use PR1758's per-visit argument, not the obsolete 2 beta<1.
Union cost power remains `epsilon+1/2-xi`. No per-axis scan of the whole union
is added, and no vanishing-union fraction is assumed. Support routing,
whole-neighborhood reservation and interchange retain their stated interfaces.

## 7. Explicit parameters and every paid row

Use PR1699's certified endpoint
`b_cert=335950991225108904267/200000000000000000000000`.
Set `b=b_cert-10^-64`, `q=b-10^-64`, `a_eff=(q+b)/2`,
`r0=10^-64`, `zeta=10^-66`, layout slack `s=10^-64`, and stopped-recursion
parameter `stop=10^-70`. The bit endpoint is 0.001733427039589844234749.
Choose

    epsilon=9999999/10000000,
    beta=9999997/10000000,
    xi=epsilon(1+q)-3/32+s.

Thus xi=0.90792965478815... . This is an explicit interior point; it does not
assert an attained limiting rate. Since beta<epsilon<1, source axes and unused
spectators remain superpolynomial and the number of groups is polynomial.

| Operation | Cost power | Saving |
|---|---|---|
| Main transforms | 1-epsilon q | epsilon q |
| Global coordinate router | 1-a_eff | a_eff |
| Fused Gaussian groups | epsilon-q beta | 1-epsilon+q beta |
| Group bit router | epsilon-a_eff beta | 1-epsilon+a_eff beta |
| Group scans, including normalization | epsilon-beta | 1-epsilon+beta |
| Strassen boundary | epsilon-xi+(tau-1)/2 | c+xi-epsilon |
| Radix union movement | epsilon+1/2-xi | xi+1/2-epsilon |
| Polynomial products | 1-epsilon | epsilon |
| Core-face corrections | epsilon+beta+48-128+2 | 1-(epsilon+beta+48-128+2) |

Boundary saving equals main saving plus s. With delta=10^-7 and beta=1-3 delta,
Gaussian saving minus main saving is `delta(1-2q)>0`. The global router also
exceeds the main saving. Every other row has larger slack. The minimum is
`epsilon q`, strictly above the rounded headline.

Key side conditions are

    1-beta=3 delta>0,
    1-beta-2(1-epsilon)=delta>0,
    epsilon-beta=2 delta>0,
    1-epsilon-r0>0,
    1-(2xi-2)-r0-beta=0.184140990423...>0,
    1/2<xi<epsilon, xi<2,
    128-48-beta>0, 48>43.

The ledger regenerates the remaining stopped-supplier, endpoint, logarithm
and layout conditions. A separate implementation reconstructs the point and
all nine powers. Fourteen rejected variants include the old theta guard,
old union scan, group=dimension, epsilon=1, an unsupported Strassen exponent
and halo/core choices outside the stated locality witness. These failures
are scoped to this proof and point, not universal lower bounds.

## 8. Scope, sources and open obligations

Newly supplied here: the effective fine-prime interval and capacity/search
argument; the polynomial setup-precision replacement; the theta-dependent
conditioning substitution; conservative locality/core choices; scalar
normalization accounting; and the exact parameter composition.

Retained or cited mathematical inputs are Trudgian's prime theorem; PR1673's
Gaussian identities, bilateral/finite LDU, capped factorization, dense boundary
and layout arguments; PR1758's fractional-shift identities, accretive circuit
theorem and per-visit union schedule; and the admitted finite supplier.
Arithmetic and finite simulations do not prove these general statements.

The multiplication conclusion remains conditional on the all-size compiler,
common labels, mutable sources, whole-call hosting, semantic online precision
C1=1, fixed tapes, prime-packing implementation, arbitrary-width equal-chunk
interchange, exact recovery and analytic transfer. The changed prime interval,
setup precision and locality scales are proved above rather than silently
substituted into old numeric hypotheses. No independent human review,
proof-assistant verification, practical cutoff or physical multiplication
implementation is claimed.

Credit Vlado Vojdanovski for PR1673; IdeaOuter, as credited by PR1758, for
fractional-shift interiors and per-visit tag accounting; Jeremy Kothe and
contributors for the package series; and LeverRank for the second schedule
simulation. PR1699's notices retain the complete supplier lineage. PR1672
published the signed-554 kernel first. New material here was prepared by
Chafik Boukhalfa with substantial OpenAI Codex assistance, under Apache-2.0.

Open next questions: independently review setup versus online precision,
uniform prefix conditioning and the enlarged halo; formalize the fine-prime
transfer lemma; improve the finite supplier endpoint. Every new endpoint
still requires a complete paid native word and admission. The extreme
eventual threshold is intentionally not presented as a practical algorithm.
