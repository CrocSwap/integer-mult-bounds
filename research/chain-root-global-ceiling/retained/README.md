# Conditional κ = 0.00337180 from a chain-nested root on the #6824 native word

The supplier tree of the #6726 caller is replaced by one root with a full site for
every native call and a chain of whole idles. The native word is unchanged. The
complete 18-call construction supports **κ = 0.00337180**, up from the pending
**0.00330823** in [#6824](https://github.com/CrocSwap/integer-mult-bounds/pull/6824),
a gain of **+6.36e-5** (**+1.92%**).

The raw crossing lies strictly in **(0.0033718004754, 0.0033718004755)**; the tested
saving is 0.00337180035. Selected κ = 0.003125804 is unchanged.

All five framework assumptions remain: `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape`, and `analytic_recovery`. External review is open.
This is a conditional, author-side construction result.

## The construction

Fields are `A, f_0..f_8, h_0..h_8` and one empty field `E`, so `n = 20`.

- L site `i`: `x = A + f_i + 2Σ_{j<i} f_j`, `y = A* - f_i*`, support `{A, f_0..f_i}`.
- R site `m`: `x = -A + h_m + 2Σ_{l>m} h_l`, `y = A* + h_m*`, support `{A, h_l : l >= m}`.
- Three thin queries between the groups complete the shortest root `Π(I - 2R_k) = -I`.

Each inner field has one idle line, `φ = f_{j-1}`, `γ = f*_{j-1} - 2A*` (mirrored on the
right). The line and its dual are killed by `y_i` and `x_i` on every later site of the
group, so it commutes across them, and its stage factors combine into **one whole idle of
rank `8·(sites covered)`**, ranks 8 to 64. Each inner field has a target of rank `8q+1`
against a paid rank `8q`, and no binary supplier nodes are left.

`PROOF.md` proves the arbitrary-input identity and states the chain-merge lemma.

The same constructor at shape `(4,4,1|1,4,4)` is built in every replay as a gate: its
invoice equals #6726's minus one cancelling pair `T_32 = P_32`, and both interval engines
place its crossing in #6824's interval (0.00330823456614, 0.00330823456615).

| Complete census | #6824 | This construction |
|---|---:|---:|
| Native calls / native word | 18 / same | 18 / same payload |
| Caller roles | 34 | 20 |
| Caller events | 606 | 1,237 |
| Thin queries | 15 | 3 |
| Whole idle jobs (`IDLE` / `IDLE_ONE` events) | 3,120 (12 / 6) | 1,664 (0 / 16) |
| Largest paid rank | 40 | 64 |
| Largest stage support (coordinates) | 4 | 10 |
| Productive fields | 13,688 | 12,232 |
| Paid Gaussian requests | 66,888 | 64,184 |
| Paid rank mass | 178,044 | 166,812 |
| Rank-mass surplus | 760 | 760 |
| Ordinary caller upper bound | 535,415,008 | 488,177,792 (recomputed) |
| Physical contacts | 7,488 | 7,488 (recomputed) |

Caller scalars are integers: `ADD` by ±1, ±2, −3 and `SCALE` by −1.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-chain-nested-root
```

The self-contained scientific replay also works without Git or network:

```sh
python3 -B research/p104-chain-nested-root/verify.py
```

Expected: `PASS_CHAIN_NESTED_ROOT`, with conditional κ = 16859/5000000, and
`PASS_REGISTERED_RESEARCH_PACKAGE` from the registered command (normal and optimized
interpreters). The literal caller is `CALLER.json`, rebuilt by `chain_root.py`; the pins are
in `EXPECTED.json`. To write the native word, use
`python3 -B research/p104-chain-nested-root/construct.py --output lifted-native.json.gz`.

## Sources and review boundary

Base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The native word is rebuilt from the #6702
word through #6805 and #6824 (`2a7ca44fbda3abaa4df355b183ed7d7478eef7c1`), and
`native_payload_sha256` is unchanged from #6824. The #6726 caller at
`435bbe91fb28cb1d7a569ca70c6c4e9eb302d486` is retained and rebuilt as the comparison
baseline. All required bytes are committed, with Git blob and SHA256 pins in
`retained/SOURCE-PINS.json`; nothing needs fetching for replay. The canonical-job adapter
charges follow [#6763](https://github.com/CrocSwap/integer-mult-bounds/pull/6763).
`ADAPTERS.md` lists each adapted driver and each recount.

**Whole idles at ranks 48 to 64 extend the rule #6726 used at rank 40. This package gives no
new compiler proof for them.** The merged lines also cross sites with different ordinary
bases, unlike #6716's shared-basis coordinates; `ADAPTERS.md` and `PROOF.md` section 6 quote
the rule and state the reading for reviewers to check.

The retained BIT saving is 17/5000, the claim is below it, and no BIT improvement is claimed.
The selected full multiplier cold replay, hosted CI, proof-kernel verification, historical
pending-commit ancestry and human review are not claimed. No exhaustive novelty search is
claimed. Reviews under `retained/predecessor-reviews/` concern earlier words.

## Open next questions

1. Does the compiler contract accept whole idles of rank 48 to 64 across several sites with
   no further argument? This is the first point to review.
2. Do roots with more than one coupling field admit a longer chain? Each needs its own exact
   root, identity and complete bill; none is claimed here.

Structured first steps and blockers are in `TASK.json`.

## Credit

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code, for the chain-nested root.
thu-nmrc for common idle fusion (#6716); zxv for the two-pair root and paid fragments (#6726);
[@CubeJerry](https://github.com/CubeJerry) for #6805 (substantial OpenAI Codex assistance) and
the BIT pin it keeps; Ali Romman for the independent-helper basis mechanism, the exact caller
replay engines and native input lifting (#6349, with #6353 and #6372); DreamingOfClouds for
#6702, #6375 and #6824; the canonical-job adapters follow #6763. Cinna Davis, David Arias and
Gareth Davidson for native/caller predecessors; Jacob Alan Sussman for productive
recursion/compiler work; Cao Yifan, ywz65, Nick Petalas and all retained source authors for
interval and analytic work. Original notices, headers and the Apache-2.0 license are preserved.
