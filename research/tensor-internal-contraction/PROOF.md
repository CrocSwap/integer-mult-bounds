# Internal contraction of the actual staged Tensor expansion

Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
This is an independent informal audit of an existing author proposition in
Jose Manuel/jmbarrancoml's `physical-gaussian-tensor/PROOF.md`, “Norm and
numerical error”. It is a conditional source proof, with finite conformance
checks. It is not formal-kernel or independent human acceptance of the
complete physical construction.

## Quantified boundary

For every admitted original-axis source-produced expansion page, let `p,P,
sigma,s,t,alpha` be its integer fields, `alpha>=2`, `P>=p+2sigma`, and
`u=alpha²`. Retain the producer's normalized nonnegative factors, source
window/crop identity, exact signed word/convolution semantics and ownership
contracts. Caller operand widths are derived below from the actual header. Let `x` be any admitted complex p-grid line in the
input disk, with `R=max_j |x_j|`. The actual `Block.scalar`, joined by `Tile`
and `LineApply`, obeys

\[
 |\widetilde A x(z)|\le {1\over2\alpha}\sum_{j\in\mathbb Z}
 e^{-\pi(j-(s/t)z)^2/\alpha^2}|x(j\bmod s)|
 \le b(u)R,\qquad b(u)={1\over2}+{1\over20^u-1}.
\]

For every finite number of axes `D>=1`, positive row multiplicity `C`, admitted
axis sizes and original-coordinate catalogues, the actual expansion prefix
of `Tensor.run`, through its second complete natural-coordinate gather and
before `self.chirp`, consequently satisfies

\[
 \|X^{(i)}\|_\infty\le R_0\prod_{k<i}b(u_k),\qquad
 \|X^{(D)}\|_\infty\le {1\over2}\prod_{k<D}b(u_k)<3/5
\]

when its boundary input has norm at most `R_0=1/2`. This removes no
approximation error from comparisons with the exact Fourier map: the claim
is solely a hard norm bound for the computed expansion. The preexisting
expansion error, source tails, work-width admissions and remaining supplier
premises stay conditional.

## Each signed internal truncation

Let `Q=2^P`, and write source-page integer numerators as `A_j,K_l,B_z,c`,
all nonnegative; `0<c<=Q/4`. Put

\[
 T_a(n)=\operatorname{sign}(n)\lfloor |n|/2^a\rfloor.
\]

For each signed real **and** imaginary p-grid input numerator `v_j`, the
actual archived `expansion_block.py` and `gaussian_convolution.py` execute

\[
\begin{aligned}
w_j&=T_P(A_j 2^{P-p}v_j),\\
y_l&=T_P(\sum_j w_jK_{l-j}),\\
z_k&=T_P(B_k y_{n-1+k}),\\
f_k&=T_P(cz_k),\\
o_k&=T_{P-p-2\sigma}(f_k).
\end{aligned}
\]

The convolution includes zero padding to `nc=n+m-1`; all `nc` signed
outputs are truncated before cropping the prefix of length `n-1`. Four
sign-separated packed exact products and coefficient-separation checks
implement its signed sum. The word/convolution correctness contract is
retained, not inferred from these finite fixtures.

For every integer `n` and nonnegative `a`, `|T_a(n)|<=|n|/2^a`, including
negative values and zero. Apply this inequality separately at the five
sites above, and apply the triangle inequality at the signed convolution.
Positivity permits replacing every intermediate component by its absolute
majorant. In output p-grid numerator units this gives

\[
 |o_k^{(r)}|\le\sum_j W_{kj}|v_j^{(r)}|,\quad r\in\{\Re,\Im\},\qquad
 W_{kj}=2^{2\sigma}\,{cB_kK_{n-1+k-j}A_j\over Q^4}\ge0.
\]

This is a bound on a nonlinear calculation, not an equality with a linear
map. In particular `T_2(3)+T_2(3)!=T_2(6)`, and negative floor division
fails `|floor(-1/4)|<=1/4`. An error bound on differences cannot be obtained
by treating these truncations as linear or nonexpansive.

Let `m_k=sum_j W_kj` and, in this numerator calculation, `R=max_j |v_j|`. Weighted Cauchy, applied to both components, yields

\[
 |o_k|^2\le
 (\sum_jW_{kj}|\Re v_j|)^2+(\sum_jW_{kj}|\Im v_j|)^2
 \le m_k\sum_jW_{kj}|v_j|^2\le m_k^2R^2.
\]

Equivalently Minkowski bounds `|o_k|` by `sum_j W_kj |v_j|`. Zero rows
are harmless. This step is needed: cancellation in signed components and
several internal component truncations cannot be replaced by one claim
that the final complex truncation shrinks a linear output.

