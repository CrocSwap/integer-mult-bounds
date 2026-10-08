# Balanced coarse sums, future completion and bounded carry exchanges

This reproducible finite conditional witness gives
**κ = 25872812736433/500000000000000000 = 5.1745625472866×10^-5**, with bit saving
**51748303221339/10^18**. This is **0.6437453019850683%** above the complete
published PR71 witness. The full old recursive child list is excluded at the
new accepted bit saving, using strict exact rational enclosures.

| Quantity | Published PR71 | This witness |
|---|---:|---:|
| h23 auxiliary roles | 27,455 | 27,297 |
| h25 auxiliary roles | 36,015 | 35,684 |
| Physical width W | 135,075,665 | 134,126,064 |
| Total recursive rank | 77,666,660,475 | 77,120,639,900 |
| Rank deficit | 1,846,900 | 1,846,900 |
| Bit wire bits | 28 | 27 |

The selected graph retains PR71's anchored `[1,1,2]` split recursion and
PR65's `cover-core` h23 / `reverse-node` h25 schedules. PR69's balanced
coarse sums use columns for h23 cells with `i+j<ng-1` and rows elsewhere;
h25 uses rows everywhere. Both dimensions select independent unit-completion
rows by compatible future uses. Only h25 adapts PR70's carry exchange with
fixed exact integer prices: up to three passes accept 1,000 exchanges.
PR67 cost-based reclamation and PR68 pending live controls retain both frame
containment checks and PR71's next-use score.

```sh
make balanced-split-verify
make verify
```

The focused gate freezes no files. It verifies the source closure,
regenerates the literal words and compares their decompressed bytes, replays
every ordinary and dirty basis column in both orientations, reconstructs frame
raises from literal XORs, and recomputes every actual fixed-I+J profile using
the inherited bounded-minor/CRT checks. It constructs all paid recursive
children, checks independent directed moment enclosures, rejects the next
10^-18 bit and κ grid points, and verifies all 47 strict assembly constraints
and seven margins. The width crosses below 2^27; every dependent bridge field
is recomputed and negative controls reject stale values.

The [proof and scope](PROOF.md) state the exact finite claims and the inherited
ordered residual compiler, all-size recursion, routing, prime selection,
recovery, finite scalar alphabet/tape and analytic transfer assumptions.
Arithmetic cutoffs are not full operational thresholds. There is no global
optimality, full formalization, practical speedup or removed-hypothesis claim.

PR71's complete published source/finite-input closure and arithmetic baseline
are preserved under `references/frame-compiler/pr71`. PR69 and PR70 originals,
licenses and notices are preserved in their own archives. Their ideas are
composed here without treating their external numerical claims as proofs.
Earlier contributor archives and certificates remain available. The two
portable engines retain every audited discovery function/class unchanged;
only ROOT is relocated. Source freezes are explicit maintenance operations
through `pin_balanced_split_sources.py`; derived arithmetic and validation
receipts are excluded to avoid circular inputs.

Source credits: @eumemic [#57](https://github.com/CrocSwap/integer-mult-bounds/pull/57)
and [#69](https://github.com/CrocSwap/integer-mult-bounds/pull/69);
@rohangar1 [#59](https://github.com/CrocSwap/integer-mult-bounds/pull/59);
@ikeboy [#62](https://github.com/CrocSwap/integer-mult-bounds/pull/62);
@DominikScholz [#63](https://github.com/CrocSwap/integer-mult-bounds/pull/63)
and [#68](https://github.com/CrocSwap/integer-mult-bounds/pull/68);
@rohanarun [#65](https://github.com/CrocSwap/integer-mult-bounds/pull/65)
and [#67](https://github.com/CrocSwap/integer-mult-bounds/pull/67);
@alejandrozu [#70](https://github.com/CrocSwap/integer-mult-bounds/pull/70);
@chafreaky [#60](https://github.com/CrocSwap/integer-mult-bounds/pull/60)
and [#71](https://github.com/CrocSwap/integer-mult-bounds/pull/71).
Chafik Boukhalfa prepared this selected composition with OpenAI Codex assistance.
All original authorship, license and AI-assistance notices remain applicable.
