# Exact price of simultaneous helper restrictions in the selected BIT word

**The selected BIT caller is globally optimal within the family of simultaneous helper restrictions studied here.** Its best raw price saving is the original PR7001 crossing, strictly between **0.0038525393934 and 0.0038525393935**. The proof covers arbitrary simultaneous choices within all nine boundary groups, all 437 helper coordinates, both word orientations, and the full price range. At the project's 0.01 target, even the best complete signed margin is between **−2355.302 and −2355.301**. The gate requires a positive margin.

This compares recursive rank prices under the fixed PR7001 word, granting free same-chart scalar XOR and retention of every earlier receiver value. The project's reviewed conditional multiplication exponent saving is **0.00363005817**. [Selected certificate](../../certificates/selected-result.json) · [Maintainer application review](../../docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md)

Price a rank-$r$ job at $r^t$, where $t=1-\eta$. Each of the nine groups may impose an arbitrary binary subspace of relations at the same time. Every independent relation surrenders one productive target of that group's rank. In either orientation, for $\log_2(5/3)\le t\le1$, the maximum gain per invocation is exactly

$$
\max_{(U_1,\ldots,U_9)}\bigl(\text{paid price saved}-\text{productive price surrendered}\bigr)
=\max\{0,\ 1+4^t-6^t\}.
$$

The complete paired caller uses 36 native invocations. Its maximum change in signed margin is 36 times this expression. Over the full interval $0\le\eta\le1$, an edit improves the original invoice exactly when $\eta>\eta_*$, where $6^{1-\eta_*}=1+4^{1-\eta_*}$. For the positive branch in the displayed range, setting helper 341 to zero removes one rank-one and one rank-four paid arrival per invocation and surrenders one rank-six target. [Proof and equality cases](PROOF.md) · [Exact certificate and bank witnesses](RESULT.json)

### Why the groups have to be checked together

Ali Romman ruled out restrictions within any one group at a time for $0\le\eta\le0.01$. His work includes the individual rank-six case. An actual bank at forward chart 50 has value $x_{331}+x_{332}+x_{333}$. Imposing $x_{331}=0$ in one group and $x_{332}+x_{333}=0$ in another makes that bank free to reconstruct. Each equation alone still requires the paid arrival. The new upper bound accounts for these interactions at every chronological receiver prefix and matches the rank-six witness. [One-group predecessor, PR #7722](https://github.com/CrocSwap/integer-mult-bounds/pull/7722) · [Single-relation predecessor, PR #7720](https://github.com/CrocSwap/integer-mult-bounds/pull/7720)

### Reproduce

From the repository root, use CPython 3.12 and the standard library.

~~~
python3.12 -B scripts/research_package.py --package research/bit-simultaneous-helper-relations
~~~

The first verifier reconstructs all 437 helper roles and all 2,871 paid arrivals, checks 3,530 receiver prefixes in each orientation, and certifies both the edit threshold and the global raw BIT ceiling with rational bounds. The second verifier solves the orthogonal equations in bank coordinates, checks all 820 price assignments on the largest block across the two orientations, and enumerates 64,882 small-block subspaces across both orientations. Both start from the original word. [Primary verifier](verify.py) · [Column-nullspace cross-check](crosscheck.py) · [Declared inputs](SOURCES.json)

Local verification used CPython 3.12.2 on Windows and CPython 3.14.7 on Arch Linux. The selected source-binding baseline and PR7001's original paired BIT application check passed. The complete selected PR7000 cold replay, human review, and proof-kernel verification are outside this session.

The physical domain fixes the paid forms, their order and their charts. Boundary changes stay within each common entrance/exit chart pair. Receiver equations may combine evidence from different groups. Changed paid routes, new chart transports, cross-chart boundary equations and forward/transpose compositions require separate analysis. Native all-column realization, owned erasure, the compiler, precision and tape accounting, and analytic recovery remain the five inherited framework assumptions. The scope of this proof is the exact scalar cost comparison.

## Open next questions

Can a **changed delivery after a restriction** beat the combined obstruction? PR #7723 keeps all public inputs independent and proves that each original paid arrival already has minimum rank among single causal nested deliveries. Here the inputs can satisfy joint relations and the paid route stays fixed. A bounded first experiment is to impose the two chart-50 equations, then test a still-required arrival against earlier source banks at a lower-rank nested chart. A candidate needs both productive debits, every new transfer, and a causal implementation at the receiver. [Single-delivery predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/7723)

### Sources and credit

AlephNaN (@alephnan) prepared this proof and both implementations with substantial OpenAI Codex assistance. The two checking methods share authorship. New work is licensed under Apache-2.0.

Ali Romman supplied the causal-bank model, the single-direction analysis, the one-group common-pivot bound, and the question about simultaneous groups. Jerry Chen / CubeJerry supplied the selected PR7000 construction and its PR7001 BIT dependency. DreamingOfClouds supplied the chain-root caller. zxv and the retained authors supplied the BIT word and earlier proofs. The package reads the two existing source files in place. [PR7001 and retained credits](../../research/paired-query-only-bit/NOTICE) · [Selected contributor map](../../docs/research/community-frontier7000-contributors.md) · [Predecessor proof at its exact head](https://github.com/aliromman/integer-mult-bounds/blob/8a70046cafae35d29627017983d55cec71e06e27/research/bit-joint-relation-bank-obstruction/PROOF.md)
