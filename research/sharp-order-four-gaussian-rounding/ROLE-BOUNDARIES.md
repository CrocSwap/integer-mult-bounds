# Roles and independence boundaries

- Root proposed the annular matching and 36-vertex boundary mechanism, then
  wrote review/root/check_candidate.py before reading the other checkers.
  Root independently reviewed the all-candidate color-domain reduction and
  wrote review/root/ROOT-PROOF-REVIEW.md.
- The proof role derived the all-candidate reduction from F^2=swap, checked
  lower and upper proofs, and generated bounded ring dictionaries. It saw
  an earlier root conserved-map reference to fix conventions, disclosed in
  proof/SOURCES.json, but did not import it or the other worker's code.
- The constructive review independently implemented the annular formula,
  checked arbitrary rings/identities/radial bounds, and proved the lower
  bound within the equivariant matching class. It did not read either the
  root or proof-role implementation and explicitly excludes the arbitrary
  map reduction.
- The publication cross-check compares these implementations after the
  original freezes. This is regression/cross-implementation evidence, not
  an additional independent mathematical proof.

All roles are AI agents in one coordinated session with a shared proposed
formula. No human, blind or formal proof-assistant acceptance is claimed.
The original frozen packages and notices are copied unchanged; no worker
performed remote publication.
