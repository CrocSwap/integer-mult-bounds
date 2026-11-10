# Proof note: a surplus bound, a hub rank law, and a form-capacity lemma for the P104 word

Every claim below carries one of: **[C]** exact computation reproduced by `check.py` (a PASS line per claim), **[P]** hand proof, re-derived and confirmed independently, **[P+C]** both, **CONDITIONAL** (stated, not proved or not checkable here). No kappa claim and no new word are made. Labels follow one rule: a verifier or package restriction is never called a law.

Label vocabulary: **SPEC** = a premise of the outer framework or a statement in the paper; **package convention** = a choice of the existing construction that another legal object could replace; **verifier behaviour** = what the shipped checkers enforce; **derived** = follows from the others; **family assumption** = a hypothesis of this note only.

## 1. Setting and notation

A LOCAL call acts on v ports (v = 104). Each port path contains L native moves (L = 18) and each LOCAL owns mass c (c = 56). A "Q-odd unit" is a unit that separates the two real characters Q = +1 and Q = -1 of the shear variable. S denotes the rank-mass surplus: the sum of rank times count over productive targets minus the same sum over paid calls. At the selected record (conditional kappa 0.003125804, 13,444 productive fields, 66,834 paid calls) S = 760 [C: the surplus is recomputed from the record's profile; the shipped pricer asserts the same value at `research/p104-helper470-twin-rung-removal/pricing.py:75`], and 760 = v(L-1) - Lc = 104*17 - 18*56 [C].

## 2. Ratio lemma

**Lemma 1 [P+C].** Let a word be any product, in any order, of arbitrary invertible Q-independent maps G_j and N rank-one units I + Q x_k y_k^T with y_k^T x_k = 0 (isotropic). Let P(Q) be its matrix, R = P(-1) P(1)^-1, and let n be the dimension. Then N >= 1 + dim ker(R + I).

*Proof.* (1) Moving every G_j to the left turns each unit into I + Q x'_k y'^T_k with x' = G^-1 x, y'^T = y^T G, still isotropic. So P(Q) = G A(Q), A(Q) = prod_k (I + Q x_k y_k^T). (2) With X = [x_k], Y = [y_k] and L the strictly triangular part of Y^T X in time order, A(c) = I + c X (I - cL)^-1 Y^T. (3) Hence A(1) + A(-1) - 2I = 2 X (I-L)^-1 L (I+L)^-1 Y^T, of rank at most rank L <= N-1. (4) A(1) + A(-1) = G^-1 (I + R) P(1) has rank n - dim ker(R+I); subtracting 2I lowers rank by at most n, so rank(A(1)+A(-1)-2I) >= dim ker(R+I). Combine (3) and (4). QED.

Checks: identity (2) and the rank bound (3) hold exactly on 48 random isotropic instances (n = 3, 4; N = 3..6; c in {1,-1,3}); the lemma holds on 90 further instances; it is attained by the chain root (n = 4, N = 5, R = -I) and by (n = 6, N = 7) [C].

Hypotheses of the lemma: exactness at both real characters (verifier behaviour: the package replay keeps Q as a formal invertible variable, `research/p104-productive-controller/PROOF.md:119`, so specialisation to Q = +-1 is valid); isotropic rank-one units (package convention: units write a register other than the one they read; the shipped endpoint is Y_r -> Y_r + X_r, `PROOF.md:31`, and the event alphabet fixes rank one); and that credited fields are exactly ker(R+I) (derived from whole-job credit, a framework premise, plus the no-leak family assumption below). CONDITIONAL on those.

## 3. Surplus bound

**Theorem 2 (S bound), conditional on H1-H6 below.** For every target size r and every Q-independent network, the per-port surplus satisfies r_p - thin_p <= L_p - 1, hence
**S <= sum_p (L_p - 1) - sum_j c_j**, which is v(L-1) - Lc for uniform ports. Equality requires r >= L-1 and thin = 1 + r - L (thin = 0 at r = L-1). Here thin = N - hosted is the number of Q-odd units that no LOCAL hosts.

*Proof.* Lemma 1 gives N >= 1 + r. By H5 each LOCAL hosts at most one Q-odd unit per port, so hosted <= L and thin >= 1 + r - L. By H4, S per port = r - thin - Lc/v. The target size r cancels. QED [P; the sweep over r = 0..80 and the non-uniform-port form are [C]].

| # | hypothesis | label |
|---|---|---|
| H1 | credited fields = ker(R+I) per port | derived from whole-job credit (framework premise) and the Gaussian endpoint family; the endpoint derivation is a hand argument, CONDITIONAL |
| H2 | units isotropic and rank one | package convention |
| H3 | exact at Q = +-1 | verifier behaviour (see Section 2) |
| H4 | ledger: outer credit = stage rank + r; S/port = r - thin - Lc/v | derived from the invoice shape; the identity 884 = 576 + 288 + 20 is [C] for the record's invoice; the "mains pay exactly the stage rank" step is a hand argument not re-audited, CONDITIONAL |
| H5 | a LOCAL hosts at most one Q-odd unit per port | family assumption (not proved by rank conservation); with two hosted units per LOCAL the same arithmetic would allow 2632 [C] |
| H6 | an unhosted Q-odd unit costs one uncredited rank-one query; natives and Q-independent moves are Q-free; c >= 56 | pricing: package (`pricing.py:48-49`); Q-freeness: package convention; c >= 56: family assumption (Gram-class result), the bound is parametric in c |

Supporting package facts used by the ledger: the price of a native boundary move equals |dim U - dim W| for nested frames (verifier, `local.py:229`) which is the Fourier rank d(U,W) = dim U + dim W - 2 dim(U cap W) of the paper (`notes/general-clifford-frames.tex:16,27`; the inequality d >= |dim U - dim W| used by the ledger is exhaustively checked on F2^4 [C]); public paths are nested and ascending (verifier, `local.py:126`); end frames are pinned (verifier, `local.py:242-243`).

**Open doors, all at hypotheses.** Two hosted Q-odd units per LOCAL (H5); a cheaper realisation of the thin queries (H6, Section 4); c below 56 outside the Gram class; words that leave H1-H3 (scratch with leak, units that read and write one register, exactness only in a limit). The bound concerns the numerator S only; kappa depends equally on the denominator.

## 4. Typed query

**Proposition 3 (scoped).** A rank-one Q-odd unit realised by a Clifford operator has Bruhat rank one: C = aI + bX with b/a = -i, symplectic matrix [[1,1],[0,1]], rank_F2 B = 1, and C lies in a single H-cell F H F with C not in the free monomial group F [C]. For symplectic matrices rank B(UV) <= rank B(U) + rank B(V), and free pieces (B = 0, A and D invertible) leave rank B unchanged [P: B(M1 U M2) = A1 B_U D2], so any factorisation into free pieces and Clifford jobs has Clifford ranks summing to at least one. The plane kernel K_P is a rank-two job in the cell of C (x) C [C]; it does not lower the rank.

**Cost-model reading, CONDITIONAL.** The pricer charges a query shear one rank-one paid call per port (`pricing.py:48-49`), and the finite compiler's base case is a rank-one leaf (`FINITE-PRECOMPILATION.md:139,169`; `05-layers.tex:431,640`). A cheaper accounting for thin queries is not excluded by any text cited here; none exists in the package.

**Not covered.** The non-unitary shear factorisation C = U(i) W U(i) is exact [C] and lies outside the Clifford lemma. Whether a shear-typed supplier can be priced below a leaf (the shear exponent beta) is open.

## 5. Hub rank law

**Theorem 4 (conditional on H-grammar).** Setting: coordinate masks in one frame; units I - 2 x_k y_k^T with y_k x_k = 0 and x_k, y_k inside the mask M_k; one scalar D_k at each LOCAL site and none on thin units; the word equals -diag(prod D^eps) with eps the masks and equals -I at D = 1; characteristic not 2; the total excess N - n equals v; every LOCAL is a width-v block with y_a x_b = 0 for all a, b. Then, at every nonzero D:
(1) rank Z(D) = v; (2) Z_kl = (1/2) Z_km Z_ml for LOCAL blocks k, m, l (Z normalised with diagonal LOCAL blocks 2I); (3) for the first and last LOCAL f < l, Z_fl(D) = Z_fl(1) prod_{LOCAL k in [f,l)} D_k^-1 with Z_fl(1) invertible; (4) at least v coordinates lie in every LOCAL mask.

*Proof sketch [P+C].* (1) Moving each scalar left, the primed word is a product of isotropic units equal to -I; writing the product as I - 2 X A^-1 Y^T with A = I + 2U unit triangular gives X A^-1 Y^T = I_n, so A^-1 Y^T X is idempotent of rank n and I + U - L has rank N - n = v (identity and rank verified exactly on the chain roots, n = 4 and 6 [C]). (2) A diagonal block 2I is invertible and rank Z = v, so the Schur complement of that block vanishes. (3) Entries of Z_{kk'} are sums of multilinear monomials in E = D^-1 and each is divisible by E_k; multiplying the chain over consecutive LOCALs gives divisibility by every E_k in [f,l) while multilinearity bounds each exponent by one. (4) Z_fl(1) is a sum over coordinates c of rank-one terms y_f[c] x_l[c], so rank v needs at least v coordinates. Exact replays at v = 1 (control) and v = 2 with port-coupling gauges, L = 2 and 4, at generic and degenerate nonzero D, all pass [C].

Scope: the checked instances are gauge-equivalent to a direct sum, so they cannot exhibit a non-gauge coupling; the proof, not the replays, carries the claim. The grammar (coordinate masks, unit inside its mask, one scalar per LOCAL) is what a different framework would change; a half-width hub needs one of those to fail, not a rank drop.

## 6. Form-capacity lemma (one-pass family)

**Theorem 5 [P, tested by C].** Family: stops in order Z (frame 0: Y, K, A, E), L_r (line r: X_r, helpers h_r*, scratch), V1 (X, A, B, scratch), Z2 (frame 0: Y, B, E), P_t (hyperplane q_t^perp: Y_t, helpers h_*t, scratch), V2 (X, K, A, scratch); helper h_rt (r != t) visits Z, L_r, P_t, V2; owned rows start at zero; kd = |B| down rows, ku = |A| up rows; any number of helpers per pair. Each stop applies a free invertible map. If Y' = c x with c != 0, T[Y,K] = 0, and X', K' span (y - a x, k) for some a, then **ku >= v**, for every kd and every a.

*Proof.* Let pi project forms modulo span(x). (i) Before P_t the only register carrying x_t is Y_t (helper h_rt carries x-content of x_r only, r != t; scratch is zero), so Y'_t has a nonzero coefficient on Y_t. (ii) pi(Y'_t) = 0, so pi(Y_t before P_t) lies in span pi(h_*t). (iii) After L_r, pi of the helpers and of X_r lies in the span Omega_r of pi(h_r* at Z); with |K| helper registers, dim Omega <= |K|. (iv) By (ii), P_t adds nothing outside Omega; V1 adds only pi of the |A| = ku up rows, and down rows carry only these and x. (v) V2 must output pi-rank v + |K|, so v + |K| <= |K| + ku. QED.

Check [C]: constraining only Y' = x and solving numerically with free X', K', the pi-rank of (X', K') equals |K| + ku (never above) in every solved cell tested (v = 3, kd in 0..6, ku in 0..3, and v = 2), independent of kd. This is generic-solution evidence for the invariant; the proof is the argument above.

**Scope.** Covers the stated stop shape only: targets with T[Y,Y] = 0 and fixed toy pins with independent ports. It does not cover landings of down rows at a line after the register has reached V: a control family with that landing exceeds the bound [C]. It does not cover targets with T[Y,Y] != 0, non-diagonal port Gram matrices, rank-one crossings at mid frames, or real words that read X_r at many frames.

## 7. Label corrections and retained arithmetic

- The requirement that all incident registers at a scalar gate use one identical exact representative is a construction choice of the frame lemma (`notes/general-clifford-frames.tex:62`, "Choose ... use one identical exact representative"). It is sufficient for exactness, and no text I read shows it is necessary. It should be called a package convention, not SPEC.
- The requirement that the word be exact symbolically in D is verifier behaviour. For a word that is multi-affine in D, vanishing on the character grid {+1,-1}^k is equivalent to vanishing as a polynomial (evaluation matrix of full rank 2^k, k = 2, 3, 4) [C]. Replacing the symbolic replay by a character-grid replay therefore changes nothing for such words.
- Public ascend-only paths are verifier behaviour (`local.py:126`), not a law.
- Arithmetic on stated invoice totals (the inputs are hard-coded in the check, not recomputed from a word): root net of perfect mains 85,277 (37.6% of D); public stop tax 142,686 (62.9%); the hub term f(145)*v = 75,049 (33.1%); S = 864 - 104 = 760; a 14.3% cap needs a cut of 28,392 R0 in D (1,577 R0 per call). The two partial sums differ by 4 from the quoted total (226,935 versus 226,939) from rounding of the per-call taxes.

## 8. What is not claimed

No bound on kappa; no statement about the denominator D; no claim on non-diagonal Gram structure; Lemma 1 and Theorem 2 do not cover in-place units, words with leak, or words exact only in a limit; Theorem 5 and Theorem 4 are as scoped above; the shear exponent is open.
