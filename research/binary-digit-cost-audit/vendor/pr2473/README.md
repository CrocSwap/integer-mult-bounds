# Independent local cost audit of the encoded ADD in PR2449

The fixed-current-prefix ADD in Jose Manuel's [PR2449](https://github.com/CrocSwap/integer-mult-bounds/pull/2449)
has the claimed linear counter and payload bill, under its canonical extent
and restored deterministic callback contracts. This audit supplies **exact
all-length counter formulas**, counts the full split/merge scratch cleanup,
and separates numerical preparation from payload movement. No failure of the
stated local cost implication was found.

The reviewed head is `ef4640fbf9c360ef66dbc5d29916e741d515bf39`.
Six unchanged source files, their Git blobs and SHA256 hashes are retained in
[SOURCES.json](SOURCES.json). Authentication precedes runtime imports.
The review does not implement the selected residual being developed in
Discussion2319, nor certify the complete selected callback or global caller.
The selected frontier is unchanged.

## Added implication and precise contract

PR2449 PROOF sections5–6 invoke amortized counters to obtain `C_q V`.
We derive that billing directly for the pinned `stream.py` and `records.py`,
including zero ranges, the final decrement, head returns and erasure.
This is an independent written all-length audit, supported by finite checks;
the predecessor already provides the ADD construction and its endpoint proof.

Fix integers `M>=2`, `U,G,S>=1`, `0<=c<M` and complete layout

```
[U] x [M] x [G] x [M] x [S],       V = U M^2 G S bits.
```

`S` counts bits, including any data suffix. The modulus has exactly
`L=bitlength(M)+1` bits. Each spectator extent A has its own
`k_A=bitlength(A)+1` bits. Work tapes start blank with the declared local
left markers; numerical roles are available as in the source contract.
The source has exactly V opaque bits. The callback returns an owned
canonical coefficient word, with value **the same c on split and merge**,
and preserves its inputs and restores its own work and heads.

The actual `add_pass` calls the callback **twice total**, once before each
whole traversal. It is a fixed-current-prefix call; `before` is a spectator
of that fixed coefficient. The source proof's phrase “once per prefix” must
be read in that enclosing fixed-prefix sense for this executable. Applying
different raw headers across U requires an outer prefix driver or a changed
stream primitive. This is an implementation boundary, not a finding that
PR2405's separate varying-header theorem is false. Reusing different values
on split and merge can silently produce a wrong permutation even when every
split bit is consumed, as the control below demonstrates.

## 1. Exact all-length countdown bill

Write `s=popcount(N)` and let k be the input word length, with `k>=2` and
`0<=N<2^k`. Count one tape-symbol read, write or unit head move as one
operation. For construction, all N decrements and `close`, the counter's
**own tape** has exactly:

| N | Reads | Writes | Moves |
|---|---:|---:|---:|
| positive | `7N-2s+2k+11` | `2N-s+3k+4` | `6N-2s+4k+14` |
| zero | `2k+12` | `3k+5` | `4k+16` |

Reading and restoring the separate input word adds exactly
`(3k+3, 0, 2k+4)`. Those operations are charged to its numerical arena in
the source, **not** to `traffic["counters"]`. Neither meter alone is the
whole machine cost.

Here is a derivation rather than an extrapolation from measured values.
For N>0 put `b=bitlength(N)` and `z=k-b`. Construction appends k bits and
a delimiter, removes z high zeroes, and rewinds. Its own-tape bill is

```
(2k+3, 3k-2b+1, 4k-2b+4).
```

For a decrement of n>1 let `t=v2(n)`. If n is not a power of two, its
bill is `(2t+5, t+1, 2t+4)`. If n is a power of two, removing the top
digit adds `(0,2,2)`. The final `1 -> 0` step instead costs `(6,4,8)`:
it preserves the one-digit zero representation. There are b powers of
two in `[1,N]`, and

```
sum_(n=1)^N v2(n) = sum_(j>=1) floor(N/2^j) = N-popcount(N).
```

Thus all decrements cost `(7N-2s+1, 2N-s+2b+1, 6N-2s+2b+2)`.
Closure of the canonical zero costs `(7,2,8)`, giving the first row.
For N=0, construction scans all k zeroes and installs a one-digit zero;
its bill is `(2k+5,3k+3,4k+8)`. The same closure gives the second row.
Input-word traffic follows separately from its initial rewind, two reads per copied bit,
copy, delimiter read and final rewind. These arguments hold for every
finite input length; the finite replay corroborates the source binding.

Let `F(N,k)` be the sum of the three own-tape entries. Including input
traffic gives

```
C(N,k) = 15N-5popcount(N)+14k+36   (N>0),
C(0,k) = 14k+40.
```

In particular `C(N,k)<=15N+14k+40`. At canonical positive widths,
`k<=2N`, so `C(N,k)<=83N`. For target-range counts t and M-t, both
stored at width L, `L<=2M` and `M>=2` give

```
C(t,L)+C(M-t,L) <=111M,
```

including t=0. Counting zero ranges as free would be incorrect.

## 2. Actual nested counters and payload movement

For one split or merge traversal the counter invocations are:

| Counter | Multiplicity |
|---|---:|
| U | 1 |
| M source atoms | U |
| G | UM |
| t_x and M-t_x, where `t_x=cx mod M` | UG for each x |
| S bits | `UM^2G` |

The source constructs a suffix counter once per target block, including
both target ranges together. Their lengths add to M. Applying the preceding
bounds gives at most

