# R439: complete later-cut retirement census

**Scoped bit-supplier negative result and precise handoff; no new kappa.**
For PR1128's six width-seven candidates, this package checks every boundary
along the fixed PR589 B word: **713 cuts and 4,278 helper/cut pairs**. It supplies the complete
necessary-condition census for the later-cut first-restoration question left
explicitly open by Ross Richardson's concurrent PR1256.

A cut numbered k is **after exactly the first k B records**. Thus cut 10 is
after zero-based B[9]. The D/A/scatter prefix and B chronology are fixed.

| Helper | Cuts with joint restoration/erasure rank seven | Cuts also passing first-restoration target access |
|---:|---|---|
| 465 | 0–48 | **10–48** (39 cuts) |
| 466 | 0–78 | **none** |
| 468 | 0–88 | **31–88** (58 cuts) |
| 469 | 0–555 | **none** |
| 470 | 0–517 | **0–517** (518 cuts) |
| 476 | 0–284 | **none** |

Every later cut outside the second column has joint rank eight. These are
**necessary-condition windows**, not feasible suffixes or constructions.
No B/C replacement, physical owner allocation or supplier invoice is supplied.

The sharp chronology point is helper466: its blocking target208 is first
read at B[88], but the joint bound has already risen to eight after B[78].
Simply waiting for that target read cannot save it. Helpers465 and468 do
escape their initial target-access obstruction after B[9] and B[30],
respectively, but only until the joint bound rises after B[48] and B[88].
For helpers469 and476, at least one inaccessible required target dependency
remains at every cut with joint rank seven.

## Exact contract and argument

The sole mathematical input is the frozen PR589 tuned word. At each cut,
write the 661-register scalar state as `w=M u` over F2. All source, target
and helper inputs are independent. Each prefix gate is an invertible
transvection, including the already-consumed retained scatter; no new access
to its COPY channels is allowed. Current frames F_r are rational subspaces
of Q^8. Frame changes must be monotone. Scalar operations must use a common
frame, extra dirty workspace must start independently and be restored, and
there is no new COPY, descent, reset or other high-to-low transport.

We test a suffix whose **first restoration block** operates at a single
rational frame J, with no lower-frame preprocessing after the chosen cut,
and restores the designated helper h to its original dirty input s_h.
After that block, arbitrary allowed multi-frame scalar work is permitted.
The ultimate endpoint for h must have dimension at most seven; other source,
target and helper endpoints and scalar values retain their original contract.
This is the first-restoration model of PR1256, not arbitrary suffix synthesis.

Let R_h be the support of `e_h^T M^-1`, and D_h the support of the h-th column
of M. The restoration/erasure argument from PR1128 gives the necessary bound

`U_h = span(F_h, {F_r : r in R_h union D_h}) <= final_frame(h)`.

All these joins have rank seven or eight in the completed census. A rank-eight
join excludes every proper final frame in this interface, even with arbitrary
rational choices, target access and restored dirty scratch. For a rank-seven
join, a first restoration block must use a frame containing

`J_h = span(F_h, {F_r : r in R_h})`.

The required final target value `y_t + x_(t-111)` has the unique boundary row
`b_t = (e_t + e_(t-111))^T M^-1`. If b_t uses a coordinate forced into the
restoration block, but J_h is not contained in t's final frame V_t, no allowed
completion can supply that dependence to t. Every touched register has moved
to J_h or a larger frame; monotonicity prevents any of its information from
reaching V_t. Untouched boundary coordinates and fresh independent dirt cannot
encode the missing independent coordinate. Enlarging the first restoration
frame cannot cure a failed containment.

This is PR1256's information-access implication. We apply it at **every**
later B boundary, where both inverse rows and frames change. The complete
certificate records contiguous runs with identical restoration donors, join
rank, restoration rank and lost-target sets. No cut, rational station or
support-size cutoff is sampled. The proof establishes the stated exclusions;
passing the two tests supplies no sufficiency claim.

For helper466, the target-access witness is target208 at every eligible cut
0–78. At cut79 the joint rank is eight; at cut89, after target208's original
read, it is still eight. The 469/476 lost-target sets are likewise nonempty
through every rank-seven cut. Full sets and every transition are retained in
[LATER-CUTS.json](LATER-CUTS.json).

## Predecessors and evidence-driven scope change

Ali Romman's PR1128 (`df29b159239b79d7e451d6ddda826a73e0e50a67`) establishes the
boundary lemma and the six after-scatter candidates. Ross Richardson's
PR1256 (`d6d5a994fcdcd8d04ec439ff988daa8f37b17ece`) establishes the initial
six-case target-access obstruction and an explicit finite helper470 retirement
using rank two before rank seven. Its construction is predecessor evidence,
not implemented or repriced here. Its native/physical/H4 obligations remain.

