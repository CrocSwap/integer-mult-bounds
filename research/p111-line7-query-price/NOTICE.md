SPDX-License-Identifier: Apache-2.0

The pinned word and centre seed are byte copies of Rohan Arun's PR #1525 at
`90d39a5603c7fbfd8d8d957e9732d9b6ebd6317f`, paths
`research/p111-early-merge-query/inputs/word-base.json.gz` and
`research/p111-early-merge-query/CENTRE-SEED.json`. That draft retains the
PR1297 word, the PR1134 arithmetic, and the PR1060 physical model, with the
notices in that package. Those predecessor files are not modified here.

The containment test is the same subspace test as PR1060 `model.py`. This
package reimplements that one predicate; it does not vendor or replay the
PR1060 compiler.

New checks and text: unpaidmoon, with substantial Cursor Grok assistance.
Apache-2.0. No independent human review is claimed.
