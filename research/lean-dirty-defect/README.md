# Lean proof and sharper envelope for dirty-register defects

This package kernel-checks the composition implication behind
[PR2596](https://github.com/CrocSwap/integer-mult-bounds/pull/2596), then links it
to the existing `NonlinearEcho` integer dispatcher. It proves a new error bound,
not only the previously formalized exact cancellation/restoration identity.
The actual PR628 rounded leaf and the complex Euclidean norm are **not**
instantiated here. Their analytical estimates remain explicit external inputs.

For an earlier block B and later block A, the increment is

```
G_node(x,z,t) = G_A(z + G_B(x,t),t) - G_A(z,t).
```

With additive shadows S_A,S_B, a Lipschitz bound K_A for S_A, and uniform
defects E_A,E_B, Lean proves

```
error_node <= K_A E_B + 2 E_A.
```

For every ordered binary tree with n leaves, each leaf shadow bounded by L,
each leaf defect bounded by E0, **L >= 2** and **E0 >= 0**, it then proves

```
error_tree <= n L^(n-1) E0.
```

The package also improves this generic bound. Define H_0=0 and
H_(n+1)=L^n+2H_n. For **every L >= 0**, Lean proves

```
error_tree <= H_n E0,
(L-2) H_n = L^n - 2^n.
```

Thus for L>2 the bound is `(L^n-2^n)/(L-2) * E0`. This is the exact maximum
of the scalar tree recurrence: a comb with each earlier child a leaf attains
H_n E0. It is **not** a claim that a physical nonlinear implementation attains
that error, or that no sharper error theorem exists. The formal proof uses
`H_(a+b)=L^a H_b+2^b H_a`, `2^b>=2` and nonnegativity.
It also proves `H_n <= 2 L^(n-1)` for L>=4 and n>=1. For example, at L=4,
n=7 the recurrence envelope is 8,128 E0 instead of 28,672 E0.
This removes the factor n from PR2596's data-rounding bound once its hypotheses
are instantiated; its separate shadow-to-ideal coefficient-perturbation term
still has a factor n.

The factors retain their original order. There is no commutativity assumption.
All initial borrowed rows are universally quantified, subject to the same
closed source domain. Neither balancing nor bounded initial dirt is assumed.

## Exact formal boundary

`Bound.lean` uses vectors `iota -> Rat`, with arbitrary index type `iota`.
Its `Gauge` supplies a rational-valued nonnegative function and the two
triangle inequalities for addition/subtraction. It need not be definite or
homogeneous. Shadows explicitly preserve addition and subtraction and satisfy
the stated gauge Lipschitz bound. The product bound is proved, not assumed.

`Domain` explicitly supplies closure under addition and subtraction. Each
implemented leaf must preserve the domain and have a defect bound for **every
source in that domain**. Initial source and all borrowed rows belong to it.
Shadows need not preserve the grid. Thus a grid-only leaf estimate is not
silently promoted to a bound on every rational input.

`delta_lift` proves equality with the pinned `NonlinearEcho.delta` after
coordinatewise integer-to-rational conversion, given leaf compatibility and
agreement on the finite scratch prefix. `execution_error` combines this with
the predecessor's proved `positive_increment`, so the bound applies to its
literal four-call integer evaluator. `execution_envelope` gives the stronger
H_n version through the same proved lift. Both allow arbitrary initial target y.
The integer evaluator's exact restoration/inverse theorem is reused unchanged.
An unused tail extends finite scratch to a total sequence; the proof requires
agreement only on the available finite rows.

The main roots are `commutator_bound`, `tree_recurrence`, `budget_closed`,
`all_tree_error`, `delta_lift`, `execution_error`, `budget_envelope`,
`envelope_division`, `comb_budget` and `execution_envelope`. `Examples.lean` also proves
a nontrivial full instantiation: scalar absolute value, shadow `S(x)=2x`, and
nonlinear leaf `f(x)=2x+sign(x)`, taking sign(0)=-1, for every tree/input/dirt.

PR2596 uses the maximum complex Euclidean norm, L=4R/beta^2 >= 4 and
E0=8Ru/beta^2 with frozen rounded coefficient powers. Our rational-valued gauge
is not that generally irrational norm. No equality of those formal objects is
claimed. A formal real/complex norm instantiation (or a separately proved
rational norm estimate with adjusted constants), grid scaling, actual leaf
semantics, coefficient preparation, ideal-product perturbation, integer storage,
aliasing and bit-reversible implementation remain outside this proof. This is
not a new supplier, exponent, physical scratch bound or full multiplication
theorem. The selected result is unchanged.

## Reproduction and controls

Python 3.12, standard library:

```sh
python3.12 -I -O -B research/lean-dirty-defect/verify.py
python3.12 -B scripts/research_package.py --package research/lean-dirty-defect
```

The default/registered replay authenticates source bytes and checks all 197
ordered binary-tree shapes with one through seven leaves, three dirty profiles
per shape, and exact Fraction arithmetic. The two-dimensional leaf shadows are
noncommuting shears of maximum-row-sum norm two; their nonlinear perturbations
have maximum norm one. Profiles include half-grid values and 10^12-sized dirt.
All 591 errors satisfy both the tree recurrence and the closed bound.
Another 985 scalar-recurrence cases cover all those shapes at L=0,1,2,7/2,4,
checking the geometric sum and the exact attained maximum for each leaf count.
This finite replay **does not run or certify the Lean proof**.

For the live kernel proof, install Lean **4.34.1** and pass its executable:

```sh
python3.12 -I -O -B research/lean-dirty-defect/verify.py --lean /path/to/lean
```

It freshly compiles the pinned `NonlinearEcho.lean`, `Bound.lean` and
`Examples.lean` in a temporary directory. It then issues genuine `#print axioms`
queries for nineteen roots, accepting only the standard `propext`, `Quot.sound`
and `Classical.choice` set, which the checked roots use. No stored log or receipt
is accepted as a proof. This is an audit
of these source modules, not a sandbox for malicious Lean metaprograms.

Five changed claims must fail compilation: removing the second endpoint
defect, weakening the scalar threshold, reversing shadow composition, and
omitting the dirty baseline subtraction, or changing the geometric numerator's
base from two to three. A real injected-axiom query is also
rejected. Independent exact controls show why the premises matter:

* `f(x)=2x+sign(x)`, x=1,z=0 gives error 4; replacing `2E_A` by `E_A`
  would allow only 3.
* `f(x)=x+sign(x)` gives error 3; L=1 would make the claimed two-leaf
  closed bound only 2.
* A quadratic leaf has unbounded dirty-dependent increments, so a local
  source test cannot replace a uniform defect hypothesis.
* The two noncommuting shears distinguish forward and reversed factor order.

Verification is read-only by default. `--write` explicitly regenerates the
finite receipt; even in that mode source pins must pass first. Raw source hashes
are checked before their text is consumed. Git is unnecessary for the direct
replay, including in a source export; the generic metadata runner additionally
checks historical Git provenance.

Validation on 2026-10-15: registered Python 3.12 replay and the complete live
Lean 4.34.1 run passed (Lean commit
`5045d0056413266e57c625dcd7c365b10e377c52`). A Git-free export with an empty PATH
passed without changing any exported file. Separate corruptions of the pinned
predecessor Lean source, new formal source, vendored handoff and finite receipt
all failed verification. Hosted CI was not checked.

## Sources, credit and overlap

The parent checkout starts at canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The task picker nonce is `9386e9fd9f519381fad76db42411aad2`; the prescribed
binding baseline passed. `TASK.json` records refinement, claim and overlap
coverage. The complete cached Discussion snapshot is 2026-10-15 15:22 UTC;
subsequent targeted REST checks are bounded supplements after GraphQL quota
exhaustion, not a claim of refreshed complete Discussion coverage.

The nonlinear restoration semantics and `NonlinearEcho` proof are Gareth
Davidson's (@bitplane), crediting chafreaky's PR628/PR663 construction. They are
pinned unchanged from main and remain in their existing package. The analytical
handoff is ywz65's PR2596 at
`8472f5470f7ef5f24a910ccdc73cdd0d000c002c`; its README is retained verbatim with
SHA256 and Git blob ID in `SOURCES.json`. Its proof gives the actual rounded-leaf
premise and the mathematical real-norm argument; this package contributes the
separate kernel proof of the rational interface and its integer-dispatcher lift.
The earlier generic fanout bounds and nonlinear Lean identity are not claimed
as new. Prepared for ywz65 with substantial OpenAI Codex assistance, Apache-2.0.

## Open next questions

1. Instantiate the actual rounded leaf and analytic norm in the formal
   interface. Start with real/complex norm theory or a rigorously adjusted
   rational-coordinate norm, then bind grid scaling and frozen coefficient
   powers. This is necessary before calling PR2596's leaf constants formal.
2. Formalize the separate ordered shadow-to-ideal product perturbation bound.
   Start with noncommutative telescoping and explicit operator bounds; that
   implication is not covered by the uniform data-defect theorem here.
