# Four-axis certificate to lattice map and literal kernel

## Result and exact scope

Qualified written PASS for the conditional implication from the source's finite correction predicates to its all-integer bijection, literal inverse, complex-sum preservation and local error theorem, and for the actual kernel binding. No material theorem or kernel discrepancy was found on the valid constructed-table domain. One minor fixture-label clarification is recorded below.

Source: Nick Petalas [PR6574](https://github.com/CrocSwap/integer-mult-bounds/pull/6574), head `48e312ff18d5b66b0969148f615fdf5ce0f92edd`, `research/four-axis-reversible-grid/`. Exact PROOF blob `fc3baa1e271cd89acabcb40248fb5e17dfdfac59`, construction `c80d588ef9ca33494ca78b8abd737e6e8722b4c4`, kernel `883c1c317d2d4394f534e785a5d46b443549db9a` and verifier `c5057740a3fa15d8169669fdb8e984eb4e88be8f` are retained as inert text, with README/ENGINEERING/ORIGIN/SOURCES and root license/NOTICE.

The actual successful 64-row matching/certificate, table payload, 4096 class pairs, endpoint fixtures, controls and finite outcomes remain **source-owned and unreplayed**. No constructor, matching, class enumeration, scientific import, fixture, fault or kernel ran. This review does not independently establish the finite matching's existence. It audits what a successful actual certificate means, rather than treating fixtures as a proof over unbounded integers. No new codec, table, masks, numerical optimum, phase covariance, fourth-power identity or physical tariff is claimed.

## Operator and complete quotient

Index sixteen coordinates by s,t∈F₂⁴. Let H_st=(−1)^(s·t), so H²=16I and H/4 is orthogonal. Let D_jj=(−i)^popcount(j). For C=[[i,1],[1,i]], π=1+i, the stated ideal operator is

    U=π⁻⁴ C^(tensor4)=−D(H/4)D.

Indeed C's tensor entry is i^(4−popcount(s xor t))=D_ss H_st D_tt and π⁴=−4. This keeps both diagonal factors and the global minus. Since C/π is unitary and has row/column sum one, U is unitary and preserves complex sum. The local operator convention is explicit; this is not a new binding to a physical/native caller's charts.

For any z∈Z¹⁶ the table key is q=Hz mod4, componentwise canonical residues. Modulo4, a Walsh column indexed by t is the all-ones column plus the sum, over set bits j of t, of the column difference H_:,2^j−H_:,0. Each difference has order two and the all-ones column has order four. Consequently all keys have form

    q_s=A−2(s·B) mod4,  A∈Z/4Z, B∈F₂⁴.

Conversely choose z₀=A−ΣB_j and z_(2^j)=B_j, all other entries zero. Its row-zero residue is A and row-2^j residue A−2B_j, proving both existence and uniqueness of the 4·2⁴=64 keys. This is the source's algebraic coverage argument, not a new program census. It covers negative and arbitrarily large z, without inferring coverage from a finite input box.

`construction.quotient_keys` generates the complete column span modulo4. `verify.representatives` separately constructs those sparse representatives and uses `direct_walsh`, then rejects duplicate keys. `certify` requires both table domains to equal that representative key set. There is no separate source function named classify: `kernel.real_map` computes its actual key from the Walsh numerator. These associations, not the size64 assertion alone, provide complete-domain coverage.

## Actual finite predicates and both lattice inverses

Write e_q for the forward offset and f_t for the backward offset. On the constructed plain integer tuple/dictionary domain, the literal `certify` checks:

- exact complete forward/backward key domains;
- forward offset length16 and genuine integer components, with q+e_q≡0 mod4;
- He_q divisible by4;
- distinct targets p(q)=He_q/4 mod4, ultimately equal to the full key set;
- `backward[p(q)] == −He_q/4`;
- squared norm≤64 and both real/imaginary D-weighted sums zero for each forward and paired inverse offset;
- zero offsets at the zero key and maximum squared norm exactly64.

The forward map R(z)=(Hz+e_q)/4 is integral by congruence. Integrality of He_q/4 also follows algebraically from e_q≡−Hz and H²z=16z, while the explicit source check usefully verifies its implementation association. Every output key satisfies

    H R(z) mod4 = He_q/4 mod4 = p(q),

because H R(z)=4z+He_q/4. A permutation p identifies q uniquely from any target key t. With f_(p(q))=−He_q/4, define S(y)=(Hy+f_t)/4 for t=Hy mod4. It is integral for **every** y, since f_t≡−t mod4. Substitution gives S(R(z))=z.

For the other direction, fix arbitrary y and its target key t, and let q=p⁻¹(t). Then Hf_t/4=−e_q, so H S(y)=4y−e_q and its key is −e_q mod4=q. Thus R(S(y))=y. This establishes a bijection on the entire integer lattice, not merely inverse agreement on finitely generated forward images. Complete target coverage and correct target-indexed pairing are central to that inference.

`build_tables` stores `forward[keys[source]]=value` and `backward[keys[target]]=tuple(−v//4 for v in walsh(value))`. Division is exact because every v is divisible by4, including negative v. The paired inverse is indexed by the **target** key, not by the source key. The finite checker recomputes its image with the separate direct transform. Search candidate completeness or closest-vector optimality is unnecessary once these predicates hold; the actual matching's successful existence remains an unreplayed source premise.

## Literal complex phases and inverse order

Apply R and S separately to real and imaginary parts, using the same certified table pair. The complex maps are

    F(x)=−D R_C(Dx),
    G(y)=D⁻¹ S_C(−D⁻¹y).

Quarter rotations preserve Gaussian integers. Substituting these expressions and S_C R_C=R_C S_C=I proves both G F=I and F G=I. This does not assume R is odd or F's ideal square/fourth power is preserved.

`rotate((a,b),k)` multiplies a+ib by i^k. Forward `block` rotates by −popcount(j), uses the forward table on both components, then negates and rotates again by −popcount(j): exactly D→R_C→−D. The inverse path negates **before** rotating by +popcount(j), uses the backward table, then rotates by +popcount(j): exactly −D⁻¹→S_C→D⁻¹. Moving the minus through the nonlinear table map would require an extra symmetry not proved here. The linear ideal for this inverse order is U*=−D⁻¹(H/4)D⁻¹.

`real_map` applies the actual Walsh function, selects the numerator's modulo4 key, adds its offset, checks exact divisibility and divides by4. `block` returns newly constructed tuples and does not write input or table entries. Inputs and tables must remain fixed during the call; no concurrent-mutation, adversarial-object or arbitrary-hostile-table admission claim follows from this path.

## Sum, zero, error and sharpness are separate obligations

For real e, `WEIGHTS` are precisely the real and imaginary parts of D_jj. The two checked weighted sums give ΣD_jj e_j=0. Therefore the correction in F(x)−Ux=−D(e_real+i e_imag)/4 has complex sum zero. U preserves sum, hence F does too. Its bijective inverse preserves the same sum. The inverse offset checks also use D; for real offsets vanishing D-weighted sum implies vanishing conjugate-D-weighted sum, as needed by D⁻¹. Norm alone could not imply these weighted identities.

Zero is a separate table condition e₀=f₀=0. It gives F(0)=G(0)=0; injectivity or a uniform error bound alone would not establish that endpoint.

Each real correction has squared norm≤64, so its real error e/4 has squared norm≤4. The inverse error f/4 has the same bound; f=−He/4 also gives equal norms by orthogonality. Quarter rotations preserve Euclidean norm. Adding the two component squared errors yields≤8 in each complex direction, hence≤√8·h on grid h.

For x=(2+2i,0,...,0), Ux_j=−D_jj(1+i)/2. Every one of the 32 real/imaginary components is a half-integer. Every Gaussian-integer output therefore has squared distance at least32·(1/2)²=8. The adjoint has the same half-grid argument. This is the source's existing written optimality witness, not a newly run endpoint fixture or search. No claim of pointwise nearest output or optimal error for a complete caller follows. For disjoint sixteen-entry blocks the usual sum of squared bounds gives h√(N/2); no inherited three-plus-one implementation, physical speed or outer bound was replayed.

## Mathematical map versus the executable precision boundary

The proof defines a map on all Z[i]¹⁶, conditional on valid tables. The executable `validate` accepts only a list/tuple of sixteen real/imaginary pairs of genuine Python integers, each with `bit_length()≤4096`; Boolean components are excluded. `block` separately requires a genuine Boolean inverse selector. These are **entry** checks. Output components are not recapped, and that finite admitted input set need not be closed under the map or inverse. Thus this API is a restriction of the lattice bijection, not a permutation of every4096-bit register configuration.

The source's4090-bit headroom recommendation is sufficient: for component magnitude≤2^4090−1, a Walsh numerator has magnitude≤16(2^4090−1), while every offset component has magnitude≤8 from its norm bound. After exact division by4, component magnitude is≤2^4092−2. Phase swaps/negations do not increase it, so the next inverse entry is safely below4096 bits. This is a written conservative estimate, not a new optimal cap or an executed large-word test.

One source prose label merits clarification. `endpoint_checks` loops over a parameter B in(128,1024,4090) and constructs components containing `(1<<B)+j`. Their largest bit length is B+1 (already j=0 gives2^B), so the largest corresponding components have129,1025,4091 bits. Calling those fixtures “128-,1024-,4090-bit components” labels the shift parameter rather than the actual maximum bit length. The distinction does not invalidate the theorem,4096-bit admission or stated4090-bit headroom. This observation is deduced from the literal expression; no fixture was executed or outcome newly verified.

## Evidence, weakening controls and source closure

The separately sealed abstract/code notes give written **UNEXECUTED** challenges to incomplete key coverage, colliding target classes, wrong inverse indexing, lost global sign/phase order, missing weighted sums/zero constraints, fixture-only all-integer extrapolation and a false finite-register/physical transfer. Some predicates, such as He_q divisibility, follow algebraically from stronger genuine-key/congruence premises; merely removing that redundant check is not by itself a valid counterexample. No executed control or new source failure is claimed. The fixture-label precision issue is separate from the source's original ten executed controls, all unreplayed here.

Ten exact inert input objects/65198bytes retain eight foreign source texts and two canonical root license/NOTICE texts. SOURCE-PINS binds foreign commit/tree/path/blob/mode/size custody separately from canonical guidance provenance. Original source ORIGIN/SOURCES entries are contextual pins, not automatic proof that every upstream body or theorem was read. This subset omits the original TASK/VERIFY and is not registered as a runnable original suite. There is no scientific VERIFY hook or science command.

The source already supplies construction/checker routes, full class-pair fixtures, native error oracle and controls; these are not described as absent. No original/new constructor, matching, class enumeration, scientific import, endpoint, fault campaign, numerical experiment, NumPy/native operator or proof kernel ran. Hosted repository-helper CI, if present, is a separate metadata/testing receipt rather than acceptance of this conditional theorem or a source certificate replay.

The coordinator read the prior scout/source body and had informal preclaim quotient/phase reasoning. The target-known abstract role sealed before current6574 proof/code/peer reading; historical exposure is not categorically excluded. The code role had actual earlier source-scout exposure and sealed before peer reading. First drafts remain unchanged, followed by source cross-binding and exact-version assessment. AI role separation supplies inspectable arguments, not blind discovery, independent human review or proof-kernel acceptance. The original formal-interface card is retained with CHANGED written-review scope and partial outcome; its formal/kernel gate remains unmet.

## Credit and remaining obligations

Nick Petalas6574 owns the codec, matching/certificate, sharp constant, table and original finite outcomes. Credit Ali Romman6536/6534/5821 predecessor constructions/questions, David Ganz/Dugongue5815 Gaussian conventions/Smith context, Brian/JoyboyBrian5485,4743 and all retained Gaussian/native/compiler/source-NOTICE authors. Walsh orthogonality, finite-quotient algebra and matching are classical. ToikY produced this external review with substantial OpenAI Codex and separate abstract/code/metadata/byte roles; exact licenses, headers, original attribution and context pins are retained, without predecessor endorsement.

Actual caller entry/exit charts, adjoint/group order, dirty-bank ownership, physical transforms/classification/shared-table access/movement/precision/auxiliary restoration and complete invoice remain open. The additional norm-nonincreasing premise in6619 is not imposed on this codec; phase covariance, exact fourth power and source6536's full ports are not inherited. Retained-record stochastic callers and the distinct shear/predecessor error models are not recounted. All five selected assumptions, native/all-column/full supplier and outer admission remain. No κ/frontier/adoption change, merge, physical speedup or complete multiplication result follows; follow-ons are unreserved.
