# Verification receipt

Executed locally on Linux x86_64 on 2026-10-13. Original base:
`66849e1475c930fd7732b1a0067ffee7e1e95f60`. Upstream refresh during verification:
`7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.

## Completed checks

- CPython 3.10.12: fresh `verify.py --record` construction, complete all-column
  native replay, exact prices and prefixes, both forest algorithms and controls
  passed. The recorded artifacts are the package's `RECIPE.json` and
  `EXPECTED.json`.
- CPython 3.10.12: `PYTHONOPTIMIZE=2 python3 -I -O -B
  research/complex-ck-target-forest/verify.py` passed against the saved artifacts.
  Every new guard is explicit and remains active with optimization. Inherited
  native subprocesses explicitly ignore optimization environment settings and
  retain their assertions.
- CPython 3.12.11: default verification passed in a minimal checkout under a
  path containing spaces, invoked from an unrelated working directory. Every
  inherited gzip was repackaged with compression level 1 and mtime 17. The
  decompressed payloads and all semantic checks agreed. A file-hash snapshot
  confirmed the verifier did not modify the checkout. This replay took 11.193
  seconds; that is an execution receipt, not a performance comparison.
- Both complete native programs pass on 716 logical columns, including all
  arbitrary helper and target inputs, with the 25 inherited adverse cases
  rejected. All non-scalar events and the paid histogram remain identical.
- The independent integer panel engine passes on 366 active columns in each
  orientation and checks that no gate touches the remaining 350 registers.
  Independently priced Prim and Kruskal agree at 16,364 complex primitives;
  every one of 12,544 cycle inequalities passes.
- Eleven new mathematical controls pass. Literal coefficient-work replay
  covers all 206 distinct coefficients, including arbitrary initial work dirt.
- Four external corruption checks reject altered native source bytes, a
  corrupted recipe, an understated forest floor and an inflated scalar saving.
  These were also run with `-I -O` on CPython 3.12.11, in the temporary checkout;
  each original file was restored afterward. These four external smoke checks
  are additional to the default command's 11+25 controls.
- `make selected-record-check` passed at the original base. It certifies the
  original base's selection, not the newly published #741 construction.
- All seven runtime source pins also match exact Git blobs on refreshed main.
  Its preserved `certificates/checkpoints/k492626.json` is byte-identical to
  the original base's selected record. The moving selected pointer is recorded
  as historical provenance and is not a runtime mathematical dependency.
- The complete patch passes `git apply --cached --check` against refreshed
  main using an isolated temporary index. A fresh minimal checkout populated
  with that main's actual input blobs and its new #741 selected pointer passes
  the complete default verifier on CPython 3.12.11. No rebase or replacement of
  the recorded original base is needed.
- Python compilation, JSON parsing and tokenization pass. Neither new Python
  file has source comments or assertion statements. No repository-wide
  no-comments target was found. Local documentation links and staged whitespace
  were checked before submission.

## Coordination and interpretation

The first pre-submission inventory contained 625 open PRs through #812;
the final refresh immediately before posting contained 628 through #815.
The six-PR integration reduced the open count while new research arrived.
There was still no pinned coordination issue. #741 is now the accepted
frontier; this package continues the explicitly claimed #626 CK investigation.
It makes no claim of automatic transport to #741. Related #749/#759/#769/#793
and concurrent #807 retain their separate contributions and recorded heads.
New #811 concerns additive coefficient routes in JP8 and #815 changes only
frames, both different scopes. The contribution was submitted as
[PR #816](https://github.com/CrocSwap/integer-mult-bounds/pull/816).

## Checks not claimed

The repository-wide `make verify`, either frontier's full cold regeneration,
global owner/invoice/outer admission, exact Clifford wrapper regeneration,
Lean, hosted CI and independent human review were not run for this isolated
addition. The native scalar/frame auditor checks the unchanged wrapper order
and endpoints; it does not regenerate the previously accepted Clifford phase
identities. Production construction integration remains open.

The two new verification implementations were written by one OpenAI Codex
agent. Their different arithmetic and spanning-tree methods provide a useful
crosscheck, not an independent-author or formal-theorem claim.
