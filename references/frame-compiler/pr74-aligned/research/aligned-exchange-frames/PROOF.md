# A paid finite witness from aligned partitions and carried-signal exchanges

## Statement and conditional scope

The authoritative exact values of `kappa` and `bit_saving` are the rational
fields with those names in [certificate.json](certificate.json). Together
with its complete paid profile and assembly checks, they certify the inherited
conditional bound

`T(n) = O(n (log n)^(1-kappa))`.

The all-size compiler and analytic transfer remain assumptions, as do the
inherited fixed-alphabet tape simulation, precision, routing, prime selection,
and exact recovery hypotheses. The finite graph, word, profile, and rational
checks below do not establish those general hypotheses. This document makes
no claim that the selected finite witness is optimal.

## 1. Pinned scalar construction

The original PR #71 source closure is archived at commit
`1bef94fd40a746452548c84a4a8f8834670a3113`, and the balanced coarse-sum source
from PR #69 at `91aa1f17e6e3fc063241686a41a34ddd0dc24c50`. The original sources,
licenses, notices, and predecessor manifests are preserved. The selected
source manifest also pins the local producer, policies, configurations, and
independent checkers; construction rejects changed inputs.

The scalar graph uses dimensions 23 and 25 with the complete bases of 1,771
and 2,300 triples. It splits six aligned top-level pairs for dimension 23 and
nine for dimension 25. The deeper choices are `[1,1]` and `[1,1,2]`,
respectively. The first three levels use half-plane row/column factoring;
later levels use columns. The matching intact global pairs are placed first in each
common-point ordering. The precise choices, contraction cap, weighted
exclusion identity, anchor permutation, and source hashes are proved in
[partition-proof.md](partition-proof.md).

The contraction cap retains at least one pair and strictly decreases the
number of points in every recursive call. Splitting several pairs preserves
the partition into groups of size one or two, so the inherited weighted
singleton/pair identities apply. Balanced row/column sums retain each original
summand exactly once. No cancellation or uncharged linear identity is used.

The active nodes are grouped by their original `(core,cover)` frames, then
ordered by increasing frame rank, decreasing core, increasing cover, and
first original node. Source IDs and the original order inside each frame
remain fixed. Every edge between different frames has strictly increasing
rank; the preserved internal order handles edges within a frame. The graph
audit checks this literal remapping, exact operand chronology, all dense
global triple supports, disjoint additions, every core/cover recurrence, and
the entire prescribed output set. The resulting scalar graphs have 84,930
and 117,256 additions and 5,336 and 6,925 prescribed outputs.

## 2. Matching and future unit-row completion

The inherited compiler first computes a matching of eligible carried signals.
The selected PR #84 engine makes up to three single-edge passes and three
two-edge cycle passes. Its archived code is unchanged except for private
location bindings, explicit coordinate pricing, and the frozen pass count. Every selected
edge remains in the inherited eligible list. Use uniqueness, matching
cardinality, and independence of each region's desired-output-plus-carried
rows are preserved. [exchange-proof.md](exchange-proof.md) gives the local
exchange argument and the final explicit independence checks.

At a region with `d` input coordinates, let the independent desired output
rows and selected carried unit rows form the initial row list. The PR #79
future-compatible completion orders the remaining candidate unit rows by
the number of later compatible uses, then by current signal support size
and input index. It appends a row only after an exact binary independence
test. Since all `d` standard unit rows are considered and span the input
space, this extends the independent list to a full basis regardless of the
priority rule. The priority changes the chosen completion; it is not a
correctness assumption about later reclamation.

The inherited elimination synthesizes the complete invertible basis change
as literal XORs. All copies, swaps as synthesized XORs, carried signals,
clearing operations, and required frame raises are serialized. Pending live
controls can enter a clearing basis only when their current frame is
contained in the present frame and the present frame is contained in their
next-use frame. Each such control retains its value. These eligibility checks
are separate from the score that chooses among eligible operations.

The exact PR #84 retired and pending indexes select the same eligible roles
in the inherited iteration order, updating them at every raise, retirement,
assignment and removal. They accelerate candidate queries; the independent
literal replay validates the resulting physical construction. For h25,
outgoing uses are sorted by descending future deadline, with terminal uses
last in execution time and use ID breaking ties. This changes which physical
role is retained for each use; all other occurrences still receive paid copies.
h23 retains baseline outgoing-use order.

## 3. Discovery coordinates and final physical coordinates

`selection.json` records two explicit permutations for each axis.
`pricing_permutation` specifies the coordinate flag used by both matching
and clearing discovery oracles. Core and cover masks are permuted before
the oracle evaluates its fixed-basis transition profiles. Its reproducible
integer profile-entropy score only chooses a finite construction. It does
not replace any charged operation or serve as a moment certificate.

`coordinate_permutation` specifies the final relabeling of the physical word;
it may differ from the pricing permutation. The producer applies it to all
frame masks, source-triple labels, scatter targets, output common points,
and output triples. Scratch IDs, literal XORs, and frame IDs are unchanged.
Each relabeled word is replayed and its actual ordered profiles are rebuilt.
Thus a subsequent coordinate improvement requires its own actual profile
even when the construction was priced using an earlier coordinate flag.

For a permutation matrix `P`, the fixed basis `I+J` and the inherited
permutation-invariant projector metric commute with `P`. The envelope
projectors consequently transform by conjugation. Incidence, containment,
and invertibility remain valid, while ordered contiguous child profiles may
change. This is why the final word's exact profiles are regenerated.

