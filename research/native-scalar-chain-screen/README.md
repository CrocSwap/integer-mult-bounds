# Corrective ADD chains in the round-three native word

No higher κ is established. In the frozen round-three word, the bounded
corrective expansions below never reduce the complete paid rank bill, for
any concave rank price with f(0)=0. The selected record has conditional
κ = 0.00302015 at the research base; this package changes no selected record.

Each orientation independently has 381 adjacent eligible chains and 1,512
nonadjacent eligible chains at raw-event distance at most 16. All three
placements of the corrective gate give 5,679 orders, of which 1,281 have no
legal monotone realization. The other orders have 4,621 feasible dimension
triples: 4,400 preserve the paid histogram and 221 strictly worsen every
power price r^t with 0<t<1. These counts describe each orientation separately.
No finite-subspace catalogue, floating price or discovery solver is used.

This tests a changed scalar dependency graph. The earlier
[commuting two-contact census](../commuting-warp-retiming/README.md) fixes two
commuting gates, while the [owned-wire floor](../monotone-owned-centre-floor/README.md)
fixes the scalar graph. Neither result supplies this census. The elementary
corrective identity, flag reduction and concavity method are prior work in
[CubeJerry's PR589 screen](../bit589-steinberg-fan-seed06/README.md), which
credits Ian Libânio's PR933, Dugongue's Steinberg work and the retained BIT
lineage. This package applies that method to a different, source-bound complex
native word, includes rational signs and coefficients, and moves the first
gate across fixed commuting contacts before expanding it.

## Exact domain

Remove only `climb` records when numbering the raw word. Choose two persistent
L-to-L ADDs g and h at indices i<j, with j-i<=16, on three distinct roles.
Exactly one gate writes a source read by the other. Every intervening event
must be a persistent L-to-L ADD commuting with g. No warp, phase, SCALE,
owned macro or adapter is crossed. Move g right across that fixed intervening
sequence M; reverse g,h; insert their corrective ADD first, middle or last
in the resulting three-gate cluster. Every intervening contact frame, all
external contacts, native maps/pairs, main/helper endpoints and owned-center
jobs remain fixed. The three cluster frames may be arbitrary binary subspaces
of F2^9, including spaces absent from the source registry. Ordinary transport
must be monotone, and each scalar ADD has one common physical contact frame.

For chronological g=(a+=c*b), h=(b+=d*v), the correction is a+=-c*d*v.
For g=(b+=c*v), h=(a+=d*b), it is a+=c*d*v. The correction commutes with g
and h. Thus all three placements reproduce the original rational map on
arbitrary input values. Since g commutes with M, the replacement is also an
identity in the full word. The verifier checks each actual rational identity
and the necessary middle-gate commutations; it does not presume zero helpers.

Every transition on an affected role is charged, including the bridge that
bypasses the old g, transitions through M and exits to the next fixed contact
or native input. All other transitions and every productive boundary are
unchanged. The complete source profiles are reconstructed as positive controls:

```text
paid:    {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}
helpers: {4:28, 7:7, 8:47, 9:326}
```

## Why the dimension census is complete

After the fixed prefix M, let P_r be the actual entry subspace on each of the
three roles, and Q_r its next fixed external subspace. For a particular order
of the three corrective gates, define

```text
L1 = sum of P_r on the first gate's operands
L2 = sum of P_r on all three roles
U2 = intersection of Q_r on all three roles
U3 = intersection of Q_r on the last gate's operands.
```

Every pair of successive gates shares a role, so their contact spaces satisfy
F1<=F2<=F3. All roles occur among the first two and last two gates. Consequently
L1<=F1, L2<=F2<=U2, F3<=U3. If L2 is not contained in U2, no realization exists.
Otherwise L1<=L2<=U2<=U3 is an actual flag of binary subspaces. A rank triple
(d1,d2,d3) is feasible exactly when

```text
dim(L1) <= d1 <= d2 <= d3 <= dim(U3)
dim(L2) <= d2 <= dim(U2).
```

Necessity follows from containment. For sufficiency, choose a basis adapted
to L1<=L2<=U2<=U3 and take its first d1,d2,d3 vectors. These spans meet all
entry, common-contact and exit requirements. The fixed prefix's bypass
containments are checked separately. Thus ranks suffice: the calculation
covers every binary frame schedule in the stated domain, rather than a
sample of candidate bases. The same flag argument applies over other fields,
but this package makes its source claim only for the declared binary grammar.
An independent finite control enumerates every nested boundary flag and every
candidate F1<=F2<=F3 in F2^3 and compares the attainable dimension triples.

For candidate histogram n and source histogram b, each affected wire has the
same fixed entrance/exit, so sum r*(n_r-b_r)=0. The verifier additionally checks
that identity and the nine integer inequalities

```text
S_k = sum_r (n_r-b_r)*min(r,k) >= 0,  k=1,...,9;  S_9=0.
```

Writing s_k=f(k)-f(k-1), concavity gives

```text
f(r) = s_9*r + sum_{k=1}^8 (s_k-s_{k+1})*min(r,k).
```

The cost difference is nonnegative. For r^t with 0<t<1, every curvature
coefficient is strictly positive; a distinct equal-mass histogram has a
nonzero cut slack, so its cost is strictly higher. The unchanged productive
inventory and all fixed controller bills cannot extract a higher κ from
these substitutions. Added scalar work is an additional nonnegative cost.
This is a bounded supplier-profile conclusion, not a universal word optimum.

## Reproduce and evidence

From the repository root, standard Python 3.12 or later:

```sh
python3 -B scripts/research_package.py --package research/native-scalar-chain-screen
python3 -I -W error -B research/native-scalar-chain-screen/verify.py
python3 -I -O -W error -B research/native-scalar-chain-screen/verify.py
```

The registered replay uses the last two commands. It authenticates the source,
reconstructs both complete source invoices, checks every chain/placement/rank
triple, and compares RESULT.json. The receipt retains the histogram-delta census
and a SHA256 of every ordered local record, including its actual entry/exit
frame IDs, baseline histogram, candidate ranks and all cut slacks. It is
reconstructed afresh, not trusted as an acceptance oracle. `--write` regenerates
this deterministic receipt; ordinary verification writes nothing.

Controls include 108 exact rational identity fixtures, seven rejection controls,
and an improving boundary fixture from the credited PR589 package. That fixture
changes {1:4} to {1:2,2:1}; the checker detects its negative cut slack, rejecting
a false universal obstruction. All 355 nested three-bit flags independently check
the rank-feasibility reduction. Metadata/pin validation is separate from these
mathematical checks. No Lean, historical full replay or optional solver is run.

SOURCES.json pins the exact live source and historical task/selected records.
Frozen predecessor bytes remain unchanged. Evidence is author checked with
substantial OpenAI Codex assistance, without subagents, independent human review
or proof-kernel acceptance. Native all-column realization, physical phase,
owned erasure, uniform compilation, precision/tape and analytic integer recovery
are inherited obligations and are not verified here.

## Open next questions

A different scalar graph must affect a rank bill before further implementation.
This census excludes neither interacting replacements, retiming the intervening
contacts, changed helper boundaries/native contracts, nor other scalar identities.
A bounded next test should exhibit one explicit candidate with its complete
changed paid/helper histogram, then perform arbitrary-input and signed native
replay only if the moment improves. Increasing this window without evidence
of a new cost lever is not proposed. A whole-profile optimum remains unproved.

Credit Cao Yifan's #4610/round-three word and native-map/helper work; Cinna
Davis's #4470 and subsequent native/controller work; Dugongue's transported
frames; CubeJerry, Ian Libânio and the credited corrective/concavity lineage;
zxv, Jacob Alan Sussman and the retained scalar, E8, Clifford, precision,
compiler and outer contributors. Prepared by Cinna Davis / 1337isnot1337 with
substantial OpenAI Codex assistance. Apache-2.0.
