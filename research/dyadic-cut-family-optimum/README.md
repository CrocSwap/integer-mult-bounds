# The exact best cut in the dyadic two-parameter family

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

This scoped proof gives the unique best member of CubeJerry's
[PR #6784](https://github.com/CrocSwap/integer-mult-bounds/pull/6784)
cut family at every fixed height. It also sharpens the predecessor's
leading asymptotic to an explicit convergence rate. No new kappa is claimed.

For height `h>=2`, write `m=h-k-1` with `0<=k<=h-2`. The family reads
scratch `z_(m+1)` at completed-leaf cut `4^h-(4^k+2)/3`. Its mass `K_h(k)`
is equation (12) of the cited predecessor, treated as a mathematical input.
The new adjacent-difference identity is

```text
8 * [K_h(k)-K_h(k+1)]
    = 16*4^k - 3^k*(3*4^(h-k)-8*2^(h-k)+8).
```

After division by `3^k` this expression strictly increases and never
vanishes. The first positive value gives the unique optimum; if there
is none, use `k=h-2`. Exact integer bisection finds it using logarithmically
many comparisons in `h`.

Let `D_h=2*4^h-max_k K_h(k)`, and
`beta=4*log(2)/log(16/3)`, about `1.656289`. The new proof establishes

```text
(2^h)^beta / 6 <= D_h <= 6*(2^h)^beta.
```

The exponent is sharp inside this family. For the global formal peak,
the source's envelope consequently gives the new quantitative statement

```text
0 <= 2-E_infinity(n)/n^2 <= 6*n^(-(2-beta))
```

for every dyadic `n>=4`. No matching global deficit exponent or exact global
maximizer is asserted. [PROOF.md](PROOF.md) proves the optimizer, the bounds,
the finite exceptional heights and the stated distinction.

## Evidence and reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -X dev -W error -B research/dyadic-cut-family-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -X dev -W error -O -B research/dyadic-cut-family-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dyadic-cut-family-optimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dyadic-cut-family-optimum --check-source-history
```

An equivalent CPython 3.12 interpreter path works elsewhere. Expected markers
are `PASS_DYADIC_CUT_FAMILY_OPTIMUM`, `PASS_REGISTERED_RESEARCH_PACKAGE`, and
`PASS_RESEARCH_COMMIT_BYTES`. The verifier prints a generated receipt bound to
all eight package files and writes nothing into the checkout.

The finite arithmetic checks enumerate every family member at heights
`2..256`, check the adjacent identity and unique optimum, and check rational
rate enclosures through height 512 and at 1024, 2048 and 4096. Exact integer
powers bracket the logarithmic balance, so no floating-point decision is used.
The new `h=11` optimum is `k=8,m=2`, with mass `7,735,559`. Five wrong-decision
and formula controls and ten invalid-input rejections must pass in both modes.
These corroborate the new written proof. They do not replay predecessor
channel words or validate the predecessor's theorem.

## Source boundary, credit and limitations

The immediate mathematical input is CubeJerry's PR #6784, exact head
`c134aa6edc8ed6444bbf7bfcabbed8124ff26c39`, PROOF section 6, equations
(11), (12) and the family construction. Its unchanged proof is retained in
[predecessor-proof.md](predecessor-proof.md), including its original notice.
[PREDECESSOR.json](PREDECESSOR.json) records the public URL, head and byte
hash. No unavailable side-branch Git object is required for replay.

Retained mathematical credit goes to Chafik Boukhalfa's balanced dirty word
in #628, Philippe Van Velzen's prefix/exit and inverse lemmas in #2177,
ywz65's support recurrences in #2735, Adam Gall's endpoint channel counts in
#2067, and their credited predecessors, including woklerx, Charles Bethin,
Arham Tahir and Hanson Sun. Their transport results are cited, not audited.
The new contribution is optimization of the stated two-parameter mass and
its quantitative rate.

This is a formal free-algebra result for independent completed-leaf errors
on the unchanged balanced word. It does not prove simultaneous physical
rounding attainment, internal-leaf error behavior, non-dyadic bounds, a
complete error-budget profile, a native operator realization, precision/tape
costs or supplier admission. All five selected assumptions remain, and the
selected frontier is unchanged. No full selected replay, proof-kernel check
or independent human review is claimed.

The original `uniform-transfer-audit` card is recorded as changed scope in
[TASK.json](TASK.json). This is a side result relevant to precision envelopes,
not discharge of the selected `precision_tape` assumption.

## Related open work

- #6784 is the immediate predecessor. It gives the family and global leading
  limit; this package adds its exact finite optimizer and a quantitative rate.
- #6770 studies total mass of one interval transport row; this package sums
  distinct completed-leaf error channels and optimizes one cut family.
- #6668 attains a small-error-budget channel segment for `n=2^g-1`; it does
  not supply the total mass or optimizer studied here for `n=2^h`.

## Open next questions

1. Can another chronological cut family improve the exponent `beta` for the
   global deficit? First derive its exact independent-channel total and
   compare it to the proved `Theta(n^beta)` limit of this family. The existing
   global lower exponent `log_2(3)` does not settle this.
2. Determine exact global finite-height maxima. Start with a phase recurrence
   preserving collisions and complete profiles, then compare every phase
   with the optimized family here. A mass-only relaxation is insufficient.
