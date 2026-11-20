# Second, adjoint paid-chain contraction

The combined candidate's bounded-scalar application reports conditional κ ≥ **0.00387990740712**, above 0.00387981257853 by 0.00000009482859, under the same five inherited premises. This is a conditional finite application, not a proof of those premises, maintainer selection, or an unconditional resolution.

Starting with the separately preserved first contraction (`CANDIDATE.json.gz`, canonical SHA-256 `320847d42f2655c3cc0fd29fe670ae77277e9c2f377c1c92f33d7df050872f54`), reverse the scalar incidences. In that adjoint, retire paid slot 94025 (304 → 2) and replace 94019 (2 → 3) with 304 → 3. Its new source is `-1/1536` times address -1288 plus `1/8` times 94034. Restore its old value at all 14 original readers using `-1/8` times 90072 and `-1/2` times 90555. The independently written `verify_second.py` checks the literal delta, causal availability, and exact arbitrary-input identity. The forward representation is recovered by reversing the adjoint incidences. Layout and caller remain unchanged. This second contraction changes the 48-call paid histogram by P1 −48, P2 −48, P3 +48; productive targets remain unchanged.

`DOUBLE-CANDIDATE.json.gz` is the combined graph, canonical SHA-256 `7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48`. `DOUBLE-REPLAY.json` records the construction and reader roster. `DOUBLE-APPLICATION.json` is the full finite application against the predecessor source contract, with the independently admitted binary cap 0.0038799074072. The predecessor producer cap is looser; its first combined replay failed the independent audit and is not the claimed result. `qualify_capped.py` authenticates the predecessor script and independent binary receipt, checks the same binary word and tighter cap, then patches only the cap assignment in a temporary copy. The earlier graph and evidence remain in this archive and its earlier commits. The dedicated workflow first replays those, then verifies the second exact delta, replays the combined finite application, and runs the predecessor expanded audit on the combined receipt. Independent human review remains requested.

For manual replay, use the source preparation in the main README, then:

```sh
python3.12 -IB "$pkg/verify_second.py"
python3.12 -IB "$pkg/qualify_capped.py" --cache /tmp/p104-sources --package "$pred" --word "$pkg/DOUBLE-CANDIDATE.json.gz" --word-sha 7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48 --layout "$pred/continuation/LAYOUT.json.gz" --layout-sha f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7 --out /tmp/p104-double-application.json
python3.12 -IB "$pred/continuation/audit_expanded.py" --cache /tmp/p104-sources --word "$pkg/DOUBLE-CANDIDATE.json.gz" --layout "$pred/continuation/LAYOUT.json.gz" --word-sha 7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48 --layout-sha f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7 --receipt /tmp/p104-double-application.json --binary-receipt "$pred/binary/INDEPENDENT.json" --reference-application "$pred/evidence/application.json" --out /tmp/p104-double-audit.json
```

Credit and inherited licenses are as recorded in the main README and predecessor. Clear1nsight prepared the continuation with substantial OpenAI Codex assistance, including independent AI checks.
