# Q8 three-role targets retain their direct call bills

**Scoped exact finite result; no supplier or kappa change.** In the three-register `F2[Q8]` paid-call model, every coordinate permutation of `diag([z],[z],[x])` or `diag([z],[z],[y])` has exact minimum five calls. The all-central target `diag([z],[z],[z])` has exact minimum six. Here `x=i`, `y=j`, and `z=-1=x^2=y^2`. The latter resolves the Q8 predecessor's listed open question about the three-active-role target.

## Model and cost

A paid factor is

`D_N(g) = I + ([g] + [1]) N`,

where `g` is `x` or `y`, and `N=uv^T` is any binary rank-one idempotent in `M3(F2)`. There are 28 idempotents and 56 paid factors. Equality is coefficientwise in the full eight-element group algebra, so each identity holds for arbitrary dirty contents of all three registers. The check covers free scalar `GL3(F2)` mixing by normalizing it into the paid factors; every one of the 168 conjugations preserves the enumerated idempotent set. No free address maps, clean roles, COPY/ERASE, or unpriced calls are allowed.

The coordinate construction costs five calls for `diag(z,z,g)` (two calls for each `z`, one for `g`) and six for `diag(z,z,z)`. The search gives no local call saving. The construction cost includes every paid factor; extra setup, hosting, precision, restoration and any physical address-group implementation are set to zero, so it is an optimistic formal screen. The selected bit primitive remains above the complex primitive (`0.001733427039589844...` vs `0.001675462676808103...`), and no mapping of this Q8 model into the selected supplier is known. This result cannot change selected kappa.

## Exact lower bounds

The quotient `J/J^2` of the augmentation ideal records the abelianization classes of `x` and `y` as independent `C2` directions. Each `x` factor contributes `N` to the `x` coefficient matrix, and each `y` factor contributes `N` to the `y` coefficient matrix. Every such `N` has trace one over `F2`.

For `diag(z,z,x)` the first-order trace parities are `(1,0)`; for `diag(z,z,y)` they are `(0,1)`. Thus every word for these targets has odd length. The exhaustive exact state search finds none through length four, while the coordinate word has length five. Their exact minimum is five.

For `diag(z,z,z)`, both first-order coefficient matrices vanish, so the number of `x` calls and the number of `y` calls are each even. Every realizing word therefore has even length. The exact state search finds no word through length four, and length five is excluded by parity. The six-call coordinate word is optimal.

The first-order invariant supplies only the parity restriction. The depth-four census is what excludes the remaining shorter words; it is not a claim about other targets or longer words.

## Exact census and controls

Breadth-first search starts from the identity matrix and right-multiplies all 56 paid factors. A state is the full 3-by-3 matrix of eight-bit group-algebra coefficients. Equal states have identical continuations, so exact state deduplication preserves complete coverage through depth four. The counts below are new states at each minimum distance; digests hash each sorted layer as concatenated nine-byte states.

| Depth | New states | SHA-256 |
|---:|---:|---|
| 0 | 1 | `8c6a94754fb4364d433e02bca32367314b62f40c15aad5dd88748e5843715742` |
| 1 | 56 | `920b43f241039210191338537e0bd917afdd1d4c6ddbab3e31a16d15642b96cf` |
| 2 | 2,324 | `0403597968f6fb572c65e5da6a3edbd9afc2cec41b518afde02b8d6b78183b9c` |
| 3 | 89,574 | `e3f6671475c4ae9bb909dffea5cb05010c6aa8afbb0b3969d0ee471fbc0611b0` |
| 4 | 3,286,437 | `e4501b88905298a7098da79c9f11e9a1ed595bf41da4e1a3467a8d7addd9b2c0` |

The verifier checks Q8 associativity, the `C2 x C2` abelianization map, all rank-one idempotents, all `GL3(F2)` conjugations, and 952 packed-versus-generic matrix transitions. It verifies all seven direct target words, 36 one-call-deletion controls, and the known depth-four `diag(z,z,1)` positive control. The generic matrix multiplier independently checks each direct word and each sampled transition.

The search represents at most `10,013,305` raw words of lengths zero through four before merging identical product states. The depth-four frontier expands 5,016,144 outgoing transitions. The exact state search and parity proof together establish only the stated minima in this finite alphabet.

## Reproduce

From the repository root:

```sh
python3 -I -B research/q8-r3-two-central-one-generator-seed809fc39d/verify.py
python3 -I -O -B research/q8-r3-two-central-one-generator-seed809fc39d/verify.py
python3 scripts/research_package.py --package research/q8-r3-two-central-one-generator-seed809fc39d --check-only
```

Expected verifier status: `PASS_Q8_EXACT_MIXED_TARGET_FLOORS`. The local direct replays use CPython 3.14.7; the registered package manifest targets Python 3.12. The package check pins its exact Q8 predecessor inputs and selected-result provenance. The selected cold replay remains `make frontier1094-verify`; it was not rerun because this contribution does not change the selected construction.

## Open next questions

- **Do the `diag(z,z,x/y)` minima remain five for every `r>=3` when additional dirty identity-target roles are allowed?** This would separate the three-role result from the uniform mixed-target bounds already proved for other Q8 profiles. A feasible first step is to derive an `r`-uniform trace/rank lower bound after the `J/J^2` parity step, then identify the first coefficient degree not controlled by parity. The blocker is that the current exact census is only for `r=3`, and the number of rank-one idempotents grows rapidly with `r`.

## Credit

The group model and Q8 factor normalization follow the merged Q8 central-pair result in PR #1822 and the mixed-target result in PR #1925. The `diag(z,z,z)` endpoint was explicitly left open in the Q8 predecessor package. PR #2047 and Discussion #2034 concern one central output with two order-four outputs, a different role profile. Prepared by Cinna Davis with substantial OpenAI Codex assistance; no independent human review is claimed. The repository contribution is Apache-2.0.
