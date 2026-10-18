# Sharp separate-COPY cost for one P112 two-column completion

Hanhong Zhao ([@Hope7Happiness](https://github.com/Hope7Happiness)), with substantial OpenAI Codex, Claude Code and Gemini assistance.

For **exactly the PR2021 completion with live ports j=0, k=1 and coefficient +1**, every nine-term factorization over C, using ordinary transpose and the original binary labels, has

```
min sum_i rho_i^q = 7*8^q + 7^q + 1,  for every 0 < q <= 1,
```

where rho_i is the actual binary support-pairing rank charged separately to term i. The rational witness has ranks `(8,7,8,8,8,8,8,8,1)`. Its sum is **64**, versus **65** for the displayed predecessor factorization. For `0<q<1`, its sharp power bill is **strictly greater** than `8*8^q`; this fixed completion cannot improve that COPY power benchmark.

This is a scoped negative effective-rank result and sharp attainer. The universal statement follows from [PROOF.md](PROOF.md), using the complete finite support catalogue and duality cases. Replay verifies those finite premises exactly; it is not a proof-assistant formalization or an exhaustive coefficient search. The mathematical proof and exact witness were independently reviewed by separate Opus agents. No independent human review or formal verification is claimed.

## Reproduce

From a repository checkout with Python 3.12 and no third-party dependencies:

```sh
python3.12 -I -O -B research/p112-two-column-copy-optimum/verify.py
python3.12 -I -O -B research/p112-two-column-copy-optimum/test_controls.py
python3.12 -B scripts/research_package.py --package research/p112-two-column-copy-optimum
```

The entire package directory can also be copied out of the repository: run `python3.12 -I -O -B verify.py` there. The default verifier reads files and writes no evidence or bytecode. `test_controls.py` creates and removes temporary test files; it never changes package files. No network, quota guard, absolute workstation paths, timestamps, random sampling or external solver is used.

To generate a fresh deterministic certificate, explicitly choose a **nonexistent** output path:

```sh
python3.12 -I -O -B verify.py --write /your/new/certificate.json
```

Existing paths are refused. Normal replay recomputes and compares the complete checked-in certificate; `--write` is an explicit certificate-generation mode and still validates source binding and the exact witness. Verification uses explicit checks, not Python assertions, and survives `-I -O -B`.

## Data and evidence

- `ROOTS.json` is the exact ordered `root_lines` and `binary_ports` extract from the pinned upstream prototype. The first eight rows are the removed frame; the remaining 112 are never reordered.
- `SOURCES.json` binds the source commit, Git blobs and SHA256 digests. The verifier authenticates the complete manifest and extract bytes. If the original prototype exists at its canonical repository path, its complete bytes and extraction are also checked. A detached export uses the pinned extract; Git provenance checking is performed by the repository replay hook in a checkout.
- `WITNESS.json` contains exact canonical-rational M,N and actual support ranks. D=LM and T=RN are reconstructed, not stored redundantly.
- `CERTIFICATE.json` retains all 1,022 rational character kernels, class pairing table, complete compensation cases, integer majorization checks and attainer. It contains no session-dependent values.
- `model.py` derives both L/R catalogues independently from the input rows. It checks all 12,544 matrix entries, the displayed COPY65 control and the COPY64 attainer. An exact nonreal phase control preserves ordinary products and rejects Hermitian substitution.
- `test_controls.py` rejects source/manifest drift, wrong compensation, corrupt kernel/witness records and out-of-domain JSON numbers with exact expected failure reasons, and tests a present-but-corrupt canonical prototype, invalid `--write` inputs creating no output, a detached read-only optimized replay and overwrite refusal.

## Scope, provenance and next questions

The prospective hypothesis was recorded at [Discussion2006 comment18940755](https://github.com/CrocSwap/integer-mult-bounds/discussions/2006#discussioncomment-18940755), H `q_a9e057b2a674468b:e15`, before the independent e17 first gate. `TASK.json` retains the original task card, single-draw selection and scope change. Discussions are provisional research provenance, not independent mathematical validation.

Credit: commdata2338 / [PR2021](https://github.com/CrocSwap/integer-mult-bounds/pull/2021) for this completion and displayed factorization; Arham Tahir / [PR1591](https://github.com/CrocSwap/integer-mult-bounds/pull/1591) and bitplane / [PR1652](https://github.com/CrocSwap/integer-mult-bounds/pull/1652) for one-anchor classification and compensation precedents; root/label lineage [PR845](https://github.com/CrocSwap/integer-mult-bounds/pull/845), [PR717](https://github.com/CrocSwap/integer-mult-bounds/pull/717), [PR968](https://github.com/CrocSwap/integer-mult-bounds/pull/968), [PR1077](https://github.com/CrocSwap/integer-mult-bounds/pull/1077). The new R catalogue and its pairings are checked afresh: no one-anchor theorem is transferred without proof. Predecessor files are unchanged; this package contains a minimal data extract, not copied predecessor executables. Repository Apache-2.0 licensing applies; the license is included for detached exports.

Changing the completion, term count, labels or sharing COPY work changes the premises. This package makes no native/frame/dirty-restoration, full-cost invoice, precision, all-size, selected-exponent, CI, full-cold or Lean claim. Other completions and legal physical sharing remain open questions, recorded with first steps in `TASK.json`.

## Open next questions

1. Other completions: rederive both exact character-kernel catalogues for one prospectively selected matrix. The present proof fixes its ports and coefficient, so it cannot settle that question.
2. Shared physical COPY work: specify a legal implementation and charge all frames, restoration and precision. Separate term billing is a theorem premise; no such implementation is supplied here.
