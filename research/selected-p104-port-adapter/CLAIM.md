# Cycle 2 local claim

- Recorded: 2026-10-14T08:27Z. Expires: 2026-10-14T10:27Z.
- Track/task: `complex-mechanisms` / `complex-new-helper-inventory`.
- Seed: `e8aefa5747f8dc1d69ca9c50f361d20c`; priority revision 3.
- Exact base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
- Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Scope status: refined to construction of an exact 9-bit linear adapter from the selected 112-port set to the E8 P112 port set, then reindexing one P104 frame-pair decoder onto the selected ports.
- Question: does the selected word's actual port set admit such an adapter, and what exact P104 decoder and COPY rank profile does it induce?
- Changed assumption/expense: use a P104 (104-port, eight rank-7 term) decoder on the selected 112-port label configuration, rather than PR1619's favorable cost-only P104 knob. The port reduction, embedding into the selected local word, frame/restoration costs, and outer hosting must be charged before claiming a new supplier profile.
- Method/domain: exact binary linear algebra on all 512 functionals, deterministic search over the 168 isomorphisms of the seven-element weight-64 subspace and a bounded six-dimensional quotient search; exact decoder check on all 104 live indices. No random search and no claim beyond this fixed selected set and chosen frame pair.
- Predecessors/overlap: PR717 and PR968 give the abstract E8 P104 decoder; open PR1619 (`6c96bc1a0e374a713e9ae493228247f49be49dd5`) prices the P104 knob but explicitly has no selected-word realization. Its earlier claim #1606 is expired. The 08:04 UTC full-pagination overlap refresh returned no active exact P104-adapter claim. Open PR1348 concerns changed coverage laws and does not include this port relabeling or decoder.
- Expected handoff: exact adapter matrix, 8 removed selected ports, P104 decoder witness, exact term-rank checks, negative controls, and a precisely scoped cost/implementation boundary. The local profile must not be promoted unless the selected-word endpoint and all interface costs are derived.
- Coordination: posted to [Discussion #1163](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18919568). The claim is advisory and expires at the time above.

## Result — 2026-10-14 08:30Z

- Constructed a bijective F2-linear relabeling of the selected 112-port set to E8 P112 and identified the eight removed port values for one admissible P104 frame.
- Reindexed one exact decoder: `D T^T = 2G` on all 104² pairs; all eight COPY ranks are 7, total 56.
- Exact selected T37 knob replay: complex lower bound +5.5311%, above the fixed bit primitive; the favorable outer result is capped at κ `0.001730427469823602`. This is not a complete supplier or a new κ claim.
- Submitted as [PR #1746](https://github.com/CrocSwap/integer-mult-bounds/pull/1746), head `c5d240fd4bd2e7b9a828d18cfb7619bd004a124a`, base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. It is open and mergeable; repository checks were still pending at handoff.
- Remaining obligations are asymmetric-centre compilation, phase-frame legality/restoration, unpaired-centre parity and pair-split charges, and a full hosted supplier profile. The local verifier and package pin check pass; local generic CI replay was unavailable because Python 3.12 is not installed (the direct verifier passed on Python 3.14.7).
