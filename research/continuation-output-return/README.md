# Physical output return through a continuation

This package closes the designated child-output return question left by
[PR #5329](https://github.com/CrocSwap/integer-mult-bounds/pull/5329) and
[PR #5356](https://github.com/CrocSwap/integer-mult-bounds/pull/5356).
One added relay tape preserves the result through child cleanup and physical
pop, delivers it into a reserved empty parent role, and returns empty.
All other parent bytes, heads, presence bits and descriptors are restored.
The fixed nineteen-tape bank works for arbitrary finite proper nesting.

[PROOF.md](PROOF.md) gives the contract, nesting proof, exact linear bill and
space charge. [return_output.py](return_output.py) uses only current-symbol
operations and unit moves. [RESULT.json](RESULT.json) records 1800 exact
invoice cases, nested returns through depth 31, six unchanged compact-source
endpoints and six rejecting ABI controls. Both source layouts deliver 1024
bits in 24388 return actions for dirty ancestor lengths 16,257,4096.

```sh
python3.12 -B scripts/research_package.py --package research/continuation-output-return
```

Both registered isolated, warning-strict normal and optimized modes print
`PASS_CONTINUATION_OUTPUT_RETURN`. Source bytes and the complete receipt are
checked. No third-party package is needed. The all-size claim rests on the
written induction, not the finite tests.

The complete kappa calculation is unchanged. A reserved empty parent output
role is required. Actual packet order, recursive C, physical source allocation,
logical-counter compilation, full supplier/stock/precision and outer recovery
remain open. Lean, Docker, selected cold replay and full-history validation
were not run. The source calibration retains its explicit Python facade.

## Open next questions

Bind this returned stream to the actual FOUR/base packet order and its left
map. First show where the caller reserves the output role and how its child
width determines the stream grammar. Separately compile the source's logical
counters and lexical slots at the repair/stable_radix maximum-live cut.
Neither obligation is discharged by successful byte delivery alone.

## Credit and coordination

Base 7c472563474e60185e6ca101a17622133d047e56, priority7. The live stack handoff
was already complete, so this package takes only its remaining output-return
boundary. Current PR and Discussion bodies and main notes were checked;
arbitrary historical diffs and unpublished work remain outside coverage.

The byte-exact stack and adapter in vendor/ are consumed from Ali Romman's
pending PR #5356, head ef1cc26e1e9a08c11cf382de948ee433bebab16d. They are pinned
in [SOURCES.json](SOURCES.json). Replay pins resolve to the byte-exact copies
in this PR history. Each upstream_pin retains the original pending source.
Thus a clean checkout does not need an unmerged predecessor commit. They are
not claimed as main-branch or independently accepted results. The complete
linear theorem is conditional on that retained stack contract. JoyboyBrian supplied the segment refinement
and locality invoice. Jose Manuel/jmbarrancoml supplied the retained sequential
compact source. Douglas Colkitt supplied guard/repair, Cinna Davis the caller,
and Matarener the cover/stock lineage. Original notices remain unchanged.

New work: Ali Romman with substantial OpenAI Codex assistance in proof,
implementation, review and verification. Apache-2.0. No independent human or
proof-kernel acceptance is claimed.
