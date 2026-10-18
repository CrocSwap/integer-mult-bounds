# Encoded setup and ownership invoice

This is a source-level proof for successful calls of the unchanged
`high_route.execute` and `high_route.extents` retained by
`selected-bit-fast-primitives` (PR2915), including its nested PR2899 count and
physical-word implementations. Finite executions corroborate the identities;
they do not establish the universal statements by extrapolation. All input
bytes and attribution are recorded in `SOURCES.json` and `README.md`.

## Boundary and currency

Count one physical Tape read, write or unit move once. Numerical Word/Lease
aliases do not introduce a second charge. Native-controller operations belong
to the native toll below. Host bookkeeping, finite-control selection,
compilation and initial provisioning of the enclosing fixed inventory are
outside this currency. The high bank's repeated marker provisioning **inside**
`execute` is included.

Let `d>=1` be the compiled matrix dimension, `N=d²`, `Q>=1` the high-field
modulus, `H=Q^N`, `F>=1` the canonical fibre Count, and `V=HF` the number of
payload bits in a complete cube. Put `L=bit_length(Q)`. The context's `cap`
and `ring.one` are distinct Words of the same encoded width `I>=L`; the former
is a fresh quotient in `directory.Context`. I is the actual outer Word width,
not the quotient's significant bit length. The borrowed
Counts have canonical digits and all borrowed heads enter at their origins.
The source is a dense V-bit tape.

Use the retained pooled factory: a successful acquisition returns a distinct
blank caller-owned lease and performs one physical blank read. Require valid
compiled field indices, enough fixed inventory, and an empty, erased high
bank with `K` numerical roles plus its template. K is a **role count**, not a
word width; the adapter default is `2^24`, while reduced fixtures may use 64.
The result is a distinct owned dense V-bit tape at its origin. Borrowed state
is preserved. This does not assert exception recovery or allow arbitrary dirty
numerical bank residents.

For each reached kernel/adapter call retain its successful endpoint contract:
it preserves its borrowed dense input, restores that input head to its origin,
and returns a distinct dense V-bit owned output at its origin. The composition
below uses these shape/head/ownership facts and charges the entire call. It
does not replace their all-width native or kernel proofs with reduced tests.

## Exact count primitives

All following counts include the pooled acquisition reads. Write
`b(x)=max(1,bit_length(x))`. A tape at head position h, with LEFT at zero,
rewinds in `2h+1` operations. Closing a canonical n-digit Count at its origin
therefore costs

```text
C(x) = 5b(x)+12.
```

Copying a positive x from an I-digit encoded operand costs
`18I-4b(x)+21`. The canonical special case is `14b(x)+21`.
Copying zero from I digits costs `18I+29`. These include normalization:
each removed high zero costs six operations, and zero additionally repairs
its sole digit and delimiter. `Count.literal(x)` costs `24b(x)+42` for
positive x and 78 for zero, including its raw temporary's disposal.

For the source's multiplication by two, define

```text
Dbl(x) = 11                         if x=0,
         6b(x)+9                    if x>0.
```

For `Count.add` with x>=0 and a>0, put `X=b(x)`, `A=b(a)`, `Z=b(x+a)`.
The exact invoice is

```text
Add(x,a) = 23A+2X+9Z+50.
```

Indeed its copied source costs `14A+21`, the two initial rewinds cost six,
the addition loop costs `2X+2A+3Z+2`, writing and normalizing the result costs
`6Z+9`, and closing the source at its RIGHT delimiter costs `7A+12`.
The terminal loop iteration is included.

For positive a,b, let `A=b(a)`, `B=b(b)`. Define P(a,b) by scanning b's
bits from most to least significant, initially v=0:

```text
P(a,b) = 19A+21B+151
         + sum_bits [3+(1-bit)+Dbl(v)+bit*Add(2v,a)],
v_next = 2v+a*bit.
```

