# Attribution and license

New material is prepared for Ali Romman (@aliromman), with substantial
OpenAI Codex assistance in the derivation, implementation, tests, and text.
One AI agent performed this work. The separate exact arithmetic paths are
not independent human review or a formal proof of the full theorem.

The new files use Apache-2.0. The retained predecessor files keep their
original notices and source pins in `SOURCE.json`.

- Rohan Guliani (@Rohansguliani), PR846, supplies the Euclidean chain and
  closure decomposition and its linear-tape clean-storage solver. This
  submission uses that decomposition and supplies a separate dirty transport
  proof. It does not reuse the clean queue or its traffic constant.
- Chafik Boukhalfa (@chafreaky), PR628, supplies certified factor data,
  paid coefficient and phase preparation, rounded integer lifts, and the
  balanced dirty commutator. Its unchanged checker and dense solver check
  the original kernels here. Its original dirty proof supplies the
  conservative full-word perturbation argument.
- Charles Bethin (@cbethin), PR764, supplies the shared-suffix estimate used
  in the weighted error argument, also used by PR846. No PR764 code is used.
- Ali Romman, PR621, supplies the uniform cyclic inverse bound and retained
  kernel lineage. PR628's notice credits the pinned OpenAI exact-DFT
  preprint, classical Newton and q-Pochhammer factorization, Alexey
  Kuznetsov, and the cited preparation and filtering methods. Those credits
  remain applicable. No priority claim is made for those methods.
- 0xkilgore's PR663 independently audits exact restoration and the binary
  leaf count. PR673, PR689, PR730, PR744, and later echo work study other
  tree and scratch contracts. The present source reuse acts inside a leaf.

The overlap check also read Chafik Boukhalfa's PR862, PR905, PR929, and PR951,
Gareth Davidson's PR877, Wentao Li's PR805, and Chafik Boukhalfa's new
PR977. PR977 improves the precision of the clean solver. Ross Richardson's
PR982 borrows outputs for a different fanout interface. These results supply different
precision or storage results. They are not implemented, benchmarked, or
combined by this package. Their inspected heads are recorded in CLAIM.json.

No literature-priority, new kappa, selected-supplier, production-speed,
bit-reversible compiler, or complete multiplication theorem claim is made.
