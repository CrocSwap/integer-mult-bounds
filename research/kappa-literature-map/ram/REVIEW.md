# Word RAM and transform literature: exact transferable mechanisms

The strongest concrete result in this lane is a phase-preserving modular port of the actual repaired complex prefix: its two- and three-call arbitrary-target identities work over every commutative ring containing an invertible 2 and a square root of −1. The triangular ports do not need their coupling to be invertible. Exact replay over F₅, F₁₇ and F₉₇ demonstrates the useful characteristic-5 distinction. This is an implementation lemma and tested research direction, not an improved complete multiplication κ.

Eighteen selected primary works were inspected, with honest reading depths in [SOURCES.json](SOURCES.json). Four local Problem 1.8 modules and one machine-reuse note were read and hash-pinned in [LOCAL-PRECEDENTS.json](LOCAL-PRECEDENTS.json), as source-level precedents only. The search is bounded and does not establish that a technique has never appeared in the project. No Lean build, kernel audit, or exhaustive DAG ingestion was performed.

## Fair model and current-caller comparison

Use one uniform Word RAM with w = C log₂(n + 2) bits per word, for a fixed sufficiently large constant C. Charge ordinary arithmetic, Boolean operations, shifts, comparisons, indirect access and stores on bounded words; specify multiplication/high-product access when used. A fixed number of words is allowed for an intermediate whose bit length is explicitly bounded by a constant multiple of w. Neither an arbitrary complex number nor a whole array is a unit-cost register. Packed input and output conversions, table generation, private initialization, and cleanup are part of the bill.

Fürer's [2014 paper](https://arxiv.org/html/1402.1811v1), §2 and Theorems 4.1–4.2, already proves O(n) log-RAM multiplication for SS-C and Fürer's algorithm. The refined depth-cost model is different. The project's [#4541](https://github.com/CrocSwap/integer-mult-bounds/pull/4541) is a stronger comparison baseline than one native operation per TM step: its explicit local tables and packed IO give O((T(n) + n + m)/log(n + 2) + (n + 2)^(1/16) log(n + 2)) for a fixed finite machine with a polynomial address envelope. [#4552](https://github.com/CrocSwap/integer-mult-bounds/pull/4552) and [#4553](https://github.com/CrocSwap/integer-mult-bounds/pull/4553) provide separate checks. Consequently T(n) = O(n log(n)^(1 − κ)) already transfers conditionally to O(n/log(n)^κ) native operations. Removing tape syntax again does not improve that κ.

The pinned [current upstream manuscript](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026) already has Gaussian-dyadic phase frames, selected-bit packing, signed polynomial packing and explicit guard growth. Read locations are `00-introduction.tex`, `05-layers.tex`, `06-transforms.tex`, and `07-resampling.tex`; exact hashes and URLs are in SOURCE-PINS.json. Its complete product also uses analytic Gaussian resampling, roots approximated on a disk grid, CRT layouts and final rounding. A modular identity for the finite dyadic network transports only that algebraic component. It does not make these other operations finite-field operations or discharge their invoices.

The cp22f port uses N = 8^f coordinates and P + H + 4f + 12 bits per real or imaginary coordinate under its displayed contract. With P, H = Θ(log n), only O(1) complete coordinates fit into a C log n-bit word. Broadword packing of such coordinates is therefore a constant-factor optimization. Packing many *short metadata fields* is still useful for address and phase generation, but must not be counted as a second logarithmic speedup.

## Positive theorem: base change of the actual arbitrary-target ports

Let S = Z[i, 1/2], and let R be any commutative ring with identity, an invertible element 2, and an element j with j² = −1. There is a ring homomorphism φ: S → R sending i to j and 1/2 to the inverse of 2. Apply φ entrywise to the literal predecessor matrices and separately tensor each individual letter f times. For every positive f, write

    A = C0_f, L = P_f + 2 Q_f,
    D = J_f W_f C0_f,
    B = M_f C2_f + 2 K_f a_f.

