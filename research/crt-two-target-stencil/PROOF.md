# Two-target unary stencil, dense mask, and exceptional repair

This closes the two-target producer/consumer handoff of unpaidmoon's
[PR4644](../crt-joined-hole-repair/README.md). It specializes the existing
arbitrary-source algebra of Hiroki KUMAZAKI's
[PR4169](../crt-arbitrary-source-repair/PROOF.md) and uses ToikY's
[PR4208 producer helpers](../crt-unary-stencil-producer/PROOF.md),
[PR4201 scanner](../crt-dense-guard-scan/PROOF.md), and Ryanson Jonathan's
[PR4328 repair schedule](../pr4100-crt-repair-tariff/README.md).
The new result is a paid unary producer for two ordered disjoint windows,
joined to those interfaces. It is not a new generic repair theorem or a
complete bit-step implementation of a CRT switch.

## 1. Domain and mathematical interfaces

Let the seven unary input values satisfy

```text
G >= 1, H >= 2G, K >= G+4, J0 >= 0,
J1 >= J0+K, Y >= J1+K, B >= 0.
```

Here `B` is the back-field width; write `b=2^G` for the compact radix.
Set `L=2H+Y+B`, `M=2^L`. A complete address, in MSB-first field order, is
`(u,t,y,back)` of widths `(H,H,Y,B)`. All field values are arbitrary,
including inactive high bits of `u,t` and the complete back field. Define,
for `i=0,1`,

```text
u_i = floor(u/b^i) mod b,       t_i = floor(t/b^i) mod b,
g_i = floor(y/2^(Ji+1)) mod 2^(K-1),
Q_i = (u_i < b-1) and (t_i < b-1)
      and (2b <= g_i < 2^(K-1)-2b).
```

The good set is `Q=Q_0 intersect Q_1`. Its complement is
`E=(not Q_0) union (not Q_1)`: failure at either target marks a hole.
The intersection of the two failure sets is insufficient.

For the repair statement let `f_0,f_1` be Boolean functions of the complete
`y` field, independent of `u,t,back`, that omit **both** target bits:

```text
f_i(y xor 2^Jj) = f_i(y),  for every y and i,j in {0,1}.
```

Let `S` be the pinned compact macro with digit `i` assigned to target `Ji`,
and let `T` leave `u,t,back` fixed and replace `y` by
`y xor (f_0(y)2^J0 + f_1(y)2^J1)`. The guard scan itself needs no source
functions. The independence premise is needed when joining it to `S,T`;
omission of each function's own target alone does not suffice (#4169 §7).

## 2. Paid admission and stencil identity

Each protected input is `LEFT, 1^n, END`, followed by an initially blank
tail, with its head at the permanent `LEFT`. The inherited validator pays
for checking that word and its immediate blank successor. It does not
decide the contents of an arbitrary infinite tail. The producer allocates
eleven fixed private unary roles and one owned stencil role, all initially
blank apart from permanent `LEFT` infrastructure. Its derived values are

```text
HG=H-G, HGG=H-2G, KG=K-G, THREE=3, A=K-G-3,
TAIL=G+1, J0P=J0+1, J10=J1-J0, GAP=J1-J0-K,
YJ1=Y-J1, TOP=Y-J1-K.
```

These values are obtained by the inherited protected unary subtraction,
plus-one and constant-three scans. Positivity tests on `G,A`, together
with the subtraction underflow checks, enforce exactly the displayed
domain; all input values are nonnegative by unary representation. No host
geometry comparison admits an input. A failed subtraction writes no
partial output, so all allocated private words remain END-terminated for
rejection cleanup. On a grammar or arithmetic rejection, the private words
and empty stencil are erased and all heads return to `LEFT`, under the
representation contract above.

Write `s^n` for `n` skip atoms, `d^G` for one separately delimited digit
interval, and `g^(K-1)` for one separately delimited guard interval. The
normal successful output is exactly

```text
s^(H-2G) d^G d^G  s^(H-2G) d^G d^G
s^(Y-J1-K) g^(K-1) s^1 s^(J1-J0-K) g^(K-1) s^(J0+1) s^B.
```

The two digit intervals in each field are, in scan order, digit 1 and
digit 0. They retain separate begin/end flags even when adjacent or when
`G=1`. The upper guard belongs to target `J1`; its following single skip
omits that target's parity bit. The lower guard belongs to target `J0`;
the following `J0+1` skips omit its parity and all lower bits. Thus a zero
gap is legal, while overlapping or reversed windows are rejected.

Each guard consists of `A` leading atoms, one pivot and `TAIL` trailing
atoms. Since `A>=1`, its two threshold strings are exactly

```text
low  = 0^A 1 0^(G+1) = 2^(G+1),
high = 1^A 1 0^(G+1) = 2^(K-1)-2^(G+1).
```

Begin is set only on the first leading atom and end only on the last
trailing atom. Every other emitted cell is a canonical skip or digit
atom. The total length is `2H+Y+B`. The four digit intervals and two guard
intervals therefore test exactly the six conjuncts defining `Q`.

This proves atom identity for every admitted geometry, including inactive
high digits, arbitrary gaps, tight guards and zero back width. The fixed
alphabet and fixed tape inventory do not depend on any input value. All
producer loops branch on tape symbols; coordinates and integer lengths in
this proof belong to the observer, not the executable producer.

## 3. Exact producer and scanner action invoices

One action is one `Tape.read`, `Tape.write` or one-cell `Tape.move`.
The inherited successful helper counts, including their head returns, are:

