# Field-sensitive audit of PR1417 P112 graph tensors

**Scoped independent verification. No new kappa and no theorem counterexample under the target proof's stated field.**

## Finding

PR1417 claims that the 5,824 ordered edge tensors from the selected P112 ports span dimension 80 in an 81-dimensional matrix space and uses the identity form as their nonzero null vector. The rank is characteristic-dependent. Reconstructing the actual selected ports and every edge gives rank 80 over `F2` but rank 81 over `F1009`. The audit supplies an 81-by-81 pivot minor whose determinant is nonzero modulo the prime 1009, so the same integer matrix has rank 81 over the rationals and complexes.

The pinned PR1417 proof explicitly declares `F2^9` in its linear-lift statement and invokes characteristic two. The result therefore does **not** refute the theorem as written. It shows the rank-80 certificate cannot be carried over unchanged to characteristic zero. This is a field-contract result, not evidence of a larger or smaller supplier bound.

A concrete identity-form check makes the distinction visible: selected port 0 has ordinary integer self-dot 3, and graph edge `(0,1)` has ordinary integer dot 2. Modulo two these become 1 and 0, respectively, as required by the stated binary model. Across all 112 ports, the integer weight distribution is 77 of weight 3 and 35 of weight 7; across 5,824 parity-selected ordered edges, integer dot products are 0 (1,400), 2 (3,948), and 6 (476).

## Exact pins

Research/source base: `410026dc5513b87db92ae98571d1d5984c69a983`. For publication the branch was rebased onto refreshed `main` at `4040a0f46d67b41c36a472a7cd4af791fd4c36cc`; the selected certificate and all three pinned repository inputs retain identical blobs across those commits. The ports come from the selected PR1094 canonical word inside the pinned replay archive. The target is PR1417 at exact head `c755bf393bea26d2275e1516b0560ca92de7a52e`. `SOURCES.json` records Git blob IDs and SHA256 values for the selected inputs and the target proof, certificate, geometry code and verifier. The proof and certificate snapshots in this package are byte-for-byte copies from that head.

## Reproduce

From the repository root with Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/pr1417-field-sensitive-rank-seed47
```

Expected: `PASS_REGISTERED_RESEARCH_PACKAGE research/pr1417-field-sensitive-rank-seed47 outcome=completed`. The checker uses only the standard library. A nonzero 81-by-81 determinant modulo a certified prime proves the characteristic-zero rank is 81; the full theorem and supplier/cost interface are outside this audit.

## Scope and limits

This verifies the finite graph tensor ranks and the stated field marker in PR1417's proof. It does not dispute the intended `F2` result, prove that the full proof transfers to the retained complex supplier, or audit the dimension-18, all-size endpoint, 144-call cost, moment, controller, native or outer-bound arguments. No selected certificate or frontier value changes.

The initial suspicion that the binary rank was being applied over characteristic zero was rejected after inspecting the pinned proof. This is an explicit field-sensitivity control, not a failed search for a new kappa.

## Open next questions

Trace the binary-field contract through PR1417's full endpoint and Fourier-rank cost argument. That would establish whether every linear map and bilinear form in the physical-supplier interface remains over `F2`. The present package supplies exact finite evidence but does not re-derive that theorem.

## Credit

Credit Ali Romman / PR1417 for the P112 graph and field-specific theorem, and the selected PR1094 contributors for the frozen source word and archive. Prepared by Cinna Davis (@1337isnot1337) with substantial OpenAI Codex assistance in source tracing, exact arithmetic, implementation and writing. This is a code-disjoint field audit, not independent human review. The copied proof and certificate retain their Apache-2.0 source context; new material is Apache-2.0.
