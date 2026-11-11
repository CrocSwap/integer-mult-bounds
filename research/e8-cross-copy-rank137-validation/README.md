# Rank137 validation evidence

Python3.14.8 complete component replay passed using the already verified PR447 parent. This includes source reconstruction, mixing, record export, C++ legality and columns, record mutation controls, Gram checks, geometry, template emission and independent audits, regenerated complex supplier, both moments and finite outer assembly. It is not a fresh full parent replay.

Tested package manifest: `8441fa7b22a19ec4ac31625d0c7c2f9d581b43c970406cc8d85e6f390a82c14d` at PR453 code commit `bd4dc1a3b32a0c094304e34be75e28dbddc3130b`.

Fresh full Python3.14.8 replay PASS at the same package manifest; receipt and logs are in `python314/`. Python3.11.15 also passed in full; receipts and logs are in `python311/`. Both full RESULT.json files agree exactly. GitHub CI is queued, not passed. The rank138 anchor exactly reproduces PR450. The partial idle remainder changes rank14 to rank3; the initial README wording was corrected after the full runs. `DOC-ONLY-UPDATE.json` and `README-STATUS-ONLY.diff` bind that documentation-only change; executable source and data are unchanged.

The123-relation subset MILP nominates the same rank137 selection. The solve uses a floating objective and relaxed concentration model, so its optimal status is not a mathematical optimality proof. The search script refers to the local research workspace and is retained as experiment provenance, not the standalone verifier.

Fixed-rank137 stage screens at13,15,17,19stages all produce lower exact bit endpoints than11stages. These are losing aggregate-only screens, not admitted global constructions.
