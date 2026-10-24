# Acceptance addendum: corrected literal tariff and independent local envelope

This addendum **supersedes two version-specific statements in the frozen `REVIEW.md`**: the exact scalar tariff is 175,022, not 175,038; and the provider's maximum-field local exponent 18,996 now has an independent literal recomputation and proof review. The partial-provider acceptance scope is unchanged. There is still no completed consumer, autonomous credit for coupled H, complete precision/funding theorem or new kappa.

The authoritative new scientific outputs are `agents/budget/RESULT-v3.json` and `agents/budget/LOCAL-ENVELOPE-v1.json`, produced by root's guarded runs. I inspected both scripts, the written `LOCAL-ENVELOPE-PROOF.md`, semantic results and root guard receipts/stdout. A separate static check authenticated the script/result hashes, all fourteen norm-source pins and both log hashes. It also compared the complete stored recursive profile and conditional moment screen against v1 and found exact equality. No scientific execution occurred in this acceptance lane. Original acceptance and scientific artifacts remain untouched.

## Literal scalar-tariff correction

The emitted `PROVIDER.json` field `cache_scalar` already means the final output coefficient `1/(2 f_i)`. The earlier independent checker treated it as f_i and applied the reciprocal formula again. That misread affected its exact boundary scalar tariff. It did not change the emitted source, physical equations, operation counts, paid/productive profiles, moment intervals, cleanup budgets or no-credit boundary.

The new `screen_v3.py` uses the emitted `cache_scalar` directly. Its diff changes that interpretation, checks the resulting totals, and records its own executed SHA256. The actual boundary scalar tariff is 42 rather than 58; the full inherited tariff including eight SWAP allowances is **175,022**, or **16,854 above the original raw-source 158,168**. The prior 175,038 was a conservative overestimate, but calling it an exact literal bill was incorrect. Earlier code/results and their preserved execution history remain version-scoped evidence of the independent checker's correction, not a provider construction failure.

The root v3 run passed with exit zero, no termination, 0.908223 seconds guard elapsed and sampled peak descendant RSS 57,507,840 bytes. The complete recursive comparison and the hypothetical eight-H8-per-provider necessary screen are byte-for-byte equal as JSON objects to the previously reviewed result. No numeric moment conclusion is strengthened by this sixteen-unit ordinary-tariff reduction.

## Independent envelope and its geometry

The new checker constructs the entire finite provider schedule from the current literal changed word, both basis programs, all actual mode input/output scalings, cache swaps/clears and boundary words. It recomputes exact upward power-of-two factors without executing submitted Python. Only after summing them does it compare the maximum-field exponent with the author's declaration.

For fields in the same square ambient Hilbert space at one fixed fiber width, use either

```
||v||max   = max_j ||v_j||2
||v||joint = (sum_j ||v_j||2^2)^(1/2).
```

ADD has norm at most `1+|q|` in either geometry; SCALE has whole-bank norm at most `max(1,|q|)`. CLEAR, whole-field SWAP and square unitary maps have norm at most one. COPY has maximum-field norm at most one, but joint-field norm at most `sqrt(2)`, conservatively enclosed by two. This COPY bound applies to arbitrary destination perturbations, because COPY discards the old destination and duplicates the source. It does not assume a numerically clean destination.

The exact logarithm ceilings produce

| Geometry | Independent exponent L | Bound |
| --- | ---: | --- |
| Maximum of field Euclidean norms | 18,996 | `2^18996` |
| Joint field Euclidean norm | 19,012 | `2^19012` |

The difference is exactly the sixteen COPY operations. It is a change of norm geometry, not a contradiction of the author's maximum-field statement. The exact rational-logarithm, COPY-geometry and direct emitted output-scaling controls passed.

All elementary assigned exponents are nonnegative, so the sum over any contiguous subinterval, prefix or suffix is at most the complete L. Submultiplicativity gives its operator bound `2^L`. Expanding propagated initial error and local residuals through suffixes then gives, in the selected same geometry,

```
||e_out|| <= 2^L (||e_in|| + sum_j ||local_residual_j||).
```

These are whole-field residual norms at one fixed width. With zero initial error and m residuals of norm at most epsilon this gives `m*2^L*epsilon`. It is not a dimension-independent conversion from coordinatewise error, nor a choice of machine precision.

The all-width premise is substantive: mere free-group invertibility would not suffice for the unitary bound. The written proof uses the normalized square native gate `C_q=((1+i)/2)I+((1-i)/2)X_q`, where the translation X_q is a self-adjoint involution; cross terms cancel, so C_q and its inverse are unitary. Invertible address permutations and unit-modulus diagonal/phase factors are unitary. Canonical frames, their complex conjugates and chart transitions preserve this property. The checker verifies the actual frame/warp rank conditions and invertibility of each literal boundary P. Columnwise tensor lifts preserve unitarity at every positive width, while scalar owner coefficients stay exterior. Therefore the finite exponent bound is uniform over widths under the stated normalized square realization.

The source's adapter and phase annotations retain the pinned physical interpretation. This new checker does not reconstruct every inherited native physical implementation or prove the absence of hidden rescalings independently of that retained contract. The already reviewed source/physical audit and explicit square-unitary premise remain necessary. Complete caller precision, routing, storage, movement, recursive primitive implementation, compiler and outer funding remain outside the local envelope.

The root envelope run passed with exit zero, no termination, 0.504455 seconds guard elapsed and sampled peak descendant RSS 59,138,048 bytes. The result records the complete grouped exponent contributions and abstract scalar/unitary transcript hash.

## Static bindings

| Artifact | SHA256 |
| --- | --- |
| `screen_v3.py` | `9805fb55fe2888ae7e10a96c5f91e032fc9e6ac95a7831fed987d502e4814c2e` |
| `RESULT-v3.json` | `3918ce76fabf77199f18756249b13067c3d2319b67dfbab86d922de463320def` |
| v3 stdout, matching root receipt | `32fde6ed6a8a21cbcd27c1b95fcb3cd2e91d9222d7773cb5124b0c50c0631d98` |
| `independent_local_envelope.py` | `11d8b361adacac9ae44985ffa8a83ff0e9de47e94571e486427baa7201da7715` |
| `LOCAL-ENVELOPE-v1.json` | `f99bc2dd5f60b38d6ee9617fac9fb1f03ce9c5f10455650ccf2f7acc54bb490f` |
| Envelope stdout, matching root receipt | `1a27db01ba466c1ea58cf2bc1e8c6909b10ab6cb5144354f5fc4747fc3ef0350` |

The fourteen source pins in the envelope result match the files read during this static review. The result's executed-checker hashes match the current scripts. The written envelope proof was reviewed for the mathematical implications described above; subsequent publication prose should identify these outputs as executed and the v3 tariff as authoritative. Construction and predecessor credit remain as preserved in the source and other audit lanes.
