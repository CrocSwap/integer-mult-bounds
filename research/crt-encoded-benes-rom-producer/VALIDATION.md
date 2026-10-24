# Validation and scope

Python 3.12.2 on macOS; no dependencies, Lean, Docker or selected-result replay.

* Full normal `python3.12 -B research/crt-encoded-benes-rom-producer/verify.py --write-result` passed all four producer fixtures and twelve controls. Authoring mode executes the same checks as registered verification; only its final receipt write replaces receipt equality.
* The actual h3, W20, modulus5, offsets[0,2,4,0] producer executed459,156,907 primitive instructions, used16,685 represented cells, and emitted all five canonical layers. It directly joined the same selected ROM list to the unchanged key service. Final disposal took1,796 instructions.
* After that run, the verifier's receipt epochs were normalized from tuples to JSON lists, and address10 was added to the four original consumer cases. A consumer-only calibration passed its positive epochs (10,1),(14,1),(14,1). The final exported optimized replay below executes all five cases on the newly generated actual list; no normal producer rerun is implied.
* Independent agent review checked the literal control, word representation transport, marker-driven unbounded finite list traversal, ownership/rejection boundaries, source recurrence, consumer identity and independent epoch audit. The small W4,17-offset case was independently replayed. This is agent review, not human or proof-kernel acceptance.
* Metadata and exact source pins passed. Vendored PR4192 bytes were compared with original commit519d811cc48693ad9969d6d7994bef3940167005. The manifest records that original pin separately; its transport pin identifies the identical vendored path in this branch's first implementation commit.

Final committed source-history check passed at ae564e3c13bde53f292a608a38793aa7710ded84 (21 files; both source commits in ancestry). The official export/check passed. In an extracted tree with no .git metadata, `/opt/local/bin/python3.12 -O -B research/crt-encoded-benes-rom-producer/verify.py` passed all four complete producer fixtures, all five direct consumer cases and twelve controls, including frozen exact receipt equality. Export SHA256: ed2e8b2601df11e825fa281423e57d7d3bbfd4bf42a5f16989986f69c5b8ee00. A separately corrupted retained machine source was rejected by source authentication before producer execution. Subsequent edits record this validation and clarify that the service target is bit position 2, not Boolean value 2; every executable/input-source/receipt hash remains unchanged. Frozen receipt comparisons authenticate source content and exact primitive counts; these finite replays calibrate the separately stated scoped proof. No complete CRT evaluator or selected frontier change is claimed.

## Hosted replay budget correction

GitHub Actions on Linux with CPython 3.12.15 reached the original 180-second
per-command limit on the complete normal producer replay (run 39927492849,
job 120328791828, 2026-10-23 08:55:01–08:58:01 UTC). The reported failure was
`verification timed out`; it did not report a mathematical or receipt mismatch.
Both registered commands now have a bounded 600-second budget to accommodate
that platform. This change preserves every executable, retained input, source
pin and frozen receipt byte. The existing complete local normal and exported
optimized evidence above is reused; no additional scientific replay is implied.
Metadata/source-history and committed export checks were repeated for the budget
change. Hosted completion must be reported separately from the local evidence.
