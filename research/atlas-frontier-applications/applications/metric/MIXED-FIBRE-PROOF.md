# Mixed cover/fibre magnitude bound for the actual controller

Status: sufficient mathematical proof with a completed current-source finite certificate. This is a separate branch from the checked 2048-bit release. A payload of 256 bits is a proposed consequence for the magnitude reserve only; no new kappa or complete 256-bit admission is claimed here.

`CURRENT-RESULT.json` records the current native and T372 ownership checks: both fresh five-stage chains, exact arbitrary-dirty endpoints, every static owner chart, and thirteen negative controls. Authenticated source bytes are executed directly; a timestamp-valid stale-bytecode control is rejected. This is informal mathematics and exact finite computation, with no new Lean claim.

## 1. The domain is a role indexed by a cover element, carrying an address function

Write Gamma for the finite orthogonal cover group, and use g in Gamma for its index. This is not the selected-bit address. A wire of the expanded finite network is indexed by a physical family a and a cover label g. Its value is a function

    f_(a,g): X -> C,       X = (F_2^73)^k,

where k is the positive number of selected-bit columns. Unselected address bits, polynomial coefficient indices, outer prefixes and suffixes may be held fixed; every estimate below is uniform in them.

This distinction is present in the pinned primary preprint. `03-motifs.tex`, lines 544–566, defines a wire's array on the selected-bit space and takes tensor products over columns. `05-layers.tex`, lines 47–49, explicitly fixes the unselected bits. Lines 86–139 put frame changes into invertible selected-address maps. Lines 141–154 give the exact recursive C contract, including arbitrary dirty roles. Lines 563–590 split preceding rows into wire roles while preserving the remaining complete selected-bit fields. The manifest in `primary/PINS.json` binds these files to the original openai/math commit `adc7f1241b42e322a6451854ab7e4b4c146bf78a`.

The actual hosted controller then replaces an abstract wire by `(family, g sigma)`, for a fixed orthogonal matrix sigma specified by the literal owner descriptor. Its `route_semantics` says this explicitly. In `emit_allcold.py`, lines 69–84, sigma is computed only from the fixed port, pending child, offset, width and spectator list. No input address x is read. The independent controller audit recomputes the same actual 73-column matrices; its source and exported matrices are separately hash-bound. Therefore g -> g sigma is a bijection independent of x. For active data, source and target have the identical route `[1, stage, port]`.

A wire stream already has both indices. The cover labels are additional finite wire roles; they are not Fourier coordinates of X. The size of Gamma enters the operation/role invoice, but need not enter a supremum over these roles.

## 2. The stronger norm and the precise closure property

For one physical family put

    N_a(f) = max_(g in Gamma) ||f_(a,g)||_(l2(X)).

A fibre-monomial unitary has the form

    (Tf)_(a,g) = U_(a,g) f_(a,pi(g)),

where pi is a permutation of Gamma and every U_(a,g) is unitary on X. Such a map preserves N_a: each output fibre has the norm of its input fibre and pi visits every input once. A contraction in place of each U gives an inequality in the same direction. The U may depend arbitrarily on g. No representation-theoretic sparsity assumption is imposed on f.

The statement is stronger than ordinary unitarity on l2(Gamma x X). A unitary that averages different cover fibres can enlarge this mixed norm. For example C=((1+i)I+(1-i)X)/2 on two cover labels maps the scalar fibre vector (1,i) to (1+i,0): its mixed maximum grows from 1 to sqrt(2). Such a cover transform is not an allowed primitive. Thus generic helper unitarity alone would not prove this argument.

Every native operation must instead have its actual selected-address or static-chart meaning. That verification is essential; the norm is not licensed by a name such as 'warp'.

## 3. Primitive audit, including dense maps and resets

1. **Static owner charts.** Every actual descriptor is a finite list of integers fixed before evaluation. Its matrix sigma acts on the cover index by right multiplication and is independent of x. Orthogonality implies invertibility, so this is a permutation of Gamma. Reindexing g preserves N_a. Data source and target routes coincide portwise.

