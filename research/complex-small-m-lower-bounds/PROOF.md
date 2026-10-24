# The written arguments

Each part is headed by its status, in the words of the README. "Argued by hand" means a written argument that no
person and no proof checker has checked. The setting and the words are those of README section 3: W arrays of 2^m
complex numbers, calls C_v = aI + bX_v (a = (1+i)/2, b = (1−i)/2), free steps by game, and correctness at every
number f of digit columns, where every letter acts the same way on each of the f columns.

## 1. The kept-subspace bound

*Status: proved in Lean for the engine game with rational mixing (`engine_lower_bound`). The form below, over any
field and with any linear mixing, is argued by hand.*

**Setting.** Fix a width f and let V be the data space of one array at that width. A program has R ≥ W registers;
registers 1..W start with the inputs y_1..y_W, the others start at 0. Three kinds of step:
- *mixing* (free): replace one register by any linear combination of all registers (copies into scratch, overwriting
  and erasing included; nothing is assumed invertible);
- *a free letter* (free): apply a map b of a group B to one register;
- *a call* (paid): apply an invertible map g to one register.

At the end, for each l, some register (a different one for each l) holds T_l·y_l, the target of array l.

Let N ⊆ V be a subspace with b(N) = N for every free letter b, and let raise(g) = dim(N + gN) − dim N.

**Theorem.** In every correct run, the sum of raise(g) over the calls is at least raise(T_1) + ... + raise(T_W). If
every call has raise at most `cap` and every target has raise at least `demand`, then cap · s ≥ W · demand.

*Proof.* A state gives a linear map M from V^W (the inputs) to V^R (the registers). Let A = M(N^W), the image of the
inputs taken from N, and Φ = dim(A + N^R) − R·dim N: what the state adds beyond N in each register.
- At the start A = N^W ⊕ 0 lies in N^R, so Φ = 0.
- Mixing multiplies M by an R × R matrix acting on registers, and a free letter multiplies one block by b. Both map
  N^R into itself, so they map A + N^R into (new A) + N^R. The new quotient is an image of the old one, so Φ does not
  grow (an erasure may lower it).
- A call g on register r multiplies block r by g. Call this map D; it is invertible, so dim(DA + N^R) =
  dim(A + D^(−1)N^R). The space D^(−1)N^R is N in every block except block r, where it is g^(−1)N, and it exceeds N^R
  by dim(N + g^(−1)N) − dim N = raise(g) dimensions. So Φ grows by at most raise(g).
- At the end, keep only the W delivering registers. There the image of A is the direct sum over l of
  (N + T_l N)/N, because the y_l vary independently over N. Dropping blocks cannot raise a dimension, so
  Φ ≥ Σ_l raise(T_l).

Φ starts at 0, ends at least at Σ_l raise(T_l), and grows by at most raise(g) per call. ∎

In the Lean form, the free letters are the engine's shifts, address maps and phases, mixing takes a rational matrix,
and correctness is required at every width (`GLiveKernel`). The one step that uses the mixing, that it maps N^R into
itself, needs only that N is a complex subspace; so the same proof works for complex mixing. That last sentence is
argued, not in Lean.

## 2. The hook: kept, its cap, and the demands

*Status: kept and cap proved in Lean at every block size (`hook_kept`, `hook_cap`); demands 8 (block 2) and 224
(block 3) proved in Lean; the block-4 demand 86,592 checked by computer, with the split into 16 equal character
blocks argued by hand.*

At block m and width f = j + 2 write the data space of one array as V ⊗ V^(⊗(j+1)), V = C^(2^m), and keep only its
part V ⊗ Λ^(j+1) V (every letter acts the same on each column, so it keeps this part). The hook is

  N = span{ e_x ⊗ e_T : T a (j+1)-subset of addresses, x in T }.

- *Kept.* A free letter inside one array sends each address x to one address π(x) and multiplies by a number c(x),
  the same in every column. It sends e_x ⊗ e_T to a multiple of e_π(x) ⊗ e_π(T), and π(x) lies in π(T). So N is kept
  by every shift, every address map (not only the affine ones) and every diagonal phase.
