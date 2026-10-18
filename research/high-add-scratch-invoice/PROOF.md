# Ordered high-field ADD: local reserve and physical I/O

This is a source-level cost and lifetime proof for the **unchanged**
`kernels.added` in Jose Manuel/jmbarrancoml's PR2915, including its actual
PR2809 `ScratchPool.install` specialization and retained `stream.add_pass`.
It answers the ordered-ADD part of Nick Petalas's PR2982 handoff. It does not
complete that handoff's single-cube setup, sign/translation composition or B1
swaps, and it does not derive a whole bootstrap-stage stock coefficient.

## Domain and boundary

Let Q >= 3 be odd, B,M,S >= 1 be integers, and c belong to
{-4,-2,-1,1,2,4}. Here M is the middle spectator multiplicity, **not** the
modulus. Set

```
b = bit_length(Q)+1,
l_X = bit_length(X),
V = B Q M Q S.
```

The source contains one complete Boolean packet ordered as (prefix,x,middle,y,
suffix). Its action is y -> y+c*x mod Q. B,M,S arrive as canonical Count
encodings; the three marginal copies have exactly one extra high zero.
The initialized Ring has modulus Q, its one word, and the minimal b-digit
template. All borrowed heads begin at their origins. Distinct payload,
numerical and count roles obey the retained ownership contract; any already
occupied pool roles and numerical slots remain charged to the caller.
The source and contexts are read-only, and the output is a distinct owned
dense V-bit stream with its head restored. Dirty entry roles are preserved.

Count physical Tape reads, writes and unit moves once, including operations
through PhysicalWord and Lease aliases. One acquisition costs the pool's
actual blank read. Finite-control selection, initial marker/template
provisioning, installation/compilation and permanent inventories are outside
this local I/O currency. These are not machine-step constants. Counted
initialization is the allocation and initialization **inside** `added`, not
the enclosing high-bank setup. Successful return is the boundary; arbitrary
interrupted-macro recovery is not claimed.

For each fixed prefix, x and middle coordinate, the first traversal splits
the Q suffix blocks after Q-offset, with offset=c*x mod Q. The second
traversal writes the trailing offset blocks followed by the leading blocks.
This rotates their y address by offset, preserving each suffix block's bit
order. Both traversals use the same prefix/x/middle nesting, so no spectator
coordinate moves. Only head movements touch the borrowed input and Counts;
their rewinds restore the entry heads.

The numerical margin suffices: residues are below Q<2^(b-1), a modular sum
is below 2Q<2^b, and Q-offset is between 1 and Q. The fixed literal is at
most four and fits b>=3 digits. Binary division keeps remainder below Q
before each shift. These inequalities discharge the arithmetic width checks;
the reserve proof below discharges the local allocation checks.

## Scratch and numerical capacity

The three marginal Counts persist throughout the call. `add_pass` then owns
left, right and output. Inside either traversal the maximum live chain is:

| Roles | Count |
|---|---:|
| Marginal Counts | 3 |
| Left, right, output payloads | 3 |
| Outer, source-coordinate and middle countdowns | 3 |
| Split-block countdown | 1 |
| Suffix-bit countdown, when S > 1 | 1 |

`copy_blocks` closes its block/bit countdowns before returning. Each middle,
source-coordinate and outer countdown closes before its next instance.
Marginal construction allocates one stream per result, with no hidden
stream temporary. Word arithmetic uses the separate numerical bank.
Consequently exactly **10+[S>1] free scratch roles** suffice, independent of
Q,B,M and the coefficient. This is a bound on every allocation prefix, so it
excludes a first scratch-capacity failure when other source conditions hold.

The leading split has Q-offset > 0 at every x. Hence the nested block
countdown, and for S>1 its bit countdown, really occur while all earlier
listed roles remain allocated. Thus the bound is attained in every call in
this domain, not merely in the saved examples. All scratch leases except
the one output close before return. Clearing that output releases the last
new lease; entry leases survive.

At numerical coefficient preparation, the literal, division scan, quotient,
remainder and new shifted/subtracted remainder need at most five new slots.
The old remainder is freed before the subtraction result is allocated.
After preparation only the coefficient persists. Each outer iteration adds x.
`Ring.multiply` needs at most four further slots: scan, old accumulator,
new addition total and its conditional modular-reduction output. They are
reused, not accumulated over the bit scan. The following leading-count
subtraction needs only offset and leading beside coefficient and x.
Thus **six free numerical slots above all entry residents** suffice at every
allocation prefix. This includes both pending and completed results.
Outside the coefficient callback this is Ross Richardson's PR2810 bound for
the same `stream.add_pass` source; the callback's at most five slots compose
with it by maximum, as PR2810 states. The
Q=3,c=-4,B=M=S=1 fixture attains six; one fewer rejects at the real allocator.
The input modulus and Ring.one, and any additional caller residents, are
entry resources, not part of those six.

