# Conditional complete tensor join

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
I retain the source premises and contributor notices through `inputs/`.
I checked complete finite execution in both directions against separate
staged references. I retain publication receipts separately from this proof.
I do not claim independent review, production-sized execution or a new
selected exponent in this working proof.

## Boundary and normalization

I use `D` for the actual number of resampled scalar axes. In the retained
bulk notation, `D=d-1`. I borrow a positive number of complete rows in the
original increasing source-box order, with complex input norm at most1/2.
I use one common integer `alpha>=2`, `u=alpha²`, target precision `p`, and
work precision `P`. Each original source length is odd. The target lengths
are `r` or `r/2`, with a final `r` axis, as required by the retained chirp.

For production I retain PR3851 and PR3878's ratio, concentration, separation,
period, core-margin and precision admissions. I use `p>=101`, `P=32768p`,
`sigma=4096p`, `L=2^ceil(log2(p^8))`, and halo `H=4096p³`. I derive each
paired source window with `ProductionTile`, including its `ProductionPlan`.
I compare that window against the original-axis compression producer.

For one axis define

\[
A_i=\mathsf S_i/2,\qquad
B_i=2^{-j_i}D_{\mathrm{norm},i}N_i^{-1}C_i,
\quad D_{\mathrm{norm},i}=2^{-2u_i}\mathsf D_i,
\quad j_i=\lceil\log_2(32p)\rceil.
\]

I retain the exact Gaussian identity from source07, lines103–145 and305–319,
and the rad20 inverse normalization from
`downstream-phase-cell-inverse.md`, lines303–309. With
`N_i=C_i T_i D_i`, these identities give

\[
B_iQ_iF_{t_i}A_i
=2^{-(2u_i+j_i+1)}R_iF_{s_i}.
\]

I therefore restore the complete tensor by

\[
2^\gamma,\qquad \gamma=\sum_{i=1}^{D}(2u_i+j_i+1).
\]

For common parameters I obtain `gamma=D(2u+ceil(log2(32p))+1)`. I retain the
source convention `R F_s`. I do not replace it with an unpermuted transform
or reuse source07's older `gamma=2Du` after changing the inverse normalization.

## Physical schedule

I first pad each source axis from `s_i` to `t_i`, using fixed cuts and zero
records. I then gather the complete natural tensor into canonical
`[all coarse fields][all short inner fields]` order. I include the coarse
fields in that permutation.

For each expansion axis, I move its short field next to its coarse field,
copy the monotone periodic source windows, return the resulting field to
canonical position, and apply the actual expansion tile pages to complete
lines. I interleave halo construction and expansion across axes. Duplication
and zero extension on a different axis commute with a deterministic,
zero-preserving line operation, including its rounding. I make no linearity
assumption about the rounded expansion map.

I scatter to the complete natural target box and invoke the retained chirp
once on that box. I gather its complete result, generate the target halo
boxes, then apply compression one axis at a time. For each axis I retain
the requested source core and zero-pad its rectangular slot to `L`.
I finish with core assembly, the fourth full gather/scatter operation,
fixed-cut removal of global zero padding and exact `2^gamma` restoration.

I generate all compression target halos before restricting any axis. Later
compression acts along different axes. In particular, I do not reuse
artificial-cut output rows as new global halo values. I retain the tensor
locality argument in rad20 `downstream-microbox-resampling.md`, lines232–267.

For a field `i` in `[K_0...K_(D-1)][I_0...I_(D-1)]`, I use the encoded
spectators

\[
C'=C\prod_{j\le i}K_j,\quad
A'=\prod_{j>i}K_j\prod_{j<i}I_j,\quad
R'=2(p+2)\prod_{j>i}I_j.
\]

The short-field move sends `[C'][A'][I_i][R']` to
`[C'][I_i][A'][R']`. The halo or assembly operation then sees one complete
original axis with prefix count `C product_(j<i) K_j` and record width `A'R'`.
For line application I move `I_i` across the suffix inner fields, with
prefix `C product_j K_j product_(j<i) I_j`. I reuse the current page across
`product_(j>i) K_j product_(j!=i) I_j` complete lines.

I preserve absolute signed window origins in the catalogue. I check the
expansion, compression and source-core descriptors against the original
`s_i,t_i`, with floor endpoints for cores and half-shifted ceiling endpoints
for principal windows. The inner compression page omits absolute origins,
so I also retain a separate compression-source descriptor stream. Header
checks alone do not certify arbitrary supplied factors; the theorem requires
pages from the declared original-axis producer.

## Norm and numerical error

