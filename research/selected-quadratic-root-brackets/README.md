# Quadratic screening brackets for the selected supplier roots

**Independent analytic screening, not endpoint-grid certification or a new κ.**
For the three frozen selected pricing ledgers, two rational surrogate curves
bracket the moment root more than **418×** more tightly than the gap left by
the linear `a < D/E` diagnostic. All modeled surcharges are retained as
exponential terms. No arbitrary fractional-power evaluation is used to obtain
the brackets, and no predecessor pricing function is imported.

The selected endpoint signs already have several independent full replays.
This contribution instead supplies a sharper screening implication and a
source-bound check of that implication. It does not replace those replays.

## Exact model and comparison theorem

For the normalized bill, write

```text
M(a) = sum_i c_i exp(lambda_i*a),   c_i>0, lambda_i>=0,
D    = 1-sum_i c_i > 0,
E    = sum_i c_i lambda_i > 0,
F    = sum_i c_i lambda_i^2,
L    = max_i lambda_i.
```

An ordinary rank-r child contributes `c_i=n_r*r/(m*W)` and
`lambda_i=ln(m/r)`. The modeled bad-residue surcharge contributes
`rho*m^a`, with `rho=32*m*sum_r n_r/(10^16*W)`: its weight is rho and its
logarithmic rate is ln(m). It contributes to **D, E, F and L**, not just D.
The physical derivation of this inherited surcharge remains assumed.
With no surcharge, this normalized D/E equals the repository's raw
`(mW-sum n_r r)/(sum n_r r ln(m/r))` diagnostic.

For `0<=t<3`,

```text
1+t+t^2/2 <= exp(t) <= 1+t+t^2/[2(1-t/3)].
```

The lower inequality follows from the nonnegative exponential series. For
the upper inequality, `n! >= 2*3^(n-2)` for every n>=2: equality at n=2,3,
and induction thereafter. Summing that geometric coefficient majorant gives
the rational upper expression. Applying it to every term, and using
`lambda_i<=L`, gives

```text
E*a + F*a^2/2 <= M(a)-M(0)
             <= E*a + F*a^2/[2(1-L*a/3)].
```

For certified nonnegative log intervals, let `Elo<=E<=Ehi`,
`Flo<=F<=Fhi`, and `L<=Lhi`. Define

```text
Q(a) = Elo*a + Flo*a^2/2,
U(a) = Ehi*a + Fhi*a^2/[2(1-Lhi*a/3)],
H    = D/Elo, requiring Elo>0 and Lhi*H<3.
```

Both Q and U are strictly increasing on [0,H], start at zero and reach at
least D at H. Their roots at height D are therefore bracketed there.
The true moment is strictly increasing and unbounded because some positive
weight has positive rate, so it has exactly one positive root a* at height one.
The comparison proves

```text
root(U=D) <= a* <= root(Q=D) <= H.
```

Exact rational bisection reports the **lower endpoint of the U-root bracket**
and the **upper endpoint of the Q-root bracket**. The inner endpoints would
not certify this implication. The implementation verifies the final signs
and rejects the pole/domain or an unbracketed surrogate.

## Selected evidence

Profiles are read from the selected assembly and bit `nine.profile`, not from
PR headlines. The complex profile, rank mass and deficit are cross-bound to
the retained independent owner receipt. The bit rank mass and endpoint are
also matched, and the selected surcharge flags checked. Exact live-input and
historical provenance pins are in [SOURCES.json](SOURCES.json).

The following decimals are **outward rounded** displays of the exact rational
root brackets in [RESULT.json](RESULT.json). Narrowing is
`(linear_upper-published_endpoint)/(root_upper-root_lower)`; it measures a
diagnostic uncertainty gap, not a speedup or exponent improvement.

| Model | Certified lower | Certified upper | D/E upper | Narrowing factor |
|---|---:|---:|---:|---:|
| Native complex, m=73, W=14336 | 0.00167546136793417 | 0.00167547358407120 | 0.00168059070975433 | >419 |
| Conservative complex, same profile + surcharge | 0.00167546136507270 | 0.00167547358120967 | 0.00168059070687533 | >419 |
| Bit, m=64, W=28416, surcharge | 0.00173342514312811 | 0.00173343740334675 | 0.00173855724840137 | >418 |

Every interval contains the published endpoint and its next 10^-24 grid
point. **Containment does not reprove acceptance or rejection at those points.**
The approximately 1.2e-8 surrogate gap also cannot resolve the much smaller
native/conservative correction. Finer bisection alone will not remove this
analytic approximation gap.

