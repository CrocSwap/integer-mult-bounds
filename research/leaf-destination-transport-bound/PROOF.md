# Exact maximum of leaf-destination transport: E(n) = max(1, floor(log2 n))

Status: a written proof checked by its author with exact finite computation (`verify.py`). It
has not been independently reviewed.

## Theorem

Take PR628's balanced reserved-depth dirty word on n free, noncommuting, contractive factors,
in either orientation. Inject a unit error at the destination of a completed leaf and transport
it to any later cut. Let E(n) be the largest mass of any register over all such injections, cuts
and orientations. Then

  **E(n) = max(1, floor(log2 n)) for every n >= 1.**

It is the conjunction of Theorem 1 (upper bound, §3) and Theorem 2 (an attaining family for every
n >= 2, §4). In particular E(2^h) = h. The range h−1 .. h+2 (h = ceil(log2 n)) left open by
PR1416's `single-register-interval-transport` closes at floor(log2 n), which is h for powers of
two and h−1 otherwise.

## 1. Setting and notation

PR628 `compose(x, y, factors)` with n >= 2 factors splits at mid = floor(n/2): B is the first
b = floor(n/2) factors, A the last a = ceil(n/2) factors, and z is the depth scratch. With
U = (x -> z, B) and V = (z -> y, A), a call of sign + runs the phases U, V, U', V', and a call of
sign − runs V, U, V', U' (a prime marks a sign − phase). A single factor is a leaf y += s f x.
Scratch levels are numbered 1 (z of the top call), 2 (the children's z), and so on.

Factors are free noncommuting contractions. The entries of a column are noncommutative
polynomials. The mass |p| of an entry is the sum of absolute coefficients, which bounds the
operator norm of that entry. fl(x) = floor(log2 x); for k >= 2,
fl(floor(k/2)) = fl(k) − 1 and fl(ceil(k/2)) = fl(k+1) − 1.

For a call K and a cut t inside it, Pre_K(t) is the map from K's start to t. For an injection at
a leaf of K, e(K) is the largest mass of any register at any later cut inside K, and e(m) is the
maximum over calls of size m and both signs. E(n) = e(n).

**Facts.** (F1) Inside a call K, the source x_K is never written and the destination y_K is
never read. (F2) A complete call K of sign s acts on any column exactly as y_K += s P_K x_K,
where P_K is the ordered product of its factors, and restores its scratch exactly.

## 2. Lemmas

**Lemma S and Lemma L2** (proved together by induction on the call size).
- (S) Pre_K(t)[y, x] is 0 or s·P_K.
- (L2) Every entry of Pre_K(t) is 0 or a single signed monomial.

*Proof.* A leaf gives y += s f x. For a larger call, Pre_K(t) = Pre_child(t) ∘ T, where T is the
composition of K's completed phases before the child that contains t. By (F2):

Sign +:
- child U: T = I.
- child V: T is z += Bx, so Pre[w, x] = Pre_V[w, z] B.
- child U': T is z += Bx then y += Az, so row y = (1, A, AB). Then
  Pre[z, x] = Pre_U'[z, x] + Pre_U'[z, z] B ∈ {−B, 0} + B = {0, B} by (S) for U'. Rows below z
  have Pre_U'[w, z] = 0 by (F1).
- child V': T leaves z and sets y = y + Az + ABx. Then Pre[y, z] = A + Pre_V'[y, z] ∈ {A, 0} by
  (S), and Pre[y, x] = AB.

Sign −:
- child V: T = I.
- child U: row y = (1, A).
- child V': T sets y = y + Az and z = z + Bx. Then Pre[y, x] = Pre_V'[y, z] B ∈ {0, −AB} and
  Pre[y, z] = A + Pre_V'[y, z] ∈ {A, 0}.
- child U': row y = (1, −AB). Then Pre[z, x] = Pre_U'[z, x] + B ∈ {B, 0}.

In each case every entry is 0 or one signed monomial, and (S) holds with P_K = AB. ∎

**Lemma L1 (exit column).** Inject at the destination of a leaf inside K. At K's end every entry
has mass at most 1, the source entry x_K is 0, and the support lies in {y_K} ∪ scratch(K).

*Proof.* Induction. The child's exit column is zero at the child's source. The remaining phases
at K's level add at most one term to an entry that was 0, or cancel: sign + from U, V adds
A c_z to y and V' removes it; sign + from U', y = −A c_z; sign − from U, y = −A c_z; all other
cases leave the column unchanged. ∎

**Lemma I (inverse).** word(k, −s) is word(k, s) reversed with every leaf sign negated. Since a
leaf has x ≠ y, the leaf (x, y, f, −s) inverts (x, y, f, s), so the sign −s call is the
operator inverse of the sign s call, leaf by leaf.

*Proof.* Induction: the sign − call reverses the phase list and negates each phase's sign. ∎

**Corollary I.** Let C and C' = C^{−1} be calls on the same registers. Let column e come from an
injection at a leaf of C followed by C's suffix. Then every prefix of C' maps e to a forward
transport inside C or inside C' that starts at an injected leaf destination, so its mass is at
most e(|C|).

*Proof.* Let C have leaves L_1..L_N and let the injection be at L_i. A prefix of C' of length j
is (L_{t+1} … L_N)^{−1} with t = N − j. If t >= i, the product is the segment L_{i+1}..L_t of C.
If t < i, the inverse L_i^{−1} does nothing to e_{y_i} because it reads x_i, and the rest,
L_{i−1}^{−1} .. L_{t+1}^{−1}, is a segment of C' that starts right after its leaf L_i^{−1}, whose
destination is y_i. ∎

**Lemma X (exit support).** Inject at a leaf of a call K of size k. At K's end let S be the
support of the column and S_z its scratch part. Then |S| <= fl(k) + 1 and |S_z| <= fl(k).

*Proof.* Induction; k = 1 gives S = {y}. Let φ be the phase of K containing the leaf. By the L1
case analysis, phases after φ never change entries on scratch levels >= 2 (they are complete
calls, F2), leave z_K unchanged, and can only set y_K, and only when φ = U' (sign +) or φ = U
(sign −), where y_K = −A c_z.
- φ of V-type (size a): S = S(φ) and S_z = S_z(φ), so |S| <= fl(a) + 1 <= fl(k) + 1 and
  |S_z| <= fl(a) <= fl(k).
- φ of U-type (size b): y_φ = z_K, so S ⊆ S(φ) ∪ {y_K} and S_z = S(φ). Hence
  |S| <= fl(b) + 2 = fl(k) + 1 and |S_z| <= fl(b) + 1 = fl(k). ∎

Both bounds are attained. Call the U-phase that keeps y "y-keeping" (U' for sign +, U for
sign −). Following the y-keeping U-phase at every level (the signs alternate) reaches a leaf
whose exit support is all fl(k) scratch levels plus y. Each level prepends −A_i, so the entries
are ± monomials of strictly increasing length.

**Lemma P (readout, sign + only).** In a call of sign + and size k, let t be the cut after the
leaf reached by following V at every level; this is the first leaf of factor f_{k−1}. Then
Pre(t)[y, x] = P_K and Pre(t)[y, z_ℓ] = f_{k−1} … f_{k−ceil(k/2^ℓ)} for every scratch level
ℓ = 1..ceil(log2 k).

*Proof.* Induction. With K = U V U' V' and t in V, T = U is z += Bx and leaves y untouched. So
Pre_K[y, x] = Pre_V[y, z] B and Pre_K[y, z] = Pre_V[y, x_V], since z = x_V. Deeper levels are V's
scratch levels, covered by induction. ∎

Lemma P fails for sign −: there T contains V, which adds Az to y, and V' cancels it in row y.
`check2.py` confirms the failure.

## 3. Theorem 1: e(m) <= max(1, fl(m)) for all m

Strong induction on m. If both cuts lie in one child, use e(child). Otherwise let K (size
m >= 2) be their lowest common call, with the injection cut t_α in phase φ_α and the later cut
t_β in phase φ_β, so the transport is M = Pre_β(t_β) ∘ T_mid ∘ Suf_α(t_α). Let q be the column at
the start of φ_β. All its entries have mass at most 1 (L1, F2), and registers outside φ_β's
footprint keep that bound. By L2 a footprint row has mass

  |Σ_v Pre[w, v] q_v| <= #{v in footprint : q_v ≠ 0}.   (*)

| K | (α, β) | argument | bound |
|---|---|---|---|
| + | (U,V), (U',V') | T_mid = I; (*) with q = exit(φ_α) and Lemma X | fl(b)+1 = fl(m) |
| − | (U,V') | same | fl(m) |
| + | (U,V') | row y gets (A + Pre[y,z]) c_z ∈ {A c_z, 0} by S; other rows have Pre[w,y] = 0, so the count is at most \|exit(U)\| | fl(m) |
| ± | (U,U') | T_mid touches only y_K, which U' does not read; Corollary I with C = U | max(1, fl(b)) |
| ± | (V,V') | T_mid is U' (+) or U (−) and reads x_K = 0, so it acts trivially; Corollary I with C = V | max(1, fl(a)) |
| + / − | (V,U') / (V,U), (V,U'), (V',U') | x_K = z_K = 0, so T_mid reads only zeros; (*) counts S_z(exit of the V-type phase) ∩ levels(U) | fl(a) |

Here fl(b) + 1 = fl(m), fl(b) = fl(m) − 1 and fl(a) = fl(m+1) − 1 <= fl(m). Every case is at
most max(1, fl(m)) <= max(1, fl(n)). ∎

*Why the floor half matters.* Counting the ceil(log2 |φ_β|) scratch levels of φ_β plus the dirty
source and destination gives only E(n) <= ceil(log2 n), the first version of this argument.
Lemma X instead counts the dirty registers that φ_α can export: at most fl(b) + 1, with b the
floor half, and only B-phases export into a footprint that holds the extra source register. The
ceil-half mutation control (E(6) = 3 > fl(6)) shows that the split direction is essential.

*Exact case values (census only).* For all m <= 80 and both signs the census equals the last
column: fl(m) in the four source-dirty cases, max(1, fl(m) − 1) for (U,U'), and
max(1, fl(m+1) − 1) for every case starting in a V-phase. So the maximum is attained in all four
source-dirty cases for every m, in the V-start cases exactly when m + 1 is a power of two, and
never in (U,U') once m >= 4. Only the (U,V) sign + case has a written lower-bound proof (§4).

## 4. Theorem 2: an attaining family for every n >= 2

Take the top sign +, H = fl(n). Inject at the leaf of factor f_0 reached inside U along the
y-keeping chain U, U', U, U', …, and read row y at the Lemma P cut inside V. By the tight case of
Lemma X, q = exit(U) is supported on z_K (level 1) and levels 2..H, with entry
(−1)^{H−ℓ} f_{floor(n/2^ℓ)−1} … f_1 at level ℓ. Lemma P applies to V with levels shifted by 1,
since H − 1 = fl(b) <= ceil(log2 a), and gives

  y = Σ_{ℓ=1}^{H} (−1)^{H−ℓ} · f_{n−1} … f_{n−ceil(n/2^ℓ)} · f_{floor(n/2^ℓ)−1} … f_1.

The original y entry is 0. The H words have pairwise distinct right factors over the B-letters,
because their lengths differ, so nothing cancels and the mass is exactly H = fl(n). ∎

For n = 2^h this is Σ_{j=0}^{h−1} (−1)^j (f_{n−1} … f_{n−2^j})(f_{2^j−1} … f_1); for example
n = 16 gives f15 − f15f14f1 + f15..f12f3f2f1 − f15..f8f7..f1.

## 5. Exact finite checks

All checks are exact in the free algebra. They corroborate the proof; they do not replace it.

- `verify.py` (registered, about 20 s): `census.word` and `check2.gen` equal the literal PR628
  `compose` event order for n <= 40; `check2` `ok` mode for n = 1..40 (Lemma I, L1, Lemma X bound
  and tightness, the §3 case table, E(n), Lemma P) and the family for n <= 128; the family row
  equals the §4 closed form for n = 2..200, and Lemma P's formula holds for k <= 128; Lemmas L1,
  L2 and S for n <= 32; the independent `census.py` engine gives E(n) = max(1, fl(n)) for n <= 24.
- Author runs (`logs/`): `check2.py ok` over n = 1..80 with the family to n = 512,
  `fam_closed.py 2 512`, and `census.py` for n = 71..128 (`ext_*.log`).
- Mutation controls, which must fail: the unreversed inverse (INV, L1, case table and E fail,
  E(7) = 54; Lemmas S and L2 fail), the ceil-half split (X, case table, P, family and E fail,
  E(6) = 3; the family misses the closed form for 32 of n = 4..39), and dropping the top
  restoring phase (INV and Lemma L2 fail). See `logs/controls2.log` and `logs/controls.log`.
- `lcabound.py`, `patterns.py`: replacing Lemma S's paired entries with independent ones raises
  the envelope to h + 1, so Lemma S is needed.

## 6. Scope

Covered: one unit error at a completed-leaf destination, any later cut, any register, both
orientations, all n. Not covered: internal leaf intermediates, multiple or accumulated errors,
arbitrary joint errors, rounding, aliasing, a precision invoice and kappa.
