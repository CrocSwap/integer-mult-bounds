# Local recovery trail and author verification checkpoint

Base: e54523517d0f03e58352e647c403a5af3e525a57.
Branch: research/continuous-20261110-bit-history.
Package: research/fixed-dimension-bit-coefficients.
Initial WIP commit: aaca699b. It was explicitly unverified and not offered for
publication. The later author checkpoint below supersedes its draft status;
no selected result is updated, and independent review is a separate gate.

Implemented: 17 authenticated specialization sites over the four #6903
encoded numerical modules; one exclusive four-tape continuation Workspace;
explicit source-arena/record historical bounds; separate small-block modular
oracle and pre-guard demand observer.

Executed coverage before this checkpoint:

* N=2,w=1,depth 0: exact coefficient 2; residue/index pending 28/11.
* N=3,w=2,descriptor GUPG: coefficient 8; pending 59/18.
* N=65,w=2,depth 0: coefficient 8; all 4,225 field digits read; pending 16,912/11.
* N=130,w=1,depth 0: coefficient 2; target row 129 crosses the historical
  multiplier cap; all 16,900 field digits read; pending 67,612/11.
* Earlier exploratory controls rejected insufficient capacity, a wrong global
  field code and a truncated field. A GUPG call repeated four times used the
  same four continuation Tape identities and retained erased backing.

At the initial WIP checkpoint the proof was a draft. Missing then:
the final registered verifier/receipt, full boundary-control suite, complete
package metadata/attribution/overlap report and independent review. The
selected source label generation, root-size map, literal table lowering and
changing-precision physical bank are explicitly outside the proved seam.

Reproduce one current positive fixture:

    python3 -B research/fixed-dimension-bit-coefficients/check_consumer.py

Next command after completing the verifier:

    python3 -B scripts/research_package.py --package research/fixed-dimension-bit-coefficients

The initial scaffold verify.py intentionally exited DRAFT. That scaffold is
now replaced by the actual read-only verifier.

## Author verification completed after the WIP

The final registered normal/optimized replay passed fourteen positive cases,
ten runtime controls and the isolated Git-free three-corruption suite. The
typed mathematical receipt digest is
`afd86ba5470b877b6cad58a86fe26a58d98bb7e81129be4f1db47fd1a285a39a`.
Exact executed commands and limitations are in VALIDATION.md. Added tests
include N=44/rank43, a halved Unit, a dead earlier global-code mismatch,
full warm erased slots and normal exclusive Workspace reuse.

The supported entry is Workspace.open. The untouched legacy selected_offset
wrapper does not pass borrowed stack roles and is outside the contract.
Review clarified the linear current-handle contract: closed/aborted callbacks
cannot be reused after a later open, and no physical stale-generation service
is claimed. This changes the stated scope only; numerical source and receipt
are unchanged.
Scientific proof and implementation are frozen for independent review; only
explicitly reported review fixes should change them. Root coordinates review,
publication and a separate durable recovery-branch snapshot. No push or PR
creation is performed by this worker.

Next action: integrate the independent review if it passes, rerun affected
registered checks and the committed-byte preflight, then let the root publish
the verified package. In parallel this worker cross-reviews the separate
encoded-balanced-crt-entry package under the root's Wave-2 assignment.
