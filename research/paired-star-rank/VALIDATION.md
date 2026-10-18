# Validation receipt

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Prepared 2026-10-13 by ellipsi2 with substantial OpenAI Codex assistance.

The completed result is a written uniform rank theorem plus a finite exact
certificate. It does not certify a new paid supplier or the multiplication
theorem. The literature dependency is identified in RANK-PROOF.md.

## Executed checks

| Environment / check | Result |
| --- | --- |
| Windows, CPython 3.11.15, `python -I -B research/paired-star-rank/verify.py` | PASS, complete receipt matched |
| Windows, CPython 3.11.15, `python -I -O -B research/paired-star-rank/verify.py` | PASS, all assertions-independent checks active |
| Windows, CPython 3.11.15, `python -I -O -B research/paired-star-rank/test_verify.py` | Four test groups passed |
| Ubuntu under WSL, CPython 3.12.3, isolated `-I -O -B` verifier | PASS, same committed receipt |
| Ubuntu under WSL, CPython 3.12.3, isolated `-I -O -B` harness | Four test groups passed |
| Deterministic certificate regeneration in both harness runs | Byte-identical UTF-8/LF certificate |
| Relocated replay with only declared package/input files | PASS, no repository or working-directory imports |
| `python -B scripts/verify_selected_result.py` | PASS selected record, exact kappa, original source inventory and proof supplement |
| `git diff --check` and staged whitespace check | PASS |

The Windows-mounted drives were unavailable to WSL in this session. The Linux
check therefore used an in-memory archive of the same declared files, streamed
to a fresh Linux `/tmp` directory; no Windows-side imported modules or network
dependencies were available there. This was local Linux execution, not GitHub CI.

The verifier checks all 36 declared cases (`k=2,3,4`, `p=k,...,8`, both
empty-star policies), 2,706 unit-vector decoder identities and 3,714 spanning
identities on the complete original port families. Every target's permitted
overlap corrections is checked in the power-of-two cases; k=3 supplies the
positive escape control. Every invocation runs all eight named rejection
controls and compares the entire deterministic receipt.

The four harness groups additionally cover byte-for-byte regeneration,
relocated optimized replay, a corrupted certificate, an incomplete receipt,
modified contextual source bytes and modified source pins. Failed runs must
leave a pre-existing export file unchanged and cannot print the success line.
The false-rank internal control must reach the full-family spanning failure;
a mismatch against the theoretical rank formula alone does not count.

A separate AI worker reviewed the unsigned-basis argument, the sign-sector
decomposition and the no-empty criterion, and inspected the identity verifier.
This is disclosed AI-assisted review, not independent human review or formal
proof-assistant checking.

## Scope of verification

The existing supplier generators, selected certificate and `upstream/` were
not edited. The expensive repository-wide `make verify` and selected cold
replay `make frontier626-verify` were not repeated for this additive research
package. No repository-wide or hosted CI pass is claimed. The selected-source
integrity command above checks bindings; it does not cold-replay the suppliers.

The finite checks establish the explicit certificates. The uniform theorem
uses the written argument and cited integral inclusion-basis theorem; it is
not established by extrapolating from the tested domain.

The pre-submission overlap refresh covered **586 open PRs through #767**.
The relevant #669, #732 and #747 heads still matched SOURCES.json. #747's
`(6,4)` all-target result is credited; the new contribution is the uniform
rank formula, exact empty-star boundary and literal `(8,4)` information sets.
