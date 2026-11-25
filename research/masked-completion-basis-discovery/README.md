# Bounded basis search on changed masked E8 completions

**Exploratory checkpoint; no new K and no decoder floor.** One fixed eight-case
pass used four P112 rectangles and four P120 rectangles. Each initial matrix
is the normalized Gram matrix plus a nonzero rank-one term supported entirely
where the fixed binary mask allows an off-diagonal change. Every factorization
has nine terms, including the initially zero-cost added term.

All four P112 cases stayed at copy cost 64; all four P120 cases stayed at 72.
Each case took 32 accepted exact rational factor-basis changes. The complete
pass took 246.233 seconds on the author's machine. CHECKPOINT.json records the
seed, rectangle sizes, accepted move traces, final mask/rank check summaries,
minimum costs and factor fingerprints. It records observed search execution,
not an exhaustive mathematical exclusion or an independent replay certificate.
Final factors are not embedded in this checkpoint; reproduce the search to
materialize a successful candidate, if a changed future configuration finds one.

For a two-factor shear, replacing p_i by p_i+alpha*p_j and q_j by
q_j-alpha*q_i preserves the completed matrix exactly. The implementation
keeps integer vectors with rational term weights, normalizing integer gcds
with compensating weights. Candidate alpha values come from exact coordinate
cancellation ratios. Every trial support rectangle is repriced using the
original binary pairing. The final result of every case passed the retained
full rational mask check and two distinct binary-rank oracles. No rational
rank is substituted for this support-pairing cost.

The fixed seed is 20261023, with at most 32 accepted changes per case and a
five-minute wall limit. Trial alpha numerator/denominator sizes are capped at
12 bits; trial integer vectors at 192 bits. Moves stay within two cost units
of the starting bill. The seeded tie break explores neutral states while
avoiding repeated complete factor states. There are no additional restarts.
Eight rectangles and this restricted local walk do not cover all completions,
all bases, longer walks or other term counts.

To reproduce the discovery pass from the repository root, use standard-library
Python 3.12 and a **new** output directory:

```sh
python3.12 -I -B research/masked-completion-basis-discovery/search.py --output /tmp/masked-basis-replay
```

The output directory must not already exist. The portable wrapper authenticates
the exact source geometry/checker before executing it. No scientific search was
rerun after the recorded pass; publication changes only make source/output
paths portable, pin the input and add attribution. This checkpoint has no
registered replay hook or hosted mathematical-verification claim. Under a
slower machine the wall limit can stop before all eight cases finish.

Canonical investigation: [Discussion #5048](https://github.com/CrocSwap/integer-mult-bounds/discussions/5048).
The base is main 4c0a359d88f22f05189d51f48387750b801a45d4, priority revision 7,
selected conditional K=0.00302015. The source bytes and earlier exact
rank-nine-completion handoff are pinned or identified in SOURCES.json.

## Open next questions

The unchanged nine-factor local walk is stopped. A useful continuation must
change a completion or factorization premise and explain how its optimistic
full support-pairing budget can attain cost 63 on P112 or 71 on P120 before expanding the search. Any
actual improved decoder still needs source-compatible physical realization,
dirty restoration, native frame/phase and recursive rank admission, then a
complete paid supplier and compiler/outer invoice. Unknown costs are not zero.
No such physical or K claim follows from this checkpoint.

## Credit

Philippe Van Velzen supplies the masked gain/padding reduction; the
masked-e8-padding-transfer package supplies the exact geometry, candidate ABI
and independent binary-rank oracle. The P112 completion authors supply the
rank-nine handoff; DreamingOfClouds and the retained root/decoder contributors
keep their original credit. Native/compiler context retains Cao Yifan,
Cinna Davis, zxv and Jacob Alan Sussman where their premises are used.
New exploratory script/checkpoint by Cinna Davis with substantial OpenAI Codex
assistance. Apache-2.0. No subagents, independent human review, proof-kernel
acceptance or selected-frontier change is claimed.
