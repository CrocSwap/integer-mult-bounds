# Validation and handoff

Local execution on 2026-10-13, macOS arm64. Base:
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.

## Completed evidence

- `python3 -I -B research/r420-block7-exact-schedule/native.py --out /private/tmp/r420-block7-native-v1`:
  PASS on CPython **3.14.5**, Apple Clang **17.0.0**, Boost **1.90**.
  The source-pinned, unchanged native code was freshly compiled for this run.
  Both original/replacement words passed chronological legality and all
  900 / 1,380 / 1,620 physical columns at five / nine / eleven stages.
  All 6 / 18 / 24 bridge-omission controls per word rejected: **96 total**.
  Native counts and exact positive-prefix payloads matched the independent
  Python recount. The two native summaries are retained in `NATIVE.json`.
- The primary verifier passed on CPython **3.14.5** with isolated optimized
  execution (`-I -O -B`), and system CPython **3.9.6** (`-I -B`).
  All eight semantic/accounting controls rejected for their named reasons.
- Fresh nomination reproduced `CERTIFICATE.json` byte for byte. The verifier
  does not import the nomination code and checks every lower-bound edge using
  a different donor-subset enumeration and integer-column interpreter.
- A minimal export containing only this package and `SOURCES.json` inputs
  passed from outside the repository, in a path containing spaces, under
  isolated optimized Python. Corrupt-source, inflated-potential,
  changed-expected-receipt and existing-output controls all rejected.
  The existing-output sentinel remained unchanged.
- Git verified that the original word has the same blob
  `0c63ca62759dc63d302be6552aeeee1ede70350f` at both the exact main base and
  the fetched PR543 head `2065fe4f72a914d907f1046603f5a36f17018535`.
- `make selected-record-check` passed. Its first invocation failed because
  certificate bootstrapping (without `-B`) created an untracked xcheck cache
  in an immutable supplier package. Only that new cache was removed; the
  contribution now suppresses bytecode before importing repository modules.
  No selected source bytes or inventory were changed.

The execution path above identifies the local run; it is not a portability
dependency. Use a fresh output directory for reproduction. `NATIVE.json`
records a completed local run, not hosted CI status. `native.py` recomputes
and checks native status/counts/coverage against the exact Python receipt.

## Deliberately outside this contribution

No full repository-wide `make verify`, selected supplier cold replay,
hosted-parent invoice, outer assembly, remote Linux CI, proof-assistant
build, or runtime benchmark is claimed. This addition changes only the new
research package, not a selected generator. Full native stage replay was
chosen because a local circuit changed. The selected bit source, frontier,
and `upstream/` remain untouched.

All-size compiler/common-label/mutable-basis, physical hosting, residual,
precision/tape/exact recovery and analytic assumptions remain. A potential
certificate proves the stated finite schedule-class minimum; finite scalar
replays do not prove the integer multiplication theorem.

## Review focus

1. Check the fixed 17/24 cut and row-batch class in README; the minimum 28
   does not claim unrestricted XOR optimality.
2. Check the independent base-16 subset enumeration and potential
   inequalities, including empty batches and arbitrary completion order.
3. Check the complete integer map, reverse positive domination, unchanged
   register frame paths and literal cleanup. All restoration work is priced.
4. Check `EXPECTED.json`, `NATIVE.json`, source pins and predecessor credit.

Contributor: Yuzhou Wang / @yzhouwang, substantial OpenAI Codex assistance.
No delegated workers or independent human peer review. Apache-2.0.

## Publication overlap refresh

The initial snapshot covered 586 open PRs through #767. The submission
refresh inspected the 100 most recently updated open PRs, including all new
arrivals #768–#786. Main remained at the exact base. No block-7 or fixed
two-factor row-batch certificate appeared. New #774 concerns target
compensation forests; #782 concerns intrinsic lattice parity. Neither
changes this block or supplies the finite schedule-class certificate.
The inspected #681/#691/#754 heads remain those in `SOURCES.json`.
No pending implementation was imported and no additive composition claimed.

Final committed-files-only replay at construction commit
`d8c13a065a942018e41721f859dc97da5249a2e1` passed from a minimal export.
The complete patch applied cleanly to an empty target for these additions;
staged whitespace checks passed. The submission is
[PR #789](https://github.com/CrocSwap/integer-mult-bounds/pull/789).
The subsequent handoff commit changes only this validation record and the
one-time claim result update, with no code or certificate changes.
