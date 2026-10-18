# Independent adversarial review: finite, source-binding, and final proof audits

Reviewed source base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Source: `research/complex-k492-owner-repair/code/build_hpe.py`.
SHA-256: `ba2001695d8c7547a82260c3b016e01dac686e95a61757ca124eb9879078ea8e`.

Phase 1 independently analyzes the scalar rewrite and supplies an exact finite
oracle. Phase 3 (below) reviews the completed Python CK source binding. This
review originally left the Lean artifacts and generated instance for the final
proof audit, recorded below. The clean proof is accepted. The later narrow
publication audit also accepts the frozen-baseline binding and confirms the
runner's exact-version fix; see `PUBLICATION-REVIEW.json`. No scalar counterexample to
the source's accepted commutation/extraction rules was found in the stated
finite domain. This is neither a new bound nor a full multiplication proof.

## Required scalar statement

For arbitrary rational register state `x`, addition means the simultaneous
read/write update `x[t] := x[t] + q*x[s]`; scale means `x[t] := q*x[t]`.
All reads use the pre-gate state. In particular, a self-add means
`x[t] := (1+q)*x[t]`. Program lists run left to right.

The predicate at source lines 37–42 is sufficient, not necessary:

1. Neither gate's target occurs among the other's touched registers; or
2. Both gates add to the same target, and neither reads that target.

The first case includes self-adds on registers disjoint from the other gate.
The second case includes equal sources and unequal sources. Two scales of the
same register commute semantically but the predicate rejects them. A zero
addition can commute across a syntactic dependency and still be rejected.
Consequently, the proof must establish **acceptance implies equality**, not an
iff, and cannot silently assume `source != target` for every gate.

No invertibility or nonzero coefficient hypothesis is needed for the forward
rewrite. Zero scales and self-add with coefficient `-1` are legitimate tests
of that broader algebra. An inverse-transpose corollary would separately need
invertibility; these singular boundary tests do not establish that corollary.

For original cleanup list `C` and a list of original indices `I`, the consumer
constructs exactly

```
selected = [C[i] for i in I]
rest = [gate for j, gate in enumerate(C) if j not in set(I)]
rewritten = selected + rest
```

`I` need not be sorted. The actual code emitting `I` is `build_hpe.py:78`;
the consumer preserving this order is
`research/complex-k492-owner-repair/code/hpe_audit_and_transport.py:146–163`.
Frame replacement on selected gates does not alter their scalar fields.

Sufficient hypotheses for the source's scalar rewrite are:

- Every index is valid and appears once.
- Each selected gate commutes with **every** earlier gate in the original
  list, including earlier gates that are also selected.
- The output preserves the exact recipe order for selected gates and original
  relative order for the remainder, without dropping or duplicating gates.

The second condition itself makes all selected pairs commute, so arbitrary
recipe order is allowed. The source imposes the stronger condition that
selected gates have pairwise disjoint touched-register sets (`apply:70`).
This also implies unique selected indices, since every gate has a target.
It must not be confused with checking commutation only against unselected
gates, which is insufficient for arbitrary recipe order.

The source tests only earlier gates found through its `on[r]` incidence
lists (`apply:59–69`). Any omitted earlier gate has disjoint touched-register
sets and therefore satisfies the first predicate branch. A source-bound proof
must justify this implication, or check the full original prefix explicitly
when instantiating a more general theorem. Original indices must not be
interpreted as indices into a progressively shortened remainder.

## Source-binding acceptance checklist

These were the phase-1 obligations. The phase-3 evidence below addresses the
completed Python/source binding; the Lean and generated-instance obligations
remain for final proof review:

1. Identify the actual selected CK **input** cleanup word and HPE recipe from
   the pinned supplier chain, with content hashes for decompressed/canonical
   semantic inputs. An already-extracted output alone does not bind the
   rewrite's premise to its source.
2. Validate and translate every cleanup gate, every scalar coefficient, every
   touched index, and every recipe index without truncation, reordering, or
   unsupported-op fallbacks. Require actual integer indices in bounds and
   nonzero denominators. The Python helper `regs` treats every non-`add` tag
   like scale, so its use alone is not a gate-language validator.