This is the exact `Count.product` cost, with the returned product still owned.
The initial term accounts for both operand copies, literal zero, scan.msb,
the final scan termination/move and closing factor and scan. The per-bit term
includes the source's extra ZERO read on a zero multiplier digit. The invoice
is asymmetric: for example `P(2,1)=340` and `P(1,2)=329`.

Define W(Q,e), the complete `fixed_power` cost excluding disposal of its
returned Count, by the actual binary-exponent recurrence. Initialize
`r=1,f=Q,n=e` at cost `66+14L+21`. While n is nonzero:

1. If its low bit is one, add `P(r,f)+C(r)` and replace r by rf.
2. Shift n right once. If it remains nonzero, add `P(f,f)+C(f)` and replace
   f by f².

Finally add C(f). In particular, the zero-exponent case is not free:
`W(Q,0)=99+19L`. Each replaced value and the final unused factor are disposed.
All returned and borrowed Count heads are at their origins.

## Exact extent lifetimes

These equations price `extents` **and** the returned Counts' `apply`-finally
closures, not just preparation. For a unary field i, put `t=N-i-1`:

```text
E1(i) = W(Q,i)+W(Q,t)+P(Q^t,F)
        +C(Q^t)+C(Q^i)+C(Q^t F).
```

For binary fields sorted as i<j, put `g=j-i-1`, `t=N-j-1`:

```text
E2(i,j) = W(Q,i)+W(Q,g)+W(Q,t)+P(Q^t,F)
          +C(Q^t)+C(Q^i)+C(Q^g)+C(Q^t F).
```

Zero exponents are allowed. In each case the suffix product is fresh; its
power operand closes in `extents` even though the product survives. The
other two or three returned Counts remain live through every data call and
close exactly once in `apply`. These are different physical tapes; none is
the borrowed modulus or fibre.

## High bank and execute skeleton

When Q>1 the bank uses `B=L+1` bits per numerical Word. Directly counting the
retained loops gives:

| Source interval | Physical operations |
| --- | ---: |
| Initialize all K role markers and the template marker | `5(K+1)` |
| `bank.prepare(modulus)` | `9L+16` |
| `bank.load(modulus)` | `19L+32` |
| `Ring(modulus_word)` | `22L+63` |
| `ring.close()` | `5L+13` |
| `bank.free(modulus_word)` | `5L+13` |
| `bank.erase_owned()` | `5K+5L+17` |
| **Complete bank lifecycle** | **`10K+65L+159`** |

For example, `Arena.zero` costs `9B+12`, a B-bit Word erasure costs `5B+8`,
and comparison of distinct I-bit Words costs `9I+14`. The comparison before
the branch is charged even when Q=1. That branch skips all factors and every
bank operation, but still copies the cube and creates/closes its modulus Count.

Use PR2877/PR2982's credited canonical countdown and row-copy invoices:

```text
D(n) = 15n+14b(n)-5popcount(n)+36,
Pprobe(F) = 4   if F is even,
            15  if F>1 and F=1 mod 4,
            12  otherwise,
R(H,F) = D(H)+1+H*(Pprobe(F)+5F+[F>1]*(D(F)+1)).
```

The initial source copy costs R(H,F). Outside data calls, extents and bank
operations, `execute` costs exactly

```text
E0 = R(H,F)+4V+27I+L+61.
```

To see the constants, retain rather than hide the Count costs: the skeleton
is `R+4V+Copy(Q,I)+(9I+14)+5L+26`. It includes the initial output acquisition,
initial source rewind, complete-source probe, source/current rewinds after
copying, final source rewind and modulus closure. Substituting
`Copy(Q,I)=18I-4L+21` gives E0.

## Data calls, disposal and exact composition

