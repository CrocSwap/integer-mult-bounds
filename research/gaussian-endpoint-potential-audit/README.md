# Gaussian correction powers: keep the endpoint squares together

**Research audit / analytic refinement; no new kappa.** The existing
`lem:correction-powers` in `notes/fast-gaussian-resampling.tex` is valid but
separately bounds two correlated endpoint terms. Keeping them together gives

\[
 \|E^n\|_\infty\le
 \exp\left(\frac{\pi\alpha^2}{\theta}
                \frac{\lfloor s/2\rfloor^2}{s^2}\right)
 \left(\sum_{h\ne0}e^{-\pi\alpha^2\sigma h^2}\right)^n
 <\exp\left(\frac{\pi\alpha^2}{\theta}
                \frac{\lfloor s/2\rfloor^2}{s^2}\right)
 (2.01e^{-\pi\alpha^2\sigma})^n.
\]

Here `2 <= s < t` are coprime integers, `sigma=t/s`, `theta=sigma-1`,
`alpha >= 2`, and `n >= 1`. The old exponential prefactor uses
`1/(4 theta) + 1/2`; the new one uses at most `1/(4 theta)`, and less
when `s` is odd. This is a deduction from eumemic's existing potential,
not a new Gaussian algorithm. There is no contradiction to the old bound.
No optimality of the new prefactor or truncation count is claimed.

## Precise object and proof

Use the correction operator from the pinned note, on `s`-periodic vectors:

\[
 (Eu)_j=\sum_{h\in\mathbb Z\setminus\{0\}}
 e^{-A X_{j,h}}u_{j+h},\quad
 A=\pi\alpha^2,\quad
 X_{j,h}=(\sigma h+\beta_j)^2-\beta_{j+h}^2,
\]

where `q_j=floor(tj/s+1/2)` and `beta_j=tj/s-q_j` for every integer `j`.
Thus `-1/2 <= beta_j < 1/2`; ties round upward. In particular **nonzero
multiples of s remain in the sum**, even though they address the same
coordinate. Periodicity is not a reason to discard them.

Put `y=beta_j+theta h` and `w=q_(j+h)-q_j-h`. Then `w` is integral and
`beta_(j+h)=y-w`. Direct expansion gives the sharper one-step identity

\[
 X_{j,h}=\sigma h^2+
 \frac{\beta_{j+h}^2-\beta_j^2}{\theta}
 +\frac{\sigma}{\theta}w(2y-w).                 \tag{1}
\]

The last term is nonnegative: writing `z=y-w` gives
`w(2y-w)=w^2+2wz >= w^2-|w| >= 0`. This uses only `theta>0`,
not `theta<1`. Equivalently, in the predecessor's proof combine
`Phi(end)-Phi(start)` with `beta_start^2-beta_end^2` **before** bounding
them: since `sigma/theta-1=1/theta`, their sum is exactly the middle
term in (1).

For a path `j_i=j_(i-1)+h_i`, sum (1):

\[
 \sum_i X_{j_{i-1},h_i}\ge
 \sigma\sum_i h_i^2+
 (\beta_{j_n}^2-\beta_{j_0}^2)/\theta.        \tag{2}
\]

This holds for every finite path of nonzero integer increments, including
negative increments, repeated coordinates and arbitrary winding. Coprimality
implies the residues `tj mod s` visit every residue. Hence

\[
 \min_j\beta_j^2=0,\qquad
 \max_j\beta_j^2=\lfloor s/2\rfloor^2/s^2=:b_s^2.
\]

Apply (2) to every term in the path expansion of `E^n`. The positive
Gaussian sums converge absolutely (quadratic decay in each increment), so
Tonelli permits summing the inequalities. The sum of the majorants factors
into the nth power of the one-dimensional Gaussian sum. Every row sum is
bounded by `exp(A beta_j^2/theta)` times that power; taking the maximum
proves the first displayed bound. Equivalently, conjugation by
`D_jj=exp(A beta_j^2/theta)` makes every row sum of `D^-1 E D` at most
the Gaussian sum. No diagonalization or eigenvalue assumption is used.

For `a=A sigma>4 pi>12`, the inequality `h^2 >= 1+3(h-1)` for `h>=1`
gives

\[
 \sum_{h\ne0}e^{-a h^2}\le 2e^{-a}/(1-e^{-3a})<2.01e^{-a}.
\]

For the last strict comparison it suffices that `e>2` and `a>12`, so
`e^-3a < 4096^-3`; the remaining comparison is rational and checked.

## Certified counts and what they do not mean

Let `L=(333/106)/(6932/10000)` and `U=(355/113)/(693/1000)`.
Then `L < pi/log(2) < U`, and `log2(2.01)<101/100`. Define

\[
 d=L\alpha^2\sigma-101/100>0,\qquad
 B=U\alpha^2 b_s^2/\theta,\qquad
 n_p=\left\lceil(p+B)/d\right\rceil.
\]

The bound above implies **`||E^n_p|| < 2^-p`**. The verifier encloses
pi by Machin's identity with alternating rational arctangent sums and
log(2) by the positive series `2 atanh(1/3)`, including its tail. It
does not use floating-point evaluations of a logarithm or exponential.