3. Translate both predicate branches faithfully, including self-add behavior,
   and instantiate a theorem quantifying over **all register states**. A theorem
   about syntactic swaps with semantic commutation left as a hypothesis is not
   by itself the requested scalar semantics proof.
4. Bind the exact original selected indices, their original order, and the
   untouched subsequence. Prove or check valid/unique indices and full-prefix
   conditions. A sorted-only theorem is insufficient for the general source
   interface, even if the CK instance happens to be sorted.
5. Compile the final concrete theorem with Lean's kernel; report axioms and
   reject `sorry` or a purported identity introduced as an axiom. Explain the
   trust boundary for any Python-generated declarations and ensure the clean
   command regenerates/checks them from the pinned inputs.
6. Keep source eligibility checks (entering helper, one cleanup occurrence,
   frame join, profile nonnegativity) distinct from scalar hypotheses. They
   support other constructor obligations; scalar equality alone does not
   establish legal physical frames, lifetime guards, paid profile accounting,
   or arbitrary-dirt restoration of the complete invocation.

## Reproduction and finite evidence

From the repository root:

```sh
python -I -B research/cleanup-prefix-lean/review.py
```

Expected status: `PASS_INDEPENDENT_FINITE_CLEANUP_PREFIX_REVIEW`.
Only stdout is written. The script uses standard-library `Fraction` arithmetic
and computes full matrices by executing every standard-basis input. It imports
no supplier arithmetic engine, emitted replay, CK binding, or Lean result.
It extracts the pinned source functions by AST solely to test the actual
predicate and constructor guards against its independent scalar oracle.
Supplier assertions are compiled with `optimize=0`; the review's own checks
use explicit exceptions, so an outer `python -O` cannot disable these checks.

Completed deterministic domain:

| Check | Coverage/result |
| --- | --- |
| Ordered scalar pairs | 14,400 pairs on four registers; coefficients `-2,-1,0,1,2,1/2`; add includes self-add; scale includes zero |
| Predicate acceptance | 8,208 admitted pairs, every full matrix equal after swapping |
| Predicate incompleteness | 2,292 rejected pairs nevertheless commute; no converse claimed |
| Extraction | 8,529 word/recipe combinations: word lengths 0–3 over eight specified gates; every permutation of every index subset |
| Admitted extraction | 2,767 full-map equalities; 1,014 select multiple gates; 555 use unsorted recipe indices |
| Source `apply` | Accepts disjoint multiple moves in recipe order `[3,1]`; oracle verifies equal six-register maps |
| Source rejection controls | Duplicate change; selected gates sharing a source; twice-touched helper; self-add helper counted twice; noncommuting prefix; negative original index; incorrect frame join |

The exact alphabet, gate lists, rational outputs, and differing basis column
for every counterexample appear in `review.py` and its JSON output. This is
exhaustive over the declared finite domain, not arbitrary dimensions or words.
Matrix equality tests arbitrary initial values of **all** represented registers,
not merely clean helper inputs.

Meaningful invalid-rewrite witnesses include:

- `a: x0 += x1`, `b: x1 += x2`. On `e2`, `[a,b]` produces
  `(0,1,1,0)` while `[b,a]` produces `(1,1,1,0)`.
- In `[a, scale(x3,2), b]`, moving `b` first passes an adjacent-only check but
  has the same unequal outputs on `e2`.
- Selecting both `a,b` in recipe order `[1,0]` fails if selected pairs are
  exempted from the prefix test. There are no unselected gates to catch it.
- `scale(x0,2)` and `x0 += x1` yield first coordinates `1` versus `2` on `e1`.
- `x0 += x0` and `x1 += x0` yield `(2,2,0,0)` versus `(2,1,0,0)` on `e0`.
- Duplicating extraction of `x0 += x1` yields first coordinate `2` instead of
  `1` on `e1`.

The source self-add distinction matters: its **commute** predicate admits
disjoint self-adds, but `apply` counts both entries in `regs`, so a selected
helper self-add fails the exactly-one-occurrence guard. These are different
interfaces, not a contradictory test result.

## Finding classification and limits

