# Deferred native code: exact local transport and the actual caller junction

Apache-2.0. Substantial OpenAI Codex assistance. Credit PR4929's center-free code, Cao Yifan's native/controller sources, and the retained compiler and helper lineage.

The physical wrapper construction in this package supplies a real monomial-conjugate code C_s of A=I-14 P at each FULL stage s, in the common central-line convention. Write Q for the central Gaussian, D_s for that stage's fresh rank-eight Gaussian, and R_s=D_s Q. The physical gate is

    [C_s,R_s]=0.

Different C_s need not commute each other or Q. Each C_s is supported on the central coordinate and its own fresh block; thus it commutes D_t when t differs from s. Phase-correct native normalizers, rather than the mere binary orthogonality of a route, are needed for these exact operator statements. The raw-dual backward convention uses the stated monomial Q^2 conjugation on X.

Set H(B)=diag(B,Q^-1 B Q). If B involves only earlier code stages, then [B,D_s]=0. With F_s(C)=diag(D_s,D_s)L(CQ^-1) and B_s(C)=diag(D_s,D_s)U(-QC), direct block multiplication gives

    diag(C_s,I) F_s(C_s) diag(I,C_s) H(B)
      = H(C_s B) F_s(I),
    diag(C_s^-1,I) B_s(C_s) diag(I,C_s^-1) H(B)
      = H(C_s^-1 B) B_s(I).

All newly exposed pre-Y and post-X codes are fixed nonrecursive owner/address circuits, with the explicit local bill in PHYSICAL.md. The inverse code has the explicit coefficient 13 denominator inherited from A^-1; that coefficient's allowed implementation and precision remain part of physical closure. There is no assumption that C_s commutes Q or B.

For a chronological product B_S of codes whose distinct stages comprise an already-paid IDLE D_S, the same relations give

    Q^-1 B_S Q = D_S B_S D_S^-1.

Pre-Y B_S and post-X B_S therefore install H(B_S) around that paid IDLE. This reuses its actual Gaussian work; it does not add an unpriced IDLE.

## Exact algebraic replay

`gauge.py` implements the group algebra of a semidirect product. Q, every C_s and an independent previous-code B freely generate a free group. The commuting D_s act by the automorphisms C_s -> Q^-1 C_s Q while fixing Q, other C_t and B. A canonical reduced free word and an integer D-vector represent each monomial. Thus the replay is symbolic noncommutative algebra, not a numerical matrix sample or an assumption that tensor powers preserve sums.

The checker compares every block of both displayed identities, a four-stage mixed-orientation IDLE, and controls that retain [C,Q], [B,Q] and [B,C] as nonzero. Reversed update order, the wrong backward exponent and an omitted IDLE stage are rejected. The written block argument establishes applicability to every operator representation satisfying the stated relations; the symbolic checker corroborates its transcription. This is not proof-kernel acceptance.

## Initial per-pair proof attempt (superseded below)

The retained main `research/joint-helper-lattice/CONTROLLER.json` has 18 FULL calls at stages 0,1,3,...,31,32 and 15 paidIDLEs. Its seven initial IDLEs are on pairs 1 through 7. Under the declared per-pair gauge policy, after the backward FULL at stage 2 j+1, pairj carries

    W_j=C_(2 j+1)^-1 ... C_3^-1 C_1^-1 C_0.

For j=0,...,6, the already-paid initial IDLE puts pair(j+1) in the same gauge, so the next bridge has matching gauges. At j=7, pair 7 carries W_7 while pair 8 still carries I: the source has deliberately omitted that initial IDLE. The exact chronology control records that first mismatch and its two symbolic words. Tail IDLEs and the full scalar boundary remain available resources, but the local identities do not establish their complete coded endpoint.

The recorded mismatch is a stopping control for this particular forward per-pair policy. It is not a lower bound for all caller designs. In particular, a bidirectional gauge, a whole-word factorization or a separately paid junction could change the conclusion. Likewise, a terminal Q^-1 B Q gauge cannot simply be declared a free output code or an independent Gaussian target. A complete favorable caller must bind the actual terminal outputs and its whole invoice before using the supplier compiler or claiming a new kappa.

## Open next questions

Can the 16 explicit negative-Q coded output types be admitted with their 15 matched paid IDLE types, or converted to ordinary Gaussian targets for a favorable full bill? The complete coded word below makes that question concrete. The first step is a typed completion identity on one paid-IDLE/negative-output pair; a Gaussian supplier admission and new recursive saving remain unproved.

## Independent binding of the predecessor noncommuting-stage identity

Dugongue's existing `research/frame-aware-native/noncommuting-controller/PROOF.md` already proves the universal p16 identity for freely noncommuting stages and a central Q, crediting Cinna Davis / 1337 isnot 1337 #4470 and Ryanson Jonathan #4516. The present Q=I calculation is an independent binding/control for that predecessor theorem, not a new noncommuting-controller theorem. Its README and proof were read during this investigation.

The retained controller has the following already established algebraic property. Set Q=I, replace every one of its 18 FULL-stage diagonals by a distinct freely noncommuting letter Z_s, and implement each already-paid IDLE as its chronological ordered product. Keep all 154 physical events and both actual 32-by-32 scalar boundary matrices. The resulting 32-by-32 operator matrix is exactly diagonal. Its i-th diagonal is the chronological ordered product of precisely the stages selected by the source's i-th target word.

