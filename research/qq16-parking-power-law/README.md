# A critical-exponent law for QQ16's parked current-bank volume

This contribution is produced by Nick Petalas. Apache-2.0.

**Claim type: scoped recurrence proof with exact finite corroboration.**
For the original selected-C child backend retained inside the QQ16 caller,
assume the published tree and volume premises of Brian's
[PR #4753](https://github.com/CrocSwap/integer-mult-bounds/pull/4753), head
`44e2c79344e0090d4e829e0dde4f533d8d0273ec`. The volume-weighted current-bank
parking subtrace has a two-sided power law at its exact critical exponent.
The bounds below hold for every integer width `w >= 356` in the stated
recurrence, with no extra logarithmic factor:

```text
       ((w + 3456/25) / (355 + 3456/25))^s - 1
H(w) >= ------------------------------------------------,
                         248163/7168

       (w/4)^s - 1
H(w) <= ----------------,
          248163/7168

0.9983245373 < s < 0.9983245374.
```

Thus `H(w) = Theta(w^s)` for this fixed-cutoff recurrence, and no smaller
power gives an asymptotic upper bound. The exponent is the root of the
**already existing supplier moment**. More digits of that root are not the
new result. The new result is the quantified two-sided parked-volume bound,
including its endpoint exponent, floor correction and finite cutoff.
No literature-priority claim is made for the weighted-tree argument.

## Premises and the exact quantity being bounded

The live input is the published, hash-bound `RESULT.json` from #4753. Its
histogram, global cutoff and physical interpretation are cited premises.
This package does not rerun its census or audit its sources. The proof also
uses #4753's written fresh-row/full-spectator-volume argument.

In the historical descriptor family `p=2^8500`, the unchanged global height
makes a call terminal exactly when its integer width is below 356. At every
nonterminal selected-C node, with `q=floor(w/73)`, the selected children have
width `r q`, multiplicity `n_r Gamma`, and full physical bank volume
`v/(14336 Gamma)` when the parent's bank volume is `v`. The inherited list is:

```text
r       1       2      3      4      5    7     8     48
n_r  349604   60192  62585  20448  11808   7   1152   4866
```

The source tests its global cutoff before removing the remainder and does
not test again after stripping it. In particular a fresh width-356 call runs
its selected program at width 292. Its selected child parking is still paid.
Remainder leaves, native/Ordinary internals, other parked roles and restore
work are outside the subtrace considered here.

Put `N=sum n_r=510662`, `c_r=n_r/14336` and `C=sum c_r=255331/7168`.
The normalized internal-node mass is the unique terminating recurrence

```text
H(w) = 0,                                         0 <= w < 356,
H(w) = 1 + sum_r c_r H(r floor(w/73)),             w >= 356.
```

For one complete original C8 call of width `w` and input-bank bit length `v`,
let `P(w,v)` sum the current-bank bit length once per selected-child parking
pair, across the complete selected-C descendant tree. Then exactly

```text
P(w,v) = N Gamma v H(w).
```

To prove this identity, group internal nodes by rank path. At depth `j` their
multiplicity contains `Gamma^j`, and each current bank has volume
`v/(14336 Gamma)^j`. These factors of Gamma cancel. Each such node parks its
whole current bank once for each of its `N Gamma` selected children.
The normalized path weight is consequently `prod(n_r/14336)`.
Counting calls without dividing descendant volume gives a different quantity.

For the sixteen equal-volume removed C8 calls per outer cover in #4753,
this extends its once-generation term to

```text
P_removed = 16 N Gamma^2 v H(8 lambda).
```

Under the same source assumptions, #4753's literal park-loop lower bound
therefore gives removed reads, writes and unit moves at least
`(2,5,5) P_removed`. This remains one removed expense. It does not determine
the sign of `T_D-T_B`, `T_D-T_B*` or an implemented `D*` comparison.

The abstract recurrence permits arbitrary widths. A physical application
additionally requires an admitted root, sufficient fresh-row stock for its
whole reached tree, and the inherited source, layout, precision, restoration
and native contracts. In particular the fixed physical descriptor has finite
root width. The statement `Theta(w^s)` concerns the recurrence as `w` tends
to infinity, not an assertion of unbounded admissible widths for that one
fixed RootPlan. No smaller root stock is installed.

## Proof of the critical-exponent envelope

Define

```text
M(t) = sum_r c_r (r/73)^t.
```

Every `r/73` lies strictly between zero and one. Therefore M is continuous
and strictly decreasing. The exact inequalities

```text
M(0) = 255331/7168 > 1,
M(1) = 1041408/1046528 < 1
```

give a unique `s` in `(0,1)` with `M(s)=1`. The rational interval calculation
in the verifier encloses this root as displayed above. This is a convenient
certified coordinate for the proof, not a changed supplier saving or kappa.

Expand the grouped rank tree to its terminal leaves. A rank-r edge has weight
`c_r`, and a vertex has the product of its edge weights. Let I be the sum of
internal vertex weights, including the root, and L the sum of terminal leaf
weights. Every child has width at most `48w/73`, so the tree is finite.
Each internal vertex replaces its own frontier weight by C times that weight.
Telescoping the resulting increments gives the exact identity

```text
I = H(w),                  L = 1 + (C-1) H(w).
```

For `phi(x)=x^s`, writing `w=73q+delta` gives

```text
sum_r c_r phi(r q) = (73q)^s <= w^s.
```

Apply this inequality at every internal vertex. The weighted terminal sum
of `phi` is at most `w^s`. Every terminal descendant of a nonterminal root
has width at least `floor(356/73)=4`, and at most 355. Consequently
`4^s L <= w^s`, which proves the upper bound after substituting for L.

For the reverse inequality take `b=3456/25` and `psi(x)=(x+b)^s`. For every
rank in the list and every `delta` in `{0,...,72}`,

```text
b >= r delta/(73-r),
r q + b >= (r/73)(w+b).
```

The largest allowance is exactly `48*72/(73-48)=3456/25`.
It is sharp for a uniform shift that must satisfy these individual affine
inequalities. It is not claimed to optimize every possible potential or the
constants in the final envelope. Since `s>0` and `M(s)=1`,

```text
sum_r c_r psi(r q) >= (w+b)^s.
```

The weighted terminal sum of psi is therefore at least `(w+b)^s` and at most
`(355+b)^s L`. Substituting the exact identity for L proves the lower bound.
Both bounding expressions grow as positive constants times `w^s`, completing
the two-sided asymptotic statement. Every step uses a finite tree; no exchange
of an infinite sum with a limit is needed.

## Exact verification and reproduction

From the repository root, use the interpreter available in this workspace:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/qq16-parking-power-law
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/qq16-parking-power-law/verify.py
```

For another checkout, replace that absolute interpreter path with CPython
3.12. The registered normal and optimized commands each run the standalone
standard-library verifier. It writes no files. Its JSON output is a generated
receipt containing hashes of the package files.

The verifier checks all 8,193 widths from 0 through 8,192 for the weighted
leaf identity. An independently arranged integer path census checks eleven
widths from 356 through 1,048,576, retaining level-by-level active and terminal
path multiplicities and their denominators. It compares the two methods
where their domains meet and checks both envelopes with outward rational
bounds. For example `H(584)=9601/7168`, the first extra-generation value.
These are finite corroboration of the written proof, not physical execution.

The root enclosure uses log range reduction to `[1,2]`, 48 terms of the
atanh series with its positive geometric tail, and outward rounding to
40 decimal places. It evaluates `x^s` as `x exp((1-s) log(1/x))` for `x<=1`
and by the corresponding reciprocal formula for `x>=1`. The positive exp
series through degree 12 has tail at most its first omitted term divided
by `1-y/14`. All acceptance comparisons use rational arithmetic.
Eight controls distinguish two incorrect exponent brackets, reversed
endpoints, a repeated cutoff, terminal equality, missing fresh-row volume,
ceiling instead of floor, and an insufficient affine shift.
These compare specific incorrect predictions at named boundary witnesses.

The source-binding positive control for the current selected record passed.
The card's historical `scripts/research_baseline.py` raises `KeyError:
bit_lower` against that changed record. It is not treated as scientific
verification. The current selected record remains unchanged.

## Scope, resources and remaining obligations

This is an ordinary written proof with an exact host certificate. Independent
human and formal proof-kernel review are unclaimed. No production C8 payload,
full RootLayer, native execution, complete cost comparison, supplier admission,
new kappa or selected-frontier change is established. No predecessor result
is independently validated by this package.

Power of Ten rule 3 deviation: CPython's Fraction, Counter and JSON operations
allocate dynamically. This verifier is a finite exact certificate, not a
steady-state service. The DP arrays contain 8,193 entries each; the integer
census accepts widths at most `2^20`, at most 4,096 simultaneous distinct
widths and at most 64 levels. Child widths decrease by a factor at most
48/73. Series have 48 and 12 fixed terms, arguments have explicit bounds,
and the two authenticated premise files are each capped at 1 MiB. The
finite integers and rational denominators have bounds derived from these
limits. These bounds, ordinary failure exits and warning-as-error runs are
the compensating controls. Reassess capacities and arithmetic size before
raising any limit. There are no recursive calls or proof-relevant child
processes. Functions stay below 60 lines. Static parsing and normal/optimized
warning-as-error execution are the available Python diagnostics; no new
repository-wide lint configuration is introduced.

## Open next questions

1. Bound the complete unmatched candidate nonchild and shell work at one
   admitted nonterminal geometry. The present removed-expense bound alone
   cannot settle affordability. Start by supplying an upper bound for the
   corresponding candidate terms while retaining every later root call.
   This is blocked by the existing unpriced physical operations and control.
2. Determine the necessary stock and descriptor range when applying this
   envelope to a growing family of admitted roots rather than a fixed-cutoff
   recurrence. Start with the actual RootPlan height/cutoff relation and
   source row divisions. Root admission and full physical contracts remain
   separate premises; no construction expansion is justified by this bound.

## Predecessor credit and coordination

Brian / JoyboyBrian's #4753 supplies the histogram, cutoff, full-volume
fresh-row relation, original-child-backend boundary and park-loop floor.
Chris R / Clear1nsight's #4166, #4167, #4172 and #4177 supply the installed
caller, protected returns, context cancellation and terminal-band comparison.
Jose Manuel supplies the physical C/Ordinary/Compact machinery. Preserve
ywz65, Sagar Thakrar, Tekalign, Ali Romman, Arham Tahir and the full source
lineage credited in those packages. Their census and physical claims are
premises here. #4790 composes protected returns in the installed outer caller;
it does not replace the original descendant backend bounded here.

Base main is `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
This refines the joint-query-controller card to a scoped analytic cost
obligation rather than another decoder or construction round. Entry overlap
covered 379 open PRs and 3,853 Discussion records with complete pagination.
The sparse local scan covered 115 of 6,319 tracked note paths; separate Git
searches covered distinctive terms across main READMEs/proofs. Closed-code
and unpublished-work coverage is incomplete. These searches are not a
novelty certificate.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133725).
