# CK cleanup-prefix scalar rewrite

Validation status: independently reviewed and accepted. A fresh, cache-free
Lean 4.27.0 replay reported `PASS_CLEANUP_PREFIX_LEAN` in 43.725 seconds.
The review's exact-version runner finding R1 was fixed and its focused controls
passed; the reviewed proof and generator bytes are unchanged. See
`ACCEPTANCE.json` for the final disposition and `FINAL-REVIEW.json` for the
historical review that found R1. This is local validation, not hosted CI or a
full supplier replay.

The final narrow metadata refresh in `OVERLAP-FINAL.json` reaches PR #833.
It found no direct duplicate in the inspected keyword results and newest
20 PRs; it does not establish absence of unpublished or differently named work.

This package formalizes the scalar rewrite used by the CK provider selected at
the research base. Its `hyperplane_end` step moves selected commuting cleanup
gates to the front in recipe order and retains the other gates in their original
order. It proposes no new κ and does not formalize integer multiplication.

The universal proof is in `CleanupPrefix.lean`. Its `extract_in_context` theorem
allows arbitrary preceding and following scalar programs, arbitrary register
states, and one arbitrary scalar coefficient per original instruction index.
The checked extraction result is the hypothesis connecting the finite instance
to that theorem. Self-adds are supported in the disjoint branch. Recipe indices
are not sorted.

The scalar abstraction assumes only associative and commutative addition;
multiplication is arbitrary. A concrete `Int` instance is included. No formal
`Rat` or `Complex` instance is claimed.

## Reproduction and evidence

Run the source binding alone, offline, with Python 3.10+ and its standard library:

```sh
python3 -I -B research/cleanup-prefix-lean/check_source.py
```

`check_source.load_fixture()` returns the validated `CK-FIXTURE.json` object for
the Lean runner. Each cleanup gate records `kind`, `target`, optional `source`,
and the exact normalized numerator/denominator; `selected_indices` preserves the
recipe order. Lean quantifies coefficients per instruction index, so it proves a
stronger statement than checking only these rational coefficients.

With Lean 4.27.0 installed, run the complete proof and axiom audit:

```sh
python3 -B research/cleanup-prefix-lean/run.py
python3 -I -O -B research/cleanup-prefix-lean/review.py --source-binding
python3 -B research/cleanup-prefix-lean/test_runner.py
```

The runner checks the source and generated `CKFixture.lean` against the current
fixture before building; it does not download or change a global toolchain.
It automatically finds the cached pinned Lean 4.27.0, or accepts
`--lean-bin /path/to/lean-4.27.0-linux/bin`.
The independent review's coverage and limits are in `REVIEW.md`.
The original clean-build output is retained in `evidence/lean-clean.txt`.
The version controls accept the exact release and reject prerelease/build
suffixes before source checks or compilation. These controls use temporary
tool stubs; the independent clean replay used the real pinned release.
A source-check pass alone is not a Lean-build pass. The source check
compares its complete recomputed receipt with `SOURCE-RESULT.json`; it does not
silently regenerate expected evidence.

Actual CK coverage is **2,869 cleanup gates**, **34 selected gates**, **19,084
original-prefix pairs**, and **68 distinct selected registers**. Eight prefix
pairs share a register; all others are disjoint. The actual indices descend
from 664 to 448, with gaps. The source checker includes five positive scenarios
and thirteen rejection controls. `SOURCE-RESULT.json` records all shared pairs,
indices, rejection reasons, and the four exact noncommuting witnesses.

The concrete Lean bridge splits the word without reducing its coverage:

- `CK.checked` kernel-checks `sourceExtract` on the initial **665 gates**,
  containing every selected index and all **19,084 original-prefix pairs**.
- A bounded-index lemma proves that the **2,204-gate suffix** is unselected.
  `CK.stable_remainder` covers the stable remainder of the full original cleanup.
- `CK.scalar_rewrite` covers **all 2,869 gates**, with arbitrary preceding and
  following programs, coefficients and initial states.
- `CK.source_coefficient_rewrite` uses `rationalPalette` and `coefficientCodes`
  to retain the exact source numerator/denominator pairs losslessly. Their
  compression does not approximate coefficients. The interpretation of those
  pairs is a parameter; this is not a claimed formal rational/complex instance.

The final axiom audit reports only `propext` and `Quot.sound`; `CK.checked`
depends only on `propext`. The finite extraction premise is kernel-checked,
without `native_decide`.

`SOURCE-VALIDATION.json` records normal and optimized Python source checks,
an optimized replay from an unrelated working directory containing only this
checker's files and seven pinned inputs, successful gzip recompression, and
rejection of independently corrupted source, fixture, payload and result bytes.
This is local source-bridge evidence; it does not assert hosted CI or a full
supplier/repository-suite pass.