- *Cap.* A call dir(z) pairs each address a with a + z. For each pair and each j-subset w, the vector
  e_a ⊗ (e_a ∧ e_w) − e_(a+z) ⊗ (e_(a+z) ∧ e_w) lies in N and its image stays in N. These vectors have disjoint
  supports (the w that contain both a and a + z give nothing), so they span a subspace of N of dimension
  dim N − (2^m/2)·C(2^m − 2, j) that the call keeps inside N; hence raise(dir z) ≤ (2^m/2)·C(2^m − 2, j). At block 3 (j = 3) that is 280 − 200 = 80; `verify.py` builds the 200 vectors
  exactly over the Gaussian integers for all 7 directions, and checks that 80 is attained. (Lean proves the formula
  at every block by its own route.)
- *Demand.* raise(C^(⊗m)) is the rank of the block of C^(⊗m) acting on V ⊗ Λ^(j+1) V from N to its complement. At
  block 2 it is at least 8 (Lean, `dem2`). At block 3 the block is 280 × 280 and its rank is at least 224: the
  characters of F_2^3 (the shifts commute with the kernel) split it into 8 blocks, each of rank at least 28 (Lean, `dem3`).
  At block 4 the same split gives 16 blocks; one has rank at least 5,412 by a certificate checked by computer (a
  second block was checked too), and that all 16 have that rank is argued by hand. So the demand is at least
  16 × 5,412 = 86,592.

**Consequences.** With the theorem of section 1: block 2 gives 8W ≤ 4s, so s ≥ 2W; block 3 gives 224W ≤ 80s, so
s ≥ 14W/5; block 4 gives 86,592W ≤ 27,456s, so s ≥ 41W/13. At block 3, a run of two calls on one array raises the
hook by at most 144 < 160 (136 exact vectors, checked by computer), so a grouped call of rank 2 also fits the bound.

**The widened game** (every address permutation and every phase pattern free). *Status: argued by hand; three AI
reviewers upheld it (one re-derived the bound against the Lean engine, one checked keptness exactly for 199 free
steps including Toffoli, CCZ and controlled-S, one redid the numbers).* The kept bullet above covers every
permutation and every diagonal, and nothing else changes, so 14W/5 and 41W/13 hold there too.

## 3. Complex mixing and Harvey's B-calls

*Status: argued by hand, not checked by a person. The numbers it uses are the ones proved in Lean in section 2.*

- *Complex mixing.* Section 1's proof uses only that mixing is linear and maps N^R into N^R, which holds for complex
  coefficients. So 2W and 14W/5 hold with complex mixing.
- *B-calls.* B = (1 − i)·S·C·S with S = diag(1, i). A B-call along an axis at width f is (1 − i)^f times a C-call
  between two diagonal maps (S on that bit, in every column). For invertible diagonals D_1, D_2 (which keep N) and a
  nonzero scalar λ, raise(λ D_1 C D_2) = dim(D_1^(−1)N + C D_2 N) − dim N = raise(C). The same holds for the target
  B^(⊗3) = (1 − i)^3 S^(⊗3) C^(⊗3) S^(⊗3). The program at width 5 is a fixed linear program, so section 1 applies
  at that one width, which is all the block-3 proof uses. So 4 arrays at block 3 need at least 12 B-calls too.

## 4. One array needs m calls

*Status: argued by hand, not checked by a person. AI reviewers re-derived the general form in two rounds; the
single-array support count was re-derived by one AI reviewer.*

**Without scratch** (David Harvey's single-array programs P_M0 A_i1 P_M1 ⋯ A_ig P_Mg, with any free steps that send
one address to one address). Follow one input basis vector e_x. A free step sends a basis vector to a multiple of
one basis vector; a call sends it to a combination of at most two (at width f, of at most 2^f). After g calls,
e_x has spread to at most 2^g addresses (2^(gf) at width f). Every column of the target has all its entries nonzero:
the entries of B^(⊗m) are ±1, and those of C^(⊗m) are a^(m−d) b^d with d the distance between the two addresses.
So 2^g ≥ 2^m and g ≥ m, at every width, width 1 included.

