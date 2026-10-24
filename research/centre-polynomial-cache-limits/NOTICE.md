# Credit, source pins, and limits

The source is the historical selected construction at commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Its selected archive is
[retained here at the source commit](https://github.com/CrocSwap/integer-mult-bounds/blob/bce54fb3f895cbe5cd4c0eb477c3afeed100190f/research/community-frontier1042-audit/selected-replay.tar.gz).
The two needed archive members are copied without edits. Their original
compressed digests and the complete archive digest are in SOURCES.json.

The original supplier notices are retained under `notices/`. They identify
the source work, compiler work, and earlier contributor lineage. In
particular, the [Gauge44 notice](https://github.com/CrocSwap/integer-mult-bounds/blob/bce54fb3f895cbe5cd4c0eb477c3afeed100190f/research/gauge44-slots-t16/NOTICE.md)
credits icekylinx and retains the upstream notices. This package does not
infer contributor identity from a PR submitter account.

The circuit-interface lane derived the actual R. The history-encoding
lane supplied the Bell certificate. The interface-proof lane supplied
the separate sparse replay, the all-size extension, and the inverse
corollary. The native-encoding lane supplied the scalar-cache theorem.
These are OpenAI Codex research roles under Ali Romman's direction.
They are not independent human authors or reviewers. Substantial
OpenAI Codex assistance was used for research, checks, and packaging.

[PR #1719](https://github.com/CrocSwap/integer-mult-bounds/pull/1719)
published the historical doubled Walsh lift at commit
`3ae9a6f3ac74ded022ab3b4872a7357a621af6fb`. This package uses the doubled
port representation to study one weighted Gram; it does not re-publish
that lift as a new construction.

The actual query source is already retained by
[PR #4720](https://github.com/CrocSwap/integer-mult-bounds/pull/4720) at
[this exact source path](https://github.com/CrocSwap/integer-mult-bounds/blob/cb102a57254748651ce16aa4454bb611f6380e53/research/actual-query-information-bounds/payload/lanes/circuit-interface/INTERFACE.json).
That PR also publishes the separate scalar source-span theorem.
[PR #4750](https://github.com/CrocSwap/integer-mult-bounds/pull/4750)
publishes the [fixed-code projector criterion](https://github.com/CrocSwap/integer-mult-bounds/blob/3c6a768e5391e6bc8355fe2bc849d2978afef8f6/research/phase-coded-callers/annexes/fixed-code-interface/PROOF.md).
The new package does not claim those results again.

The 22 October cleanup audit found these two notes outside the fixed
469-observation closure. It checked the exact published source objects
and found no equivalent adopted statement in the 15 campaign packages.
A bounded source search is not a universal literature novelty check.

Apache-2.0 applies. Original notices and license text are unchanged.
