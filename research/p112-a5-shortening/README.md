# P112 A5 shortening beyond the coordinate bound

The actual ten-piece TWOSIDE `(6,4)` profile `2,5^2,6^6,7` is impossible
over every characteristic-zero field. Delete its last piece first. The
remaining nine independent pieces still need five code dimensions; their
six normalized endpoints require **128 support incidences against allowance
120**. The earlier coordinate inequality gives only `795<=800` here.

The general lemma requires all pieces to be collectively independent. It allows
any number of small pieces whose common support union has size at most 29,
followed by six pieces of support at most twenty. Their span has code-intersection
dimension at most four. The exact A5 count is still `122>120` at support 29. Support 30
is a failed proof boundary, not a counterexample or a claimed sharp code bound.

The new result is the general shortening contract and this actual-profile
application. Nick Petalas/PR3188 supplies the A5 spectrum; PR3195 supplies
the earlier deletion slice. PR3197's separate support 24 application is
credited. [PROOF.md](PROOF.md) gives every hypothesis, the field-extension
argument and the distinction from those predecessors.

The result advances one finite decoder-floor case. Full C5, `C(P112)>=64`,
supplier admission and an improved kappa remain open. The selected frontier
is unchanged. Evidence is author-checked with internal read-only review;
independent human and proof-kernel review are separate.

## Evidence and reproduction

From the repository root, with Python 3.12 and its standard library:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/a5-shortening-replay"
mkdir -p "$RUN"
TMPDIR="$RUN" python3.12 -W error -B scripts/research_package.py \
  --package research/p112-a5-shortening
```

`uv run --python 3.12 --no-project python` can replace `python3.12`.
The registered replay authenticates its inputs before importing geometry,
reconstructs the P112 labels, exhausts the five-/six-flat capacities, checks
all root planes and complete A5 extension orbits, binds the original
historical profile, and compares [RESULT.json](RESULT.json). Eighteen behavioral
groups include separate explicit-star and cut counts, proof boundaries,
source/receipt corruption, ambient-module collisions, complete historical-table
validation, and child failure/timeout controls.

The direct mathematical replay needs no Git, network or third-party package
when the package and its two declared inputs are present at their repository
paths. To write a fresh external receipt, use an absent path:

```sh
python3.12 -W error -B research/p112-a5-shortening/verify.py \
  --output "$RUN/fresh-result.json"
```

Existing outputs and checkout outputs are refused. Without `--output`, replay
writes no receipt. [SOURCES.json](SOURCES.json) pins exact base, source blobs,
hashes and lineage; [VERIFY.json](VERIFY.json) declares all live inputs.
[CHECKS.json](CHECKS.json) records actual checks and limits.
[ENGINEERING.md](ENGINEERING.md) records implementation bounds and deviations.

## Open next questions

Can a named actual caller with support budget 30 be treated using its full
support 70 edge alphabet? First verify its quotient hypotheses and audit the
D7 branch. The current root-only argument and strict relaxed endpoint count
both fail there, so a larger numerical allowance alone is not justified.

What remains of C5 after reconciling public exclusions at exact heads?
Compare their precise premises with the original ledger before claiming
another profile as new. This package does not establish the complete current
residue count. Structured questions and blockers are in [TASK.json](TASK.json).

## Sources and credit

Nick Petalas contributed the support 29 shortening statement, its support 26
application and this replay. DreamingOfClouds/PR3154 at
`708f0ad8928c383de8294aea3c126e9461d2066d` supplies TWOSIDE and its historical
filter. Nick Petalas/PR3188 at `93f1fb95a2ab1413b2e9c90a6be4f3a2c4090034`
supplies the A5 spectrum; PR3195 at
`22f1479db213b1ed0de68cbc61ba15f6352d3276` supplies the earlier deletion proof
and retained geometry. PR3197 at `3949cc17a4fa4f108a044f532a5d58323c6cb6d2`
supplies the separate weight-seven deletion application. The star-orbit
algorithm follows retained PR3176 code. Root and label reconstruction retain
PR3161/3162 and the E8/P112 lineage, including joaqcoo's decoder model.

All required provenance resolves through canonical main
`463113d675af7410ac91d53a4fed51ec6494eb9a`; replay does not require unrelated
unmerged heads. Predecessor files and frozen inputs are unchanged. Retained
notices and license are in `vendor/`; new work is Apache-2.0. Development used
substantial automated drafting, internal review and exact finite checks.
The standard Weyl-chamber theorem and the original decoder reduction remain
explicit dependencies. No complete multiplication theorem is claimed.
