# Envelope ordering inside balanced split compilation

The finite conditional witness gives **kappa = 5203279888519/100000000000000000 = 5.2032798885190e-05**,
0.49049670% above PR80. Bit saving is 13008876609597/250000000000000000.
The full expanded repository verification passed on research commit `3410b940aa26e5876202152dfa7c4f66451ee22c`; see `validation.json` for the log hash, timing and coverage.

PR80 selected already-compiled axes from PR76 and PR79. Here we compose
their construction methods before compilation on both axes: PR79's balanced
coarse graph and future-compatible unit completion; PR76/PR74's envelope
node ordering; three passes of PR79/PR70's bounded carry exchanges; and
PR78's geometric coordinate flags. h23 uses the half-plane coarse choice
and cover-core schedule; h25 uses row coarse sums and reverse-node schedule.
Both retain the anchored [1,1,2] split vector and exact next-use profile costs.
All archived sources are unchanged. `compiler.py` is the portable composition.
At h25 the discovery oracle receives coordinate-permuted frame masks, so its
costs refer to the final flag rather than the original coordinate order.
`flag_engine.py` differs from PR79's engine only in that oracle frame writer
and an attribution comment; operations, eligibility, independence and dirty
checks are unchanged. This changes only heuristic selection among legal
choices. Its final word is still independently replayed and exactly priced.
At h23 oracle pricing retains the original coordinate order.

| Quantity | PR80 | This witness |
|---|---:|---:|
| h23 auxiliary roles | 27256 | 27075 |
| h25 auxiliary roles | 35684 | 35500 |
| Physical width | 134031764 | 133289600 |
| Total recursive rank | 77066417400 | 76639673100 |
| Deficit | 1846900 | 1846900 |

## General compatibility argument

Balanced coarse parenthesization changes only how the same Cartesian-product
edge sums are evaluated. The weighted scalar identities and recursively
contracting anchored partition are inherited from PR79's proof. Envelope
ordering then applies a bijection to non-source scalar node IDs, grouping
nodes by (core, cover), preserving the order inside each group and every
argument, output and provenance reference. It changes no scalar linear form
or frame. The graph verifier is rerun after this relabeling. Dependency and
carrier-eligibility checks in the compiler remain enabled.

Future-compatible completion chooses independent unit rows after the desired
outputs and retained carriers. Any accepted independent completion is a full
invertible basis; the unchanged synthesis emits its literal XOR operations.
Bounded carrier exchanges preserve matching cardinality, unique uses and
independence of the output-plus-retained-input rows. These choices can change
each other's costs, so the words are recompiled and every profile recomputed;
we do not add reported savings or assume independent numerical gains.

All clearing targets and controls remain charged. Both frame-containment
checks for pending controls remain enabled. The compiler and independent
replay verify the full arbitrary-dirty-role wrapper in both orientations.
Independent axis implementations expose the same source triple lines, fixed
I+J basis, terminal frames and scatter identity. Hence the complete tensor/data
construction is unchanged. Every endpoint/copy/data-growth/complex term is
retained exactly once. The fixed-width bridge is derived from the actual W.

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

## Reproduction and validation

From the repository root with assert-enabled Python 3.11+ and C++17:

```sh
python3 research/envelope-balanced/verify.py --regenerate
(cd research/envelope-balanced && python3 -m unittest test_controls -v)
make verify
```

The regeneration option launches two isolated compiler processes and requires
both original words to reproduce byte-for-byte. The verifier then regenerates
the coordinate-permuted words, performs independent full input/dirty replay,
reconstructs all transitions, and regenerates exact bounded-minor/CRT profiles.
The complete paid child list is reconstructed; independent rational moment
bounds, 47 strict inequalities, seven margins and both next-grid exclusions
are checked. The complete PR76, PR79 and PR80 child lists are each excluded at
the new bit saving using their own width. Six physical/coordinate failure
controls and three stale bridge controls run separately. A dedicated
three-version CI workflow retains every inherited workflow.

The bounded searches are not proofs of global optimality. All inherited
all-size residual compiler, routing, recovery, prime selection, finite
alphabet/tape, precision and analytic transfer interfaces remain hypotheses.
No unconditional multiplication theorem or practical speedup is claimed.

## Attribution

Thomas DiFiore (PR74) introduced the envelope ordering; Dominik Scholz
(PR76) composed it with carried exchanges; Chafik Boukhalfa (PR79/71)
provided balanced/future/exchange and anchored split compilation; eumemic
(PR69/57) provided balanced coarse sums and reversible compilation;
Alejandro Zarzuelo Urdiales (PR70) supplied the carry-exchange strategy;
Rohan Arun (PR78/80/65/67) supplied coordinate flags, axis selection,
schedules and profile-cost reclamation. This new pre-compilation composition
and finite selection were prepared by Rohan Arun with OpenAI Codex assistance.

Credit also Rohan Garg, Avi Eisenberg, icekylinx, James Chang, Zhihao Chen,
Aurel Prosz/Paureel, Swapnil Jain, RaD/hipotures, Douglas Colkitt, OpenAI,
Harvey–van der Hoeven and all inherited contributors. Original licenses,
author and AI-assistance notices remain preserved. Tested PR75 zero-circuit
variants were not selected for this witness and are not claimed as its method.
