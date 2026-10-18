# Research audit: sequential factor lookup in a balanced dirty word

The unchanged PR985 dispatcher admits an O(NB) factor-tape movement bound,
where N is its leaf count and B is the fixed descriptor width.
This replaces its conservative cubic lookup allowance with a quadratic term,
subject to the explicit layout, parsing, global-parameter, and control costs below.
It does not change the word, arithmetic precision, selected supplier, or kappa.

[PROOF.md](PROOF.md) gives the all-size argument for both directions.
For every n>=1, total index variation is at most 2(N-n).
Including the initial position and final return, index travel is less than 2N.
A reader that copies each full record and rewinds it uses fewer than 4NB head moves and exactly NB reads.
The result concerns a contiguous read-only region of fixed-width records.

The complete lookup bill is

```text
P_layout + P_parse + O(G + N(B + log^2(nB+2))).
```

G counts the bits in a fixed number of retained common parameters.
Layout conversion and parsing remain explicit; the proof also prices copies, preflight, counters, and returns.
The predecessor's numerical validation, preparation, data routing, arithmetic, and compiler obligations remain separate.
This closes one access-cost obligation, not the full execution or multiplication theorem.

## Reproduction

Use CPython 3.11 or later and its standard library:

```sh
python3 -I -O -B research/balanced-descriptor-travel/test_package.py
```

Expected: `PASS_DESCRIPTOR_PACKAGE`, five rejected package faults, and a nested
`PASS_BALANCED_DESCRIPTOR_TRAVEL` receipt with the following coverage:

- 78 signed dispatcher cases and 150126 actual factor lookups;
- two extra cases with length-five arrays;
- 4241 compressed word summaries, including counts beside powers of two through 2^60;
- 102 literal bit-tape cases at widths 1, 3, and 17;
- 1025 literal countdown cases, including zero detection and counter-head returns;
- nine mathematical or tape controls.

The actual pinned dispatcher uses length-one, zero-coefficient fixtures for its main trace checks.
Its factor branch structure depends on count and direction, not these coefficients.
The separate summary algebra uses no mutable arrays, dispatch calls, or expanded trace.
Literal tape and countdown models check the charged movement, reading, and control mechanisms.
These checks support the written all-size proof; they do not prove a numerical precision theorem.
The finite domains and stopping rule are fixed in `verify.py`; no adaptive search selects favorable counts.

The package harness also runs the full audit from a read-only copy with a different path.
Its source checks reject altered, missing, unlisted, unpinned, or uncovered vendor input.
`VALIDATION.json` records measured local checks and the interpreter; hosted CI is separate.

## Sources and credit

Ali Romman's PR985 supplies the unchanged dispatcher and its conservative descriptor-access bill.
The exact source head is `da1cdf8ed4ac9b1b8378dfec73f77ff4e81a4f70`.
Chafik Boukhalfa's PR628 supplies the balanced commutator and paid preparation lineage.
The exact leaf-count result retains 0xkilgore's PR663 credit.
Hanson Sun's PR1085 concerns prefix magnitudes, and Ali Romman's PR1054 concerns precision and length admission.
Neither numerical theorem is imported or reverified here.

[SOURCES.json](SOURCES.json) records source hashes, original Git blobs, and inspected related heads.
The vendor files retain their Apache-2.0 license and predecessor notice.
New work is by Charles Bethin, with substantial OpenAI Codex assistance in derivation, implementation, tests, and text.
There is no independent human review, literature-priority claim, runtime benchmark, or new kappa.
