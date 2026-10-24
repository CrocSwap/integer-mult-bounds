# A sharp block-four coordinate-face obstruction

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof with an exact finite certificate. No new κ.** At block size
four, let a paid call in direction `v != 0` apply
`C_v = (1+i)I/2 + (1-i)X_v/2`, where `X_v e_x = e_(x+v)` on
`V = C^16`. Write `wt(v)` for its Hamming weight in the specified coordinates.
A program delivering `K y_l` for each of `W` independent arrays, where
`K = C_e3 C_e2 C_e1 C_e0`, satisfies

```
sum over paid calls of wt(v) >= 4 W.
```

The program may use arbitrary complex register mixing, zero scratch, copies,
erasures, arbitrary diagonal address operators, translations and coordinate
permutations for free. Every address operator acts identically on all digit
columns. Inverse calls have the same weight. Correctness at digit width five
already suffices for the theorem. Thus every all-width unit in this game obeys
it. For coordinate calls alone the exact minimum is `4 W`, attained by applying
four coordinate calls independently to each array.

The certificate also has a sharp limitation. Its exact call contribution is
`112 wt(v)`, while its target contribution is 448. A weight-four direction
has contribution 448. Consequently this certificate, used alone through the
kept-subspace inequality, gives only `s >= W` when every nonzero direction has
unit price. It does not exclude the unrestricted block-four open shapes.

## What is new, and what is inherited

