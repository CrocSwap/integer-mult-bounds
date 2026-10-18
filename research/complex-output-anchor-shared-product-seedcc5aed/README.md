# Zero-anchor shared-product block

**Exact conditional local construction. No selected-provider placement or new κ is claimed.**

This package studies a new output-state interface for the `complex-new-helper-inventory` task. One required output starts clean and becomes the shared product itself. That removes the separate clean scratch helper and its cleanup multiplication used by the closest prior shared-product construction.

## Construction

Work over F_2. For q >= 2, let

\[
F_0(x,y)=x_0y_0,\qquad
F_i(x,y)=x_0y_0+x_i y_i\quad(1\le i<q).
\]

The entry state has $A_0=0$ and arbitrary dirty $A_1,\ldots,A_{q-1}$. The forward schedule is:

1. One rank-one child toggles $A_0\mathrel{\oplus}=x_0y_0$.
2. For each $i=1,\ldots,q-1$, linearly add the required output $A_0$ into $A_i$, then use one rank-one child to toggle $A_i\mathrel{\oplus}=x_i y_i$.

The final state is $A_0=F_0$ and $A_i=A_i^{\rm entry}\oplus F_i$. All dirty non-anchor targets are preserved as XOR accumulators. The reversed schedule restores the initial state exactly. The anchor is not a temporary register: its final value is the required output.

For one block, the direct per-output evaluation costs $1+2(q-1)=2q-1$ rank-one calls. The anchor construction costs $q$ rank-one calls and $q-1$ affine ADD fanouts. It uses no extra clean helper, no source copies, no frame changes, and no helper cleanup call. The affine fanouts are counted explicitly; only rank-one multiplication calls enter the selected recursive-moment profile. If a target interface charges them as recursive work, that charge must be added and the screen rerun.

For the same output contract, a direct adaptation of the scratch-helper schedule computes and uncomputes the common product in a separate clean register. It costs $q+1$ rank-one calls, $q$ affine ADDs, and one clean helper slot reused sequentially across blocks. The output anchor removes one child call, one ADD, and that helper slot per block. Thus the incremental result beyond scratch-based sharing is deliberately modest: one child per block. The much larger comparison against the selected profile below includes the common-product reuse mechanism already explored in PR #1872.

The bilinear tensor rank is exactly $q$. Its output slice matrices are $E_{00}$ and $E_{00}+E_{ii}$ for $1\le i<q$. In any zero linear combination, diagonal entry $(i,i)$ forces the coefficient of $E_{00}+E_{ii}$ to vanish; entry $(0,0)$ then forces the remaining coefficient to vanish. Thus the output-slice span has dimension $q$, while the displayed $q$ products give a matching decomposition.

## Conditional selected-word screen

The selected record at base `0b1cccf86e2f5132ed286a26ef0a681a495740ea` has per-call profile

```text
{1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
```

The local screen uses `m=73`, 896 families, 9 stages, centre charge 64, and idle-rank cap 51. In the conditional placement scenario, each of the 8 pair/orientation classes has a 112-channel block with one clean output anchor and the same common operand pair. Each block replaces 223 direct rank-one calls with 112 rank-one calls and 111 affine fanouts. Across the eight blocks, the hypothetical per-call profile is

```text
{1: 1524, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
```

This saves 888 rank-one calls and adds 888 affine ADDs, with zero extra clean-helper roles. Using the pinned `ceiling.ceiling()` relaxation at grid $10^{-12}$, the exact upper endpoints are `169005411/100000000000` for the selected profile and `202675103/100000000000` for the conditional profile. The certified relative-gain interval is

```text
[336696919/1690054110, 336696921/1690054109]
```

whose lower endpoint is about 19.9223%. The relaxation sends freed local mass to idle children of rank at most 51. This is a local conditional ceiling, not an admitted supplier or a κ result.

The same-interface scratch-helper profile is `{1: 1532, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}` and has ceiling bracket `[126444951/62500000000, 2023119217/1000000000000]`. The anchor profile improves that ceiling by the certified interval `[3631812/2023119217, 1815907/1011559608]`, about 0.1795%, in addition to removing the reusable clean helper slot and eight affine fanouts across the eight sequential blocks. The profile work and per-call helper counts are in [CERTIFICATE.json](CERTIFICATE.json).

## Scope and unresolved placement

The exact local contract is complete for $2\le q\le112$, including arbitrary dirty non-anchor accumulators and a zero anchor. The eight-block profile is conditional. This package has not identified eight matching operand families or verified clean anchor state in the selected provider. If the real provider requires output clearing, copies, transfers, frame changes, helper hosting, precision work, or extra restoration, the invoice must include them and the moment must be recomputed. The selected frontier and its κ are unchanged.

Nearest predecessor: [PR #1872](https://github.com/CrocSwap/integer-mult-bounds/pull/1872), head `626ce207ec92a76f70a84843fe4ce3c39f67899d`, shares a product among arbitrary dirty mixed outputs using one separate clean scratch helper. Its three-output instance costs five rank-one calls versus six directly, with two helper calls including cleanup and three ADD fanouts. An active related claim by the same account on [Discussion #1167](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18923890) names that task and predecessor. This package instead makes each common product a required clean output, uses no extra helper, and does not clean that output away. The distinction is the output-state contract and the one-call-per-block helper-elision saving; no broader novelty is claimed.

The accepted task selection was seed `cc5aed06f9ab7cecac40f4b4a54dccb5`, track `complex-mechanisms`, priority revision 3, catalogue SHA-256 `6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075`. The selected-record SHA-256 is `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. Full source pins are in [SOURCES.json](SOURCES.json); the scope claim is [Discussion #1167 comment 18925019](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18925019).

## Reproduce

From the repository root, using the standard library and the pinned local ceiling implementation:

```sh
python3 -B research/complex-output-anchor-shared-product-seedcc5aed/verify.py
python3 -B research/complex-output-anchor-shared-product-seedcc5aed/verify.py \
  --write research/complex-output-anchor-shared-product-seedcc5aed/CERTIFICATE.json
python3 scripts/research_package.py --package research/complex-output-anchor-shared-product-seedcc5aed --check-only
python3.12 scripts/research_package.py --package research/complex-output-anchor-shared-product-seedcc5aed
```

The generic registered replay expects Python 3.12; direct local verification is also supported with the available Python interpreter. `CERTIFICATE.json` records exact counts, rational ceiling brackets, and controls.

## Open next questions

1. Can the pinned provider supply eight disjoint 112-port blocks with the required repeated source pair and a clean anchor at entry? This determines whether the conditional profile can become a physical local-word improvement. First step: trace source identities and target entry states in a source representation that exposes bilinear operands. The predecessor phase-A stream lacks operand-pair fields, so another source-bound representation may be needed.
2. If such blocks exist, do their actual source/output transitions require any charged copies, transfers, frame changes, hosting, precision work, or restoration? This determines whether the exact profile survives the real interface invoice. First step: write and replay the local state schedule against the pinned provider. The blocker is that no candidate placement has yet been identified.

## Credit

Prepared by Cinna Davis with substantial OpenAI Codex assistance in scope selection, construction, exact screening, verifier implementation, overlap checks, and writing. No independent human review is claimed. New work is Apache-2.0; predecessor attribution is retained above.
