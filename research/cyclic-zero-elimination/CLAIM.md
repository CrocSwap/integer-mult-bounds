# Sprint claim

- Track: verification engineering. OS-random assignment seed: 94.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Object: PR621's standard-library prime-power cyclic-inverse verifier,
  specifically zero-coefficient row updates in exact cyclotomic elimination.
- Method: compare the original and a zero-skipping implementation on the same
  eight shipped cases, then exercise singular and pivot-swap controls. Seed 94
  selects the additional right-hand sides `(zeta_q^94, 94)` at q=3,4,5.
- Deliverable: one scoped tooling improvement, exact receipt comparisons,
  same-input timings, and a reproducible command. No new mathematical bound.
- Expected finish: 2026-10-13 05:26 UTC, 10:56 IST.
- Coordination: no pinned issue existed when checked. Open PRs through #720
  were inspected. #668's modular CRT resultants extend coverage to larger
  orders; this task accelerates the existing exact elimination and retains
  its Bezout solve. #662/#667/#672/#707/#709 concern other kernels.
- Candidates considered: selected-source hashing, independent owner-check
  arithmetic, and cyclotomic elimination. Hashing was already short, and owner
  arithmetic overlapped pending work. Seed 94 directs this run to the older
  exact verifier rather than another selected-frontier kernel.

Prepared by thakrarsagar with substantial OpenAI Codex assistance.

## Result update

Submitted [PR736](https://github.com/CrocSwap/integer-mult-bounds/pull/736).
The source-pinned adapter preserves all eight cases and their negative controls.
All 28 measured full replays match the predecessor receipt. Seven alternating
pairs per interpreter measured 24.6% and 26.2% lower child CPU medians on local
Python 3.13 and 3.14. Wall medians improved with more variability, including one
slower pair. The [README](README.md) retains exact scope and all timing evidence.

The 36 focused matrix/mode checks and corruption controls pass, including
optimized Python. Isolated optimized replays from `/tmp` match on Python 3.11
and 3.14. The selected-record check passes. The original source and `upstream/`
remain unchanged. Full repository, cold frontier, and SymPy checks were not
rerun. A separate Codex agent reviewed the guard and controls.

Before submission, the PR queue was refreshed through #732 and relevant heads
were checked separately. PR668 remains a distinct CRT coverage extension;
PR727 optimizes a different owner checker. No overlapping zero-row adapter was
found, and no pinned coordination issue was available.
