# Attribution and scope

Prepared by **Wentao Li** ([GitHub: VictorLiwentao](https://github.com/VictorLiwentao),
[X: @Is__Victor](https://x.com/Is__Victor)) with substantial **OpenAI Codex**
assistance in task selection, implementation, proof explanation, tests,
benchmarks and writing. No independent human review is claimed.

Douglas R. Colkitt authored the retained historical balanced-Fano investigation,
its exact meet-in-the-middle checker, negative certificate and independent
dense controls. The preserved research documentation discloses AI assistance.
`baseline.py` is an unchanged copy of his `scripts/experiments/balanced_fano.py`
from base `66849e1475c930fd7732b1a0067ffee7e1e95f60`, originating at
`d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0`. The graph, local operations, matching
criterion, search domain, stream hashes and negative finding are predecessor
work; this contribution claims the packed-column implementation and its
performance/equivalence evidence only.

See [the original stronger-screen note](../../docs/research/stronger-rank-screens.md)
and [Fano completion audit](../../docs/research/fano-completion-audit.md) for the
mathematical context and underlying literature. No new literature theorem is
claimed or independently verified here.

The selected conditional certificate remains the separately reviewed #626
construction with eumemic's #543 bit supplier, credited to Chafik Boukhalfa,
Jeremy Kothe and the full predecessor chain in the maintainer review. Pending
verification-engineering PRs were consulted for overlap; none is a code or
mathematical dependency of this change.

All added and modified code and evidence use the repository's Apache-2.0
license. The original root license and contributor notices remain in place.
