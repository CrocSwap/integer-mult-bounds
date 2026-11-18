# Credit and source identity

Ali Romman prepared this separate basis audit with substantial OpenAI
Codex assistance in implementation, checking and writing. New work is
Apache-2.0. The source proof and code were read; this is not blind,
independent human or formal-kernel review.

Ali Romman's separate workstream supplied the construction, all 33
certificates and requested cases in
[PR #7713](https://github.com/CrocSwap/integer-mult-bounds/pull/7713),
scientific commit `06b75fde21f4231a2bd0725542c3ba60a908d83b`, published
head `52e7eb424b9ae9f2e6002eb17e475bce6195d848`.
The [proof](https://github.com/aliromman/integer-mult-bounds/blob/06b75fde21f4231a2bd0725542c3ba60a908d83b/research/p104-helper-quotients/PROOF.md),
[constructor](https://github.com/aliromman/integer-mult-bounds/blob/06b75fde21f4231a2bd0725542c3ba60a908d83b/research/p104-helper-quotients/quotient.py)
and [relation checker](https://github.com/aliromman/integer-mult-bounds/blob/06b75fde21f4231a2bd0725542c3ba60a908d83b/research/p104-helper-quotients/witness.py)
were inspected. No source checker module is imported. The rational
restriction and transpose argument remain source work. New evidence
uses forward basis expansion, a separate graph implementation,
direct endpoint comparison and rank accounting.

The parent is Ali Romman's 46-cut graph from
[PR #7708](https://github.com/CrocSwap/integer-mult-bounds/pull/7708),
scientific commit `f0e2db5b5b46b139da17d2b32fab6633164443a9`, with hash
`db10e4ca7154b454f86bf404bc34b3a16d02de6cc008d5227e4eef2654cb0778`.
The retained graph and interface are derived exports, not copied
source files. Source `quotient.parent()` and `recoding.layout()` made
the export. Their raw-word and cut construction is trusted here;
the exported endpoint is checked directly.

[SOURCE-PINS.json](SOURCE-PINS.json) gives SHA-256 values for retained
inputs and original Git blobs for byte-exact copies. QUOTIENTS.json,
both application receipts, LICENSE and all supplier notices retain
their bytes. The audit history contains these inputs. Replay needs
no predecessor commit or network. Source pins identify attribution
and bytes, not ancestry. The catalogue and selected record are base
provenance in [SOURCES.json](SOURCES.json).

The [source notice](https://github.com/aliromman/integer-mult-bounds/blob/06b75fde21f4231a2bd0725542c3ba60a908d83b/research/p104-helper-quotients/NOTICE)
credits SYLforge for the nine-swap word in
[PR #7700](https://github.com/CrocSwap/integer-mult-bounds/pull/7700),
Clear1nsight for the relay and schedule in
[PR #7704](https://github.com/CrocSwap/integer-mult-bounds/pull/7704),
and DreamingOfClouds for related bank work in
[PR #7705](https://github.com/CrocSwap/integer-mult-bounds/pull/7705).
It credits Rohan Arun for the signed caller, Jerry Chen / CubeJerry
for the selected complex and BIT application, Douglas Colkitt and
repository contributors for the framework, and mightyOil for the
concave comparison. All supplier notices remain under credits/.
Related constructions and gains are not counted as audit results.

The neighboring [PR #7712](https://github.com/CrocSwap/integer-mult-bounds/pull/7712)
uses another helper interface. Its splits are not composed with these
restrictions. No other workstream's claim or PR is changed.
