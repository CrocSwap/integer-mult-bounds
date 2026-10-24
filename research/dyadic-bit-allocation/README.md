# Exact minimum-bit allocation for a fixed dyadic error budget

DONE — an exact minimum-bit allocator for a fixed dyadic error budget. Scoped algorithm and proof, with exact finite checks; no new kappa. This question is complete and no claim remains active.

The retained rounding interface gives sufficient uniform fractional-bit guards. This result supplies a concrete alternative when a caller has fixed, unequal certified error weights. It applies to a separable error bound, not automatically to a coefficient-dependent nonlinear bound.

**Contract.** Let a_i>0 and epsilon>0 be rational, and let l_i>=0 be integer minimum precisions. The caller has proved

```text
error <= sum_i a_i 2^(-p_i),    p_i >= l_i,    p_i integer.
```

The a_i must remain valid independently of the chosen p_i. Every extra fractional bit has the same unit cost. Start at p_i=l_i. While the sum is above epsilon, choose a largest current contribution a_i 2^(-p_i) and increase that p_i by one. Ties may be broken arbitrarily.

**Result.** This algorithm minimizes sum_i(p_i-l_i). In fact, after every fixed number K of increments it has the smallest possible residual sum among all legal allocations with K increments. A rational max-heap implements K increments with O((n+K) log(n+1)) heap comparisons and arithmetic operations. This is an arithmetic-operation count, not a bit-complexity or tape-cost claim.

**Proof.** The successive reductions available from coordinate i are

```text
a_i 2^(-l_i-1), a_i 2^(-l_i-2), a_i 2^(-l_i-3), ... .
```

Each list decreases. Any legal K-bit allocation selects a prefix of each list and K reductions in total. The K largest reductions in the union can be selected with this prefix property: selecting an item requires only earlier, larger items in its own list. The greedy algorithm merges these decreasing lists and selects exactly such a set. Its total reduction is therefore maximal for every K. Since the residual at K-1 still exceeds epsilon when the algorithm stops at K, no smaller allocation is feasible. Termination follows because a sufficiently large common precision makes the finite sum smaller than epsilon.

**Exact fixture.** For weights (256,1,1,1), zero lower bounds and tolerance 1/8, the algorithm returns (13,5,5,5): 28 total bits, with residual exactly 1/8. A common precision requires 12 bits per term, hence 48 total bits; 11 bits fails. Thus an admissible unequal allocation saves 20 bits in this declared model. It is not a measured production-memory saving.

**Boundary.** Different costs per bit require a different algorithm. Even choosing the largest reduction/cost ratio can fail: initial contributions (8,7), costs (3,2), and target residual 11. Ratio-greedy first pays 2 to reduce 7 to 7/2, but residual 23/2 still fails. It next pays 3, for total cost 5. Paying only 3 to halve the first contribution reaches residual 11. The equal-price assumption cannot be dropped. Coupled errors, allocation-dependent weights, or a maximum-word-width objective are also different problems.

**Evidence.** Both warning-strict normal and optimized CPython 3.12.14 runs pass 480 instances and 13,565 exhaustive allocations, comparing the heap result with every composition of the same total bit count. The checker also rules out every allocation with one fewer bit, checks the 28-versus-48 fixture, rejects five invalid input classes, and checks the unequal-cost counterexample. It uses only the standard library and contains no assertions that disappear under optimization.

Base: canonical main ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority revision 7. Live PR/Discussion and pinned precision-note searches found no exact allocator for this contract. Adjacent global precision-guard and completed-downset results retain their separate scopes. This is a numerical-interface side result under `uniform-transfer-audit`, not a complete PR4100 caller audit.

**Sources, limits and next step.** Credit ywz65's [PR #2701](https://github.com/CrocSwap/integer-mult-bounds/pull/2701) and its [pinned noise contract](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/simultaneous-gate-rounding/README.md), Vlado Vojdanovski's [PR #1673](https://github.com/CrocSwap/integer-mult-bounds/pull/1673), and Nick Petalas's separate [PR #5153](https://github.com/CrocSwap/integer-mult-bounds/pull/5153) endpoint refinement. The greedy argument is a classical separable diminishing-return allocation method; the contribution is this exact, executable dyadic precision contract and its boundary controls, not a new general greedy theorem.

For a concrete application, freeze one emitted circuit, derive precision-independent suffix/error weights, and state the real cost per added bit. That source binding, coefficient production, integer range, physical movement, reversibility and the complete supplier/outer bill remain open. No predecessor scientific replay, native/selected replay, Lean or Docker build was run. Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0. No independent human or proof-kernel acceptance is claimed.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/dyadic-bit-allocation
```

Use Python 3.12 with the standard library. The normal and optimized commands must print `PASS_DYADIC_BIT_ALLOCATION`. The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The checker has no external runtime inputs.

## Open next questions

Bind fixed error weights and real bit prices to one emitted circuit. The source binding and physical cost model are not supplied by this package. See `TASK.json` for the structured scope.