This session initially derived the same stationary stars and endpoint-cap
failures independently. The final overlap refresh found PR1256 before any
submission. That initial material is retained in [STATION-NOTE.md](STATION-NOTE.md)
and `CERTIFICATE.json` as corroboration only. It is not the novelty claim.
The one evidence-driven pivot is exactly PR1256's listed later-cut question;
its README says no search there was performed. In particular, our no-window
result for helper466 explains why its proposed target-read follow-up fails
in the fixed chronology, while the two other suggested candidates retain
precise finite windows. Earlier helper470 deletion belongs to Ali Romman's
PR1043; its savings are not combined with anything here.

Fresh OS seed **17** selected the original user's bit-supplier track. The
three initial candidates, first scope, pivot and stopping rule are in
`TASK.json`. There was no pinned sprint issue, so the authorized local-claim
fallback was used. The initial snapshot covered 850 open PR bodies; the final
pre-pivot refresh covered 855 and all 12 returned discussions. PR1253 concerns
common-first-contact kernel entrances and PR1250 source-mask deletion; both
are distinct and neither is a mathematical dependency here.

## Reproduce and negative controls

Python 3.12, standard library only, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/r439-later-retirement-cuts
```

The principal commands also run on Python 3.10+:

```sh
python3 -I -O -B research/r439-later-retirement-cuts/later_cuts.py
python3 -I -O -B research/r439-later-retirement-cuts/check_later_cuts.py
python3 -I -O -B research/r439-later-retirement-cuts/test_later_cuts.py
```

Expected markers include `PASS_LATER_BIT_CUTS pairs=4278` and
`PASS_INDEPENDENT_LATER_CUTS full_inverse_rebuilds=713 helper_cut_pairs=4278`,
followed by passing tests and `PASS_REGISTERED_RESEARCH_PACKAGE`.

The primary engine incrementally updates inverse rows with each B
transvection, using packed binary rows and rational geometry. The separate
checker imports no primary engine, reconstructs the **entire inverse from
scratch at every one of the 713 boundaries**, and uses independently replayed
set-valued scalar states and fraction-free integer geometry. It checks each
restoration identity directly and agrees on every run and boundary, not just
the total counts. Both inherit only the exact raw word; no predecessor
executable code is imported. Separate code paths are not independent human
review.

The test suite rejects wrong boundary indexing, shifted donor support,
missing target obligations, false pass windows, incomplete cut coverage and
changed source bytes. It checks optimized source-only relocation and parsed
certificate regeneration. The retained stationary suite adds all ten legal
witness-gate omissions, three endpoint-cap failures with relaxed positive
controls, six certificate mutations in both engines, a wrong station, damaged
original cleanup and source-corruption tests.

Base `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`; input SHA256
`e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`.
`SOURCES.json` pins base Git blobs, historical context and both predecessor
heads/documents. See `VALIDATION.md` for actual local runs and omitted work.

## Scope, cost and credit

This is an exact finite census plus the cited necessary-condition arguments.
It is not a formal proof-assistant verification of the multiplication theorem.
Even optimistically free suffix work cannot repair a failed information-access
condition within this model. The surviving windows still require full source
access, target effects, restoration, frame transitions, copies, recursive
children, physical hosting, precision/tape and outer/all-size admission before
any new paid profile or exponent can be claimed. The selected complex supplier
remains binding. No native replay, complete cold supplier replay, production
adoption, remote CI or new kappa is claimed. `upstream/`, frozen predecessor
packages and the selected frontier are unchanged.

Credit **Ali Romman** (PR1128 and earlier PR1043), **Ross Richardson**
(PR1256), **Sagar Thakrar** (PR1023 width-seven hosting incentive),
DreamingOfClouds (PR589/545), eumemic (PR555/543), and their retained
compiler/hosting lineage. Prepared for **Philipp (@mightyOil)** with substantial
**OpenAI Codex / GPT-6 Astra** assistance in proof, code, tests and writing.
New material is Apache-2.0.

## Open next questions

Can helper465 at cut10 or helper468 at cut31 be restored through a fully
priced legal suffix? Those are the earliest new necessary-condition windows;
start there and preserve all dirty columns, pending target reads and physical
frame paths. The census supplies no such suffix and does not justify a new
search outside the 39/58 windows without a changed assumption. For helper470,
PR1256 already gives a finite cut-zero continuation; native H4, owner-window
and precision admission are the more useful next checks. Changes to the prefix,
lower-frame preparation, target-read reordering or added transport are outside
this census and require a new explicit contract and complete cost.
