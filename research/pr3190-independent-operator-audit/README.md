# Independent exact audit of PR #3190's port-0 transfer witness

**Scoped finite result. No new κ, supplier bound, or multiplication theorem.**

## Result and exact scope

At owner replica 0, port 0, the pinned PR #3190 move list contains exactly two transfers:

- child 14 to child 8, axis 2^72;
- child 15 to child 10, axis 2^72.

Using the selected frame recipe and completed local-invocation event contract at the single Fourier character 2^72, an independent dense matrix replay gives the baseline operator i I₈. Each transfer alone changes exactly five matrix entries; the joint transfer changes the disjoint union of those ten entries. For example, entry (6,6) changes from i to −1 under 14→8, and entry (7,7) changes from i to −1 under 15→10.

| Isolated transfer | Exact changed entries, before → after |
| --- | --- |
| 14→8 | (3,1): 0→−1+i; (3,3): i→1; (5,1): 0→−1+i; (5,3): 0→1−i; (6,6): i→−1 |
| 15→10 | (0,2): 0→−1+i; (0,4): 0→−1+i; (2,2): i→1; (2,4): 0→1−i; (7,7): i→−1 |

This independently reproduces the port-0 counterexample in [PR #3296](https://github.com/CrocSwap/integer-mult-bounds/pull/3296). It establishes that these two literal transfers do not preserve this finite operator under the stated contract.

It does **not** establish that every move in #3190 fails, that every port or replica fails, that simultaneous or repaired transfers fail, or that the broader remainder-transfer mechanism is impossible. It changes no selected result and gives no bound on κ.

## Inputs, method, and assumptions

The package pins eight base data inputs and the task-catalogue/selected-result provenance records in [SOURCES.json](SOURCES.json); its nine offline copies are separately bound by SHA256 and Git blob IDs in the retained-file inventory. The selected base is main commit 463113d675af7410ac91d53a4fed51ec6494eb9a. The move-list Git blob is e8401e6d138d9fcf9725530e7ae36d2db1386bda, pinned locally to parent package commit 32a3fa83aaa639570db53beb381016711aa6f5b5 so the repository replay can resolve it from the PR branch history. Before opening this PR, GitHub's blob API reported the same object ID at PR #3190 head 5e4a3235169edddd033889da4e9f47635ff50c3e, path research/rank7-idle-remainder-donors-t740/MOVES.json.gz; PR #3296 carries the identical bytes. SOURCES.json retains both the local pin and the observed upstream head/path/blob.

The verifier does not import PR #3187's algebra.py or source.py, nor PR #3296's obstruction.py. It checks every vendored SHA256, reconstructs the 2,717,280-row fill from its base rows and exchange journal, verifies the canonical fill digest, and independently projects the 30 owner-0/port-0 hosted rows. It then applies the declared per-axis rule, rank cap, and orthonormality checks, and composes the event gates as dense 8×8 matrices over the Gaussian integers. The exact 5+5 entries above are compared, including an empty-overlay positive control and invalid-axis/self-transfer rejection controls.

The operator interpretation follows the repository's completed local-invocation contract and pinned execution schedule. As in that contract, bank-padding events remain outside these eight streams, and the all-family translation correction is zero at identity gauge. This replay does not independently prove that the contract models a more general computation or that every omitted system-level obligation is discharged.

The task picker first suggested independent-moment work, but live overlap checks found active #2979 audits. This package records a changed scope: a bounded independent audit of the newest open, unreviewed #3296 port-0 operator claim. It does not extend the overlapping #2979 moment work.

## Reproduce

From the repository root, run:

    python3 scripts/research_package.py --package research/pr3190-independent-operator-audit --check-only
    python3 scripts/research_package.py --package research/pr3190-independent-operator-audit

The second command runs the registered bounded verifier. It uses only the Python standard library. The package metadata check verifies source pins and declared tracked inputs; the verifier checks the complete fill digest, exact move identity, and exact matrix differences.

## Open next questions

Can a proof covering simultaneous transfers, all 112 ports, and every owner-replica hosting show that no legal remainder-transfer family preserves the local operator? That would bear on whether the transfer mechanism has any valid form beyond these committed moves. A first step is to express the transfers as character-dependent phase changes on child pairs and classify how the intervening bridges can conjugate or cancel them. The present package checks one port and one character; the complete classification and simultaneous-transfer proof remain open.

## Credit

Prepared by OpenAI Codex with substantial AI assistance, disclosed in TASK.json. Source and lineage credit remain with the authors of [PR #3148](https://github.com/CrocSwap/integer-mult-bounds/pull/3148), [PR #3187](https://github.com/CrocSwap/integer-mult-bounds/pull/3187), [PR #3190](https://github.com/CrocSwap/integer-mult-bounds/pull/3190), and [PR #3296](https://github.com/CrocSwap/integer-mult-bounds/pull/3296). No human or formal mathematical review is claimed. New work is Apache-2.0.
