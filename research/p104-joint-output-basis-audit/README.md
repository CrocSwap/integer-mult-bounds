# Independent rational audit of PR6353's nine output contractions

This source-bound audit checks the **rational scalar projection**, not supplier
admission or a new κ. The selected PR6030 record remains authoritative.

## Result and evidence

The frozen PR6349 source and PR6353 output word have the same 770-by-770 public
transfer matrix over Q: 592,900 coefficient positions, with 874 nonzero entries.
Two separate standard-library implementations establish this: `verify.py`
propagates sparse public basis rows forward; `oracle.py` pulls every output
functional backward. Neither imports a supplier constructor or author checker.

The primary checker derives the 4,607 ZERO-preparation gates from the actual
source transpose. It independently checks the 17-gate B0, 37-gate B2 and three
departure blocks, all nine anchor identities `row_a(C A) B0 B2 = e_a^T`, all 19
nonzero response rows, nine zero **dual preparation** temporary rows, and exact
basis inverses. The 381 full ZERO-to-FULL helper channels are a subset of the
562 non-main public helper roles. They must not be conflated.

The literal words retain all original input frames and original frame vectors.
Exactly nine forward output frames contract: one from rank nine to five and
eight from rank nine to eight. This is a finite frame-subspace check; scalar
MOVE is the identity and does not certify a native transport operator.

The oracle also independently checks that all 24 source COPY destinations are
zero before overwrite. Its four literal omission controls remove an input-basis
gate, departure inverse, dirty-carrier subtraction, or output inverse. Each
produces an explicit input/output coefficient counterexample in `ORACLE.json`.
Additional primary basis/response/interface controls are in `RESULT.json`.

**Erasure boundary:** the nine added forward CLEAR rows are nonzero scalar
functionals, with supports 116, 4, 110, 106, 8, 109, 100, 4, 110. Their full
rows are retained in `ORACLE.json`. They are distinct from the nine dual
preparation zeros. The forward scalar model discards CLEAR rows; endpoint
equality therefore proves no physical erasure permission. This is a scoped
clarification, not a counterexample to the author's native erasure framework.

## Exact sources and reproduction

The scientific predecessor is Ali Romman's PR6353 at
`db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3`, whose scientific artifacts match
`18cf11a6c411962494c7c4328818767bc8bb3533`. Its source is PR6349 at
`af7cb6c67f8fc7d82a2e4aee2dd2f07481bf6690`. The retained input word is present
at canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

`SOURCE-PINS.json` records original paths, commits, Git blobs and SHA256 hashes
of the five byte-exact vendored inputs. Both checkers independently hardcode
their authentication. The upstream proof is retained as a source statement,
not imported proof evidence. These package-local copies make scientific replay
independent of pending foreign Git history or network access. `SOURCES.json`
separately pins the historical task catalogue and selected record at the base.

With Python 3.12, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-joint-output-basis-audit --check-only
python3.12 -B scripts/research_package.py --package research/p104-joint-output-basis-audit
```

Standalone replay also works in a Git-free copy:

```sh
python3.12 -I -O -W error -B research/p104-joint-output-basis-audit/verify.py
python3.12 -I -O -W error -B research/p104-joint-output-basis-audit/oracle.py
```

Default execution strictly compares the computed receipt with retained
`RESULT.json` or `ORACLE.json`, preserving JSON value types. `--emit` prints a
fresh candidate without checking the retained receipt; it does not write files.

## Open next questions

This resolves the finite rational basis/public-boundary obligation only.
Native absolute phases and all operator columns, physical erasure, complete
caller behavior, paid/productive accounting, ordinary/outer admission, uniform
compiler, precision tape and analytic recovery remain separate obligations.
No full native replay, accepted supplier, improved κ or multiplication theorem
is claimed. All five inherited framework assumptions remain.

The two structured questions in `TASK.json` identify the next native-operator
and complete caller/invoice checks, their first steps and blockers. Start with
the nine exact changed output frames; do not treat these rational receipts as
admission of those interfaces.

## Credit and coordination

Construction credit stays with Ali Romman (substantial OpenAI Codex assistance),
PR6349/6348/6350, DreamingOfClouds's PR6314 work with Claude Opus 5.5, Cinna
Davis / 1337isnot1337's productive caller and thin-query interface, and the full
retained [upstream NOTICE](sources/NOTICE) chain. New independent checkers and
proof review: ToikY with substantial OpenAI Codex assistance, including three
bounded subagents for the primary checker, independent oracle and mathematical
review. Apache-2.0.

The canonical claim is [Discussion5645 comment19343025](https://github.com/CrocSwap/integer-mult-bounds/discussions/5645#discussioncomment-19343025),
taking the released [handoff19342830](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19342830).
Live overlap was bounded, not a novelty certificate. `TASK.json` records the
task refinement and `VALIDATION.md` records final verification and freshness.
