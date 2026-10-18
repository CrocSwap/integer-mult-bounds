# Kernel proof of the classical complementary-block nullity identity

This is an independent proof and executable audit of a classical linear
algebra identity, not a new theorem. Douglas Colkitt's
`research/kappa-nine/MIXED-RANK-TEST.md` already gives a valid Schur-complement
proof of the local invertibility implication it needs. We corroborate that
implication with a kernel argument and rectangular/degenerate block coverage.

## Identity over any field

Let A be an invertible n-by-n matrix over a field F and B=A^-1. Choose any
sets I of output indices and J of input indices, including empty or full
sets. Complements are within {0,...,n-1}. The identity is

```text
nullity A[I,J] = nullity B[J-complement,I-complement],
rank A[I,J] - rank B[J-complement,I-complement] = |I|+|J|-n.
```

Here nullity means dimension of the right kernel. Thus the domain
dimensions in the first identity are |J| and n-|I|, respectively. Forgetting
this difference gives a wrong rank equality for rectangular blocks.

Embed a vector x in F^J into F^n by zeros outside J. It belongs to the first
kernel exactly when Ax vanishes on I, which says y=Ax is supported in
I-complement. Moreover By=x vanishes on J-complement, so y belongs to the
second kernel. Conversely, embed a vector y in the second kernel by zeros
outside I-complement. Then x=By is supported in J, and Ax=y vanishes on I.
These maps are linear and inverse to one another because AB=BA=I. They
are therefore an explicit kernel isomorphism. Rank-nullity gives the
displayed offset. No characteristic restriction, symmetry, positive form,
or invertibility of either subblock is required.

## The exact mixed-rank application

In the source note, n=6 and I=J={0,1}. Write

```text
A = [X Y; Z D],       B = A^-1 = [P Q; R S],
```

where X,P are two-by-two and D,S four-by-four. The classical identity gives

```text
rank X = rank S - 2,
rank P = rank D - 2.
```

Thus the source's hypotheses rank D=rank S=4 imply rank X=rank P=2.
Both complement hypotheses matter for the two conclusions: for
A=[[0,1],[1,1]], D=[1] is invertible but X=[0] is singular, while the
upper-left inverse block is [-1]. The original note supplies both
hypotheses through its regular-color pattern, so there is no flaw to fix.

The source's literal rational six-by-six control is read as an AST literal
without executing its predecessor code. Independent Fraction row reduction
reconstructs its inverse, checks both matrix products, and agrees with the
pinned source receipt. Its ranks (X,D,P,S) are exactly (2,4,2,4). The six
regular two-by-two restrictions of each of A and B also have the original
rank-one values. This corroborates the actual example used by the note.

For this same matrix, the executable kernel method checks all 64*64=4,096
row/column subblocks, including empty/full and rectangular blocks. For every
kernel basis vector it explicitly embeds, transports, checks the required
support and applies the inverse transport. It also checks rank-nullity and
stores a deterministic digest of all those maps and the full rank histogram.

## Separate exhaustive evidence over F3

The finite engine enumerates all 3^9=19,683 three-by-three matrices and
retains all (27-1)(27-3)(27-9)=11,232 invertible ones. It computes inverses
by the cofactor/adjugate formula and checks both inverse products. For every
matrix it visits all six nonempty proper row subsets and all six nonempty
proper column subsets: exactly 404,352 complementary-block comparisons.

These blocks have at most two rows and columns. Their ranks are computed
directly from entries and two-by-two minors, independently of the rational
row reduction used for the source example. Every nullity and rank identity
passes. The receipt records complete rank/nullity histograms, a deterministic
trace digest, and a concrete counterexample to forgetting to exchange the
row and column complements in the inverse. The census supplies bounded
evidence; the preceding kernel argument proves the general statement.

## Boundary

This audit verifies the classical algebra used in the local block argument.
It does not rederive the Fano support/color hypotheses, replay the seven
three-exception exclusions, or exclude any of the surviving four-exception
patterns or 103 global branch representatives. It changes no supplier,
paid profile, selected kappa, compiler, native admission or analytic claim.
No Lean or other proof assistant was run; the general proof is written
mathematics supported by exact finite executable checks.

Original application: Douglas Colkitt, with OpenAI Codex assistance,
Apache-2.0. This audit: @woklerx with substantial OpenAI Codex assistance
in proof, implementation, validation and writing; Apache-2.0.
