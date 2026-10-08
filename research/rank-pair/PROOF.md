# Rank-first reclamation on interval strips and pair assembly

This finite conditional witness gives

\[
\kappa=\frac{5102757}{10^{11}}=0.00005102757,
\qquad a_b=\frac{5103018}{10^{11}}.
\]

It composes Avi Eisenberg's PR #62 interval-strip and core-aware pair graph
(`ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`) with Chafik Boukhalfa's PR #60
rank-first reclamation compiler (`e7a492dd8bee4e6f574ced784a62af2ce735edc4`),
which derives from eumemic's PR #57 joint frame compiler. The graph is
unchanged, and the candidate compiler is copied byte-for-byte from PR #60.
The composition experiment and exact validation driver were prepared by
Dominik Scholz with substantial OpenAI GPT-6 Astra assistance.

The witness exceeds PR #62's stacked κ by exactly 1066/10^11. It exceeds
PR #61 at `afb7cb67d1858641315cfbf4ac768ee64a8eff3a`, whose stated κ is
25508460085039/500000000000000000, by exactly
5324914961/500000000000000000 (approximately 0.0208751% relative).
These comparisons are against pinned research claims, not independent
acceptance of any of the full multiplication theorems.

## Mechanism and paid quantities

PR #57 originally visits retired physical roles in increasing slot order.
PR #60 visits them by descending current frame rank, breaking ties by slot
order. In either policy a retired role is eligible only if its current frame
is contained in the requested frame. Linear dependence is witnessed by
literal XOR operations involving eligible retired roles and the current
anchors; those XORs clear the selected role. Every operand is raised to the
requested frame and every resulting transition is charged. Only then is the
cleared role reused.

For the PR #62 graph, this changes the physical frame paths and their actual
fixed-basis profiles without changing the roles or the total rank. The
improvement is therefore established by the complete child moment, not by a
role-count heuristic or by treating clearing as free.

| h | roles | reclaimed roles | clearing XORs | all elementary XORs | distinct profile matrices | CRT-checked matrices |
|---|---:|---:|---:|---:|---:|---:|
| 23 | 27918 | 801 | 1612 | 149172 | 36378 | 6049 |
| 25 | 36586 | 1090 | 2092 | 205915 | 50419 | 8127 |

Both axes have zero CRT disagreements. PR #62's original clearing counts
were 1398 and 1827, respectively: the present witness explicitly pays the
additional clearing. The unchanged global quantities are m=575,
N=4073300, L=2226400, W=137151806, total rank=78860441550, and deficit=1846900.

## Finite validation and inherited hypotheses

`frame_compile.py` checks every input and dirty basis vector in both
orientations, then calls the independent serialized-word replay. `screen.py`
repeats that replay, reconstructs every transition from the actual word,
regenerates all fixed-basis profiles with the inherited bounded-minor and CRT
checks, and applies PR #62's unchanged complete paid-profile constructor.
The constructor verifies the total-rank identity and copied-center counts.

Exact rational logarithm/exponential enclosures show the moment is below 1
at a_b=5103018/10^11 and its lower bound is above 1 at 5103019/10^11.
PR #62's original complete child network also has lower moment above 1 at
the new a_b. The inherited balanced assembly passes all 47 strict constraints
and all seven margins at κ=5102757/10^11, and rejects the next grid point.
It uses the unchanged β=1/20, backoff h=10^-12, complex saving 717/10^7,
semantic C1=1, and product row stock p^2000. Smaller rational grids and
backoff were not needed for this witness and could refine its last digits.

The graph supports, scalar producer, original-envelope interpretation, data
geometry, paid endpoint copy, exact corner recovery, and all-size proofs
remain inherited from PR #62 and its cited predecessors. The rank-first
compiler uses precisely PR #60's mechanism. This note does not independently
prove OpenAI's base theorem, the fixed-alphabet/multitape transfer, the
analytic, semantic, routing or recovery interfaces, or their eventual
thresholds. Finite success is not formal verification of the full theorem,
and neither global optimality nor a practical speedup is claimed.

## Reproduction

```sh
python3 research/rank-pair/frame_compile.py
python3 research/rank-pair/screen.py
python3 -m unittest discover -s tests -p test_rank_pair.py -v
```

On this development machine the default MacOSX27 SDK fails to link because
the selected linker does not recognize its arm64e.x1 TBD architecture. The
successful local process-scoped override was:

```sh
CXX='c++ -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX15.2.sdk' python3 research/rank-pair/screen.py
```

The candidate compiler SHA256 is
`9984aaccf880e4840402322d76678bfddb33ce7e494af78430a43429f51b85fd`.
The graph SHA256 is
`3d47e89d2649c90800a276bdd0480131def50e0bdf92c122a19494b55bf17420`.
`frame-compiler.json` pins both sources and every serialized word; wall-clock
timing is excluded so recompilation reproduces the record deterministically.
`screen-certificate.json` records the exact moment, assembly, eventual
arithmetic cutoffs, complete child multiplicities, and pinned comparisons.
Six failure controls check omitted literal XORs, understated physical width,
omitted paid transitions, non-nested frames, exclusion of the old network,
and refusal to disable assertions with optimized Python. The independent experimental reproduction and a fresh parent reproduction
on the integrated main-based branch passed, including all six failure
controls. Repository-wide validation and PR review remain pending in CI.

Integration preserves main d55bcd62 and its existing verification groups.
The imported pair/skip source manifests were updated for main's six added
standard-library includes in `binary_io.hpp`; its functions and binary format
are unchanged. Their arithmetic certificates were regenerated. The imported
stacked certificate's source paths use POSIX separators for Linux CI.
The new candidate and both imported producers have separate CI groups.

## Bounded unsuccessful experiments

At h=23, three further policies were tested: descending rank with decreasing
slot tie-break; decreasing slot without rank; and increasing rank with
increasing slot tie-break. All retained the same 27918 roles. Full independent
dirty-word replay, frame reconstruction and profile regeneration passed for
each, but disjoint exact enclosures prove each has a strictly worse internal
moment than the selected rank-first policy at a_b=5103018/10^11. No claim is
made about those policies at h=25, which was not tested in this bounded round.
The negative-result records and exploratory compiler variants remain local
research scratch; they are not used to generate this witness.

## Attribution

Retain PR #62's full attribution in `research/pair-assembly/PROOF.md`, PR #60's
Chafik Boukhalfa rank-first contribution, and PR #57's eumemic compiler.
The pipeline additionally depends on Avi Eisenberg, Rohan Arun, RaD /
hipotures, icekylinx, Zhihao Chen, Aurel Prosz / Paureel, Swapnil Jain,
James Chang, Douglas Colkitt, OpenAI and Harvey–van der Hoeven, with the
complete inherited notices retained in the repository. The PR #62 graph was
prepared with Claude (Anthropic) assistance; the PR #57/#60 compiler and this
composition use substantial OpenAI assistance. Apache-2.0 applies, subject
to the existing separately retained source notices and terms.
