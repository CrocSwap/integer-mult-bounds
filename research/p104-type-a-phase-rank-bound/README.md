# Type A phase-rank bound for one QUERY replacement

**NO VERIFIED GAIN.** All 68 alternatives require a phase difference
of exact rank three. The retained Type A J provider has rank two, and
invertible q-even left and right adapters preserve that rank. The bound
allows adapters to move the active input and output images anywhere
within the same port.

The corpus fixes the exact [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
and [#7277 invoice](https://github.com/CrocSwap/integer-mult-bounds/pull/7277)
at head ed090b57ed88f8859e5ff4643645099e6ba856ea. Each alternative
replaces one of four literal Type A QUERYs with the same-clock ordinary
ADD and changes one of 17 literal Type A J blocks. All other operations
stay fixed. The paid and productive invoice has 110,536 paid jobs and
22,461 productive fields, including all 17 native word copies. Deleting
one QUERY grants exactly 96 rank-one child credits across the 96 Type A
ports before new costs. Each alternative is priced separately. The
compatible saving upper after the rank obstruction is exactly zero.
The comparator remains κ = 0.003645669928698.

[Proof](PROOF.md) gives the unique required provider, the fixed-role
exclusion and the phase-rank obstruction. The original four-role test
excludes all 68 cases. The full rational rank replay and the modular
minor replay independently make 68 rank-three decisions. The replay
also checks every modular minor against exact rational entries on the
same row and column indices. There are zero unresolved cases in scope.

## Replay

From a clean checkout, use CPython 3.12 with assertions enabled.

~~~sh
python3.12 -I -B research/p104-type-a-phase-rank-bound/replay.py
~~~

No external downloads or prior output are needed. LOCAL-PINS.json
authenticates all bundled inputs and frozen receipts by path. The
upstream byte and Git blob provenance is recorded separately in
PROVENANCE.json. Replay rebuilds the directed price before support,
matches the frozen scientific receipts byte-for-byte and cross-checks
the 68 pairs of exact and modular decisions. Expected output starts
with PASS_TYPE_A_QUERY_PROVIDER. The registered command is in
VERIFY.json.

## Open next questions

- Can a single already-paid provider supply the required rank-three
  phase difference at a favorable fully charged price? Pin one proposed
  provider and one of the certified matrices, then price its signed
  arbitrary-input action and dirty restoration before a literal build.
  The complete compiler, precision, tape and caller proofs remain open.
- Changing several provider clocks, cross-port mixing, moving the
  deleted QUERY and changing the Type A port or phase contract all
  require their own scope and price analysis.

The earlier [fixed-J result #7309](https://github.com/CrocSwap/integer-mult-bounds/pull/7309)
keeps every provider fixed. This package uses its source lineage and
adds one changed provider at a time. Round 45 supplies the exact
rank-one transport and fixed-role test. Round 46 supplies the rational
rank and modular minor tests. OpenAI Codex and subagents materially
assisted with proof, implementation, replay and packaging.