**With scratch and mixing**, in every game whose free letters have at most c nonzeros in each column, with c not
depending on f. The output of array l is a sum over the paths through the program, with fixed coefficients, of
words in the letters; the number of paths does not depend on f. A path with j calls and k free letters gives an
operator with at most c^k 2^(jf) nonzeros per column. If every path from input l to output l had at most m − 1 calls,
the coefficient of input l in output l would have at most (number of paths)·c^(k_max)·2^((m−1)f) nonzeros per column,
fewer than the target's 2^(mf) once f is large. So some path has at least m calls, and one array needs m calls.

This needs correctness at large f. At width 1, one zero scratch array makes C^(⊗3) free: copy the array into the
scratch, shift the copy by e_i, replace the array by a·(array) + b·(copy), for i = 1, 2, 3. The result is
C_(e_3) C_(e_2) C_(e_1) = C^(⊗3) at width 1, but at width 2 it is a·I + b·(X_v ⊗ X_v) per direction instead of
C_v ⊗ C_v. *Checked by computer* (`verify.py`, part `width`: equal at width 1, all 4,096 entries differ at width 2).

## 5. Block 3 without phase letters: s ≥ 3W for every group of address maps

*Status: argued by hand, not checked by a person; one AI reviewer re-derived it and recomputed the certificate with
its own exact code. The certificate's numbers are checked by computer here (`verify.py`, part `face3`).*

**Statement.** In the game with calls, shifts, any complex mixing with scratch, and address maps from any subgroup H
of GL(3, 2), but no phase letters, every unit for W arrays at block 3 uses at least 3W calls.

*Proof.*
- *The group.* The calls dir(z) and the shifts X_a generate an abelian group A (every element is a polynomial in the
  shifts). An address map h is not in A unless h = 1, and h^(−1) dir(z) h = dir(h^(−1) z), h^(−1) X_a h =
  X_(h^(−1) a). So the letters generate the semidirect product A ⋊ H. A program right at every width is an identity
  in the group algebra C[A ⋊ H].
- *Trading address maps for arrays.* C[A ⋊ H] is a free right C[A]-module with basis H. Left multiplication gives an
  injective algebra map ρ into n × n matrices over C[A] (n = |H|), with ρ(a) = diag_h(h^(−1) a h) for a in A and
  ρ(h′) a permutation matrix. Apply ρ to every step. Each register becomes n registers; a call dir(z) becomes n
  calls dir(h^(−1) z), one on each copy; a shift becomes shifts; an address map becomes a permutation of registers,
  which is mixing. The result is a program with no address maps for nW arrays with nM calls, in which array (l, h)
  is owed h^(−1) K h = dir(h^(−1) e_1) dir(h^(−1) e_2) dir(h^(−1) e_3): the kernel in another basis.
- *The certificate.* At width 3 take the antisymmetric part Λ³(C^8), which every letter keeps, and N = the span of
  the 24 *face* triples (three addresses that agree in one bit). Shifts and every diagonal map keep N. For every
  direction, raise(dir z) = 8; for every basis b of F_2^3, raise(K_b) = 24 (exact ranks over Q(i)).
- *Count.* Section 1 on the new program gives 8·nM ≥ 24·nW, so M ≥ 3W. ∎

**Scope.** Pauli Z phases and scalars do not break it. The engine's phase letters do: S·dir(e_1)·S is a scalar times
a Hadamard on one bit, a product of S phases gives CZ, and conjugating CZ by a Hadamard gives a CNOT, an address map.
Then ρ produces address maps inside the new program, and they leak out of N (`verify.py` checks that a CNOT raises N
by 8). Without address maps, phase letters alone also give 3W at block 3 (argued by hand). So a block-3 saver must
use address maps and phase letters together. Harvey's §7.4 model has neither, and his §6 relabellings with C-calls
fall under this section; his §6 B-calls along relabelled axes bring phases, and there only section 2's 14W/5
applies.

## 6. W + m and 2W in every game with bounded free steps

*Status: argued by hand, not checked by a person. One AI reviewer re-derived 2W line by line and checked its key
orthogonality fact with its own code over a wider set of free steps; one AI reviewer upheld the trace-limit version
of W + m and reproduced its numbers. Below is the outline of the written proofs.*

