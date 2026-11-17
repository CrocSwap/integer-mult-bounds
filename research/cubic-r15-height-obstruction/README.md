# Two small query directions cannot repair the arity-15 cubic reader

This result was produced by Nick Petalas. Apache-2.0.

**Finite certificate with a scoped algebraic proof.** Every exact three-query
dyadic repair of the fixed cubic reader at arity 15 needs at least two source
directions whose primitive integer coefficient height exceeds 64. The third
direction has no height bound in the check. This does not settle whether three
queries exist, prove a four-query lower bound, or improve kappa.

A dyadic source row is normalized to a signed primitive integer pair (a,b),
with a>0 or a=0<b. Its height is max(|a|,|b|). The statement applies to
arbitrary invertible dyadic source changes, not only monic forms or shears
that keep the original b fixed. The incoming y,a,b are arbitrary. The
fifteen original children remain in order. Source changes act on a,b alone;
both sources must be restored, and queries are fixed dyadic weighted cubes
without output feedback.

The new step is an exact reduction from any two query directions to their
only possible third direction, followed by two complete finite checks.
There are 5,040 canonical primitive rows in the height-64 box and 12,698,280
unordered pairs. Both checkers find zero admissible dyadic triples. The
primary census rejects 17 pairs because their third direction repeats one
of the pair and 12,698,263 because a forced weight is not dyadic. It finds
no pair with an undetermined third direction. These counts enumerate the
stated pair domain only.

