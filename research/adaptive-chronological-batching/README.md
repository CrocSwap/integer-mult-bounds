# Chronological batch divisibility for arbitrary-height forests

**Result (conditional batching transfer, no new kappa).** Mihir Srivastava's
[PR #4507](https://github.com/CrocSwap/integer-mult-bounds/pull/4507) gives the
least per-cut replication factor for the *default-height* direct flow of zxv's
[PR #4436](https://github.com/CrocSwap/integer-mult-bounds/pull/4436). Its open
question 2 asks whether that policy survives the arbitrary-height forests of
[PR #4483](https://github.com/CrocSwap/integer-mult-bounds/pull/4483). It does.
For every height `G >= 0` and every ambient rank whose forest contains a unit,
the same batch list, least-LCM replication factor and cost recurrence hold, and
the normalized rank-one leaf cost is unchanged. #4483 already covers the
aggregate arbitrary-height flow, so what is new here is the **batch level**:
which exits must form one whole supplier batch, and why. The conditional
width theorem below bounds width growth, not a tighter leaf exponent;
there is no convergence or native-admission claim.

**Executed evidence.** Python 3.12.14, standard library only.
The direct isolated replay passed in 35.02 s: 405 nonempty census fixtures,
19,089 literal oracle classes, 2,304 brute-force minimality cases and 25
semantic rejection controls. Six compilations check 186,476 chronological
batch constraints. The final width replay passed in 2.20 s: four additional finite
compilations, 13,377 batch constraints, three pinned profile applications
and two boundary controls. Receipts are [RESULT.json](RESULT.json) and
[WIDTH-RESULT.json](WIDTH-RESULT.json).

Huge receipt integers are represented by bit length and big-endian SHA256;
the exact calculations and acceptance comparisons still use integers.
No global integer-to-decimal safety limit is disabled.

Independent OpenAI review of the Anthropic batching implementation found no
blocking issue; its isolated optimized replay passed in 34.39 s. Independent
Anthropic review of the OpenAI width implementation and its proof found no
gap; its final isolated optimized replay passed in 2.25 s. These are AI
checks, not human or proof-kernel acceptance.

The companion conditional all-rank width theorem is in [WIDTH.md](WIDTH.md).
It is a separate argument, written and reviewed by the parent, and is not
repeated here. This package and the preserved
[default-height package](../chronological-width-bound/README.md) form one
contribution with two scoped replays, not two competing submissions.

**Delta against the closest proofs and checks.**
[#4586](https://github.com/CrocSwap/integer-mult-bounds/pull/4586) at
`aadb7bc59390683450b1969e4632f546929dc569` already proves the default-height
bound `log B_N=O((1+log N)^(d+2))`. The default companion sharpens it to
`d+1` by bounding visits to each source-count plateau.
[#4588](https://github.com/CrocSwap/integer-mult-bounds/pull/4588) at
`2f6578907b7f8718a13921552cc3069d3908e936` supplies independent finite
default checks. [#4591](https://github.com/CrocSwap/integer-mult-bounds/pull/4591)
at `84c0fb3a39bcb1e4b8c48892bfdd8a6e7ae58a50` checks arbitrary-height
aggregate identities, not feasibility of each actual chronological cut.
This package adds that cut-level transfer and its conditional fixed-parameter
all-rank envelope; it does not claim the inherited aggregate identities,
least-LCM algorithm or default finite width improvement as new.

**Specialization is symbolic, with distinct hypotheses.** WIDTH.md gives
`z=max(0,1-g log_M(k0))` and degree `d'+1`. At `M=k0,g=1`, `d'=d,z=0`,
so it recovers the default order on their common domain. The named adaptive
code interface requires positive `a,b`, hence `g=a+b>=2`; that route does
not exercise `g=1`. Direct fixed-height/g witnesses are separate. WIDTH.md
assumes paid rank one for nonemptiness; the default proof needs no such
assumption because its root is nonempty. The default plateau-product and
adaptive level-LCM divisors differ; neither is claimed universally smaller.

## 1. What is certified

Fix positive integer multiplicities `W_k` (target ranks, `2 <= k0 <= k <= m`)
and `P_r` (chronological paid ranks, `1 <= r <= rmax < m`). At ambient rank `n`
put `C = floor(n/m)` and pick any integer height `G >= 0`. The forest has one
class per paid-round path `(d, rho)`; `rho` is the product of the paid ranks
along the path. Class `(d, rho)` holds the units `u(alpha)` of every target
multiindex of degree `G-d` with `rho c(alpha) <= C` (PROOF.md of #4483, section
1). A class that holds no unit still spawns its child at paid rank `r` whenever
`rho r <= C`; those children can hold units and fresh sources.

**Batches.** The complete batch list at `n` is

1. `(n-s, S_s)` for every source rank `s`, taken before the flow starts, and
2. `(e, q)` for each *cut*: one paid position of one path class, grouping the
   equal-rank unmatched exits of that class's units.

The replicated copies, the repeated paid positions and the repeated path
classes are occurrences. They multiply the exit and cost census, **never** the
`q` of a cut.

**Theorem A.** Let `B_j > 0` be the prescribed widths for `j < n`, with
`B_0 = 1`, and let `S > 0` be the source count. Put

```text
a_n = lcm over batches (e,q) of B_e / gcd(B_e, q),        B_n = S a_n.
```

Then (i) every batch is a whole number of supplier invocations at replication
`a_n`, (ii) `a_n` is the least such positive integer for this policy and these
`B_j`, and (iii) the normalized leaf cost obeys #4483's recurrence

```text
L(n) = [ sum_s S_s L(n-s) + sum_e E_e L(e) ] / sum_s S_s,
```

independent of every `B_j`. This equals the leaf cost of the nested #4436
widths at each rank, whenever both widths are valid.

## 2. Why #4507's proof extends

#4507's argument uses only the following facts about the forest. Each is
re-derived for arbitrary `G`; none needs `G = floor(log_k0 C)`.

* **Divisibility (ii).** `B_e` divides `a q` exactly when `(B_e/g) | a` for
  `g = gcd(B_e, q)`, because `B_e/g` and `q/g` are coprime. The conditions for
  all batches hold exactly when their LCM divides `a`. This is height-free
  number theory.
* **Strict descent.** Every recursive call must have a smaller rank so strong
  induction supplies `B_j`. An exit is an actual paid job of rank `r z`
  with `z <= C`, so `1 <= e <= rmax n/m < n`. A source has rank
  `k z` with column `z <= C`, hence `1 <= s <= n`, and its complement `n-s`
  lies in `[0, n-1]`; rank 0 costs 0. **Root sources can be small** at large
  `G` (as small as `k0^(G+1)`), which breaks the default-height lower bound
  `s > n/m` on every source. It does not break descent: only `s >= 1` is used,
  and a smaller `s` only enlarges the complement rank.
* **Cut structure.** At depth `G` a present class has `F_0(1) = 1` unit, so each
  paid position of a leaf class is a cut of size one. At depth `d < G` a present
  parent at product `c` supplies `F_(G-d)(c)` units and the child at paid
  rank `r` demands the Pascal terms with `rho r c/k <= C`. Present supply
  covers demand (Pascal expansion), the positive difference is one cut at
  rank `rho r c`, and demand with an **absent** parent
  (`rho c > C`) is a fresh inner source. Distinct target multisets with one
  product `c` are one cut because they leave through the same rank, `rho r c`;
  the batch list sums them.
* **Empty classes.** A class that holds no unit has an empty supply but its
  child may not, so the path must continue while `rho r <= C`. Dropping it
  loses the later components and their sources. This is the case that the
  default height never reaches, since there the root is always nonempty.
* **Chronology.** Each class and all its exits return before the next
  suspended paid position resumes, so cuts of different paths or positions are
  never pooled even if their ranks agree.

The cost step is the same: complements contribute
`sum_s (a S_s/B_(n-s)) P_(n-s)` leaves and cuts contribute
`sum_cuts (a q/B_e) P_e` with all occurrences kept. Dividing by `B_n = a S`
cancels `a`, and induction from `B_e = 1, P_e = e` below `m` gives the
recurrence. No claim is made about physical routing or native cost.

**Mathematical limitation.** Minimality is local to this policy, one fixed
library of smaller widths, and one common replication per rank. Joint
optimization, fractional or per-class replication, and widths not forced by
divisibility are outside it. Nonemptiness of the forest is a hypothesis: the
verifier requires a unit, and an empty flow is not replaced by a supplier. A
paid rank one makes this automatic (WIDTH.md).

## 3. Independent checks

`batching.py` holds the multiplicative-polynomial census (`census`,
`batch_rows`, `multiplier`, `compile_widths`, `check_ledger`, `leaf_total`). It
imports no predecessor code. `verify.py` supplies three separate references.

1. **Literal oracle.** `oracle_flow` enumerates ordered target words by sorted
   content, instantiates every paid position separately, and returns each
   child before the next position. It uses no Pascal coefficient, no
   product-keyed polynomial and no compressed path count. It is compared on
   roots, inner sources, boundary exits, leaf exits, columns, units, matched
   jobs and the full multiset of cuts `(depth, rho, paid rank, exit rank, q)`,
   at toy profiles and several `G`, in both paid orders for two fixtures.
2. **Closed form.** `closed_form` recomputes cut sizes and fresh sources from
   `Q = sum_(k|c, rho r (c/k) > C) W_k F_(G-d-1)(c/k)` and its absent-parent
   counterpart, sharing nothing with the census.
3. **Authenticated #4483 Flow.** The bytes of `research/rank-convergence/flow.py`
   and `research/direct-mixed-flow/flow.py` are hashed against pins before
   `exec`. Sources, exits and unit columns are compared on all 405 nonempty
   fixtures. Every fixture has paid rank one; rejection of a wholly empty
   forest is not exercised. Empty-root forests with later components are.

On top of this the verifier recovers #4507's default-height widths and leaf
counts, checks that the least width divides the nested one at every rank,
checks the normalized cost recurrence in exact rationals, and brute-forces the
minimality of the LCM against all small `(B, q)` pairs.

## 4. Semantic controls

Each control must fail for the stated reason; a wrong exception type or
message fails the check.

| Control | Why it is semantic |
| --- | --- |
| drop-empty-parent | Suppresses the later components below an empty class. Disagrees with the literal oracle and with the authenticated Flow on the empty-root fixture. |
| drop-boundary, drop-leaf | Remove premature or final exits. Disagree with the oracle and break the formal rank-invoice cancellation. |
| ignore-path-multiplier | Child eligibility without the paid prefix. |
| split-collisions | Keeps distinct same-product target multisets in separate cuts. A pinned collision geometry (targets 2, 4, 8) merges two contents at rank 80. |
| pooled aggregate, occurrences, leaf-pooled | Each pooled multiplier passes its own rows but leaves an actual cut with a nonzero remainder. The verifier first finds a geometry with a real gap for each policy. |
| multiplier missing a prime factor | `a/p` leaves a remainder; `2a` is accepted. |
| zero, boolean and future-rank inputs, equal paid and target maximum, non-integer multiplicity | Contract violations. |
| omitted occurrence leaf cost | Breaks the exact normalized recurrence. |
| tampered flow bytes | Fail before execution. |
| perturbed receipts | A false root, a false unit column and a missing cut fail the ledger. |

## 5. Source inputs and bounded domain

Pinned in [SOURCES.json](SOURCES.json) and declared in [VERIFY.json](VERIFY.json):
#4507's `README.md` and `batches.py`; #4483's `PROOF.md`, `flow.py` and
`BENCHMARKS.json`; `direct-mixed-flow/flow.py`; the p7 invoice at
`higher-moment-strictification/RESULT.json`; and, for the width probes,
`native-lattice-retiming/RESULT.json` and `compact-joint-compiler/arithmetic/RESULT.json`.

The real profile is the pinned raw p7 invoice (7,688 target and 55,998 paid
items), never a retuned strictification. The later
[PR #4533](https://github.com/CrocSwap/integer-mult-bounds/pull/4533) changes
the height base; this package does not certify that geometry.

Bounded replay domain, set by the code:

* Oracle census: `n = factor m + extra` for small factors, all eight height
  rules, `G <= 6` (`G <= 2` for the heavy repeated-paid profile). The oracle
  stops at 300,000 classes.
* Least-width compilations: four toy geometries through rank 100 and two p7
  height rules through rank 1,209.
* Real-profile source comparison: p7 at ranks 121 through 60,000 for the
  census only; no all-rank compile there.
* Width probes: see `width_bound.py` and WIDTH.md.

## Reproduce

From the repository root:

```sh
python3.12 -B research/adaptive-chronological-batching/verify.py --write
python3.12 -B research/adaptive-chronological-batching/verify.py
python3.12 -O -B research/adaptive-chronological-batching/verify.py
python3.12 -B research/adaptive-chronological-batching/width_bound.py --write
python3.12 -I -O -B research/adaptive-chronological-batching/width_bound.py
python3 scripts/research_package.py --package research/adaptive-chronological-batching --check-only
```

The complete registered replay is
`python3.12 -B scripts/research_package.py --package research/adaptive-chronological-batching`.
`--write` is needed only to intentionally regenerate receipts, not to replay them.
The other scoped replay in the same PR is
`python3.12 -B scripts/research_package.py --package research/chronological-width-bound`.

`--write` regenerates the committed receipt and then exits. A plain run
replays and requires equality with the receipt. `--survey` prints the
authoring statistics for the pooling gaps.

## Coordination and historical provenance

The base `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`, priority revision 7,
the `independent-moment` original card and all source pins remain historical
provenance. The consolidation comparison uses fetched main
`fbc9ea0249746acca4f504d4fda2b84e0e36cf0d`: selected conditional κ is
`.00302015` from #4470, not #4483 or #4507. No selected-frontier file changes.
The 2026-10-22 overlap refresh covers 408 open PRs at 13:08:38 UTC, 3,852
closed PRs at 13:09:39 UTC and 3,577 Discussion records at 13:09:11 UTC,
with complete reported pagination. This non-atomic snapshot is not an
exhaustive novelty proof; the actual #4586/#4588/#4591 proofs/code supply
the comparison above. Evidence and the combined PR draft remain local-only
pending publication approval. Existing receipts report author/AI runs and
were not regenerated during consolidation; no human/formal acceptance is claimed.

## Open next questions

1. **Retuned geometries.** Does a pinned retuned height base such as #4533's 768
   for p16 keep the same divisibility and width envelope? This matters because
   a new base changes the forest. A first step is to add its `(M, g)` to the
   probes, with an authenticated profile pin, and compare each cap to the
   source Flow. Blocker: the pinned profile bytes.
2. **Sharper width envelope.** Can actual gcd savings or narrower semigroup
   counts tighten the bound of WIDTH.md? A first step is an exact prime-valuation
   recurrence at selected pinned p7 ranks, then a symbolic bound retaining gcd
   cancellation. Finite fits alone cannot prove the asymptotic improvement.

## Credit

Predecessor work: Jacob Alan Sussman's integer lockstep compiler; zxv's #4436
chronological flow and #4483 arbitrary-height wrapper; Mihir Srivastava's #4507
least batching policy, whose proof this package extends; Ryanson Jonathan's
#4459 mirror identity underlies the #4483 accounting. New material here is
Apache-2.0, prepared for codyw912 with substantial AI assistance (OpenAI model
sessions and an Anthropic-model implementation worker). The independent
mathematical challenge of WIDTH.md was also AI review. None of it is human or
proof-kernel verification.
