# Local validation

The final package command exited with status 0 on 2026-10-13:

```sh
sh research/cyclic-schur-lean/verify.sh /path/to/lean-4.21.0/bin/lean
```

The machine was macOS on ARM64. The compiler reported Lean 4.21.0,
commit `6741444a63eec253a7eae7a83f1beb3de015023d`. The downloaded
official archive matched the release's published SHA-256 digest in
`SOURCES.json`. The build used only the matching core and Std libraries.
No shared Lean cache was changed.

The check compiled `CyclicSchur.lean`, `Counterexamples.lean`, and
`Audit.lean` from source in a fresh temporary directory. The final output
is byte-identical to `AXIOMS.txt`. The guard checked 102 theorem
declarations, including generated equation and tactic lemmas. A separate
source inventory found all 30 named proof theorems and all six named
example/control theorems in that report.

The mathematical controls prove that four concrete incorrect reductions
fail: positive instead of negative child stride, a tail that starts one
entry early, omission of the chain-start coefficient, and a stale
predecessor read. The build also verified both axiom-guard controls.
The incomplete-proof input failed specifically on `sorryAx`. The custom
axiom input failed specifically on the package-axiom check.

A measured run of the same three proof modules and guard tests took
16.24 seconds wall time. Peak resident memory was 901,316,608 bytes
(859.5625 MiB). Each compiler call used `-j 1`. These are local build
measurements, not solver performance results.

The first resource wrapper could not read macOS `kern.clockrate` in the
sandbox. It returned status 1 after the inner verification had printed
both pass messages. That wrapper result is not counted as a successful
run. A permitted resource-accounting run exited 0. The final plain
verification command also exited 0 after the script's signal-cleanup
change. The proof source did not change between those successful runs.

The four inspected subject files have exact commit, Git blob, and SHA-256
pins. The PR846 pins were checked against GitHub's immutable file API.
The PR985 pins were checked against the local pinned Git objects. PR846,
PR985, and PR896 still had the recorded heads at the overlap refresh.
The recent open-PR inspection reached PR1012 and found no newer cyclic
Schur formalization. This is a bounded overlap check, not a claim about
all unpublished or external work.

No global `make verify`, selected cold replay, hosted CI, Python runtime
test, FIFO proof, or physical tape test was run. This package changes
none of those implementations or certificates. The limits in `README.md`
remain part of the claim. No independent human review is claimed.

`VALIDATION.json` binds the checked source bytes and output digest. The
full local logs and the compiler receipt are retained in the lane archive
named in the coordinator handoff.
