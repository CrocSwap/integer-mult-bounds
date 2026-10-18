# Attribution and scope

Prepared for GitHub user @woklerx with substantial OpenAI Codex assistance.
New audit code and exposition are provided under the repository's
Apache-2.0 license. No independent human or proof-assistant review is
claimed.

The unchanged selected PR589 tuned word and PR555 punctured word chain
are credited to their original authors, including eumemic and the
disclosed Anthropic Claude assistance in the source adapter. The original
source word, all data and predecessor implementations are unmodified.

`export_records.py` is Dylan Crow's exporter with disclosed Anthropic
Claude assistance. `global_k.py` credits DreamingOfClouds's generalized
odd-stage schedule (with Claude Opus 5.5 assistance), chafreaky's kernel
integration and replication extension (with OpenAI Codex assistance),
and Zhihao Chen and eumemic's PR386/436 geometry lineage. Those comments
remain in their original source files. PR463/510 provides the consumed
nine-stage pipeline; `adapt9p.py` specializes it to the punctured unit.

This package imports neither predecessor search nor pricing routines.
It calls the credited exporter and evaluates the pinned recipe and
prefix expression, then independently propagates the finite scalar
program and its three-coefficient bounds. Source text hashes normalize
CRLF to LF; the gzip word is pinned by its exact file bytes.
