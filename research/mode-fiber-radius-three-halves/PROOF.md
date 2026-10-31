# Mode-fiber rounding radius: R ≤ 3/2

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

## Setting

M is the 112×8 mode matrix of Dillon Amburgey's
[PR4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933), read from
`research/coded-native-caller/NORMALIZERS.json` (`mode_columns`), with rows
m_0, …, m_111. As in #6312 (`research/mode-preserving-rounding`) and #6320
(`research/mode-fiber-radius-bounds`), let

    ρ(x) = min { ‖z − x‖∞ : z ∈ ℤ^112, Mᵀz = Mᵀx },
    R    = sup { ρ(x) : the fiber is nonempty },

and L = Mᵀℤ^112. #6312 proves R ≥ 1, and #6320 proves R ≤ 2 (its Theorem C).
This note proves **R ≤ 3/2**, so 1 ≤ R ≤ 3/2, with a shorter argument than
Theorem C. It needs neither #6320's genericity reduction nor its Hall lemma.

## 1. Finite facts (exact, verify.py)

* **Blocks.** The 112 rows split into 14 blocks of 8 by support. In block s, one
  *pinned* coordinate p(s) has a fixed sign σ_s, and the three free coordinates
  take all 8 sign patterns.
* **Code.** The 14 supports, with 0 and 1⁸, are the 16 words of the extended
  Hamming code H8 = [8,4,4], and the complement of a support is a support.
  Since every row reduces mod 2 to its support, L mod 2 ⊆ H8. Each coordinate
  lies in exactly 7 supports.
* **Column sums.** Σ_i m_i = (32, 16, 56, 0, 0, −8, 0, 0) ∈ 8ℤ⁸. Hence
  C := ½ Σ_i m_i ∈ 4ℤ⁸.
* **Pairs.** Call rows a, b of one block a *j-pair* if they differ only at the
  free coordinate j, so m_a − m_b = 2(m_a)_j e_j, or if j = p(s) and they are
  antipodal on the free coordinates, so m_a + m_b = 2σ_s e_j. For every
  ε ∈ {±1}, a j-pair has signs κ_a, κ_b ∈ {±1} with κ_a m_a + κ_b m_b = 2ε e_j.
  The signs are κ_a = ε(m_a)_j = −κ_b in the first case and κ_a = κ_b = εσ_s in
  the second. Every block has two kinds of perfect matching into pairs:
  - a *straight* matching: 4 j-pairs, for each j ∈ s;
  - a *rainbow* matching: one j-pair for each of the 4 coordinates j ∈ s.

## 2. Balancing lemma

**Lemma.** Let u ∈ ℤ⁸ with ‖u‖∞ ≤ 4 and u mod 2 ∈ H8. Then some κ ∈ {±1}^112
satisfies Σ_i κ_i m_i = 2u.

*Proof.* Let h = u mod 2 and g = 1⁸ − h, the set of coordinates where u is even;
g ∈ H8. Choose matchings as follows:

- if g = 0, every block is rainbow;
- if g is a support s, block s is straight in direction min s and the rest are rainbow;
- if g = 1⁸, take a complementary pair of supports s, s̄; both are straight and
  the rest are rainbow.

Every row lies in exactly one pair. Let n_j be the number of pairs in direction j.

- With all blocks rainbow, n_j = 7, since j lies in 7 supports.
- Making block s straight in direction a changes n_a to 10 and the other three
  coordinates of s to 6.

So n_j is odd and equals 7 where u_j is odd, which covers |u_j| ≤ 3. Where u_j is
even, n_j ∈ {6, 10}, which covers |u_j| ≤ 4. For each j, give
(n_j + u_j)/2 of its pairs ε = +1 and the rest ε = −1. Summing the pair
identities gives Σ κ_i m_i = Σ_j 2u_j e_j. ∎

verify.py checks all 16 cases of h. In every case the pair counts are at least
6 on even coordinates and 7 on odd ones.

## 3. Theorem D: R ≤ 3/2

**Theorem D.** For every x ∈ ℝ^112 with Mᵀx ∈ L, some z ∈ ℤ^112 satisfies
Mᵀz = Mᵀx and ‖z − x‖∞ ≤ 3/2. Hence R ≤ 3/2.

*Proof.*

1. *Centre.* Let c ∈ ℤ^112 be a nearest integer vector to x and v = x − c ∈ [−½,½]^112.
   Then r := Mᵀv ∈ L.
2. *Vertex.* The polytope Q = {v′ ∈ [−½,½]^112 : Mᵀv′ = r} contains v. Take a
   vertex v*. The set F = {i : |v*_i| < ½} indexes linearly independent rows, so
   |F| ≤ 8.
3. *Snap.* Put s_i = +1 if v*_i ≥ 0 and −1 otherwise. Then s_i/2 = v*_i off F.
   Set u = Mᵀ(v* − s/2) = Σ_{i∈F} (v*_i − s_i/2) m_i. Each coefficient has
   absolute value at most ½, and column j meets at most 8 rows of F, so
   ‖u‖∞ ≤ 4. Also

       u = r − ½ Σ_i s_i m_i = r − C + Σ_{s_i = −1} m_i ∈ L,

   because r, C ∈ 4ℤ⁸ ⊂ L (2e_j = m_a − m_b ∈ L) and the rows lie in L. So u ∈ ℤ⁸
   and u mod 2 ∈ H8.
4. *Balance.* The lemma gives κ ∈ {±1}^112 with Σ κ_i m_i = 2u.
5. *Round.* Set e_i = (s_i + κ_i)/2 ∈ {−1, 0, 1} and z = c + e ∈ ℤ^112. Then

       Mᵀz = Mᵀc + ½ Mᵀs + ½ Σ κ_i m_i = Mᵀc + Mᵀ(s/2) + u = Mᵀc + Mᵀv* = Mᵀc + r = Mᵀx,

   and |z_i − x_i| = |e_i − v_i| ≤ 1 + ½. ∎

The point of the vertex is that every row off F is already at ±½, where both
neighbouring integers are equally close. The rows then enter only through
signs κ_i, and the pair structure turns signed sums into an 8-coordinate
balancing problem with a large margin: up to 7 or 10 pairs against a
demand of at most 4.

`rounder.py` executes steps 1–5 and the lemma in exact rational arithmetic. It
raises if any claimed bound fails. verify.py runs it on 150 fixed exact
inputs, including the #6312 witness. A separate stress run on 12,000 exact
random and sparse inputs found no failure. Its worst error was
1259/840 ≈ 1.4988, so 3/2 is the limit of this construction, not evidence
about R. The loss is in step 5: a row with |v_i| near ½ can receive e_i = −2v_i.

## Scope

R is a property of the stated exact-mode contract for this M, inherited from
#6312. Nothing here shows that an actual caller must preserve these modes, or
supplies a physical rounder, error ledger, tape/precision bill, supplier
admission, new κ or frontier change. The five framework assumptions keep their
status. Theorem D is a written proof whose finite inputs are checked exactly;
no proof-assistant or independent human review is claimed. Theorem D supersedes
the upper bound of #6320's Theorem C. #6320's Theorem A (R = 1 is a finite
zonotope-filling question) and its evidence for R = 1 are unchanged.
