# Stream the complete high-prefix directory into its real consumer

**Scoped source-order theorem and bounded executable certificates; no new bound.**

The original producer writes every complete old/new prefix to a whole directory
before its consumer starts. [streaming.py](streaming.py) instead reuses one saved
old-prefix role, one current-prefix role, one reader counter and one odometer,
then invokes the actual leaf and XOR consumer synchronously. It preserves all
physical occurrences, including repeated bytes, and every high matrix in original
source order. [PROOF.md](PROOF.md) gives the uniform contract, induction, backing
bound, cleanup scope and complete remaining ledger.

The complete generic q3,w2,d2 test produces all 81 high matrices for each of three
old physical prefixes. All243 prefixes and the full 19683-bit dirty-payload result
match the original eager pipeline and independent byte/permutation oracles;
1458 actual coefficient callbacks remain in each execution arm. The separate
[actual64.py](actual64.py) calibration substitutes the same consumer code into
#4981's authenticated actual R437 SOURCE87 nonzero-high fixture. It samples two
complete prefixes of the 3**4096 domain and makes no full-domain claim.

The retained current-directory backing is `(2h+1)B+2` for the two prefix roles,
with `B=(code_bits+1)+d²(word_bits+1)+1`; the original new directory needs
`C H (h+1) B` cells. Encoded counters, odometer, setup and erasure remain paid.
The full borrowed payloads and owned result remain; the unchanged leaf allocator
still creates per-call tapes, so this is not an overall physical reserve saving.

## Reproduce

```sh
python3 scripts/research_package.py --package research/r437-streaming-directory --check-only
python3.12 scripts/research_package.py --package research/r437-streaming-directory
```

The registered normal and optimized hooks authenticate all declared live inputs
before execution and compare typed deterministic receipts. [SOURCES.json](SOURCES.json)
pins exact Git/SHA256 provenance and the historical selected-loader projection.
The actual64 harness reads the pinned predecessor verifier and restricts its AST
without changing frozen source files. [ACTUAL64.json](ACTUAL64.json) and
[RESULT.json](RESULT.json) are separate deterministic receipts.

## Family gate

#4981 proved prefix-local functional fusion but retained the full producer. This
package closes that named obligation once, with complete generic production,
rather than adding another selected statement or tiny prefix census. The active
#4927 existing-directory audit remains separate. The actual complete GL64 gather,
Context/codebook setup and q127 huge payload are not executed or priced.

## Open next questions

The next useful task is a source-bound persistent pool for the complete leaf/XOR
workspace plus its movement/erasure tariff. Start by tracing every per-prefix
Tape constructor and lifetime in the actual leaf; retain all full input/output
and spectator backing. Without that whole-caller result, do not infer a supplier
admission, kappa change or a complete multiplication theorem.

## Credit

JoyboyBrian; substantial OpenAI Codex assistance; Apache-2.0. Retains Chris R /
Clear1nsight's physical bridge and all original directory, numerical, leaf and
XOR source attribution. The #4981 fixture and theorem are pinned predecessors.
