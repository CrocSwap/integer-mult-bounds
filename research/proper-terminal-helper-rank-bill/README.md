# A proper helper terminal and the rank bill

**Proof with an exact finite counterexample. No new κ.** The selected
conditional exponent stays `363005817/100000000000`. No word is emitted, no cut
is declared legal, and no ordinary or paid bill is priced.

## Result

Fix a real exponent `0 < t < 1`, integers `0 < T < D`, and `m ≥ 1`
contact-free paths `0 ≤ a_i ≤ b_i ≤ D`. The helper boundary now runs from `0`
to the proper terminal `T`, so the rank bill of a cut at dimension `x` is

```text
G(x) = x^t + (T-x)^t - T^t
       - Σ_i ( (x-a_i)^t + (b_i-x)^t - (b_i-a_i)^t ),
```

with `0^t = 0`. This is the formula of
[#7283](../helper-split-endpoint-rank-bill/PROOF.md) with `D` replaced by the
terminal `T`. A path with `b_i > T` leaves the boundary. The feasible interval
is `[A, B]` with `A = max a_i` and `B = min(T, min b_i)`.

**Theorem 1 (one crossing path).** If `m = 1` and `b > T`, then `G` is strictly
decreasing on `[a, T]`. Its maximum is `G(a)`. If moreover `a = 0`, then
`G(0) = 0` and `G(x) < 0` for every `x ∈ (0, T)`.

So the answer to the first step of the #7283 open question is: for one path that
leaves the boundary, the endpoint maximum survives, and the only candidate
dimension is the path's own lower endpoint.

**Proposition 2 (the terminal is never a positive bill).** For every `m` and
every path with `a_i ≤ T ≤ b_i`, `G(T) ≤ 0`, with equality exactly when `T` is
an endpoint of every path.

**Proposition 3 (no path starts inside the boundary).** If every `a_i = 0` and
at least one path crosses the terminal (`b_i > T`), then `G(x) < 0` for every
`x ∈ (0, T)` and every `m ≥ 1`. No number of boundary-crossing paths makes a
proper interior cut profitable in this first-order sense.

**Proposition 4 (the endpoint maximum fails for four crossing paths).** At
`t = 1/2`, `D = 26`, `T = 24` and paths

```text
(3, 25), (17, 26), (0, 25), (6, 25),
```

the interior dimension `x0 = 3819/160 = 23.86875` satisfies

```text
G(17) = -3.747477... < G(x0) = -3.554274...
G(24) = -3.734846... < G(x0).
```

The comparisons `G(17) < G(x0)` and `G(24) < G(x0)` are certified with exact
integer square-root arithmetic, not floating point. At this witness both
endpoint values are lower than the interior value, so the endpoint maximum of
#7283 does not survive a proper terminal once four paths cross the terminal.

The counterexample does not make the interior bill positive: it shows that the
endpoint comparison alone can understate the maximum, not that a gain exists.
Whether a positive proper-terminal bill can appear away from `A` is left open;
see Open next questions.

## Evidence classes

1. **Written proof.** Lemmas 1-3 and Theorem 1 in [PROOF.md](PROOF.md), for
   every real `0 < t < 1`, every integer `0 < T < D` and every `m ≥ 1`.
2. **Exact finite certificate.** Proposition 4 is one exact instance at
   `t = 1/2`. The verifier compares sums of integer square roots with a
   certified truncation whose error is strictly less than one unit per term.
3. **Exhaustive finite censuses**, only on the domains named in
   [VERIFY.json](VERIFY.json): the one-path decrease on a rational grid for
   `D ≤ 10`; the zero-start negativity for `D ≤ 8` and `m ≤ 3`; the terminal
   sign for `D ≤ 8` and `m ≤ 2`; and the absence of an interior win for two or
   three crossing paths on the stated grids (`D ≤ 8` for two paths, `D ≤ 7` for
   three). A census is not a proof for larger parameters and is not used as
   one.
4. **Control rejections.** The verifier rejects a flipped endpoint comparison,
   a one-path decrease claim applied to the four-path witness, and a positive
   terminal bill.

A failed or absent search is not used anywhere in this package.

## Scope and connection

Card `p104-side-correction`, priority revision 8, base commit
`e54523517d0f03e58352e647c403a5af3e525a57`, selected record unchanged.
Scope status: **changed**. The card asks whether a legal causal split improves
the complete P104 invoice. This package answers one boundary case of the
rank-bill factor that #7283 explicitly left open. It prices only the rank-bill
term `G`. Legality, ownership, ordinary cost and any target/paid invoice remain
where the selected record left them.

## Reproduce

From the repository root, CPython 3.12, standard library:

```sh
python3.12 -B research/proper-terminal-helper-rank-bill/verify.py
python3.12 -O -B research/proper-terminal-helper-rank-bill/verify.py
python3.12 -B scripts/research_package.py --package research/proper-terminal-helper-rank-bill
```

The direct verifier prints

```text
PASS_PROPER_TERMINAL_HELPER_RANK_BILL ...
```

Proof checks raise `SystemExit` rather than using `assert`, including under
`python -O`.

## Open next questions

- **Can a positive proper-terminal bill appear away from the endpoints?** The
  four-path witness has an interior maximum that is still negative. A search
  over four million random integer configurations with `D ≤ 24`, `m ≤ 8` and
  `t ∈ {1/2, 1/3, 2/3, 1/4, 3/4, 1/5, 2/5, 3/5, 4/5}` found no case with both
  endpoint values nonpositive and an interior value above zero. That search is
  floating-point evidence, not a proof and not part of the verifier. The
  smallest next step is to fix `m = 4` and ask for the exact sign structure of
  the unique interior critical point, or to prove the sign claim by a
  maximum-principle argument on the tent decomposition in PROOF.md.
- **Which crossing count is the threshold?** Theorem 1 proves one path. The
  verifier finds no interior win for two paths with `D ≤ 8` or three paths with
  `D ≤ 7` on the stated grids, and Proposition 4 gives four paths. Resolving
  `m = 2` and `m = 3` for all `D` would make the threshold exact.
- **Does a proper terminal help any actual helper?** Evaluate `G` at the two
  endpoints for one pinned helper of the published 68-split word whose terminal
  is proper, and compare with the zero-to-`D` certificate. A positive value
  would still need legality, ownership and the paid profile.

## Credit

The rank-bill formula, the zero-to-`D` endpoint theorem, the one-path
normalization and this open question are unpaidmoon's [#7283]. That package
credits CubeJerry's shared-native helper-split exploration and the two-chain
word from DreamingOfClouds in #6902. The present package adds the proper
terminal case, the crossing-path theorem, the zero-start proposition and the
four-path counterexample. Nothing from #7283 is replayed or re-audited.

This package was produced by Nick Petalas. Apache-2.0.

[#7283]: https://github.com/CrocSwap/integer-mult-bounds/pull/7283
