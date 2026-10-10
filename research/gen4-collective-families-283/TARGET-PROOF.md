# Latest PR279: 220 target-prefix squares on the composed word

Pinned upstream: PR279 commit 913ccc48a0bc1173709ea92280b96252256b7754, research/five-stage-gen4-banks/inputs/targets220.json and target_transform.py. These 220 squares are upstream work, not a claimed new invention here. Preserve the upstream Apache-2.0 notices and author/AI disclosures. Our contribution is their concrete recomposition with independently checked sinks, helper kernels, source retiming, and later endpoint transformations.

## Sufficient identity with arbitrary dirty targets

At a common cut, let the four target contents be arbitrary y_t. Suppose throughout a prefix none of these targets is read as a control, and its incoming increments are p_t. If p_a = p_b + p_c + p_d over F2, replace all incoming prefix writes to target a by:

1. at the cut, y_a <- y_a - y_b - y_c - y_d;
2. run the other targets' original increments;
3. at the close, y_a <- y_a + y_b + y_c + y_d.

The final value is exactly original y_a + p_a. The other targets are unchanged. This needs neither clean targets nor independent helper inputs. All initial data variables, including dirty helper and target variables, are included in the finite response check. Initial subtraction and final addition are signed integer instructions; the identity promised here is the F2 payload identity, followed by the project's separately priced odd-payload integer lift.

## Actual boundary and dependency checks

The new upstream cut is 566579 and closes are 570442 through 571858. They precede the first source retiming at original record636200; the original and reconstructed retimed record prefixes are byte-identical there. An earlier trial at the old D0 cut found no useful dependency and is not the claimed candidate.

The native adapter maps the proposed boundaries to unique surviving scalar events on the actual changed word, using the original-to-new helper role map. It then treats those mapped boundaries as candidates and proves the required dependencies again. It does not trust the old record numbers as rewrite offsets. All target intervals are checked for forbidden control use; each response uses the complete actual all-input F2 columns. A minimum-weight independent response set is chosen with a heuristic floating-point ordering, but every chosen linear relation is checked exactly. Only the subsequently regenerated exact histogram and rational outer price certify a saving.

For the 16-sink plus741-kernel plus880-source-retiming checkpoint all220 four-target groups are geometrically compatible and supply220 exact dependent rows. The actual cut is557154. Removing1100 prefix ADDs and inserting1320 setup/restore ADDs changes the paid recursive histogram by {-220 rank1,-220 rank20,+220 rank21}, with rank mass423806 unchanged. Setup/restore tags are34/35, separate from the sink and restoration tags.

Both forward and inverse all19914-column payload replays pass. Deliberately omitting the first setup produces117 wrong output words; omitting a restore produces174. MOVE records are regenerated from actual events and checked with arbitrary-precision basis/annihilator containment, COPY windows and all input/output frames are retained.

## Geometric/prime admission

All220 close frames have rank21 and are already present, with identical bases, in the pinned original frame table. An independent exact rational Gram inversion for G=I-J/9 passes for every frame; the maximum observed numerator and denominator are both60. No positive-definite assumption is made. The original baseline prime audit thus already covers these frames, and the additional Gram receipt independently confirms them. New numerical frame IDs in the transformed file are aliases for these existing bases, not unproved new charts.

## Native CLI and scope

    target279 BASE_EXPORT CURRENT_LEAD inputs/targets220.json OUT ORIGINAL_GEN4_RAW OLD-TO-NEW.json

Outputs use the standard COHORT249 record/frame/initial/selection/replay names. The detailed target receipts retain the historical names TARGET268-RECEIPT.json and TARGET268-GROUPS.json; this is a compatibility filename, not provenance. `TARGET279-GRAM.json` is the separate geometric admission receipt.

This transformation establishes the finite payload/geometry improvement. The complete package must still run its independent full-stage, bank, signed coefficient/finite-invoice, and final strict-constraint checks. Kappa is not obtained by adding the upstream and local reported gains. Later compositions must rerun the response/lifetime checks on their actual current word and endpoints.
## Final composed checkpoint

The final input additionally includes29 transported kernel operations and440 shortened restoration endpoints, with its actual updated final-frame table. The same220 groups pass again at actual cut557038. This time1119 prefix ADDs are deleted and1320 setup/restore ADDs inserted. Rank mass stays422844. Both full19914-column endpoint directions and both omitted-instruction controls pass. The close frames are unchanged existing rank21 bases, and the independent Gram/finite admission is replayed on this exact output. Exact final pricing belongs to the separately regenerated full package receipts.
