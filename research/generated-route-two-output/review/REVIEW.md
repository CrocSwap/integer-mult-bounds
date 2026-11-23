# Independent review of both-output binary low/carry production

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Apache-2.0. This is separate model-assisted review, not independent human
or formal-kernel acceptance.

**Decision: accept the scoped construction and one-pass obstruction at the
exact frozen inputs recorded in FROZEN-INPUTS.json.** The result produces
low digits and exact localized carries for the retained admitted grammar.
It does not establish a payload permutation, a complete canonical assumption
discharge or a new kappa.

## Source and review method

I read the proof, transducer, retained grammar, alphabet, examples and
predecessor boundaries. Eight `commit:path` entries were independently
resolved in Git and compared byte for byte with their retained copies;
`SOURCE-COMMIT-CHECK.json` records this. The executable independently checks
the SHA256 and Git-blob identities.

`independent.py` does not import or run the author's `check.py`. It compiles
authenticated `transducer.py` source bytes as the implementation under test,
bypassing `.pyc`. Expected local outputs instead use

    y=(Z * D^(-1)) mod q,       c=(Z-Dy)/q.

This modular inverse is part of the review oracle, not the runtime producer.
Whole-word expectations use independently assembled dense rational right
matrices. Separate transition, register and distinguishability checks are
also included. The universal conclusions rest on the arguments below,
not extrapolation from finite cases.

## 1. Both local outputs, signed states and short inputs

For fixed coefficients, set L=sum min(a_i,0), H=sum max(a_i,0),
U=max(0,H-1). Canonical inputs imply L<=floor(Z/q)<=U, including H=0.
For threshold j the length-r state is floor((Z_r-j q_r)/2^r). Writing
the previous numerator as quotient plus remainder in [0,2^r) proves
exactly the source floor recurrence after appending an LSB row. The final
state sign is therefore the exact threshold comparison, and the sum of
true comparisons gives floor(Z/q).

The declared state interval contains zero and all possible per-row
increments. Flooring the average of two interval members preserves the
integer interval. This proves its invariant at arbitrary input length.

Odd q is invertible modulo fixed D. Taking the largest c<=u in the required
residue class gives u-D+1<=c<=u and 0<=Z-cq<Dq. Thus (Z-cq)/D is the
unique canonical low output; c/D is the localized carry. Negative
fractional carries are intentional.

The second pass is signed binary accumulation with retained bounded c.
Floor division is essential when the state is negative; its remainder
bit is still in {0,1}. At every prefix, the consumed integer equals the
emitted low bits plus 2^r times the signed state. Divisibility makes the
first s bits zero. The s zero rows give B+s total ticks, exactly B retained
output bits and zero terminal carry. This includes B<s: some discarded
zeros and the remaining output bits occur during flushing. No B-bit
accumulator is hidden in finite control.

Input comparisons reject x_i>=q; first/last radix bits one and at least
two rows give canonical odd q>=3. The two traversals must read the same
supplied read-only channels. Malformed or changed channels do not receive
a rollback or correctness guarantee.

## 2. Finite control and admitted alphabet

Independent enumeration of all 109 fixed columns confirms:

| Quantity | Bound |
| --- | ---: |
| Quotient comparators | 54 |
| First-pass product-state encoding per fixed column | 388 bits |
| Local carry numerator | -54 through 54 |
| Second-pass signed arithmetic state | -54 through 86 |

The 388-bit number is a declared logical encoding for a fixed column. It
does not describe Python memory, all output data, tape backing or minimum
state complexity. A shared dispatcher also has fixed finite opcode/type
information, as the revised statement now says. Growing output and fused
carry data remain separately charged.

The frozen alphabet is closed under addition negation and scale inversion.
The admitted constructors copy seed words, relabel, concatenate, reverse
and invert; none invents a coefficient. The scope is essential: generic
`literal` and `euclidean_seed` APIs can accept other data, so their arbitrary
outputs are not automatically covered by the census. The revised theorem
explicitly restricts itself to the retained admitted seeds.

## 3. Whole-word carry registers

Let D_j be the denominator product and P_j the product of the elementary
maximum-coordinate norm factors. The exact rational prefix has induced
norm at most P_j/D_j. Comparing it to its canonical low row proves

    |p_(j,i)| <= (1-1/q)(P_j+D_j) < 2P_j.

