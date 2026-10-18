# Attribution and license

Prepared for **Sagar Thakrar (@thakrarsagar)** with substantial **OpenAI Codex
assistance**, including separate workers for the written proof and independent
verification. New code and documentation are Apache-2.0 under the repository's
root [LICENSE](../../LICENSE). No independent human review is claimed.

- **androolloyd**, [PR #673](https://github.com/CrocSwap/integer-mult-bounds/pull/673):
  the multiway dirty echo, its nonlinear restoration identity, recursive
  instruction generator, and precision/resource argument. Its full-transform
  experiment supplies the scoped negative result for a direct all-role adapter.
  `vendor/pr673_echo.py` retains the exact source, including its AI disclosure.
  `optimize.py` adapts that emitter to an explicit ordered tree; this package
  contributes the interval optimization and its independently checked witnesses.
- **Dillon Amburgey (@dillona)**,
  [PR #689](https://github.com/CrocSwap/integer-mult-bounds/pull/689): the minimum
  among recursively balanced ternary splits with uniform leaf costs, and the
  corrected baseline used here. The result at 15 factors is credited to #689;
  this package's savings at 27 and 56 factors use a larger, explicitly scoped
  tree class. No claim of priority over general alphabetic-tree optimization
  algorithms is made.
- **Chafik Boukhalfa (@chafreaky)**,
  [PR #628](https://github.com/CrocSwap/integer-mult-bounds/pull/628), head
  `0768f97d06c623b8211e651543c66135796b62bf`: the rounded cyclic-inverse leaves,
  balanced binary dirty commutator, and inherited preparation/precision
  contracts. Those analytic and numerical implementations are not re-audited
  or copied here. Their cited mathematical predecessors retain their credit.
- **0xkilgore**, [PR #663](https://github.com/CrocSwap/integer-mult-bounds/pull/663),
  head `e0e546fd01b396478c68b6b6c5a16d87515983ba`: independent nonlinear
  restoration audit and the exact count for the balanced binary dispatcher.

[SOURCES.json](SOURCES.json) records exact source commits, SHA-256 hashes and
Git blob identifiers. The checker needs no network or pending-PR checkout.
Only the vendored echo is an executable predecessor dependency. The other
pins document comparisons, mathematical dependencies, and the selected-result
context at the base commit.

The accepted #626 construction remains credited to Jeremy Kothe's K-triangle
construction and the complete supplier/owner-allocation lineage in the
[maintainer review](../../docs/research/community-k492-review.md). This local
interface research neither alters that construction nor establishes a new κ.