## Internal operand and record headroom

The source header fixes `width=P+ceil(log2(n+1))+3`. These internal amplitude
bounds can be closed without knowing a production tail error. For a unit-disk
input, every component numerator has magnitude at most `2^p`. Promotion gives
at most `Q`; every A/K/B numerator is at most Q. Hence each weighted record
has magnitude at most Q. Every exact convolution coefficient has magnitude
at most `n Q²`, so each truncated convolution record has magnitude at most
`n Q`. Post-B records are at most `n Q`, and fine-normalized records are at
most `n Q/4`. In particular `n Q < 2^(width-3)`: every scalar operand and
work-grid signed record fits the declared width, with room for its sign.
The product owner receives operands within its declared width and returns
an exact double-width product under its retained contract. No fixed-width
wraparound can be hidden inside an inward-rounding argument.

Finally, the preceding Gaussian majorant bounds final complex outputs by
`b(u)<=21/38<1`; their p-grid component numerators therefore fit the
source's signed `p+2` input/output records. `Tile`'s next-axis unit-disk
checks admit these computed outputs. The exact packed convolution's own
coefficient-separation/slot correctness and fixed-tape implementation
remain inherited primitive contracts; this argument closes the caller's
operand widths and intermediate amplitudes, not those algorithms.

## Retained Gaussian identity and windings

The actual `Preparation` supplies downward nonnegative normalized factors.
Here is the source identity rather than an abstract positive-page assumption.
Set `kappa=s/t`, let the original block target start be `z0`, put
`j0=floor(kappa*z0)`, `gamma=j0-kappa*z0`, `h=j-j0`, and `k=z-z0`.
`BlockGeometry.prepare_quadratics/exponent` form

\[
 a(h)={(1-\kappa)h^2+2\gamma h+\gamma^2\over u},\quad
 q(k-h)={\kappa(k-h)^2\over u},\quad
 d(k)={(\kappa^2-\kappa)k^2-2\gamma\kappa k\over u}.
\]

Their sum is exactly `(h-kappa*k+gamma)^2/u=(j-kappa*z)^2/u`:
the `h²`, `hk`, `k²`, `gamma*h`, `gamma*k` and constant coefficients
are respectively `1,-2kappa,kappa²,2gamma,-2gamma*kappa,gamma²`.
The selected convolution index is `n-1+k-i`; the kernel's signed origin
`-h_high`, together with `n-1=h_high-h_low`, makes its exponent argument
`k-(h_low+i)=k-h`, including negative starts and fractional centers.
`prepare_page` uses scale `sigma` for A and B, none for K, writes the
lower interval endpoint (or exact unit), and uses exact quotient for c.
Thus the factor values are bounded above by
`2^-sigma exp(-pi*a(h))`, `exp(-pi*q(k-h))`,
`2^-sigma exp(-pi*d(k))` and `1/(2alpha)`. Individual a and d may be
negative; the source's normalization/interval admissions must still bound
the stored values by one. Multiplying these four positive inequalities
and the actual `2^(2sigma)` extraction gives

\[
 0\le W_{zj}\le {1\over2\alpha}
 e^{-\pi(j-(s/t)z)^2/\alpha^2}.
\]

The powers `2^(2sigma)` above are the actual final extraction restoration;
they cannot be omitted or restored before work-grid truncations. Header
positivity alone does not prove this identity for arbitrary supplied pages.
Source-produced pages and the producer's analytic/directed interval proof
are necessary premises. The local finite fixture compares the **actual**
page majorants rationally; it does not independently reprove the interval
backend or the production tail/ratio admissions.

Periodic windows copy `x(j mod s)` for each lifted index `j`, including every
retained winding. If two lifts have the same residue, they retain separate
weights. Enlarging the finite retained source sum to the positive sum over
all integers increases the majorant. Dugongue's all-center row-mass theorem
in `gaussian-expansion-headroom/PROOF.md` bounds that sum by `b(u)<=21/38`.
The Poisson/Gaussian analytic bridge of that theorem remains an inherited
informal premise. PR3910 supplies a separate elementary row audit and local
additive-error disk consequence; it explicitly leaves the staged physical
tile and tensor recurrence outside its replay.

## Actual Tile ownership, halos and layout

