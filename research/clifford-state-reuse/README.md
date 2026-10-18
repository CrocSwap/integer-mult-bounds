# Opt-in exact Clifford state reuse

Verification engineering, seed88; source base
`8bddbee377e2f3ce1f1247196c4b290d55767d20`.

This tool removes a repeated exact state calculation in the retained Clifford
compiler's `monomial()` function. It generates a source-bound compiler copy
outside the checkout and runs the unchanged phase driver against that copy.
Every tableau, rank, support, denominator and global-phase assertion remains.
The frozen construction sources and default selected verifier are unchanged.

**Current validation status:** the 16-operator, three-pair probe passed, with
identical recipes, tableaus and literal compiled circuits. It reduced
`zero_state()` evaluations from144 to104 per round. Independent semantic
controls passed107 circuits and all552 basis columns, including6 mathematical
fault rejections and6 positive guard-reachability cases. Nine driver controls
also passed, including an actual phase-child timeout. All six complete phase
runs passed with identical canonical recipe bytes. Baseline seconds were
152.5922,112.3706,137.0704; candidate seconds were97.2235,83.8536,84.9869.
The timing ranges were disjoint and the median ratio was1.6128 on this host.
Some early runs overlapped another allocated research job; this is an observed
phase-step result under that host load. Independent saved-artifact review passed
197 checks across74 files. A relocated minimal source closure passed the controls,
the current probe and a fresh complete baseline/candidate phase pair. No new
kappa or default-checker speedup is claimed.

From the repository root, with Python3.11 or newer and a fresh work directory
outside this checkout:

```sh
python3 -I -B research/clifford-state-reuse/verify.py --work /tmp/clifford-state-reuse-fresh --rounds 3 --hard-seconds 3600
python3 -I -B research/clifford-state-reuse/controls.py --work /tmp/clifford-state-reuse-controls-fresh
```

Successful replay result:
`PASS_EXACT_SOURCE_BOUND_PHASE_REUSE`. The command must generate fresh results;
an old successful recipe or receipt never substitutes for execution. Work
directories are preserved and cannot be reused. Numerical library threads are1.
The internal acceptance budget begins before preparation and bounds child
execution using the remaining time. Campaign runs additionally use an outer
whole-command watchdog; filesystem preparation/finalization can block before
Python gets an opportunity to check its clock. A timeout or incomplete output
is a failed/incomplete trial, never a performance result.

The replay first executes the separately implemented Gaussian-rational circuit
oracle. It interprets literal gates on every basis input for107 finite circuits
on0 through3 qubits. It checks the actual retained support, denominator and
absolute-phase guards with positive reachability and intentional faults. Its
source-pin and optimized-Python rejection children use isolated Python too.
This finite domain supplements the pinned full-word replay; it does not replace
the complete native inventory or prove all Clifford algebra. `controls.py`
checks source/input/generated/control-source pins, assertion mode, fresh work,
the checkout boundary, timeout acceptance, and hostile inherited environment.

The fixed input is the retained U8 local phase word:2,949 directed edges and224
endpoint adapters. Each baseline/candidate run must emit the entire pinned
canonical recipe JSON identically, including every recipe phase. Three pairs
alternate execution order. A performance claim requires disjoint timing ranges;
the result also retains individual timings and the median ratio. This is a
phase-step benchmark on this input and host, not a multiplication runtime
benchmark. PR1004/1005 and later changed words require their own input/source
and recipe coverage; these U8 counts and timings do not transfer.

`probe.py` selects the first and last actual edge at each rank1,2,3,4,5,8 plus
four real endpoint adapters. It is a cheap experiment, not complete phase or
full construction certification. See [PROOF.md](PROOF.md) for the sole edit and
its nonmutation argument, and [SOURCES.json](SOURCES.json) for exact pins and
credit. Global composition, physical admission, all-size/compiler realization,
common labels and mutable sources, complete-call hosting, precision/tape,
analytic transfer, and bit H1–H5 remain inherited obligations.

The original exact compiler and scalar lineage are retained Apache-2.0 work,
including PR531/552/558 and earlier credited sources. The phase driver credits
icekylinx's heterogeneous adaptation of PR425; the U8 lineage credits
JeremyKothe's PR869/870. Charles Bethin's PR662 accelerates this same evaluator
with gate tables and is the closest performance predecessor; this experiment
changes a different operation. Substantial OpenAI Codex assistance was used for
this tool, its separate exact semantic oracle, review and packaging. Independent
implementation/review here does not mean external human acceptance.
