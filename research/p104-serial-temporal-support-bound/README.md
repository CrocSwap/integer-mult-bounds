# Timed input support for serial MOVE fusion

**NO VERIFIED GAIN.** The fixed-clock model for #7161 grants arbitrary coframed scalar work, unlimited cache, the old paid calendar, and optimistic availability of other serial fusions. Missing original input coordinates exclude every candidate spanning a certified read gap. At κ = 0.0040075385047236, the 1,024-gap cap removes 1,105 of 3,925 blocks. The remaining optimistic price is positive. [Proof](PROOF.md) · [Directed receipt](RECEIPTS.json)

## Reproduction

Use CPython 3.12 with assertions. From a clean checkout:

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-serial-temporal-support-bound
~~~

Regenerate the full temporal receipt with `python3.12 -I -B checks/temporal_barrier.py source7165` from the package directory. The registered check authenticates the path-keyed [bundled source inventory](INPUTS.json) and verifies all three exact stdout digests.

## Open next questions

Resume at role 85, read 40874. Preserve all pending blocks in the directed price upper until an exact exclusion applies. Any surviving layout must preserve the signed arbitrary-input read, ownership and restoration with the actual costs. Moving another paid clock and terminal-only repair are separate mechanisms.

## Credit

Clear1nsight #7161 supplied the native word. Rohan Arun #7113 supplied the signed caller and directed arithmetic. #7165 supplied the normalized replay and paid extractor. See [proof attribution](PROOF.md#attribution) for adjacent same-head work and earlier retiming. Codex and subagents materially assisted. New work is Apache-2.0.
