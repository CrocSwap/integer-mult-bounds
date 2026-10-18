# One arity-four source bundle on the universal connector

**Scoped negative result for a new connector operation; no selected-supplier or κ change.** Let the added operation be

```text
Q_S: z += sum(B_j x_j for j in S),  |S| = 4,
```

where the four existing source maps are applied into the same dirty connector in one root transition. All four source-map additions remain charged. The connector and five/six input rows may start dirty; sources are read-only; targets are independent and are not observed between operations. Every output map is required to be applied an even positive number of times so connector dirt cancels. The only alphabet change is this one Q4 operation.

## Exact source-word reduction

At each boundary let `q_t` be the parity vector of source-map additions so far. Then

```text
z_t = z_initial + sum_j q_t[j] B_j x_j.
```

If output map `A_m` is applied at two boundaries `s,t`, the dirty connector cancels and the target receives

```text
A_m(z_s + z_t) = A_m(sum_j (q_s XOR q_t)[j] B_j x_j).
```

Thus two reads of every nonzero output mask are possible exactly when the boundary-difference set contains every nonzero mask. The fixed connector lemma in the pinned universal-connector certificate supplies both directions of this test for arbitrary dirty rows and arbitrary admissible linear maps.

We first screened the smallest useful five-source profile. A four-source bundle plus eight singleton calls restores all five source maps with nine source transitions and ten boundary values. Relabeling sets `S={0,1,2,3}` and rotating the unique Q4 transition to the start. The five singleton-count profiles are `(3,1,1,1,2)` (four label choices) and `(1,1,1,1,4)`. The exact 15,120 distinct orders have no full 31-mask cover; the maximum is 25. This is a pivot result for that source-call profile only.

The six-source minimum is one Q4 plus ten singleton calls: the four Q-sources have odd singleton counts and the two other sources have positive even counts. There are six profiles: one Q-source receives two extra singleton uses, or one outside source receives two extra uses. After the same label and cycle normalization, the exact domain has **756,000** orders and twelve boundary values. Despite 66 unordered boundary pairs for 63 required masks, there is no full cover; the maximum is **41/63**. The complete histograms, an attaining 41-mask word, its 22 missing masks, the five-source pivot, and pins are in [RESULT.json](RESULT.json).

## Cost consequence in the uniform local model

Write `o` for one root instruction/call and `p` for one source or output map addition. A Q4 transition costs one `o` and four `p`; it does not erase any of the four child additions. Let `rho >= 0` collect every extra Q4-specific cost: macro implementation, nonuniform source-child deltas, staging, temporary storage, hosting, precision, restoration, interface transitions, and dispatch not already counted.

The best nearby six-source TRIO profile in PR #2146 is `138o + 140p` at head [`302b0e87d9328fabc2a670248afb357bbb44041b`](https://github.com/CrocSwap/integer-mult-bounds/commit/302b0e87d9328fabc2a670248afb357bbb44041b). The one-DUO comparator PR #2128 is `140o + 142p` at head [`697369a971eed02c0fbcd75ebefec9f59945f08e`](https://github.com/CrocSwap/integer-mult-bounds/commit/697369a971eed02c0fbcd75ebefec9f59945f08e).

For a six-source Q4 word:

| Source transitions | Pair coverage | Minimum output calls | Root calls | Map additions | Comparison with PR #2146 |
|---:|---:|---:|---:|---:|---|
| 9 | At most `C(10,2)=45`, so at least 18 masks have no two-read representation | 162 | 171 | 174 | Dominated |
| 11 | Exact census maximum 41, so at least 22 masks have no two-read representation | 170 | 181 | 184 | Dominated |
| 13 or more | Even source multiplicity makes the next length 13; at least 16 B additions remain | 126 | 139 or more | 142 or more | Dominated |

For each output mask without a boundary pair, an even target update needs at least four `A_m` reads. That gives the first two rows. In the last row, the minimum paired-readout bill is already componentwise above PR #2146. Every additional Q4 surcharge only raises the cost. Therefore this single-Q4 six-source family cannot improve the existing `(root calls, map additions)` frontier in the uniform positive `(o,p)` model. This is a root-interface obstruction only; it says nothing universal about other alphabets, additional Q4 calls, altered output contracts, nonuniform actual child prices, or the multiplication theorem.

## Reproduction and controls

From the repository root:

```sh
python3 scripts/research_package.py --package research/connector-quad-six-seedde3f84 --check-only
python3 -I -B research/connector-quad-six-seedde3f84/verify.py
```

The package runner is registered for the repository's Python 3.12 environment. This host has Python 3.14.7 and no `python3.12`; local direct verification is on 3.14.7. Expected direct output:

```text
PASS_QUAD4_SCOPED_OBSTRUCTION n5 15120 max 25 n6 756000 max 41 full 0
```

The verifier checks every live source SHA-256 and Git blob, exhausts all distinct words, independently compares set- and bitset-based difference calculations on the pinned positive control, verifies source restoration, and rejects both a deleted-source control and a coverage mutation that preserves source multiplicities. `SOURCES.json` pins the selected record, catalogue, baseline certificate, and verifier at exact base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.

## Assignment and attribution

- Accepted seed: `de3f84ac54d98bf098a9e9bab973b212`; track `recursive-interfaces`; task `connector-alphabet-change`; priority revision 4; selector scope key `ff4f5113ed2256ab19ed`.
- The exact n=6 one-Q4/10-singleton domain is the main result. The n=5 screen was a bounded pivot, not a claim about longer n=5 words.
- Nearest predecessor scopes: PR #2128 (pair-source DUO), PR #2134 and PR #2146 (three-source TRIO paths), and PR #2182 (fixed-port and two-root connector boundaries). Their work is not copied or modified.
- Live lexical searches also surfaced PR #2098 (an order-four typed echo with a 3|7 handoff across two banks; not a four-source connector bundle) and PR #2116 (a four-output target in the group algebra of `A4`; not an F2 source-bundle operation). Both were read and found to use different interfaces.
- Coordination claim and correction history: [Discussion #1166 comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18935950).
- Prepared by Cinna Davis with substantial OpenAI Codex assistance in scope selection, exact enumeration design, implementation, debugging, and packaging. No physical operation implementation, independent human review, supplier, or new κ is claimed. New package material is Apache-2.0; predecessor licenses are unchanged.

## Open next questions

This one-Q4 six-source family has a scoped cost obstruction. Any different operation arity, output-readout contract, or physical Q4 implementation is a separate hypothesis requiring a fresh budget and overlap check; no additional question is left open within this package's stated scope.

Maintainer integration note: the historical task catalogue is retained as `task-catalog-snapshot.json` and checked against its original SHA-256 and Git blob. The live research priorities have advanced; all mathematical inputs remain checked at their original paths.
