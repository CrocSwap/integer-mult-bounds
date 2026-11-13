# P104 structure laws (no κ claim)

This package states five general laws that bound changes to the P104
invoice. Each comes with a scope and a standard-library checker. It makes no κ
claim and builds no word. The census numbers (laws 1 and 5) are statements
about Clear1nsight's
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) word,
which is vendored unmodified (`data/word-7334.json.gz`, SHA256 `4b9fd118…d9bb2a`).
Proofs, premises and scope tags are in [PROOF.md](PROOF.md).

## 1. Credit/cut law for credited public fields (`credit_cut.py`)

This is the law for a public register that is credited on its path S → T, at
net credit dim T − dim S, with every MOVE priced at its Fourier rank
d(E,F) = dim E + dim F − 2 dim(E∩F).

- **Loss identity.** paid − credit = 2 × Σ(descent depth of each step).
  Laterals and descents included, a public exit step of depth k costs 2k that
  is not credited.
- **Two-sided cut law.** For every up-set U of frames,
  junk_U ≤ o_in(U) + p_out(U) and cout_U ≤ o_out(U) + p_out(U). Public entries
  appear on neither side.
  - The entry side needs invertible T.
  - The fuzz shows the premise is needed: every violation is on a singular-T
    word.
- **Consequences.**
  - A zero-loss credited field leaves no up-set, so it supplies no cut
    capacity.
  - Any credited public substitute for an owned entry of depth k pays at least
    2k, where the owned entry pays k.
- **#7334 census.**
  - All 6,232 public MOVEs ascend.
  - All 73 owned lifetimes are monotone.
  - On all 511 principal up-sets the law holds, and on every one of the 501
    with an owned entry, **need_in = o_in with zero slack**. That is 2,032
    entry incidences, each carrying a dimension the public arrivals cannot
    supply.

## 2. Legality is forced by the specification (`legality.py`)

- The specification fixes the complex label space as F₂ʰ with the
  **ordinary dot product** (`upstream/build/sections/03-motifs.tex`, checked
  verbatim), and fixes the terminal labels X: U_a → 𝓕, Y: 0 → U_a^⊥.
- Over **all** Lagrangians at h = 4 and 5, the charts are exactly the
  Lagrangians split by (L₀, L_F).
- The x_p and y_t cones share a frame iff p·t = 0.
- No other form is free:
  - a different symmetric Gram M costs rank(M+I);
  - an alternating form cannot express an endpoint relation, which needs a_p·b_p = 1;
  - the most general sound variant moves Y ends, at 2 per moved end.

## 3. Owned-unit deletion bound (`owned_deletion.py`)

This law covers exact 8-term decoders in PR968's normal form (D = RA, T = RB,
ABᵀ = 2I) on the E8 lines with h = 9 labels, after a puncture of p lines.

- **The bound.** cst ≥ 56 − E(p), where E(p) = 0 for p ≤ 24, 1 at p = 25,
  2 for 26 ≤ p ≤ 35, and 6 for 36 ≤ p ≤ 38.
- **Consequences.**
  - cst = 48 is impossible for every n = 120 − p ≥ 82.
  - For n ≥ 85, cst ≥ 54.
- **With the 16 lines Z16 kept in the puncture.** Z16 is the complement of
  PR968's 104-line clique. Then E_Z = 0 up to p = 34, 1 at p = 35, and 2 for
  p = 36 to 38.
- **What the checker computes.** It generates E8, the S9 pairing and every
  object below from scratch.
  - It reproduces PR968's hyperplane-normal census: 440,880 normal lines, with
    D7 π7 = 42 and every other type at least 51.
  - Non-flat normals need at least 52 lines.
  - Root reduction sets need at least 25, 37 and 45 lines at levels 2, 3 and 4.
  - The Stab(root) orbit representatives have sizes 25, 29, 29, 33, 36 and 37.
  - The E(p) table comes from a complete enumeration of unions. It is
    cross-checked by a run without the orbit reduction.
- **Scope of the statement.** It is a lower bound; attainment is not claimed.

## 4. Odd-rank classes of per-port contracts (`contracts.py`)

These are per-port contracts M = W₁·L_c·W₂ over monomials ±q^e, with q a
primitive 4th root of unity and σ: q ↦ −q.

