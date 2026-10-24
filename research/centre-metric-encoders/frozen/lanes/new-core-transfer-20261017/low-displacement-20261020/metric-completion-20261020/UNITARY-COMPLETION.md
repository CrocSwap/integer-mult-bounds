# A unitary completion of the actual centre readers

The actual rank-sixteen centre readers admit a Gaussian dyadic unitary
completion C on all 112 ports. Both C and C* have zero diagonal in the
actual native mode basis. They also have zero diagonal in the physical
port basis.

All sixteen original centre readers can be recovered from a fixed set
of 32 output coordinates of C. Each large reader uses four of these
physical output coordinates. Each small reader uses two. No ordinary
output coordinate is needed for this recovery.

The complete scalar code and its inverse each cost 5,460 real scalar
primitives. They use no extra field. Both pass all 1,280 independent real
input columns, which represent 640 arbitrary complex fields. The 528
fields outside the code remain unchanged.

This packet proves a code, its scalar implementation, its centre
information, and its native support conditions. It does not emit a
changed native service or prove a routed caller.

## The actual basis and reader blocks

The pinned native response has eight six-mode blocks and eight
eight-port blocks. In each block its response is

```text
E_block = I - d d^T,
```

where each entry of d is a sign. The eight-port blocks have d=1.
The exact physical pair code H acts on the 48 large ports. Its 24
two-by-two matrices satisfy H_pair* H_pair=2I. It acts as identity
on the 64 small ports.

The pinned placement payload includes the actual port list, block
assignment, and pair matrices. The unitary payload includes the port
list and reader matrix V. No new abstract placement replaces these
data.

Put alpha=(1+i)/2. A signed six-mode block uses the names
(p,c,n,t,a,b) from the stored matching placement. First put
z_j=d_j x_j. Its code is

```text
out_p = (z_c+z_t+z_a+z_b)/2,
out_c = alpha (z_p+z_n),
out_n = (z_b+z_c-z_a-z_t)/2,
out_t = alpha (z_p-z_n),
out_a = alpha (z_b-z_c),
out_b = alpha (z_a-z_t).
```

The four-coordinate sum, its contrast, and two pair differences form
an orthonormal basis on those four coordinates. The two-coordinate
sum and difference form an orthonormal basis on the other two
coordinates. Here |alpha|^2=1/2. The full block is therefore unitary.
Each output row omits its own input coordinate, so its diagonal is
zero.

The original centre reader of this block is

```text
d^T x = 2 out_p + (1-i) out_c.
```

The centre is distributed over two output coordinates. This is why
the construction does not need a single normalized row of squared
length six.

For an eight-port block, split its stored ports into two groups of
four. Use the normalized sum, two pair differences, and one contrast
on each group. Put each group's four output rows in the other
group's four output locations. The two sum outputs are

```text
out_p = -sum(right)/2,      out_c = sum(left)/2.
```

Thus the block is unitary and has zero diagonal. Its centre reader
is 2(out_c-out_p). The six other rows are the normalized differences
and contrasts, each with zero sum.

## Physical pair closure

The two distinguished mode outputs per large block form two disjoint
perfect matchings in the actual eight-vertex pair graph. Their union
is closed under the physical pair code. The chosen 32 physical output
ports are serialized in `selected_full_ports`.

Let C_mode be the direct sum of the sixteen block codes. Define

```text
C = H^-1 C_mode H.
```

The factor H*H is 2I on all 48 large modes and I on the small modes.
The mode code preserves these two sets. These constant factors
therefore cancel when the physical adjoint is taken. It follows that

```text
C* C = C C* = I,        C^-* = C.
```

The checker verifies both identities on all 112 physical columns.
It does not treat the unnormalized pair matrix H as unitary.

The two modes of a physical pair belong to different six-mode
vertices. The mode code has no entries between those vertices and
has zero diagonal within each vertex. Conjugation by the pair code
therefore preserves the zero diagonal. The checker also verifies
this directly on the physical matrix.

## Centre information and the ordinary rows

Let P32 be the selected output set and R80 its complement. The
payload stores the exact decoder

```text
T = V C*.
```

Every row of T is supported on P32, and exact multiplication gives
T C=V. This is a statement about available centre information. It is
not an instruction to discard the other independent coordinates.

Every ordinary mode row r has r d=0 in its block. Hence

```text
r E_block = r.
```

The selected pair closure transfers this statement to physical
ports. The full exact matrix check gives

```text
(C E)_R80 = C_R80.
```

The ordinary diagonal is zero for both responses. The complete
response C has zero diagonal on all 112 modes. Its adjoint has the
same property. Every nonzero off-diagonal entry stays inside the
original six-mode vertex or eight-port clique. These are the
existing native transfer supports.

This creates two different native construction targets:

* Response CE uses the same 80 ordinary rows as C. Its exceptional
  rows can use the 32 selected FULL paths and a late FULL query.
* Response C needs no diagonal override in the native mode basis.
  It can be tested in the existing off-diagonal grammar.

These support statements do not price retuned native ADDs, compile
new complete native words, or prove that a current code can replace
an old code at a hole phase. Those are separate obligations.

## Complete scalar implementation

The program applies the actual H pair word, the sixteen real
unnormalized Haar blocks, the row normalizations, and the inverse H
pair word. The two selected rows of each small block use a paid
three-ADD signed rotation. No field permutation is free.

The complex factor alpha has an explicit real-component word.
For a field with real and imaginary parts (r,s), execute

```text
r -= s;
s *= 2;
s += r;
r /= 2;
s /= 2.
```

The result is ((r-s)/2,(r+s)/2) in terms of the original values.
Its price is eleven real scalar primitives under the source tariff.
The program uses only real ADDs and signed power-of-two scales.
There are no odd divisions, extra fields, or implicit complex
multiply primitives.

The serialized words use component index 2p for the real part of
field p and 2p+1 for its imaginary part. The code and its inverse
each have 1,778 component instructions and cost 5,460 real scalar
primitives. Each inverse instruction is emitted in the exact reverse
order with its inverse coefficient.

The largest real-component row one-norm at an instruction boundary
is 16 for C and 28 for C*. The additional binary denominator height
is two. These are exact local bounds. They do not include a
recursive child or rounding error.

The code accepts arbitrary field values at one common physical
type, such as current I or completed FULL. Its scalar word cannot
be applied across unequal hole types without an additional access
proof. In particular, C_t C_s^-1 is not assumed free.

## Checks, reproduction, and credit

Both unitary product orders, both physical zero diagonals, the
ordinary-row equality, and the full centre-decoder identity pass.
Every matrix entry is Gaussian dyadic. The literal component word
and inverse pass all 1,280 real columns, including 1,056 unchanged
outside components. A missing component ADD is rejected in both
directions. The saved programs are replayed.

Run in new output directories:

```text
python3 check_unitary.py --out <new-directory>
python3 -O check_unitary.py --out <another-new-directory>
```

The normal and optimized payloads and receipts are byte-identical.
The earlier signed-metric construction remains as a pinned placement
dependency. It is not substituted for the new positive unitary code.

The root lane proposed the distributed positive unitary normalization.
This lane supplied the actual matching placement, physical basis
binding, zero-diagonal output assignment, scalar words, and complete
checks. The controller and native response packets supplied the
centre readers and the six-mode and clique supports. The cover lane
is studying the caller that uses the primal and inverse-adjoint code.
AI assistance was used throughout.

No PR, commit, push, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
