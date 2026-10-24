# Independent review of the fused native Gaussian route

Prepared for Dugongue with substantial OpenAI Codex assistance. This is an informal mathematical/code-design review, not a new formal or external human audit.

## Sources actually read

Read in full: research/capped-fusion-t74-k554/outer/GAUGEFREE-INTERIORS.md; outer/FINE-PADDING-COMPOSITION.md; outer/UNION-SCHEDULE.md; vendor/pr1673/capped-phase-fusion/SHALLOW-TOEPLITZ.md; and vendor/pr1673/capped-phase-fusion/CAPPED-GAUGE-AUDIT.md. The parameter/boundary alternatives in outer/STRUCTURED-BOUNDARY.md were inspected; its stronger unproved structured-stability premise is not required. Sources are bound to canonical commit f626db5c3a3d781d8f7695038776c621651f75e1. Raw copies were fetched at that exact commit when the partial Git clone could not retrieve missing blobs. Their raw Git object hashes, independently computed from byte lengths and blob headers, equal the commit's tree entries. Git hash-object applies the local CRLF filter to some of these files and is therefore not the raw-byte comparison.

SHA-256 bindings:

- FINE-PADDING-COMPOSITION.md: 331189874c79c2fbfb839838ec8ea61c09a7f0769098af88716ad6e7c54c0b5a.
- SHALLOW-TOEPLITZ.md: b384b93f3fb4a8c97da2e617ebc14d55cebb0a739070e7f8dbb66f63e24e9310.
- UNION-SCHEDULE.md: b1e6237655616a9d779f69915eb05a78e001d52150c168588426a5208e3d85a6.

## Precision finding, and its existing resolution

The old capped-gauge audit converts absolute full-cell weight error to relative error using exp(a/(4θ)). Its claim that this is absorbed by C p precision uses θ⁻¹ = O(d) and a d = o(p). That argument alone is invalid after fine padding makes θ⁻¹ = Θ(p²). This is not an outstanding gap in the composed route: FINE-PADDING-COMPOSITION explicitly imports PR #1786's setup precision C p + 64 p² ceil(log₂ p). The larger precision is OFFLINE ONLY and must be included explicitly in any native lowering.

A native implementation computes those setup-only scalars by signed multiword grade-school arithmetic, Machin pi and rational Taylor/series methods at polynomial(p) precision. It costs polynomial(p) per local coefficient, and polynomial(s,p) in total, hence n^o(1) once per axis. It must not claim O(1) bounded-word exp-table queries for these wider setup values. The data circuit applies only locally anchored shifted kernels with O(p)-bit online coefficients; applying the full-cell diagonal to data and hoping it later cancels would be invalid.

For g = p^β simultaneous axes, fine padding gives chirp guard exponent β+2ξ−2, and the accretive shallow circuit adds g polylog(p) bits. Thus β+2ξ−2 < 1 and β < 1 suffice for O(p) total online precision. The source's offline-only override is essential to this conclusion.

## Shallow circuit check

The shifted Gaussian identities are exact expansions. The symbol argument keeps |s| < 1/2, with polynomial lower gap in θ. The Jacobi-product factors interlace, giving argument bounded in absolute value by the first-factor argument, hence an accretive real-part bound. At fine θ⁻¹ = O(p²), both broad and narrow inverse bounds remain polynomial in p.

The full Toeplitz construction actually supplies a finite circuit on the existing wires, rather than an unspecified fast transform. Its principal-section Schur recursion has logarithmic depth; displacement ranks grow additively; the Stein generator representation follows by finite telescoping; the four-update generator shear restores its source; triangular parity children run in parallel. The resulting circuit has O(log⁴ N) matching rounds and O(N log⁴ N) gates. Coefficient setup uses rational minors and exact independent-column/orthogonalization calculations at polynomial local precision. The prefix/inverse-prefix bounds extend from near-identity to accretive principal sections via their inverse norm and Schur bounds.

The accretive proof's shear norm may be conservatively bounded using Λ' rather than the original Λ for descendants; both remain polynomial and this changes only fixed constants/guard logarithms. No exponent changes.

The scalar application of every individual axis would cost T d and would lose the proposed saving. The full theorem must retain the inherited tensor-to-kernel fusion identity and its provider, applying matching rounds on groups of axes. The native Gaussian row is the FUSED tariff, not that scalar fallback. This review validates the cited shallow construction and precision; it does not independently emit a complete fused multiplier program.

## Native union metadata and wrap gathers

