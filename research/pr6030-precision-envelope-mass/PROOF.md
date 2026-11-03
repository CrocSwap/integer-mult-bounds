# Complete-envelope exponent of the selected PR6030 review

Assumption ID: `precision_tape`. This is a scoped identity for the published
envelope. It is not a proof of that assumption.

## Data

Let `H` be `complete_cost.paid` in
`research/p104-helper470-twin-rung-removal/RESULT.json`, and let `T` be
`complete_cost.targets`. Write `R(H) = Σ r n_r` and `N(H) = Σ n_r`.

Direct evaluation gives

- `R(H) = 240152` and `N(H) = 66834`;
- `R(T) = 240912` and `N(T) = 13444`;
- `R(T) - R(H) = 760`, equal to `rank_mass_surplus`.

The same file records `nonrecursive.raw_budget = 10^9`,
`nonrecursive.raw_scalar_upper = 184647552`, and
`nonrecursive.local_paid_rank_mass = 5952`. The local mass is the
nonrecursive note's growth coefficient. It is not `R(H)`.

The application review
`docs/research/pr-intake-evidence/pr6030-audit/PROOF-REVIEW.md` states the
paid rank mass `240,152`, the productive rank mass `240,912` with surplus
`760`, the caller bound `126,626,680`, the allowance `184,647,552 < 10^9`,
and the envelope `2^(10^9+240152f)`.

## Lemma

Let a product contain elementary factors whose coordinate row-l1 majorants
are at least 1. Suppose at most `B` of them are non-Gaussian and each has
majorant at most 2, and suppose the Gaussian factors have ranks `r_i` with
`Σ r_i = R` and majorant at most `2^(r_i f)` for an integer `f ≥ 0`.

Then every subproduct has row-l1 majorant at most `2^(B + R f)`.

Proof. Pass to base-2 logarithms of the majorants. Each logarithm is a
nonnegative integer, the non-Gaussian logarithms sum to at most `B`, and the
Gaussian logarithms sum to at most `R f`. The logarithm of a subproduct is
at most the sum of the logarithms of its factors, hence at most the sum of
every logarithm. Nonnegativity is necessary: majorants `2` and `1/2` have
logarithms `1` and `-1`, the full sum is `0`, and the first factor alone
has logarithm `1`.

## Application to the published sentence

Take `B = 10^9` and `R = R(H) = 240152`. The lemma's conclusion is exactly
the published envelope `2^(10^9+240152f)`.

The review also states a caller bound `C = 126626680` and an allowance
`A = 184647552`, with `C < A < 10^9`. The differences are

- `10^9 - C = 873373320`;
- `10^9 - A = 815352448`.

Under the same majorant hypotheses with `B = C` instead of `B = 10^9`, the
lemma would give `2^(126626680+240152f)`, smaller than the published
envelope by exactly `2^873373320`, for every `f`. The review states `C` and
still writes the budget exponent. This note does not replace `10^9` by `C`.

## Not established

The lemma's majorant hypotheses are not proved for the selected caller.
`RESULT.json` does not count non-Gaussian factors. The review's next
sentences keep COPY residuals and the owned-erasure premise outside this
exponent. Nothing here discharges `precision_tape`, `native_all_columns`,
`owned_erasure`, `compiler`, or `analytic_recovery`, and κ is unchanged.
