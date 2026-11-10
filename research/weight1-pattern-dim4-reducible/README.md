# Weight-one covectors cap a pattern-dimension-4 no-edge image at 6

**Proof, plus one finite witness. No new κ.** The selected conditional
value stays `781451/250000000`.

## Result

Over `F2`, let `P` be a linear space of zero-diagonal matrices with
`dim P ≤ 4` and with no matrix unit. Suppose every rank-one idempotent in
the complete off-diagonal pool has covector weight 1. Then the joint image
`V` has dimension at most 6. If the pool is nonempty and
`dim V ≥ dim P + 1`, the action on `V` is reducible. In particular every
such pool with pattern dimension 4 and joint-image dimension at least 5 is
reducible.

Dimension 6 is attained. On eight coordinates the two column spaces

```text
span{e1+e2, e1+e3}    and    span{e5+e6, e5+e7}
```

give a complete pool of six projectors, pattern dimension 4, no matrix
unit, image dimension 6, and an invariant kernel of dimension 4. The
argument is in [PROOF.md](PROOF.md).

This is a proof under the weight-1 hypothesis. The width-8 pool equality
is an exhaustive census of the finitely many rank-one idempotents on those
eight coordinates. Neither statement is a census of all pattern spaces, and
neither bounds a pool that uses a covector of weight 2 or more.

## Scope and evidence

Catalogue card: `bit-new-register-model`, priority revision 8, base commit
`f16923d466a6aba912299882e0545564d2ba7bb2`. The session opened on
`17469fff78c22941280f04d39dc5a1faee09c840`; upstream main then advanced by
the PR #7000 admission commit, which does not touch this proof. Scope
status is **changed**.
The card asks for a larger or nonabelian register alphabet. This package
answers the weight-1 case of the pattern-dimension-4 image question left
by #6962 and narrowed by open #7094. The original card is copied verbatim
in [TASK.json](TASK.json). Pins are in [SOURCES.json](SOURCES.json).

Ordered eligible list for session r230. Dropped first: every unpaidmoon
pull request and fork `cursor/*` branch named in the session brief,
including the newer fork tips `cursor/frame506-carry-ledger-30b5`,
`cursor/two-gap-constant-insertion-1bb5`,
`cursor/y-exit-partial-round-trip-70ac`, and
`cursor/y-exit-rank-lift-obstruction-b140`. The 19 October handoffs are
already delivered. The revision-8 next-decision table comes next, then
catalogue cards that table does not name, in catalogue order.

1. Complex helpers (`p104-side-correction`, `coverage-law-change`).
2. BIT helper contract (`bit-helper-contract`).
3. New decoders and interfaces.
4. Supplier audit.
5. All-size audit and formalization.
6. Verification tooling.
7. `bit-new-register-model`.
8. `r437-carrier-integration`.
9. `complex-rank-shape-decoder`.
10. `complex-new-helper-inventory`.

Item 3 of that list is a changed producer/consumer contract. This package
is item 7. It is the distinct remaining piece of that card after #6921,
#6962, and open #7094: those results use covectors of weight greater than
1, or stop at pattern dimension 3. The weight-1 hypothesis is not the
hypothesis of #7094, whose irreducible dimension-5 pool has covector weight
at least 2. The 112-owner linear relation left by open #7056 was not
taken.

#7094 is not on this main. Its factors were read from the pull-request
head and are not replayed here. The four-cycle of #6962 is used only as a
negative control: its covector weight is 3, so the theorem does not apply
to it.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/weight1-pattern-dim4-reducible --check-only
python3 -B scripts/research_package.py --package research/weight1-pattern-dim4-reducible
```

`verify.py` prints `PASS_WEIGHT1_PATTERN_DIM4_REDUCIBLE` with
`pool=6`, `image_dim=6`, `kernel_dim=4`, `partition_max=6`, and
`new_kappa=null`.

Not run: Lean, Docker, the selected cold replay, and any search over
heavy covectors. An incomplete search is not evidence in this package.

## Open next questions

Can a complete no-edge pool of pattern dimension 4 that uses at least one
covector of weight 2 or more act irreducibly on a joint image of dimension
6 or more? Open #7094 already gives irreducible dimension 5 in that heavier
class, so the weight-1 cap does not bound it. The smallest next step is one
explicit heavy-covector pool with a written invariant-subspace check, or a
proof that every such pool has image dimension at most 5 or is reducible.
No column decomposition in this note makes that domain finite, so a search
that finds nothing would not be a proof.

A second boundary is left open on purpose. The kernel test needs
`dim V ≥ dim P + 1`. The four disjoint weight-1 lines have pattern
dimension 4, image dimension 4, and trivial common kernel, while each line
is invariant. That example does not decide whether every weight-1 pool with
`dim V = 4` is reducible.

## Credit

The fiber lemma is Nick Petalas, #5921,
`research/pattern-pool-cardinality`. CubeJerry, #6838, proved the
pattern-dimension-at-most-3 total-image bound and gave the reducible parity
pool of image dimension 5; this note does not reprove that theorem. #6921
proved the irreducible bound 3 for pattern dimension at most 3. #6962 showed
that bound fails in pattern dimension 4, by the four-cycle. Open #7094
shows irreducible image dimension 5 with heavier covectors. This package
does not replace those arguments.

Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0. No independent human or formal-kernel review is claimed.
