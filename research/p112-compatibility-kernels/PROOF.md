# Exact restriction-kernel evaluation

This contribution was produced by Nick Petalas. Apache-2.0.
The census, decoder theorem and scientific receipt are Philipp / mightyOil's
[PR1325](https://github.com/CrocSwap/integer-mult-bounds/pull/1325).
Binary elimination and rank-nullity are classical. PR1325's `independent.py`
already computes nullities by stacking equations in nine coefficient
coordinates. No priority for that method is claimed. The new contribution is
direct restriction of bit-string basis rows as an exact, faster evaluator
preserving the primary command's complete scientific object and ordered digest.

## The replacement identity

Let V be a binary vector space of bit strings of length n. Let g_1,...,g_d
be an independent basis. For a bit mask M, restriction to M is the linear map

```text
R_M : V -> F_2^n,     v -> v & M.
```

Its matrix has rows g_i & M. Therefore

```text
dim {v in V : v & M = 0} = d - rank_F2(g_i & M : 1<=i<=d).
```

The predecessor constructs that kernel by filtering every vector in V and
takes log_2 of the resulting cardinality. A binary vector space of dimension k
has exactly 2^k elements, so both methods return exactly the same integer.
The restriction images may be dependent even when the original basis is
independent. Elimination must occur after restriction; subtracting the number
of nonzero restricted basis vectors would be wrong.

For each plane with canonical generators x,y, the predecessor tests
`not z & (x|y) & conflict[a][k]`. Choose
`M=(x|y)&conflict[a][k]`. For its single-vector census choose
`M=z&conflict[a][3]`. These are exactly the two uses replaced in `fast.py`.
No predicate, selected mask or plane representative changes.

## Complete output preservation

The implementation retains each source geometry, pairing, support and span
constructor. It visits the same sorted spaces, the same canonical plane test
`y < x^y`, the same three anchors and the same partner order. Each dimension
tuple is equal by the identity above. Consequently every census increment and
every canonical byte fed to the ordered plane digest agrees.

The source's real-span, code-dimension and zero-cost checks remain. Every
decoder witness, nonconstant example and all six rejection controls are
retained, in their original order. The new orchestration calls the pinned
source's `decode` and `check_identity` functions. The complete returned object,
including source hashes, is compared with the unchanged source certificate.
The CLI prints the identical scientific success line. Exclusive `--write`
creation produces the same sorted, indented scientific JSON and rejects
overwriting an existing file. These statements concern preservation of the
source contract; they are not independent validation of the decoder theorem.

## Exact restriction work

The three coordinate spaces have 256 elements and dimension eight; the extra
space has 512 elements and dimension nine. For each of the 32,385 planes,
the source masks 256+256+512 partner vectors. Its 765 single-vector queries
each mask 512 vectors. Thus it performs

```text
32385*(256+256+512) + 765*512 = 33,553,920 vector restrictions.
```

The replacement masks 8+8+9 basis rows per plane and nine per single query:

```text
32385*(8+8+9) + 765*9 = 816,510 basis-row restrictions.
```

This removes 32,737,410 restrictions in those queries. It introduces bounded
binary elimination and builds four bases once. The calculation is not a total
instruction count or an asymptotic multiplication bound. The verifier counts
all 97,920 replacement queries and their masked basis rows during the complete
replay. Timing measures the complete CLI, including unchanged work.

## Bounded conformance

The conformance checker enumerates all 67 subspaces of F_2^4 and all 16 masks,
for 1,072 cases. Its independent oracle counts literal vectors in each kernel.
Another 320 fixtures cover basis dimensions zero through nine and 112-bit
strings, again enumerating every vector. Five direct boundary controls cover
the zero space, zero restriction, injective restriction, dependent restricted
images and bit 111. The unchanged complete scientific object and digest are
also compared. Quantified correctness follows from rank-nullity, rather than
extrapolation from these fixtures.

## Limits

The evaluator is opt-in and tied to the exact retained source bytes. Its
orchestration duplicates the source's contract and fails the source hash if
that contract changes. The kernel routine assumes an independent basis of
at most nine rows. Source construction and explicit dimension checks enforce
that premise. This is a finite evaluation improvement. It supplies no new
decoder floor, physical COPY word, paid histogram, supplier admission, kappa
or complete multiplication theorem.