- **Logical error in source:** none established by this review.
- **Invalid weakened statements:** concrete counterexamples above.
- **Proof/source-binding gaps:** phase 3 checks the completed Python/source
  bridge below; final Lean and generated-instance inspection/replay remain pending.
- **Uncovered claims:** frame/profile correctness, backward inversion without
  invertibility hypotheses, whole-call hosting, common-label realization,
  all-size compilation, precision/tape recovery, and analytic transfer.

Existing independent arbitrary-column restoration and frame checks live in
`research/complex-k492-owner-repair/code/hpe_audit_local.py` and
`hpe_audit_and_transport.py`. The contribution's proposed novelty is the
kernel-checked universal cleanup rewrite, not replacement of those replays.

Attribution: the reviewed constructor is retained from Jeremy Kothe's K492
supplier lineage and carries its original Claude Code assistance notice.
This independent phase-1 review and oracle were prepared with substantial
OpenAI Codex assistance under assignment seed 76, Apache-2.0.

## Phase 3: completed source-binding review

Reviewed only `check_source.py`, `CK-FIXTURE.json`, `CK-PRE-HPE.json.gz`,
`SOURCES.json`, `SOURCE-RESULT.json`, `SOURCE-VALIDATION.json`, `README.md`, the
phase-1 files, and pinned supplier inputs. Lean, generated Lean, generator,
runner, and configuration files were intentionally not read. The requested
literal `NOTICE` path was absent; no assertion about another notice filename
is made here.

Reviewed `check_source.py` SHA-256:
`4f21b111c938b0b5ca68c09a3acfb1725554b544d43feb14d7af37e95643315d`.
Reviewed `CK-FIXTURE.json` SHA-256:
`d5499623f1d9738b65dd3ef009a57037dcb1a724c87c95aa0a704c43c5b5543c`.
These identify the completed versions reviewed, not regenerated gzip containers.

All seven `files_sha256` entries were independently checked against `git show
66849e1475c930fd7732b1a0067ffee7e1e95f60:<path>`; every pin matched. The selected
record leads to the selected #626 inventory, which pins the CK SPEC, constructor,
and recipe. The retained decompressed input matches the SPEC's CK step-5 output
and step-6 HPE input, `b19c9c7cf895e31cd0afd12e5226cd0c917fac387bf7b12533437141790845c8`.
The descriptive `SOURCES.json.ck_chain` also equals the actual SPEC CK chain.
The checker verifies adjacency through the later cold-end output; it does not
mistake that final cleanup word for the earlier HPE input.

Independent projection confirmed **all 2,869 cleanup gates**: 2,659 adds and
210 scales. Every target/source and exact rational coefficient agrees with
the fixture; there are 196 negative raw denominators, normalized correctly.
The actual 34 original recipe indices are strictly descending, not silently
sorted. Independent counting gives 19,084 full original-prefix pairs, exactly
the eight shared-register pairs recorded in the receipt, and 68 selected
registers. The original pinned `commute` predicate accepts the scalar guards.

Two additional checks go beyond comparing the source checker's receipt:

1. Executing the original pinned `build_hpe.apply` on the retained full word and
   actual recipe passes its helper, incidence, frame, and profile guards and
   reproduces the SPEC/recipe HPE output hash exactly:
   `93228917343883327493cf8e8af68be06251be4db719039ae3ca8d54595f2be6`.
   This is a finite source replay, not a universal proof of those extra guards.
2. A separate exact sparse-row oracle propagates the entire cleanup's linear
   map and compares it with the extracted map on **all 716 input columns**.
   It reads the raw word, uses the actual recipe order and untouched subsequence,
   and calls none of the source checker's arithmetic or pair oracle. Maps agree.

Reproduction, from the repository root:

```sh
python -I -O -B research/cleanup-prefix-lean/review.py --source-binding
```

Expected nested status: `source_binding.status` is
`PASS_INDEPENDENT_CK_SOURCE_BINDING_REVIEW`. This additionally runs the phase-1
checks. The first optimized run completed in 20.67 seconds. The source binding
checks are explicit exceptions; the original source `apply` is compiled with
assertions enabled. Corruptions use in-memory intercepted reads and never alter
the checked files or supplier tree.

