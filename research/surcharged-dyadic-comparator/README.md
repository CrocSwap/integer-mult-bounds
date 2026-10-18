# Exact dyadic root comparison with the actual bit surcharge

**Scoped arithmetic completion; no supplier or new kappa.** This package
resolves exact ties between distinct dyadic profiles while retaining the
count-dependent surcharge `lambda = 32 m^2 / 10^16`. It also orders unequal
roots with exact certificates. Counts and rank masses may differ. The result
answers PR1508's explicit surcharge-equality handoff, and does not change the
pending PR1392 implementation or its safe `UNRESOLVED` decisions.

The new point is the full surcharge contract and equality test, including
irrational common roots. The polynomial GCD and rational bisection are
standard methods, already used in PR1508's independent oracle. This is not
another fixed-score audit or a more precise evaluation of an unchanged root.
[PROOF.md](PROOF.md) proves the all-input statement; the finite census tests
implementation, not universality.

## Contract and result

Let `m=2^k>=2`, `W>0` be integers and let `n_r` be nonnegative integer counts
at ranks `r=1,2,4,...,m`, with positive total count `N`. Define

```
F_n(a) = sum_r n_r r^(1-a) + lambda N - W m^(1-a).
P_n(t) = sum_(j=0)^k n_(2^j) 2^j t^(k-j) + lambda N t^k - mW,
t = 2^a,                 P_n(2^a) = 2^(ka) F_n(a).
```

Require `P_n(1)<0`. This yields a unique positive root `t_n>1`, hence a
unique positive saving `a_n=log2(t_n)`. Profiles compared together have the
same m and W. There is no equal-count, equal-mass, small-exponent or proper-rank
restriction on the new arithmetic theorem. Unsupported non-dyadic ranks,
noninteger counts/stock and nonpositive-root cases reject explicitly.

For `g = monic gcd(P_A,P_B)`, the exact equality criterion is **`g(1)<0`**.
A nonconstant gcd alone is insufficient: it may contain only a shared
negative root. If `g(1)>0`, exact rational root brackets eventually separate.
The default comparator terminates; an optional finite refinement budget can
instead return `UNRESOLVED`, with no equality claim. The sign returned is
`sign(a_A-a_B)`, so +1 means A has the larger saving.

Equality certificates contain a common factor and two quotient polynomials;
strict-order certificates contain disjoint rational enclosures. The separate
[independent.py](independent.py) imports neither the compiler nor the GCD:
it checks factor identities by k+1 evaluations of the direct source residual,
or checks both endpoint signs and strict separation. This validates decisions
without trusting the primary polynomial construction or equality algorithm.

## Source execution and evidence

The original PR1392 `pricing.py` is pinned at
`bedd71af790bb151590be45599cb5bafe89d9723`. Its `signed_price` retains exactly
the fee above and supports m=64. The unchanged routine is actually executed,
with its assertions enabled, on two constructed ties at m=64:
`t=1025/1024` and `t=sqrt(1025/1024)`. Their counts differ; both exponents
lie strictly in its supported `(0,1/10)` range. Original certified signed
intervals contain zero, while the new algebraic certificates prove equality.
The quadratic tie is beyond the linear-common-factor shortcut of PR1508's
old independent oracle: its 512-step fallback remains unresolved. Supplying
these new polynomials to that utility is outside PR1508's advertised
unsurcharged profile contract, so this is a coverage demonstration, not a bug.

We execute PR1392's signed arithmetic, **not** its full fixed PR589
`ReferencePricer` pipeline. These large integer profiles are arithmetic
fixtures, not realizable circuits or profiles with the fixed W=28416 and
idle rank42. The selected non-dyadic spectrum is deliberately outside the
new comparator's domain. No production integration is claimed.

[RESULT.json](RESULT.json) records six named fixtures, all **9,669** unordered
pairs with repetition among the valid m=8 profiles with W=1..5 and each
count in 0..2, reverse-order checks, source-probe enclosures and **16**
semantic rejection controls. The fixtures include a negative-only common
factor, a constant-gcd pair requiring over 512 refinements, full-rank calls
with dropped zero terms, and PR1508's old unsurcharged tie broken by the fee.
Controls reject changed quotients, reversed order and the three tempting
substitutions: omit the fee, charge rank mass instead of count, or replace
m squared by m. No floating-point acceptance decision is used.

Source SHA256 and Git blobs are checked **before** predecessor code executes.
[SOURCES.json](SOURCES.json) pins main inputs; [VENDOR.json](VENDOR.json) pins
the exact small PR1392 executable dependency slice and its notices. The
standalone verifier works from a Git-free source export with those declared
inputs. The registered wrapper also checks historical Git provenance.

## Reproduce and limits

From the repository root, using standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/surcharged-dyadic-comparator
python3.12 -I -O -B research/surcharged-dyadic-comparator/verify.py
```

Expected scientific marker:
`PASS_SURCHARGED_DYADIC_COMPARATOR pairs 9669 controls 16`.
The committed receipt is fully recomputed and compared with typed canonical
JSON. `--write` is only for initial receipt creation and refuses overwrite.

There is no runtime complexity bound on polynomial GCD or separation, no
arbitrary-rank comparator, and no claim that the fee is a complete physical
invoice. Circuit realization, ownership, restoration, precision/tape,
whole-call hosting and bit H1-H5 obligations remain unrun and inherited.
The selected certificate, supplier and conditional kappa are unchanged.

## Open next questions

Can a production reference-root caller expose an optional exact dyadic branch
while retaining safe interval fallback for non-dyadic spectra? This would
make equality useful in optimization. First identify a real caller whose
entire reference and candidate profiles satisfy this domain, preserve its
replication/idle normalization, and replay its full invoice. The current
fixed rank42 idle profile blocks directly installing this package in PR1392.
The structured question and screened overlap are in [TASK.json](TASK.json).

## Credit

Prepared by ywz65 with substantial OpenAI Codex assistance in derivation,
implementation, execution and writing; separate AI review is recorded in
TASK.json and is not independent human review. Hanson Sun (@bbMisk) supplied
PR1508's unsurcharged comparator, GCD oracle and explicit surcharge handoff.
Brian Ross supplied PR1392's retained-fee reference comparator. flemhhh
supplied the original PR1048 interval routines; woklerx supplied PR1182's
endpoint repair, and Douglas Colkitt supplied the retained fixed-exponent
counterexample. Existing construction credit and source-specific notices
remain with their authors; see [NOTICE.md](NOTICE.md). New work is Apache-2.0.
