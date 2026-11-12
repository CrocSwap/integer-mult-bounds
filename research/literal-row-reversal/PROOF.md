# Literal whole-record reversal at the elementary stream interface

## 1. Exact claim and source boundary

Fix positive integers `P,R,B`, let `V=PRB`, and let
`E=ell(P)+ell(R)+ell(B)`, where `ell(n)=floor(log2(n))+1`.
There is one fixed, 13-tape, four-symbol program that maps a bit array

`A:[P] x [R] x [B] -> {0,1}`

to `A'(p,r,b)=A(p,R-1-r,b)`. Every complete B-bit record retains its
internal bit order. The output occupies the original DATA owner and exact
original field. On success the three descriptor tapes, their heads, all
other heads, all private banks, and all opaque exteriors are restored.

The actual program is `compile_reverse()` in `reverse.py`: 524 locations,
alphabet `{'_','0','1','|'}`, and no runtime compiler argument. Each executed
instruction is one scanned-symbol branch, one-cell write, unit head move,
fixed jump, or halt. There is no bulk transfer, computed address, decoded
shape, multiplication service, host loop, or input-dependent instruction
generation in its execution path. The fixed Python loops only emit this
single finite graph. `check.py` uses decoded integers solely as test fixtures
and independent expected-value/cost observers.

The canonical elementary interface is exactly
[02-streams.tex at e545235](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/upstream/build/sections/02-streams.tex).
It gives lexicographic implicit addresses, complete rows on `[P]x[R]x[B]`,
and a fixed number of collapsed lengths supplied in canonical binary on
descriptor tapes. Its separate Gamma convention applies to interfaces
that explicitly supply a concatenated header. This program uses the
elementary binary ABI directly; it does not silently receive or decode a
nine-Gamma layer header. Producing the three collapsed lengths from a
growing coordinate list is still caller work, as the source states.

The two-stack idea is also already in that source's ordered-affine proof:
its modular negation fixes row zero and reverses the remaining rows, first
popping entire blocks and then restoring their internal bit order. This
package does not claim a new reversal algorithm, new affine theorem, or
new asymptotic exponent. Its result is the literal, same-owner realization,
exact complete census, and retirement/history contract at this interface.

## 2. Encoded entry contract

The tapes, in order, are `PDESC,RDESC,BDESC,DATA,OUTPUT,PTR,RTR,BTR,DOUBLE,
HTRACE,GROUP,RECORD,DTRACE`. They are thirteen distinct physical tape owners.
Each head starts at its own origin `u_i`, which can be any integer. Origins
are not supplied as numerical values to the controller.

On each of the first three tapes, the field starting at its origin is the
ordinary MSB-first binary representation of its positive parameter, with
leading `1`, immediately followed by a blank. The program reads this blank
terminator but never crosses it. DATA contains exactly V consecutive bits,
followed immediately by a blank. Other public cells can hold arbitrary
opaque symbols in the fixed alphabet and are preserved. A later field after
the terminator is not part of this invocation's descriptor or DATA field.

The last nine tapes are private work roles. Their guard cell at `u_i-1`
and the intervals through the caps in Section 6 must be blank at entry.
This is an ownership/blankness precondition; the program does not claim
that two local reads establish a whole blank tail. All cells outside the
listed private intervals may be opaque. The first 27 instructions place
nine temporary guards; the last 27 erase those guards. No public guard is
needed or overwritten.

An invocation with a missing bit, an invalid symbol before a terminator,
a nonpositive/noncanonical descriptor, or an extra immediate DATA bit
rejects before any DATA write, provided the private entry contract holds.
Rejection is the finite table's missing-branch endpoint, represented by
`invalid scanned symbol` in the reference interpreter. No rejection-time
head return, private cleanup, or subsequent reuse is asserted. An arbitrary
malformed string with no finite terminator is outside the terminating-input
contract. No input-dependent safety budget is part of the abstract program.

## 3. Binary guides without decoded arithmetic