| Adversarial check | Observed result |
| --- | --- |
| Change the last unselected gate's coefficient in the fixture | `fixture mismatch` |
| Replace selection with an empty list | `fixture mismatch`; no vacuous fixture accepted |
| Sort the actual descending indices in the fixture | `fixture mismatch` |
| Add an unexpected gate field | `fixture mismatch` |
| Replace a normalized rational by an equivalent doubled numerator/denominator | `fixture mismatch`; canonical fixture schema retained |
| Alter a non-cleanup input field (`ports[0]`) in a valid gzip payload | `pre-HPE payload hash`; the full input is bound |
| Alter recipe bytes or producer source bytes | corresponding `source hash` failure |
| Recompress identical decompressed input with a different gzip timestamp | accepted, identical fixture |
| Boolean denominator/register, float coefficient, out-of-range source | rejected at the appropriate schema guard |
| Zero scale in the fixture parser | rejected as `zero scale` |
| Negative denominator (`2/-4`) | accepted and normalized to `-1/2` |

No source-binding logical defect was established. The checker is nonvacuous on
the actual pinned instance, preserves complete cleanup data and recipe order,
and rejects tested corruptions beyond the selected prefix. It deliberately
uses stronger concrete conditions (selected gates are additions targeting the
listed entering helpers) than the generic source predicate. That is valid for
this CK binding, not a claim that these are the only scalar gates the source
can rewrite. Descriptive provenance text is not itself formal evidence; the
existing pinned input and output hashes provide the concrete linkage.

**Actionable documentation clarification:** `README.md` currently lists zero
scales among rejected inputs but does not explicitly separate the concrete
fixture's nonzero-scale restriction from the generic scalar rewrite domain.
Zero scale is mathematically valid for the forward scalar commutation theorem
and remains covered by the phase-1 oracle. The fixture parser's stronger
restriction is appropriate for this retained invertible cleanup; it is not a
counterexample, an unsound acceptance, or a theorem limitation. Add that
distinction explicitly in the source-checking/trust-boundary section. The
reviewer did not edit the README.

Final Lean/kernel review remains open. None of the README's proof, generated
instance, coefficient-parametric, or runner claims were independently verified
in this phase; their files were outside this phase's authorized read scope.

## Final proof and runner audit

**Disposition: clean proof accepted; one runner fix required before package
acceptance.** The phase-3 zero-scale documentation clarification has been added
to the README. The actual notice is `NOTICE.md`, inspected in this final phase.
The earlier statements about unread proof artifacts describe the historical
phase-3 boundary and are superseded by this final audit.

The immutable reviewed file hashes, complete commands, toolchain identity,
20 theorem axiom reports, generator controls, and runner controls are recorded
in `FINAL-REVIEW.json`. None of the implementation files were edited by the
reviewer. The reviewed runner SHA-256 is
`ab7fdf220ec490433a15b63e435bb335387abc47170975643eaa8e8a0d60bc3f`.

### Semantics and nonvacuity

`Scalar` supplies associative and commutative addition, with no multiplication
laws. This suffices: disjoint gates preserve each other's operands, and the
same-target add case needs only reordering of the two unchanged addends.
`eval` reads the old state before updating the target, so disjoint self-adds
have the correct meaning. `State α = Nat → α` quantifies arbitrary initial
register values, including every helper's initial dirt and unused registers.
The explicit `Int` instance and counterexamples establish a concrete model.
No formal rational/complex instance or rational embedding is supplied, as the
README now explicitly states; neither is silently inferred by this review.

`run` retains coefficients by the original instruction's `index`.
`pull_sound` proves a real scalar program equality by induction, using the
proved `commute_sound`, rather than assuming the desired semantic identity.
`pull_split` describes the actual removed instruction and stable remainder.
`extract` prepends pulled gates in recipe order and checks selected-register
disjointness. `sourceExtract` additionally checks every selected original prefix
before any deletion. For the actual distinct sequential source indices, those
are exactly the intended original positions. The checked CK premise discharges
the extraction hypothesis; the final equality has no unevaluated commutation
assumption and is universal in all coefficients and initial states.

