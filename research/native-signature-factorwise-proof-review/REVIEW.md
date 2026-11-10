# External audit: exact native signatures and the factorwise caller boundary

Source: thu-nmrc PR6716 outer head `4a40713f10d47da5894d7673eb6d0ab2ebdf0687`, `research/p104-native-semantic-review/evidence/PROOF.md`, sections "Exact signed operator signature", helper normalization in "Delivered current recipes", and "Scalar word and every positive tensor width". The source separately pins the actual retained current native word/compiler to `17c08db090004c1fb54220a6d8463a5095789fa9`, and the selected reference to canonical `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. These are three different provenance roles. Reading the prose is not verification of its compiler/container custody.

**Verdict: no gap found in these conditional algebraic implications.** This written review proves the exact signature criterion constructively and expands the eventwise all-width argument. It does not check a single actual emitted recipe, inventory entry, scalar endpoint row, price or physical event. Source counts 3,184/39/512/800/18,577 remain predecessor assertions here. This is external source-aware AI review, not scientific adoption, a proof-assistant result or discharge of a selected framework assumption.

## 1. A signed signature and exact nonzero column determine the operator

Fix n>=1, V=(C^2) tensor n, with computational basis e_x for x in F2^n. Define Z_j e_x=(-1)^(x_j)e_x and X_j e_x=e_(x+e_j). Let U,W be invertible operators. Suppose their **actual matrix conjugations** agree on each X_j and Z_j, with the full complex phase included. In the source these operators are unitary Clifford words; invertibility alone suffices for this implication.

Put A=W^(-1)U. Conjugation equality implies A X_j=X_j A and A Z_j=Z_j A. To see the commutant without relying on a group-name assertion, write a_(x,y) for a matrix entry of A. Commutation with Z_j gives

    [(-1)^(x_j)-(-1)^(y_j)] a_(x,y)=0.

Over C, a nonzero entry therefore requires x_j=y_j for every j, hence x=y. So A is diagonal, say A e_x=d_x e_x. Commutation with X_j then gives d_(x+e_j)=d_x. Single-bit flips connect every basis label, so all d_x equal one scalar lambda. Invertibility makes lambda nonzero. Thus U=lambda W.

If in addition U e_0=W e_0 as **complete exact complex vectors**, then (lambda-1)W e_0=0. Since W is invertible, W e_0 is nonzero; hence lambda=1 and U=W. Comparing one arbitrarily chosen nonzero component would suffice mathematically, but the source requires the complete vector. A vector norm, support, absolute values or phase-free ray cannot replace that equality.

The Clifford hypothesis lets the eighteen generator images at n=9 have compact signed-Pauli encodings. The proof requires those encodings to denote the same actual complex matrices under one shared multiplication/order/phase convention. Unsigned binary tableau labels, frame names, task types, matching hashes or a claimed norm are not substitutes. Verifying that the current compiler actually emits operators with these signatures is a separate premise, which source check_signatures claims to check. We have not inspected or run it.

## 2. Canonical dyadic vector data and price are separate issues

Suppose a nonzero vector has coordinates (a_k+i b_k)/2^d, with integer arrays a,b and integer d>=0. Let h be the minimum of d and the common power of two dividing every nonzero integer component. Divide all integer components by 2^h and replace d by d-h. This is finite because the vector is nonzero.

The result either has d=0 or has at least one odd component. If two such reduced representations denote the same vector and d'>d, every numerator in the second representation equals the corresponding first numerator times 2^(d'-d). They are all even while d'>0, contradicting reduction. The denominators therefore agree, and so do all integer components. This proves uniqueness. Capping reduction by d is necessary to retain the declared nonnegative denominator exponent. A unit-norm check is the exact integer equality sum_k(a_k^2+b_k^2)=4^d; it excludes the zero vector but does not fix global phase by itself.

This argument validates the representation rule stated in PROOF. It does not establish that an implementation's parser/canonicalizer enforces it, that its tuples were recomputed from emitted gates, or that a receipt hash authenticates the entire dependency closure. Those require code/source/replay evidence outside this review. Similarly, equality of operators alone does not establish equal paid rank, price, legal chronological use or a correct current implementation. The source's same-rank and all-current-emitted-recipe guards are necessary separate claims; the 3,145 matching task count is not a replacement for them.

## 3. Ordered helper normalization on arbitrary inputs

Read matrices as acting on column vectors, rightmost first. If an actual complete helper recipe obeys

    U = L G_r R,

where L,R are invertible ordinary signed monomial factors, then applying R^(-1) BEFORE the invocation and L^(-1) AFTER it gives

    L^(-1) U R^(-1) = G_r.

Both inverses and their side matter. This is equality of full operators, so it holds for every arbitrary helper input y, not only a zero register, a selected column or an observed correlated output. For any spectator space E, tensoring this equality with I_E proves the same result for all vectors in V tensor E, including vectors not expressible as one pure tensor.

For every positive integer f, the factorwise ABI gives

    (L^(-1)) tensor f * U tensor f * (R^(-1)) tensor f
      = (L^(-1) U R^(-1)) tensor f = G_r tensor f.

No commuting of L,R or erasure of their central phases was used. This conditional identity establishes neither a physical implementation of the ordinary normalizers nor their full resource bill. The source's five reported dense helper checks are not rerun here.

## 4. An explicit invariant for every positive column width

Fix any finite chronological word satisfying the following hypotheses.

1. Every active field has a named invertible one-column frame T_c. The intended frame at width f>=1 is literally T_c[f]=T_c tensor f. Actual MOVE/adapter templates have their prescribed exact one-column operator identities, including global phases, and the width-f ABI applies those templates factorwise in the same order.
2. Each ADD uses one common current chart for its participating active fields. Its rational coefficient and every SCALE coefficient act as **exterior scalars** at width f. They are not folded into the one-column operator and tensorized. The checked scalar word uses the same operands, aliases, signs and chronological order as the actual word.
3. INIT, COPY, release/CLEAR and allowed field accesses obey their checked symbolic and owned-field contracts. Release does not supply a free physical erasure theorem; the retained erasure premise and its bill are still required. The eventual scalar exit rows and desired endpoint declarations have actually been checked.

These hypotheses are caller obligations, not consequences of a reported event count. For every public input field j initially in chart a_j, define

    z_j = T_(a_j)[f]^(-1) x_j.

Invertibility makes these arbitrary input arrays in bijection with the original x_j. The x_j and z_j need not be pure tensors. At every active field r maintain

    payload_r = T_(c_r)[f] * sum_j s_(r,j) z_j,          (I)

where s_(r,j) is the scalar interpreter's exact rational row. Extra independent helper/public sources are included as distinct j when their declared interface introduces them; none is identified with an observed output of another job. The initial source rows and zero INIT fields satisfy (I).

For a MOVE from chart a to b, the exact one-column map is T_b T_a^(-1). Multiplicativity of tensor powers and the inverse identity give

    (T_b T_a^(-1)) tensor f = T_b[f] T_a[f]^(-1).

It therefore changes only the chart in (I), preserving the scalar row. The same argument applies to a composite adapter when its exact individual identity and factorwise ABI are premises. A common-chart ADD with coefficient q combines two fields as

    T_c[f] v + q T_c[f] w = T_c[f](v+q w),

so it performs exactly the corresponding rational row operation. SCALE is the same exterior-linearity step. A legal ideal COPY duplicates the appropriate logical row into the contractually owned destination; its initialization, authorization, eventual cleanup and paid status remain part of the inherited ownership contract. The selected review implements COPY as ADD into owned zero and explicitly propagates approximate residuals as an ADD. This exact-algebra invariant does not erase those residuals or validate an actual current implementation/error bound. A permitted CLEAR/release retires an owned field under that contract and its specified symbolic transition. The invariant continues on the remaining active fields. None of these statements gives a released physical cell zero cost or makes an owned copy productive.

Induction over the finite chronological word proves (I) at every exit. An exit field o in chart b_o thus has exactly

    sum_j s_(o,j) T_(b_o)[f] T_(a_j)[f]^(-1) x_j.

A separately checked scalar row plus its declared endpoint binding gives the prescribed endpoint. Counting 800 rows or knowing a word has 18,577 events does not establish those row identities. We do not re-check either here.

The reasoning works for an arbitrary f fixed at the start and does not use a bound on f. It therefore proves the implication for every integer f>=1 under the same factorwise ABI. Replacing all operators by their tensor products with an identity on any spectator space preserves each event equality. This covers arbitrary correlations by linearity; no product-state input or statistical independence assumption is introduced. The independence of source labels is the caller's freedom to choose arbitrary input arrays, not a probability-law assumption.

## 5. Central phase versus exterior coefficient

If a one-column frame or template has central factor i^a, then its actual tensor power has central factor i^(a f). Retaining the exact one-column operator retains that factor automatically. Discarding the phase before tensoring changes the width-f operator in general.

An exterior scalar coefficient q in a row operation remains q at every width. The rule q*(T tensor f) is not (q*T) tensor f: the latter has q^f instead. A phase-complete one-column signature still does not determine whether a coefficient is encoded inside a factorwise frame/template or outside it as a scalar-row operation. Thus the stated width-f ABI is an additional premise, not something signature uniqueness proves. INDEPENDENT-REVIEW gives the concrete U=iI helper: normalizing by an exterior -i once instead of the factorwise (-i)^f fails already at f=2.

The invariant applies tensor functoriality only to individual operator products, inverses and equalities. It never applies the nonlinear map A -> A tensor f to a width-one sum identity. This is the precise boundary that prevents accidental scalar cancellations from becoming an all-width claim.

## 6. Written controls against weaker premises

All controls below are hand matrix/algebra calculations, not executed numerical tests, and are not counterexamples to the source's stronger stated hypotheses. Embed the first-qubit examples into n=9 with identity factors if desired.

- **Omit generator signs:** I and Z have the same unsigned Pauli generator labels and the same exact zero column e_0. But Z X Z^(-1)=-X, so their signed X images differ and the operators differ. Exact zero-column data does not repair an unsigned tableau.
- **Omit exact absolute column phase:** I and iI have identical full signed generator images and unit-norm zero columns. The columns are e_0 and i e_0; the operators differ. Norms, magnitudes and supports cannot replace the exact column.
- **Normalize on the wrong sides:** let S=diag(1,i), X=[[0,1],[1,0]], K=((1+i)/2)[[1,1],[1,-1]], L=S,R=X,U=S K X. The Gaussian-dyadic Clifford K is a phase-adjusted Hadamard. The correct S^(-1) U X equals K. The reversed X U S^(-1) equals ((1+i)/2)[[-i,1],[1,-i]], whose zero column differs from K's. Ordinary monomial factors do not commute through a Gaussian invocation.
- **Tensorize a cancelled sum:** I+(-I)=0 at width one. At width two, I tensor I + (-I) tensor (-I)=2(I tensor I), whereas 0 tensor 0=0. Both summands are phase-complete Clifford operators. Width-one scalar endpoint coincidences alone do not lift.
- **Tensorize an exterior coefficient:** exterior SCALE2 at width two sends any payload to twice itself. Tensoring the one-column operator2I would multiply by4 instead. Thus a correct width-one scalar test does not establish the required ABI if coefficients are folded into tensor factors.
- **Drop the common-chart condition:** in a one-qubit field, x=e_0 in chart I and y=K e_0 in chart K, with K=((1+i)/2)[[1,1],[1,-1]], have formal source coordinates e_0,e_0. Physical addition x+y is not I*(e_0+e_0)=2e_0 because its second component is nonzero. A scalar row addition needs matching charts or an explicitly checked conversion. This is an omitted-premise control, not a claim about any source event.

## 7. Selected-review comparison and remaining obligations

The exact canonical selected review uses the same whole-helper/common-chart/exterior-coefficient factorwise method, with source-specific finite coverage. It does not state the compact signature/canonicalization criterion as its admission rule; the classical uniqueness proof here is supplied separately. Its seven new dense tasks, own absolute-phase checks,799 scalar rows and ownership/allocation audits are not evidence for the current3184tasks/800rows. The selected source's COPY-as-ADD residual requirement remains explicit above. Same proof method is not transfer of source-specific coverage.

## 8. Remaining actual-source obligations and credit

This review reads eight exact inert companion texts plus the exact selected-review text and no scientific .py engine. It has not independently authenticated nested compiler containers, checked gate unitarity/phase encodings, compared selected/current signatures, reconstructed actual current outputs, checked paid B-block ranks, replayed 39 full matrices or five helper normalizations, checked scalar/owned chronology, or bound current caller contacts and invoices. A full source adoption needs those actual premises. All-size production/layout/stock/routing/precision/erasure/compiler/analytic/outer contracts and all five selected framework assumptions remain explicit. There is no new cost, rank, exponent or frontier claim.

The signature, helper normalization and common-chart argument remain predecessor work stated by thu-nmrc's PR6716 native companion. DreamingOfClouds/PR6030 repair and PR6702 supply the retained reference/current lineage; Matarener the independent scalar/inventory machinery; Clear1nsight the dense Gaussian-dyadic semantics; Charles Bethin and the Clifford compiler lineage; Ali Romman the current prefix evaluator and prior caller lineage; unpaidmoon/PR5837 the scalar common-chart and exterior-coefficient audit; Mark/Matarener/PR5442,5445,5974 the lifting/record/native-certificate lineage; DLamdata/PR5894 the phase/coverage context; and the retained Clifford engine contributors including Dugongue and icekylinx. The elementary Pauli commutant, canonical rational representation, ordered matrix algebra and tensor/linearity arguments are classical. ToikY with substantial OpenAI Codex assistance and separate source-aware AI proof/adversarial roles supplies this external written audit. Apache-2.0. No human or proof-kernel acceptance is claimed.