[PROOF.md](PROOF.md) proves the unrestricted-third-row reduction and the
connection to source-restoring programs. `verify.py` uses a homogeneous
annihilating-cubic condition and exact forced weights. `independent.py`
changes to the two selected source coordinates and compares the mixed
coefficients there. It imports neither the primary checker nor predecessor
code. Both checks cover the full pair domain; both include positive
certificates with an unbounded third row and pure-B directions, along with
non-dyadic and defect controls. Finite execution supports the stated finite
exclusion; independent human and formal proof-kernel review are unclaimed.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cubic-r15-height-obstruction
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/cubic-r15-height-obstruction/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/cubic-r15-height-obstruction/independent.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cubic-r15-height-obstruction --check-source-history
```

The registered manifest runs both complete checkers normally and under `-O`.
Each command has a 300-second bound. Expected markers are
`PASS_CUBIC_R15_HEIGHT_OBSTRUCTION`, `PASS_CUBIC_R15_INDEPENDENT`, and
`PASS_REGISTERED_RESEARCH_PACKAGE`. Every run must report 12,698,280 pairs
and zero admissible triples. The primary has eight control fixtures; the
coordinate checker has fourteen, including nine substitution fixtures.

Source documents are bound to canonical main
`e54523517d0f03e58352e647c403a5af3e525a57` in [SOURCES.json](SOURCES.json).
They are read-only inputs to metadata authentication; their scientific
executables are not run. The selected record and original card are historical
provenance. Revision 8's assessment predates the selected #7000 record;
the cheap selected source-binding orientation passed, without a supplier replay.

## Local verification and CI limitation

Both full checks passed in normal and optimized mode under CPython 3.12.
The four timed direct runs took 16.79, 17.04, 16.28 and 16.00 seconds,
respectively. These are command-duration records for the replay budget,
not performance-comparison claims. Each run visited all 12,698,280 pairs.

The unchanged base has a separate CI navigation failure. The six-test
`test_research_current_status.py` module has one failure because
`test_current_ci_section_matches_selected_record` expects
`make frontier7000-verify`, while `docs/ci-verification.md` still names
#6030. The same final test failure appears in the hosted planning jobs for
[#7475](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/43291062509/job/131437108801)
and [#7478](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/43291772301/job/131439552156).
Those logs were read; their research results were not replayed. This package
leaves that shared documentation and its test unchanged. Hosted success for
this contribution is unclaimed.

## Overlap coverage

Live PR title/body searches included the exact arity, cubic repair, general
frames, coefficient height and general-arity variants, alongside main-branch
README searches. The task overlap helper fetched all 800 open PR records and
7,396 Discussion records at the reported snapshot, but its sparse local scan
covered only 222 of 10,178 tracked note paths. Relevant cubic packages were
materialized and main was searched directly. No duplicate pair-height
exclusion was found within that coverage. This is not a novelty certificate
or a claim about private work or every historical code diff.

## Limitations and expansion decision

This is a local coefficient obstruction. No attaining r=15 word, priced
query or shear, complete caller invoice, restoration implementation, native
backend, routing, precision/storage or new selected assumption is supplied.
A finite exclusion with two bounded directions is stronger than a search
that bounds all three, but it is not an unrestricted nonexistence theorem.
Height 64 is not claimed to be sharp. The three-versus-four dyadic query
minimum remains open. No selected scientific cold replay, Lean or Docker
run is needed for this isolated result, and none was run.

Stop this construction attempt at the proved finite exclusion. Further
searches must allow at least two larger primitive directions and still need
an exact identity and legal restoring schedule before physical pricing.
This package does not authorize a larger dependent implementation campaign.

The checkers have no recursion or external solver. Their fixed loops visit
5,040 rows, 12,698,280 pairs and at most three weights per pair. Per-pair
state is local. Python and Fraction allocate dynamically, a managed-runtime
deviation from fixed-allocation guidance; the fixed input box bounds the
integer sizes and live storage. The primary third-row coordinates have
absolute value below 2^26, and the separate coordinate check uses fixed-degree
integer formulas. Warning-strict normal and optimized executions provide the
available interpreted-language diagnostics. No repository-wide changes are made.

## Open next questions

1. Does arity 15 have an exact three-query dyadic repair with at least two
   primitive directions above height 64? Start with larger primitive pairs
   or a global valuation restriction on one common rational triple. An exact
   identity and source-restoring schedule are the missing obligations.
2. Can an unbounded family of pairs be excluded algebraically? Start with
   odd prime factors of the three forced denominators. The present finite
   domain alone does not control arbitrary coefficient height.

These questions are open, not reserved follow-on work. Structured first steps
and blockers are also recorded in [TASK.json](TASK.json).

## Credit and related open work

The immediate source question is Armin Pourshafeie / apoursh's
[PR #7475](https://github.com/CrocSwap/integer-mult-bounds/pull/7475),
head `ee81d7e993025b62983ac3def76991af1a58eb01`. Its three-query construction
at r=24 is cited, not replayed. The arity-15 opening predates that work in
Nick Petalas's #6653. The fixed cubic reader and defect are from Nick Petalas's
#6200; the dyadic general-frame contract and query lower bound are apoursh's
#6212. The finite-slope node lemma is Nick Petalas's #6653. Its integer-direction
search did not cover the general primitive rows excluded here.
apoursh's #6215 already excludes every r=15 three-query repair containing a
pure-original-B query. The new exclusion also covers pairs of two non-pure-B,
nonmonic directions. The classical annihilating-form and coordinate-change
methods are not claimed as new general mathematics.

- [#7475](https://github.com/CrocSwap/integer-mult-bounds/pull/7475) constructs
  an exact three-query dyadic repair at arity 24; this package excludes small
  pairs at arity 15, without recomputing the arity-24 result.
- [#7478](https://github.com/CrocSwap/integer-mult-bounds/pull/7478) classifies
  fixed equal-weight repairs by a Pell recurrence; this package allows every
  dyadic weight within its stated pair domain.
- [#7479](https://github.com/CrocSwap/integer-mult-bounds/pull/7479) establishes
  three-query solvability modulo every odd integer; this package constrains
  one exact global representation and does not contradict modular solvability.

All predecessor attributions and frozen files remain unchanged. The new pair
exclusion and its two complete checkers are the contribution here.
