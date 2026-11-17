# Five A2 longest-element targets need five rank-three calls

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped written proof with exact finite corroboration. Five identical
longest-element targets w0=sts=tst in S3 have exact formal tariff **5 f(3)**
when paid scalar rank is capped at three and the common rank price f is
nonnegative, nondecreasing and discretely concave, with f(0)=0. The result
holds over every field, with free scalar GL mixing and any finite number
of restored dirty spectators. In particular, five unit-priced invocations
are necessary and sufficient.

The new diagonal support schedule has five rank-three calls, compared with
six calls of ranks (3,3,3,2,2,2) from fixed disjoint batching. It costs
5 f(3) instead of 3 f(3)+3 f(2), saving 3 f(2)-2 f(3). At f(k)=k/(k+1),
the exact bill is 15/4 instead of 17/4. The matching 15-unit rank lower
bound is a cited predecessor theorem, not a new result here.

[PROOF.md](PROOF.md) gives the complete endpoint, five support sets and
all-field argument. This answers one nondivisible-target instance explicitly
left open by zhaobenny's [PR6817](https://github.com/CrocSwap/integer-mult-bounds/pull/6817).
Its divisible theorem does not cover five targets at cap three. Nick Petalas's
[PR5083](https://github.com/CrocSwap/integer-mult-bounds/pull/5083) already
supplies the changing-support idea and the distinct three-target/cap-two
word; those are credited. ToikY's
[PR6821](https://github.com/CrocSwap/integer-mult-bounds/pull/6821) treats
repeated st, a different endpoint. The new contribution is this five-target
support schedule and its sharp cap-three tariff, not a new root-cut or
concavity principle.

## Evidence and reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/a2-five-target-cap-three/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/a2-five-target-cap-three/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/a2-five-target-cap-three
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/a2-five-target-cap-three --check-source-history --check-modes
```

Other installations can substitute their CPython 3.12 path. The direct
commands print `PASS_A2_FIVE_TARGET_CAP_THREE` in a newly computed JSON
receipt bound to the SHA256 of all six package files. They write no files,
import no predecessor program and require no Git, network or external input.
`SOURCES.json` pins cited prose and the historical task context as provenance;
the package validator authenticates those Git pins separately.

The finite checks cover exactly:

- 24 complete signed group-algebra endpoints over Q, F2, F3 and F5, using
  five, six and eight roles and two scalar gauges. All 120 paid couplings
  have rank three and are idempotent; 78 genuinely couple productive and
  dirty roles. Entrance and exit scalar maps restore the target endpoint.
- 912 basis columns of the complete left regular action, using a separate
  GL2(F2) address representation rather than the S3 permutation product.
- 120 omitted-call and 120 label-flip mutants, each rejected by its complete
  formal endpoint. These controls concern the new word only.
- 36 exact rational price schedules, including all 35 nonincreasing
  nonnegative integer slope triples with slopes at most four, plus
  f(k)=k/(k+1). Each is compared against all 90 nonnegative rank-count
  profiles with total rank 15 through 17, for 3,240 comparisons.
  Exactly 31 of the 36 schedules give strict savings over fixed batching.

The price-profile enumeration suffices for this finite relaxation: from
any list of ranks 1..3 with total at least 15, retain a prefix through its
first crossing of 15. Its total lies in 15..17 and its cost cannot increase.
The universal circuit lower bound is the written cited theorem, not an
extrapolation from this finite price test or from the tested fields.

Local validation uses CPython 3.12.15 on macOS arm64. Normal, optimized
and registered replay are the required checks; exact timings and the
publication commit are recorded in the PR body. Hosted CI status is separate.
No local mathematical check is deferred solely to CI. Independent human
and formal proof-kernel review are unclaimed.

## Scope and overlap

The formal paid operation is I+([u]-[e])A, u in {s,t}, with arbitrary
scalar A of positive rank at most three. The endpoint is diagonal with
five [w0] entries and identity on every other role. Arbitrary couplings,
free scalar maps and restored dirty spectators are allowed for the lower
bound. The attaining schedule needs only coordinate projectors and no
spectators. It does not classify other target counts, caps or prices.

This is a changed-scope side result for `bit-new-register-model`. It does
not fulfill that card's native-conversion or complete-supplier gate.
Scalar coupling rank is not recursive child rank. The actual physical
price, ownership, routing, storage, precision, stock, compilation, hosting
and complete supplier invoice remain unknown. No new kappa, supplier
admission or selected-frontier change is claimed; all five selected
framework assumptions remain. Lean, Docker, the selected cold replay
and predecessor scientific suites were not run.

The scientific base is canonical main
`e54523517d0f03e58352e647c403a5af3e525a57`, with the selected #7000 record
and priority revision 8 pinned separately in `SOURCES.json`. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19538441)
states the same five-target/cap-three scope.

Entry overlap included live open PRs, account PR history, recent handoffs,
active discussions, relevant PR bodies, and distinctive whole-main README
searches for the specific and general batching formulas. The cached scan
covered 477 open PRs and 7,121 Discussion records with complete remote
pagination, but only 169 materialized notes against 10,178 HEAD note paths.
Whole-main Git searches supplemented that sparse coverage. A separate
source-reference scan covered 477 open and 6,175 closed PR bodies and found
no account PR created since November 4 citing #6817. These snapshots are
non-atomic; arbitrary diffs, unmaterialized nested code and unpublished
work are outside coverage. A lack of matches is not a novelty certificate.

## Credit

zhaobenny / Benny Zhao's #6817 supplies the all-field rank-cap model,
nondivisible-target question and root-cut/concave-price lower bound.
David Arias's #2738 supplies its Coxeter predecessor. Nick Petalas's
#5083 supplies the older cap-two changing-support construction. ToikY's
#6821 settles the distinct repeated-st question. Credit also Adam Gall,
Ross Richardson, ywz65, eumemic, Ali Romman and Gareth Davidson for the
retained cut and register-model lineage. All predecessor notices remain
unchanged. No literature-priority claim is made for support scheduling,
concavity, matrix rank or regular representations.

## Open next questions

Can a native implementation supply a rank-three call with a complete
subadditive price? First specify the actual data/address layout and
arbitrary-input entry/exit contract, then charge scalar maps, movement,
ownership, precision and restoration. No such physical contract or map
from scalar rank to recursive child rank is supplied here.

Which other nondivisible longest-element batches attain the packed floor?
Start with a support-incidence feasibility problem at one declared target
count and cap. This result gives no general scheduling theorem or chronology
obstruction. No broader construction or follow-on scope is reserved.

## Verifier bounds

The verifier has no recursion, subprocess, solver, external mutable state
or unbounded CLI input. Dimensions are at most eight, each formal matrix
has at most 6*8*8=384 coefficient positions, and words have five calls.
Price loops use 36 schedules and 972 candidate rank-count tuples before
filtering. All functions are shorter than sixty physical lines. Explicit
exceptions preserve invariants under optimized Python.

Python's managed tuples, dictionaries and arbitrary-size integers allocate
during calculation. This is a deviation from fixed allocation, confined to
the bounded finite verifier. Fixed dimensions, domains and support-capacity
checks bound live collections. Warning-strict normal and optimized replay
check the same result. A future larger or native verifier must reassess
allocation rather than inherit a real-time or native-memory guarantee.