## Reproduce and controls

Python 3.10+, standard library only, from the repository root:

```sh
python3 -I -O -B research/selected-quadratic-root-brackets/verify.py
python3 -I -O -B research/selected-quadratic-root-brackets/test_verify.py
python3 scripts/research_package.py --package research/selected-quadratic-root-brackets --check-only
python3.12 -B scripts/research_package.py --package research/selected-quadratic-root-brackets
```

Expected verifier output:

```text
PASS_SELECTED_QUADRATIC_ROOT_BRACKETS ledgers=3 controls=12 narrowing_gt_100x surcharge_included no_new_kappa
```

The independently written logarithm primitive uses binary reduction and
72 positive atanh terms, an explicit geometric tail, and outward 160-bit
dyadic rounding. On `[1,2]`, z=(x-1)/(x+1) lies in [0,1/3]. After 72 terms,
the remaining log series is at most `2*z^145/[145*(1-z^2)]`.
The log method itself is not claimed as new or distinct from every retained
log implementation: the **moment-root enclosure** is the rational surrogate
comparison rather than another full exponential-series endpoint replay.

Twelve check groups cover log-one, a log-two decimal interval, a single
exponential root, an independent exact dyadic root, six invalid-domain or
unbracketed-root rejections, every surcharge D/E/F contribution and a fixture
where the surcharge strictly raises the maximum logarithmic rate. The
exact fixture `M(a)=2^(a-1)` has root 1; broad rational bounds
`2/3<ln(2)<7/10` give `Q(1)=4/9<1/2<U(1)=469/920`, so it checks the root
directions without evaluating fractional powers. The separate CLI tests run
under `-O` and reject altered root, surcharge and source-hash receipts with
the expected diagnostic. Default replay is read-only; `--write` explicitly
regenerates RESULT after the mathematical checks. Local registered replay
is bounded and requires no installations.

## Task and scope

Base `2de86c77b4127d2f01f504e0c7c5e4db737caa3c`; track
`independent-verification`; card `independent-moment`; catalogue scope key
`c191650c0fa8d2fa514e`; OS nonce `4fa6ddc953abae43610a0c49ace10c99`.
[TASK.json](TASK.json) records the refined three-ledger domain, stop rule,
source heads and local card. The first bounded computation succeeded; no
pivot was used. The baseline binding command passed before computation.

The entry survey and immediate concrete-object overlap refresh found the
prior linear diagnostic, its log-contract audit and existing selected
endpoint audits, not a matching quadratic screening package. This is not
proof of novelty. Claim:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18915959.
No directly matching open handoff was found; the chosen card's independent
numeric-enclosure route was retained rather than forcing an unrelated task.

No word, frame, ownership, hosting, precision/tape, all-size compiler,
analytic-transfer or bit H1-H5 obligation is rechecked. No full cold replay,
supplier adoption, selected-frontier edit or new κ is claimed. Existing
profile realization and surcharge-contract assumptions remain inherited.

## Open next questions

Can a certified surrogate reject one pinned pending changed profile before
a full moment comparison? A sharper cheap rejection screen could save
pricing work, without proving physical feasibility. A feasible first step
is one exact profile/charge model, checking D>0 and `Lhi*D/Elo<3`, then
comparing with its independent full replay. The blocker is that this package
covers only three frozen selected ledgers; pending-profile source binding,
complete invoice and actual timing benefit must be established separately.
Structured fields are in [TASK.json](TASK.json).

## Credit and license

Credit the selected construction and reviewed source lineage: Rohan Arun
(https://github.com/CrocSwap/integer-mult-bounds/pull/1094), Jeremy Kothe
(https://github.com/CrocSwap/integer-mult-bounds/pull/1087 and mutable-leaver
lineage), Hao Yan (https://github.com/CrocSwap/integer-mult-bounds/pull/858),
and DreamingOfClouds' retained bit supplier
(https://github.com/CrocSwap/integer-mult-bounds/pull/589), with eumemic and
the full predecessor credit in the selected review. Sources are untouched.
Aaron Wang / navinor's prior linear diagnostic
https://github.com/CrocSwap/integer-mult-bounds/pull/1293 motivates the
comparison; TennisBowling's https://github.com/CrocSwap/integer-mult-bounds/pull/1405
is credited for the fail-closed log-contract audit. Neither numerical routine
is imported or reused. Existing complete endpoint replays retain their credit.

Prepared by Aaron Wang / navinor, **with help from chatgpt**, including
separate read-only AI proof/code review. No independent human or
proof-assistant review is claimed. Apache-2.0.
