# Movable source cuts at two rank-eight merge frames

The two actual merge frames 983 and 991 cannot give a saving in the
snapshot model below. To form a k-dimensional subspace of the eight
centre queries through either merge frame costs at least `8k` added
native rank. In particular, all eight queries cost at least 64.

This result permits shared intermediate fields and arbitrary scalar
cancellation. It does not require eight separate cache paths. It does
not give a bound for a network that uses different merge spaces.

## Source and model

Use the pinned clean backward word and the snapshot rows in
`BACKWARD-SNAPSHOT-INTERVALS.json.gz`. Its decompressed SHA256 is
`3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c`.
The independently reviewed support law states that, on the input
family `X=JY`, with all helper and private inputs zero, an observation
at frame U uses only source ports q with `q perpendicular to U`.
The completed X and FULL helper baselines vanish on this family.

The model grants every actual snapshot at every time. All used frames
must be actual canonical subframes of one chosen frame V. Frame zero
is also allowed. A field can move from U to W when `U subset W`, at
cost `dim(W)-dim(U)`. The transition preserves its logical content.
Scalar gates can share, add, or cancel fields in a common frame.
After the queries reach V, they move to FULL. These are relaxations
of the real chronological and native-phase requirements.

The two chosen frames are

```text
983: [256,129,64,33,17,9,5,3]
991: [260,128,64,32,16,12,2,1]
```

There are 122 and 124 actual contained frames, respectively, when
frame zero is included. Their Hasse graphs have 238 and 246 edges.

## Cut argument

For a source-port set S, let `Omega_S` contain the frames at which
every source port in S is excluded by the support law. All free
observations in these frames vanish when Y is supported on S.

Choose any upward-closed set `Omega subset Omega_S` that contains V.
If `R restricted to S` has rank eight, its restriction is injective
on every k-dimensional centre-query subspace. Thus at least k
independent whole-array fields must enter Omega. This argument also
holds for arbitrary tensor size: the input, output, and field ranks
all acquire the same array-dimension factor.

The certificate gives seven such cuts for each V. Each has weight
one and a source restriction of exact rank eight. For every actual
inclusion `U subset W`, the number of cuts entered is at most
`dim(W)-dim(U)`. Sum the seven cut demands and charge each entering
field to its native transition. The internal cost is at least `7k`.
Completion from the rank-eight frame to FULL costs at least k.
The total is therefore at least `8k`.

Upward closure is not needed for the general rank-cut lemma. It is
used here to make the finite search and the edge check simple. The
general statement is in `../cover-algebra/MOVABLE-SNAPSHOT-CUTS.md`.

## Exact certificate and search

`MOVABLE-FULL-RANK-CUTS.json` gives all source sets, all seven inside
node sets, and all Hasse edges. The checker also checks every direct
inclusion edge. The two certificates use five and four distinct
source sets. Repeated uses of one source test have different cut
placements.

`probe_movable_full_rank_cuts.py` selects cut placements with integer
max-flow. It allows at most 24 trials on eight fixed source tests per
merge. Both certificates were found in the second trial. The proof
uses only the displayed cuts, exact source ranks, and exact edge
charges. It uses no float optimization or optimality claim.

Run:

```text
python3 -I -O -B probe_movable_full_rank_cuts.py
```

The final printed line for each merge reports `unit cuts 7`.
The source tests come from the frozen rank-five cut seed file and
two known orthogonal source minors. No source observation is added
to the clean word.

This closes strict savings through the two rank-eight convergence
frames above the weaker rank-six cases 982 and 990. Those rank-six
cases have bound `8k`; cases 774 and 782 have bound `9k`. The present
result does not change those bounds and does not prove a global
64-rank obstruction. It emits no new native word and gives no change
to the complete supplier calculation.