The union source's O(g) bit scan for an r-th set bit is paid there by a p-bit tape move. One cannot silently reuse that as O(1) Word RAM work. A constructive native replacement is available: the header contains k = O(g log L) = p^β polylog(p) = o(p) bits, where L is the polynomial microbox side. Enumerate all 2^k headers and all r ≤ g during setup, storing their membership masks and r-th-set-bit tags. The work and space are 2^k polynomial(p) = n^o(1); each key and result fits a machine word. Each online visit then computes its tag in O(1) indexed operations.

For consecutive mixed-radix axis groups, extract the group coordinate by division by its stride followed by reduction modulo its group radix; both fit the declared word. The group local header is then a table key. If a fused circuit uses arbitrary selected binary positions, prepare the full 2^k deposited-submask table. Enumerate complementary masks in increasing order by next = (current−M) AND M, combining each base with every prepared deposited submask. This enumerates each gathered record once, so no per-record k-step extraction is required. The tables are generated explicitly; no PEXT/PDEP or nonuniform advice is assumed. Coarse labels and per-axis factor pages are input-independent local setup. Reuse is paid once per axis/microbox as in the source and amortized by the superpolynomial spectator payload.

Radix distribution, its reverse, transpose/untranspose, splitting and LIFO restoration use O(1) word instructions per moved bounded-word record. The source's complete-line lemma remains exact: membership flags depend only on the chosen-axis membership and the other coordinates. Total visits equal sum_x |F(x)| ≤ g μ V. Thus the native union cost is O(V g μ polylog p) per group, not O(V g² μ). It is unnecessary to retain the source's tape-head API. Periodic indices are reduced modulo their known line lengths using bounded-word arithmetic; gathers/scatters enumerate the explicit physical selected positions and their inverses, including both endpoint groups. No native sorting oracle is assumed.

## Capped boundary cost

Fine cells may have Θ(p²) entries, but capped interiors have length at most B = p^ξ. The boundary density remains O((W/B) polylog p), since cap B < p² and clipped endpoint cells are separately retained. With W = O(sqrt(p/u)), the explicit inverse-block and right-hand-side Strassen batching of BATCHED-INVERSE.md applies to the ordinary factors and the small periodic Woodbury closure. BOTH coupling matrices are evaluated by the same batches. The per-axis cost is O(T W^(ω−1)/B), up to polylogarithms, and summing axes gives O(T d W^(ω−1)/B).

Since 7^16 < 2^45, take ω < 45/16. With T p = Θ(n), this allows native boundary saving

    c + ξ − ε,       c = 3/32.

The weaker explicit Strassen construction is enough; no unproved near-quadratic structured-boundary stability theorem is required. Periodic correction and both endpoint groups remain charged. All matrix inverse/preparation steps are explicit polynomial local calculations, with setup-only multiword scalars separated from the O(p)-bit data path.

## Candidate parameter arithmetic

Let q = 0.0030201656 be an ACTUALLY supplied uniform native kernel exponent, and choose

    δ = 10⁻⁸, ε = 1−δ, β = 1−3δ, r₀ = 10⁻⁹,
    ξ = ε(1+q) − 3/32 + 10⁻¹⁰,
    κ = 0.0030201655.

The modern fused rows are main εq; Gaussian 1−ε+qβ; boundary 3/32+ξ−ε; union ξ+1/2−ε. Every one strictly exceeds κ. The main surplus is about 6.98×10⁻¹¹, so it is essential to keep exact rationals and not replace q by a downward display that erases that gap. Membership 1−β−2(1−ε) = δ > 0; γ spare power 1−ε−r₀ = 9×10⁻⁹ > 0; group size ε−β = 2δ > 0; β < 1; cap 1/2 < ξ < ε; and fine chirp guard 1−β−(2ξ−2)−r₀ > 0. Polynomial setup and all polylogarithmic factors can be absorbed into the corresponding strict margins above a finite eventual cutoff. These are asymptotic mathematical bounds, with no practical cutoff or speedup claim.

This verifies that the fused analytic/native adapter stack has no exponent obstruction at the candidate point. It remains essential that the full submission separately supplies and credits the exact uniform native kernel provider, its all-input operator identity, arbitrary phases, normalization, complete cyclic/convolution embedding and exact recovery. Those are the full assembly worker's obligations, not consequences of this parameter table or finite circuit fixtures.

## Credit

Retain PR #1673 (Vlado Vojdanovski: capped phase-cell fusion/shallow circuits), PR #1758 (fractional-shift accretive interiors and per-visit accounting), PR #1786 (Chafik Boukhalfa: fine primes and offline precision), Tim Trudgian's prime estimate, Jeremy Kothe's ledger lineage, the retained supplier authors and the Harvey–van der Hoeven/OpenAI analytic lineage. Native arithmetic primitives retain PR #4554 and its complete contributor notices. The new review and primitive-specific batching/metadata lowering do not replace predecessor credit.
