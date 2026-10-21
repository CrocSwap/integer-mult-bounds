# Nonconsecutive commuting C3 fanout on the selected word

**Bounded new mechanism and favorable profile screen. No physical supplier or new kappa is claimed.**

This package extends the consecutive shared-source C3 family in [PR #1799](https://github.com/CrocSwap/integer-mult-bounds/pull/1799). It allows selected ADD shears to be separated by operations that commute exactly with every selected shear. For `C_d = I + a E_(d,s)` and an intervening ADD `G = I + b E_(u,v)`, matrix multiplication gives

\[
C_dG-GC_d=ab\bigl(\mathbf 1_{s=u}E_{d,v}-\mathbf 1_{v=d}E_{u,s}\bigr).
\]

For a nonzero intervening ADD coefficient, the exact rule is `u != s` and `v != d`; a zero ADD is the identity and always commutes. Thus an intervening ADD may read the shared source or write a selected destination; it may not update the common source or read a selected destination. An intervening diagonal SCALE commutes when its factor is one or its register is outside the common source and all three destinations. The verifier checks this algebra against small exact matrices in focused positive and negative controls.

## Result

On the exact selected width-73 rational word pinned at base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`, exhaustive A/B enumeration found:

| Quantity | Exact finite result |
|---|---:|
| Eligible C3 triples | 54 total |
| Consecutive triples | 32 |
| Nonconsecutive, exactly commuting triples | 22 |
| Maximum disjoint interval schedule | 27 triples (2 in A, 25 in B) |
| Nonconsecutive triples in the maximum target-saving schedule | 4 |
| Resulting paid rank mass | 5,586, unchanged |

The target-saving schedule has paid profile `{1:2377, 2:422, 3:417, 4:124, 5:82, 8:8, 9:8, 12:6}`. Under the selected 896-family, nine-stage ceiling, its upper endpoint is `1705759704147/1000000000000000 = 0.001705759704147`, a **0.9292953979%** increase over the selected fixed-word upper endpoint `1690054109089/1000000000000000 = 0.001690054109089`. For comparison, PR #1799 reports +0.9065527351% for its consecutive-only schedule; the new schedule adds two grouped intervals while remaining a very small fixed-word improvement.

At `a = 1.05` times the selected ceiling's upper endpoint, the exact weighted interval DP maximizes an optimistic saving bound over every eligible schedule. The resulting moment lower bound is still above one by the exact positive margin in `CERTIFICATE.json` (about `0.0001979582081`). Therefore no schedule in this finite commuting-C3 family reaches the five-percent target, even after granting zero adapter, copy, helper, hosting, frame-transition, restoration and precision costs. Any such expenses are additional nonnegative costs.

The schedule's four nonconsecutive groups are B indices `[185,186,188]`, `[201,202,204]`, `[217,218,220]`, and `[468,504,736]`; the last group factors across 266 intervening gates that each pass the exact commutator criterion. Full sources, ranks, coefficients, gaps, schedules, profiles, and exact rational margins are in `CERTIFICATE.json`.

## Reproduce

From the repository root, with Python 3.10 or later and the standard library:

```sh
python3 -B research/complex-commuting-fanout-seed6935/verify.py
python3 -B -m unittest discover -s research/complex-commuting-fanout-seed6935 -p 'test_*.py'
python3 scripts/research_package.py --package research/complex-commuting-fanout-seed6935 --check-only
```

Expected verifier line: `PASS_COMMUTING_FANOUT_FINITE_SCREEN`. The verifier binds the selected record, selected source manifest, assembly certificate, compressed and decompressed word, selected slot pin, and ceiling implementation. It reconstructs the complete baseline local profile before enumerating candidates.

## Scope and attribution

This is a fixed-word, fixed-arity, fixed-coverage result. It does not cover noncommuting dependencies, other local words, other fanout arities, or a physically realizable child adapter. The candidate rank profile replaces each selected triple's positive target increments by one child whose rank is their sum; this preserves total rank mass and is only a favorable local profile model. The cost of realizing that interface is not known. No selected frontier is changed.

The result is a complementary follow-up to [PR #1799](https://github.com/CrocSwap/integer-mult-bounds/pull/1799), which studied consecutive triples and left nonconsecutive source-version intervals open. The original claim and current overlap snapshot are included. Substantial AI assistance from OpenAI Codex is disclosed; no independent review is claimed.

## Open next questions

- Can a physical adapter realize the 27-group schedule while preserving arbitrary dirty input values and fitting the full source, copy, helper, hosting, transition, restoration and precision bill? Start by deriving exact maps for the four nonconsecutive B groups. This matters because the screen's zero-interface profile is not a supplier. It is blocked by the absence of an admitted adapter contract and complete invoice.
- Can another arity or a changed coverage law create a target-scale gain? Start with a fully charged optimistic moment under the explicitly changed hypothesis before any new enumeration. This result's certificate covers only C3 on one selected word under the selected coverage law.