| Helper | Actions |
| --- | ---: |
| Validate unary `n` | `4n+10` |
| Difference `a-b`, `0<=b<=a` | `8a+15` |
| Plus one on `a` | `8a+14` |
| Write three | `17` |
| Positive test on a positive word | `5` |
| Skip/digit/leading/trailing emission of `n` atoms | `6n+5` |
| Erase unary `n`, including END | `5n+7` |

Let `N=G+H+K+Y+J0+J1+B`. Summing the eleven private values gives
`W=2H-4G+2Y-J0+2`. The literal successful sequence has these costs:

| Stage | Actions |
| --- | ---: |
| Initialize eleven private words and the output | `36` |
| Validate seven inputs | `4N+70` |
| Positivity and unary arithmetic | `16H+16K+16Y-8G+8J1+175` |
| Emit stencil, END and return output head | `8L+63` |
| Erase eleven private words | `5W+77` |
| Final seven input-head checks | `7` |

For the emission row there are fourteen helper calls emitting `L-3`
atoms and three directly written atoms: two guard pivots and the skipped
upper parity bit. The cost is
`6(L-3)+5*14+2*3+1+1+(2L+3)=8L+63`; the final term is the literal rewind.
Consequently

```text
T_prod = 46H+20K+38Y-24G-J0+12J1+12B+438
       <= 70L+438.
```

The inequality uses `K<=Y`, `J1<=Y` and drops negative terms. This is an
all-size derivation from the helper counts, independently compared with
observed counters on finite cases. The producer has nineteen fixed roles.
Its exact visited cells, including input/output, markers and erased cells,
are `N+W+L+45 = 5H+K+4Y-3G+J1+2B+47 <= 6L+47`.

The unchanged #4201 scanner admits this stencil. It conjoins each interval
test and outputs the complement, hence its bit at address `x` is exactly
`1_E(x)`. Its counter is erased, its input is protected and all three
heads return. Its established invoice is

```text
T_scan = 8ML+15M+13L+18.
```

The composed producer/scanner has twenty-one fixed roles, cost exactly
`T_prod+T_scan <= 8ML+15M+83L+456`, and visited cells exactly
`N+W+2L+M+49 <= M+7L+51`. All seven geometry inputs remain unchanged,
all eleven producer work words and the scanner counter are blank, and
their heads are returned. The stencil and mask are owned outputs at LEFT.

## 4. Joining the produced mask to the existing repair

The parameter hypotheses above are the `r=2` instance of #4169: disjoint
windows, sufficient compact-digit width and the complete-target omission
condition. That proof gives a permutation `S` on the entire dirty address
rectangle, its explicit reverse word `S^-1`, and `S=T` on `Q` with
`S(Q)=T(Q)=Q`. It includes modular wrapping on exceptional addresses and
preserves the complete back field. This package does not infer those
properties from a finite permutation lookup.

After `S`, the payload at a hole `x` originated at `S^-1(x)`. Its correct
key is `T(S^-1(x))`, using the current source values at every reverse-word
evaluation. This key permutes exactly `E`. The #4328 schedule extracts the
records marked by the produced mask, performs `L` stable binary bucket
passes, and reinserts the sorted keyed records into the marked addresses
in increasing order. Thus the payload of every origin `q` ends at `T(q)`;
good records were already correct. The mask and repair scratch are erased.
This caller then retires its owned stencil using the inherited marker-driven
eraser, including its END and head return, for an additional `5L+7` actions.
That retirement is separate from the producer/scanner output invoice above.

For `h` holes and payload width `R`, the cited record/counter allowances
remain `9MR+5M` dense cells, `h(L+R)(9L+6)` sparse cells, and
`8M+4Lh+4L` counter cells, plus `h` key evaluations. This is the same
schedule and tariff, not a new all-bit invoice. The verifier's `RecordTape`
uses opaque records and width-weighted movements; its host key arithmetic
and indexing are not a literal bit-tape lowering. Producer/scanner actions
likewise exclude finite-control transitions and host observation. An exact
physical transition-table coefficient is not claimed by adding these
different models' meters.

A valid-address test at reinsertion cannot establish payload correctness:
keys `S^-1(x)` alone still permute the holes. A complemented mask marks
`Q`, where `T(S^-1(x))=x`, and can also pass that test while leaving wrong
payloads. An intersection-of-failures mask misses addresses failing only
one target. The controls must check the intended mask and final payloads,
not merely successful reinsertion or key-set coverage.

## 5. Evidence, attribution, and limits

The verifier separately checks a grid of produced stencils and exact
action/space counts, and exhausts the declared small two-target geometries
through the scanner, reverse evaluator and record repair. Its stored
receipt specifies the actual cases and controls. These finite replays
test implementations; the quantified stencil and cost arguments above
apply beyond that grid. No larger-address replay is implied.

Credit Cinna Davis/#4100 for the compact caller; ToikY/#4208 and #4201 for
the paid unary helpers and dense scanner; unpaidmoon/#4644 for the joined
one-target pipeline and this handoff; Ryanson Jonathan/#4328 for the
sparse tariff; Hiroki KUMAZAKI/#4169 for the arbitrary-source inverse; and
Douglas Colkitt and John-Michael Smith/#763 for the inherited compact and
exceptional-repair argument. Substantial OpenAI Codex assistance was used.

Unary descriptor construction from the actual caller, variable target
count, last-`K` boundary targets, physical placement, ordinary interchanges,
paid binary inverse keys and a common complete machine invoice remain
outside this result. No selected frontier, exponent, full CRT supplier or
proof-assistant verification is changed or established here.
