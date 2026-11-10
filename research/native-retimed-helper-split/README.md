# Conditional κ = 0.00330814 from a retimed native helper split

Advance a paid main-register move to a contact-free interval, subdivide it,
and use the new common frame to retire one independent helper. The complete
18-call construction supports **κ = 0.00330814**, up from the pending
**0.00330720** in [#6726](https://github.com/CrocSwap/integer-mult-bounds/pull/6726).
The increase is **0.00000094**, about **0.0284%**. This is a small positive
construction result, not a claim of a large advance or global optimality.

The exact local signed saving is

\[
\Delta(T-P)=H_4+H_6-H_1-H_9>0,\qquad H_r=r^t,\quad 0<t<1.
\]

It survives explicit arbitrary-input/native-phase replay, all caller costs,
two rational interval engines, finite strictification, the uniform compiler
and all 54+4 outer inequalities. The raw crossing lies strictly in
**(0.0033081451891, 0.0033081451892)**; tested saving is 0.003308145.

All five framework assumptions remain: `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape`, and `analytic_recovery`. This author-side result
builds on pinned pending work. It does not change the selected κ = 0.003125804,
claim independent human acceptance, or materialize the enormous uniform
multiplier.

## What changes

In the native word retained from [#6702](https://github.com/CrocSwap/integer-mult-bounds/pull/6702),
old event 14088 moves main role 80 from frame 749 to frame 127, with rank six.
That role is untouched from old event 12372 until the move. Advance the move
to that cut and pay for `749 → 243 → 127`, of ranks one and five. At frame 243,
the supplied exact dual vectors expose helper 368 as an independent channel.
Three ordinary dyadic basis changes replace its rank-nine obligation by
independent rank-four and rank-five obligations.

The extra input is arbitrary, never presumed zero. There are 772 native public
inputs, 29 owned labels, 47 owned lifetimes and peak 14. The complete caller
allocates all eighteen extra helper inputs separately. No new nonzero erasure
or owned lifetime is introduced; the existing owned-erasure premise is retained.

| Complete census | Pinned predecessor | This construction |
|---|---:|---:|
| Productive fields | 13,670 | 13,688 |
| Paid Gaussian requests | 66,852 | 66,870 |
| Paid rank mass | 178,080 | 178,080 |
| Rank-mass surplus | 760 | 760 |
| Native scalar allowance | 137,990 | 138,374 |
| Ordinary caller upper bound | below 10⁹ | 535,415,008 |

The new premise is a **paid, legally retimed main contact**, not a better
allocation of the fixed #6726 caller or a deletion of a charged operation.
`PROOF.md` gives the identity, exact witness, complete invoice and qualification.
`independent/` contains separately written native and caller audits and their
review notes. `RESULT.json` is the combined replay receipt.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/native-retimed-helper-split
```

The self-contained scientific replay also works without Git or network:

```sh
python3 -B research/native-retimed-helper-split/verify.py
```

Expected: `PASS_RETIMED_NATIVE_HELPER_SPLIT`, with conditional κ = 165407/50000000.
The registered checks run both normal and optimized interpreters. To inspect
the rebuilt literal native word:

```sh
python3 -B research/native-retimed-helper-split/construct.py --output /tmp/retimed-native.json.gz
```

Compressed output is compared by canonical decompressed content, never by a
regenerated gzip-container hash. Exact compressed hashes remain appropriate
for the immutable retained input.

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

1. Can another contact-free retiming expose an independent helper after this
   split? Start with the frozen successor and change the allowed coframe or
   simultaneous paid-path support; rebuild every candidate and recalculate
   its complete invoice. The successful cut here supplies no general
   independence theorem for other cuts.
2. Can several channels be retired jointly with a smaller total paid detour?
   Start with a source-bound two-dimensional dual subspace and an explicit
   chronological handoff. The missing obligations are arbitrary-input
   independence, legal physical frames and complete completion/caller costs.

Structured first steps and blockers are in `TASK.json`. Search failures
reported in `RESEARCH-NOTES.md` are scoped diagnostics, not universal bounds.

## Credit

Jerry Chen / [@CubeJerry](https://github.com/CubeJerry), with substantial OpenAI
Codex assistance, including separate mathematical and implementation review.
Credit Ali Romman for the independent-helper basis mechanism and cumulative
P104 construction; DreamingOfClouds for #6702; zxv for #6726; Cinna Davis,
David Arias and Gareth Davidson for native/caller predecessors; Jacob Alan
Sussman for productive recursion/compiler work; and Cao Yifan, ywz65,
Nick Petalas and all retained source authors for interval and analytic work.
Original notices, headers and the Apache-2.0 license are preserved.
