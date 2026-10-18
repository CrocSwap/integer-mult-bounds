# Attribution and license

Prepared for @MrPink604 with substantial OpenAI Codex assistance in task
selection, implementation, proof explanation, tests, measurements and packaging.
No independent human review is claimed. New files are Apache-2.0, as is the
repository; see the root LICENSE.

`vendor/exact_rows.py` is byte-for-byte Aman's PR367 implementation from
`522285db971642c2d744cc8d45f2a5ade3a55e19`, originally
`research/frame-algebra-performance/exact_rows.py`. It credits substantial
OpenAI Codex assistance and is Apache-2.0. That contribution optimized Chafik
Boukhalfa's PR364 helpers; this contribution reuses its arithmetic and claims
only the R420 integration/evidence described in README.md.

The original R420 checker, mutation harness, word and interleaved scalar-interface
lemma are eumemic's PR543, with substantial Anthropic Claude assistance. They are
read in place and unchanged. The R420 work builds on eumemic's PR493, the
DreamingOfClouds R480 work and the E8/compiler/official-checker lineage, including
Dylan Crow and Zhihao Chen's PR425 interface. The existing R420 README and the
repository NOTICE retain the complete construction and analytic credits.

The selected #626 composition is Chafik Boukhalfa's owner repair on Jeremy Kothe's
#622/#623 construction, with eumemic's #543 bit supplier and the retained
predecessor lineage. It is context, not a new result of this adapter. Douglas
Colkitt's current maintainer review identifies its remaining assumptions.

Concurrent #709 (geometry caching), #707 (Gram determinant prefix reuse) and
#662/#667/#672 (other exact kernels) are related verification work. None of their
code or benchmark evidence is imported or composed here.