```
83U + 83UM + 83UMG + 111UM^2G + 83V <=443V
```

operations per traversal, or 886V for both. The three initial canonical
spectator checks have `(2k+3,0,2k+4)` word bill and total at most
`8(U+G+S)+21<=30V`, because V>=4. Counter and extent-validation traffic
therefore costs at most **916V** symbol operations, excluding arithmetic
on coefficient/source words. This constant is deliberately loose.

Payload movement has an exact, coefficient-independent bill across source,
the two scratch tapes and output:

```
(reads,writes,moves) = (10V+13, 3V, 10V+16).
```

Split copies V bits, merge copies V bits, each through one source read and
one append (read/write), with one move on each tape. Source rewind adds
`(V+1,0,V+2)`. The two scratch rewinds together add `(V+2,0,V+4)`.
The source-end and split-consumption checks add three reads. Clearing both
scratch tapes from their consumed ends adds `(3V+6,V,3V+8)`; this includes
both rewinds around erasure. Output rewind adds `(V+1,0,V+2)`. Summing
gives the displayed formula, including an empty scratch tape when c=0.
Its total is `23V+29<=31V`. Thus the nonarithmetic movement and counters
have a conservative **947V** bill, including all these heads and cleanup.

The ordering proof is unchanged from the construction: at every fixed
`(u,x,g)`, split takes the first M-t target blocks into left and the last
t into right; merge emits right then left. This maps input y to `y+cx`
and fixes all spectators and within-block bits. It never branches on an
accepted payload bit's value. Replacing c by -c restores every bit.
The source remains preserved, both split tapes are blank at return, and
all payload heads return to their declared origins.

## 3. Numerical preparation and the conditional CqV conclusion

This audit keeps the callback tariff B and modular arithmetic tariff
separate. Source `words.py` uses O(L^2) modular multiplication, O(L)
subtraction and O(L) worst-case increment. There are exactly UM source
offsets per traversal. Initial x allocation/erasure is O(UL). Hence the
remaining bill is

```
O(B + UM L^2),
```

with two callback invocations absorbed into its constant. The callback is
prepared outside G and S loops; their arbitrary extents do not enter it.
For fixed prime q, M=q^w and L=O_q(w). Under PR2449's separately retained
root-coupled callback guarantee `B<=A_q w^1800`, both terms are O_q(V):

```
w^j <= j! exp(w) <= j! 4^w <= j! q^(2w)  (q>=2),
w^2 <= (2^2 * 2!) q^(w-1)              (q>=2).
```

The first uses the exponential series and e<4; take j=1800 and V>=M^2.
The second is the predecessor's factorial absorption inequality; it also
follows from `w^2 <= 2!*2^2*2^(w-1)`. Then `UM L^2=O_q(UM^2)<=O_q(V)`.
This confirms the local CqV implication **conditional on B**. It does not
independently prove the generated descriptor tree, full matrix preparation,
the selected root coupling, recursive child cost, parking of an enclosing
caller, fixed-machine compilation or the global family/owner interpreter.

Canonical spectator widths are necessary for this particular volume-only
statement: N=1 encoded in k bits alone costs `14k+46` operations including
input traffic. It is unbounded at fixed logical volume as k grows. The
source's `positive_extent` correctly rejects that padding. The separate
modulus-width target ranges may be zero, and are already paid by M.

## Evidence and reproduction

The independent verifier imports only the three authenticated runtime modules,
not PR2449's checker, oracle, coefficient generator or receipt. It checks
1,026 complete countdowns (N=0..512, two word widths each), input-word
traffic, and 386 full Boolean basis inputs with inverse restoration across
seven complete layouts. Every payload run checks the exact composed counter
bill, exact payload bill, erased scratch, restored input/control heads and
unmodified inputs. Runtime `Word.inspect` is forbidden during each ADD.

Controls cover the special final decrement, noncanonical padded singleton,
different split/merge coefficients, wrong inverse sign and nonzero setup
for a zero target range. The separate test file mutates source motion,
omits erasure, and checks source/receipt authentication and Git-free export.
These are finite regression controls, not the proof of the all-length formulas.

```
python3.12 -I -B research/binary-add-cost-audit/verify.py
python3.12 -I -O -B research/binary-add-cost-audit/test_verify.py
python3.12 scripts/research_package.py --package research/binary-add-cost-audit
```

The default replay is read-only. `--out NEW.json` exclusively writes a newly
computed receipt; it refuses to overwrite a file. [RESULT.json](RESULT.json)
records deterministic counts and digests. No selected cold replay, new Lean
build, independent human review or formal-kernel proof is claimed.

## Open next questions

Connect the independently billed fixed-prefix stream to the complete selected
residual while keeping header-dependent coefficient pages and inverse order
explicit. Jose Manuel's active Discussion2319 scope owns that implementation;
an independent review can check the resulting trace without duplicating it.
The remaining blocker is its published complete adapter/child composition.

Separately, formalize the source-level counter transition table and owner
invariants in a finite-machine semantics. Start from the three decrement
cases above; this would strengthen a written audit to a checked operational
refinement. No such compiler or formalization is supplied here.

Credit Jose Manuel (`jmbarrancoml`) for PR2449, PR2405 and the underlying
selected callback/stream construction; `source/NOTICE.md` retains its full
source527, supplier, descriptor, stream and relative-origin lineage. This
audit adds an independently derived billing certificate and scope check.
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
