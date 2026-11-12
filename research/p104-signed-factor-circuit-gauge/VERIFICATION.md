# Verification and caps

Run the one command in README.md on POSIX CPython 3.12. The verifier authenticates each bundled runner, input and receipt under `closure/` using path-keyed SHA-256 pins. Duplicate paths and unpinned closure files are rejected. The exact source paths and commits are in PROVENANCE.json. Outputs from both literal engines are matched byte-for-byte. The two factorization receipts match exactly after removing runner time.

- Circuit screen: 38 factors, two exact nullspaces, 20 runner seconds. The independent literal engine checks every basis column of the −I endpoint, the exact slope minima and rank-18 selected residual. A corrupted original factor is rejected.
- Rank-18 obstruction and rank-19 witness: one selected residual per round, 60 runner seconds per case. The recorded shortest constructions multiply on all 36 basis columns. First-factor sign mutations are rejected. The successful shortest-control run took 0.1204s and the 20-to-19 witness took 0.1123s. An earlier shell wrapper for the same rank-18 case failed to retain the child exit after JSON emission. The corrected replay agreed on every field except time, with combined runner time 0.2408s.
- J1 extension: both literal engines independently reconstruct all 36 residual columns, with 306 off-block entries and rank one in the lower-left block. The independent engine rejects a corrupted unchanged factor. The fixed-plane proof uses these exact identities and the rank-minimal product expansion.
- D8 gate: one legal body profile, 30 runner seconds lead and 20 independent. Both exact literal endpoints agree and reject an omitted body action. The wrapper multiplies the 19 frozen witness factors after the exact sign gauge, verifies all 36 literal columns in both engines, and rejects the ungauged reuse on basis 1.
- Directed price: exact rational arithmetic reuses the two #7420 price endpoints. It checks the 33 net A calls at 96 ports and the negative 17-host upper bound.

This checks the frozen normalized result and one profile. The remaining native, all-sector and all-size gates are in README.md and PROOF.md.
