# Eighteen-PR circuit, precision and verification batch

The selected conditional saving remains **κ = 0.001661957774647029**, from
#890 / #869 / #870 with #589 on #555. This batch retains finite constructions,
scoped optimality proofs, independent checks and tooling. It does not select a
new multiplication witness or combine the submitted savings numerically.

The frozen inventory contains exactly 18 PRs. Every changed path has a recorded
source hash and retained/adapted disposition in
[CONTENT-COVERAGE.json](../../research/community-batch932-audit/CONTENT-COVERAGE.json).
[Publication and execution receipt](community-batch932-integration.json) and
[per-PR decisions](../../research/community-batch932-audit/DISPOSITIONS.json)
distinguish local verification, publication and GitHub state.

## Individual contributions

| PR | Contributor | Accepted scope and limitations |
|---|---|---|
| [#921](https://github.com/CrocSwap/integer-mult-bounds/pull/921) | [Aaron Wang](https://github.com/navinor) | Concurrent isolated test modules with ordered output; benchmark acceptance hardened against nondeterministic mismatches. All 94 modules pass in both schedules. |
| [#903](https://github.com/CrocSwap/integer-mult-bounds/pull/903) | [just-mn](https://github.com/just-mn) | Source-pinned pivot-column caching for the historical data-corner checker; all 4,073,300 cases and full receipts reproduced. |
| [#849](https://github.com/CrocSwap/integer-mult-bounds/pull/849) | [Gareth Davidson](https://github.com/bitplane) | Opt-in exact dyadic multiply-add kernel; all 70,765 native updates and 15 changed-word controls checked. Default mathematical sources unchanged. |
| [#883](https://github.com/CrocSwap/integer-mult-bounds/pull/883) | [mightyOil](https://github.com/mightyOil) | Four-operation X4 precondition pairs, exact scoped two-register minimum and 784 real primitives saved per orientation; bound to immutable #799 checkpoint. |
| [#916](https://github.com/CrocSwap/integer-mult-bounds/pull/916) | [Stephen Shore](https://github.com/nightangelflowerwin-ops) | Source-bound #883 compiler refinement admitted through the complete #799 invoice and assembly with verified reused #741 ancestry; 56,448 fewer primitives, historical kappa unchanged. No U8/T21 transport claimed. |
| [#816](https://github.com/CrocSwap/integer-mult-bounds/pull/816) | [dd-hemant](https://github.com/dd-hemant) | Historical CK signed target forest, 66,520 primitives saved per orientation; exact minimum only in signed-unit single-parent forest class. |
| [#901](https://github.com/CrocSwap/integer-mult-bounds/pull/901) | [ToikY](https://github.com/ToikY) | X4 disjoint target pairs, 33,800 primitives saved per orientation; arbitrary-input restoration and complete scalar replay. Production integration remains open. |
| [#932](https://github.com/CrocSwap/integer-mult-bounds/pull/932) | [Ross Richardson](https://github.com/RossRichardson) | X4 signed target forest, 47,690 primitives saved per orientation, 10,883 per-component compensation floor in stated class; reverse envelope rises to 74 bits. Production integration remains open. |
| [#837](https://github.com/CrocSwap/integer-mult-bounds/pull/837) | [Gareth Davidson](https://github.com/bitplane) | Bidirectional binary/NAF Horner lowering with finite scalar savings; considered together with #866 fractional-grid correction, not an unchanged full precision theorem. |
| [#866](https://github.com/CrocSwap/integer-mult-bounds/pull/866) | [Gareth Davidson](https://github.com/bitplane) | Exact scalar-prefix dyadic denominator criterion, complete CK/JP8/SW4 replays and rounding counterexample; CK forward guard rises from 3 to 5 bits, joint guard unchanged. Physical precision not certified. |
| [#882](https://github.com/CrocSwap/integer-mult-bounds/pull/882) | [mightyOil](https://github.com/mightyOil) | Seven grid-bounded JP8 coefficient circuits; 104 primitives saved per orientation and independently checked bounded single-scratch class minima. |
| [#915](https://github.com/CrocSwap/integer-mult-bounds/pull/915) | [Gareth Davidson](https://github.com/bitplane) | R439 restored target-basis D prefix: 24,305 to 13,208 ADDs; native 5/9/11-stage replay. Semantic D boundary accepted as a finite substitution; original H2/extractor remain false. Full hosted adoption open. |
| [#926](https://github.com/CrocSwap/integer-mult-bounds/pull/926) | [Gareth Davidson](https://github.com/bitplane) | R439 two-sided compensation: 11,980 ADDs; full mixed term and native 5/9/11-stage checks. Nine-stage bound uses about 99.925% of allowance. No composition with other candidate savings or full hosted adoption claimed. |
| [#891](https://github.com/CrocSwap/integer-mult-bounds/pull/891) | [Aaron Wang](https://github.com/navinor) | R439 phase-B frames 506/523 shortenings with exact single-write class census, independent Bellman verification and all-column endpoint; 16 complete ADDs saved, reverse bound improves. |
| [#884](https://github.com/CrocSwap/integer-mult-bounds/pull/884) | [martinxxx9](https://github.com/martinxxx9) | R439 frame521 47-to-31 ADD replacement and literal cleanup, 32 complete ADDs saved; 12,000-trial search reproduced, no global optimum claimed. Historical checkpoint pin preserved. |
| [#867](https://github.com/CrocSwap/integer-mult-bounds/pull/867) | [Aaron Wang](https://github.com/navinor) | Historical #799 provenance map and 298 vendored-source checks reproduced with PowerShell on original-base inputs. Matching bytes and citations do not approve whole predecessor PRs. |
| [#879](https://github.com/CrocSwap/integer-mult-bounds/pull/879) | [mightyOil](https://github.com/mightyOil) | Independent literal physical-layout and direct tensor-character checks: 9,486 layouts, 200,434 complete addresses, 4,340 ring columns and 11 controls. Bounded finite evidence, not all-size proof. |
| [#813](https://github.com/CrocSwap/integer-mult-bounds/pull/813) | [Gareth Davidson](https://github.com/bitplane) | Exact Bernstein certificates for 47 retained outer inequalities, 57 polynomial rows and 2,586 weights; independent SymPy crosscheck. Historical #626 witness/domain only, supplier and bridge hypotheses inherited. |

## Review findings and adaptations

**Test scheduling (#921).** All 94 discovered modules passed sequentially and
with four workers, with identical stdout, exit codes and timing-normalized
stderr. This local comparison took 282.06 versus 83.39 seconds (3.38×), while
other research replays shared the machine; it is not a controlled portable
performance guarantee. The submitted Windows measurements are retained separately.
The original benchmark's same-mode comparison included raw timing hashes and
could excuse a substantive mismatch as nondeterminism. The integrated version
rejects every remaining mismatch, treats same-mode variation as diagnostic only,
and requires a fresh output path. Two regression controls check the distinction.
The runner buffers results before ordered output; its commands and test coverage
are unchanged. The user's original research checkout was not modified.

**Checkpoint drift (#883/#884/#813).** Initial #883 and #884 commands correctly
rejected the moving selected-result pointer after the previous frontier update.
The same issue was identified and fixed for #813. Each now reads its immutable
#799 or #626 checkpoint with the original digest. No witness or expected source
hash was weakened. Adapted commands and controls pass. #903's tests use their
documented ordinary Python command; isolated `-I` removes their local import
path and is not a supported invocation. That failed extra invocation is retained.

**X4 admission (#916).** Fresh primitive lowering, both full scalar projections,
complete invoice and outer assembly were rebuilt using the previously verified
complete #799 replay at `/tmp/frontier799-integrated` and #741 ancestry at
`/tmp/frontier741-composed-fresh`. Coverage admission was rerun first. No new
cold ancestry reconstruction is claimed. The two-row primitive proof, 672
predecessor mutations and 16 admission controls pass. The historical #799 κ
is unchanged. Applying the change to the newer U8/T21 supplier is separate work.

**Forest and pair constructions (#816/#901/#932).** Reviewed the arbitrary-dirt
identity T⁻¹(Ty+TCh)=y+Ch, leaf-before-parent preparation and reverse restoration,
chronological inverse-transpose convention, and the fully charged coefficient
lowering. The signed-forest reduction is to an exact superroot spanning tree;
independent Prim/cycle checks certify only the declared single-parent class.
Complete scalar replay includes private dirty inputs and both orientations.
#932 follows #816's mechanism and extends #901's same-panel result; both retain
credit. #932's reverse positive envelope increases from 72 to 74 bits. Counts
are not automatically additive with #883, #837 or other lowerings.

**Bit prefix substitution (#915/#926).** Reviewed E⁻¹(Ey+EKs)=y+Ks and the two-sided
E K H⁻¹ identity, including the mixed term. The semantic frame-zero D boundary
is a valid finite substitution under inherited realization assumptions. This
does not make the predecessor's gate-local H2 or literal K extractor true;
the unchanged predicates explicitly reject the new shapes. All arbitrary input
columns, literal bounds, unchanged MOVE/COPY/ERASE obligations, and native
5/9/11-stage tests pass. #926 uses about 99.925% of the nine-stage numerical
allowance. Full hosted emission, precision invoices, source bindings and assembly
must be rebuilt before replacing the selected bit supplier. #891 and #884 are
separate candidates, not silently combined with this tight budget.

**Precision and exact checks (#837/#866/#882/#879/#813).** Endpoint identities
alone do not certify intermediate numerical behavior. #866 proves the scalar
grid criterion through the largest reduced dyadic denominator of every prefix,
including a concrete failed three-bit CK run. #882 checks finite coefficient
graph distances and an independent integer replay. #879 compares explicit moves,
rounds and twists with a separate character oracle, including order-three layouts
and missing-step controls. #813 reconstructs every polynomial from positive
Bernstein/monomial coefficients and crosschecks all 57 rows with SymPy. Its
positive bridge gaps remain assumptions. None is a complete all-size physical
precision proof or full Lean multiplication theorem.

**Provenance (#867).** Both original PowerShell scripts were replayed under
PowerShell 7.6.6 on an isolated original-base input tree. The JSON output matches
the submitted historical report exactly: 76 source PRs, 13 without a record,
26 without an incorporated-strength record; 298/298 vendored rows match both
SHA-256 and their named Git blob. These are #799-era counts, not the live queue.
No predecessor is promoted to whole-PR approval by this check.

## Reproduction and credit

The package entrypoints and commands remain in each contributor's README.
Maintainer logs, native replay archives, exact heads, source comparisons and
benchmark evidence are under `research/community-batch932-audit/`. Normal verifier
runs compare complete expected receipts and candidate-specific mutation controls;
regeneration is distinct. #884's complete 12,000-trial search was also reproduced.
#891's exact class census is independently certified by its backward verifier;
this review does not claim rerunning its forward discovery program.

Credit includes Aaron Wang / navinor, just-mn, Gareth Davidson / bitplane,
Philipp / mightyOil, Stephen Shore / nightangelflowerwin-ops, dd-hemant,
ToikY, Ross Richardson and martinxxx9. Mechanism lineage remains with Oscar
Fennell (#759), Sricharan Vagvala (#749), Scott Woolsey Biggart (#713/#733),
Sagar Thakrar's lowering and sharing, Romain Hedouin's #183 outer analysis,
and the icekylinx / Jeremy Kothe / Chafik Boukhalfa / DreamingOfClouds / eumemic /
Rohan Arun construction and verification lineage. Original notices and AI
assistance disclosures remain. Parallel and historical contributions receive
credit independently of whether their candidate is selected.

All-size compilation, common-label/mutable-source realization, whole-call hosting,
precision/tape and analytic assumptions remain inherited. Local execution is
separate from subsequent Linux CI; see the integration receipt for current status.
