# Validation and review scope

Executed on Windows with bundled CPython **3.12.14**. Experimental base:
`abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`; branch
`research/seed58-batched-connector-interface`. Assignment seed 58, from the
operating-system cryptographic random generator; its value selects the
recursive-interface track and rotates the six child lengths.

Commands from the repository root:

```sh
python3 -I -O -B research/weighted-signed-connector-seed58/verify.py
python3 -I -O -B research/weighted-signed-connector-seed58/test_package.py
python3 -B scripts/verify_selected_result.py
python3 -B -m unittest discover -s tests -p test_selected_result.py
git diff --cached --check
```

Expected respectively: `PASS_WEIGHTED_SIGNED_CONNECTOR`,
`PASS_WEIGHTED_SIGNED_PACKAGE` with 47 controls, selected record PASS,
five tests OK, and no whitespace errors. The package uses explicit failure
checks under optimized Python; no mathematical check depends on `assert`.

The independent verifier imports neither generate.py nor predecessor code.
Nomination uses multiset permutations and sign choices; the independent census
uses signed-move DFS. Prefix coefficients and the free noncommutative primitive
interpreter are separate implementations. A direct dense integer backend checks
all input basis columns and an arbitrary dirty fixture for each L=1,2,3 and
every repair. Literal data-head traces agree with a separate formula.

Completed exact coverage: 720 support-bound paths, 60,480 repeated-operator
paths, six minimum words, 288 orbit matrices with 1,728 transformed query words,
all six literal primitive expansions and inverses, 378 dense cases, seven
rational price/tie fixtures, and 18 data-tape trace/formula comparisons.
The scoped positive-price theorem follows from the written lower-bound
reduction and six witnesses, not from the finite price fixtures alone.

The package suite has 47 rejection/boundary controls and reproduces a valid
but nonoptimal 332-call B0-repeat comparator. Isolated optimized-process replay
works after relocation, certificate regeneration is byte-identical, and
corrupted source text/certificate/expected receipt and erased provenance pins
each fail closed.

The full package suite also passed on files exported from the Git index into
a separate directory: verification therefore covers the submitted LF-normalized
bytes. Both artifact writers specify LF explicitly, so Windows and Linux
regeneration retain the same byte representation. PR944 README/notice Git blobs
are respectively `f07370732c8bbe6c49b502308a657a6eb94a019e` and
`037d5c6193921ed1b56038ac0f0d7a5f964aa091`; both match its pinned submission head.

Prepublication metadata refresh covered **752 open PRs through #1083**.
PR1083 formalizes the five-source binary pairing census, a different domain;
PR997 remains the four-by-four Hadamard construction. No overlapping arbitrary-
positive-price signed three-by-three repair was found. Upstream main still
matched the exact experimental base. No pinned sprint board existed.

No repository-wide make verify or cold selected-supplier rebuild is claimed:
this is a standalone research package, with no existing tracked file or
upstream source modified. Relevant local checks and selected-record integrity
are run; no full theorem, human peer review, hosted Linux CI or measured
runtime speedup is asserted. Contributor and AI-assistance credit is in NOTICE.md.