**Setting.** Free letters have at most s_0 nonzeros per row and column, each of modulus at most c_0, independent of f
(this includes address maps, phases, Toffoli, controlled-S and maps that mix neighbouring digit columns). A unit is
a straight-line program u_k = D_k c_k, c_k = Σ_(i<k) B_ki u_i + γ_k, with outputs K e_l = A_0^(l) + Σ_k A_k^(l) u_k,
where D_k are calls and all coefficients are fixed combinations of free words. It must be right at infinitely many f.

1. *Support growth gives orthogonality.* Every entry of K has modulus N^(−1/2) (N = 2^(mf)), and a word with at most
   m − 1 calls has at most C·2^((m−1)f) nonzeros per row. Hence, for free words c, c′ and such a word w,
   |tr((cKc′)* w)|/N ≤ C′·2^(−f/2).
2. *The trace limit.* τ(y) = lim tr(y_f)/N along an ultrafilter over the widths is a trace; its GNS completion gives a
   finite von Neumann algebra. Let H_k be the closure of the words with at most k calls and H_top the closure of
   span{cKc′}. By step 1, H_top ⊥ H_(m−1). The projections onto these spaces commute with multiplication by free
   words on either side.
3. *Top layer.* Project the output identities onto H_top. Only calls that end a chain of m calls survive, and only
   contents that start one. If s = W + m − 1, this leaves K·I_W = 𝐀 Z Γ with W × W matrices; direct finiteness of the
   algebra makes all three invertible. (With s = W + m − 2 there are only W − 1 surviving calls, which is impossible:
   s ≥ W + m − 1 for every W.)
4. *Next layer* (W ≥ 2). Project instead onto H_(m−1) ⊖ H_(m−2). K and the inputs vanish there; using that 𝐀 is
   invertible, the last path part reaching the top is forced into H_(m−2), so its top part is 0, against step 3.
   So s ≥ W + m.
5. *2W.* The same projections, with H_1 ⊖ H_0 as the next layer: every single call is orthogonal to the free words
   (its entries have modulus 2^(−f/2)), so the next-layer path matrix is triangular with unitary diagonal, hence
   invertible. Then the next-layer equation reads 𝐁·𝐆 = 0 and the top equation K·I_W = 𝐁·(…)·𝐆, with 𝐁 of rank at
   least W and 𝐆 of rank at least W. Sylvester's rank inequality in the finite algebra (Murray and von Neumann)
   gives rank 𝐁 + rank 𝐆 ≤ s, so s ≥ 2W.

At block 2 this gives s ≥ 2W, the plain cost, in every such game. At larger m it adds to W + m only when W > m.

## 7. From block 4 on: 2.9447 calls per array in the engine game

*Status: argued by hand from exact computations, not checked by a person; two AI reviewers reproduced every number
with their own code, and Maximilian Lutz checked it independently (#4643).* The block-4 hook is carried upward
through projections between the frame graphs of the engine, controlled by a coupling argument; the exact values are
834,241/278,850 = 2.99172 at block 5 and 1,188,222/399,685 = 2.97290 at block 6, and the bound stays above 2.9447 at
every block. Its inputs are the exact cap a_1 = 27,456 and lower bounds on what two, three and four moves in
independent directions do to the block-4 hook: a_2 ≥ 48,576, a_3 ≥ 68,320 and a_4 ≥ 86,592 (a_1 and a_4 as in section 2). For a_2 and
a_3, part `depth` of `verify.py` splits the hook over the address bits the moves leave untouched, which turns each
into ranks of at most 280 × 280 that it computes modulo a prime (a lower bound over Q(i)), and it recomputes
834,241/278,850 and 1,188,222/399,685 from that profile; two stored minor certificates, checked on all 16 characters,
are author evidence (`author-evidence/check_mj.c`). The written proof is
`author-evidence/induction-across-block-sizes.md`, an unchanged copy of the file of my repository named in
SOURCES.json, headed by the corrections its AI reviewers asked for; none of them touches this bound. The projections
use the engine's frames, so nothing here carries it to the widened game; there the bounds at blocks 5 and 6 are 62/29
and 63/31 (checked by computer).
