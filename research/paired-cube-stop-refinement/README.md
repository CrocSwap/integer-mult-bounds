# A near-boundary stopping refinement of reviewed paired cubes

Prepared with substantial OpenAI Codex assistance, 9 October 2026.
Apache-2.0; all predecessor notices and credits remain applicable.

On reviewed main `d1d6c070f5a8c684727ee7ec35d930f9ebfa9758`, the same
finite construction gives the conditional witness

\[
\kappa=\frac{115286146679}{250000000000000}
      =0.000461144586716.
\]

The reviewed benchmark is `4609169/10^10 = 0.0004609169` (PR144,
integrated by PR149). The increase is exactly `56921679/250000000000000`,
approximately 0.04939865%. This is a parameter refinement of the reviewed
construction, not a new finite circuit or a practical speed measurement.
It is smaller than several **unreviewed** pending circuit results.

## Choices and reproduction

| Parameter | Reviewed main | This witness |
|---|---|---|
| Coarse bit saving | `4617656/10^10` | `115441418341/250000000000000` |
| Atom exponent theta | `1/1000` | `230785143998139/500000000000000000` |
| Complex saving | `4856569/10^10` | same |
| Complex stopping beta | `1/10^6` | same |
| Assembly eta | `1/10^8` | `1/10^14` |
| Final kappa | `4609169/10^10` | `115286146679/250000000000000` |

Run from the repository root, with Python 3.11+ and assertions enabled:

```sh
make paired-cube-verify
python3 -B research/paired-cube-stop-refinement/verify.py --check research/paired-cube-stop-refinement/certificate.json
# Regenerate deterministically:
python3 -B research/paired-cube-stop-refinement/verify.py --output /tmp/stop-refinement.json
cmp /tmp/stop-refinement.json research/paired-cube-stop-refinement/certificate.json
make verify
```

The new entry point first reproduces the complete selected main certificate,
including its source-bound bit reconstruction. The existing selected target
also independently rebuilds the signed complex producer and checks its actual
frames. The new files do not alter the historical certificate or source pins.
`certificate.json` binds all inherited certificate sources, the independent
enclosure implementation, this verifier and this written argument by SHA-256.
It records both complete suppliers, the full finite bridge, all 47 strict
downstream constraints and all seven final margins.

## The stopping argument, with every term retained

Let A be the coarse bit saving and L the inherited ordinary-leaf saving,
`L=384599/10^10`. The written uniform stopped recurrence in
`notes/three-stage-cover-bit.tex` and its restored-row wrapper in
`notes/three-stage-cover-rows.tex` establish, for every fixed atom exponent
`0<theta<1`, `w=ceil(e^theta)` and logical volume V, the bound

\[
O\left(V\left[e^{1-\theta}
+e^{(1-\theta)(1-A)+\theta(1-L)}+e^\theta\log e\right]\right).
\]

The first term pays all linear atom adapters and remainder peeling through
the contracting rank moment. The second pays the stopped weighted leaves.
The third pays the entire internally borrowed selector stock and its
restoration. The two ordinary-wrapper calls multiply only the overall
constant; they do not multiply the recursive characteristic. The old leaf
algorithm remains the source of the width-w interchanges.

Put `a=(1-theta)A+theta L`. The sufficient strict conditions remain
`a<theta<1-a`. No cost or assumption is removed. Since A>L, a decreases
strictly with theta. Algebra gives

\[
 a<\theta\quad\Longleftrightarrow\quad
 \theta>\theta_*:=\frac{A}{1+A-L}.
\]

We choose the first rational on the `10^-18` grid strictly above theta_*.
The certificate verifies its exact value and that the immediately preceding
grid point violates the strict condition. The two strict toll gaps are
reported exactly. The adapter cost therefore remains strictly lower order,
and `theta<1-a` absorbs the logarithm in the restoration term. The selected
effective saving is exactly

\[
a=\frac{57696285999534736416907057601}
        {125000000000000000000000000000000}.
\]

Changing theta affects only asymptotic constants and eventual thresholds in
the proof: `log S=O(w log e)` still holds, `w log e=o(e)`, ancestor descriptor
cost `e^{O(1)}` is still `w^{O(1)}` for fixed positive theta, and the complete
`q^w` fibers absorb that polynomial preparation. The low-type number of
tapes and the fresh-selector restrictions remain identical. Binary-range
padding has the same fixed `q^2` volume factor. The old ordinary supplier's
row reserve remains charged. No dense chart transformation is added.

## A rigorous finer coarse saving

The bit profile is exactly the reviewed `m=69`, `W=32408` profile with
rank mass `2234128`, deficit `2024` and largest child `66`. Its actual gauge
selection, dirty-read itinerary and physical frames are unchanged. Let n_r
be its complete child multiplicities and E their sum. The certified moment is

\[
\mu(A)=\sum_r\frac{n_r r}{69W}\exp(A\log(69/r))
+10^{-16}\frac{32\cdot69^2 E}{69W}\exp(A\log69).
\]

The second term adds the **entire** fallback for every edge; no displaced
good contribution is subtracted. The prime bound `2*69^3/2^80<10^-16`
and the contaminated rank-mass contraction are rechecked.

The existing independent maintainer enclosure in
`scripts/audit_community_candidate.py` supplies two-sided bounds without
using the selected producer's logarithm/exponential implementation. For
`1<=x<=2` and `z=(x-1)/(x+1)`, it uses

