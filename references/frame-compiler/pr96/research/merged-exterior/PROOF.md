# Merged auxiliary exteriors: finite certificate and scope

## 1. Claim

On PR79's unchanged words, data profile, endpoint copies and complex layer,
change only the endpoint frames of selected auxiliary roles, as described
below. The complete recursive profile then has the same width
W = 134,126,064 and rank deficit 1,846,900 as PR79. The accepted bit saving
is 27678860161103/(5·10^17) and

$$
\kappa = 55354656014473/10^{18} = 5.5354656014473\times10^{-5}.
$$

The next bit-saving and κ grid points at denominator 10^18 are rejected.
PR79's complete child list fails the moment at the new bit saving. All
inherited hypotheses stated in PR79's PROOF.md remain assumptions. The claim
is a finite conditional certificate only.

## 2. Moving the exterior into an endpoint edge

We work in the endpoint contract of the pinned upstream Section 4. Every
source, gate and sink carries an exact rational m×m frame. Each restored
auxiliary role satisfies M_out − M_in = I_m. An edge is charged by the
recursive profile of its residual M_head − M_tail. Auxiliary source frames
are free.

Fix an axis h ∈ {23, 25} and one invocation with other-axis line projector
B = vν^T. In the inherited accounting, an auxiliary role pays for the
following residuals:

- its local residuals Δ⊗B, profiled by the unchanged local profiler;
- its entrance from the zero frame to the first frame A_first;
- its cleanup from the last frame A_last to I_h, or side growth if it is an
  output role;
- one exterior E = I − I_h⊗B, profile [h, m−2h].

For readability these use the axis-23 factor order; axis 25 is symmetric.

The exterior is always the role's final residual. In stage one it is the
outer residual from I_h⊗B to the sink I. In stage two (PR29 note,
"Two stages, endpoints and the copy correction") the role starts at
D_0 = E, its gate labels contain E, and E is the exit after cleanup.

Neither change below touches a gate frame, an XOR, or another role.

- **Merged entrance (any role).** Replace M_in and M_out by M_in − E and
  M_out − E. The endpoint identity is unchanged.
  - The first residual becomes Δ_first + E. For stage one this is
    A_first⊗B + E = I − (I_h − A_first)⊗B. Stage two gives the same matrix.
  - The final residual E becomes zero.
- **Merged exit (non-output roles).** The inherited accounting splits the
  final segment, from the last gate frame to the sink, into the cleanup and
  E. Charge it instead as the one residual I − A_last⊗B.
  - Output roles end with side growth, not a cleanup edge, so they keep
    their charge.

In both cases one local transition and one exterior are replaced by a
single residual I − Y with Y = X⊗B:

- entrance: X = I_h − A_first;
- exit: X = A_last.

X is idempotent and has rank r ≤ h. The rank of I − Y is m − r, which
equals the removed rank plus m − h.

## 3. Corner ranks of a complementary projector (Lemma 1)

Let Y = UW^T ∈ F^{m×m} with W^T U = I_r, so Y is idempotent of rank r, and
let M = I − Y. Write ρ(i,j) for the rank of M restricted to rows ≤ i and
columns ≥ j. Then:

$$
\rho(i,j)=\begin{cases}
(i-j+1)-r+\operatorname{rank}U_{<j}+\operatorname{rank}W_{>i}, & j\le i+1,\\
\operatorname{rank}\,U_{\le i}W_{\ge j}^{T}, & j\ge i+1.
\end{cases}
$$

*Proof.* Let G_j be the span of e_j,…,e_{m−1}. For j > i, the identity
vanishes on the corner, so M's corner equals −U_{≤i}W_{≥j}^T. For j ≤ i+1,
take the following steps.

1. M is the projector onto ker Y = ker W^T along im Y = im U. Therefore
   M(G) = (G + im Y) ∩ ker Y for every subspace G.
2. Hence dim M(G_j) = dim(G_j + im U) − r = (m−j) + rank U_{<j} − r.
3. Since G_{i+1} ⊆ G_j, M(G_j) ∩ G_{i+1} = ker W^T ∩ G_{i+1}. Its dimension
   is (m−i−1) − rank W_{>i}.
4. ρ(i,j) is the dimension of M(G_j) after deleting coordinates > i, which
   is the difference of the two dimensions. ∎

The NE pivots of the top-row-first, rightmost-pivot elimination are exactly
the positions where the second difference

$$
\rho(i,j)-\rho(i-1,j)-\rho(i,j+1)+\rho(i-1,j+1)
$$

equals one. Maximal diagonal runs of pivots are the recursive children, as
in the inherited profiler.

## 4. The fixed PR34 basis

The PR34 reversed (23,25) basis gives the physical image of X⊗B the entries

$$
Y_{kl}=X_{\lambda(k),\lambda(l)}\,v_{o(k)}\nu_{o(l)}.
$$

