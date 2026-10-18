# Notices and attribution

The decoder fixture `P104_HIT_flip_3a.txt` is the byte-pinned PR717 hit authored by DreamingOfClouds, sourced from PR717 head `4a97676294f9fa413b65986e9984fddeda71e4cc`. Its original Git blob and SHA-256 are recorded in `research/complex-frame-pair-decoders/SOURCES.json` and in this package's `SOURCES.json`.

The exact E8 line and support-pair label model is reused from `research/complex-frame-pair-decoders/verify.py`; the local moment engine is reused from `research/complex-local-word-ceiling/ceiling.py`. Their source pins are recorded in `SOURCES.json`.

Mathematical and predecessor credit:

- PR717 / DreamingOfClouds: the exact P104 decoder hit and original decoder model.
- PR968: frame-pair structure and the exact eight-term P104 copied-information floor.
- PR1071, head `ce9531beba1ce115fdcdc44925ded995a29b8bac`: delivery lower bounds for the pinned frame-pair decoder.
- PR1125, head `9f7c0679d64bab954b7161d8586dc626a59b92ee`: asynchronous delivery bounds over the frame-pair family.
- PR1240: the fixed-word packing ceiling and exact local moment screen.
- PR1619, head `6c96bc1a0e374a713e9ae493228247f49be49dd5`: port-count and puncture-depth planning bounds; its result is not imported as a certificate input.

New files in this package are Apache-2.0. Prepared with substantial OpenAI Codex assistance; no subagents and no independent human proof review are claimed.
