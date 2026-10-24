# Linear radix scans in the actual Context constructor

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## Result and credited premises

For each fixed compiled radix q>=2 and dimension d>=1, let M=q^w with w>=1.
Let B=bit_length(M)+1 be the retained Word extent, including its zero high
margin. The new constructor returns the same genuine source Context, cap
q^(w-1), and high Count H=q^((w-1)d^2). It executes through the unchanged
Machine.new_context and save_count bodies with one explicit Context factory.
It preserves the source Ring/raw aliases, fixed Tape views, numerical inputs,
other borrowed records and canonical heads.

The numerical and record source-action count is O(w^2) for fixed q,d. The
literal and already-shared Context have an Omega(w^3) general-division term.
The new constructor uses one temporary record-tape lease and four live
numerical Words, including the supplied modulus and retained ring.one. The
literal and shared fixtures require two leases and nine numerical Words.
These are local counts in the named source model, not a complete supplier
or frontend tariff. Extra caller-owned words remain additional live storage.

The count formula and source classes are retained. ToikY's
[PR #4025](https://github.com/CrocSwap/integer-mult-bounds/pull/4025) supplies
shared high-power traversal; Chris R's
[PR #4062](https://github.com/CrocSwap/integer-mult-bounds/pull/4062) already
applies it to Context construction. Ali Romman's
[PR #5025](https://github.com/CrocSwap/integer-mult-bounds/pull/5025) supplies
a unary radix cache at a different caller. No new claim is made for sharing
or caching radix iterations. Fixed-radix long division is classical and is
already used by Natural.divide_small in the retained source. This work binds
that operation to fixed-width Words and fuses the actual Context producer.
Mihir Srivastava's [PR #5363](https://github.com/CrocSwap/integer-mult-bounds/pull/5363)
supplies the installation proof and source extraction fixture.

## Quotient and constructor invariants

The quotient kernel moves to the most significant bit of an owned B-bit
Word. It scans left, with finite remainder r initially zero. For each input
bit b, replace r by 2r+b. Write quotient bit one and subtract q when r>=q;
otherwise write zero. Before each iteration 0<=r<q, and before subtraction
0<=2r+b<2q. Thus the control state is finite for compiled q. No runtime
Word, exponent or cardinality is decoded into an unbounded host integer.
The unread lower bits are not changed. Standard prefix induction proves
that the final Word is floor(x/q) and the returned state is x mod q. The
RIGHT marker and fixed leading zero margin remain in place. The head returns
to one. The kernel also works when x<q and for words without a high margin;
the Context caller uses the stronger retained margin contract.

Copy the supplied modulus to one owned Word, and create Count() with value
one on one leased record tape. Compare the power Word with ring.one. At each
iteration divide that owned Word by q in place and require zero remainder.
At the first iteration, copy the quotient into the persistent cap Word.
At every later iteration, execute d^2 unchanged Count.multiply_small(q)
operations. Stop when the power equals one, then erase it.

For M=q^w there are exactly w iterations. The first quotient is q^(w-1).
There are exactly m=d^2(w-1) Count multiplications, so the result is H=q^m.
This is the already-credited shared multiplication order. The first quotient
also supplies cap, and the same traversal validates M. No second validation,
separate cap division or unary guide is needed. All source Context fields
are installed in their original order and with their original shared aliases.
The returned Count is then installed by the unchanged source save_count.

On a non-power modulus, a nonzero remainder rejects. The owned count is
closed and Arena.rollback restores the recorded set of borrowed Words.
The compiled-vocabulary check occurs before allocation. Valid-call numerical
and record costs below do not claim a complete rejecting-path tariff.

## Exact numerical bill

Count each primitive read, write and unit move as one source action. A rewind
from offset h costs 2h+3. The quotient kernel costs exactly 5B+7: its initial
msb operation costs 2B+5, and its descending quotient scan costs 3B+2.
The current bit is read once per iteration and retained as a finite symbol.

For the authenticated fixed-width Word methods, with heads at one:

```text
Arena.zero       9B+12
Arena.copy      18B+22
Arena.free       5B+8
Unsigned.compare (distinct Words) 9B+14
Ring construction                22B+41
```

These follow by counting the literal loops. Zero includes template reads,
blank-cell checks, delimiter installation and both rewinds. Copy includes
zero initialization and both payload rewinds. Free includes the final erased
RIGHT cell. Ring includes one literal, comparison, high-margin inspection
and head return. Metadata allocation and pool selection are separate below.

Context production uses two copies, one free, w quotient scans and w+2
comparisons. Hence its numerical action count is exactly

```text
C_word = (14w+59)B + 21w+80.
```

The final comparison is deliberately included even though the while condition
has already stopped. The source interpreter and verifier execute it.

## Exact record and complete constructor bill

Put n_j=bit_length(q^j), m=d^2(w-1), and N=n_m. Count() costs 22 tape actions;
the scratch allocator's blank-read adds one. One multiplication from length
n_j to n_(j+1) costs

```text
6 n_j + 4(n_(j+1)-n_j) + 5.
```

The four-term part includes new high bits and the longer return scan. Thus

```text
C_record = 23 + 6 sum_(j=0)^(m-1) n_j + 4(N-1) + 5m.
```

An empty sum gives 23 when w=1. The proof needs no floating logarithm.
The verifier computes the integer lengths independently for its finite cases.
The bound C_record <= 23+6mN+4(N-1)+5m is uniform.

Let D be the old dense highs body length. The unchanged installation uses
n=N+1 cells including RIGHT and costs 15n+5D+24 actions. This is the sum
of the separate read/write/move bill proved in PR5363. It includes clearing
the old destination, copying, rewinds, source cleanup and its idempotent
second close. The actual parked recursive caller has D=0; standalone dirty
replacement cases remain checked with D>0.

The complete executed new_context numerical/record bill is therefore

```text
22B+41 + C_word + C_record + 15(N+1)+5D+24.
```

Input construction and final disposal of the returned Context are outside
this constructor interval. The verifier separately executes disposal and
checks that all returned owned state is released. No leaked temporary is
counted as output. Pool/control bookkeeping and physical metadata compilation
are not included in this source-action bill.

## Strict improvement over already-shared traversal

The literal source performs ((d^2+1)w+1) general Word divisions. The shared
predecessor performs 2w+1: one validation traversal, one count traversal,
and the cap division. Each general divmod scans all B numerator bits. Every
iteration calls shift_add_bit, which scans all B remainder bits, even when
those bits are zero. Thus that component alone is Omega(w B^2).

For fixed compiled q and d, B=Theta(w), m=O(w), and N=O(w). The new exact
formula is O(wB+mN+B+N+D), hence O(w^2+D). The already-shared general-division
term is Omega(w^3). Both constructors retain the same m Count multiplications.
This is an asymptotic source-action comparison for fixed q,d, not a uniform
finite-state-size bound as q varies or a measured wall-clock guarantee.

At q=5,w=8,d=4,D=0, the literal, shared and fused complete constructors use
2614926, 407496 and 96660 source actions respectively. All produce the same
261-bit Count and preserve the same borrowed state. The new construction
saves 76.28 percent against the shared predecessor on this fixture.

## Storage, source boundary and limitations

On Context entry, ring.modulus and ring.one are live. The only additional
numerical Words are the owned power and cap. Thus four suffice in the fixture;
with R other live caller Words the peak is R+4. A zero template is separate
backing. Count() needs one record tape, which save_count returns empty. Its
maximum body is N+1 cells plus the LEFT marker. The installed highs output
also owns its complete N+1-cell body. Erased backing is retained capacity,
not a free resource. No extra unary guide or giant quotient table is supplied.

Source files come from the unchanged PR2753/2809 nested archive and exact
PR4025/4062 and PR5363 pins. The full loader, selected codebook, physical
pool/handle controller, arbitrary caller root closure, parent parking,
complete F(K), native/stock/precision and outer recovery are not implemented
or verified here. The source factory binding is explicit and local to this
package. No frozen runtime or selected frontier is changed. The complete
kappa calculation is unchanged. Independent human and proof-kernel acceptance
remain open.
