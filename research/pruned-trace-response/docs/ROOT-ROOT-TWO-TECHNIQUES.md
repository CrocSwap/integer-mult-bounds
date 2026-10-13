# Exact pruning and rectangular-shear factorization

Two selected OpenAI source structures:

1. QuantumCircuit/PruningConstruction: reflect_action_error and reflection_filter_error make inactive action the criterion for removing a gate. We use the exact zero-action idea; approximate pruning and a norm tolerance are not admissible here. Our observable may be a nonunitary output projection, so the new exact algebraic statement below is proved independently, not cited as a direct Lean import.
2. FourierCircuit/SparseShear: rectangularShear_single, rectangularShear_add_le and rectangularShear_sum_le separate a rectangular update into rank-one source/target factors. TensorCostAlgebra tensor_exchange/power_reindex additionally motivate searching coordinate factorizations before materializing a larger circuit. We apply the rank-one response factorization to the pruning certificate and test the retained-copy factor for a possible smaller realization.

## Sufficient observable-pruning theorem

Let X be background registers and Y observed outputs over a field. A background gate has T=I+e_t u^T with u_t=0. Let Q be the exact suffix map from the state immediately after that gate to final outputs, with every retained-copy/scatter observation included at its actual time. If Qe_t=0, then Q T=Q. Thus deleting the gate preserves all observed outputs for arbitrary initial registers, including arbitrary dirty helpers. This follows by factoring Q(T-I)=(Qe_t)u^T, a rectangular rank-one response, so a multi-source gate is tested once without enumerating every pair of formal columns.

Scan the background word backwards while maintaining Q. On a zero-response gate Q remains unchanged on deletion. Induction therefore deletes every selected gate simultaneously without stale-support assumptions. This statement preserves the observations, not the entire intermediate background operator. Regenerate the literal inverse of the changed background body to restore X. Provided the body never reads Y into X, background restoration and unchanged observed outputs give the full original clean/dirty endpoint. In general fields, inverse cleanup reverses order and negates coefficients; in the actual F2 word these signs agree.

Frame legality and cost are separate. Removing events leaves a subsequence of each old nested frame chain; check retained observations, entrances, exits and the actual copy ranks explicitly. Recompute the resulting complete native profile and prefix bill. No omitted operation is declared free merely from its output response.

## Actual application

On the previous preload60 bit word the exact backward suffix census finds227 zero-response A gates. Retained-copy scatter is included before propagating through A. Deleting these gates and rebuilding cleanup passes all720 formal columns over F2 and all rational frame-chain checks. All nine retained copies still have rank8 and the complete paid profile is unchanged. This removes454 grouped instructions across body and inverse cleanup; it is not by itself a recursive-exponent gain.

The trace worker then finds moves forbidden by the original dependencies. Its new construction starts from this explicitly pruned word and checks every exchange on that word. This is the numerical interaction: unchanged scalar observations allow a different dependency graph, and the different graph allows a lower frame cost. The new output must pass the full native/global pipeline before its price is claimed.

## Second structural screen

The nine retained state rows have rank9 over F2, and their120-by9 scatter matrix also has rank9. Thus this particular factor cannot simply be compressed to eight scalar intermediates by an exact rank factorization. This is a bounded statement about this concrete matrix, not a lower bound against different decompositions, changed representations, or an entire algorithmic class. The full-rank outcome contributes no claimed kappa gain. The rank-one rectangular-response factorization above is nevertheless exercised in every pruning decision.

## Source scope

The listed OAI files were read and hashed, not recompiled. The source proofs inspire a new checked application; we do not assert that zero-action pruning, rank factorization or coordinate reindexing are globally new mathematics. The preserved all-size compiler and analytic assumptions remain explicit.
