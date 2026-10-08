# Merged auxiliary exteriors

This finite conditional witness gives
**κ = 55354656014473/10^18 = 5.5354656014473×10^-5**, with bit saving
**27678860161103/(5·10^17)**. It is **6.9746%** above PR79's witness, which
is its base.

**Idea.** In the inherited accounting every auxiliary role pays a separate
exterior edge I − I_h⊗B with profile [h, m−2h]. Auxiliary source frames are
free, so this residual can be merged into the role's creation edge
I − (I_h − A_first)⊗B. For a role that is not an output, it can instead be
merged into its retirement edge I − A_last⊗B. Each role takes whichever of
the three options has the lowest profile cost. Words, gates, XORs, W and the
deficit are unchanged.

| Quantity | h23 | h25 |
|---|---:|---:|
| Auxiliary roles R | 27,297 | 35,684 |
| Merged at creation | 15,410 | 20,111 |
| Merged at retirement | 4,216 | 5,149 |
| Unchanged | 7,671 | 10,424 |
| Distinct merged edges certified | 8,537 | 10,601 |

The first-order profile cost Σ t·n_t·ln(m/t) drops from 3.5686×10^10 to
3.3359×10^10.

**Corner-rank lemma** ([PROOF.md](PROOF.md) §3–5). Let M = I − Y with
Y = UW^T and W^T U = I. Then the NE corner rank of M is

- (i−j+1) − r + rank U_{<j} + rank W_{>i} for j ≤ i+1;
- rank U_{≤i}W_{≥j}^T for j ≥ i+1.

In the PR34 fixed basis these reduce to ranks of local submatrices X[S,T], so
the profile is the same for every other-axis line. Each X[S,T] is a 0/1
diagonal plus a rank ≤2 correction. Its rank is computed exactly over Q from
2×2 integer determinants, with no modular step.

**Bridge change.** Merged edges create bit children up to **552**, above the
inherited 529. As a result:

- the bit halving degree becomes **17** (it was 9);
- the row coefficient becomes 1059;
- the product row stock is raised from p^2000 to **p^2200**, with gap 991/25.

This affects only the row-product slack and the eventual cutoffs, not κ
(§7).

```sh
make merged-exterior-verify
make verify
```

The focused target does the following:

1. Checks the controlled permutations against the pinned PR34 module.
2. Recomputes every candidate edge profile exactly and replays the per-role
   selection. There are 24,586 candidate edges for h23 and 31,717 for h25.
3. Profiles the removed transitions with the unchanged inherited profiler.
4. Rebuilds the complete child list on top of PR79's verified profile.
5. Checks the exact and independent moment enclosures, and that the next grid
   point is rejected.
6. Verifies the 47 assembly constraints and the seven margins with the
   recomputed bridge.

It takes about 4 minutes on 4 cores.

As an additional discovery-time check, all 19,138 selected edges were compared
with direct NE elimination of the full 575×575 physical matrix for one line
modulo 2^31−1, with no mismatch. Unit tests check Lemma 1 against exact
elimination on random layouts.

Builds on @chafreaky [#79](https://github.com/CrocSwap/integer-mult-bounds/pull/79)
and the work it composes:

- @eumemic [#57](https://github.com/CrocSwap/integer-mult-bounds/pull/57), [#69](https://github.com/CrocSwap/integer-mult-bounds/pull/69)
- @rohangar1 [#59](https://github.com/CrocSwap/integer-mult-bounds/pull/59)
- @ikeboy [#62](https://github.com/CrocSwap/integer-mult-bounds/pull/62)
- @DominikScholz [#63](https://github.com/CrocSwap/integer-mult-bounds/pull/63), [#68](https://github.com/CrocSwap/integer-mult-bounds/pull/68)
- @rohanarun [#65](https://github.com/CrocSwap/integer-mult-bounds/pull/65), [#67](https://github.com/CrocSwap/integer-mult-bounds/pull/67)
- @alejandrozu [#70](https://github.com/CrocSwap/integer-mult-bounds/pull/70)
- @chafreaky [#60](https://github.com/CrocSwap/integer-mult-bounds/pull/60), [#71](https://github.com/CrocSwap/integer-mult-bounds/pull/71)

It also uses the PR34 fixed basis (jamesyc) and the PR29 two-stage endpoint
note. The merged exteriors are by eumemic with Anthropic Claude assistance.
