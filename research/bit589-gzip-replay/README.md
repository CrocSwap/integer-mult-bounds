# PR589: compare regenerated words by their complete gzip payloads

**Opt-in portability repair; no new mathematics or selected-source changes.**

The selected bit replay reconstructs two words, then compares their gzip
containers using `cmp`. Eight controlled recompressions of the actual words
fail those comparisons even though every decompressed byte is unchanged.
This package replaces exactly those two comparisons with full decompressed-byte
equality. It also corrects the associated success message.

The local Python builds tested here reproduce the original compressed bytes.
The false rejections are controlled representation changes, not an observed
failure of those installed Python versions. Earlier cross-environment failures
are reported in [the T37 independent replay](../complex-t37-independent-seed39/README.md).

## Reproduce

The focused regression requires Python 3.12, Bash and `cmp`; it uses no Python
packages beyond the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/bit589-gzip-replay
```

The opt-in **complete bit-supplier replay** uses the original NumPy, SymPy,
SciPy, C++17 and Boost dependencies. Use an interpreter with those packages and
a fresh output directory outside the checkout:

```sh
export BOOST_INCLUDE=/path/to/boost_1_87_0
python3.14 -B research/bit589-gzip-replay/replay.py --work /fresh/external/bit589
```

This command executes all original steps 0–8. The registered regression command
does not execute that longer native replay. The default selected replay still
uses the frozen entrypoint.

## Preserved checks

The adapter pins the original shell script and input manifests, then invokes
an in-memory copy with its original `$0` and paths. The exact three-line delta
is checked by the regression. No original file is edited. Step 0 retains both
complete package manifests, vendored provenance and dependency checks.

Only the two **generated** files use payload comparison. The committed source
containers retain their exact hashes, including the original expected-word
checks and final summary. Every downstream mathematical command is unchanged.

The new comparison decompresses both files and requires exact byte equality.
It neither parses JSON nor drops fields: whitespace, metadata and unknown fields
remain bound. Gzip timestamps, compression levels and member boundaries may
differ. Invalid CRCs, truncated streams and unequal payloads fail. The argument
is equality of the complete input byte streams, without an additional semantic
canonicalization assumption.

## Evidence and limits

[EVIDENCE.json](EVIDENCE.json) records environment, commands, source identities,
observed outputs and artifact hashes. The focused suite passes on Python 3.12.13
and Python 3.14.6, including an optimized parent run:

- Eight timestamp/level/member variants: original shell comparisons reject;
  both adapted shell sites accept.
- Twelve gate, whitespace, extra-field, CRC, truncation and extra-member mutants:
  all reject under normal and optimized Python, giving 24 CLI rejection checks.
- Four original-word CLI controls pass; four source-drift controls and six
  missing/duplicate replacement-anchor controls reject.
- The adapter retains every other shell line, and the adapted shell parses.

The complete adapted replay passed on macOS arm64 / Python 3.14.6 in 131 seconds,
using NumPy 2.5.4, SymPy 1.14.0, SciPy 1.18.1 and Boost 1.87.0. It checked 883,
1,327 and 1,549 formal columns for five, nine and eleven stages, respectively,
and reproduced the original nine-stage bit saving
`1733427039589844234749/1000000000000000000000000`.

That complete run used the generators' normal compression. The eight alternate
encodings were exercised through the two actual shell comparison sites in the
focused suite; they were not eight additional complete supplier replays.
No selected `make frontier1094-verify`, Lean proof, hosted CI run, Windows run,
new κ or independent human review is claimed. All inherited algorithmic and
analytic obligations remain.

## Scope, overlap and credit

Base: `55a02580ce1b283026e9d3b3510b218f8c93a4de`. The task selector proposed
`portable-replay`; [TASK.json](TASK.json) records the refined two-word domain,
selection nonce and overlap checks. [SOURCES.json](SOURCES.json) binds exact Git
blobs and SHA-256 hashes. [Discussion #1547](https://github.com/CrocSwap/integer-mult-bounds/discussions/1547)
records the claim and disposition.

Credit DreamingOfClouds (#589/#545), eumemic (#555/#493), and their retained
construction, hosting and checker lineage. The payload convention follows
Maxime Fleury's [#220 audit](../gzip-container-reproducibility/README.md) and
Antoine Olivier's #214 findings. MrPink604's [#819 adapter](../pr626-native-payload-binding/README.md)
applies the same principle to a different PR626 owner-checker boundary.
Pending #946/#1298 address text encodings; #1509 addresses the bit589 Boost
dependency. This package changes none of their files.

Prepared for Hanson Sun (@bbMisk) with substantial OpenAI Codex assistance in
investigation, implementation, verification and writing. Apache-2.0.

## Open next questions

Should a maintainer-reviewed successor migrate the two default PR589 rebuild
comparisons to complete-payload equality? This would remove the need for the
opt-in entrypoint. A first step is a complete bit replay on a different Python/
zlib build, followed by review of the default entrypoint and its source pins.
Default integration and that additional environment remain outside this result.
