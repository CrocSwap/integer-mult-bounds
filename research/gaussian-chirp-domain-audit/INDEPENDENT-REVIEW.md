# Independent source and arithmetic review

Reviewed on base `66849e1475c930fd7732b1a0067ffee7e1e95f60`, assignment
seed 64. This review covers the generated Gaussian chirp domain, integer
window containment and the two displayed working-precision budgets. It does
not certify the analytic or tape-complexity theorem and claims no new kappa.

## Source composition resolves the apparent domain mismatch

The unmodified header in
[`upstream/build/sections/07-resampling.tex`, lines 53–59](../../upstream/build/sections/07-resampling.tex#L53-L59)
has the older condition `theta > p/alpha^4`. Reading that header together
with the new chirp note would indeed leave the latter's upper bound on theta
unexplained. They are not the composed manuscript.

[`scripts/make_fast_gaussian_patch.py`, lines 23–33](../../scripts/make_fast_gaussian_patch.py#L23-L33)
replaces that condition by `alpha^-2 <= theta <= 1/4`, while retaining integer
`p > 100`, integer `2 <= alpha < sqrt(p)`, coprime integer `2 <= s < t < 2^p`,
and `sigma = t/s = 1+theta`. The chirp note is inserted by the same function
at line 160; dispatch occurs at lines 300–312. Calling `patched_files()` on
the exact base produced these conditions at generated
`build/sections/07-resampling.tex:59–65`, and the chirp lemma refers back to
them at generated lines 392–400. Thus `sigma <= 5/4 < 2` is available.

The generated assembly also supplies this domain: source
[`scripts/make_fast_gaussian_patch.py`, lines 232–263](../../scripts/make_fast_gaussian_patch.py#L232-L263),
generated `build/sections/08-assembly.tex:105–115,160–174`, gives
`alpha=floor(sqrt(b/(8d)))`, `eta=1/(4d)`,
`eta < theta_i < 1/(2d-1) <= 1/4` for `d>=3`, and
`alpha^2 theta_i > b/(64d^2) >= 1` eventually. This verifies the particular
domain transfer; it does not independently prove the prime-existence or
asymptotic setup claims used by that assembly.

PR [#371](https://github.com/CrocSwap/integer-mult-bounds/pull/371), immutable
head `988ef67986c313445936fc7103908b6163b9d47e`, correctly keeps its rounding
correction conditional on the other proof obligations. The fetched historical
head's generator and upstream section 07 were compared with this audit's
base and match byte for byte; the generator SHA-256 is
`ce2013dc3a674b920ddacf25fd17329b262885af0a19279e084238318dff4760`.
The note differs only by the proposed correction. Therefore the PR body's
additional assertion that the referenced no-sort header is broader does
**not** describe either its own composed construction or the construction at
this audit's base. It reads the unmodified header without its replacement.

## Universal arithmetic checks

The following arguments use every integer `p>=101` and every integer
`2<=alpha<sqrt(p)`, with `alpha^-2<=theta<=1/4`. They are written arithmetic
arguments, not a formalization. The one-block error enclosure itself is an
inherited premise, not re-proved here.

- **Output and input windows.** In the S' block, put
  `c=floor(k0/sigma)` and `j0=c-m`, where `m=ceil(sqrt(p))*alpha`.
  For `0<=b<m`, every integer `j` with `|j-(k0+b)/sigma|<m` lies strictly
  between `j0` and `j0+3m`; hence it is included in the `3m+3` input records.
  In the E block, an output `ell=ell0+r`, `0<=r<m`, uses every required
  `ell+h`, `|h|<=m`, inside `[ell0-m,ell0+2m]`, the `3m+1` input records.
  For the selected outputs, monotonic nearest-integer rounding gives
  `0<=q_(ell0+r)-q_ell0<=ceil(sigma*r)<=2r<=2m-2`;
  this fits the `2m+2` correlation outputs. These are integer containments,
  not a numerical Gaussian-tail test. See the
  [note, lines 160–169 and 190–216](../../notes/fast-gaussian-resampling.tex#L160-L216).

- **Exponential growth enclosures.** The elementary bounds `pi<22/7` and
  `ln(2)>2*(1/3+1/81)=56/81` imply `pi/ln(2)<891/196`.
  Consequently `(891/196)*(121/400)<7/5`,
  `(891/196)*(25/4)<29`, and `(891/196)/4<57/50`.
  These respectively justify the displayed S' `Gamma=ceil(1.4p)`,
  E `Gamma=29p`, and E input scale `B=ceil(1.14 alpha^2)` from the
  exponents in the [note, lines 170–205](../../notes/fast-gaussian-resampling.tex#L170-L205).
  The S' step uses `sqrt(p)+1 < 1.1 sqrt(p)` for `p>100`; the E step uses
  `alpha*(2m+2)<=sqrt(p)+4alpha<5sqrt(p)`. Both Gammas satisfy `Gamma<=2P`.

- **S' precision.** `L_A=3 alpha ceil(sqrt(p))+3 < 4p` for `p>=101`.
  For each `p=101,102,103,104`, `4p<=2^(floor(p/4)-1)`. Increasing p by
  four doubles the right side and adds only 16 to the left, proving the
  same inequality in all four residue classes. Thus
  `ceil(log2 L_A)<=p/4`, and the block requirement is at most
  `p+(7p/5+1)+p/4+11=(53/20)p+12<3p`.

- **E precision.** `m=ceil(sqrt(p)/(2alpha))<=sqrt(p)/4+1` implies
  `L_A=3m+1<=3sqrt(p)/4+4<=p`.
  Hence `ceil(log2 L_A)<=p-1`. Because B is an integer,
  `ceil(log2(F L_A))=B+ceil(log2 L_A)` for `F=2^B`.
  Using `B<=1.14p+1` gives the source's bound
  `p+29p+(1.14p+1)+(p-1)+11=32.14p+11<34p`.
  The weaker printed bound `F<=2^(1.15p)` alone would instead give
  `32.15p+10`; that also suffices, but is not the derivation of `32.14p+11`.
  See the [note, lines 197–213](../../notes/fast-gaussian-resampling.tex#L197-L213).

- **PR #371's corrected final extraction.** Conditional on its internal
  enclosure `h/4`, the exact normalization by `2alpha>=4` leaves at most
  `h/16`, and precision-`3p` rational division adds less than
  `sqrt(2)*2^(-3p)`. Their sum is below `h/4` for `p>=101`.
  Since `sqrt(2)<3/2`, the complete displayed budgets are strictly below
  `(1+1/4+3/2)h<3h` for S' and `(3+1/4+3/2)h<5h<(p/3)h` for E.
  This corroborates the propagation of the predecessor correction; its
  original final-grid counterexample is not a new finding of this audit.

## Independent calculation and limits

A separate Python standard-library calculation, without importing the
production numerical verifier, checked all 168,093 pairs
`101<=p<=4096`, `2<=alpha<=floor(sqrt(p-1))`. Integer square roots located
both windows; integer `bit_length` computed ceiling logarithms; rational
arithmetic checked the three exponential-growth bounds above. It checked
`L_A<4p` or `L_A<=p`, both precision requirements, `B<=1.15p`, and `m<2p`.
All passed. Minimum integer precision slack was 40 bits for S' at
`(p,alpha)=(101,8)`, and 277 bits for E at `(101,10)`. This finite replay is
supporting evidence only; the preceding arguments establish the stated
uniform arithmetic claims.

The calculation is retained in
[`independent_budget_check.py`](independent_budget_check.py), independently
implemented from the main checker. From the repository root run:

```sh
python3 -B research/gaussian-chirp-domain-audit/independent_budget_check.py
```

Expected first line:

```text
PASS_INDEPENDENT_GAUSSIAN_BUDGETS pairs=168093 controls=5
```

The following JSON line records the fixed domain, stopping rule and minimum
slacks above. Five negative controls reject `p=100`, `alpha^2=p`, the two
insufficient sufficient-precision choices `P=2p` and `P=31p`, and an E window
one integer too short at `(p,alpha)=(101,2)`. Runtime checks remain active
under `python3 -O`; the independent script imports no repository verifier.

This review has not independently re-established Gaussian tail estimates,
transcendental approximation algorithms, exact packed multiplication,
multitape movement, the full Neumann theorem, or the selected multiplication
frontier. In particular, absence of a domain mismatch does not remove the
genuine final-grid defect that PR #371 addresses.

Credit: eumemic's fast-Gaussian construction; icekylinx's shifted-input error
enclosure; Harvey and van der Hoeven's analytic interfaces; and Artus
Krohn-Grimberghe / PR #371's disclosed GPT-6 Pro and Codex rounding work.
Prepared with substantial OpenAI Codex assistance as a separate source and
arithmetic review in Effy's research sprint. No independent human peer review
or formal proof is claimed.