A useful occupied-content corollary, excluding LEFT markers and every entry
resource, is

```
additional occupied symbols <= 2V + 2(l_B+l_M+l_S) + 8b + 20.
```

Left+right together contain at most V bits and output at most V. The three
marginals occupy l_B+l_M+l_S+6 symbols, including RIGHT. The five possible
countdowns occupy at most (l_B+2)+(b+1)+(l_M+2)+(b+1)+(l_S+2).
Six new numerical words add 6(b+1). Omitting the absent suffix countdown
only improves this upper bound. A local inventory of eleven scratch and
six numerical roles adds seventeen LEFT markers. Previously retained blank
backing, permanent bank templates/markers and simultaneous caller categories
are separate: this occupied-content bound is not a backing-capacity theorem.

## Exact non-arithmetic invoice

Let C(n,l) be the complete pooled countdown cost, from construction on an
l-digit input through draining and disposal, where l >= max(1,bit_length(n)).
Arham Tahir's PR2877 countdown identity for this Counter, derived earlier by
ywz65's PR2473, plus the pool's one acquisition read, gives

```
C(n,l) = 15n + 14l - 5 popcount(n) + 37 + 4[n=0].
```

PR2877 states both branches for every width d>=max(1,bit_length(n)):
15n+14d-5 popcount(n)+36 for n>0 and 14d+40 at zero. Each additional leading
zero costs six input-copy operations, two extra rewind operations and six
normalization operations. For n=0, direct constructor normalization followed
by clearing the two-symbol zero/RIGHT body gives 14l+41. As both
predecessors note, the positive formula is not valid at zero.

An independent count makes the endpoint convention explicit. For n>0 and
t=bit_length(n), construction costs 10t+16+14(l-t), including acquisition.
Draining costs 15n-5 popcount(n)+4t+4: ordinary decrements with k trailing
zeros cost 5k+10; the t-1 nonfinal powers of two add four each; the final
one-to-zero decrement adds eight. Use sum_(a=1..n) v_2(a)=n-popcount(n).
Disposal of the canonical zero costs seventeen. At n=0 construction is
14l+24 and disposal is again seventeen. This rederives both branches from
the literal loops; PR2877 and PR2473 retain credit for them.

For the marginal suffix, the literal `one_bit_suffix` probe costs

```
P(S) = 4 if S is even; 15 if S = 1 mod 4; 12 otherwise.
```

In particular P(1)=15, because this argument has a high-zero margin. It is
not the canonical one-digit suffix probe used in PR2982's wrapper.

The complete lifecycle of a marginal copied from an l-digit canonical Count
costs 27l+63: construction/margin 18l+35 (including acquisition),
`positive_extent` 4l+11, and disposal 5l+17. These follow by counting literal
reads/writes/moves in `Natural`, with no decoding of runtime extents.

Put

```
J(Q,b) = C(0,b)+C(Q,b)+2 sum_(n=1..Q-1) C(n,b).
```

The coefficient is a signed power of two and Q is odd, so multiplication by c
permutes the offsets 0,...,Q-1. The two split counts are offset and Q-offset.
Thus J accounts for every block countdown in one source-coordinate cycle,
including the zero block. This permutation argument is why the following
invoice is independent of c. Nonunit coefficients are outside this claim.

Let N be the physical traffic inside the explicitly enumerated numerical
calls in the next section. Every other physical operation has exact total

```
W = sum_(X=B,M,S) (27l_X+63) + 23V+32
  + 2 C(B,l_B+1)
  + 2B C(Q,b)
  + 2BQ C(M,l_M+1)
  + 2BM (J(Q,b) + 2Q P(S))
  + 2BMQ^2 [S>1] C(S,l_S+1).
T = W+N.
```

There are two traversals. Each copies V payload bits at five operations per
bit. The split-stream rewinds, source rewind, split-stream disposal, output
rewind, three extent probes and three payload acquisitions supply the
remaining 13V+32, for 23V+32 in all: PR2473's exact unpooled payload bill
23V+29 plus the three acquisitions. The counter rows then follow the actual nesting of outer,
source-coordinate, middle, split block and suffix bit. Counter costs include
reads of numerical input Words; these are **outside** N and are not counted
again as arithmetic. No retained alias meter is added to its physical tape.

Exactly

```
8 + 2B + 2BQ + 4BMQ + 2BMQ^2[S>1]
```

leases are acquired. This includes the three marginals, three payloads and
both outer counters. Acquisition count differs from peak live inventory.

For a uniform upper bound, C(n,l) <= 16n+16l+64, l_X <= X, and b <= Q.
The following contributions divided by V bound all terms of W:

| Term | Upper bound / V |
|---|---:|
| Three marginal lifecycles | 30 |
| Payload, fixed probes and acquisitions | 239/9 |
| Outer countdowns | 224/9 |
| Source-coordinate countdowns | 320/9 |
| Middle countdowns | 224/3 |
| Split-block countdowns | 544/3 |
| Marginal suffix probes | 20 |
| Suffix-bit countdowns | 224 |

