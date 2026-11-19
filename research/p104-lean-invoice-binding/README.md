# Complete formal caller invoice binding

This audit binds the formal caller in PR #7783 to the complete submitted
invoice in PR #7761. It proves that the formal paid and productive sums
match for every real exponent. It also proves that `Valid` holds for
`0 <= kappa <= 1/1000`, with margin at least `2432/25`.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[SOURCE-PINS.json](SOURCE-PINS.json), and [CREDITS.md](CREDITS.md).
The finite check covers 2,048 native calls, 5,746 banks per call,
400 mains, 862 helpers, both caller tables and the complete histograms.
Seven controls check the counts and main/helper distinction.

Use Python 3.12 with the standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-lean-invoice-binding
```

Both modes print this prefix, followed by elapsed seconds:

```text
PASS_P104_LEAN_INVOICE_BINDING 2048 calls 862 helpers 2432/25 margin 7 controls
```

No new multiplication exponent is claimed. This is an external proof
and source-aware computational audit. Lean, physical realization,
full caller chronology, ordinary BIT, outer assembly, stock and compiler
checks do not run. All five framework assumptions remain.

## Open next questions

Add the invoice identity and positive interval as Lean theorems. Start
with the existing `cdat` definition and these authenticated histograms.
This package supplies no Lean proof term or build.

Bind the caller tables to a complete physical execution. Start with
the pinned caller ownership and chronology checks. Equality to a
submitted receipt does not prove that receipt.
