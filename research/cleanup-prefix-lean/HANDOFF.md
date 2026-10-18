# Handoff: source-bound CK cleanup-prefix scalar proof

**Status:** accepted local independent verification/formalization contribution.
Source binding, finite independent audit and a cache-free Lean build passed;
the latter reported `PASS_CLEANUP_PREFIX_LEAN` in 43.725 seconds. The runner's
exact-version finding R1 is fixed and its targeted tests pass. `ACCEPTANCE.json`
records the final disposition without overwriting the original review.
Prepared for one focused GitHub pull request, with a clean patch against the
base below as a second delivery format. The accompanying publication receipt
records the final PR URL.

The CK `hyperplane_end` builder selected at the research base moves cleanup gates past commuting
prefixes and emits selected gates in recipe order. Existing written arguments
and finite replays justify this mechanism. This package targets the missing
universal scalar semantics proof of that exact rewrite, together with a binding
to the actual baseline #626 pre-HPE word. It preserves arbitrary recipe order,
disjoint self-adds and all initial scalar register states.

The concrete fixture contains 2,869 gates and 34 selections. The checker covers
all 19,084 original-prefix pairs, retains exact rational coefficients and binds
the full intermediate input by its existing SPEC hash. An independent review
compares the full original/extracted cleanup maps on all 716 input columns and
reproduces the expected HPE output using the pinned original builder. Eight
corruptions and five schema/domain controls are rejected. Normal/optimized,
isolated and recompressed source checks pass.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Selected at the research base, #626: `660de893d27bb7abd1d5b01b1640207528a5c851`.
Exact dependencies and input hashes are in `SOURCES.json`; seed 76 selects CK.

Publication portability: this audit remains bound to base #626 after upstream
main `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf` selected #942.
`BASE-SELECTED-RESULT.json` preserves the original base certificate byte for byte
(SHA256 `b3bf402f31a69bde0629936a9b569bed48281568d7b16d5fba120b5311ea1f53`).
The checker pins this snapshot instead of the floating repository selection.
All other source/construction pins and proof fixtures remain unchanged.

## Reproduce

```sh
python3 -I -B research/cleanup-prefix-lean/check_source.py --portability-controls
python3 -I -O -B research/cleanup-prefix-lean/review.py --source-binding
python3 -B research/cleanup-prefix-lean/run.py
python3 -B research/cleanup-prefix-lean/test_runner.py
```

The proof, source and independent checks completed successfully. After the
version-gate-only correction, the leader replayed its focused tests and verified
all reviewed proof, fixture and generator hashes unchanged; no redundant proof
rebuild was performed. The Lean runner automatically
finds the cached pinned Lean 4.27.0, or accepts `--lean-bin /path/to/bin`.
`CK.checked` covers the initial 665 gates and all prefix pairs; a bounded-index
lemma excludes the 2,204-gate suffix from selection. `CK.stable_remainder` and
`CK.scalar_rewrite` cover the full 2,869-gate cleanup. Exact source coefficients
are retained by `rationalPalette` and `coefficientCodes`. Axioms are only
`propext` and `Quot.sound` (`CK.checked`: only `propext`).

## Scope and credit

No new κ, full multiplication proof, physical/frame/accounting certification or
runtime improvement is claimed. Python parsing, hashing and generation remain
an explicit executable trust boundary. The fixture rejects zero scales, while
generic forward semantics permits zero scales and self-add annihilation:
invertibility is not required for forward equality. No singular inverse claim
follows.

The scalar abstraction requires associative/commutative addition and places no
laws on multiplication. A concrete `Int` instance is included; no formal `Rat`
or `Complex` instance is claimed.

Credit PR601/608's commuting-prefix constructions, PR593/599's HPE proofs,
PR622/623/626's selected supplier lineage and all predecessors in `NOTICE.md`.
Substantial OpenAI Codex assistance and separate AI review are disclosed.
The dated public refresh in `OVERLAP.json`, through newest PR #811, found related
finite circuit work but no direct duplicate in reviewed metadata; its keyword,
first-page and unpublished-claim limits remain explicit. The original local
claim is preserved with a final result appended. Publication is recorded separately.

`OVERLAP-FINAL.json` adds the final narrow metadata refresh through PR #833,
with complete results for two keyword queries and the newest 20 open PRs.
No direct duplicate was identified in this inspected metadata.

The baseline-binding correction passes focused source and generator-consistency
checks. Later/current or absent live selection metadata leaves the audit
unchanged; snapshot corruption is rejected. Exact hashes of `CK-FIXTURE.json`,
`CKFixture.lean`, `CleanupPrefix.lean` and `generate_lean.py` are unchanged.
No redundant Lean build was run for this correction. The independent focused
review accepted it with no remaining findings; see `PUBLICATION-REVIEW.json`
and the publication addendum in `ACCEPTANCE.json`.
