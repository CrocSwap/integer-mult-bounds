# The binary first-pivot quarter law

This scoped counting proof was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

For every ordered pair of idempotents S,T over **F2** with invertible
commutator, exactly **one quarter** of complete uniform headers have both
first pivots nonzero. This is a dimension-uniform first-pivot count. It supplies
no full-guard chain, physical header cover, supplier admission or new kappa.
The theorem is restricted to F2.

This answers one bounded transition-count question left open by MatShep's
[#4762](https://github.com/CrocSwap/integer-mult-bounds/pull/4762) and
codyw912's [#4735](https://github.com/CrocSwap/integer-mult-bounds/pull/4735).
Their factor invariant, split recurrence and the earlier seven-state table
are predecessors, not audit targets. The block reduction below is elementary
background; the contribution is the explicit header count and its proof.

## Statement

Let V be a positive-dimensional finite vector space over F2. Suppose S,T are
idempotents on V and C=ST-TS is invertible. Then dim V=2r and both projectors
have rank r, with r>=2. For a complete header G in GL_(2r)(F2), the first pivots
are the leading entries of G^-1 S G and G^-1 T G. The number of headers on which
both pivots are nonzero is exactly

```text
|GL_(2r)(F2)| / 4.                                      (1)
```

Equivalently, let a be the first column of G and beta the first row of G^-1.
A split satisfies beta(a)=1. Exactly

```text
g(r) = 2^(2r-3) (2^(2r)-1)                              (2)
```

splits have beta(Sa)=beta(Ta)=1. Each has |GL_(2r-1)(F2)| complete-header
extensions. Nonzero and equal-to-one pivots coincide over this field.

No assumption about a preceding commuting pair or Schur deletion is made.
The result covers any ordered pair satisfying the displayed binary hypotheses.
It does not assert that the residual pair after a successful pivot has an
invertible commutator, so (1) cannot be iterated without further work.

## Proof

### Reduce to one compression

Use V=im S direct-sum ker S. In these coordinates write

```text
S = [I 0],    T = [A B],    ST-TS = [0 B].
    [0 0]        [C D]             [C 0]
```

Invertibility of ST-TS forces B and C to be isomorphisms, so the two summands
have the same dimension r. Choose bases with B=I and rename the other blocks.
The top blocks of T^2=T give C=A+A^2 and D=I+A. Thus

```text
S = [I 0],    T = [A       I  ].                         (3)
    [0 0]        [A(I+A)  I+A]
```

Both A and I+A are invertible. The image of T is exactly
`{(z,(I+A)z): z in F2^r}`, so its rank is r. If r=1, the binary scalar A would
have to differ from both zero and one, which is impossible. Thus r>=2.
A simultaneous change of basis bijects complete headers and preserves their
pivot values, so it suffices to count (3).

### Count first vectors and functionals

Put a=(x,y) and N=2^r-1. If x=0 then Sa=0 and admission fails. Fix a nonzero x.
We have

```text
Sa = (x,0),
Ta = (Ax+y, (I+A)(Ax+y)).                               (4)
```

The three values `y=0`, `y=Ax`, and `y=(I+A)x` are distinct, since x, Ax and
(I+A)x are all nonzero. When y=0, the vectors a=Sa and Ta are independent,
because A(I+A)x is nonzero. When y=(I+A)x, the vectors a=Ta and Sa are
independent. Each case therefore gives exactly 2^(2r-2) functionals with all
required evaluations equal to one. When y=Ax, Ta=0 and there are none.

Every remaining y makes a,Sa,Ta independent. To prove this, y is nonzero, so
a and Sa are independent. Suppose Ta=u Sa+v a for binary scalars u,v. Put
t=u+v. Equation (4) implies

```text
y=(t I+A)x,       (t+v)Ax=t(1+v)x.                      (5)
```

The vectors x and Ax are independent: over F2 dependence would give Ax=0 or
Ax=x, contradicting invertibility of A or I+A. Hence (5) forces t=v and
t(1+v)=0. The only possibilities are t=v=0 and t=v=1. These give the already
excluded values y=Ax and y=(I+A)x. This proves the asserted independence.

For each of the 2^r-3 remaining y, specifying the three evaluations to be one
leaves exactly 2^(2r-3) functionals. Summing over all N nonzero x gives

```text
g(r) = N [2*2^(2r-2) + (2^r-3)*2^(2r-3)]
     = 2^(2r-3) (2^r-1)(2^r+1),
```

which is (2). This step uses the binary scalar possibilities in (5); it is
not a proof over general characteristic-two fields.

### Complete the header

Every header gives a split beta(a)=1. Conversely, for such a split the remaining
columns of G are exactly an arbitrary ordered basis of ker beta. Thus the
completion fiber has |GL_(2r-1)(F2)| members, following the split-completion
method of #4735 and the earlier header-count lineage.

There are `(2^(2r)-1)2^(2r-1)` splits in total. Both literal first pivots are
one precisely when beta(Sa)=beta(Ta)=1. Dividing (2) by that total gives 1/4;
multiplying by the common completion fiber proves (1).

## Finite corroboration and reproduction

The standard-library verifier computes observed counts by literal binary
matrix action and vector-functional enumeration. It does not use the proof's
dependent-triple partition for its observed counts.

- It enumerates all 16 binary 2-by-2 compressions and all 512 binary 3-by-3
  compressions. Exactly 2 and 48 respectively satisfy invertibility of A and
  I+A. Every admitted case has respectively 30 and 504 passing splits.
- A separate census fixes S=diag(I_2,0_2) and scans every one of the 65,536
  binary 4-by-4 matrices. It finds 802 idempotents and exactly 12 with
  invertible commutator. All 12 have 30 passing splits. This corroborates
  partners outside the B=I presentation; it is not an enumeration of every
  first S.
- A literal GL4 census scans all 65,536 binary matrices, inverts each
  invertible header and conjugates both requests. Exactly 5,040 of the 20,160
  headers pass the first pivots, agreeing with 30*|GL3|=30*168. It also exhibits
  a first-passing header with a failed second leading minor, so no full-guard
  interpretation is possible.
- Seven controls distinguish the two forbidden scalar compressions, singular
  commutators, nonidempotent partners retaining invertible commutator, the
  zero-vector denominator, missing completion multiplicity and first/full
  guards. All checks use exceptions and remain active under optimization.

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/generic-idempotent-first-guard
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/generic-idempotent-first-guard --check-source-history
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/generic-idempotent-first-guard/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/generic-idempotent-first-guard/verify.py
```

Expected markers are `PASS_GENERIC_IDEMPOTENT_FIRST_GUARD`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
Any CPython 3.12 interpreter may replace the local path. The standalone
verifier reads only its five package files to generate source hashes, writes
no files, imports no predecessor and runs without Git. Its deterministic
stdout receipt binds those five files; no receipt is handwritten or committed.
The registered runner additionally checks historical source metadata.

Universal claims rest on the written proof. Finite corroboration is not a
formal proof or a complete multiplication theorem. No selected scientific
cold replay, native build, Lean or Docker run is claimed. Physical request
compatibility, header selection/emission, reads, dirty return, stock,
precision and the complete consumer bill remain unknown.

All executable domains are fixed: raw matrix domains have at most 65,536
members, vector/functional domains at most 64 members and dimensions at most
six. No recursion, persistent cache, subprocess or network is used. Functions
are under 60 lines. Python allocates during enumeration; these fixed domain
bounds are the managed-runtime deviation from a fixed-allocation discipline.
Warning-strict normal/optimized execution and package validation ran.
No external static analyzer was installed.

## Sources, scope and credit

Canonical base is `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
The selected source-bound orientation passed. Selected conditional kappa remains
60403/20000000. [TASK.json](TASK.json) records the F2 scope and replacement
claim. [SOURCES.json](SOURCES.json) binds historical provenance; there are no
external mathematical inputs or pending-source runtime dependencies.

- MatShep's #4762, head `3b4e0449262b0b1e07b80e009ef71cc0ca5bf816`, supplies
  the complete factor invariant and leaves transition counts open.
- codyw912's #4735, head `4afbea22e79e19d1d65702eb4090d454ee39d967`, supplies
  the binary split recurrence, rank-one invariant and block-centralizer method.
- Mihir Srivastava's #4689, head `3a72fbad148294aa9ca7f900a48dbb10e64232be`,
  supplies the seven residual states for its specified binary initial profile.
- ssafwann's #4678/#4671 supply the sharp-block header counts and sector
  criterion. Nick Petalas's #4597/#4278 and earlier header laws retain the
  ordered Schur and completion lineage credit.
- Ryanson Jonathan, lee-phys, Cinna Davis, source527, commdata2338 and Jose
  Manuel retain the earlier full-guard, dimension, request and normalizer credit.

General commutators of idempotents have a substantial prior literature, such
as Drnovsek, Radjavi and Rosenthal's
[2002 characterization](https://doi.org/10.1016/S0024-3795(01)00533-X).
No global novelty for the block normalization is asserted. The family decision
is narrow and stop after this F2 first-pivot count; it authorizes no unpriced
construction expansion.

## Open next questions

1. What is the successor-state distribution after an admitted generic binary
   first pivot? It would enable an honest second-step count. Start with r=2
   and retain ordered residual types and split multiplicities. The present
   result supplies no successor distribution or repeated quarter law.
2. What replaces the count when the binary commutator has a kernel? This
   covers many actual scalar-Schur residuals. First separate the generic part
   from the singular representation data of #4762. The invertible off-diagonal
   reduction here does not classify that remaining data.
3. Can an actual caller use a fully paid cover informed by this count? First
   pin its field, allowed headers, selection/emission, reads and dirty-return
   costs. A uniform complete-header count supplies none of that physical bill.