Then the actual three-call branch identity is

    D L A = B.

The two-call and three-call arbitrary-input maps respectively are

    U₂ = [[A, 0], [A L A, A]],
    U₃ = [[A, 0], [D L A, D]].

They are invertible over R, with literal inverses

    U₂⁻¹ = [[A⁻¹, 0], [−L, A⁻¹]],
    U₃⁻¹ = [[A⁻¹, 0], [−L, D⁻¹]].

Their forward and reverse schedules each use two or three Gaussian calls, respectively, together with separately applied monomial terms and ordinary field/ring mixing. Both input banks may be arbitrary. No coupling inverse is executed in these schedules.

**Proof.** The predecessor Gaussian letter is `(1 + i) I/2 + (1 − i) X/2`; its square is X, so its inverse is X times the same letter. All monomial letters have inverse monomial letters with coefficients among fourth roots of unity. Their inverses are identities already inside S; no positive-definite inner product is needed after base change. Each predecessor branch is a matrix-word equality over S. Entrywise φ preserves sums and products, while tensor products commute with φ. Thus each separately tensorized branch equality remains valid. Add the two branches with scalar coefficients 1 and 2 to obtain D L A = B. Direct block multiplication verifies each displayed inverse in both orders. These multiplications use A A⁻¹ = D D⁻¹ = I and never cancel L.

For an explicit Word RAM implementation over a fixed word-sized split prime field, apply each Cj_f in f stages of independent two-point butterflies. This costs O(Nf) ordinary bounded-word field operations per call. Apply monomial maps by the existing address/phase enumeration, with O(N) work and separately owned workspace whose initialization and clearing cost O(N). This gives an actual O(Nf + N) implementation of each fixed port, without a fast-transform oracle. A faster recursive supplier may replace these calls only after its complete contract is bound and paid.

If 15 is also invertible, put T = P_f⁻¹ Q_f. The actual source has T⁴ = I, and

    L⁻¹ = −(I − 2T + 4T² − 8T³) P_f⁻¹ / 15.

Indeed `(I + 2T)(I − 2T + 4T² − 8T³) = −15 I`; all factors commute as polynomials in T. This proves both inverse orders. This *optional* formula needs 15 invertible; the triangular ports do not. Over F₅ with i ↦ 2, the actual tested L is singular at widths 1 and 2 while both complete ports remain invertible. Over F₁₇ and F₉₇ the formula is valid. Finite tests support these examples; the ring argument proves every width.

Absolute scalar phases remain attached before tensorization. In particular, `(−G)⊗f = (−1)^f G⊗f`. Tensoring `P + 2Q` as one base letter introduces different mixed terms and is not the port above. The tests reject this error and an actual phase mutation. Euclidean singular-value and conditioning statements have not been transferred to finite fields. In particular, φ into a split prime field with its identity involution is not a star homomorphism: φ(conjugate(i)) = −j differs from φ(i) = j. A literal conjugated-coefficient inverse word may be transported as that fixed word, but its image is not automatically the Hermitian adjoint for a chosen field involution. In a nonsplit quadratic extension F_(p²), for p ≡ 3 modulo 4, Frobenius can separately supply the conjugation i ↦ −i; that is a different involutive target and is not assumed by these split-field tests.