Each permutation also gives a bijection on the complete triple family.
The full two-axis data-block family and its rational recovery cases are
therefore reindexed. Their aggregate inherited geometry and paid profile
remain valid; the final axis profiles retain all copied centers, endpoints,
and growth costs.

## 4. Complete dirty-basis word and exact profiles

The full two-copy word is checked on every ordinary-input coordinate and
every arbitrary scratch coordinate, in both the forward and dual
orientations. The checks establish the prescribed input/output shear and
exact restoration of the scratch registers for arbitrary dirty contents.
An independent checker repeats the calculation from the serialized word,
validates every physical frame inclusion, and checks its expected hash.

The selected role counts are `R_23=26409` and `R_25=34772`. The full basis
checks therefore use `2*1771+26409=29951` and `2*2300+34772=39372` coordinates.
These role counts describe the literal physical construction, including
reclamation and all selected basis changes.

The transition preparer derives the fixed-`I+J` matrix inventory from the
serialized events and endpoints. The retained exact bounded-minor/CRT
profiler computes the final child blocks, and all CRT profile disagreements
must be zero. The same nested-frame formulas and exactness bounds apply:
the partition and matching changes alter which legal transitions occur,
without changing their matrix family. The per-axis rank identities are

`sum_t t*b_(23,t) = 23*26409 + 23*22 = 607913`,

`sum_t t*b_(25,t) = 25*34772 + 25*24 = 869900`.

Rebuilding profiles from the selected final word prevents a discovery
histogram or an earlier coordinate profile from being substituted for the
actual paid costs.

## 5. Complete recurrence

Let `N=4073300=1771*2300` and `m=575=23*25`. The complete width is

`W = 2N + (N/1771)*R_23 + (N/2300)*R_25 = 130468512`.

The child multiplicity multiset contains all of the following terms:

| Contribution | Paid children |
| --- | --- |
| Data blocks | `18N` of size 1; `2N` each of sizes 21, 17, and 481 |
| Endpoint copies | `N` additional children of size 1 |
| Internal axis `h` | `(N/binom(h,3))*b_(h,t)` children of each size `t` |
| Exterior axis `h` | `(N/binom(h,3))*R_h` each of sizes `h` and `m-2h` |
| Data growth, each axis `h` | `2N` each of sizes 1 and `h-2` |

The checker reconstructs these contributions separately and compares their
sum with the supplied multiplicities. Their total rank is

`sum_t t*n_t = mW - 1846900 = 75017547500`.

The maximum child size is 529, strictly below `m`. The deficit `1846900`
is unchanged because the full input/output geometry is unchanged. The
inherited complex recurrence and its charges are retained in the finite
bridge and assembly; they are not omitted from the final saving.

## 6. Strict moment and finite assembly

For the exact rational `a=certificate.json.bit_saving`, define

`M(a) = sum_t [t*n_t/(mW)] * exp(a*log(m/t))`.

The certificate supplies a rigorous upper bound below 1 at `a` and a
rigorous lower bound above 1 at `a+10^-18`. Every logarithm is positive,
so the characteristic is strictly increasing. Production arithmetic uses
the retained exact rational logarithm/exponential bounds. The independent
arithmetic checker reconstructs the complete paid multiset and uses its own
40-term atanh logarithm sums and degree-ten exponential expansion with a
geometric tail bound. It does not import the production arithmetic or
assembly routines.

The assembly retains positive backoff `10^-18`. Since
`2^26 < W < 2^27`, the bit width is 27. The product-row coefficient is
`9*27+20*30=843`. With degree 2000 and suffix slope 8000, its degree gap is
`2000-(51/25)*843=7007/25`. The checker derives these quantities from the
actual width, avoiding stale predecessor constants.

The exact value `kappa=certificate.json.kappa` must satisfy all 47 assembly
inequalities and all seven strict margins. The independent checker derives
and checks those slacks separately; the next `10^-18` kappa grid value is
rejected. The source, replay, profile, moment, and assembly gates together
certify this finite conditional witness. Arithmetic cutoff bounds are not
complete operational runtime thresholds.

## Credits and notices

The aligned multi-pair choices, continued core ordering, selected coordinate
flags, two-edge extension, composition, packaging, and independent audits
were prepared for Thomas DiFiore with substantial OpenAI Codex assistance.
The construction builds on:

- Rohan Garg's split operation (PR #59);
- Avi Eisenberg's interval strips and core-aware pair assembly (PR #62);
- Dominik Scholz's ranked composition and pending live controls (PR #63/#68);
- Rohan Arun's region schedules, profile-cost selection and geometric
  pricing composition (PR #65/#67/#82);
- eumemic's reversible compiler and physical/profile interfaces (PR #57),
  and balanced coarse-sum reassociation (PR #69);
- Chafik Boukhalfa's anchored splits and next-use-aware live selection
  (PR #71), future unit completion (PR #79), and exact candidate indexes,
  bounded two-cycles and outgoing-use routing (PR #84);
- Alejandro Zarzuelo Urdiales's carried-signal exchange method (PR #70);
- Dominik Scholz's integer profile-entropy pricing and one-edge exchanges
  (PR #76);
- our earlier PR #74 core-order and coordinate-relabeling continuation.

The preserved archives retain all earlier credits, including RaD/hipotures,
icekylinx, James Chang, Zhihao Chen, Aurel Prosz, Swapnil Jain, Douglas Colkitt,
OpenAI, Harvey–van der Hoeven, and predecessor AI-assistance disclosures.
Original Apache-2.0 licenses and notices remain in force. No predecessor
authorship, endorsement, or priority claim is implied by this composition.
