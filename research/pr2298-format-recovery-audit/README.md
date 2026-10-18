# PR2298 format, error and recovery chain audit (sections 6 and 4; compact 3a/3b; section 5 chirp/twist identity only)

**Status: independent audit (research note). No kappa is claimed and the selected
frontier is unchanged.** Every audited implication in this scope holds. We found
no FALSE item and no substantive GAP. The audit supplies explicit cutoffs for every
"eventually" or "fixed cutoff" step in section 6, written proofs of the section 4
packing and recovery lemmas, and four documentation clarifications (see below).
These are exact finite checks plus written arguments for one interface layer. They
are not a formal proof of the PR2298 transfer theorem.

**What is new relative to the predecessor and concurrent work.** PR2298's own `checks.py`
already asserts the final recovery cutoff and the gamma bound at b = 2^24
(`10 + 24 < 3*(1<<24)//4`, `F(9,20)*24 > 7`), the carry invariant `0 <= carry <= q(radix-1)` for
n = 2..96, and an `omit_sign_extension` fault in `packing.py`. Concurrent PR #2365 (jerrylin-23,
head `24746e536dfa5e632d4f3036a477ec4f1b7bb0e6`) proves, for b >= 2^524288, `gamma < b/4` and
`448b 2^(-b+gamma) < 1/2` (its items 5-6), which is row 6.15 and the gamma remark below, plus
the H2 items `ceil(b/2) <= L <= b`, `ell < p` and `2 <= alpha`, `alpha^2 < p`. This package adds:
explicit least thresholds for the rest of the section 6 chain (rows 6.1-6.14 and 6.16-6.18) with
a written monotone tail; written section 4 packing, extraction, wrap and Q_p(fg/r) lemmas checked
against an independent Fraction reference; the tight carry maximum q(Q0-1)-1; compact section
3a/3b checks; and the exact section 5 chirp/twist identity. Row 6.15's tail (b >= 19) and the gamma
threshold b >= 48,161 (equivalently b^9 >= 2^140, the same comparison #2365 uses) are an
independent cross-check of #2365, not new results.

## Object and pins

- Audited object: PR #2298 (jmbarrancoml), head `8507498d363735ced0b0a3f02d5ecf80ed3e3805`,
  `research/selected-conservative-outer/PROOF.md`
  (sha256 `4afeb1708cf9568a9cd25afc72b159d5b06d151a6a6aba567a50970b38a1f513`).
  PR2298's `checks.py` (sha256 `2a522b930dd131919f7078fa54dd8c3043173ce8780f3ec519801b7d71d825d8`)
  and `packing.py` (sha256 `08239599c6e31f2f705f0b857a1b935989360d91d1f1eed5b37db71048e1942f`) were not
  imported, and were not used to write this verifier.
- Base commit: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (origin/main). See also [SOURCES.json](SOURCES.json).
- Retained sources consulted, read-only at the base commit:
  - `upstream/build/sections/06-transforms.tex`
    (sha256 `924316e4bc905066281d8f9e8746a49d8829aeb393688608deb1e61c3c87853c`) for unit U2
    (lines 399-420 and 636-719).
  - `upstream/build/sections/07-resampling.tex`
    (sha256 `8a6b91670f9163afb54892489fa2210c77fe1b058f0325ec7d18b44b94be6e2c`). It supplies the DFT sign,
    where `F_q` has kernel `e^{-2 pi i jk/q}` (line 13). It also supplies the imported Harvey and
    van der Hoeven Lemma 2.12 phase accuracy `2^p|zeta~ - zeta| < 2` for p>100 (lines 43-47).

## Reproduce

```sh
python3 -B research/pr2298-format-recovery-audit/verify.py
# optional pin check against a local copy of PR2298's PROOF.md:
python3 -B research/pr2298-format-recovery-audit/verify.py --proof=/path/to/PROOF.md
```

Expected output: the last line is `PASS_PR2298_FORMAT_RECOVERY_AUDIT`, and the line before it is
`S6 explicit cutoff: every section 6 eventual step holds for all b >= 25`. All 17
mutation controls print `DETECTED`, and all 4 hypothesis-sensitivity checks print `BOUND FAILS`.
The per-row least values and the cutoff 25 are asserted, not just printed. The run is single-process and stdlib-only. Measured on Python 3.14.4, it took 17-18 s
with a 21 MB peak RSS. VERIFY.json registers the same command for the generic hook, which pins
Python 3.12. That interpreter was not available on the authoring host, so the registered-hook
replay was not run there. The direct command above was run.

## Hypotheses

**H2 (section 2 conclusions, not re-audited; jerrylin-23 audits sections 1-2 in Discussion #2291
and PR #2365):** p=6b, h=2^-p, T=2^L with b/2<=L, S<T, gamma<=b/4, d<=b^(1/12), d>=2
(p>=2^40), r=2^ell with 2<=r<2^p, and q=ceil(n/b)<=2^b. The strict bounds T<2^b (so L<b) and
S<T<2^b are taken from the section 6 restatement; section 2 itself states b/2<=log2 T<=b. Every row
below still holds with L<=b and S<T<=2^b. PROOF.md's own bound is d<=(6b)^(1/40); d<=b^(1/12) is the
weaker form used here (with it, row 6.8's least b is 24 instead of 25). **Inherited units (named, not re-derived):**
- (U1) A component truncation toward zero has error < sqrt2·h.
- (U2) Each normalized synthetic round is a contraction, with at most ell truncating rounds per
  transform, prefix-slot rounds included (PR2298 section 3; retained source06 lines 399-420 and its
  synthetic-convolution error proposition, lines 636-719, which give sqrt2·M(3ell+1)2^-p and the rho/(1-rho)
  disk criterion that PR2298 instantiates with rho=.7).
- (U3) Phases satisfy zeta~ in D_p (so |zeta~| <= 1) and |zeta~ - zeta| < 2h (HvdH Lemma 2.12 via
  source07 lines 43-47). Row 6.3's no-norm-increase step uses zeta~ in D_p.
- (U4) Each line Gaussian map has disk-grid error < p^2 h (published, via source07). The tensor maps
  A and B0 are contractions with error < d p^2 h: this tensoring step is PR2298 section 5's own
  argument, inherited and not re-audited.
- (U5) Normalized DFTs and length-normalized ring/scalar convolutions are sup-norm contractions,
  and the convolutions have bilinear norm <= 1.

## Verdict table

PROVED means a written argument from H2 and the named units (below, or in the `verify.py`
comments). FINITE-CHECKED means an exact check on the stated domain. The "least" cutoff is the
least integer at which the sufficient inequality holds for every larger value. It is computed
exactly, with a written monotonicity tail argument.

| Item | Statement (PROOF.md) | Verdict | Explicit cutoff |
|---|---|---|---|
| 6.1 | synthetic error < Lh (from sqrt2·ell·h, ell=ceil(L/d), d>=2) | PROVED | L>=2 (b>=4) |
| 6.2 | sqrt2·M(3ell+1) <= M(3L+2) = E_ring < 5TL (M=T/r<=T) | PROVED | L>=2 |
| 6.3 | unit-phase product: no norm increase, error < 4h | PROVED from U1+U3 (2+sqrt2<4). The norm claim is also FINITE-CHECKED (38,809 grid pairs, p=3) | none |
| 6.4 | operand norm <=.7 implies ring output < .701 | PROVED | b>=3 |
| 6.5 | scalar convolution error < 6TLh (E_ring + 3 phase units of 4h) | PROVED | L>=2 |
| 6.6 | chirp error < 8TLh (6TL + three phase units of 4h, budgeted as 16h); output stays in the disk | PROVED | L>=3 (b>=6) |
| 6.7 | expansion norm < .51 | PROVED (U4) | b>=3 |
| 6.8 | 2dp^2 < TL, hence E_s = 9·2^gamma·T·L | PROVED | **b>=25** (binding S6 cutoff) |
| 6.9 | source output norm < .501 | PROVED | b>=4 |
| 6.10 | digits·2^(-b-2) are exact on the p-grid, norm < 1/4 | PROVED | b+2<=p |
| 6.11 | computed transforms norm < .26 | PROVED | b>=3 |
| 6.12-13 | .26^2 < .5; product error < (2E_s+2)h | PROVED (exact) | none |
| 6.14 | S(3E_s+2) < 28·2^gamma·T^2·L; (u*v)/S norm < 1 | PROVED | b>=2 |
| 6.15 | 2^(2b+4)·S·28·2^gamma·T^2·L·h < 448 b 2^(gamma-b) <= 448 b 2^(-3b/4) < 1/2 | PROVED. The algebra is checked exactly on 300 random admissible tuples. Also proved by PR #2365 (item 6) for b>=2^524288; independent cross-check | b>=19 |
| 6.16 | rounded coefficient is exact, 0 <= c < 2^(3b), fits 3b+1 signed bits | PROVED (q<=2^b); FINITE-CHECKED | none |
| 6.17 | 0 <= k_j <= q(Q0-1) < Q0^2, the partial-sum identity, and exact 2n-bit output | PROVED (induction); FINITE-CHECKED on 74,113 cases. The same induction gives k_j <= q(Q0-1)-1 (PROVED); that all-max digits attain it is FINITE-CHECKED (b<=64, q<=64) | none |
| 6.18 | widths w+b, then w+4b+4, lose no significant bit | PROVED (magnitudes < .501·2^b, then < 2^(3b+4)) | none |
| 4.1 | signed packing carry in {-1,0}; two's-complement value = A(B0) | PROVED; FINITE-CHECKED (every vector, r<=4, p<=3) | none |
| 4.2 | coefficient modulus <= r 2^(2p) < 2^(3p) < B0/2 | PROVED for r<2^p **and p>=2** (2^(3p) = B0/2 at p=1) | p>=2 |
| 4.3 | extraction carry in {0,1}, h_j = c_j, h_(2r-1)=0, rho_(2r)+eps=0 | PROVED; FINITE-CHECKED (every real pair, (r,p) in {(1,1..3),(2,2),(2,3)}) | none |
| 4.4 | negacyclic wrap; output numerator modulus <= r 2^(2p) | PROVED; FINITE-CHECKED | none |
| 4.5 | shift by p+ell gives exactly Q_p(fg/r) (truncation toward zero), stays in the disk, error < sqrt2·h | PROVED. FINITE-CHECKED against an independent Fraction ring product: every r=1 grid pair with p<=3, plus extremal and random cases with r<=64 and p<=24 | none |
| 3a | b_i = a_i + mu_i sum_(j<i) a_j P_j ≡ k·mu_i mod s_i; Phi is bijective and multiplicative; shifts run in decreasing i, the inverse in increasing i; padding is fixed | PROVED (b_i reads only a_j with j<i). FINITE-CHECKED for 8 prime tuples with d<=4 on full padded boxes | none |
| 3b | each exchange word is one equal-width interchange plus one bit move and yields the reversal | PROVED (structural); FINITE-CHECKED for m<=6, \|G\|<=6 | none |
| 5 | Q F_t x = conj(a)[a conv (conj(a)x)]/T for even t_i; the zeta twist cancels the negacyclic sign | PROVED for kernel e^{-2 pi i jk/t} (source07's F). FINITE-CHECKED exactly on 18,896 entries and 6,851 twist cases | none |

**S6 conclusion.** Under H2 and U1-U5, every section 6 margin and error step holds for all
b >= 25. The number 25 is the least b for the auditor's chosen family of sufficient inequalities
(with d treated as a real number d<=b^(1/12)); it is not a threshold inside a nonempty parameter
box, since H2's d>=2 already forces b far larger. The meaningful conclusion is that section 6 adds
no cutoff beyond the H2 domain. That is far below the source recovery threshold b >= 2^24. It is also below the section 2
cutoff d >= 2, which needs p >= 2^40, i.e. b >= 183,251,937,963, and below the package domain
log2 b = 524288. Section 6 therefore adds no binding cutoff of its own. As a remark only, not an
audit of section 2: the H2 step gamma <= b/4 via 32 b^(11/20) <= b/4 needs b >= 48,161, which is
also below 2^24; PR #2365 proves this bound (as b^9 >= 2^140) on its domain. The precision is
load-bearing for the proof: the final bound is 448 b 2^(gamma+5b-p), so the section 6 bound chain
closes iff p > 5b + gamma + log2(896b). (This is a property of the upper-bound chain, not a proof
that recovery itself fails below it.) With p=6b and gamma<=b/4 the margin is 3b/4 - log2(896b) bits.

## Written lemmas (section 4)

- **Packing.** |a_i| <= 2^p < B0/2 and the carry k_i is in {-1,0}, so a_i+k_i lies in [-B0, B0) and
  k_(i+1) = floor((a_i+k_i)/B0) is in {-1,0}. By induction,
  sum_(i<m) a_i B0^i = sum_(i<m) blk_i B0^i + k_m B0^m.
- **Extraction.** Let P = A(B0)C(B0) = sum_j c_j B0^j, with c_(2r-1)=0 and |c_j| <= r 2^(2p) < B0/2.
  The c_j are integers and B0 is even, so |c_j| <= B0/2 - 1. Hence
  |A_j| <= (B0/2 - 1)(B0^j - 1)/(B0 - 1) < B0^j/2 for every j >= 1 (the real bound |c_j| < B0/2 alone
  would not suffice for j >= 2), and in particular |P| < B0^(2r-1)/2. Since |P| < B0^(2r-1), write P in two's complement over 2r blocks as
  P = sum_(j<2r) q_j B0^j + eps B0^(2r), with 0 <= q_j < B0. Put Q_j = sum_(i<j) q_i B0^i and
  A_j = sum_(i<j) c_i B0^i. Then rho_j = (Q_j - A_j)/B0^j is an integer, because Q_j ≡ P ≡ A_j mod
  B0^j. It satisfies rho_(j+1) = (q_j + rho_j - c_j)/B0. Since 0 <= Q_j < B0^j and |A_j| < B0^j/2,
  rho_j lies in (-1/2, 3/2), hence in {0,1}. Integrality gives c_j ≡ q_j + rho_j mod B0, and
  |c_j| < B0/2 makes c_j the centered residue h_j. Finally rho_(2r) = (Q_(2r) - P)/B0^(2r) = -eps.
- **Output.** fg/r has numerator N/2^(2p+ell) with |N| <= r 2^(2p), and Q_p truncates 2^p·fg/r toward
  zero. Hence Q_p(fg/r) = sign(N)·floor(|N|/2^(p+ell))·2^-p. Componentwise truncation toward zero does not
  increase the modulus, and each component error is < 2^-p.

## Clarifications (not GAPs)

1. **Sign-extension identity.** The coefficients h_0..h_(2r-2) are determined by q_0..q_(2r-2)
   alone. The identity rho_(2r)+eps=0 is a true invariant and a consistency check, not the
   recovery step. Mutation evidence: setting eps=0 leaves every recovered coefficient correct and
   fails only the identity. Reading the magnitude blocks without the sign negates the
   coefficients but keeps the identity. For negative products, the essential step is reading the
   two's-complement blocks of the signed product.
2. **2^(3p) < B0/2 needs p >= 2.** This is immaterial because p = 6b.
3. **PROOF.md does not decompose the 6TL and 8TL budgets.** The table gives one decomposition:
   E_ring plus 12h (three phase units of 4h) for 6TL, and 6TL plus 16h for 8TL (three phase
   units, 12h, budgeted as 16h). It has slack for L >= 2 and L >= 3 respectively.
4. **Section 6 does not tie the "<4h" unit-phase error to section 5's cited Lemma 2.12.** PROOF.md
   section 5 lists HvdH Lemma 2.12 among the results it uses; the <4h bound follows from that
   lemma (|zeta~ - zeta| < 2h for p > 100, via source07) plus one truncation (2 + sqrt2 < 4). The displayed chirp
   identity depends on source07's DFT sign. With the opposite kernel it fails, and a control checks this.

## Negative controls (17 mutation controls, all must be DETECTED)

- S4: packing without carry, unsigned extraction, ignoring the product sign, dropping sign
  extension, a shift by p instead of p+ell, dropping the wrap, and a floor shift instead of
  truncation toward zero.
- S3a: forward shifts in increasing i; the inverse in decreasing i.
- S3b: swapping the two word recipes; omitting the bit move.
- S5: the opposite DFT sign, odd target lengths, an unconjugated outer chirp, and omitting the twist.
- S6 machinery (exercises least_L/least_b and the asserted table): a non-eventual row 6.6
  (8TL+16 < 8TL) is rejected by the scan-top check; a changed row 6.8 derivation (exponent 3/2
  instead of 13/12) is still eventually true but moves the least b to 29, which the asserted per-row
  table rejects.

**Hypothesis-sensitivity checks (4, not counted as mutation controls).** These are true by
construction and do not exercise the cutoff machinery: using d=1 in row 6.1 makes sqrt2·ell < L
fail for every L; lowering p to 5b+floor(b/4), raising gamma to b, or weakening S<2^b to S<2^(2b)
each makes the stated 1/2 recovery bound fail.

## Scope, inherited assumptions, unresolved obligations

- Section 2 conclusions are hypotheses (H2). The following are inherited and not audited here:
  - the callee contracts of PR2234, PR2287 (extended to epsilon=1/40) and PR2250;
  - the Harvey-van der Hoeven Gaussian maps;
  - the source permutation-cancellation identity (source07).
- Not covered:
  - section 3 identities other than 3a/3b: the synthetic-round exponent
    E = -sum (2r/2^(h+1)) b_i k_i mod 2r, the named-slot reading, the B bit-reversal, and the
    composition L B F^- / F^+ B^-1 L^-1 with composite I/M;
  - section 5 beyond the chirp/twist identity: the dilation identity F^+R_c = R_(c^-1)F^+ and the
    resulting (u*v)/S^2 (a reviewer's floating-point check agreed to about 1e-15, but it is not part
    of this package);
  - section 3's complete-field admission of the extended PR2287 layer (the exact-K chunk
    transposition, header length, named-slot table and common-offset rounds);
  - all cost claims, including the O(V d(1+ell^tau)) reversal cost;
  - section 7.
- The finite checks use small parameters, and the written arguments are informal. No proof
  assistant was used.

## Open next questions

1. **Does section 3's exact-K positional layout meet the extended PR2287 layer's complete-field
   contract?**
   - Why it matters: this is the remaining reviewer request in PR2298 section 8, and the format
     chain audited here assumes it.
   - First step: write the field list (prefix, D=d-1 K-bit chunks, header, named-slot table) as an
     explicit word. Then check it against PR2287's admission predicate for small (d, K, ell).
   - Blocker: the PR2287 layer contract is itself pending review, and the section 1 epsilon
     extension is under jerrylin-23's audit.
2. **Are PR2298 section 3's operation counts right?** The claims are at most floor(d/2)
   nonadjacent exchanges per reversal, at most 2(d-1) exchanges per tensor map, and one
   interchange plus one bit move per one-extra-bit pair.
   - Why it matters: the section 7 row "Nonadjacent CRT and line exposure" (exponent
     tau+epsilon(1-tau)) depends on these counts, and this audit checked only the algebra of the
     words, not the counts.
   - First step: emit the explicit exchange schedule for d<=8 with mixed r/2 and r axis widths,
     then count interchanges and bit moves exactly.
   - Blocker: none.
3. **Can the section 6 table become a machine-checked proof?** One way is to encode each row as an
   exponential inequality with the exact cutoffs found here.
   - Why it matters: this would replace a finite cutoff search plus a written tail argument with a
     formal statement.
   - First step: formalise rows 6.8 and 6.15.
   - Blocker: time. The inequalities need a small exponential-bound tactic.

## Credit

- PR2298 and its proof are by Jose Manuel (jmbarrancoml). It rests on:
  - PR2234, PR2287 and PR2250;
  - Douglas Colkitt's nonadjacent CRT/axis schedule;
  - retained source sections 06-08;
  - Harvey and van der Hoeven (published).
- Concurrent work: jerrylin-23's audit of sections 1-2 (Discussion #2291) and PR #2365 (opened
  2026-10-15T06:43Z, during this audit's experiment), and mason-hale's small-box numerical
  execution (PR2313). PR #2365 overlaps this package on row 6.15 and the gamma remark (its items
  5-6); here those two are an independent cross-check, not new results. The remaining section 6
  rows and the section 4/3a/3b/5 checks are not covered by #2365 or #2313.

Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