For every direct `adapter.swap` invocation let A_j be its **whole** physical
toll. It includes its width/extent preparation, the actual native B1 call,
copying the returned B1 output and its disposal. Write `A_j=B1_j+J_j` if
separating the actual B1 interval from adapter overhead. Both remain charged;
do not add B1_j again to a toll that already contains it. Let K_j be the
whole toll of each direct high-field kernel invocation, including its internal
allocation and cleanup. These quantities are not assumed uniformly bounded
by this proof, and elementary B1 fixtures do not prove a fitted all-width bill.

Let s be the number of factors actually executed (zero when Q=1), r the
number of reversed ADD factors, and E_j the applicable E1/E2. A reversed ADD
means its control field exceeds its target, before sorting the extent indices.
Then the exact successful open-cube invoice is

```text
T = sum_j A_j + sum_j K_j
    +E0+[Q>1]*(10K+65L+159)
    +sum_j E_j+(s+2r)*(5V+7).
```

A normal factor disposes the previous owned cube once. A reversed ADD first
swaps into B, computes into C and clears B; it then swaps C into D and clears
C. The outer loop additionally clears its retained input A. Each cleared
tape is dense, at its origin and distinct from the borrowed original source,
so each clearance costs `5V+7`. There are two direct swap calls for a reversed
ADD, one for a swap factor, and none for an ordered ADD. All their actual B1
calls remain within the charged adapter tolls.

At these call-return cuts an ordered ADD has two caller-owned V-bit cubes;
a reversed ADD has three. The borrowed original source is additional. This
is a bound on caller-retained payloads at those cuts, **not** a total workspace,
allocation/backing bound or a bound on opaque callee/native internals. Cleared
pooled tapes can retain longer blank backing. Consuming the final returned
owned output costs another `5V+7`; its disposal is outside the open invoice.

## A safe uniform bound for the proved part

Put `n=bit_length(V)` and `J=2bit_length(N)`. Every positive product occurring
in extent preparation has operands and product at most V. The recurrences
above imply

```text
P(a,b) <= 40n²+103n+151 <= 294n²,
C(a) <= 17n²,
W(Q,e) <= (118+311J)n²                 for 0<=e<=N-1,
E1,E2 <= B_N n²,     B_N=716+933J.
```

For W, at most J products occur; the literal/copy startup costs at most
101n², each product plus replaced-value disposal at most 311n², and the
final factor closure at most 17n². Binary extents need at most three powers,
one further product and four closures. This proves the displayed bounds
without relying on measured ratios.

For every positive integer V, `n²<=3V`: check n=1,2,3, then use
`(n+1)²<=2n²` for n>=3 and `V>=2^(n-1)`. The credited row-copy bounds give
`R<=83V`; also `L<=n<=V` and `r<=s`. Thus, excluding the explicitly charged
data-call tolls, a convenient uniform upper bound is

```text
T - sum A_j - sum K_j
 <= 27I+10K+[373+s*(3B_N+36)]V.
```

It covers Q=1 as well, with s=0, though its unused bank allowance is then
loose. Output disposal adds at most 12V. This is not claimed sharp.

The actual outer Ring requires exactly one high zero above its modulus; it
does not permit arbitrary extra Ring padding. With the retained source
binding `I=bit_length(q^w)+1` and `Q=q^(w-1)`, one has
`I<=L+bit_length(q)+1`. Thus fixed q,d,K yield a linear-V bound for this proved
part. The radix must remain exposed when eliminating I: at width one, q=3
and q=5 both give Q=1 and the same V, but their I values are three and four,
so their setup costs differ by exactly 27. This substitution does not price
finite-control transitions, native/kernel tolls, caller hosting, all-stage stock
or complete multiplication.

The source implementation belongs to Jose Manuel/jmbarrancoml and its credited
predecessors. The countdown/copy-row bills are inherited from Arham Tahir's
PR2877 and Nick Petalas's PR2982; this note adds the encoded setup and disposal
composition. Prepared for thakrarsagar with OpenAI Codex assistance, including
separate source derivation and finite observation. No independent human review
or proof-assistant verification is claimed. Apache-2.0.
