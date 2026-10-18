# Selected bootstrap stock: independent audit and a factor-16 fit extension

This package independently corroborates the fourteen selected bootstrap cutoffs
and stock headrooms from [Josie Elliston's PR1965](https://github.com/CrocSwap/integer-mult-bounds/pull/1965),
then proves a small extension of its **conditional stock-fit bound**. Under the
same stock-envelope hypothesis, every recorded cutoff supports a coefficient
16 times the coefficient admitted by that proof's sufficient guard. The actual
selected coefficients remain unknown. There is no new κ, supplier adoption,
frontier change, or proof of the full multiplication theorem.

The subject is the seven native and seven conservative stages in
`research/community-frontier1094-audit/ASSEMBLY.json`, bound by
`certificates/selected-result.json` on main commit
`4d3248d6d52f8ddfe612e8508b74a36acb67fbe3`. PR1965 is pinned at
`c9819a94f9c630f8b42ff5c3027965c4ba451653`; its README and result are retained
byte for byte under `sources/pr1965/`. Its checker is neither imported nor run.

## Exact arithmetic scope

For each branch, reconstruct the selected producer's seven-step chain:

```
beta = 1/10^24
s = min(bit_lower, (1-beta)*complex_lower) - 1/10^27
a_0 = 384599/10^10
a_j = (1-s)*s + s*a_(j-1)
delta_j = min(s-a_j, 1-a_j-s, 1-a_j-s*(1-a_(j-1)), 1-s)
L_j = max(ceil(36/delta_j^2), ceil(1032/delta_j))
H_j = floor(L_j*delta_j/2) - 4
```

Use `conservative_complex_lower` for the conservative branch. The formula is
read from frozen PR1087's `code/assemble.py`, lines 205–211, inside the pinned
`upstream1087.tar.gz`; source is inspected, not executed. Integer rational
pairs, Euclidean reduction and cross multiplication reconstruct every stage.
The tests use a separately implemented `Fraction` oracle. Neither arithmetic
path calls the retained assembler or PR1965's functions. The inequalities
`2(H_j+4) <= L_j*delta_j < 2(H_j+5)` certify that H is the **largest integer
log bound admitted by this guard**. They do not characterize all possible fit
proofs.

Both branches have `H_1 = 6,562,783`. Their original guard coefficient cap is
`2^6,562,780`; the extension below admits `2^6,562,784`. At stage seven, H is
`296674203132883528250615` (native) and `296674207198239164557594`
(conservative). `RESULT.json` retains all fourteen exact values and symbolic
coefficient exponents; it never materializes these enormous powers of two.

## Conditional factor-16 fit lemma

Let `0<s<1`, `0<delta<=1-s`, `L>=3`, `L*delta^2>=36`, and
`H=floor(L*delta/2)-4`. For every width `e>=2^L`, set
`t=log2(e)`, `w=ceil(e^s)` and `k=ceil(log_q S(e,w))`, where `q>1`.
Assume, uniformly at those widths,

```
log_q S(e,w) <= sigma*w*(1+log2 e),   0 < sigma <= 2^(H+1).
```

Then `k<e/2`.

**Proof.** Put `sigma_0=2^(H-3)`. For `t>=L`, we have
`H+4<=delta*t/2` and `3*sqrt(t)<=delta*t/2`. The elementary inequality
`log2(1+t)<=3*sqrt(t)` for `t>=1` therefore gives

```
8*sigma_0*(1+t)*2^(-delta*t) <= 1/16.
```

For completeness, `ln(2)>=1/2` follows by integrating `1/x` on `[1,2]`.
Also `sqrt(t)-ln(1+t)` is positive at one and nondecreasing for `t>=1`,
because `1+t>=2*sqrt(t)`. Thus the stronger inequality
`log2(1+t)<=2*sqrt(t)` suffices for the displayed elementary bound.
Since `w<=2*e^s`, `s+delta<=1`, and `sigma<=16*sigma_0`,

```
k <= sigma*w*(1+t)+1
  <= 16*e^(s+delta)/64+1
  <= e/4+1 < e/2                 (e>=8).
```

All fourteen selected cutoffs meet the lemma's arithmetic premises. This proof
changes only a sufficient fit coefficient and leaves the recorded L values
fixed. It does not measure or derive sigma.

At `sigma=2^(H+1)`, `log2(8*sigma)=H+4` exceeds the original guard's maximum
H. Nevertheless the displayed proof still establishes fit under the envelope
hypothesis. Consequently PR1965's phrase "valid exactly when" should be read
as passing that particular sufficient guard, rather than as a necessary
condition for `k<e/2`. The restated repair lemma itself remains a sufficient
statement; this package finds no discrepancy in its fourteen headrooms.
The factor 16 is a convenient proved extension, not an optimal coefficient.

## Source boundary: the coefficient is still uncomputed

The explicit new contribution in
`five-stage-source527-banks/proof/FINITE_BIT_ACCOUNTING.md`, lines 90–95,
is `57,604*w*ceil(log2(max(2,n)))`. That source fixes its own candidate
`m=120`, `W=23,683` and uses a four-level halving bound. The selected
complex assembler prices an `m=73` supplier. A numerical increment from the
former source cannot become a selected-stage coefficient merely by citation.
The earlier `three-stage-cover-rows.tex` has a different depth statement,
`47*ceil(log2(max(2,n)))+O(1)`, and leaves the inherited reserve logarithmic.
These are distinct source statements, not a contradiction to resolve by
silently replacing a depth factor.

The reviewed PR185 proof, retained in PR387's `bootstrap-sources/`, states
that completed ordinary leaves need no **external** extra stock: their own
borrowing uses the chunks passed to them, preserves outer spectators and
restores the row coordinate. It also says the parent stock is `O(w log e)`
and explicitly declines to identify the external 252 allowance with the
leaf's actual internal reserve. Neither that text nor PR387 supplies a
numerical coefficient for the selected fourteen stages.

In particular, neither `sigma_j=sigma_0+j*57604` nor use of 252 as a selected
sigma is discharged here. An additive reserve recurrence needs an explicit
same-domain reserve bound and a selected-producer binding; completed inner
borrowing is not an external reserve multiplication. A very large arithmetic
headroom cannot replace that missing source obligation.

## Reproduction and evidence limits

```
python3 -I -B research/selected-bootstrap-stock-audit/verify.py
python3 -I -O -B research/selected-bootstrap-stock-audit/test_verify.py
python3 -B scripts/research_package.py --package research/selected-bootstrap-stock-audit
```

Use Python 3.12 for registered replay; no dependencies or network are required.
The checker binds all consumed source bytes, reproduces the fourteen stage
records and PR1965 headrooms, certifies guard maximality, and checks the
factor-16 arithmetic premises. Tests cover independent positive cases and
semantic/source/receipt corruptions, including incorrect acceptance above
the original guard and substitution of an unproved selected stock claim.
Assertions are not the acceptance gate. The stored receipt is required;
explicit regeneration writes a new external file without overwriting one.
See `VERIFY.json` for the exact registered commands. This is a finite
arithmetic and conditional proof audit, not a full cold supplier replay.
The originating task catalogue is pinned as historical provenance by the
registered metadata check; later priority edits do not alter this arithmetic.

## Open next questions

1. What explicit uniform stock envelope does the selected stopped producer
   supply at each stage? Start with its per-level divisor and depth constant,
   then account for outer borrowing and completed inner leaves at their actual
   atom widths. The missing numerical source binding blocks comparison with
   either the original or extended caps.
2. Does every other "sufficiently large width" condition in the inherited
   producer fit the same recorded cutoffs? PR1965's H2 uniform time estimate
   and inherited hosting/compiler/precision/tape assumptions remain open.
   Inventory such conditions before treating the fit lemma as adoption.
3. Should the retained proof use PR1956's carried-constant cutoffs or PR1965's
   time/space restatement? Maintainer review must choose the proof wording;
   this package changes neither source proof nor selected result.

## Credit

Josie Elliston, with Claude Code, supplied PR1956's carried-constant audit and
PR1965's time/space separation, guard, and fourteen headrooms. This package
corroborates those headrooms and derives the factor-16 extension from the slack
in that proof. Rohan Arun supplied PR387 and the selected PR1094 assembly;
Jeremy Kothe supplied its PR1087 predecessor. The retained PR185/PR384
reviewed lineage and eumemic's five-stage accounting provide the source
contracts examined here. Tekalign and Wronskode supplied earlier fixed-allowance
checks. No predecessor mathematical result is claimed as new.

Prepared for ToikY with substantial OpenAI Codex assistance, including separate
source-contract and arithmetic review. No independent human review is claimed.
Apache-2.0, following the repository license; retained predecessor files preserve
their original attribution.