`binary_descriptor` first insists on a scanned leading `1` and writes one
unary mark on its target. For each subsequent scanned binary digit b, it
copies every existing target mark twice to DOUBLE and appends one extra
mark precisely on the finite b=1 branch. It clears the old target, copies
DOUBLE back with erasure, and returns both heads locally. Thus after every
prefix the target contains exactly its numerical value in unary. Induction
on the number of read digits proves the final guides have lengths P,R,B.

Every advance of a public descriptor head writes one mark to HTRACE.
`trace_return` subsequently erases one trace mark for each backward unit
move, ending at the saved origin. It does not look up an origin or seek to
an integer address. HTRACE is retired before decoding the next descriptor.
DOUBLE is also blank with its head returned after each digit. Both can be
reused across all three descriptors.

For completeness, the guide construction is linear in the represented
value, although the descriptor is logarithmic. If `n` has bit length ell
and popcount s, the strict prefix values sum to `n-s`. Each doubled prefix
and optional extra bit is at most n. The construction therefore costs
O(n+ell) and never visits above cell n of either unary role. Since each of
P,R,B is at most V, paying for these unary guides is legitimate here. This
argument would not justify unary decoding of an unrelated parameter that
can exceed the data volume.

## 4. The two reversals and prefix isolation

At each `prefix` entry, PTR's position names the next prefix without storing
its address numerically. GROUP and RECORD are blank at their origins; RTR
and BTR are at their unary origins; OUTPUT is at its current append frontier.

The load loops copy R successive B-bit records from DATA to GROUP. BTR is
rewound after each record and RTR after the whole group. DATA advances V
positions over the entire call; each advance appends a DTRACE mark. No DATA
cell has yet been written. At the end of a group, GROUP contains exactly

`A(p,0,0)...A(p,0,B-1), ..., A(p,R-1,0)...A(p,R-1,B-1)`.

Moving GROUP back one cell exposes the last bit. The pop loops read B bits
backward into RECORD, erasing GROUP as they go. For the j-th popped record,
RECORD therefore contains the bits of original row `R-1-j` in reverse order.
The emit loop then scans RECORD backward into OUTPUT, erasing RECORD. This
second reversal restores the B-bit suffix order. It ends on RECORD's guard,
then moves once to its origin. Repeating R times ends exactly on GROUP's
guard; checking that guard and moving once restores GROUP's head. RTR is
rewound before PTR advances to the next prefix.

This inductively establishes prefix isolation and the claimed involution.
In particular, reversing all V bits, reversing all records across prefix
boundaries, or omitting the second reversal would implement different maps.
R=1 and B=1 are permitted; the corresponding identity work is still paid.

Only after PTR reaches its blank terminator does the program inspect the
next DATA cell. A bit there rejects for excess cardinality. A blank proves
that precisely the descriptor-derived volume has been consumed. A shortage
would already have rejected at a required DATA-bit read. The output has
been staged in its entirety and DATA has not been modified.

The program returns DATA through DTRACE, rewinds OUTPUT, and commits its V
bits to the same DATA tape while erasing OUTPUT and constructing a new
DTRACE. It returns DATA through that trace and OUTPUT through its blank
visited body. It rewinds PTR, clears all three guides, removes the nine
private guards, and halts. The restoration claim follows cell by cell from
these scans and the per-prefix invariants. Each DATA cell is written exactly
once during this final commit, and descriptors are never written.

## 5. Exact complete cost

Count every table instruction, including local branches, fixed jumps and
halt, as one step. This is a valid restriction of the canonical tape model;
no simultaneous multi-tape action is being assigned unit cost off-table.
Let `s(n)` denote the number of one bits in n. The following are exact
instruction counts on their stated valid entry invariants:

| Helper | Executed instructions |
| --- | ---: |
| Rewind from position n over n allowed symbols to a guard | `3n+3` |
| Clear n unary marks and return | `7n+4` |
| Copy n unary marks, repeat r, append e, optional source erasure z in {0,1} | `(6+5r+z)n+5e+7` |
| Trace-return over n marks, erase trace and return both heads | `5n+3` |
| Decode a canonical positive binary n and restore its descriptor | `47n-30s(n)+28ell(n)-31` |

