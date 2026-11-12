# Independent review of the encoded CRT endpoint join

**Outcome: PASS for the declared source-model, one-lifecycle address-state
theorem.** No substantive defect was found. This does not discharge
`analytic_recovery`, certify payload routing, or certify a complete binary
machine tariff. It establishes no new kappa.

Reviewer: compiler/source-index worker, independently of the CRT package
author. Prepared for Jerry Chen / @CubeJerry with substantial OpenAI
assistance. Canonical base is
`e54523517d0f03e58352e647c403a5af3e525a57`.

## Reviewed bytes and dependencies

- `endpoint.py`: SHA256
  `c24ae2c90d175d276120438809e7c7401b8a8c04dec139f1b7345e9778984ced`.
- Updated `PROOF.md`: SHA256
  `a20c90aada4ea2d9141a465b10bd1d54a1047b52608bb19c88efa7fd98eeacf3`.
- Read the complete new endpoint, numerical producer, persistent bank,
  guide-driven numerical entry, frontend iterator and its node/lease
  classes. Also read the source-model word/record APIs and relevant
  predecessor iterator and whole-state composition proofs.
- All seven source files independently matched both SHA256 and Git blob
  pins in `INPUT-PINS.json`. The frontend dependency is the explicit
  CubeJerry fork commit `cc35ecedce6f208d5056fab6d17c58555affc73c`, blob
  `8adbe2cfef74da9854ed0b70b6c221f5746efa9f`; it is a pending contribution,
  not silently treated as merged canonical code.

No author files were edited during this review. The proof hash differs
from the initial review assignment because its author clarified the
staging boundary-cell accounting before the final review snapshot.

## Mathematical assessment

### 1. Source mutation is compatible with the iterator

The persistent topology contains the axis count, balanced level, half-size,
current STEP and pending VALUE markers. These are derived from record
framing and never from coordinate values. The numerical precision is
manufactured afresh by scanning unary width headers in the selected node.
The commit preserves all such headers, moduli, delimiters, record count,
logical length and historical backing. Therefore none of the iterator's
cached topological facts is invalidated. Each subsequent node projection
reads the updated coordinate bits from the actual source rather than
reusing old arithmetic payload.

At a handoff the width counter is clean at head one, so staging can reuse
it. Its full-source pass restores axis, half-size, source, guide and result
heads before close. Closing is permitted to advance or entirely retire
the topology: commit subsequently uses only source and staging. The final
node is thus covered without trying to read a retired cursor.

### 2. Numerical projection and padded inputs

For a valid left child, the independent defining residues are
`x_i * product_(a<=j<i) s_j (mod s_i)`. The numerical producer's running
reconstruction satisfies those congruences and is below the product of
the left moduli. If any left coordinate is padded-invalid it sets the
whole lower value to zero. For each right axis, the prefix includes every
previous modulus, including a modulus whose coordinate is invalid.

The right update rotates the valid interval modulo its modulus and fixes
each invalid padded coordinate. Both branches fit the declared field
width. The endpoint skips the offset, copies precisely the declared low
bits of the updated word, and rejects a nonzero upper part before commit.
It does not reapply validity decisions to individual intermediate Beneš
switches. This is consistent with the inherited padded rotation endpoint;
the inherited micro-row routing theorem itself is not re-proved here.

Nodes at a fixed level have disjoint read/write groups. Their endpoint
maps commute, justifying the change from row/node order to complete-node
order. Between levels the prescribed order is retained. This proves the
state endpoint claim without asserting agreement at intermediate rows.

### 3. Source leases and retained histories

During staging the source is read-only. Its numerical result is consumed
only while the current lease is live. `lease.close()` erases the numerical
outputs and releases the owner before `commit()` performs a source write.
The commit guard checks both iterator liveness and bank ownership. The
staged source has identical length; commit leaves the final RIGHT and the
entire inaccessible source tail unchanged.

Every newly used staging cell is erased on success, including its LEFT
marker. The numerical and guard histories retire at every node; topology
histories retire on final completion. The theorem requires the stated
linear-use protocol and initially clean private backing. It does not
promise rollback following a failed precondition or support stale aliases.

### 4. Cost and capacity

The adapter charges a complete source scan/copy and commit/erase for
every node, full-precision scans of right outputs, width manufacture and
erasure, and every cursor/guide/result return. No numerical call or
retirement is cancelled merely because physical roles are reused.

The identity
`sum_G n_G(P_G+2)=3d log2(d)+2A(d-1)` follows level by level: a level of
node size n contributes `3d+nA`. Together with `(d-1)M` source copies,
this yields the stated quadratic adapter overhead. For near-equal widths,
the inherited numerical fourth-power sum is `O(A^4)`. The complete-control
multiplier remains an unspecified input-independent constant, as stated.

The staging backing has exactly M cells in the test model, but its head
visits index M after appending/clearing RIGHT. A literal visited-span
measure is therefore M+1. The updated proof explicitly makes this
distinction and does not infer a binary-tape space theorem from backing
length alone. The source's historical tail is included through K_source.

## Independent executable evidence

Reproduce from this package directory:

```sh
python3 -I -W error -B independent_check.py . > independent-result.json
```

The checker imports the pinned implementation modules directly; it does
not import, invoke or copy the author's `verify.py`. Its numerical oracle
uses the CRT idempotent sum, a different arithmetic route from the
producer's digit reconstruction. On globally valid inputs it also checks
the independent full mixed-radix closed form, which uses no tree updates.

Observed result: **18 cases, 46 numerical nodes, PASS**. Cases include
2-, 4- and 8-axis trees; widths through 9; alternating declared widths;
each possible invalid axis position in four-axis examples; multiple
simultaneous invalid fields; and an inaccessible tail containing hostile
LEFT/RIGHT/record symbols. Every node checks the actual precision guide,
STEP/VALUE location, topology restoration, source bytes outside coordinate
fields, bank/guard/staging retirement and the per-node adapter action bill.
At termination it checks all 79 owned histories blank at head one. A
mutation committing stale coordinate bits fails the independent endpoint
comparison. Complete tested source hashes and per-case measurements are
in `INDEPENDENT-RESULT.json`.

These finite tests detect implementation failures and reinforce the
symbolic argument; they are not the universal proof or an asymptotic
experiment. The universal claims depend on the stated source contracts.

## Residual obligations

The package is a useful uniform endpoint composition. Its declared scope
still excludes the actual caller's encoded source production, payload
routing/micro-row selection, reverse scheduling and the complete binary
machine refinement. The pending frontend dependency and inherited
numerical/rotation contracts must remain explicit in publication.

## Root integration review

The orchestrator independently read the complete adapter, author verifier, proof and this review. The staging boundary-cell clarification was accepted before freezing the core. Publication changes only packaging, the independent checker's default path and documentation; the reviewed endpoint and proof bytes remain unchanged. Strict author and independent checks were rerun from this self-contained package. No complete selected-certificate replay is claimed or needed for this isolated enabling lemma.