Jacob Alan Sussman's [PR #4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628),
at `ee4fd87f064017c23e5a86fc1dcfe0a5237caed3`, supplies the kept-subspace method,
the block-three face certificate, and the relevant small-unit questions. See
[PROOF.md sections 1 and 5](https://github.com/CrocSwap/integer-mult-bounds/blob/ee4fd87f064017c23e5a86fc1dcfe0a5237caed3/research/complex-small-m-lower-bounds/PROOF.md).
The method originates in eumemic's #288 certificate method and Swapnil Jain's
P1/P2 as credited by Sussman. These are cited predecessors; their executables
and reported ranks are not replayed here.

The new result is the block-four fifth-exterior-power certificate, its exact
compression Gram identity, the direction-weight ranks and the resulting
weighted lower bound with its sharp failure for unit-priced diagonal calls.
Sussman's block-four commutative-slice result allows every direction but has
no phase letters. This result allows arbitrary diagonal phases and restricts
the cost conclusion by direction weight. Neither statement is presented as
containing the other's entire game. General XOR-linear address maps are absent
from this theorem. They need not preserve its certificate.

This is a changed `complex-rank-shape-decoder` scope. It gives a decision about
a small complex-unit search alphabet, rather than a paid supplier profile.
The card's historical first command was attempted and failed with
`KeyError: 'complex_profile'` against the changed selected-record schema.
The current baseline command was also attempted and stopped at an omitted
sparse-checkout input, `research/fresh-helper-thinned/PROOF.md`. Neither run
is claimed as scientific verification or repaired by this package. The selected
record remains κ = 60403/20000000. The proof below is independent of that ledger.

## Proof

### The face space

Work inside the alternating subspace `exterior^5(V)` of digit width five.
It has dimension `choose(16,5) = 4368`. For `j in {0,1,2,3}` and `b in {0,1}`,
let `V_(j,b)` be the span of addresses with `x_j=b`, and set

```
N_(j,b) = exterior^5(V_(j,b)),
N = direct sum over j,b of N_(j,b).
```

Two distinct nonopposite coordinate faces intersect in only four addresses.
A five-element subset therefore belongs to at most one face. This proves that
the displayed sum is direct and that `dim N = 8 choose(8,5) = 448`.
For each coordinate `j`, the two faces together have dimension 112.
Translations and coordinate permutations permute these summands. Every diagonal
operator preserves each summand. Therefore every allowed free address operator
preserves `N`. Register mixing sends `N^R` into itself even when singular.

### Target demand and exact Gram identity

Let `H` be the normalized Walsh matrix on four bits,
`H_(x,y) = (-1)^(x dot y)/4`, and let `U = exterior^5(H)`.
Write `P` for orthogonal projection onto `N` and `A = P U |_N`.

If a row face fixes bit `j` and a column face fixes a different bit `k`,
the corresponding eight-by-eight submatrix of `H` has rank four. Its fifth
minors vanish. Thus `A` is block diagonal in the four coordinates.

For equal row and column coordinates, the two-by-two face block is

```
2^(-5/2) [[1,1],[1,-1]] tensor exterior^5(H_3),
```

where `H_3` is the normalized eight-by-eight Walsh matrix. It is unitary.
The sign in the bottom-right entry is negative because the exterior degree
is odd. Squaring this block gives `A* A = (1/16) I_448`. Since `U` is unitary,
the leakage operator `L = (I-P) U |_N` satisfies

```
L* L = I - A* A = (15/16) I_448.
```

In particular the target leakage has rank 448, and all its singular values
are `sqrt(15)/4`.

The same conclusions hold for `exterior^5(K)`. Indeed, with
`D_(x,x)=(-i)^wt(x)`, the exact identity is `K = -D H D`.
Both diagonal exterior factors preserve `N` and its orthogonal complement,
and are unitary. They conjugate the compression Gram by a unitary factor.
The scalar sign does not affect it.

### Call cap and its exactness

A call in direction `v` preserves every face space with `v_j=0`.
These give `112 (4-wt(v))` independent vectors of `N` whose image remains in
`N`. Its leakage rank is therefore at most `112 wt(v)`.

The verifier constructs every column of `exterior^5(2 C_v)` on `N`, with exact
Gaussian integer coefficients, for each of the fifteen nonzero directions.
It checks the full column Gram `1024 I_448`, the claimed kept columns, and a
modulo-65537 leakage rank of `112 wt(v)`. The embedding sends `i` to 256,
whose square is -1 modulo the checked prime. A nonzero minor in this residue
field is a nonzero Gaussian-integer minor, so this is a characteristic-zero
lower bound. Together with the preceding upper bound it proves equality.
The ranks by direction weight are respectively 112, 224, 336 and 448.
For an invertible operator `g`, `dim(N+gN)-dim N` equals the same quantity for
`g^-1`, so inverse calls obey the same statement.

### From one array to a program

For completeness, the kept-subspace argument is as follows. If the state map
is `M: V_5^W -> V_5^R`, with `V_5=V tensor ... tensor V` at width five, track

```
Phi(M) = dim(M(N^W) + N^R) - dim(N^R).
```

It starts at zero. Free address operations and mixing preserve `N^R`, so they
cannot increase this quotient dimension. Applying an invertible call `g` to
one register increases it by at most `dim(N+gN)-dim N`. This follows by pulling
back `N^R` through that call and adjoining the resulting extra dimensions.
At delivery, projection to the `W` output registers gives independent target
leakages, so `Phi >= 448 W`. Thus
`448 W <= 112 sum wt(v)`, as asserted. Extra scratch, intermediate copies and
erasures do not alter the argument.

## Exact replay

From the repository root, use CPython 3.12 with its standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/block4-coordinate-face-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/block4-coordinate-face-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/block4-coordinate-face-tariff --check-source-history
```

The registered commands also run optimized Python. All scientific checks use
explicit exceptions, so optimization does not remove them. The verifier checks
all 200,704 compression minors by fraction-free integer determinants. Their
integer compression matrix `B=1024 A` satisfies `B^T B=65536 I` exactly.
It then certifies all fifteen call ranks and rejects nine controls, including
an altered compression entry and the false cap 112 for diagonal directions.
It prints `PASS_BLOCK4_COORDINATE_FACE_TARIFF` with the results and SHA256 hashes
of all five package files. Optional `--receipt PATH` creates that generated
receipt outside the checkout and refuses to overwrite an existing file.
No hand-written receipt or predecessor replay is used.

The written program theorem uses the displayed finite identities. It has not
been checked by a formal proof kernel or an independent human. No physical
supplier, compilation tariff, rounding analysis or multiplication theorem is
claimed. The exact finite rank computation is specific to block four.

The verifier uses bounded loops over at most 4368 subsets, 448 source columns,
32 wedge choices per column and fifteen directions. Integer determinant
matrices are at most five-by-five. The sparse elimination has at most 448
pivots. Managed Python allocation and callbacks for the nine immediate negative
controls are explicit deviations from literal allocation-free and no-indirect-
call versions of the Power of Ten rules. No recursion, generated code or
external mathematical dependencies are used.

## Open next questions

- Can a different kept space give a demand-to-cap ratio above 7/2 while allowing
  every direction at unit price and arbitrary diagonal phases? The present
  exact cap 448 rules out that improvement from this space. Start by identifying
  a space that treats diagonal directions differently; general address-map
  keptness is a separate obligation.
- Does an exterior coordinate-face construction give a useful weighted law at
  other block sizes? Start with the face-compression blocks and their Gram
  identity. The present finite rank claim covers only block four.

See the structured questions and evidence in [TASK.json](TASK.json).