The completed independent source-binding review in `REVIEW.md` confirms all
716 input columns of the original and extracted full cleanup maps. It also runs
the original pinned `build_hpe.apply` on the retained word and recipe and
reproduces the expected HPE output hash, including the constructor's finite
helper/frame/profile guards. Eight corruptions and five schema/domain controls
are rejected; equivalent gzip recompression and negative-denominator
normalization are accepted. The command above reports nested status
`source_binding.status = PASS_INDEPENDENT_CK_SOURCE_BINDING_REVIEW` and also
runs the earlier independent finite review (14,400 pairs, 8,529 extraction
combinations, 555 admitted unsorted recipes, six weakened-rule counterexamples
and seven constructor-guard rejection controls). These are completed finite
review results, separate from the completed final Lean build and axiom audit.

## Exact object and source chain

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Selected at the research base, #626: `660de893d27bb7abd1d5b01b1640207528a5c851`.
Underlying #622: `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
Assignment seed 76 selects CK from `[CK, JP8]` by `76 % 2`.

This is a **baseline-bound audit of #626**, not a claim about the latest selected
frontier. Before publication, upstream main advanced to
`abdc6a7002abdbcd9e21bfc5e1a795784deacfdf` and selected #942. The original
`certificates/selected-result.json` bytes are preserved here as
`BASE-SELECTED-RESULT.json`, obtained with `git show` at the research base.
Their unchanged SHA256 is
`b3bf402f31a69bde0629936a9b569bed48281568d7b16d5fba120b5311ea1f53`.
The checker reads and pins this snapshot; the live
`certificates/selected-result.json` is not an input. All six other source pins,
the source-manifest links, construction pins and proof fixtures are retained.

The focused portability check is reproducible without changing any input files:

```sh
python3 -I -O -B research/cleanup-prefix-lean/check_source.py --portability-controls
```

It intercepts reads in memory: a later selection record or an absent live record
must leave the fixture unchanged, while corrupting the baseline snapshot must
fail its exact source hash. A separate isolated replay also used the actual
selection bytes from the newer upstream commit above. Generator consistency and
unchanged fixture/Lean/generator hashes were checked; this metadata-only binding
correction did not require another Lean build.

The frozen source root is `research/complex-k492-owner-repair/`:

- `code/build_hpe.py`, especially `commute` and `apply`;
  SHA256 `ba2001695d8c7547a82260c3b016e01dac686e95a61757ca124eb9879078ea8e`.
- `data/SPEC.json`, CK typed construction chain;
  SHA256 `2a2577ac526535826fed9d5f7f83f6e2e0ec058a146c64f7286720b995fa2323`.
- `data/recipes/k492-ck-hyperplane_end.json`;
  SHA256 `c71c2b05550544c29ebb4696e63cffc44d6daa76f1bc25e9c7c97e994b2c7657`.
- Pre-HPE raw word: output of CK step 5 (`frame_regroup`), input of step 6
  (`hyperplane_end`); decompressed SHA256
  `b19c9c7cf895e31cd0afd12e5226cd0c917fac387bf7b12533437141790845c8`.
- Expected HPE output, recorded by both recipe and SPEC:
  `93228917343883327493cf8e8af68be06251be4db719039ae3ca8d54595f2be6`.

`CK-PRE-HPE.json.gz` retains that compact intermediate input, absent from the
retained replay directory. It was obtained by a bounded construction-only
reconstruction: PR558 baseline constructors, CK 504-helper shadow stages,
K-triangle constructor, five port stages, then frame regrouping. Every resulting
word matched its existing SPEC decompressed-content pin. This did not run the
full supplier/native/global replay. Reproduction of this proof package needs
only the retained input, not those constructors. Gzip headers are not a proof
identity: the checker hashes the decompressed bytes.

`SOURCES.json` binds the frozen source files, the baseline selection snapshot
and its selected source inventory. The checker verifies chain adjacency from the K-triangle base through
the final cold-end word and matches the HPE input/output/recipe pins. It does not
re-prove preceding construction stages or the later cold-end refactor. The final
#626 canonical cleanup is a later word; it is not confused with this HPE
input.

## Independent finite checking and trust boundary

The checker imports no constructor, production commutation function, or
on-register index. It scans **every original skipped-prefix position**, including
other selected gates, checks distinct/in-range selected indices and pairwise
disjoint selected register sets, checks each selected entering helper's unique
cleanup touch, and preserves actual recipe order. All cleanup gates have exact
shape, integer register, and rational coefficient validation; negative raw scale
denominators are normalized as exact fractions rather than incorrectly rejected.