2. **Monomial native recipes.** The actual Clifford recipes have a 9-by-9 invertible binary `matrix_rows` block, an address offset, and root-of-unity phase data. They act on the native selected-bit address, embedded into 73 selected coordinates by g sigma, with spectators unchanged. For every fixed g this is a permutation of X times a diagonal phase of modulus one. They do not transform the cover index. Rank-zero warps, endpoint adapters and residual spectators use these literal recipes; the fresh all-512-column phase checks bind them to the current native program.

3. **Dense C_U and child cores.** The primary definition is C_U = H diag(i^(q_U)) H, where H is the normalized tensor Hadamard on the selected-bit fibre. H and the diagonal are unitary, hence so is C_U. A normalized rank-r child is, equivalently, a normalized Hadamard core on r selected directions with the exact monomial wrappers. Both descriptions operate inside the same X at fixed g. Taking k tensor columns preserves unitarity. An inverse uses the audited phase/sign wrappers and is also unitary. Dense averaging of selected-bit values is therefore allowed; averaging cover labels is not.

4. **Scalar copy, clear, scale, add and Horner work.** At a local cover value g, a scalar instruction only combines the explicitly mapped logical roles `(a_i, g sigma_i)`, with the same selected address. If input role i has fibre norm at most e_i, then copy gives e_target <= e_source, clear gives zero, scaling by q gives |q| e_target, and add gives e_target + |q| e_source. These hold uniformly over g, even though the source roles use different static sigma_i. The exact Horner integer-multiplication envelope uses successive doublings and additions of this same bound. This is exactly the mathematical recurrence implemented by `invoice_allcold.py`, lines 63–163: it ignores only fibre-unitary child/adapter/phase/warp events and pays all scalar coefficient work.

5. **Private centres and zero buffers.** Literal replay checks an explicit first clear before every centre read/copy, terminal zero, and allocation/free discipline for every zero buffer. No arbitrary private input can enter. Private coefficient work has the retained clear-before/after Horner contract. Shared private streams are reset before another cover value or invocation can observe them. Their intermediate values are bounded by the local scalar/Horner envelope, not assumed zero throughout.

6. **Whole cover sweeps and partial sweeps.** Within a call the 632 logical live roles occupy distinct families. For each such family, g -> g sigma_i is bijective. Therefore distinct g invocations touch disjoint live fibres. Private work is reset between them. A complete normalized helper endpoint is consequently a fibrewise unitary in each physical family, not a unitary that couples different cover labels. The exact zero dirty-helper response in both data orientations is separately replayed. During a partial sweep, processed and unprocessed fibres are selected subsets of their corresponding before/after values; a maximum over cover labels is bounded by their maximum. We retain the existing extra partial-sweep bit conservatively.

7. **Idle remainders, bridges and terminal corrections.** Idle children are selected-bit unitary kernels at each g. Bridges are signed, unit-coefficient copies between the two specified streams within a replica, at aligned chart addresses. Terminal exchanges are signed stream permutations. Data phase masks and final translations are modulus-one phases or selected-address translations depending on g. Each operation is fibrewise or cover-monomial. None is a normalized Fourier transform on Gamma.

8. **Packed physical resampling.** The ideal address map is an invertible transformation of selected bits, with unselected bits unchanged at its interface. The packed implementation may swap chunks and temporarily hold XOR combinations of their encoding bits, but no coefficient arithmetic uses those temporary strings. The primary source at `05-layers.tex`, lines 813–818, states this interface boundary. The macro returns an exact permutation before coefficient arithmetic resumes. Fixed-width bit manipulation does not require a coefficient norm interpretation at every temporary tape state.

9. **Recursive realization.** The completed child has the exact C tensor contract on its own active selected directions and identity on spectators. This is fibrewise on the parent's full X, so the mixed norm is compatible when a smaller selected subset is recursed on. No contraction assumption is made about an unfinished recursive evaluation. Its internal values retain the existing arithmetic-chain/denominator guard; the improved starting magnitude multiplies the same local recurrence. The manuscript evaluates the C recursion exactly before its prescribed completed-layer truncation, rather than silently inserting uncharged roundings into it.

