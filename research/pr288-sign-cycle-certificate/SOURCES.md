# Immutable sources and numerical normalization

- Host integration base: CrocSwap/integer-mult-bounds
  `12a4934d15006e8c10f9b2264f13f8f341be802b`.
- Existing obstruction and original checker: eumemic,
  [PR288 §1.4(d)](https://github.com/CrocSwap/integer-mult-bounds/pull/288),
  source head `475a088b5862f75f0b10596cfd6842d19531a5ec` in
  [eumemic/integer-mult-bounds](https://github.com/eumemic/integer-mult-bounds/tree/475a088b5862f75f0b10596cfd6842d19531a5ec/research/negative-results-paradigm-search).
- Graph and numerical lists: Mark Braverman and Zhongtian He,
  [arXiv:2610.10108v1 §4 and Appendix A](https://arxiv.org/html/2610.10108v1).
- Corroborating numerical data:
  [companion repository](https://github.com/zhongtianhe/multiple-unicast-counterexample/blob/3436359a85d13a1bf6e87c3a3dbdaa64788277f4/data/182-vertex-code.json)
  at `3436359a85d13a1bf6e87c3a3dbdaa64788277f4`, data Git blob
  `d84f5b3996d5e3b8bf886dfde4fde6bfc02981ca`.

PR288's `data/bh_pg29_lists.json` has Git blob
`056b3ccbb37584b5214c2db12fc65c2ab5b41b86` and SHA-256
`0e950af1a3aa07b12377780c8a82f9de97bef6f7f048a82c60c3312b0f6c5c77`.
Its R list has 176 entries with a final 13. The original checker explicitly
omits that paper page number. `instance.json` records the 175 actual indices,
the complete 182-entry π permutation, and disjoint nine-entry C and J sets.
All four lists agree with the primary paper and pinned companion data in
the independent preparation audit. This normalization is not a newly found
failure of PR288.

The normalized input SHA-256, including whitespace, is
`06f62ef3c3b5448a67fd1b8ff1edf69012f6aa07c7dd60b1f3c83baa5343dabb`.
The verifier hard-pins that value and requires the certificate's hash to
match it. The distributed certificate SHA-256 is
`12a627a89864b90ed611d156520b7c5213566f405554ea08fb1361a4bf54ae0f`.
These pins identify reviewed inputs; checking them is not a fresh remote
provenance audit or a proof of the paper's theorem.

The graph field is F₉=F₃[t]/(t²+1). Matrix ranks and traces are over Q.
Point-to-line session orientation replaces the paper's π orientation by a
bijective relabeling of independently free signs. No symmetry of unknown
vertex matrices is assumed.

PR288 remains the predecessor and receives theorem credit. This package
adds a compact four-constraint witness and independently written checking
code. A bounded PR title/body and term search through #343 found no compact
duplicate; it establishes neither worldwide novelty nor exclusive ownership.
The companion's source code and the full paper are not redistributed.
