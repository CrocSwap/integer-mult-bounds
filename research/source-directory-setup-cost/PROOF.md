# Cubic exponent reconstruction, linear complete directory production

This audit concerns unchanged PR2569 at
`0b116cb34f27a4b064f0d8dd65549ea5705cf9c0`. Its Tape charges count symbol reads,
writes and unit head moves. Python allocation, integer audit observations,
compiled finite labels, the tape-registry observer and literal machine
instructions are outside this meter, as in the predecessor.

Fix a prime q>=3, 1<=m<=64, and a finite compiled request catalogue. Constants
may depend on these fixed choices. Let w>=1, M=q^w, Q=q^(w-1), H=Q^(m²),
and L=bitlength(M)+1. All numerical arena words retain exactly L bits,
including the reserved high zero, even when their values become small.
Let C>=1 be the number of old physical prefix positions and b=bitlength(C).
Cardinality input tapes are canonical, without unrelated padding.

## 1. The exact division write bill

For one call to retained `Unsigned.divmod`, let s be the number of one bits
in its quotient. The numerator and divisor are distinct, valid L-bit words;
the divisor has its required zero margin. The exact number of Word writes,
including internal allocation and erasure but excluding caller cleanup, is

```
B_div(L,s) = 3L² + 8L + 4 + (3L+2)s.
```

An arena zero allocation writes L zeros and its right delimiter. Copying an
input therefore writes 2L+1 symbols. Erasing a word writes L+1 blanks.
The source's startup copies the numerator and allocates quotient and remainder:
`(2L+1)+2(L+1)=4L+3` writes. Its final scan erasure adds L+1.

The loop executes exactly L times: `scan.msb()` starts at the last encoded bit
and advances left once per iteration, regardless of leading zero values.
Each iteration allocates and writes its shifted remainder (2L+1 writes),
erases the old remainder (L+1), and writes one quotient bit (1). This gives
3L+3 writes per iteration. When comparison triggers subtraction, allocation
and subtraction add 2L+1, and erasing the shifted operand adds L+1. Such an
iteration writes a one to the quotient, so there are exactly s of them.
Summing proves the formula. No numerical sampling establishes this identity.

This formula does not charge freeing the returned quotient or remainder.
Those operations are separately included in the enclosing source execution.

## 2. What `high_power` actually does

`counts.high_power(value, ring, q, m)` invokes `digit_suffix` exactly m² times.
Every invocation traverses `radix_power` afresh. Starting from q^w, that
generator performs w divisions by q before reaching one. Each division uses
the same L-bit arena. Hence the exact number of divisions is m²w and the
exact number of full-width shift iterations is m²wL.

The first yield of each traversal skips multiplication. In total the value is
multiplied by q exactly k=m²(w-1) times, giving C*H. The radix traversal uses
only numerical Word tapes, while these multiplications act on the separate
Natural tape. Their meters therefore add without double counting.

In particular, writes in `high_power` obey

```
writes >= m²w (3L²+8L+4).
```

Since L>=w, fixed m>=1 and C=1 already give an Omega_q(w³) lower bound.
This rules out PR2569's stated `O_q(w log(C+1)+w²)` bound for computing CH
with these unchanged source loops. It does not rule out its final
volume-based producer or route bounds.

For a fully charged upper bound, put bq=bitlength(q). The elementary Word
copy/free/compare/subtract/shift scans each cost at most 100(L+1) of each
operation; a divmod costs at most 1000(L+1)². These conservative source-loop
bounds are also credited to PR2566's separate primitive audit. Counting the
generator's comparisons, zero tests, allocations, frees, startup and return
gives at most 2000(w+1)(L+1)² per radix traversal. There is no decoded runtime
exponent counter in this accounting.

A Natural multiplication at input bit length t costs at most
100(t+bq+1) of each operation. The bounded finite carry adds at most bq bits.
The kth product's bit length is at most b+k*bq. Thus each of reads, writes
and moves in `high_power` is at most

```
U(q,w,m,C) = 2000 m² (w+1)(L+1)²
             + 100 k (b + k*bq + bq + 1),  k=m²(w-1).
```

The correct setup order is `O_q(w³+(w-1)b)`, with m fixed. It is also sharp
as a joint order: each of the k multiplications writes at least b input-bit
positions, and the preceding division lower bound is cubic. At w=1 there
are no multiplications; `high_power` need not read the initial C tape at all.
Constructing a fresh Count copy of C, as `produce` does, adds O(b), giving
the usual complete cardinality-setup order `Theta_q(w³+w*b)`.