`Tile.run` validates one globally ordered target stream. Each block starts at
`next_target`; its length is exactly `min(radius, remaining)`, and `emitted`
advances by that length. The final equality with `target_length` gives one
owner per output, with neither duplicated nor missing targets. The source
block offset is contained in the declared halo. Monotone endpoints permit
retaining the exact overlap in two banks, followed only by fresh source
records. The crop never sums copies of an output. Padding after source_count
is checked zero. These are necessary provenance/layout clauses of the
majorant, not a claim that any positive matrix has the declared origin.

For all axes write the canonical tensor fields as
`[C][K_0...K_(D-1)][I_0...I_(D-1)]`, with `K_i=t_i/L` and initial/final
short slots `I_i=L`. Record width is `r=2(p+2)`. For axis `i` the actual
`Layout` derives

\[
\begin{array}{ll}
C_m=C\prod_{j\le i}K_j,&
A_m=\prod_{j>i}K_j\prod_{j<i}I_j,\\
R_m=r\prod_{j>i}I_j,&
C_h=C\prod_{j<i}K_j,\quad R_h=A_mR_m,\\
C_l=C\prod_jK_j\prod_{j<i}I_j,&
A_l=\prod_{j>i}I_j,\\
O_l=C\prod_{j<i}K_j,&
N_l=\prod_{j>i}K_j\prod_{j\ne i}I_j.
\end{array}
\]

The first short-field move places `I_i` next to its coarse field. Thus
`PeriodicWindows` sees one complete original axis for each of its `C_h`
prefixes, with every remaining coordinate in its `R_h` record. It copies
from the original period `s_i`, preserves signed origins, and fills the
unused capacity with zero records. The inverse move and the line move
expose `O_l` outer prefixes, each of its `K_i` tile pages on `N_l` complete
spectator lines. These products partition the padded tensor; a short-field
move is an exact permutation, not a restriction to selected active support.
`Binding.expansion_header` checks common p/P/alpha/radius/sigma, original
s/t, global signed source/target starts, exact source span, padded capacity
and complete L-record target slot. `LineApply` consumes and clears every
protected tile return before reuse.

Define `E_i` as the deterministic, zero-preserving computed line map on
axis `i`. For any other axis, its halo selection/duplication and zero
extension `H_j` satisfy `H_j E_i = E_i H_j`: each selected spectator line is
identical on both sides; a zero line remains zero. This proof is by
coordinate selection, not additivity. It does not assert arbitrary rounded
maps on the **same** axis commute or that two nonlinear maps on different
axes commute. The actual loop order is retained. Natural source padding
and complete gathers are also exact copies, zero insertions and
permutations, all with induced sup norm at most one. Inducting through the
actual order therefore gives the displayed full-axis recurrence. Halo
multiplicity never introduces a volume factor in a sup norm.

## Evidence levels and complete ledger

| Obligation | Status at this boundary |
|---|---|
| Signed inward majorant at all five actual truncation sites; complex Cauchy step | Proved here as an informal quantified source argument |
| Unique tile outputs and complete axis recurrence with original layout products | Proved here conditional on retained exact physical child semantics; bounded actual execution corroborates |
| Original factor identity, downward intervals, analytic row mass, production source/tail/ratio/concentration admissions | Inherited; not independent interval/Poisson or production-tail acceptance |
| Internal operand amplitudes and header work-record widths | Proved here from unit input, nonnegative normalized factors and the exact header; finite stages checked |
| Exact signed word/convolution, packed separation, bounded-record adapters and fast/native primitive correctness | Inherited; exercised only at declared finite widths |
| Borrowed pages/payload/rows, overlap banks, protected returns, scratch closure | Actual finite positive/rejection traces; all-size contracts inherited and inspected |
| Literal calls/rounding counts, one catalogue read and full halo/gather traffic | Counted in the bounded fixture; none called free |
| General physical asymptotic cost and production native setup/storage F_q, complete supplier and router admission | Existing conditional invoices retained; not reproved or priced as zero |
| Chirp, compression, restored Fourier error, precision allocation, CRT integer recovery and selected κ | Outside this scoped invariant; no frontier change |

The finite p48/P80, alpha2, sigma4, radius1 catalogue uses reduced halos. Its
norm domination survives omitting positive Gaussian terms; it is **not**
assigned production locality, tail accuracy, Fourier identity or asymptotic
supplier conclusions. The actual Tensor intentionally raises a checker stop
at its chirp boundary. Its finally blocks release scratch; no complete
Tensor success or protected Tensor return is claimed. Observation wrappers
only snapshot tape cells through primitive reads and restore heads; all
numerical owners, signed products and truncations run their original code.
The one outward-rounding fault deliberately changes arithmetic and is
isolated from the positive execution. All archive/member/source hashes are
authenticated before import; source integrity is not mathematical truth.