10. **Masks, truncation and errors.** Root-of-unity masks preserve fibre norm. The final H_0 conversion is the stated normalized butterfly contraction; truncating each complex coefficient on the dyadic grid gives the same uniform pointwise error bound over all a,g,x. The bound also applies to differences of two inputs, since all pre-truncation operations are linear. Thus an input error bounded pointwise by delta has fibre norm at most sqrt(|X|) delta, uniformly in g, and obeys the same propagation estimate. There is no factor sqrt(|Gamma|) in that statement. Any later summing or exact-recovery bound must keep its existing independent charges; no recovery tolerance is relaxed here.

## 4. Exact source recipe bound in the mixed norm

For stream j, group its 112 physical families and put

    z_j = (sum_(port=0)^111 N_(j,port)^2)^(1/2).

Taking a maximum separately for each port is important: port-dependent right translations of g need not preserve a maximum taken after summing all ports at the same g. The above order does preserve every family-local fibre-monomial unitary. A completed data shear satisfies the componentwise norm inequalities used in `PROOF.md`; the triangle inequality first bounds each port, and the Euclidean triangle inequality combines the 112 ports.

The exact same source-derived nonnegative matrix P and integer Schur weights therefore give

    ||z(prefix)||_2 <= 10 ||z(input)||_2 < 16 ||z(input)||_2.

Other replicas' calls contribute only fibrewise helper endpoints in this replica, so they preserve these z_j. Arbitrary interleaving and correlations are permitted. Native private reset and exact data endpoint premises are indispensable.

If the input coefficients have modulus at most M, then |X| = 2^(73 k) and

    ||z(input)||_2 <= sqrt(896) 2^(73 k/2) M.

For every k >= 1, sqrt(896) < 2^5 <= 2^(5 k), and 2^(73 k/2) <= 2^(37 k). The whole completed-boundary amplification is below 2^((5+37+4) k) M. No initial support, low-dimensional representation, or cancellation between different cover labels is assumed.

## 5. Proposed finite magnitude reserve and preserved denominator accounting

The fresh current native receipts still give 63 forward and 70 backward scalar/Horner bits. With the same partial-cover and arithmetic margins, the actual sufficient per-column magnitude allowance becomes

    70 + 37 + 4 + 5 + 1 + 4 = 121.

Keeping the local reserve of 128 gives

    128 + 37 + 4 + 5 + 1 + 4 = 179 < 256.

This is a proposed replacement for the magnitude part of the previous 2048-bit payload. It does not prove a smaller denominator depth. The primary layer argument separately pays denominators by arithmetic dependency depth; the finite invoice separately retains every scalar/coefficient operation, child rank, primitive bound, total mass, the inequality 32*m*mass^2 < C0, and its existing C0 bound. Those must remain unchanged. Norm estimates do not make division consume fewer fractional bits.

Before a 256-bit release, the owning assembly must verify that its `charged_prefix_bits`/`row_prefix_extra` substitution is only the magnitude reserve and does not remove any of those separate denominator and precision charges. The existing field `global_prefix_bits` is derived from the local norm/Horner envelope; the independent `precision` and `required_C0_bits` terms do not depend on payload. This separation supports the substitution but is not a substitute for a fresh complete admission. The row, logical work, precision, tape, ordinary bootstrap and exact moment tests must all rerun. A smaller row reserve alone does not improve the paid moment root; a superior kappa still needs an actual stronger supplier or literal allocation.

## 6. Attribution and verification boundary

The mixed supremum/direct-sum estimate and weighted Schur test are elementary classical norm arguments, not new tensor identities. The finite witness uses Pure Mathematics Atlas D031–D040. The source domain comes from the pinned original preprint's complex phase-frame and simultaneous-layer definitions. Actual native/owner contracts and notices are credited to the original integer-mult-bounds construction, the PR 2802/T114 lineage, and the PR 2833 dirt-entry rewrite and PR 2839/2848 derivatives. Their source files remain unchanged.

The full-register unitarity premise of the earlier block proof is deliberately strengthened to the actual fibre-monomial primitive classification; the two-cover-coordinate counterexample explains why this extra source work matters. Current native phase receipts are fresh and separately hash-bound. This text claims the stated sufficient magnitude bound under the retained exact primitive interfaces, not an unconditional integer multiplication theorem or a completed 256-bit frontier release.