This does not assume the intermediate rational row itself is bounded by q.
For an addition, the critical partial must be bounded jointly:

    |D p_i+a p_k| < 2P_j(D+|a|)=2P_(j+1).

Separately giving each term 2P_(j+1) would lose the stated constant. This
joint bound was added after review. A scale uses max(D,|a|) instead.
The injected local term cD_j is below 2P_(j+1), and unaffected registers
are still multiplied by D. Hence every computed sum is below 4P_(j+1).
The signed width `bit_length(P_m)+4` is sufficient with room to spare.

Denominator exponents are at most five per arithmetic instruction; norm
factors are at most 55 for additions and 16 for scales. Thus v<=5m and
W<=6m+5, including m=0. Those growing work words are not finite control.
Independent rational right products check chronology and the inverse
cocycle. An inverse begins at the committed output low row, not a stale
original low row. Reduction and transport of high payloads modulo q^(w-1)
remain another service.

## 4. Real sequential access invoice

The local stream uses a fixed number of input/output heads. Physical
origin markers permit head return without storing B in finite control.
Input traversals, output, return, discard and flushing are charged.

Extracting and replacing at most two records from an N-coordinate row is
an O(NB) scan. The fused carry update scans N work words, including every
denominator shift. Fixed source multipliers require a fixed number of
shifts/additions; conservative school arithmetic and address counters fit
the squared `B+W+log(2N)` bound. N rows and ell+1 stages give the stated
producer bill. Its materialized output requires N^2(B+W) bits, which is
not compressed into the local-state encoding.

This is an algorithmic access construction, not an executed literal
finite-tape graph or a Python memory benchmark. It neither orders complete
payload fibers by new low type nor restores a recursive caller's owner.
The explicit route, ownership and complete-cost limitations are retained.

## 5. One-pass obstruction and its exact model

The primitive is the coefficient-one shear x <- x+y mod q with two unknown
channels. This is not unary increment x <- x+1.

For odd q>=5 put K=2^(B-2), so K is even and q=aK+r with a in {2,3} and
1<=r<K. At the B-2-row cut consider prefixes x_low=t,y_low=0. The common
all-zero high continuation returns t. The alternative completions are:

- a=3: x=t+2K,y=2K are below q, and q<=x+y<2q.
- a=2,t<r: x=t+2K<q,y=K; their sum crosses q exactly once.
- a=2,t>=r: x=t+K<q,y=K; their sum again crosses q exactly once.

All high terms are multiples of even K, so subtracting odd q reverses the
first output bit relative to t. No first output bit could yet have been
emitted at any such prefix. The append-only LSB output histories are all
empty. If two prefixes had the same retained state, their identical zero
continuation would produce the same output, but their required t outputs
are distinct. At least K states, or B-2 binary state bits, are necessary.

Retained state includes all input-dependent work data and accessible
head-position encodings. The theorem does not cover uncharged growing
scratch, rereads, revised output, different output order or additional
input-dependent channels. Public q and B may be known. The finite review
covers all odd q through 1023; the above case split proves the universal
claim. The even-radix control shows why this parity discriminator needs
odd q. Neither this obstruction nor the older serialized carry-only
obstruction subsumes the other's access/output model.

## 6. Executed independent evidence

The normal and optimized receipts are byte-identical. Checks include:

- 14,855 modular cases, including 6,248 negative carries and 1,514 B<s cases;
- 24 long inputs, up to 4,097-bit odd radices;
- 55,584 affine interval corners; monotonicity supplies the interval interior;
- 75 dense matrix cases, 75 inverse cocycle cases and 225 q-power reconstructions;
- 24,489 prefix-register checks and 1,778 frozen opcodes;
- 35,912 actual 134-dimensional coordinates, including all spectator returns;
- 87,380 prefix witnesses at all 510 odd radices from 5 through 1023.

Implementation mutants omit zero flushing or unaffected denominator shifts,
or replace signed floor by truncation toward zero. Independent modular/dense
expectations reject each. Source corruption and the even-radix scope control
are also detected. Reproduction, using standard-library CPython 3.12:

```
python3 -I -B review/independent.py --package PATH_TO_PACKAGE
python3 -I -O -B review/independent.py --package PATH_TO_PACKAGE
```

No author checker was used as independent evidence. Full production
carrier materialization, physical payload routing, supplier admission
and unconditional integer multiplication remain unproved by this package.
