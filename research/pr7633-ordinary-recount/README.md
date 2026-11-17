# Ordinary work for the role-457 edit in PR 7633

The two published bills reproduce from the literal words and the signed caller. Across 17 calls the candidate costs **182,036 more ordinary units** and has **208,462,624 units of headroom** under the strict billion-unit limit. This finishes the ordinary-accounting follow-up in fluorine's paid/target recount. It concerns one finite cost model under the proposed common private-storage service U. [Review request](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19678892) · [Prior recount and open question](https://github.com/CrocSwap/integer-mult-bounds/pull/7638) · [Scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19692060)

## Paired bill

| Ordinary-work term | #7631 source | #7633 candidate |
|---|---:|---:|
| Native scalar instructions, per call | 2,205,828 | 2,213,536 |
| Native routing including owned lifetimes, per call | 10,468,000 | 10,471,000 |
| Caller envelope, boundaries and routes, once | 559,238,336 | 559,238,336 |
| Conversions for all native public inputs and outputs, 17 calls | 2,653,768 | 2,653,768 |
| Second charge on caller LAMBDA uses | 11,280,000 | 11,280,000 |
| Caller ADD and SCALE surcharge | 2,248,928 | 2,248,928 |
| Caller odd-scale conversions | 479,232 | 479,232 |
| **Total** | **791,355,340** | **791,537,376** |
| Margin to one billion | 208,644,660 | 208,462,624 |

Multiply the first two rows by 17. Per call, the edit adds 7,708 scalar units, saves 1,000 units on a MOVE and adds 4,000 for the 205th private lifetime. The diagnostic INIT/CLEAR allowance refers to that same lifetime work. The 211,190,784 candidate margin inside the matched record is a subtotal. Deducting the last two caller charges gives the final margin in the application. [Matched record](data/7633-matched-ordinary.json) · [Signed application](data/7633-application.json)

## Evidence

The checker reads both complete words, pairs allocations with returns, counts every MOVE and prices the reduced rational literal of every ADD, COPY and SCALE. The 400 distinct main roles leave 1,101 public helpers. The native conversion tariff of 104 units per public field follows from scaling by 1,125 and its reciprocal at 52 units each. On the signed caller it counts the 17 joint events and the type-specific events, evaluates the actual output masks, idle stage sets and query signs, and weights each group by its ports (96 A, 8 B). The caller's own conversion uses the pinned odd scale 675 across 3,744 owners. [Native tariff](https://github.com/CrocSwap/integer-mult-bounds/blob/07a76c5e2738882c0cb322278e56f6cae3c9885d/research/signed-caller-8x9/replay/supplier7112/short-caller/independent.py) · [Signed caller charges](https://github.com/CrocSwap/integer-mult-bounds/blob/07a76c5e2738882c0cb322278e56f6cae3c9885d/research/signed-caller-8x9/replay/supplier7112/short-caller/check_odd_partial_admission.py) · [Caller grid receipt](data/7113-grid.json)

For the native conversion, start the 1,501 independent public coordinates on the trial grid with denominator $G = 1125 \cdot 2^{25}$. Every scalar product must divide exactly before addition, including products that later cancel. A stored coefficient is an initial unit, zero, a product or a sum of these. If $g$ is the gcd of $G$ and all product numerators on the trial grid, the least common denominator of all products and stored coefficients is $G/g$. Both words attain the full denominator. The checker visits 6,660,506 source and 6,669,042 candidate products on nonzero coefficients. Dividing the candidate grid by three fails at zero-based event 1,036, input coordinate 451. [Checker](verify.py)

The published subtotals and full bills enter only at comparison. Every numerical line in the paired record is checked, as is the complete candidate ordinary block in the signed application. Reversing one negative type-A query changes the route charge by 96,000 units. Moving four route items from lifetimes to MOVEs in the comparison record also fails, even though it preserves the grand total.

## What the lifetime allowance can absorb

Holding every other tariff fixed, substitute an integer ordinary price $u$ for one complete INIT/CLEAR lifetime in each native call. The two bills become $777{,}483{,}340 + 3{,}468u$ and $777{,}597{,}376 + 3{,}485u$. The largest common price satisfying **both** strict billion-unit inequalities is **63,817**. The candidate reaches 999,999,621 at that price and 1,000,003,106 at 63,818. This sensitivity calculation concerns the ordinary inequality alone. The submitted U contract requires its own 4,000-unit tariff and additional physical and scalar bounds. [Submitted contract](data/7633-common-u.json)

## Reproduce

The registered replay uses CPython 3.12 and its standard library. Run it from the repository root.

```sh
python3.12 -B scripts/research_package.py --package research/pr7633-ordinary-recount
```

From an exported copy of this directory, run `python3.12 -I -B verify.py`. Both commands print the counts, margins, tariff thresholds and control results. The arithmetic checker imports only the standard library. The two words, literal caller and comparison records are retained byte for byte. The #7633 source word is also exactly the candidate-word Git blob in #7631. Each input has an upstream commit, path, Git blob and SHA-256. [Source inventory](SOURCES.json) · [#7631 word](https://github.com/CrocSwap/integer-mult-bounds/blob/2f1cc8c0f8c281afd2f99aeeeae6153e269f4721/research/p104-e4-direct-on7627/evidence/e4-direct-204/candidate-word.json.gz)

The registered replay took 12.6 seconds with CPython 3.12.0 on Windows 11. As an additional check on the inherited caller input, a fresh run of #7113's grid checker on the retained caller reproduced all fields of its grid receipt, including 176,874 exact divisions. [Original grid checker](https://github.com/CrocSwap/integer-mult-bounds/blob/07a76c5e2738882c0cb322278e56f6cae3c9885d/research/signed-caller-8x9/replay/supplier7112/short-caller/check_odd_caller_exact_grid.py)

## Open next questions

Can one U implementation meet the declared tariffs on both complete histories? A first test is to account for the added private lifetime's reset and nonaliasing return at full extent, including residuals under rounding. This audit assumes the normalized scalar and service semantics. CLEAR witnesses, native operators, precision and tape realizability, the five framework assumptions and frontier admission remain separate review obligations. [Common-U contract](data/7633-common-u.json) · [Task scope](TASK.json)

## Credit

Clear1nsight supplied the #7631 word and the #7633 role-457 port on DreamingOfClouds' #7630 mechanism. Rohan Arun supplied the #7113 signed caller, with ToikY's signed-caller work and the shared-native and helper lineage of CubeJerry, DreamingOfClouds, SYLforge, Ali Romman and their predecessors. Fluorine identified the ordinary-accounting gap in #7638. Mihir Srivastava prepared this independent recount with substantial OpenAI Codex assistance. Apache-2.0. [#7633](https://github.com/CrocSwap/integer-mult-bounds/pull/7633) · [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) · [Retained notice](data/NOTICE)
