# Executed validation

Environment: Windows, CPython 3.14.5, standard library only; 2026-10-13 local
client date. Base `8bddbee377e2f3ce1f1247196c4b290d55767d20` on isolated branch
`research/sprint10-r03-s31`.

- Producer ran normally to create the deterministic receipt, then `-I -O -B`
  replay reconstructed all 447,552 cases and matched every frozen receipt field.
- Separate Fraction/primitive checker ran normally, then `-I -O -B` replay
  matched the complete histogram, every pair's cost floors and exact matrix
  receipt. It executed both orientations on 219 arbitrary columns and rejected
  eight mathematical mutations.
- `test_package.py` passed with `-I -O -B`: deleted/extra pin, wrong source hash,
  wrong base, changed selected snapshot, a repinned but wrong selected kappa,
  integer-to-float receipt mutation and non-dyadic coefficient controls.
- Both parsers reject duplicate target/helper entries. The source archive and
  decompressed canonical payload are independently bound. Text source hashes
  normalize CRLF to LF; the archive hash remains exact.
- `git diff --check` passed. Only the new research package is contributed;
  no selected pointer, predecessor file or upstream source was edited.

The independent checker is a second AI-written implementation, not independent
human review. Local matrix exactness, primitive cost and positive envelope
measurements do not establish full-supplier native admission or theorem proof.
No native compiler/Boost setup, dependency installation, full repository suite,
selected cold replay, global invoice, hosted CI or Lean execution was performed.
