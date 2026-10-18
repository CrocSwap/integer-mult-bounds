# Rank-8 rigidity on the admissible P104 units

Notation, equations (E), (1), (2), (E0), (E2), (E4) and Lemmas 2–8 are those of PR1212
(`research/complex-rank8-decoder-rigidity/PROOF.md` at head `57099cb5`). Finite facts marked
**[X]** are recomputed by this package's `verify.py` (check id `X`). Facts marked **[1212: X]** are
PR1212's checks, which `verify.py --pr1212-dir` replays from blob-pinned files.

**Theorem.** Let L be one of the 896 admissible P104 units: P112 minus a frame of type (1,…,1) relative to
FRAME0. Let K be an L × L matrix over a field of characteristic 0 with rank K ≤ 8 that satisfies (E). Then
K = D (2 G_L) D⁻¹ for an invertible diagonal D.

**Corollary.** In the E-graph model, every decoder with exactly eight costly terms on an admissible P104 unit
has cst ≥ 56. This is PR968's floor at p = 16, reached through PR1212's §8 verbatim. PR717's P104 decoders,
which lie in this orbit **[1212: G.pr717-p104-orbit]**, attain it.

By PR1212 §10 transport, the stabiliser of FRAME0 is transitive on the 896 admissible frames
**[1212: G.frame-orbits]**. It therefore suffices to treat PR1212's representative, P112 minus the frame
`DEAD` with pivot `PIVOT` (both listed as root vectors in `verify.py`) **[unit.live, unit.admissible-type,
pr1212.unit-vectors]**.

## Inputs that already hold

Relative to this pivot there are 22 complete live classes, four classes with two live rows, and two empty
classes **[unit.class-profile]**. PR1212 §10 records that three of its four finite inputs hold here:

- **(I2)** zero exclusion (Lemma 8) **[1212: G.P104-11111111.zero-exclusion]**;
- **(I3)** the Lemma 5 group witnesses for every complete class **[lemma5.group-witnesses;
  1212: G.P104-11111111.class-witnesses]**;
- **(I4)** every block carries a complete live class **[lemma6.blocks-and-gluing]**.

Only (I1) fails: eight live lines lie in two-row classes, and there Lemma 5 leaves a one-parameter family
**[control.in-class-not-forced]**.

## Step 1: the complete classes

Lemma 5 applies to each of the 22 complete classes. It needs only (I2), (I3) and the class's own
equations. Lemma 6 applies to the set of complete classes. Its proof uses only complete classes:

- the gluing equation (5) between complete classes C, C′ in distinct blocks through {k, k′};
- for two classes in the same block, a complete class in one of the two other blocks through {k, k′};
- the cocycle in the block of each triple.

All three exist by (I4) **[lemma6.blocks-and-gluing]**. Lines outside the complete classes play no role. So there are nonzero
g_f (f ∈ F) and d′_j such that for every line j in a complete class and f ∈ T_j:

    a_jf = d′_j ε_jf g_f,      b_jf = 4 (d′_j g_f)⁻¹ ε_jf.                                  (6)

## Step 2: Lemma 9 (propagation)

**Lemma 9.** Let i be a live non-pivot line with support T = T_i. Call a pair {k, k′} ⊂ T *witnessed* if
some line j of a complete class has G_ij = 0 and T_i ∩ T_j = {k, k′}. If the witnessed pairs connect T,
then for a nonzero λ_i

    a_if = λ_i ε_if g_f,      b_if = 4 (λ_i g_f)⁻¹ ε_if      (f ∈ T).

*Proof.* Let j witness {k, k′}. Rule (3) with G_ij = 0 gives ε_ik ε_jk = −ε_ik′ ε_jk′
**[lemma9.propagation-connected]**. Equation (E2) in the order a_i · b_j, with b_j from (6), reads

    (4 / d′_j) (a_ik ε_jk / g_k + a_ik′ ε_jk′ / g_k′) = 0.

Multiply by ε_ik ε_jk d′_j / 4 and use the sign identity:

    a_ik ε_ik / g_k = a_ik′ ε_ik′ / g_k′.

So a_if ε_if / g_f is constant along witnessed pairs, and hence on T. Call the constant λ_i. Then
a_if = λ_i ε_if g_f, and λ_i ≠ 0 because (E0) needs a_i ≠ 0.

In the order a_j · b_i, with a_j from (6), the same steps give b_ik ε_ik g_k = b_ik′ ε_ik′ g_k′. So
b_if = μ_i ε_if / g_f. Finally (E0) gives 4 λ_i μ_i = 16. ∎

The proof needs no zero exclusion for i, no in-class equation and no witness inside i's own class. Each
witnessed pair costs one linear equation, so connectivity is exactly what is needed. With every witness at
one column of T removed, a 2-dimensional family survives **[control.disconnected-not-forced]**. As an
algebra cross-check, `verify.py` builds the witnessed equations (E2) from (6) for random rational g, d′. On
both a_i|T and b_i|T they have rank 3, with kernels ε_i ∘ g and ε_i / g **[lemma9.solution-line]**.

**Finite input.** On this unit all eight two-row lines have all six pairs of T witnessed, with 40 witnesses
each **[lemma9.propagation-connected]**. The non-gauge two-row solution of the control satisfies every
in-class condition. It fails 28 of the 40 witnessed equations for one of its rows
**[control.cross-block-rejects]**.

## Assembly

Steps 1 and 2 put every live non-pivot line into PR1212 §7's form, with d′_i = λ_i for the two-row lines.
PR1212 §7 then applies verbatim and gives K = D (2G) D⁻¹. An exact rational control checks the assembly on
all 104 live lines **[assembly-control, control.perturbed-fails]**. ∎

## Remarks

- Lemma 9 is more general than the use made of it here. It needs only a set of lines already in form (6)
  that witnesses a connected pair graph, whatever their classes. It can be iterated, since propagated lines
  become witnesses. The work on another unit is in Step 1, which needs (6) on enough classes to fix g.
- Lemma 9 is linear in a_i and b_i. The only field facts it uses are division by 4 and by the nonzero
  g_f, d′_j. Step 1 inherits PR1212's argument, which holds over any field of characteristic 0
  (PR1212 §9).