The checker proves this finite word identity by expanding all 1,024 entries over the free associative group algebra with rational coefficients. No commutative collection of stage letters is performed. Reversing the first two-stage IDLE is a semantic mutation that fails, although a commuting specialization could miss it. A separate exact 2-by-2 matrix experiment with noncommuting integer stages was used as a discovery check; the registered result is the stronger symbolic identity.

This is directly useful for the coded caller constructed below. Under H=diag(I,Q), the modified local gauge identities turn the core into scalar L/U steps with decorated stage diagonals Z_s=C_s^epsilon D_s. The core identity therefore accommodates their noncommutativity. It removes one possible obstruction to the proposed construction. It does not remove H from the two physical scalar boundaries, implement those Q-dependent boundaries for free, or establish independent Gaussian terminal jobs. The positive complete-core identity and the unresolved physical entrance/exit interface are separate statements.

## Complete typed coded caller, superseding the local junction concern

The direct global proof avoids requiring a separate matching gauge on each pair. Define H=diag(I,Q) on every pair. For each FULL stage s, emit the nonrecursive pre-Y code C_s^epsilon, the center-free native FULL in its actual orientation, and the nonrecursive post-X code C_s^epsilon, with epsilon=+1 for forward and -1 for backward. The resulting block is

    H^-1 diag(Z_s,Z_s) L(I) H       (forward),
    H^-1 diag(Z_s,Z_s) U(-I) H      (backward),
    Z_s=C_s^epsilon D_s.

For each of the 15 actual paid IDLEs, emit its chronological code product on Y, its unchanged paid Gaussian IDLE, and the same chronological code product on X. Since each code commutes the other stages' Gaussian factors, the result is H^-1 diag(Z_word,Z_word) H. Each retained thin query similarly conjugates to its original scalar shear. Every internal ADD bridge preserves X/Y parity, so adjacent H factors cancel. No extra initial IDLE is inserted. The earlier pair 7/pair 8 mismatch therefore identifies only a limitation of the per-pair proof strategy; it does not obstruct this global construction.

The global final signed swaps are retained. The actual left boundary has pure parity rows (first 16 even, last 16 odd); the right boundary has pure parity columns (first 16 even, last 16 odd). The checker binds all 64 of these facts. Moving H through those scalar boundaries and signed swaps gives the exact 32 main operator blocks

    Q^-1 B_i D_i              for i=0,...,15,
    B_i D_i Q                for i=16,...,31.

Here D_i is the chronological product of the Gaussian stages selected by the authenticated original target, and B_i is the corresponding chronological product of C_s^epsilon. The ordered words are emitted explicitly in GAUGE.json. This proves a complete *typed coupled/coded endpoint* for 3584 independent main inputs, with all 7344 independent source helpers retained once. It is not the old Gaussian endpoint. The positive-Q half can be postdecoded by B_i^-1; the negative-Q half retains its specified code between the central operation and the remaining Gaussian product.

GAUGE.json emits every retained event and every inserted code block. There are 66 inserted code blocks, comprising 194 individual code evaluations: 34 A and 160 A^-1. Each code is conjugated by 112 known monomial field maps in each direction, giving 43,456 field-monomial passes before any positive-output decoding. One conservative implementation of a dense code computes (A-I)x, or (A-I)x/13, in 112 owned temporary fields and then adds the result to x. The exact A-I support has 5,936 entries, so this uses at most 6,048 scalar ADDs per code, or 1,173,312 ADDs for the 194 evaluations. The 112 owned temporaries can be reused chronologically; each evaluation initializes and clears them. These counts exclude the separately retained native scalar work, monomial primitive lowering, optional positive-output decoding, routing/storage accounting and fixed-precision realization of denominator 13. They are explicit additional finite costs, not an outer-admission certificate.

The recursive paid profile differs from the retained caller by precisely 144 rank-eight calls removed. Every original IDLE and thin query remains paid. The source helpers remain independent and productive once per FULL. A new numerical moment cannot count the 16 negative-Q coded outputs as the original Gaussian jobs. Their new job family, a changed compiler/completion theorem, or an actually paid endpoint adapter is the remaining integration question.

The primary finite scalar realization is the already checked eight-mode program in NORMALIZERS: 896 ADDs, 224 field-monomial passes and 16 owned-CLEAR operations per C evaluation, with 8 reusable owned temporary fields. For the complete typed caller this gives 173,824 ADDs, 43,456 field-monomial passes and 3,104 CLEARs. The dense 112-temporary implementation above is an alternative upper bound, not the primary invoice. If the positive-Q half is explicitly postdecoded to ordinary Gaussian jobs, its 16 inverse code words contain 97 additional C evaluations: 86,912 ADDs, 21,728 monomial passes and 1,552 CLEARs. GAUGE.json emits those optional output decoding words and prices them separately. The typed caller alone has 3584 coded main outputs; after that priced postdecoding 1792 of them are autonomous Gaussian jobs, while 1792 retain the exact negative-Q code. The denominator 13 fixed-precision arithmetic realization remains an explicit assumption/obligation for both recipes.
