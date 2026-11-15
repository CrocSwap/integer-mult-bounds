# Validation receipt

Checked on 2026-11-15, macOS arm64, CPython 3.12.16, standard library only.
Canonical main e54523517d0f03e58352e647c403a5af3e525a57 was refreshed before
submission; relevant guidance, catalogue and selected-result pins were unchanged.

The registered command completed successfully:

```sh
python3.12 -I -B scripts/research_package.py --package research/p104-large-step-audit
```

| Command | Observed result |
| --- | --- |
| verify.py | PASS_SELF_CONTAINED_SOURCE_CUSTODY, 13 immutable exports and corrupt-byte rejection |
| frames.py | PASS_SCOPED_CONTACT_FRAME_BOUNDS_NO_KAPPA_GAIN, four exact directed negative margins |
| independent_frames.py | PASS_INDEPENDENT_FRAME_CORRIDOR_BOUNDS, separate DAG/DP/interval arithmetic agreeing in all four cases |
| bit/audit.py | PASS_INDEPENDENT_REVERSE_DUAL_FIXED_HISTORY_SCREEN, 39,848 observations and nine explicit kernel certificates |

The independent frame checker and BIT kernel audit use explicit runtime checks;
frame assertions are protected by an explicit refusal to run the primary checker
under -O. Registered commands run without optimization. Exhaustive small DP paths,
forced descents, source tampering, joint-versus-singleton recovery, altered dual
witnesses and the sole zero-state interval have explicit controls.

The initial standalone BIT receipt comparison exposed JSON integer-key versus
string-key normalization; it was fixed by canonical JSON comparison without
changing any witness, receipt bytes or scientific result. Final registered replay
passed. Proof and claim review by a separate Codex agent found no new inequality-
direction or scope issue; this is not independent human verification.

No new kappa or supplier is produced. Full native/physical/caller/tape/precision/
compiler/outer/all-size admission was not rerun and is not claimed. Historical
upstream source notices and stated premises remain intact.
