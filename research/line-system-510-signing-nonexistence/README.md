# The 510-vertex signing of `line-system-saturation` §11.1 does not exist (negative result, no κ claim)

**Answer to an open question.** `research/line-system-saturation` (#2244) §11.1 asks whether the doubled
non-collinearity graph of W(7,2) has a ±1 signing S with S² = 60S + 256I, equivalently 510 unit vectors in ℝ³⁰
with |cos| ∈ {0, 1/4} realising the saturated uniform-angle pattern (k′ = 4, m = 2, λ = 4 of its Theorem G).
**It does not.** The proof is short and by hand. Its finite steps are checked exhaustively by `verify.py`
(standard library only), and an independent CP-SAT run agrees.

Consequences, all paper-side and scoped exactly as in #2244:
- no saturated uniform-angle (cos 1/4) system on the descent ladder 120 lines in ℝ²⁴ (k′ = 2, m = 8),
  252 in ℝ²⁸ (k′ = 3, m = 4), 510 in ℝ³⁰ (k′ = 4, m = 2);
- the 1023-line candidate in ℝ³¹ (k′ = 5, m = 1, cos 1/4), which #2244 §11.1 notes descends to exactly this
  object, does not exist either; so uniform-angle saturation with m = 1 at k′ = 5 is ruled out.

Not touched: saturated W(7,2) systems with several angles (§11.3), level-2 bounds (§11.2), non-dense pairings
(§11.4). This changes no κ, supplier or selected record.

## Proof

Statuses follow #2244. **PROVEN** below, with finite steps **CHECKED** by `verify.py`.

**Step 1 (descent).** Proposition D1 of #2244 §5.2 at a label p with m_p = 2 keeps the lines with labels in
p^⊥ ∖ {p} and merges q, q + p. The lines are unchanged, so angles stay in {0, 1/4}, and non-collinear quotient
labels have all four representatives pairwise non-collinear (b(q, r + p) = b(q, r)). The result is a saturated
uniform W(5,2) system with m = 4 in ℝ²⁸; once more gives O₂: W(3,2), m = 8, 120 lines in ℝ²⁴. It suffices to
rule out O₂.

**Step 2 (frame form).** Coordinates (x₁, y₁, x₂, y₂) on F₂⁴, b = x₁y₁′ + y₁x₁′ + x₂y₂′ + y₂x₂′. Take the
generator L = ⟨a, b⟩, a = x₁, b = x₂, c = a + b. Its 24 lines are pairwise orthogonal, so they form an orthonormal
frame. Let blocks A, B, C be the 8 frame lines of a, b, c. Any other unit line u has u·e ∈ {0, ±1/4} on frame
lines, and norm 1 forces exactly 16 non-zero entries ±1/4. The support is fixed by the labels: b(a, p) = y₁,
b(b, p) = y₂. The class K₁ = {y = (1,1)} lives on A ∪ B and K₂ = {y = (1,0)} on A ∪ C, so the two classes meet
only on block A. For p ∈ K₁, q ∈ K₂: b(p, q) = x₁(p) + x₁(q) + x₂(q). Put P_i = {p ∈ K₁ : x₁ = i} and
Q_i = {q ∈ K₂ : x₁ + x₂ = i}. On the A-parts (vectors in {±1}⁸, scaled by 4), P₀ ⟂ Q₀ and P₁ ⟂ Q₁, while
P₀–Q₁ and P₁–Q₀ products are ±4. Each collinearity group of K₁ is a Hadamard matrix of order 16 containing
one point of P₀ and one of P₁. The two points of P₀ are non-collinear.

**Step 3 (A-parts).** Let U_i, V_i be the A-parts of P_i, Q_i, with N_i = Σ_{U_i} uuᵀ. Hadamard columns are
orthogonal, so N₀ + N₁ = 32I = M₀ + M₁. From U₀ ⟂ V₀, U₁ ⟂ V₁ and the full rank of the sums, all four
dimensions are 4, S₀ := span U₀ = (span U₁)^⊥ and V₁ ⊆ S₀.
(a) A 4-space holds at most 16 vectors of {±1}⁸. U₀ and V₁ both span S₀ and share no line (products ±4, not
±8). So S₀ holds exactly 8 lines and is the graph of a signed permutation, with (s, Ms)·(t, Mt) = 2 s·t.
(b) Cross products ±4 force odd Hamming distance, so U₀ is one parity class: 4 pairwise orthogonal directions.
(c) A point's group partner has A-parts in S₀^⊥, so each point of P₀ uses each direction exactly twice.

**Step 4 (contradiction).** The two lines of p ∈ P₀ on a direction e are twins, so they are (e, w) and (e, −w)
up to sign. Take a line (±e, w′) of the other point p′ ∈ P₀; it exists by (c). Non-collinearity needs
|±8 + w·w′| = |±8 − w·w′| = 4, so w·w′ = 0 and both values equal 8. Contradiction. ∎

The proof uses only two classes sharing one block. This is why the two-class CP-SAT sub-test below is already
infeasible.

## Evidence

`verify.py` (registered, about 1 s, standard library only) checks:
- that #2244 states the question as open;
- the Step 2 combinatorics exhaustively on W(3,2);
- lemmas (a) and (b) by enumeration, and the Step 4 arithmetic;
- a positive control: the k′ = 1 rung exists, 48 lines in ℝ¹⁶ (frame + Sylvester H₁₆ + bent-shifted H₁₆) built
  and checked exactly, plus two failure controls;
- the Delsarte inequalities. For each rung the forced distance distribution passes every Gegenbauer
  inequality up to degree 40 (degree 2 is 0, a tight frame), so two-point LP bounds cannot decide this question,
  in line with #2244 §6. The plain LP bound for ℝ³⁰ with angles {90°, arccos 1/4} is 900 (floating-point LP, not
  certified here; `tools/delsarte_lp.py`).