This theorem reuses the actual letters of [#4688](https://github.com/CrocSwap/integer-mult-bounds/pull/4688), the phase repair and branch identities of [#4710](https://github.com/CrocSwap/integer-mult-bounds/pull/4710), and the arbitrary-target extension of cp22f. It is an elementary base-change application; worldwide novelty is not asserted. It is useful because a modular controller can compose the full port without imposing a false clean-target or coupling-unit precondition.

## Positive theorem: signed modular recovery with an explicit bill

Let a and b be integer polynomials of degree less than r, with every coefficient of absolute value at most B. Every coefficient of their product modulo y^r + 1 has absolute value at most rB²: exactly r signed products contribute to each coefficient. For pairwise coprime moduli p₁, …, p_s with product M > 2rB², the s residue convolutions uniquely determine the exact signed product by centered CRT recovery.

**Proof.** Each coefficient lies strictly inside an interval of length M. Two different such integers cannot be congruent modulo M. The CRT supplies one residue modulo M; its unique centered representative is the coefficient. This argument applies independently to every output coordinate. Each modulus requires its own convolution and its conversion/reconstruction work; the theorem supplies no free prime search or transform roots.

The exact test uses moduli 17 and 97, r in {2, 4, 8}, and B = 3. It checks 192 complete signed negacyclic products, including negative wrap and centered recovery. It also rejects an out-of-range signed recovery. This validates the recovery mechanism, not an optimized NTT multiplier or asymptotic prime supplier. The current manuscript's `signed-ring-product` already contains a complete signed Kronecker alternative; compare complete child sizes and conversions before replacing it.

## Tested and untried technique ledger

| Technique | Exact evidence here | Effect licensed by the evidence |
|---|---|---|
| Modular base change of actual cp22f | Literal 8 × 8 phases rebuilt independently; widths 1 and 2, arrays of length 8 and 64, over three split prime fields; both branch identities and block inverse orders | Exact all-input modular port and direct O(Nf) native implementation; no new complete κ |
| Redundant-residue inverse NTT butterfly | Harvey Algorithm 4 exhaustively checked on five small primes, all twiddles and all redundant input representatives; quotient-removal mutant rejected | A valid bounded-word arithmetic kernel with fewer reductions; constant-factor benefit only |
| Zero-tail TFT | All truncation lengths 1–8 over F₁₇ and 256 roundtrips; equality with selected full DFT outputs and dirty-tail control | Valid truncated interface for declared zero support; test is a matrix oracle, not the fast TFT implementation |
| Carry-isolated SWAR addition | All two-lane additions for data widths 1–4; unguarded-carry control | Safe packed lane arithmetic under the explicit guard condition |
| Precision and paid-bank invoice | Seven exact cp22f guard rows, squared error inequality, full-rank triangular two-bank map | Constant coordinate packing and two independent output banks; no extra productive bank from the off-diagonal term |
| Signed CRT recovery | 192 exact negacyclic products with two paid modulus channels | Sufficient coefficient-recovery mechanism with a strict modulus bound |
| Cache-oblivious FFT / transpose | Primary proof-local review only | Useful implementation plan; no measured speedup or changed native exponent |
| Multipoint Kronecker / two-level cyclotomic CRT | Primary mechanism review only | Candidate reduction of actual padding/child widths; not implemented in the current caller |

The most promising exponent-changing avenue among these is a **complete modular caller** that amortizes a real representation expansion across recursion levels, rather than merely substituting a faster butterfly. [Cyclotomic coefficient rings](https://arxiv.org/html/1712.03693v1), §1.3, provide an actual precedent for that sort of saving. Here the positive starting interfaces are the modular arbitrary-target port and strict signed CRT recovery. A κ claim would still require the explicit whole caller, all independent endpoint jobs, prime/root/setup costs, reconstruction, and a strictly improved complete recurrence. None of those unbuilt components is assumed as an oracle in the present result.

## Primary reading index

The machine-readable bibliography gives exact locations, assumptions and mapping to this caller. “Abstract only” means precisely that; “local proof” means only the specified proof passage, not the whole article.

| ID | Primary work | Depth and relevant location |
|---|---|---|
| SS71 | [Schönhage–Strassen, 1971](https://doi.org/10.1007/BF02242355) | Publisher abstract; fixed-tape baseline |
| F09 | [Fürer, 2009 / STOC 2007](https://doi.org/10.1137/070711761) | Abstract; cheap roots and recursive twiddles |
| F14 | [Fürer, 2014](https://arxiv.org/html/1402.1811v1) | §2 and complete local proofs of Theorems 4.1–4.2 |
| DKSS08 | [De–Kurur–Saha–Saptharishi, 2008 / journal 2013](https://arxiv.org/pdf/0801.1416) | Abstract, §2.2 prime search and §2.3 lifting mechanism |
| HHL14 | [Harvey–van der Hoeven–Lecerf, 2014 preprint](https://www.texmacs.org/joris/mul/mul.pdf) | Theorem 1.1; precision composition §§3.4–4 |
| HV18 | [Harvey–van der Hoeven, 2018](https://arxiv.org/html/1802.07932v1) | Theorem 1.1 and representation-expansion discussion |
| HV21 | [Harvey–van der Hoeven, 2021](https://annals.math.princeton.edu/2021/193-2/p04) | Published abstract; analytic resampling |
| FLPR99 | [Frigo–Leiserson–Prokop–Ramachandran, 1999 / 2012](https://cs.uwaterloo.ca/~imunro/cs840/frigo.pdf) | §3 transpose proof and FFT work/miss separation |
| B90 | [Bailey, 1990](https://www.davidhbailey.com/dhbpapers/fftq.pdf) | Abstract and four-step transform mechanism |
| vdH04 | [van der Hoeven, 2004](https://www.texmacs.org/joris/issac04/issac04.html) | Univariate TFT; corrected multivariate caveat retained |
| H08 | [Harvey, 2008](https://arxiv.org/html/0810.3203v1) | TFT/ITFT definitions and row/column decomposition |
| HR10 | [Harvey–Roche, 2010](https://arxiv.org/html/1001.5272v1) | Explicit ownership/model §2.1 and Algorithm 1 |
| H07K | [Harvey, 2007 / journal 2009](https://arxiv.org/html/0712.4046v1) | Multipoint packing and reciprocal carry equations |
| H12N | [Harvey, 2012 / journal 2014](https://arxiv.org/pdf/1205.2926) | Algorithm 4 and complete Theorem 3 proof |
| V08 | [Vigna, 2008; updated author PDF](https://vigna.di.unimi.it/ftp/papers/Broadword.pdf) | Abstract and §2 broadword framework |
| HV16P | [Harvey–van der Hoeven, 2016](https://arxiv.org/abs/1611.07144) | Abstract; explicitly conjectural prime supply |
| HV17C | [Harvey–van der Hoeven, 2017](https://arxiv.org/html/1712.03693v1) | Theorems 1.1–1.2, §1.3 two-level CRT, principal roots |
| OAI26 | [Pinned OpenAI manuscript, 2026](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026) | Actual phase/guard/signed-packing/resampling source passages |

The local Problem 1.8 modules provide reusable *source-level* run composition, straight-line execution, `Function.update` memory semantics, power-of-two reductions, and a separate bit-cost ledger. Their polynomial-word-length theorems do not imply w = C log n, and their schoolbook instruction bound does not imply a new sharp multiplication exponent. Canonical sources and the live DAG were not edited. A targeted typed-DAG name lookup returned no exact module hit; an expensive broader lookup was stopped without a result, so no typed-port retrieval or source-matched kernel evidence is claimed from it.

## Reproduce and credit

Run `python3 -I -B test.py` and `python3 -I -O -B test.py` from any working directory, supplying the absolute or relative script path as appropriate. Python 3.12 or later and the standard library suffice. Expected final line: `PASS_RAM_LITERATURE_TECHNIQUES`. EXPECTED.json is a deterministic receipt, not an independent proof certificate. Every check raises explicitly under optimized Python. Tests implement the positive lemmas independently; they do not fetch papers, import Lean, or make network requests.

Credit the paper authors above; Dugongue's earlier packed transfer (#4541), its independent checks (#4552/#4553), Jacob Alan Sussman's complex engine framework (#4628), lee-phys's prefix (#4688), Yiyang / Lyy-iiis's phase repair (#4710), and all inherited current-provider suppliers. Prepared for Dugongue with substantial OpenAI Codex assistance. The tests and proofs here are not independent human peer review. No copyrighted paper PDFs or local Lean source files are copied into this deliverable.
