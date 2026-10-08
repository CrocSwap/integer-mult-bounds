# Coordinate flags for the split-pair witness

This finite conditional witness gives kappa = 12857195906507 / 250000000000000000
= 5.1428783626028e-5, about 0.02750% above PR71's 5.1414646104039e-5.
The bit saving is 25715714341 / 500000000000000. Roles, physical width,
recursive rank mass, scalar operations, paid clearing and copied endpoints
remain those of PR71. The changed object is the coordinate flag used to
decompose internal frame transitions into consecutive pivot blocks.

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

## Verification and scope

Run `make coordinate-flags-verify`. It checks source closure, regenerates
both words byte for byte, replays every ordinary and dirty basis vector in
both orientations, reconstructs physical transitions, and recomputes all
fixed-I+J profiles with the inherited exact CRT bounds. Six negative controls
reject inconsistent coordinates, missing source/output relabeling, missing
operations and aliased terminal roles.

The complete paid child list is rebuilt independently. Directed rational
moment bounds, an independent logarithm/exponential computation, 47 strict
constraints, seven margins, both next-grid rejections and exclusion of
PR71's complete profile at the new saving are checked.

The search used structured coordinate orders and bounded adjacent swaps.
No global optimum or practical speedup is claimed. This remains conditional
on the inherited all-size residual compiler, routing, recovery, prime
selection, fixed finite-alphabet multitape simulation and analytic transfer.
The full expanded repository rerun is pending; this package is a draft.

## Credit

Chafik Boukhalfa's PR71 supplies the split-pair graph and next-use scoring.
Rohan Garg introduced the split operation (PR59); Avi Eisenberg supplied
interval/pair assembly (PR62); Dominik Scholz supplied ranked frames and
pending controls (PR63/68); Rohan Arun supplied schedule and profile-cost
search (PR65/67); eumemic supplied the reversible compiler and physical
checkers (PR57). Credit also icekylinx, James Chang, Zhihao Chen, Aurel
Prosz/Paureel, Swapnil Jain, Alejandro Zarzuelo Urdiales, RaD/hipotures,
Douglas Colkitt, OpenAI and all inherited contributors. Existing sources,
licenses and notices are retained. Prepared by Rohan Arun with OpenAI Codex.
