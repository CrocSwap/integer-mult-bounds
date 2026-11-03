# Sharp positive-width horizon from the right-boundary kernel

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Let K be any field, let Sigma be a finite alphabet, and fix finite matrices

```
F in K^(p x D), B in K^(D x q), T_s in K^(D x D) for s in Sigma.
```

The complete residual at word w=s_1...s_f is F T_w B, with the matrices
multiplied in the displayed order. Every input/output role is retained.
The empty word is outside the tested domain. The physical-column model of
zxv's PR5441 uses s=(output column,input column).

Define V_k as the row span of all F T_w with 1<=|w|<=k. Put

```
r = dim V_1, b = rank B.
```

If r=0 or b=0, every positive-width residual is zero. Otherwise set

```
H = max(1, D-r-b+2).
```

Then the residual is zero at every positive width if and only if it is
zero for every word of lengths 1,...,H. Equivalently, any nonzero complete
residual has a literal nonzero entry at a positive width at most H.

For every integer D>=1 and every 1<=r,b<=D, this bound is attained by a
one-symbol example with exactly those ranks. The examples use only zeros
and ones and work over every field.

## Upper bound

If r=0, every word starts with F T_s=0. If b=0, B=0. These cases give the
first assertion, including D=0 and an empty alphabet.

Assume r,b>0. Let W be the left kernel of B, so dim W=D-b. The spaces V_k
satisfy

```
V_(k+1) = V_k + sum_s V_k T_s.
```

If consecutive spaces agree, that space is invariant under every T_s.
It then contains every later positive reachable row.

Suppose the residual vanishes through width H. Thus V_H is contained in W.
If r+b>D, already dim V_1=r>D-b, a contradiction. In this case H=1 and
width one must have a nonzero entry.

It remains to consider r+b<=D. Here H=D-r-b+2>=2. If every inclusion from
V_1 to V_H were strict, then

```
dim V_H >= r+(H-1) = D-b+1,
```

contradicting V_H contained in W. Some consecutive spaces therefore agree
before width H. Their invariance and containment in W prove that every
later residual also vanishes. The reverse implication is immediate.

This proof stops dimension growth at the kernel of the actual right
boundary. PR5441's bound D-r+1 instead budgets growth in the entire
D-dimensional transfer space. The improvement is b-1 widths until the
mandatory minimum positive width one is reached. At b=1 the bounds agree.

No minimum realization, genericity, commutativity, invertibility of the
transitions, numerical separation or characteristic assumption is used.

## Sharpness for every rank triple

First suppose r+b<=D+1, and put L=D-r-b+2>=1. Partition a basis into

```
r-1 dead basis vectors;
L cycle basis vectors c_0,...,c_(L-1);
b-1 unreachable accepting basis vectors.
```

The counts sum to D. The single transition T fixes every dead and
unreachable vector and acts on row vectors by the cyclic shift
c_j T=c_((j+1) mod L). Let the rows of F be the dead vectors followed by
c_(L-1). Let the columns of B be the transpose of c_(L-1), followed by
the transposes of the unreachable accepting vectors.

Then rank B=b. The rows of F T are the r-1 dead vectors and c_0, so r is
the positive seed rank. At positive widths 1,...,L-1 no reachable row
pairs nontrivially with a column of B. At width L the cycle row returns
to c_(L-1), and its accepting entry is one. The first discrepancy is
exactly L=H. The empty-word entry is one too; including width zero would
change the statement and destroy this sharp positive-width example.

If r+b>D+1, take T=I, let the rows of F be the first r coordinate vectors,
and let the columns of B be the last b coordinate vectors. The coordinate
sets overlap, giving a nonzero entry at width one. The ranks are r,b,
and H=1. This completes every admissible triple.

For example D=8,r=2,b=3 gives first discrepancy five. It passes every
width below five, so replacing the final +2 by +1 is false. The earlier
seed-rank-only horizon is seven for this example.

## Scope and credit

The proof is a rank-nullity refinement of classical weighted-automata
reachability. It is not a claim of a new general equivalence algorithm or
general literature priority. Credit zxv's PR5441 for the fixed physical
table, positive-width, full-role and complete-return contract and its
earlier D-r+1 bound. Its proof credits Kiefer and coauthors, Tzeng,
Crosswhite and Bacon, and the repository's independent/inverse register
certificates PR5235 and PR5262. Those results are premises and context,
not scientific replay or audit targets here.

This is an exact finite-representation statement. It does not certify a
width-dependent table, tolerance test, omitted return, actual source-table
extraction, native realization, physical cost, supplier or multiplication
theorem. The cutoff changes neither the transition dimension nor the
cost of testing all physical words below that cutoff. All five selected
framework assumptions remain.
