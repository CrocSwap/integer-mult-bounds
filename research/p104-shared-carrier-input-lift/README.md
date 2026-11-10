# Conditional κ = 0.00330823 from a shared-carrier input lift on the #6805 word

Two independent helpers of the pending #6805 native word are born at a later
native frame, sharing one carrier register, and their responses are repaired
afterwards. The complete 18-call construction supports **κ = 0.00330823**, up
from the pending **0.00330814** in
[#6805](https://github.com/CrocSwap/integer-mult-bounds/pull/6805). The gain
is **+9e-8**, about **0.0027%**, which is small. This is a conditional,
author-side construction result, not a claim of a large advance.

The exact per-call signed saving, with `H_r = r^t` and `t = 1 − κ`, is

\[
\Delta T=H_7-H_9,\quad \Delta P=2H_1-H_3+H_4-H_5,\quad
\Delta(T-P)=H_7+H_3+H_5-H_9-H_4-2H_1>0 .
\]

The sign is not a consequence of concavity alone; `PROOF.md` proves it for the
exponents used and `RESULT.json` records the exact interval enclosures. The raw
crossing lies strictly in **(0.00330823456614, 0.00330823456615)**; tested
saving is 0.003308234. Selected κ = 0.003125804 is unchanged.

All five framework assumptions remain: `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape`, and `analytic_recovery`. External review is open.

## What changes

The package rebuilds the #6805 word from the #6702 word exactly as before
(`retimed_construct.py`, pinned by `base_native_payload_sha256`), then
`lift.py` applies the edit list `LIFT.json`. Public helpers 556 and 664 are
born at frame 105 instead of frame 3. Both share carrier register 120:
their responses to the frame-3 preparation rows are delivered at frame 105
to registers 120 and 179 (and, for the partner helper 665, at frame 1051),
and role 665 is repaired by `ADD(665,664,-1,127)` at the end. The edit is
ten deleted/replaced and ten inserted events; it leaves
the 772 public inputs, 29 owned labels, 47 lifetimes and peak 14 unchanged.

| Complete census | #6805 | This construction |
|---|---:|---:|
| Helpers per call, rank 9 / rank 7 | 360 / 9 | 359 / 10 |
| Paid per call, ranks 1 / 3 / 4 / 5 | 2232 / 490 / 109 / 153 | 2234 / 489 / 110 / 152 |
| Productive fields | 13,688 | 13,688 |
| Paid Gaussian requests | 66,870 | 66,888 |
| Paid rank mass | 178,080 | 178,044 |
| Rank-mass surplus | 760 | 760 |
| Native scalar allowance | 138,374 | 138,352 |
| Ordinary caller upper bound | 535,415,008 | 535,415,008 (recomputed, unchanged) |

`PROOF.md` gives the arbitrary-input identity and the local saving;
`PROOF-6805.md` is the retained argument for the #6805 step. `independent/`
holds separately written native and caller audits (the native audit now
covers both the split and the lift). `RESULT.json` is the combined replay receipt.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-shared-carrier-input-lift
```

The self-contained scientific replay also works without Git or network:

```sh
python3 -B research/p104-shared-carrier-input-lift/verify.py
```

Expected: `PASS_SHARED_CARRIER_INPUT_LIFT`, with conditional κ = 330823/100000000,
and `PASS_REGISTERED_RESEARCH_PACKAGE` from the registered command (normal and
optimized interpreters). To write the lifted native word (or, with `--base-only`,
the #6805 word):

```sh
python3 -B research/p104-shared-carrier-input-lift/construct.py --output lifted-native.json.gz
```

Compressed output is compared by canonical decompressed content, never by a
regenerated gzip-container hash. The pinned payload hashes are in `EXPECTED.json`.

## Sources and review boundary

Base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The #6726 caller is pinned at `435bbe91fb28cb1d7a569ca70c6c4e9eb302d486`;
its retained #6702 native bytes are the actual baseline. All required source
bytes are committed under `retained/`, with original paths, commit IDs, Git
blob identities and SHA256 pins in `retained/SOURCE-PINS.json`. No foreign
pending commit or archive must be fetched to replay. The explicit canonical-job adapter charges follow the independently reconstructed
[#6763 audit](https://github.com/CrocSwap/integer-mult-bounds/pull/6763), pinned at
`c3e0500c7645b1bc228ebe5e5190e304a2da46ca`.
`ADAPTERS.md` identifies
each adapted driver; original retained sources remain unchanged.

The scientific replay rechecks the complete candidate native program and
every used physical map. It does not trust a predecessor PASS string as a
substitute for this coverage. The retained BIT saving is 17/5000; no new BIT
improvement is claimed. The selected full multiplier cold replay, hosted CI,
proof-kernel verification and historical pending-commit ancestry are not
claimed. Registered metadata checks authenticate the canonical base/card;
the self-contained retained source checks authenticate executable bytes.

Live PR and public Discussion views were consulted; Discussion coverage was
partial and posting was unavailable through the connector. The local task
claim and exact scope are recorded in `TASK.json`. No exhaustive novelty
search is claimed.

## Open next questions

1. Do other contact-free helper pairs with a common birth frame admit a shared
   carrier on the lifted word? Each needs its own arbitrary-input identity,
   legal frames and complete invoice; none is claimed here.
2. Can the same lift be combined with the split's common frame, so that the
   response deliveries and the paid retiming share frames? The missing
   obligations are a new identity, legal physical frames and the complete bill.

Structured first steps and blockers are in `TASK.json`.

## Credit

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code, for the
lift. The word edited is [@CubeJerry](https://github.com/CubeJerry)'s #6805
(substantial OpenAI Codex assistance); credit zxv for #6726, thu-nmrc for #6716,
Ali Romman for the independent-helper basis mechanism and for the native input
lifting of [#6349](https://github.com/CrocSwap/integer-mult-bounds/pull/6349)
(with #6353 and #6372), and DreamingOfClouds for #6702 and the shared-carrier
lifts of #6375; the canonical-job adapters follow #6763. Cinna Davis, David Arias and Gareth
Davidson for native/caller predecessors; Jacob Alan Sussman for productive
recursion/compiler work; Cao Yifan, ywz65, Nick Petalas and all retained source
authors for interval and analytic work. Original notices, headers and the
Apache-2.0 license are preserved.
