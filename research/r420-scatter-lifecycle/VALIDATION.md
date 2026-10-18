# Validation, 2026-10-13

One fresh positive build passed on the first attempt: **4 modules and all 28
required probes**, each using only standard Lean axioms. No previous objects were
retained. `exact_lifecycle` uses `propext` and `Quot.sound`; no `sorryAx` or
`Lean.ofReduceBool` was accepted. All eleven source-binding tests passed under
normal Python and `python -O`.

The official Lean 4.21.0 Linux release reported commit `6741444a63ee`. Its release
archive SHA-256 was checked before extraction:
`455c6df09d5bd54d2a51b137939c47e2dda816d512ac789c4b3642c9bf98bde8`.
The checker verified the inherited 317-module `Init` manifest before and after
compilation. The provided compiler/shared-library runtime remains a trusted input.

Execution used the official Python 3.12 container
`python@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1`,
with network disabled, a read-only root filesystem, dropped capabilities,
`no-new-privileges`, a 6 GiB container limit and two CPUs. Source and Lean runtime
mounts were read-only. Each Lean process additionally had the limits documented
in the README. The measurements below include subprocess wall time on this host;
they are not benchmarks or portable performance guarantees.

| Module | Seconds | Raw log SHA-256 |
|---|---:|---|
| BitXorTargetTranslation | 7.903805 | `a318c0e783704721480ab18b79e230e55b6ad2e43ddad13346744b52b0aad29b` |
| BitCopyScatterWindow | 7.861302 | `5765dea8e482ea3bf34e3307faf42a1e126470a361009188f1ce10ccf493e7dd` |
| R420ScatterData | 8.365274 | `3821642190add5514dbafb619d24f29b43fca0a9c0e957e0a04b93d007858cf3` |
| R420ScatterLifecycle | 9.204342 | `c69c7f9bf3bd4d9b55da8dfb34602e78635c639ed6a7befde9cded9ffb13693c` |

The emitted `RESULT.json` SHA-256 was
`498b7f9e662d31279e7558191c4f691aa276d6d2b2d8514fa70277421a07dc05`;
its input `MANIFEST.json` SHA-256 was
`447b11e3f43eefb3d63b4395801bc5d7f99e8a777b8b7da2fa532a1d8c2f8ee6`.
The reproduction command emits fresh source copies, objects, logs and a result
receipt into the specified build directory; timing and warning paths can differ.

The independent acceptance control also passed. With the exact lifecycle proof
replaced by `sorry` in a temporary copy and its manifest hash refreshed, Lean
compiled the module but reported `[propext, sorryAx, Quot.sound]` for that theorem.
The checker exited 1 with `nonstandard axioms: CurrentMain.R420ScatterLifecycle.exact_lifecycle`.
Its raw Lean log SHA-256 was
`574ac69eca593e3fd5ae7f342e73028b4fc1acae5ec6ea192de09d8b934977e9`.
This exercises axiom acceptance independently of source-hash rejection.

These are scoped local checks. No full repository replay, CI success, physical
COPY/ERASE proof, complete selected-construction proof or improved κ is reported.