I write `h=2^-p`. PR3878 gives the production expansion error
`(sqrt(2)+2^-11)h < p²h` per axis. Its actual staged factors also permit a
norm bound without an additive rounding allowance. Each real coefficient
is nonnegative and rounds downward. Each component truncation can only
decrease complex modulus. I apply the triangle inequality to the exact
real-kernel convolution, then use the Gaussian factor identity after exact
`2^(2sigma)` restoration. For a source-bound page I obtain

\[
|\widetilde A_i x(z)|
\le {1\over2\alpha_i}\sum_{j\in\mathbb Z}
e^{-\pi(j-\kappa_i z)^2/\alpha_i^2}|x(j\bmod s_i)|.
\]

I credit Dugongue's PR3877 for the all-center row-mass bound
`b(u)<=1/2+1/(20^u-1)<=21/38`. I use that analytic bound through the preceding
staged domination argument, rather than importing his different direct-row
rounding recurrence. PR3910 supplies a separate elementary row-norm audit;
its author leaves the tensor caller open.

Starting with norm at most1/2, I keep the computed expansion below
`(1/2) product_i b(u_i)<.6`. Telescoping against the exact axis contractions
gives expansion error below `D p² h`. I evaluate each local error at the
actual computed input; I do not assume rounded maps are linear.

PR3763's complete chirp contributes `(4 sqrt(2) M+22)h` against `QF_t`,
where `M=T/r`, and returns norm below `.601`. This is an admitted input to
compression. I distinguish this `M` from the number of microboxes and the
target-halo length.

PR3851 `PROOF.md`, lines329–354, bounds one production core against the true
normalized global compression by

\[
\sqrt2h+2^{-16p}+2^{-32p}+2^{-42p}+18p\,2^{-P}<2h.
\]

I retain each term: final grid truncation, principal-window locality,
completed solve, resolvent perturbation and normalized diagonal error.
That proof gives global compression norm at most1/8 and principal-window
norm at most1/4. Across disjoint source cores I take the maximum error;
across the `D` axes I add the conservative `2h` allowances. Copying a halo
does not multiply a sup-norm error by its number of copies.

Under those production contracts and the matching complete physical schedule,
I obtain

\[
\|\widetilde{\mathscr F}x-RF_{\boldsymbol s}x\|_\infty
<2^\gamma\bigl(Dp^2+4\sqrt2M+22+2D\bigr)2^{-p}.
\]

I restore by an exact numerator shift, so I add no rounding term. Conjugating
the input and output gives the corresponding opposite-sign endpoint.

I check the encoded sufficient admission

\[
p\ge\gamma+A+\lceil\log_2(Dp^2+32+2D)\rceil+8,
\qquad M=2^A.
\]

Since the parenthesized error coefficient is at most
`2^A(Dp²+32+2D)`, I bound the restored error by1/256. The exact normalized
source transform contracts the half-disk input, so the restored result has
norm below `1/2+1/256<1`. I can therefore narrow to signed `p+2`-bit
components without changing their values. I also check the actual disk and
signed-width boundary during execution.

The explicit p48/P80 fixture uses reduced, separate finite halos. I compare
it only against its complete staged reference. I do not assign it the
production locality, tail, Fourier-identity or all-size error guarantees.

## Complete cost, including the catalogue

I put `T=product_i t_i`, `S=product_i s_i`, `V=C T Theta(p)`, and
`L_h=L+2H`. The production ratio bounds give `T/S<2`. From `L>=64dH` I get
`(L_h/L)^D<2`, so the complete halo boxes occupy less than twice the target
box. I pad only the field currently moving to its next power of two, at
most another factor two in working volume.

I execute ten short-field moves per axis. Each moves a field of size `L` or
`L_h` and costs `O(V log p)`, including padding, cropping and its full
spectators. I charge `O(DV)` for parent copies and child-return consumption.
For a periodic halo I copy one fiber three times, then advance through its
lift monotonically, retaining overlaps. The sum of its output window lengths
is `O((t_i/L)L_h)`. I therefore charge another `O(DV)` for halo and assembly
traffic, with `O(V)` working space.

I execute `CT/L` expansion lines per axis. For compression axis `i`, counting
from zero, I execute

\[
{CT\over L}\left({L_h\over L}\right)^{D-i-1}<2CT/L
\]

lines. I retain PR3878's `O(Lp log²p)` expansion-tile bill and PR3851's
`O((L+Lw²/d+w²)p log²p)` compression bill. Their bills include numerical
validation, coefficient-page scans, normalization and child returns. Summing
over axes gives

\[
O\bigl(V(D+w^2+Dw^2/L)\log^2p\bigr).
\]

I also charge catalogue traffic outside those local consumers. Write
`f=1+w²/d+w²/L`. The complete serialized catalogue has size
`K=O(p f sum_i t_i)`. Each `Catalogue` reader scans it, and each selected
profile lookup scans preceding frames and copies the selected profile twice.
Across the caller I spend `O(DK)` on those operations. Since