- **Classification.** Modulo q-even monomials there are 5 classes (32
  representatives), plus 3 monomial classes.
- **o = r.** In every class the σ-rank o(M) = rank(σ(M)M⁻¹ − I) equals the rank
  r(M) of the q-odd part, because σ(M)M⁻¹ − I = −2·Odd(M)·M⁻¹.
- **Bills need q-even W.** The minimal bill min_W rank(M − W) must range over
  q-even W. With odd W, classes D and D′ drop to 1 while o stays 2.
- **The per-J odd unit is an integer rank deficit, not a parity.**
  - o(L_q) = o(L_q²) = 1, and o(H) = o(H²) = 2 with H³ = −I.
  - The genuine Z/2 invariant is det σ(M)M⁻¹.
- **Equality clause (char ≠ 2).** Suppose g = h₁⋯h_k with
  Σ rank(h_j − I) = rank(g − I), and g = −1 on Im(g − I). Then every h_j is an
  involution. This is proved, and checked exhaustively on small groups, with
  non-involutive counterexamples once the hypothesis is dropped.
- **Hub bound.** Suppose hub operations have the form Y ⊗ BᵀXB, with B of rank h
  on n ports. Then a target with odd part Odd ⊗ Iₙ needs at least
  rank(Odd)·(n − h) rank-1 transfers outside the hub. For h = 8 and n = 104
  that is 96 per unit of r.

## 5. Helper-layer lower bounds on #7334 (`helper_floor.py`)

Here the mains and the owned registers keep their schedule, and helpers climb
strict inclusions at D0 = f(b−a) − Σ f(steps), with f(r) = r ln r.

- **Per-frame need.** A frame G needs at least B_G helper stops. On #7334,
  Σ B_G = 681, and #7334 meets B_G on every frame.
- **Sound floor.** When helper count and endpoints are free, the chain cover
  adds nothing: every stop costs at least f(2). So **helper D0 ≥ 944.07**,
  against #7334's 9,983.73.
- **Conditional floor.** With #7334's (start dim, end dim) census fixed, the
  floor is **≥ 1,367.08**. It is recomputed by weak duality from vendored
  multipliers, so no solver is trusted.
- **Where the gap sits.** #7334's own need-serving chains cost 5,842.98, and
  4,140.75 is spent on stops at zero-need frames.

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-structure-laws
```

There are five commands, listed in [VERIFY.json](VERIFY.json). Each prints
every number it reproduces, asserts it, and runs at least one control that
must fail. All of them use the standard library only.
- The #7334 word is authenticated by SHA256.
- The specification and notes files are pinned in
  [SOURCES.json](SOURCES.json).

## Caveats

- These are lower bounds and structural laws. Nothing here is a construction,
  and no bound is claimed to be attained.
- Law 1 assumes the net-credit rule. A credit rule that also credits lateral
  or net-down paths is outside its scope, and so is a word with singular T
  (entry side).
- Law 2 takes the specification's target C^{⊗m}, its terminal labels, and the
  rank-0 adapter class that fixes L₀ as given.
- Law 3 covers exact 8-term decoders in PR968's normal form with punctures
  p ≤ 38. It says nothing about decoders with nine or more terms.
- In law 4, the counts 17, 36, 104 and 8 enter only as parameters.
- Law 5's floors use per-frame ranks of fixed contents. Bounds of this type
  cannot certify that a helper layer is near-optimal. The 1,367.08 floor holds
  only under its endpoint premise.
- No human has reviewed the package.

## Open next questions

- **Time-resolved helper floor.** Can a rank-flow (network-coding) cut that
  tracks helper tokens through time lift law 5's floor well above 944 D0 on
  #7334? Per-frame rank bounds cannot.
- **Beyond the owned-bound scope.** Does law 3 extend to nine-term decoders or
  to punctures p ≥ 39?

See [TASK.json](TASK.json).

## Credit

The census word is Clear1nsight's #7334, built on the signed #7113 caller of
Rohan Arun and the price and replay lineage of ToikY and others (see
[NOTICE](NOTICE)). The owned bound builds on PR968's decoder normal form.
DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
Apache-2.0.