To check the last row, after the leading one each new digit b and previous
prefix v uses `47v+17b+23` instructions, including that digit's read and
descriptor advance. Leading initialization, final blank read and trace
return total `9+5ell(n)`. The strict prefixes sum to `n-s(n)`, and the
remaining one digits number `s(n)-1`, giving the stated expression.

The program's major stages have the following exact complete counts:

| Stage | Count |
| --- | ---: |
| Install nine private guards | `27` |
| Decode P,R,B | Sum of the three binary-decode counts |
| Load/pop/emit all prefixes, including all three loop tests and local resets | `29V+23PR+14P+1` |
| Final cardinality test, DATA returns, OUTPUT rewind/commit/erase, guide retirement, guard retirement and halt | `24V+10P+7R+7B+57` |

For example, each prefix's load part costs `R(12B+7)+1`; its GROUP setup
costs `3R+4`; its pop/emit part costs `R(17B+10)+1`; its final local reset
costs `3R+7`. Adding the P+1 prefix tests gives the third row. The final
stage includes both DATA trace returns, each `5V+3`, both OUTPUT rewinds,
each `3V+3`, the complete `8V+1` commit, and all remaining retirement work.

Consequently the exact accepting cost is

`T = 53V + 23PR + 71P + 54R + 54B + 28E`

`    - 30(s(P)+s(R)+s(B)) - 8`.

It is independent of payload bits and of absolute origins. Since
`PR,P,R,B <= V`, this implies the convenient uniform envelope

`T <= 256(V+E+1)`.

Also `E <= log2(V)+3`, so it is a complete O(V) elementary scan, including
all shape parsing, unary guide construction, source access and return,
copies, restoration, and same-owner installation. The earlier speculative
budget `65536(V+E+1)` in the task checkpoint is therefore substantially
looser than the proved census; this constant has no kappa significance.
No source acquisition, conversion from a different public ABI, or transport
to the entry heads is silently included: those are separately supplied
and charged caller tasks.

## 6. Historical backing and repeated clean calls

Let `M=max(P,R,B)` and `L=max(ell(P),ell(R),ell(B))`. The private roles visit
only the following relative intervals, inclusive of guard and blank endpoint:

| Role | Visited interval relative to its own origin |
| --- | --- |
| OUTPUT, DTRACE | `[-1,V]` on each role |
| PTR | `[-1,P]` |
| RTR | `[-1,R]` |
| BTR, RECORD | `[-1,B]` on each role |
| DOUBLE | `[-1,M]` |
| HTRACE | `[-1,L]` |
| GROUP | `[-1,RB]` |

The public descriptor head for n visits `[0,ell(n)]`; DATA visits `[0,V]`.
These bounds follow directly from the loop invariants: in particular,
GROUP contains only one prefix and RECORD only one complete row. DOUBLE's
largest unary prefix cannot exceed the final parameter it is decoding.

Let K0 be the total actual pre-entry historical backing of the nine private
owners, counting cells even if their current contents are blank. No erase
deallocates those historical cells. By a union bound on the listed intervals,
the total private backing at any time in this call is at most

`K0 + 2V + P + R + 2B + M + RB + L + 18`

`<= K0 + 8V + E + 18`.

All cells written in those intervals are blank again on success. Older
private tails are already blank by induction from prior successful calls;
this call never needs to rescan a larger historical capacity. Thus a much
smaller subsequent call still has its own exact current-shape time T. A
later regrowth reuses the same clean roles with their retained histories.
This is not a claim that recreating a Python class erases tape ownership or
backing. The reuse checks retain the identical thirteen Tape objects and
their historical low/high observers across every success.

