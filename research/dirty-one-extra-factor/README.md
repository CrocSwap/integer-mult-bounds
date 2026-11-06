# Sharp dirty-word intervals at one extra factor

This contribution was produced by Nick Petalas. Apache-2.0.

For every integer h>=0, at exactly n=2^h+1 factors, the unchanged
balanced dirty word has sharp joint interval coefficient envelope

    G(h) = floor(h^2/2) + h + 3.

The claim is a **scoped written proof with exact finite corroboration**.
It covers all ordered pairs of complete ideal-leaf cuts and both word
orientations, with arbitrary shared dirty scratch. It also gives the
sharp joint operator-norm bound for contractive factors, attained by
real scalar factors +1 and -1. No new kappa is claimed.

CubeJerry's [PR #6770](https://github.com/CrocSwap/integer-mult-bounds/pull/6770)
proves the sharp height-uniform envelope and explicitly leaves exact
factor counts open. At n=17, its height-only bound is 19; the new exact
value is 15. The improvement is h when h is even and h+1 when h is odd,
relative to that height-only bound at n=2^h+1. Earlier finite values at
n=3,5,9 were already known. The contribution here is the infinite
fixed-length theorem, not priority for those earlier counts.

[PROOF.md](PROOF.md) keeps the unequal child sizes in every phase pair.
The smaller child has one idle depth register. Counting its
identity row explicitly yields the improved upper bound. Splitting the
last leaf of Arham Tahir's credited power-of-two witness adds one
independent scratch coefficient and attains the bound.

## Evidence and reproduction

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dirty-one-extra-factor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error -X dev research/dirty-one-extra-factor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dirty-one-extra-factor --check-source-history
```

On other machines replace the absolute interpreter path with a Python
3.12 interpreter. The registered manifest runs normal and optimized
execution. Expected marker: `PASS_DIRTY_ONE_EXTRA_FACTOR`.

- The free noncommutative engine enumerates every nonempty chronological
  interval in both orientations at n=17: 92,720 intervals, maximum 15.
  The first maximizing fixture is positive cuts [38,87), target row 1.
  Empty intervals are identity. Complementary cuts of the inverse word
  cover the opposite ordered direction, so both orders are covered.
- A separately implemented scalar prefix engine skips completed subtrees
  using exact integer shears. It checks the explicit attaining row at
  h=1..32, ending at n=4,294,967,297 without expanding that word. Literal
  free-algebra intervals corroborate its first four witnesses.
- The phase-bound arithmetic is checked at h=1..10,000. Six invalid
  contract fixtures reject; understated bounds, changed scalar signs and
  literal inverse-order controls are also checked.
- Default replay compares every mathematical field with the generated
  [RESULT.json](RESULT.json) and prints SHA256 bindings for package files.
  `--write PATH` authors a new result file explicitly. It does not validate
  the existing result. Run outputs belong outside the checkout.

The universal result rests on the written induction, not extrapolation
from the finite checks. Independent human and formal proof-kernel review
are unclaimed. Hosted CI is pending at publication.

## Sources and scope

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
[SOURCES.json](SOURCES.json) binds the current task catalogue, selected
record and main proof premises. The unmerged predecessor's exact proof
and README are retained unchanged in `prior/`, with its original notices.
[PREDECESSOR.json](PREDECESSOR.json) records its upstream PR, author,
exact head and local byte hashes. Those files were retrieved directly
from that GitHub head. No cached unmerged commit is required at replay.
The predecessor's executable or numerical results are not replayed.

Credit CubeJerry for the height-uniform theorem and inverse-prefix scratch
bound; Arham Tahir for the power-of-two scalar lower family; Hanson Sun
for unit-monomial prefix entries; Charles Bethin for phase identities and
the squarefree interval theorem; Chafik Boukhalfa for the balanced word;
and the precision/restoration lineage credited in the retained sources,
including Philipp/mightyOil, Gareth Davidson and 0xkilgore. Nick Petalas's
older upper-bound work is predecessor context. The new unequal-child
upper proof and last-leaf extension are the contribution here.

The selected frontier and all five framework assumptions remain unchanged.
This does not determine arbitrary fixed n, actual rounded error transport,
internal leaf magnitudes, preparation, tape costs, physical hosting,
supplier admission or a complete multiplication theorem. For commuting
factors with subset-product bound Q>=1, the cited squarefree premise
gives the sufficient bound G(h)Q; equality for arbitrary Q is unclaimed.

The verifier has no recursion, network calls or subprocesses. Literal
emission is capped at 17 factors and scalar traversal at 2^32+1 factors;
each traversal has an explicit budget. Python-managed allocation is a
documented Power of Ten deviation, bounded by those capacities. The six
negative-fixture callbacks have fixed local targets. Functions stay below
60 lines. No separate static type check was run. Normal and optimized
`-W error -X dev` replay supplies runtime diagnostics.

## Open next questions

1. Determine the sharp envelope at other exact factor counts. Retain
   correlated target/scratch support statistics in the six phase pairs.
   Simultaneous attainment remains the obstacle. This package settles
   only n=2^h+1 and stops at that improvement.
2. Bind a rounded caller with this exact size and its actual perturbation
   support. Compare the destination-only estimate before changing a
   sufficient precision budget. Rounded semantics, inverse preimages,
   preparation and the full tape invoice remain required.

[TASK.json](TASK.json) gives the structured questions and scope change.