For the inverse partial sum `S_n=sum_{k=0}^{n-1}(-E)^k`,
`(I+E)S_n=I-(-E)^n`. Thus `n_p` certifies its **residual**, not by
itself the same absolute inverse error. If the separately established
`||E||<1/2` holds, then

\[
 \|(I+E)^{-1}-S_n\|\le2\|E^n\|.
\]

Use `n_(p+1)` to certify inverse error below `2^-p`. We retain this
extra bit explicitly. Neither bound prices rounded evaluations of `E`,
storage, setup, source access, restoration or tape movement. No modified
resampling implementation, end-to-end running time or multiplication
exponent is claimed. The algebraic operator bound holds for all `theta>0`;
it does **not** enlarge the implemented chirp domain.

`RESULT.json` separates three counts: the original corollary's simplified
count, the old endpoint bound priced with the **same** rational decay `d`,
and the new endpoint bound. Only the last comparison isolates the gain
from this contribution. The original count is compared only within its
stated `alpha^2 theta>=1, theta<1` domain.

Exact examples from the receipt:

| p | alpha | s,t | Old endpoint, same decay | New residual | New inverse, if norm < 1/2 |
|---:|---:|---|---:|---:|---:|
| 128 | 4 | 15,16 | 6 | 5 | 5 |
| 1024 | 8 | 63,64 | 20 | 19 | 19 |
| 4096 | 16 | 255,256 | 68 | 67 | 67 |

## Counterexamples and finite evidence

The prefactor cannot simply be deleted. At `s=4,t=5,j=2,h=1`, (1) has
`X=1/2`, `sigma h^2=5/4`, endpoint contribution `-3/4`, and zero
remainder. At `alpha=2`, this one positive term in row 2 of E exceeds
`2.01 exp(-A sigma)`, because `exp(3A/4)>exp(9)>2.01`.
This also refutes the claimed prefactor-free operator bound, not merely
one intermediate inequality. The tuple has `theta=1/4` and
`alpha^2 theta=1`, inside the implemented Gaussian parameter restriction.

The residual/inverse distinction has a separate scalar counterexample:
`E=-1/4`, `n=2`, gives residual `1/16` but inverse error `1/12`.
It refutes the general inference from residual alone; this signed scalar
is not asserted to be one of the positive Gaussian matrices.

The finite audit enumerates all coprime `2<=s<=32, s<t<=3s`, all starting
residues and nonzero steps in `[-4,4]`. A second path calculation uses only
integer phase numerators and cross multiplication; it imports no predecessor
routine and does not call the rational step identity. All increment words
over `{-2,-1,1,2}` of lengths 1 through 4 are checked for six listed pairs,
with 620 supplemental seed-62 paths of lengths up to 16. The finite count
screen uses `p in {101,128,256,1024}`, integer `2<=alpha<=16`,
`alpha^2<p`, and `alpha^-2<=theta<=1/4` on those coprime pairs.
This fixed coverage is the stopping rule; it is not an exhaustive search
over all Gaussian parameters. Universal claims rest on the proof above.

## Reproduction, scope and credit

From the repository root, Python 3.10+ with the standard library:

```sh
python -B research/gaussian-endpoint-potential-audit/verify.py
python -B -m unittest discover -s research/gaussian-endpoint-potential-audit -p test_verify.py -v
```

The first command must print `PASS_GAUSSIAN_ENDPOINT_POTENTIAL` and match
every field and JSON type of `RESULT.json`. Source drift fails before
arithmetic. `--write NEW_PATH` creates a fresh receipt without overwriting
an existing file. `SOURCES.json` pins the exact base, SHA256 and Git blob
identities of all four inputs. `CLAIM.md` records the seed, alternatives,
bounded overlap search and result. `VALIDATION.md` records executed checks.

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. Selected conditional
kappa: `1661634653669567/10^18`, unchanged. The selected PR799 construction,
PR589 bit supplier and their all-size/compiler, common-label/mutable-source,
hosting, precision/tape and analytic obligations are not independently
replayed or discharged here. No formal proof-assistant result is claimed.

Credit eumemic's PR5 (`d3d370c34937503bd3fa63c83d505a05e8e50893`) for the
correction operator and potential argument, icekylinx for the retained
shifted chirp error enclosure, and Harvey and van der Hoeven for the
underlying Gaussian resampling algorithms. The exact audited derivative
is the base's note, rather than an assertion that PR5 bytes are unchanged.
Effy Elden's concurrent PR684 identifies the implemented Gaussian domain
and audits windows/precision; it explicitly leaves Neumann evaluation
outside its scope. Its PR description informed this scope comparison;
no pending-PR source or certificate is imported. Packed-repair audits
PR735/763/773 and signed-packing audits PR690/693 motivated choosing a
different obligation. See the repository's existing NOTICE and LICENSE.

The base ledger marks PR5 partially reviewed and PR371's separate
final-grid-rounding proposal unreviewed. This package does not change
either disposition or audit the rounded chirp implementation.

Prepared for **Alan Grillo (@bg-grillo-alan)**, with substantial **OpenAI Codex assistance**
in the derivation, code, verification and writing. One AI agent; no
independent human review is claimed. New material is Apache-2.0.
