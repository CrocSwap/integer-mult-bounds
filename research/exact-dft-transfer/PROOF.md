# The complex suppliers transfer to the exact discrete Fourier transform

This package records a transfer, not a new κ. The complex suppliers of this repository are *batched networks* in
the sense of eumemic's `exact-dft-bounds` (`notes/batched-dft-note.tex`, commit `6f87d1a`), so each certified
complex moment root `a` gives, in the exact complex-arithmetic model of OpenAI's *An explicit power saving for the
exact discrete Fourier transform* (25 September 2026, `openai/math` at `adc7f12`), an exact DFT of every length and
an exact complex convolution in

    O( n (log n)^θ (log log n)^(4−θ) ),    θ = 1 − a.

eumemic's repository proves this for the PR #144 supplier on main (`a = 607/1250000`). This package adds the two
later suppliers and the verification of all three in one place; the same two propositions were submitted to that
repository as its pull request #1 (`c92cf70`).

| Supplier | Package / certificate | m | W per vertex | Deficit | Largest child | a (certified here) | θ |
|---|---|---:|---:|---:|---:|---:|---|
| PR #144 (main `d1d6c07`) | `certificates/paired-cube-complex-input.json` | 72 | 29,937 | 1,936 | 60 | 607/1250000 = 4.856·10⁻⁴ | 1 − 4.856·10⁻⁴ |
| PR #200 (`a1175449`) | `research/paired-cube-diagonal-bit-168/certificate.json`, `complex.profile` | 66 | 13,163 | 1,320 | 20 | 3327/5000000 = 6.654·10⁻⁴ | 1 − 6.654·10⁻⁴ |
| PR #194 (`a8c8778`) | `research/source-assisted-v4/certificate.json`, `complex_profile` | 66 | 12,052 | 1,320 | 20 | 7009/10⁷ = 7.009·10⁻⁴ | 1 − 7.009·10⁻⁴ |
| PR #233 (`52c6fba`) | `research/source-assisted-v4-layer/certificate.json`, `complex_profile` | 66 | 12,052 | 1,320 | 20 | **7086/10⁷ = 7.086·10⁻⁴** | **1 − 7.086·10⁻⁴** |

For every fixed κ < 7086/10⁷ the exact DFT and exact convolution take O(n (log n)^(1−κ)) operations. In OpenAI's
preprint the saving is about 2.1·10⁻¹³; eumemic's batched recursion with the PR #144 supplier gives 4.856·10⁻⁴;
the PR #194 supplier gives 7.009·10⁻⁴; the PR #233 supplier (the same word with PR #200's physical layer, Proposition D below) gives 7.086·10⁻⁴.

## The transfer (by reference)

eumemic's note establishes, in OpenAI's model: a *batched network* of width m on W roles is a finite list of
gates (fixed linear maps with coefficients in Q(i), applied pointwise across arrays), adapters (affine binary
address maps with quadratic phases) and children (C^{⊗ρ} on ρ bit positions of every column) that applies
C^{⊗mf} to every role array for every f (Definition 2.1); a frame-consistent network correct on one column is
correct on every number of columns (Lemma 2.2); the address work is linear (Lemma 2.3); and if the children of
width ρ number N_ρ and Σ_ρ N_ρ (ρ/m)^θ < W then C^{⊗k} costs O(2^k (k+1)^θ) (Theorem 3.1), from which OpenAI's
Sections 3–5 give the DFT and convolution bounds unchanged (their Section 5 of the note). Lemma 4.1 there shows that
every exact operator with entries in Q(i) that normalizes the Pauli group is adapters around one child whose
width is its Fourier rank, so the child histogram depends only on the binary frame data.

The moment Σ_ρ N_ρ (ρ/m)^θ < W with θ = 1 − a is exactly this repository's coarse-saving moment
Σ_ρ n_ρ ρ (m/ρ)^a < W m (the group factor |G| cancels), so a supplier's certified complex saving is the DFT
exponent saving, up to the slightly weaker exp/log bounds used here (which is why PR #200's 6.65489…·10⁻⁴ is
certified as 6.654·10⁻⁴).

