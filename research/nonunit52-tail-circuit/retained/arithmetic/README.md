# A reversible arithmetic step for the paired denominator-13 sampler

**Scoped construction with an exact finite certificate.** One draw of the
fixed (1/13, 1/13) sampler uses **3,060 reversible Boolean gates** and
**484 clean work bits**. The circuit replaces the 702-byte transition table
for that pair with arithmetic on an eight-bit phase residue and a two-bit node
index. A separate bit marks termination. The coin is read-only. Every
reachable step clears its workspace, and the reversed gate list recovers the
input packet.

| Per draw | Count |
| --- | ---: |
| X | 232 |
| CNOT | 2,238 |
| Toffoli | 590 |
| Temporary Boolean wires | 473 |
| Clean packet backing bits | 11 |

The gate and workspace counts include copying, swapping and uncomputation.
The table saving refers to stored transition data. The fixed circuit still
requires a gate description or implementation. This circuit count does not
price tape movement or establish a runtime improvement over a table scan.

## Proof and reproduction

[PROOF.md](PROOF.md) gives the phase calculation and local inverse. The
verifier compares the emitted gate list to a specification using differences
of integer floors. It checks all 624 reachable input packet and coin pairs in
both directions, including continuation, termination and period wrap. It
rejects a wrong stopping flag and dirty workspace.

From the repository root, using CPython 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/paired-ddg-arithmetic-step
python3.12 -B scripts/check_research_commit.py --package research/paired-ddg-arithmetic-step --check-source-history
python3.12 -E -s -B -W error -X dev research/paired-ddg-arithmetic-step/verify.py
```

The direct verifier prints `PASS_PAIRED_DDG_ARITHMETIC_STEP` and the exact
bill. The registered manifest runs it in normal and optimized modes.
Local verification used CPython 3.12.15.

## Scope

The proof fixes the source sampler's output order and treats one draw.
Induction gives the same output and first stopping depth on every ordered coin
path when the circuit is used from the root. The sampler still has unbounded
stopping time. A complete tape implementation would need a cursor, a stopping
record, output retention, and a bill for their initialization and cleanup.
The fixed phase computation does not supply those operations or conditional
freshness after the output is retained.

This local step addresses the first tape/table service obligation raised by
PR #6102. It changes the supplier-boundary card to a gate-level operation that
precedes caller pricing. Native and caller replay, the selected cold replay,
Lean and Docker were outside the scope. No new κ follows.

## Open next questions

- Can a fixed-tape caller realize the local gates and reverse the walk with a
  complete movement bill? Start with the cursor and counter layout in #6102,
  then charge every scan and cleanup operation for a terminating path of
  length T. A tape layout and an owned stopping record are needed.
- Can one arithmetic circuit accept the two residue parameters at entry?
  Start by generating the four weight residues from the shared phase. Meter
  the parameter preparation and compare against the resident and on-demand
  table options. The fixed-weight shortcuts here do not price that setup.

## Credit

This result was produced by Nick Petalas. Apache-2.0. zxv's [PR #6072 at
`9011bf83e85ecd0443c789cf03259442f750877d`](https://github.com/CrocSwap/integer-mult-bounds/pull/6072)
supplies the paired graph, ordered-coin semantics and probability law.
JoyboyBrian's [PR #6102 at
`0422af13625c2e7e8ece28bdd74364a61764c64a`](https://github.com/CrocSwap/integer-mult-bounds/pull/6102)
supplies the reversal context and the open tape/table question. The
denominator-13 inverse lineage is JoyboyBrian's #5069/#5037. Decision graphs,
modular arithmetic and compute-copy-uncompute are classical. The new
contribution is the shared-residue arithmetic and the gate-priced reversible
step. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19718460)
