# Reproduce the frozen source export

Use the source tree of PR #7716 at
`1636b3c9b922d23b222b60dd52e005e60c592491`.
Import its verify.py from research/quotient-causal-split-composition.
Read compact.json.gz with read_graph. Read interface.json for keep and main_roles.
Read source-split-circuit.json.gz with read_graph. For each record from
literals(source), call construct with the current graph, that record,
the compact main_roles and keep.index(record["role"]). Use the returned graph
as the next input. Do this in the supplied order: chart 498, then chart 595.
Call basis_engine.layouts with the final graph and the compact frame list.
Its canonical JSON hash is
`5183479ecac34a1cb5c046f202e19d7161679265fe121b4a0af922fe344d8fc1`.
Compress that JSON into data/GRAPH.json.gz.

For data/LAYOUT.json, retain live and ports from data/WORD.json.gz
in PR #7713 at `06b75fde21f4231a2bd0725542c3ba60a908d83b`.
Copy its hosted record and replace each label r in X2 and Y2 with
keep.index(r). The other hosted fields stay unchanged.
Use the graph frame list, set public to 1470 and set source_labels to
keep followed by 1501 and 1503. These labels identify fresh distinct
helper owners; they are not accesses to the old 1501-field array.
The first-plane main labels stay unchanged. The 192 hosted second-plane
labels move with the compact interface. common.py checks their charts,
hosted partners, signed stage owners and the two protected helper boundaries.

This export used the source constructor. It is not an independent graph
construction. The constructor is not imported during package replay.
The stored hashes bind the exported bytes, while the physical basis replay
checks all 1470 endpoints against the explicit caller interface.
The normalized source proof and its faulty-construction controls remain
in PR #7716. Their result is not counted again here.
