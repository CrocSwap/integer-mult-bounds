# Bounded coupled search: numerical no-gain result

This is optional discovery evidence for the fixed binary contract in PR4994.
It does not strengthen the written interval theorem into an exact global
optimality proof and establishes no new κ. The registered standard-library
replay does not install or run this solver.

The model includes all 4,684 marginal subspaces at the 1,339 flexible contacts,
with every mapped containment constraint. It has 9,276 binary variables,
9,432 rows and 41,952 nonzeros. One-hot variables select contact subspaces;
compatibility rows reject incompatible neighboring choices. Additional binary
selectors encode each edge's integer rank difference. Edges with a rigid end
contribute directly to a contact's cost. Fixed edges and the eight rank-eight
owned jobs are included in the objective offset.

At price point a=15108879/5000000000 the solver maximizes the discount
`sum_r n_r (r-r^(1-a))`. Total rank is fixed, so this corresponds to minimizing
the recursive child price. The coefficients are evaluated with 80-digit Decimal
arithmetic and converted to floating point for HiGHS. This price point is a
parameter of the screen, not a selected-result claim.

The source warm start satisfies every model row and matches the independent
native replay's complete child profile before the solve starts. The returned
subspaces are checked with exact graph constraints, then realized and executed
by the separate rational free-word interpreter in both orientations. Forward
and backward live contacts are aligned by ordinal; each direction keeps its
own fixed contacts because their whole-node numbering differs. Both exact
replays must pass for a completed report. The raw assignment is saved before
these dependent checks so a validation failure cannot silently lose the witness.

## Retained outcome and limits

`RUN.json` records HiGHS 1.15.1 / numpy 2.5.4. With one thread and a 60-second
limit, the solver returned the original source assignment: **zero changed
contacts** and the same paid profile in both orientations. The run took about
18 seconds including construction and exact revalidation. HiGHS reported
`kOptimal` after one branch-and-bound node. Its floating objective was
10.289699734432697 versus source 10.289699734432695; the exact profiles agree,
so this rounding difference is no mathematical gain.

`MODEL.mps.gz` is the named-row/column model, `VALUES.json.gz` is the returned
forward node assignment, and `HIGHS-LOG.txt` retains the solver report with trailing whitespace removed. RUN.json
binds the executed script, source modules and source manifest by SHA256. These
are numerical run records, not a rational dual, proof tree, or exact comparison
of all feasible assignments at real-power prices. Source feasibility and its
returned endpoints were checked exactly; solver global optimality was not.

## Reproduce separately

Use Python 3.12 and the pinned discovery requirements. For example, installing
only into a temporary RAM directory on Linux:

```sh
python3 -m pip install --no-cache-dir --only-binary=:all: --target /dev/shm/carried-solver -r research/carried-warp-frame-intervals/discovery/requirements.txt
python3 -I -B research/carried-warp-frame-intervals/discovery/search.py --solver-path /dev/shm/carried-solver --output /dev/shm/carried-search-run
```

An existing environment with those versions can omit `--solver-path`. Use a new
output directory; the retained record directory is rejected. The optional
`--time-limit` is positive and at most 600 seconds, with default 60. Reproduction
writes fresh reports and candidate words in that separate directory. Run times,
MPS formatting and floating traces are not cross-platform mathematical invariants.

The [HiGHS Python interface](https://ergo-code.github.io/HiGHS/stable/interfaces/python/)
and [official examples](https://github.com/ERGO-Code/HiGHS/blob/master/examples/call_highs_from_python.py)
were consulted for the solver API. No solver binary is vendored. New script and
records: 1337isnot1337 with substantial OpenAI Codex assistance, Apache-2.0;
the source/provider attribution in the parent README remains unchanged.

## Next decision

Do not repeat the unchanged coupled screen as evidence of new progress. An exact
certificate is a different useful task: first test a stronger local-pair LP
relaxation and attempt to extract a checkable rational dual. Otherwise change a
named word, map, helper boundary or ownership premise. Any favorable new child
profile still needs physical phases and the complete controller/compiler bill.