**Proposition A (PR #144).** eumemic's Proposition 4.2: the three-stage shared-core word with copied centres,
exact representatives for every frame, the ledger of `notes/paired-cube-sharing.tex`. Not re-proved here.

**Proposition B (PR #200).** The complex supplier of `research/paired-cube-diagonal-bit-168` (the PR #168 v4
lineage with that package's own physical operation frames, 2,310 compensated reuse pairs and 44 terminal sinks) is
a batched network of width 66 on |G|·13163 roles with the per-vertex children of
`certificates/network-children-pr200.json`. *By reference:* (1) the three-stage shared-core word is retained from
PR #144; the annealed, fused local scalar word's complete signed identity is replayed on every formal column in both
shear signs (`complex/physical.py`, `complex/verify_fused.py`), which is the one-column identity Lemma 2.2 extends;
(2) every operation carries one rational frame shared by both registers and every role's frames nest along its
chronology (entrance, operations, root frame, full space), the frames being the exact representatives of
`general-clifford-frames.tex`, so each transition is adapters around one child of width its rank increment;
(3) reuse pairs (rename after a compensation read with exact adjoint coefficients), terminal sinks (delete a
destination-only register, route its writes through a pivot) and fused outputs are gates; copied centres are
temporary streams; (4) the ledger Σ ρ n_ρ = 867438 = 66·13163 − 1320 is re-counted by the package verifier, which
also certifies the moment root 665489485337/10¹⁵ with outward intervals. All gate coefficients are rational (±1
shears, denominators dividing six, exact rational adjoints).

**Proposition C (PR #194).** The source-assisted complex supplier of `research/source-assisted-v4` (icekylinx's
PR #184 frame-flow compression with exact dirty lifts, rebuilt on the v4 modules by ikeboy) is a batched network of
width 66 on |G|·12052 roles with the children of `certificates/network-children-pr194.json`. *By reference to
`notes/source-assisted-note.tex` and the PR #194 checkers:* (1) the complete transcript is a linear word
z_final = Mz + Lx with M invertible, each operation an exact local map with dyadic coefficients (the lift certificate
records all coefficients in {±1, ±2, ±1/2} with their inverse gate programs) or a source control: gates; reads subtract
the recomputed dirty response at frame zero, the endpoint identity K + B = I is checked exactly, every auxiliary is
brought to the full frame and every gate reversed, which is the one-column identity, replayed by the independent
scalar transcript with arbitrary dirty probes and mutation controls; (2) the flow is monotone along nested frame
chains (the lift checker verifies the monotone flow, the acyclic once-only reuse DAG and frame containment at every
vertex), so each transition is adapters around one child of its Fourier rank, with the ledger identity
Σ ρ n_ρ = 794112 = 66·12052 − 1320; (3) the invertible auxiliary maps of that note's lemma are gates at their frame,
and the compression removes roles, not children; (4) `contract_v4.py` certifies fresh columns, read chronology,
target chains and the normalized profile, and PR #194 certifies the moment root 7.00918…·10⁻⁴.

**Proposition D (PR #233).** The complex supplier of `research/source-assisted-v4-layer` is PR #194's word with only the physical layer (operation frames and reuse pairs) replaced by PR #200's descent; the flow, exact lift and contract are PR #184/#194's unchanged, and PR #200's complete complex checker admits the layer on the aligned word. Proposition C applies verbatim: the same gates, the same monotone nested chains and lifts, the ledger identity Σ ρ n_ρ = 794112 = 66·12052 − 1320 with a different child histogram, and the certified moment root 3543063/5000000000 = 7.0861…·10⁻⁴.

**Moments.** `verify.py` bounds Σ n_ρ (ρ/m)^θ above in exact rational arithmetic (artanh series with a tail bound
for the logarithms, exp(x) ≤ 1 + x + x²/(2(1 − x/3))) and records the margins: 3.16·10⁻³ (PR #144), 2.69·10⁻³
(PR #200), 5.27·10⁻⁴ (PR #194), 3.58·10⁻⁴ (PR #233). For each supplier the next 10⁻⁷ grid point is rejected.

## Scope and limits

- Conditional on the correctness of the suppliers' constructions, exactly as in eumemic's note: the exact complex
  phases, the Cayley cover and completed-core sharing are written arguments; the scalar identities, frame nesting,
  ranks and ledgers are checked by the packages' scripts. For PR #194 the scalar transcript replay checks the
  one-column identity but does not materialize the physical Clifford transports.
- The interfaces of the multiplication bound that concern the bit supplier, the assembly, routing, precision and the
  Turing-machine model are not used; see Section 6 of eumemic's note for the item-by-item replacement.
- No formal verification. The constants are astronomically large; this is an asymptotic existence and explicitness
  result.
- Nothing here changes any κ of this repository.