\[
L_x=2\sum_{j=0}^{79}\frac{z^{2j+1}}{2j+1},\qquad
L_x\le\log x\le L_x+\frac{2z^{161}}{161(1-z^2)}.
\]

The remainder bound follows by bounding all omitted denominators below
by 161 and summing the geometric series. Reducing `x` by exact powers of
two combines these bounds with the bound for log 2. Rounding lower bounds
down and upper bounds up to `10^-30` preserves the inequalities.
For `0<=u<1`, the exponential bounds are

\[
P_{12}(u)\le e^u\le
P_{12}(u)+\frac{u^{13}}{13!}\frac{1}{1-u/14}.
\]

Here `P_12` is the Taylor polynomial through degree 12. Every successive
tail-term ratio is at most u/14; summing that geometric majorant proves the
upper bound. All evaluated u are nonnegative and below one. Summation with
positive rational coefficients yields an enclosure of the displayed
conservative moment, including its deliberately overcharged fallback.

At the selected A the upper bound is strictly below one. At `A+10^-15`
the **lower** bound is strictly above one. Thus the latter is a mathematical
negative control, not merely failure of a conservative checker. Strict
monotonicity of this moment follows because every child ratio is below
one and all coefficients are positive. The unchanged complex moment is
also independently enclosed below one at its original saving.

## Downstream substitution and a scoped ceiling

Retain complex stopping beta=`10^-6` and all finite bridge integers. The
literal dirty-response charge, full orthogonal-group cardinality and
permutation charge, guard constants, denominator-three precision grid and
external row degree `70000` remain identical. Only the bit saving metadata
is re-instantiated. In particular `a<(1-beta)*a_c-10^-10`, so the available
complex supplier remains strictly adequate.

Instantiate the existing `structured_bulk_assembly.assembly` formula with
eta=`10^-14`:

\[
q=a(1-2\eta),\quad c=q(1+\eta),\quad
\epsilon=\frac{1-\eta}{1+c+q},\quad
g=\epsilon q,\quad r=(g+1-\epsilon)/2,\quad\delta=\eta/8.
\]

Every defining parameter remains a fixed positive rational. The exact
lambda, precision, reservation, analytic band and exposure inequalities
are all included in the same 47 strictly positive constraints. In
particular the tiny lambda and reservation slacks are evaluated as exact
fractions, never floating-point comparisons. The seven costs have minimum
g, and the prefix saving is exactly g+eta. All seven strictly exceed the
displayed kappa, so their fixed logarithmic overheads are absorbed. The
next `10^-15` headline grid point fails the assembly. Setting eta to zero
fails the strict lambda/reservation constraints and is explicitly rejected.

There is a useful *scoped* upper bound. Under the strict toll and this
assembly family, `a<A/(1+A-L)` and `g<a/(1+2a)`. The latter follows from
`q<a` and
`(1-eta)/(1+2q+eta q)<1/(1+2q)`, followed by monotonicity of
`x/(1+2x)`. Since this conservative moment's root is below `A_next=A+10^-15`,

\[
\sup\kappa<\frac{A_{\rm next}}{1+3A_{\rm next}-L}.
\]

The certificate proves that this ceiling is less than `2*10^-15` above
our kappa. This only limits the fixed reviewed contaminated profile,
strict toll, fixed leaf supplier and retained assembly family. It does
not limit other constructions, other fallback estimates or other proofs.

## Other candidates and attribution

The reviewed complex saving has slack; tightening its stopping beta alone
does not affect the bit-limited headline. Retaining the old atom exponent
limits improvements to the small coarse/assembly enclosure slack. The
stopping refinement is the tractable improvement on the reviewed finite
construction.

Gauge re-selection and terminal-role elimination could improve the bit
profile, but the finite frames and dirty chronology must be reconstructed:
rank histograms alone do not prove a compatible word. Those are already
the subjects of pending PR146 and PR147. Paired bit producers and alternative
modules in PR152, PR157, PR168 and successors claim larger bounds, but require
new scalar/frame certificates and dependency review. They are not imported
or independently validated here. We make no claim to exceed that queue.

Credits: icekylinx's PR144/130/115/104 construction and integration;
an664's PR128 completed-core sharing; eumemic's PR117 producer; Zhihao
Chen's PR97 physical word and Swapnil Jain's underlying witness; PR23 and
RaD's attributed semantic/bulk machinery; the original OpenAI #109 framework
and its analytic predecessors. Their source-specific licenses and AI
disclosures remain unchanged.

The toll optimization follows the principle already explored by Rohan Gupta
(`gupt1156`) in [PR148](https://github.com/CrocSwap/integer-mult-bounds/pull/148),
head `975c3cf5d4ee0c90d5a76500d431bfc59102bb72`, and the strict-boundary
instantiation by Abhinav Ramachandran in
[PR158](https://github.com/CrocSwap/integer-mult-bounds/pull/158),
head `6e086603f936dbb95c6d7171132ed943cc024db9`. This contribution applies
that principle to reviewed main, refines its fully charged conservative moment
with two-sided exact enclosures, and certifies a near-ceiling witness for
this profile. It claims no priority for the optimization principle.

The whole multiplication theorem remains conditional on all retained
analytic, uniform-recursion, exact-recovery and fixed-tape interfaces.
Finite replay and rational certificates establish their stated finite and
arithmetic claims, not those all-size hypotheses. No new Lean formalization
is claimed. The argument above supplies the dependence and asymptotic cost
justification that successful numerical tests alone could not provide.