At fixed origins, the repeated-call interval on each role is nested within
the largest cap reached by that role. The precise aggregate is the sum of
these per-role maxima, combined with actual initial history; it is not the
maximum of the per-call sums as an equality. A valid coarser bound after any
finite call sequence is `K_initial+8V_max+E_max+18`. If origins change, retain
the per-role absolute history unions and any caller transport corridors.
There is no max-current-volume bound on arbitrary translated histories.
Caller repositioning, replacement source encodings, and entry blankness
remain real preconditions/work. No private history or primitive tape state
is reset in this contract.

## 7. Scoped native translation consequence

If R is `2^f`, `f>=1`, then for the f-bit coordinate q,

`2^f-1-q = q XOR (2^f-1)`.

Therefore the literal map applies X (binary bit flip) to every digit in
that entire contiguous f-bit coordinate block, with all prefix and suffix
spectators preserved. This follows from the address identity, not a finite
search. It permits arbitrary payload records; no numerical format or
Gaussian arithmetic premise is needed.

For a fixed translation vector on a fixed number m of contiguous binary
coordinate positions, apply the program with R=2 at the positions whose
translation bits are one, supplying their correct collapsed P and B each
time. There are at most m calls. Their permutations compose to XOR by the
fixed vector, with the same DATA owner and clean bank reuse. The sum of
their exact complete costs is O_m(V); their nine private roles are shared,
not recreated. This is a compositional mathematical corollary at the
elementary entry boundary, not a newly emitted literal multi-call caller.
Descriptor production, call scheduling and any required head transport
remain separately charged unless already supplied by such a caller.

There is a concrete retained source join: the exact
[selected compact adapter's flip_digit](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/selected-complex-compact-adapters/streams.py)
uses left-numbered position j among d binary address digits and base record
width b. On the intended complete d-bit rectangle `V=2^d b`, the matching
call is `P=2^j, R=2, B=2^(d-j-1)b`. The pinned function itself also accepts
other lengths divisible by `2B`; on that larger accepted domain the matching
prefix length is `P=V/(2^(d-j)b)`, not necessarily `2^j`. Both maps exchange
the two complete suffix blocks within every prefix. The retained Python
source computes these quantities
and returns a new owner; this program instead consumes their supplied
encodings and commits on its own DATA owner. Map equivalence does not
silently lower that old host caller or its descriptor production.

No claim is made that selected digits at stride K are contiguous. For
example, XOR `1010` on a four-bit address differs from full reversal's XOR
`1111`. Reversing a wider field to avoid paying for packing would be wrong.
General affine maps, data-dependent controls, the source's full modular
negation with fixed zero row, and the complete native monomial caller are
still outside this package. The selected multiplier and all five global
foundational assumptions are unchanged; no new kappa is claimed.

## 8. Evidence and remaining obligations

`check.py` authenticates all nine exact source files, audits the graph's
finite instruction language, and compares every accepting run's step count
to Section 5's exact formula. It checks current visit caps, original owner
identity, all heads, every descriptor/private/exterior cell, and the exact
number of DATA writes. Its direct flat-index involution oracle does not
use the program's two-stack algorithm.

Normal and optimized Python runs agree byte for byte: 3,814 successful
packets, including every payload on all 38 positive shapes with V<=8,
plus 64 seeded larger packets; 31,833 payload bits; 4,053,639 successful
instructions. Twelve invalid packets reject before DATA writes. Six actual
graph mutants and two explicit wrong-permutation alternatives are detected.
Six grow/shrink/regrow calls retain the same owners and monotonically
retained historical backing. Twenty-one map comparisons use the exact
pinned old `flip_digit` source, and five fixed-vector examples use fifteen
literal calls, including a nine-coordinate example. These are bounded
regression/adversarial checks, not universal proofs or proof-kernel review.

The universal result is the finite-graph invariant and census proof above.
Independent reviews, when complete, are recorded separately in REVIEW.md.
Open caller obligations include literal collapsed-descriptor production and
scheduling where they are not supplied, paid selected-bit packing for
strided layouts, complete native affine/phase composition, and a failure
retirement contract if such recovery is required. No unresolved item is
treated as discharged merely because the local permutation is now literal.