The prefix optimization is sound and does not omit later instructions:

- Independent parsing of generated Lean literals recovered exactly the 665
  initial and 2,204 suffix instructions, together equal to all 2,869 fixture gates
  with unchanged kinds, registers, and sequential unique original indices.
- The 34 selected instructions appear in the original descending recipe order.
  `prefixTail ++ suffix` is exactly the other 2,835 instructions in original
  order. `stable_remainder` is kernel-checked as the full cleanup's filter.
- `scalar_rewrite` applies the contextual theorem with the entire suffix as
  part of the unchanged following program. Equality of the prefix states is
  therefore propagated through every suffix instruction; it is not a claim
  that the suffix is semantically trivial.
- Independently decoded `rationalPalette` and `coefficientCodes` contain nine
  distinct rational pairs and exactly 2,869 in-range codes. Every indexed pair
  equals the corresponding normalized source coefficient. Neither `getD`
  fallback is used by any actual cleanup instruction.
- `source_coefficient_rewrite` specializes the universal coefficient function
  to an arbitrary interpretation of those pairs. This is honest but does not
  itself prove that an external interpretation is the usual rational embedding.

The trusted Python generator/source bridge remains explicit; these are Lean
proofs about the validated generated literals, not a formalization of Python
or JSON parsing. There is no `sorry`, `admit`, user axiom, `native_decide`,
`unsafe`, or `implemented_by` in the actual two reviewed Lean sources.

### One clean proof replay

An isolated root was populated with only the package's top-level files and the
seven pinned source inputs. No `.lake`, `.olean`, `.ilean`, or Python cache was
copied. `LEAN_PATH` and `LEAN_SRC_PATH` were removed from the replay environment.
The existing release toolchain and its standard library were used; no global
toolchain setting was changed and no dependencies were downloaded.

```sh
python -B /kmh-nfs-ssd-us-mount/code/siri/tmp/cleanup-prefix-final-review-d4dbrfhe/research/cleanup-prefix-lean/run.py \
  --lean-bin /tmp/swarm-research-lean-tools/lean-4.27.0-linux/bin
```

Working directory was the isolated root. Result: exit 0,
`PASS_CLEANUP_PREFIX_LEAN`, **43.725 seconds** total. Lake reported 4.5 seconds
for `CleanupPrefix` and 31 seconds for `CKFixture`. Toolchain:

```
Lean (version 4.27.0, x86_64-unknown-linux-gnu,
commit db93fe1608548721853390a10cd40580fe7d22ae, Release)
```

Lean executable SHA-256:
`8fadc3ed92cc9decb94c96ee9c0876e91e03a3a5e69138f32114f02789e2766c`.
Clean build log SHA-256:
`5277a95f6d58643c9617175580a764ce7fb27cdaa7356461078e58de991b8a5e`.
The full log is retained in the isolated root as `clean-proof.log`.

The clean run reported `propext, Quot.sound` for all printed universal/context
theorems, `CK.scalar_rewrite`, and `CK.source_coefficient_rewrite`.
`CK.checked` uses only `propext`. A small supplementary import using these
freshly built artifacts printed the remaining structural theorem axioms:
`selected_order`, `prefix_filter`, `recipe_below_cut`, and `suffix_above_cut`
use none; `suffix_unselected` and `stable_remainder` use `propext, Quot.sound`.
This supplementary axiom query was not another full build. All 20 exact
name-to-axiom mappings are in `FINAL-REVIEW.json`.

### Generator and runner controls

In a separate isolated copy, the real generator rejected each of:
deleting the final suffix gate, changing an original instruction index, changing
a coefficient code, and sorting the recipe. Each exited 1 with
`CKFixture.lean differs from validated source`. A malformed zero-denominator
fixture failed at `fixture mismatch` before generation. Explicit `--write`
regeneration of restored valid inputs reproduced the committed generated Lean
byte-for-byte (`8647f6731d9ed2c8a6099931471ba405924f9080c2fc335a9a863ae398cd1d6b`).
These controls exercise real source validation and generation; no proof build
was repeated for a mutation that the bridge already rejected.