\[
T\ge t_{\max}L^{D-1},\quad D\le p,\quad w^2=O(p),\quad L\ge p^8,
\]

I obtain `DK/V=O(D²f/L^(D-1))=O(1)` for the admitted `D>=2` domain.
Thus I pay the complete reloads within `O(V)`.

Within `LineApply` I copy one selected page and skip the unused bank once
per outer prefix, before processing that page's complete line group. The
group has at least `L^(D-1)` lines. This multiplicity pays the page copies,
original-coordinate binding arithmetic and header checks. I do not charge
an original-axis coefficient scan to each numerical line.

For the four canonical gathers I retain the full-support router bill
`O(V p^beta log^(1+tau)p)`, with

\[
\beta={41544341\over41616125},\qquad
\Phi=.99827619697,\qquad
\Phi-\beta={36798102513\over33292900000000000}>0.
\]

I factor each complete descriptor into two involutions, cap each batch's
support at `2p^.997`, and route the whole packet for each batch. I include
the untouched-gap requirement, metadata validation and sorting, the
polynomial planner cost per batch, complete spectators and restoration.
I retain the router's cutoff and literal branch as source premises.

More explicitly, set `tau=332353/332929` and
`b=2^floor(.997 floor(log2 p))`, so `p^.997/4<b<=p^.997`. Factoring a support
of size `k<=n` gives two matchings with at most `floor(k/2)` edges each.
I finish the first matching before the second. The batch count is at most
`n/b+2`. With `b'=min(n,b)`, I sum the retained single-router invoices to

\[
O_q\!\left(V+V\sum_j(2r_j+1)^\tau\log^{1+\tau}p\right)
=O_q\!\left(V+Vn(b')^{\tau-1}\log^{1+\tau}p\right).
\]

For `n=Theta(p)`, I obtain
`beta=1-.997(1-tau)=41544341/41616125`. Each child still recompiles and
refactorizes its batch. I charge its `O(p^6)` planner per batch, global
validation/factorization conservatively at `O(p^5 log²p)`, and all metadata
sorting and wrapper copies. Under `c p<=n<=C_0 p` and
`log2(R+1)<=A_0 p`, I absorb these polynomial costs into
`V=C 2^n R`, uniformly for positive `C`.

The child requires a `ceil(log2 p)^2`-bit untouched interval and reservoir
room per batch. I choose and restore those intervals separately. I do not
assume that the full permutation has one common untouched interval. The
retained cutoff proof makes a failed geometry test a bounded-precision case,
where its literal fallback fits after enlarging the shape-dependent
constant. I also retain the exact B1/sparse endpoint and universal cost
premises. I charge the fixed native compilation and storage `F_q` separately;
I do not rebuild it for each batch or claim its production-prime execution.

Combining these charges gives, in addition to the actual complete chirp,

\[
O\!\left(V\left[
p^\beta\log^{1+\tau}p+D\operatorname{polylog}p
+(D+w^2+Dw^2/L)\log^2p\right]\right)
+\operatorname{poly}(t_{\max},p).
\]

The final term includes the actual original-axis coefficient producers,
exact rational matrix setup, global metadata and catalogue construction.
I retain it even when adjacent equal axes reuse one prepared profile.

To recover the stated target exponent, I use the retained caller-family
hypotheses, with distinct names for the three growth laws:

\[
D=\Theta(p^{.997}),\qquad
u=\alpha^2=\Theta(p^{.002}),\qquad
\ell=\Theta(p^{.003}).
\]

Here `.002` concerns Gaussian concentration. The target axis length is
`t_max=2^ell`; its bit width has exponent `.003`. Rad20 specifies
`ell=Theta(p^(1-epsilon))`. Hence the total target address width and the
chirp outer width `A=log2(T)-ell` are `Theta(p)`. I retain constants with
`p-A=Omega(p)`. These growth laws do not follow from `TensorPlan`'s finite
admissions alone.

I then have `w²=O(p^.998)` and `gamma=O(p^.999+p^.997 log p)=o(p)`.
With Gaussian logarithmic allowance `.0001`, I bound the Gaussian payload
power by `.9981`, below `Phi`. I absorb the gather logarithms using the
separate positive gap `Phi-beta`; I do not spend the larger Gaussian
allowance on that smaller gap. Finally,
`poly(t_max,p)=2^o(p)` fits within `V>=C 2^(c p)`. With the retained chirp
bound, I obtain the conditional total `O(V p^Phi log p)` and `O(V)` space.

## Remaining proof and publication work

Consult the public investigation for completed committed-export and hosted
replay receipts, separately from the author checks. I retain the full
ordinary-supplier and Fourier premises when stating that cost. The complete
CRT conversion and final integer recovery remain outside this package.
Independent scientific review remains open.