`tools/` and `logs/` (renamed `.txt`, since `*.log` is ignored) are provenance, not registered replay. They need `ortools==9.15.6755` and write a
`progress.log` beside themselves, so run them from a copy:

| run | instance | result |
|---|---|---|
| `sat_k2.py 1800 6` | full O₂, plain encoding | UNKNOWN after 30 min |
| `sat_k2.py 1800 6 2` | two classes, plain | UNKNOWN after 30 min |
| `sat_sb.py 1 300 6` | k′ = 1 control | FEASIBLE in 4 s, checked exactly |
| `sat_sb.py 2 600 2 1` | one class of O₂ | FEASIBLE in 51 s, checked exactly |
| `sat_sb.py 2 1800 6 2` | two classes, lex-leader symmetry breaking + Hadamard column constraints | **INFEASIBLE in 559 s** |
| `sat_sb.py 2 1800 3 2 nocol` | same without column constraints | **INFEASIBLE in 1319 s** |
| `sat_sb.py 2 1800 3 2 nosb` | same without symmetry breaking | UNKNOWN after 30 min |

The solver results carry no proof certificate. They corroborate the hand proof but do not replace it.

## Reproduce

```sh
python3 -B research/line-system-510-signing-nonexistence/verify.py
```

## Open next questions

Structured versions are in `TASK.json`.
- **Saturated W(7,2) systems with several angles.** These would still reopen k′ = 5 (#2244 §11.3). First step:
  apply the frame lemma (a generator class is a frame) with the angle set left free, and check whether the
  two-class block argument extends.
- **Non-dense pairings** (#2244 §11.4) are untouched and remain the larger lever.

## Credit

The question, the descent proposition, Theorem G and the counts used here are from `line-system-saturation`
(#2244). This package adds the frame reduction, the hand proof and the checks. Prepared for Mark (Matarener)
with substantial Claude (Anthropic) assistance. Apache-2.0.
