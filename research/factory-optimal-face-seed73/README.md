# Research audit: the nine-shift factory gauge is unique

PR1064 proves a nine-shift minimum for one fixed 26-ADD factory topology and
supplies one optimal schedule. This package proves that **its ADD-boundary
level vector is the unique optimum even over real levels**. Every different
integer gauge costs at least eleven shifts, with an explicit eleven-shift
witness. This closes the possible improvement from choosing another optimal
gauge in that exact class. Unary-step placement and other topologies remain
open. No new kappa is claimed.

The proof uses the dual certificate's 35 zero-flow edges: an anchored tree
forces all 26 levels. `verify.py` independently derives register paths from
PR924, checks flow conservation, reconstructs the unique optimum, certifies
the parity gap and replays exact local matrices in four orientations. It
imports no predecessor code and uses only Python's standard library.

Run from the repository root (Python 3.9+):

```sh
python3 -I -B research/factory-optimal-face-seed73/verify.py
```

Expected output:

```text
PASS_FACTORY_OPTIMAL_FACE unique_real_gauge=1 shifts=9 next_integer_cost=11 orientations=4 no_new_kappa
```

`CERTIFICATE.json` records every distance edge, the anchored tree, exact level
vector, local prefix norms/depths, and control coverage. Regenerate only this
certificate with the same command plus `--write-certificate`.

The checks reject all 52 signed unit perturbations as optimal witnesses,
unbalanced or over-capacity flow, absent boundary anchoring, an incomplete
tree, and deleted shift/sign/ADD instructions. Fifty-two rational perturbations
check the gap identity and stability inequality as additional evidence.
The all-real uniqueness and all-integer gap follow from `PROOF.md`, rather
than extrapolating from these finite samples.

Exact base: `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`.
Audited PR1064 head: `b0181971c2364744d1dd9b0c2d4ee1ea532b8bb6`.
The original input JSON files and SHA-256 pins are retained in `sources/` and
`SOURCES.json`; they are read as data. The accepted selected result at this
base remains PR942, kappa `1661960547713947/10^18`. Pending PR1064 is not an
accepted frontier. `CLAIM.json` records seed 73, candidate selection, timing
and the local claim; no pinned sprint coordination issue was available.

The scope is the local factory relaxation and canonical emitter. The exit work
CLEAR remains paid; no full supplier, frame, host, analytic or all-size replay
is claimed. `VALIDATION.json` records completed checks and omissions. Selected
certificates and `upstream/` are unchanged.

Prepared for @ToikY with substantial OpenAI Codex assistance. Ali Romman's
PR1064 provides the construction and primal/dual certificate. CubeJerry's
PR922/924 supplies the factory, following Alluri PR681 and the retained compiler
lineage. PR949's per-macro floor and PR1032/1033/1036's cache/route classes are
distinct; their searches are not repeated. Exact source and attribution details
are in `SOURCES.json`. New contributions are Apache-2.0.
