# Correlated helper constraints are funded within matching boundary groups

**Exact source-scoped signed-moment obstruction, for `0 <= kappa <= 1/100`.**
This strengthens the coordinate-zeroing theorem in `PROOF.md` by allowing
arbitrary scalar linear constraints within each group of helpers having the
same literal entrance and exit charts. It does not change the native source,
admit a new supplier, or discharge any foundational assumption.

## 1. Precisely quantified class

Use the exact #7481 native word pinned in `SOURCES.json`, and the original
assignment of all 468 main-free MOVE positions in `ASSIGNMENT.json`. Every
main input remains arbitrary. Partition the 1,101 helper inputs into the 187
groups with identical pairs `(initial frame ID, final frame ID)`.

For each group G of m_G helpers, choose an arbitrary scalar input subspace
U_G of a characteristic-zero coefficient field to the power m_G. The scalar
constraints are uniform across complete array coordinates. Different groups
and all main inputs remain independent. Write

    d_G = codim(U_G),     W_G = annihilator(U_G).

Thus `dim(W_G)=d_G`. These are ordinary scalar constraints across coframed
helper fields, not arbitrary address-dependent operators or correlations
between groups or with main inputs. Complex scalar constraints are permitted:
all native coefficient rows are rational, so their ranks are unchanged by
extension to any characteristic-zero field.

Retain all native scalar operations, their chronology, frames and owners.
Grant omission of an original MOVE whenever its entire latent row vanishes on
the restricted input space. Grant every basis conversion, zero-field transfer,
owned allocation, storage and ordinary service for free. No changed MOVE rank,
source-contact rewrite or new productive boundary is included.

Each group has one common native target operator and one target rank R_G.
The source replay proves that every helper's final latent row is its own input,
and that no helper leaks into the main outputs. Restricting U_G therefore
retains at most `m_G-d_G` independent productive directions of that same target
type. Debit exactly `d_G * R_G^(1-kappa)` from productive credit. This is the
favorable complete-field accounting convention of the declared replacement
class; it does not grant a new target split or prove an all-column compiler.

The theorem is that even this optimistic restriction cannot increase the
complete target-minus-paid moment for `0 <= kappa <= 1/100`.

## 2. Assign each removable MOVE to a necessary annihilator

The exact source has 6,279 MOVEs. Of these, 5,811 contain a nonzero main
coefficient, so none can vanish while the main inputs remain independent and
arbitrary. The other 468 have only helper support. Assign each to the boundary
group containing its charged helper from `ASSIGNMENT.json`.

Let v_e be that MOVE's latent coefficient row projected onto its assigned
group G. This projected row is nonzero: the originally charged helper has a
nonzero coefficient. If e becomes zero on the entire restricted input space,
independence of the groups implies `v_e in W_G`. If S_G is the set of removable
MOVEs assigned to G, then

    rank_char0({v_e : e in S_G}) <= d_G.

It is enough to prove the following weighted rank inequality for every subset
S of every assigned row family:

    sum(e in S) (r_e/R_G)^(1-kappa) <= rank_char0({v_e : e in S}).

Here r_e is the original paid rank. The source-bound certificate checks
`1 <= r_e <= R_G <= 9`. The assignment is a proof device; it is not a new
algorithm or a claim that the native rows have only one group's support.

## 3. Exact rational price envelope

For `0 <= kappa <= 1/100` and `1 <= r <= R <= 9`,

    (r/R)^(1-kappa)
       = (r/R) * (R/r)^kappa
       <= min(1, (1023/1000) * r/R).

The only nontrivial numerical inequality used is

    9 * 1000^100 < 1023^100.

This integer comparison proves `9^(1/100) < 1023/1000`. The separate upper
bound 1 follows from `r/R <= 1` and the positive exponent. There is no floating
root, sampled kappa grid, or uncertain sign in this argument.

Define the rational upper weight

    w_e = min(1000 R_G, 1023 r_e) / (1000 R_G).

It remains to show `sum(e in S) w_e <= rank_char0(S)` for all S.

## 4. A small certificate covers every subset

There are 102 groups receiving assigned rows. The exact rational discovery
decomposes their row families into 430 components: 409 singletons, 12 pairs,
four triples, three blocks of size four, one block of size five and one block
of size six. Only six boundary groups need a nontrivial partition. Their event
lists are recorded in `GROUP-COMPONENTS.json`; all undeclared groups are treated
as singleton components. The verifier checks complete, duplicate-free event
coverage against the actual source-derived assignment.

The independent verifier reconstructs all projected rows directly from the
native word over the prime field F_65521. Every scalar denominator in the source
is checked invertible. It does not consume a supplied matrix or an author's
rank table. For each group, it checks that the component spans form a direct
sum over F_65521 by comparing the sum of their ranks with the rank of the whole
group. For every nonempty subset S_C of every component C, it then verifies
the exact integer inequality

    sum(e in S_C) min(1000 R_G, 1023 r_e)
       <= 1000 R_G * rank_F65521(S_C).

There are exactly 612 such nonempty subset checks. The largest component has
six rows, so no large-domain cutoff or sampled subset is involved.

For any subset S of a complete group, modular direct-sum additivity now gives

    sum(e in S) w_e
       <= sum(C) rank_F65521(S intersect C)
        = rank_F65521(S)
       <= rank_char0(S).

The last inequality is essential. A nonzero modular minor of the actual
rational coefficient matrix remains a nonzero rational minor, because all
denominators are units modulo the prime. Thus modular ranks are lower bounds
on characteristic-zero ranks. **No modular zero or modular dependence is
promoted to an exact rational identity.** The component partition needs to be
a direct sum only modulo this prime for this proof to work. The originating
exact-Q calculation separately agrees with the complete group ranks.

This proves the required weighted inequality for every subset, and therefore
for every possible annihilator W_G. The passage to arbitrary input subspaces
is a linear-algebra proof; it is not extrapolation from finite input samples.

## 5. Complete signed budget

Applying the inequality to S_G and multiplying by `R_G^(1-kappa)` yields

    sum(e in S_G) r_e^(1-kappa) <= d_G R_G^(1-kappa).

The left side is the paid work optimistically removed from this group's
assigned MOVE positions. The right side is the productive credit lost.
Summing over groups proves nonpositive native signed-moment gain.

The wrapper reconstructs every entry of the exact retained 17-call caller's
target and paid histograms. All caller operations and main targets remain
unchanged. Different restrictions may be chosen in different native calls;
each contributes a nonpositive change, so their sum also cannot improve the
complete invoice. Additional physical entry/exit, storage, phase and ordinary
costs can only make this already favorable budget worse.

## 6. Controls, limitations and next obligation

`subspace_verify.py` rejects a dependent pair falsely partitioned into two
independent blocks and a dependent pair priced above its rank allowance. It
accepts a correctly funded dependent pair and fully priced independent rows.
These controls exercise rank additivity and the funding direction rather than
only source checksums. All substantive checks remain active under `python -O`.

The coordinate theorem retains its wider interval `0 <= kappa <= 1/2`.
The correlated-subspace theorem is asserted only on `0 <= kappa <= 1/100`.
Cross-group correlations, altered main inputs, address-dependent encodings,
changed native operations or frames, new target splits and different productive
boundaries remain outside the result. These are possible new questions, not
routes ruled out by the present certificate. All five foundational assumptions
remain; no unconditional multiplication bound or new complete kappa follows.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
The exact source, caller and predecessor contributors retain all credits in
`SOURCES.json`, `NOTICE` and `inputs/PREDECESSOR-NOTICE`.