For every checked gate pair a second method executes both orders on each basis
vector of their touched-coordinate union using `Fraction`. This finite matrix
comparison is independent of the syntactic predicate; neither is used as a
substitute for the universal Lean theorem.

Positive controls include shared-read adds, same-target adds, a disjoint
self-add/scale pair, and reversed recipe order. Negative controls contain exact
basis-vector counterexamples for source writes, source/target scaling and a
self-add dependency. They also exercise a source-scaling mutation inside an actual
CK skipped prefix, duplicate and out-of-range selections, boolean indices,
unknown gates, invalid coefficients, zero scales and invalid registers.

The **concrete CK fixture parser rejects zero-scale coefficients** because this
retained cleanup has nonzero scales. The **generic forward scalar semantics
permits zero scales and self-add annihilation** (`x[t] += -1*x[t]`).
Invertibility is **not** an assumption of generic forward equality. The stronger
fixture-domain check does not restrict the universal theorem. No inverse or
inverse-transpose conclusion for singular coefficients is inferred.

There are two distinct assurances:

1. Lean's kernel checks the generic semantics theorem and the generated finite
   extraction premise, with no `native_decide` required.
2. Python checks hashes, parses the pinned JSON, validates the fixture, and
   supplies the generated Lean literals. This extraction/source bridge remains
   trusted executable code and is independently reviewable. A source hash does
   **not** formalize Python, JSON parsing, or the producer implementation.

The proof is about scalar program equality, not frame legality, paid profiles,
phase/wrapper realization, dirty restoration of the complete supplier, physical
hosting, common labels, mutable bases, recursion, precision, tapes, residuals,
analytic transfer, or the complete multiplication theorem. Those assumptions and
obligations remain with the baseline #626 construction. No practical speedup or new
optimality result is claimed.

## Prior work, overlap and candidate selection

The existing written commutation argument and finite controls are retained in
`PROOF-COMMUTING-PREFIX.md`; PR601 introduced this prefix relaxation and PR608
independently constructed it. PR593/599 formalized helper-label/tail interfaces,
which consume scalar hypotheses. This package adds a universal proof of the
specific scalar rewrite and a source-bound CK instance selected at the research base.

The initial scout considered three obligations:

1. **Chosen:** `build_hpe.py` commutation and arbitrary-order prefix extraction.
2. Dead-register absorption in `code/build_cold_end.py:83–97`: a no-touch suffix
   invariant and zero extra frame climb. Existing proof notes and controls cover
   it; PR729 audits helper-frame lifetimes and PR745 independently checks JP8
   endpoints. This candidate was not implemented.
3. First K-triangle (`p=[0,1], e=-1`, 30 reads) in `data/TRI-SCHEDULE.json`: sparse
   rational substitution plus chronological span certificates. PR687 already
   gives a scoped negative relocation result; PR683 treats partial K/M bypass
   barriers. This candidate was not implemented.

The scout inspected 614 open PRs through #794. Immediately before implementation,
a public unauthenticated GitHub search for repository PRs containing both
"commuting" and "prefix" returned 17 results, including #601/#608, #710, #722,
#754 and #793. These cover existing constructions or cleanup improvements, not
this source-bound universal Lean extraction proof. No pinned sprint coordination
issue was found; the only repository issue was #650 (Discussions). `CLAIM.json`
records the local claim. This is a dated overlap check, not a guarantee about
later submissions.

The follow-up snapshot in `OVERLAP.json` records its UTC time, exact public API
queries, returned counts, PR heads and scope assessments, with newest open PR
metadata through #811. Relevant neighbors include #719's CK cleanup obstruction,
#722/#787's coefficient sharing, #793's JP8 compensation batching, #807's CK
helper-basis rewrite and #811's JP8 additive coefficient routes. Their reported
finite circuit scopes differ from this source-bound universal extraction proof;
no direct duplicate was identified in the reviewed metadata. This refresh is
keyword/metadata reconnaissance, not a code audit of all PRs. One broad query
returned only 100 of 122 matches, and unpublished claims are inaccessible.
The original `CLAIM.json` is preserved unchanged.

Evidence links: [PR601](https://github.com/CrocSwap/integer-mult-bounds/pull/601),
[PR608](https://github.com/CrocSwap/integer-mult-bounds/pull/608),
[PR729](https://github.com/CrocSwap/integer-mult-bounds/pull/729),
[PR745](https://github.com/CrocSwap/integer-mult-bounds/pull/745),
[PR687](https://github.com/CrocSwap/integer-mult-bounds/pull/687),
[PR683](https://github.com/CrocSwap/integer-mult-bounds/pull/683).
