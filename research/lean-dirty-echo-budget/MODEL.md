# Formal statement and trust boundary

`Fits s n N` is an inductive proposition, not a predicate assumed about an
opaque optimizer. Its constructors are:

1. A leaf fits every nonnegative budget, with one factor and one call.
2. Given first and last children and a list of interior child profiles, all
   fitting budget `r`, combine them at budget `r + middle.length + 1`.
   Add the factor counts. Charge the endpoints twice and the interior calls
   four times.

If there are `k` children then `middle.length+1=k-1`. This is exactly the
reserved-parent-pool recurrence in PR784's `PROOF.md`, Section 2. A child
with a smaller minimum requirement can be admitted at the common remaining
budget by the proved `weaken` theorem. Every derivation is finite; internal
arity is at least two. Factor order is represented by the first/interior/last
positions, though the resource inequalities depend only on their counts.

The original `Plan` also contains a specific ordered tree and requires the
same subtree whenever that child is invoked. Constructor derivations build
one admissible resource tree with those child witnesses. They are a model
of that static grammar, not an encoding of arbitrary adaptive programs.

## All-size proofs

**Capacity.** Induction gives `n_i <= 2^r`. Summing and using
`k <= 2^(k-1)` yields `n <= 2^(r+k-1)`. The leaf is immediate.

**Lower bound.** We state `2^(s+1)*n <= N+4^s` over natural numbers. This
avoids truncated subtraction; `call_lower_bound` derives the familiar
subtractive form. The proof deliberately differs from the paper's single
general-arity polynomial calculation:

- For a binary node, multiply the two child inequalities by two and add.
- For a ternary node, weight them by 2,4,2 and use the endpoint capacity
  inequalities to pay the remaining deficit.
- For arity `k>=4`, `2*k <= 2^(k-1)`. Therefore the node has at most half
  its budget's binary capacity: `2*n <= 2^s`. Already
  `2^(s+1)*n <= 4^s`, so the claimed lower bound is nonpositive in its
  subtractive form. The original 2/4 cost formula is still present in the
  constructor; the proof has not relaxed the admitted class.

**Feasibility.** `positive` and `capacity` prove necessity. For sufficiency,
split `n>=2` into `floor(n/2)` and its complement. Both are positive and fit
the next smaller binary capacity. Use `binary_join`; a one-factor problem
uses the leaf constructor at the available budget.

**Equality.** Write `s=d+2`. At `d=0`, a flat three-leaf node costs 8 and a
balanced four-leaf tree costs 16. For the next level, halve `n` as above.
Both halves lie in the preceding equality interval. Join their attaining
trees with a binary root. Twice the two equalities sums to
`N+4^(d+3)=2^(d+4)*n`. This constructs every integer in the band; it does
not extrapolate from the checked optimizer outputs. `sharp_minimum` combines
this equality with the universal lower bound. Substitution at `d=4,n=50`
gives the explicit `exact_50_6` theorem.

All eight public audited statements elaborate with warnings treated as
errors. Their transitive axiom lists are in `EXPECTED.json`. Lean's standard
propositional extensionality, classical choice, and quotient soundness are
the entire admitted axiom set. They are not arithmetic or resource
assumptions specific to this problem.

## Executable correspondence is bounded evidence

`verify.py` enumerates shapes independently of the pinned planner. For each
shape it recursively constructs a source `Plan`, compares the three resource
fields to a separate recurrence calculation, and emits a Lean proof using
that shape's actual children. The theorem's numeric profile is taken from
the source `Plan`. Each proof must elaborate by the model constructors and
the independently proved weakening rule. Shared subtrees reuse existing
lemmas. The full census through eight factors has sizes
`1,1,3,11,45,197,903,4279`.

For the 36 equality-band optimizer outputs, the same process proves their
actual profiles fit, and the universal lower bound proves their actual
call counts minimal. Every constructor proof and each optimality theorem
is included in an audited aggregate theorem. Generated Lean source and
profile-list hashes are retained in the receipt.

Separately, Python replays source `word` in both directions and compares its
length and per-factor multiplicities with the resource tree. It checks
inverse reversal/signs and the actual address footprint. These tests check
resource correspondence on 5,476 cases, not matrix products or numerical
accuracy. The tests and source pins do not constitute a Lean semantics of
Python, a proof that the Python optimizer is correct for every input, or
an all-input verification of its emitted word.

The universal result is about `Fits`; applying it to arbitrary future
software outputs still requires establishing this model correspondence.
Likewise, interpreting each counted leaf as a valid source-restoring
operation relies on the inherited operator and implementation contracts.
No hidden arithmetic/compiler or physical-interface hypothesis is
discharged by this combinatorial formalization.

## Different allocation contracts

PR822's reported 59-factor/five-array construction reuses connectors that
this model reserves. `no_reserved_59_5` proves that no `Fits 5 59 N` exists,
because `59>32`. That is a model-separation example, not a counterexample
to PR822. PR714's clean checkpoint likewise belongs to a different contract.