Focused runner validation controls used **mocked subprocess results**, clearly
separate from the real clean build above. They confirmed rejection of reported
`sorryAx`, `Lean.ofReduceBool`, and a custom axiom, as well as missing
`CK.checked` axiom output. Thus the audited theorem dependency paths fail closed
for those forbidden dependencies. The runner audits printed dependencies;
it is not a blanket scanner for unused declarations or arbitrary source text.

**R1 — exact-version check is too permissive (`run.py:31`).**
The current regex `\bversion 4\.27\.0\b` accepts
`Lean (version 4.27.0-rc1, ...)`, because the hyphen is a word boundary. The
focused control reproduced acceptance by the runner's actual validation branch.
Versions `4.26.0` and `4.27.1` were correctly rejected. This is a concrete runner
validation defect, not a flaw in the scalar theorem or the completed clean replay,
which used the actual 4.27.0 release. Parse the complete reported version token
and compare exactly to `4.27.0`, and add a prerelease rejection control before
declaring package acceptance. A narrow validation-only fix does not require
rebuilding the unchanged Lean proofs.

The phase-3 source checker and fixture hashes are unchanged, so the unchanged
independent full-map/corruption suite was not repeated. The clean proof runner
did re-execute source validation and regenerated-text comparison as required.

## Narrow publication audit: ACCEPT

`PUBLICATION-REVIEW.json` is the latest independent acceptance receipt. It
records exact SHA-256 hashes for every reviewed publication artifact, retained
proof/fixture/generator hashes, commands, timings, and expected failure output.
It supersedes the earlier runner-fix-required disposition in the historical
`FINAL-REVIEW.json`; it does not rewrite that earlier evidence.

The new `BASE-SELECTED-RESULT.json` is byte-for-byte equal to
`git show 66849e1475c930fd7732b1a0067ffee7e1e95f60:certificates/selected-result.json`:
SHA-256 `b3bf402f31a69bde0629936a9b569bed48281568d7b16d5fba120b5311ea1f53`.
The other six original input pins are retained unchanged, match the base
commit, and also match their paths at origin/main
`abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`. That main revision selects #942;
this contribution correctly remains a historical baseline #626 audit.

Inspection of the checker delta confirms that the sole production selection
change is reading the pinned package snapshot instead of the floating
`certificates/selected-result.json`. Additional code implements optional
portability controls; it does not weaken the original source/inventory/recipe
or full-prefix checks. Both Lean source files, generated fixture, pre-HPE input,
generator, result receipt, Lake configuration, and toolchain pin match the
previously reviewed clean-build hashes. No Lean build was rerun.

Independent on-disk controls in a fresh isolated copy passed:

| Check | Result |
| --- | --- |
| Real selected-result bytes from origin/main #942 as the live certificate | Optimized source checker passes, 5.214 s |
| Remove the live certificate entirely; run `check_source.py --portability-controls` | Source and built-in controls pass, 13.022 s |
| Run the real generator with the live certificate absent | Validated generated text unchanged, 2.645 s |
| Append one space to the frozen snapshot | Exit 1, exact frozen-snapshot `source hash` rejection, 0.211 s |

These controls changed only the isolated test root, not repository inputs.
The reviewer initially supplied `python -I` to the generator, which intentionally
uses a sibling `check_source` import; the harness was corrected to the normal
script import behavior used by `run.py`. This setup incident is recorded in the
receipt and is not an implementation failure. Source-checker runs retained
`-I -O -B`; the generator ran with `-O -B`.

R1 is resolved: `reported_lean_version` preserves the complete version token,
and the runner compares it exactly with `4.27.0`. Focused independent checks
accept `4.27.0` and reject `4.27.0-rc1`, `4.27.0+build`, `4.27.1`, and `4.26.0`.
This narrow runner correction does not affect the prior clean proof evidence.

README and HANDOFF explicitly identify the frozen certificate's base origin,
the historical #626 scope, and the independence from the current selected
frontier. No actionable findings remain in this narrow publication audit.
Patch application, commits, credentials, and external publication were not
performed by the reviewer and remain outside this acceptance receipt.