The test observer sums every tracked Tape and Arena meter. It separately
records Natural and radix-word traffic, checks every division's formula and
L iterations, and verifies the returned count and erased numerical work.
Observer decoding is external; retained `Word.inspect` is disabled.

## 3. Complete directory production still costs O_q(D)

Let h>=0 be the number of frozen fields per old position. Repeated tuples
remain distinct physical positions. Let B be the fixed compiled source-code
width. One field occupies

```
J = B+2 + m²(L+1)
```

serialized source-tape cells: B code bits and a delimiter, m² numerical
words with delimiters, and a field-end marker. Consequently the exact output
extent is

```
D = C H (h+1) J.
```

These are fixed-alphabet cells; a fixed binary symbol encoding changes D by
only a constant factor. The output alone requires D writes.

Consider `Context` construction, one `produce` call and `Context.close`.
Input fixtures and compilation of the fixed vocabulary precede this interval.
The interval returns the directory and its Count to the caller; their later
disposal is separate. The exact number of unsigned divisions is

```
((2m²+1)w + 1).
```

Here w divisions validate the modulus, one forms Q, m²w compute Context's H,
and m²w compute the producer's CH. Other production operations divide no
numerical words. These setup terms cost O_q(w³+w*b).

For every integer w>=1, w²<=3^w<=q^w=q*Q<=q*H. The first inequality follows
at w=1,2 and then by induction, since ((w+1)/w)²<=9/4<3 for w>=2. Therefore

```
w³ <= q H w <= q C H L <= q D,
w*b <= w*C <= C H L <= D.
```

This absorbs even the corrected cubic setup. It uses the actual complete
high cube, not a body-size premise or an assumption that headers are free.

The remaining loops are linear in D:

* Each old tuple is read/validated/serialized once, costing
  O_q(C*h*L), including one decoded word at a time and the h countdowns.
  Copying it H times is exactly the old-field portion of the output volume.
* The current m²-word high field is written for each of CH positions. Each
  odometer increment performs at most m² full-width increments, comparisons
  and clears. With fixed m this costs O_q(CH*L), already bounded by D.
* Emission counting uses amortized ripple increment. Its sum is O(CH), with
  O(log(CH+1)) initialization/comparison/erasure. Outer C and inner h
  countdowns, their input scans and zero cases cost O(C(h+1)) plus the
  canonical logarithmic terms, also bounded by D.
* Rewinding, clearing the serialized tuple and odometer at each old position,
  returning the input/output heads, and closing the Context add O_q(D).

Hence complete production has Theta_q(D) source-meter work, including setup
and cleanup, for arbitrary C>=1 and h>=0 under this input contract. No root
coupling or Boolean fibre size was used in this producer statement.

## 4. The separate payload-volume implication

To conclude D=O_q(V), where V=CHR, the predecessor's extra h/w/R assumptions
remain relevant. In its stated application R>=q^(2nw), n>=1, and
`w=ceil(e^(17/10000))`, `2^(h+1)<=8e²` imply h+1=O(w). Since J=O_q(w),
we get D=O_q(CH*w²)=O_q(V). The source setup correction therefore preserves
the claimed volume-linear directory asymptotic in that domain. It supplies
no practical numerical reserve constant, full selected driver, recursive
parking schedule, fixed-tape allocator/controller or new supplier/exponent.

Without a bound on h or R, D/V can be arbitrarily large; our stronger
Theta_q(D) producer lemma must not be substituted for a payload-volume claim.
The route's separate coefficient preparation and radix-sort invoice are not
re-audited here. Neither are full selected low-code compilation, packet
hosting, transported COPY endpoints, or actual 64-dimensional Boolean data.

## 5. Finite corroboration and controls

Sixteen setup cases cover two q values, w through 32, a 129-bit C, mixed m,
and the m=64/w=1 boundary. Eleven complete directory cases include empty and
repeated old tuples, three distinct empty-prefix positions, small full high
cubes, and an m=64/w=1 directory. Direct serialization checks the entire
output order and multiplicity, not merely its length. All input heads,
numerical ownership and private cleanup are checked.

Controls show that counting only Natural multiplications misses the proved
write floor, shrinking L to the significant dividend length changes the exact
bill, one division cannot represent a complete exponent traversal, and empty
old tuples cannot be deduplicated. These finite controls corroborate the
written all-size argument; no fitted growth regression is used as proof.
