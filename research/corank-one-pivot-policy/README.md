# Three pivot swaps suffice for every corank-one projector

This contribution was produced by Nick Petalas. Apache-2.0.

For every field and every m>=4, the optimal worst-case paid pivot-swap count
for rank-(m-1) projectors is exactly

    s*(m,m-1) = 3.

This is a scoped written proof with exact finite corroboration. It answers
Open next question 1 of [PR4245](https://github.com/CrocSwap/integer-mult-bounds/pull/4245),
which established finite cases and left the uniform statement open. The new
policy uses at most three swaps on every input. The explicit family
`P=I-u v^T`, with `u=(1,1,1,0,...)` and `v=(1,1,-1,0,...)`, requires three
over every field. The proof includes characteristic two.

[PROOF.md](PROOF.md) retains the prescribed pivot stages, both swap directions
and every clearing ADD. It also explains the residue-field itinerary
corollary for the split odd-prime-power-ring fallback of
[PR4235](https://github.com/CrocSwap/integer-mult-bounds/pull/4235).
Those compiler, weighted-adapter and restoration results are cited premises,
not audit deliverables. No predecessor code, census or verifier is imported
or replayed. This package changes the pivot policy.

The construction bridges all bad principal minors with one column
transposition when the last coordinate product is nonzero. Otherwise one
simultaneous row/column transposition first makes it nonzero. The latter is
performed at a legal pivot stage and costs two, giving the total of three.
After recovering the rank-one defect in O(m^2) field operations, the plan
uses O(m) field operations. Pointwise minimum cost is not claimed.

## Evidence and reproduction

From the repository root with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/corank-one-pivot-policy/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/corank-one-pivot-policy/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/corank-one-pivot-policy
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/corank-one-pivot-policy --check-source-history
```

Another CPython 3.12 path may replace the local executable. The direct
read-only verifier also runs from a Git-free package export. It prints
generated JSON with `PASS_CORANK_ONE_PIVOT_POLICY` and hashes all seven
package files. Nothing generated is retained in the checkout.

The new policy is executed on every rank-one-defect projector in seven
complete domains: F2 at m=2,...,7 and F3 at m=5, totaling 20,595 inputs.
Two literal elimination implementations check the equal-head convention
and the original reversed-tail convention on every input. These are checks
of the new policy, not optimal-policy replays of the predecessor census.
An iterative search excludes every legal plan costing at most two for 36
members of the sharp family, over F2,F3,F5,F7 at m=4,...,12. It visits 576
states. Another 72 fixtures exercise m=8,17,32,64 over six prime fields.
Nine rejection controls and three explicit semantic comparisons pass.
The universal quantifiers rest on the written proof, not these enumerations.

## Scope and credit

The executable API accepts rank-one defect vectors in dimensions 2 through
64 over primes at most 31. It validates their field entries and `v^T u=1`.
The proof covers every field and all m>=4. Source metadata pins the
predecessor READMEs, catalogue and selected record as historical provenance
at canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
There are no live external inputs. [TASK.json](TASK.json) records the scope
change from the G20 helper card to this fallback side theorem.

Credit Nick Petalas / PR4245 for the uniform question and finite boundary,
and PR4235 for the paid fallback. Cinna Davis / PR4100 supplies the block
identity; source527 and commdata2338 supply the normalizer lineage; Jose
Manuel and Ross Richardson retain the recursive closure and orientation
context. The determinant lemma and Gaussian elimination are classical.
Global literature priority is unclaimed. Frozen credit lines are unchanged.

Corank one at m=64 has rank 63, outside the retained paid boundary r<=42.
No improvement to that boundary's worst packet, new kappa, supplier admission
or complete multiplication theorem is claimed. Higher corank, physical
coefficient preparation and routing, dirty restoration installation, stock,
precision, tape and outer costs remain open. No selected cold replay, Lean
or Docker run was performed. Independent human and formal proof-kernel
review are unclaimed.

## Implementation constraints

The policy and checker have no recursion, subprocesses, network or write
path. Functions fit within 60 physical lines. Loops are bounded by validated
dimension/field sizes or literal fixture domains. Exact checks use explicit
exceptions and survive optimized Python. Both registered commands make
warnings errors and have a 120-second timeout.
Warning-strict execution and an AST function-size inspection are the available
local diagnostics; an external Python linter was unavailable.

Python allocation is a Power of Ten rule 3 deviation. The public policy
caps m at 64 and q at 31; the largest complete domain has 9,801 inputs,
processed one at a time. The two-swap search caps its frontier at 100,000
states and uses m<=12. Receipt files are capped at 128 KiB each. These
bounds constrain managed allocation; allocator internals and fixed-storage
execution are not claimed. A larger input API must replace these budgets.

## Open next questions

1. Can higher-corank residuals admit a constructive bound of 2(m-r)+2
   swaps? This would address the retained boundary. Start with a rank-two
   defect and a minor-preserving replacement for the single mismatch
   interval. Its mixed minors are no longer classified by these identities.
2. Can an actual corank-one physical packet use the policy profitably?
   Bind its coefficient extraction, full-ring clearing, weighted swaps,
   tape routes and dirty restoration. No selected corank-one paid packet
   or complete physical invoice is supplied here.
