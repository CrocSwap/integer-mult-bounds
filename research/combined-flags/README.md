# Combining envelope, balanced and geometric coordinate methods

The finite conditional witness gives **kappa = 51778825456819 / 10^18
= 5.1778825456819e-5**, 0.06415998% above PR79 and 0.077600% above PR76.
The bit saving is 51781506642569 / 10^18. Axis selection alone gives
kappa = 51767625345147 / 10^18; coordinate ordering supplies the remaining
gain (the exploratory ablation is recorded in `ablation.json`). This is a draft: the new focused
checks pass; the full expanded repository run remains pending.

Use Dominik Scholz's PR76 h23 word at
`83d4169ac9626b0ea542fd057d522b7bec850a53` and Chafik Boukhalfa's PR79
h25 word at `9a58e62cf9e8954a4dde3c9b1372d733c276a6d1`, then apply
our PR78 coordinate-flag method to each axis. This selects compatible
complete axis implementations; it does not add their reported percentage
gains. The selected coordinate orders are in `order-23.json` and
`order-25.json`. They were found by bounded adjacent-swap exploration.

## Why the axes combine

Both parent constructions implement the same complete triple-indexed
linear map and its arbitrary-dirty-role wrapper. They expose the same
fixed I+J basis, source triple lines, terminal frames, scatter identity,
and paid cleanup interface. Only their internal scalar DAG/physical word
and auxiliary role counts differ. Substituting one complete implementation
on each independent axis therefore preserves the tensor construction.
The data component is the inherited full Cartesian product of all 1,771
and 2,300 source triples. Both parents retain precisely the same data,
copied-center, endpoint and complex components; no data gain is counted twice.
Coordinate relabeling preserves those interfaces as explained below.

The resulting role counts are 27,256 and 35,684. Every internal transition
is regenerated from the actual relabeled word. With N=4,073,300,

    W = 2N + 2300*27256 + 1771*35684 = 134031764
    total recursive rank = 575*W - 1846900 = 77066417400.

The verifier independently reconstructs all internal and external recursive
children, including every copied endpoint and both data growth terms.
Width remains below 2^27. The bridge is derived from W: 27 wire bits,
row coefficient 843, degree 2000 and degree gap 7007/25; suffix slope 8000.
All 47 inequalities, seven margins and both adjacent-grid exclusions pass.
Both parent complete child lists are separately excluded at the new bit
saving using each parent's own width, not the combined width.

## General relabeling argument

Let P be a permutation matrix on the h coordinates. It commutes with J,
so P commutes with the fixed basis L = I+J and preserves the form I-J/9.
For a core/cover frame F(C,U), the relabeled projector is
P F(C,U) P^-1 = F(P C,P U). Consequently, every frame inclusion, rank,
nondegeneracy condition, projector denominator bound and elementary role
operation is preserved. The existing exact CRT bounds apply unchanged.

Relabel each input triple T to P T, each output (c,T) to (P c,P T),
each frame mask by P, and each scatter row by the induced triple permutation.
The role slots and literal XOR operations do not change. This conjugates
the complete linear word by the input/output permutation and therefore
preserves its identity on every ordinary input and arbitrary dirty role.
The verifier independently replays that identity in both orientations.

The data component sums over every pair of source triples. Independent
coordinate permutations on the two axes induce a bijection on that complete
Cartesian product. Hence its existing complete histogram, copied-center
costs and endpoint corrections are unchanged. This argument uses the full
case set; it would not justify retaining a selected subset's histogram.

North-east corner rank profiles depend on the fixed coordinate order.
Conjugating by P can change which adjacent pivots form a recursive block,
even though total rank is unchanged. We regenerate these profiles from the
actual relabeled words rather than assuming their costs are invariant.
Both dimensions use the selected orders in order-23.json and order-25.json.

## Reproduction and scope

From the repository root, with assert-enabled Python 3.11+ and C++17:

```sh
python3 research/combined-flags/verify.py
(cd research/combined-flags && python3 -m unittest test_controls -v)
make verify
```

The new verifier checks source closure, regenerates both permuted words
byte-for-byte from immutable parent words, independently replays all input
and dirty basis vectors in both orientations, reconstructs physical frame
transitions and recomputes exact bounded-minor/CRT profiles. Exact directed
moment bounds are cross-checked by an independent rational calculation.
Six physical/coordinate failure controls and three stale bridge controls
are included. The dedicated CI workflow runs these new checks on Python
3.11, 3.13 and 3.14; all inherited workflows remain enabled.

PR79's complete portable source/verification package is inherited by this
branch. PR76's original scheduling package, witnesses, licenses and source
pins are preserved unmodified under `references/frame-compiler/pr76/`.
Its original regeneration scripts require their documented PR71 baseline
archive; the new verifier needs no external archive and consumes its frozen
word directly. This distinction is explicit: deterministic regeneration of
our relabeling and serialized replay do not establish portable deterministic
regeneration of PR76's original graph/compiler search.

The result remains conditional on all inherited all-size residual compiler,
routing, recovery, prime selection, finite-alphabet multitape, precision
and analytic transfer hypotheses. Finite tests do not establish these
all-size obligations, global optimality, or practical runtime improvements.

## Attribution

Dominik Scholz's PR76 supplies envelope-ordered carried-signal exchanges
at h23, using Thomas DiFiore's PR74 ordering and Alejandro Zarzuelo
Urdiales's PR70 exchange method. Chafik Boukhalfa's PR79 supplies balanced
coarse sums, future unit completion and exchanges at h25, building on
eumemic's PR69 and the PR71 anchored split construction. Rohan Arun's PR78
supplies geometric coordinate-flag relabeling. This axis selection,
coordinate search and certificate were prepared by Rohan Arun with OpenAI
Codex assistance.

Credit also Rohan Garg (PR59), Avi Eisenberg (PR62), Dominik Scholz
(PR63/68), Rohan Arun (PR65/67), eumemic (PR57), icekylinx, James Chang,
Zhihao Chen, Aurel Prosz/Paureel, Swapnil Jain, RaD/hipotures, Douglas
Colkitt, OpenAI, Harvey–van der Hoeven and all inherited contributors.
All original licenses, author and AI-assistance disclosures remain intact.