Here λ(k) and o(k) are the local and other-axis coordinates of physical index
k = 25α + β. For axis 23, λ(k) = M_β(α) and o(k) = β; for axis 25 the roles
are swapped. For each local coordinate a, o maps {k : λ(k) = a} bijectively
onto the other axis.

Factor X = U_X W_X^T with W_X^T U_X = I and set U = D_v Û, W = D_ν Ŵ, where
Û_k = (U_X)_{λ(k)}. Then

$$
W^T U = \sum_a (\nu\cdot v)\,W_{X,a}^T U_{X,a} = I.
$$

Every line has v = t + 3·1 > 0 and
ν = t/2 − 5/(3(n+1))·1 with all entries nonzero and ν·v = 1. Lemma 1
therefore gives, with S = λ[0,j) and T = λ(i,m):

- rank U_{<j} = rank X[S, :];
- rank W_{>i} = rank X[:, T];
- rank U_{≤i} W_{≥j}^T = rank X[λ[0,i], λ[j,m)].

The profile is the same for every one of the N/v_h lines, so one profile per
merged edge suffices.

Below the band j ∈ {i, i+1}, ρ is a sum of a function of i and a function of
j, so its second differences vanish. Above the band, ρ depends only on the
sets λ[0,i] and λ[j,m). Pivots there can occur only where a new local row and
a new local column first appear. The certifier evaluates the band and these
at most h² positions. It asserts that every second difference is 0 or 1 and
that there are exactly m − r pivots.

The tests check two things against direct exact elimination of the full
physical matrix I − Y:

- Lemma 1 on random layouts with this bijection property;
- that the identity X = I_h reproduces the inherited exterior profile
  [m−2h, h].

## 5. Exact local ranks (Lemma 2)

The profiler's envelope projector is A = diag(o) + UV^T/d, with U and V
integer matrices of rank at most two. Their rows depend only on whether a
coordinate is in the core, in the cover minus the core, or outside the cover.
Both choices of X therefore have the form

$$
X = \Delta + \sigma UV^T/d,
$$

with Δ a 0/1 diagonal and σ = ±1. Write k for the number of columns of U.

For row and column sets S and T:

- Let P = S ∩ T ∩ supp Δ, S_0 = S∖P and T_0 = T∖P.
- Let C = dI_k + σ Σ_{p∈P} V_p^T U_p.
- Let Z be a basis of ker U_{S_0} and Y a basis of ker V_{T_0}.

Then

$$
\operatorname{rank}X[S,T]=|P|+\operatorname{rank}U_{S_0}+\operatorname{rank}V_{T_0}+\operatorname{rank}(Y^TCZ)-k.
$$

*Proof.* The bordered matrix [[Δ_{ST}, σU_S], [−V_T^T, dI]] has rank
k + rank X[S,T]; this is the Schur complement on dI. Eliminating the |P| unit
pivots of Δ leaves [[0, σU_{S_0}], [−V_{T_0}^T, C]].

A matrix [[0, A], [B, C]] has rank rank A + rank B + rank(Y^T C Z): reduce A
and B to full-rank blocks with invertible column and row operations, then
clear C outside the kernel directions. ∎

All quantities are integer vectors and at most 2×2 determinants, so every
rank is exact over Q. No modular reduction is used.

## 6. Composition

Each axis's selection lists the entrance roles and the exit roles. For each
selected role:

- The unchanged inherited profiler profiles the removed local transitions,
  (0 → first) or (last → I_h). The composer subtracts them from PR79's local
  blocks and asserts the result is nonnegative.
- The role's exterior is removed from the bank N/v_h · R.
- Its merged edge contributes its certified runs, multiplied by N/v_h.

The composer asserts:

- merged rank mass = removed rank mass + (m−h) × number of merged roles;
- total rank = mW − N + L = 77,120,639,900.

Roles, W and the deficit are unchanged.

## 7. Finite bridge

The largest bit child becomes 552 (it was 529). The least D with
575^D > 2·552^D is 17, so:

- the bit halving degree becomes 17 and the product-row coefficient
  17·27 + 20·30 = 1059;
- the row stock p^2000 is replaced by p^2200, with gap
  2200 − (51/25)·1059 = 991/25 > 0;
- the suffix condition becomes b_in^{1−ε} > 8800(log_2 b_in + 8), which still
  holds eventually.

The row degree is a free stock parameter: PR29 used p^47000 and the
structured-bulk assembly p^108000. It enters only the row-product slack and
the eventual cutoffs, not κ. The inherited `validate_bridge` recomputes these
fields from maxchild and W and rejects stale values.

## 8. Scope

The per-role choice uses first-order profile cost and is a discovery
heuristic; only the composed exact profile is claimed. Every other
assumption is inherited unchanged, including:

- the ordered affine residual compiler and all-size recursion;
- routing, prime selection and exact recovery;
- the fixed-tape and analytic transfer;
- the complex layer.

There is no claim of global optimality, a full formalization or a practical
speedup.