For example C(X,l_X+1)<=32X+80<=112X; a split pair is at most
16Q+32b+128<=272Q/3. The table sums to **617**, so W<=617V<640V.
It permits the suffix countdown even when absent, and uses Q>=3, B,M,S>=1.

## Numerical traffic is included

All numerical word bodies have b digits. Heads stay between the origin and
RIGHT. A rewind costs at most 3b; `msb` at most 6b; a zero test at most 9b;
and erasure at most 10b, for b>=3. From the literal loops in the retained
`words.py`:

| Operation | Physical I/O upper bound |
|---|---:|
| Arena.zero (copy initialized template) | 13b |
| Arena.copy | 28b |
| Literal of magnitude at most 4 | 19b |
| Unsigned.compare | 18b |
| Unsigned.add/subtract | 36b |
| Unsigned.shift_add_bit | 28b |
| Unsigned.divmod | 160b^2 |
| Ring.add/subtract | 100b |
| Ring.negate | 128b |
| Ring.multiply | 300b^2 |
| Fixed selected coefficient, including reduction/sign | 256b^2 |
| Increment in place | 10b |

For clarity, these are deliberately rounded source bounds, not fitted timing
ratios. Arena.zero costs exactly 9b+12 on initialized roles, at most 13b.
Copy costs at most 27b+1. Add/subtract cost at most 35b+2.
In division there are b iterations, each costing at most 104b, and setup,
scan teardown and the final probes cost at most 94b+4. This is below 160b^2.
In multiplication the two modular additions per bit cost at most 200b,
their old-result frees at most 20b, and the three loop operations at most b
per iteration. Setup/teardown is at most 111b+2. Thus
221b^2+111b+2<300b^2. Zero/one shortcuts are cheaper.
The fixed coefficient costs at most 160b^2+177b<256b^2, including literal,
division, frees and optional negation. Every bound uses b>=3.

The entire top-level arithmetic partition in `added` is:

| Numerical call | Multiplicity | Per-call bound |
|---|---:|---:|
| fixed_coefficient | 2 | 256b^2 |
| coefficient/modulus comparison | 2 | 18b |
| allocate x=0 | 2B | 13b |
| multiply coefficient*x | 2BQ | 300b^2 |
| subtract Q-offset | 2BQ | 36b |
| free offset and leading | 2BQ | 20b |
| increment x | 2B(Q-1) | 10b |
| free x / coefficient | 2B+2 | 10b |

Nested arithmetic calls belong to their enclosing row, not to another row.
These exhaust numerical work in this local routine. Their sum is

```
N <= 512b^2 + 56b + 26Bb + 600BQb^2 + 132BQb
  <= 832 BQ b^2.
```

The second inequality follows by dividing by BQb^2 and using B>=1, Q>=3,
b>=3: the resulting upper bound is 7414/9 < 832. Also b^2<=4Q for every
odd Q>=3. For Q=3 check 9<=12. Otherwise L=bit_length(Q)>=3, and
(L+1)^2<=2^(L+1)<=4Q; the first inequality follows by induction from L=3.
Consequently N<=3328 BQ^2<=3328V, and

```
T <= (617+3328)V = 3945V < 4096V.
```

Consuming the already rewound output by clearing it adds exactly 5V+7.
Since V>=9, it adds less than 6V; the convenient disposed bound is 4102V.
No sharpness is claimed for these traffic constants. The scratch count is
sharp; the numerical upper bound is attained by a stated fixture.

## Checking and remaining boundary

The independently implemented invoice is compared with the complete actual
source on 109 full packets, including every Boolean basis column of the
nine-bit Q=3 packet. The other fixtures use deterministic payloads; they are
not a full GL64 Boolean-column census. Independent modular addressing checks
endpoints, and physical meters are compared both by raw method interception
and by the sum over unique physical tapes. Fifty-one zero/padded countdown
checks and thirty-six separate arithmetic checks through 82-bit words
exercise the delicate boundaries. The all-width result rests on the written
source proof, not extrapolation from those finite executions.

Controls reject one fewer scratch role, one fewer numerical slot, a wrong
coefficient, an endpoint-preserving extra read, noncanonical borrowed-count
padding that changes only cost, omitted zero-block charges, corrupted source
pins and Boolean/integer receipt substitution. Failed-call fixtures are
explicitly cleaned by the harness; this does not prove source exception safety.

The actual high route additionally needs encoded extent/high-bank setup,
sign and carry compositions, and its B1 swaps. In particular a reversed-field
ADD may use two swaps outside this kernel, and those charges do not disappear.
Combining local occupied-content bounds with backing capacity, fixed inventories,
native/recursive lifetimes, root stock and H2 remains open. This is not a new
supplier, a whole-stage reserve, a selected-frontier change or a formal theorem.
