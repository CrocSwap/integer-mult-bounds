# Selected #626 assembly provenance digests: why replays differ

**No new κ, no certificate change.** This is an independent audit of the three
provenance digests that PR #695 (Joshua Snider, `jsnider3`) records as differing
between Linux CI run 38317651752 and the committed selected assembly, and that
#695 states it cannot explain because the workflow did not upload their payloads.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Audited #695 head:
`e322f2f1d9cc0f830cb3a50c6e928e0a1a32383c`.

## Reproduce

```sh
python3 -I -B research/pr695-digest-audit/verify.py --work /tmp/pr695-digest-audit
```

Expected last line:
`PASS_PR695_DIGEST_DIFFERENCES_EXPLAINED 3 digests reproduced, 2 rejection controls`.

If the work directory does not exist, the script first runs the cold replay
`scripts/verify_frontier626.py --work <dir>` (the step in the `frontier626` workflow). That needs the same environment as
the workflow: NumPy, SymPy and SciPy importable by `python3`, plus `CXX` and
`BOOST_INCLUDE` set. An existing completed replay directory is reused, so the
comparison runs in seconds.

## Finding

The three digests (`template_sha256`, `input_sha256.owner_audit`,
`input_sha256.fresh_invoice`) change on every replay. A fresh replay here gives a
**third** set of values, distinct from both the CI run and the committed record:

| | `template_sha256` | `owner_audit` | `fresh_invoice` |
|---|---|---|---|
| committed (`research/community-k492-audit/pr626/replay`) | `22b41c45…` | `ec7bc415…` | `367a73f7…` |
| Linux CI 38317651752 (#695 artifact) | `8aac9a65…` | `1de45f6b…` | `2219b0c6…` |
| this replay | `c8c82736…` | `2482b51f…` | `c325645f…` |

Two non-semantic inputs explain the differences fully:

1. **Wall-clock `seconds`.** Each provider's `CLIFFORD-REVIEW.json` and
   `SCALAR-FRAME-AUDIT.json` (`ck`, `jp8`) records elapsed time. These fields
   are written by `vendor/multicold/vendor/pr558/code/phases_full.py:36` and
   `code/hpe_audit_and_transport.py:286` under
   `research/complex-k492-owner-repair/`. The runtime `PLAN.json` pins the
   `CLIFFORD-REVIEW.json` file digests; the binder lists that field among the values it rebinds
   (`code/bind_providers_portable.py:65`). `code/emit_allcold.py:128`
   embeds `sha256(PLAN.json)` in the template. The template digest then propagates
   into the owner audit, the controller audit and the invoice. The package
   already treats `seconds` as non-semantic: its timing-stripped
   `provider_phase_semantic_sha256` and `provider_artifact_semantic_sha256` agree
   exactly between this replay and the committed record.
2. **Directory order.** `code/invoice_allcold.py:155` builds each provider's
   `artifacts` map from `local_dir.iterdir()`, so its key order (and the invoice
   bytes) depends on the filesystem. The keys and the timing-independent values are
   the same.

The checker substitutes only the four timing-file digests and adopts the
committed key order. That reproduces the committed `template_sha256` from this
replay's template payload, then `ASYNC-AUDIT.json`, `OWNERS-AND-PROFILE.json`,
`HOSTED.json` and `PREFIX-AND-INVOICE.json` byte for byte. The replayed complex
`ASSEMBLY.json` is then byte-identical to the committed one. Before substitution,
every assembly field except the three digests already matched, including κ
`51110230636731/31250000000000000`. Rejection controls confirm that a changed
outer margin, or a PLAN byte change that is not explained by timing, fails.

## Bearing on #695 and its triage

The facts that #695 and the earlier triage report are correct: the digests
differ, and the CI run did not upload the payloads. The concern they leave open
does not hold. The differences come from each run's timing and directory order,
not from a different template, owner audit or invoice. This explanation is not
gzip metadata, which #695 correctly declined to assume. The template digest is
taken over decompressed JSON.

Limits: the CI run's own payloads are unavailable, so its specific values are
attributed by mechanism, not by byte reproduction. Every replay, including the
same machine run twice, produces new values through the same path. The
`SCALAR-FRAME-AUDIT.json` non-timing content is not pinned semantically by the
package; only its committed digest is reproduced. Per the
[gzip/container convention](../gzip-container-reproducibility/README.md), a
future cross-environment check should compare the timing-stripped semantic
digests rather than these three digests. That change is the maintainers' call.

Environment for this replay: Linux, CPython 3.13.7, NumPy 2.5.4, SymPy 1.14.0,
SciPy 1.18.1, mpmath 1.3.0, g++ 15.2.0, Boost headers. The cold replay passed (6 stages)
in 31 minutes with `--jobs 6`. #695's own checker also passed at its head,
normally and under `-O`. Its archived artifact ZIP matches the live GitHub
artifact (`1f1ad114…`), and its archived workflow log matches the live job log.
The only difference is `gh` rendering ESC as `^[` on 7 lines.

## Credit

Joshua Snider's #695 preserved the CI artifact and recorded the three
differences explicitly, which made this audit possible. The supplier and review
lineage is the one #695 and the selected review credit: Douglas Colkitt, Chafik
Boukhalfa (#626), Jeremy Kothe (#622/#623), eumemic (#543), GamingPuzzled (#620)
and the predecessors. Maxime Fleury and Antoine Olivier wrote the
container-reproducibility convention cited above.

Audit by Rohan Guliani (@Rohansguliani), with substantial Anthropic Claude
assistance. Apache-2.0. This is not independent human peer review, and not a
formal verification of the multiplication theorem.
