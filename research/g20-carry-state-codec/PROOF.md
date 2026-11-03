# A 24-bit encoding of the retained carry state

This scoped proof changes the representation of Ali Romman's PR6503 producer.
Its quotient automata, carry identity and packet formula are inputs. Their
minimality and correctness are not new results of this package.

## Contract

Fix one source column with eight integral numerators `a_i` and denominator
`D` in `{1,4}`. A row consists of eight input bits `x_i` and one radix bit
`b`, least significant row first. The first radix bit must be one. Let
`s = sum_i a_i*x_i`. The source quotient component has `m` states, initial
state `z0`, transition `T(z,s,b)` and terminal output `U(z)`.

The retained source state is `(z,c_0,...,c_7,r,h,l,p)`. Here each comparison
`c_i` is -1 or 0; `r` is the first-two-row numerator residue modulo `D`;
`h` is the second radix bit; `l` is the last radix bit; and `p` is the
number of rows read, capped at two. Initially the comparisons are zero,
`z=z0`, and the other fields are zero. Each row updates

```
z <- T(z,s,b)
c_i <- floor((c_i+x_i-b)/2)
```

While `p<2`, add `2^p*s` to `r` modulo `D`. On the second row set `h=b`.
Set `l=b` and increment `p` up to two. At completion, require a nonempty
stream, `l=1`, and every `c_i=-1`. The packet is

```
u = U(z)
c = u - ((u-r*(1+2*h)) mod D)
packet = 4*c/D + 16
```

PR6503 supplies the quotient tables and source-column bindings. We preserve
this exact contract, including invalid-input rejection. The proof below
also works for an arbitrary total quotient transition with the same state
and alphabet bounds. No property of the quotient partition is re-proved.

## Encoding theorem

For any such component with `m>=1`, at most `4096*m+257` codes suffice for
all retained states reached from initialization. For the source bound
`m<=2406`, this is at most 9,855,233 codes, hence 24 bits.

Reserve code zero for no rows. After exactly one accepted row, retain
only its eight input bits, as a bitmap `v`, using code `1+v`. The radix bit
was necessarily one. Thus the first-row codes are exactly 1 through 256.

The bitmap determines the entire abstract first-row state. Its comparison
values are `x_i-1`, because `floor((x_i-1)/2)=x_i-1` for binary `x_i`.
Its quotient state is `T(z0,sum_i a_i*x_i,1)`, its residue is that digit
modulo `D`, and `(h,l,p)=(0,1,1)`. Evaluation of the first quotient step
can therefore wait until the next row or completion. This argument needs
no reread of an earlier input row.

After at least two rows, let `v` have bit `c_i+1` at position `i`. Encode
the retained state by

```
257 + 4096*z + 16*v + 4*r + 2*h + l.
```

There are `m` choices for `z`, 256 for `v`, four for `r`, and two each
for `h,l`. For `D=1` we deliberately allow three unused residue values
in this representation domain. Repeated Euclidean division by
`4096,16,4,2` recovers all five fields uniquely. The mature codes are
exactly the interval `[257,257+4096*m)`, disjoint from the empty and
first-row codes. This proves injectivity and the stated size bound.

At `m=2406` the full mature product domain has 9,854,976 states. Together
with the 257 early states it has 9,855,233 states, more than `2^23` and
at most `2^24`. Thus 24 bits are sharp for **this declared representation
domain**. This is not a lower bound on actually reachable joint states,
canonical-input states, terminal packets, or other implementations.

## Transition and output preservation

From the empty code, check `b=1` and save `1+v`. No table is read.
From a first-row code, reconstruct its abstract state by the formula above,
apply the new row's source transition, and encode a mature state.
From a mature code, decode, apply the source transition and re-encode.
Induction on the number of rows proves equality of every decoded abstract
state. The terminal validation and packet formula are the source formulas
applied to that decoded state, so acceptance and output are identical.

The executable uses a bitwise comparison update. If `b=0`, the new comparison
bitmap is `v OR x`; if `b=1`, it is `v AND x`. Substitution of each of the
eight triples `(c_i,x_i,b)` proves these identities. The independent
reference in `verify.py` instead updates each signed comparison with floor
division. No change to the comparison contract is assumed.

For a valid stream of `L` rows, the source uses `L` quotient transition
lookups and one terminal output lookup. For `L=1`, the new finish performs
the delayed transition and output, two lookups. For `L>=2`, the second row
performs two transitions; each subsequent row performs one; finish performs
one output lookup. The total is `2+(L-2)+1=L+1`. Both implementations also
evaluate each row's aggregate digit once. These are abstract table-query
counts, not tape travel or Boolean-gate costs.

## Evidence and limits

The verifier enumerates every mature code at `m=2406` and checks the ordered
bijection and its inverse. It checks all first-two-row pairs for one actual
largest source component, and mature transitions for every source model.
It tests the new producer on every retained source column, with every prefix
compared against the unpacked recurrence and each terminal packet compared
against modular arithmetic. These tests concern the new encoding and its
consumer interface. They do not repeat source reachability, refinement or
minimality censuses.

The argument covers every finite row count. The convenience `produce`
function explicitly limits one invocation to 65,536 rows; `step` and `finish`
do not impose a stream-length limit. The registered fixtures reach 4,097 rows.
This is a written proof with finite executable corroboration, not a formal
proof-kernel result or independent human acceptance.

The 24-bit claim counts only logical state retained between rows. Immutable
coefficients, quotient tables and descriptors, the current input row,
transient arithmetic and decoding scratch, and the output are additional.
The executable uses Python integers and is not a 24-bit-memory physical
machine. No lookup circuit, head-return tariff, dirty-workspace restoration,
reversible-history reduction, full caller substitution or runtime improvement
is proved. The full paid moment and selected frontier are unchanged.

This contribution was produced by Nick Petalas. Credit Ali Romman's
PR6503 and PR6474, PR5820 and their retained G20/native/ROW lineage for
the source construction. Mixed-radix encoding and delayed evaluation are
classical; the contribution is this concrete reduced-state representation.
New work is Apache-2.0. Independent human and formal proof-kernel review
are unclaimed.
