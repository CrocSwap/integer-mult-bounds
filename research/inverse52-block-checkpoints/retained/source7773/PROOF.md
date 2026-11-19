# A clean finite window for the actual denominator-52 sampler

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Contract and result

The actual inverse residue domain in
[PR #6096](https://github.com/CrocSwap/integer-mult-bounds/pull/6096)
contains every pair `0<=a,b<52`, already with 112 owner coordinates in
{-1,0,1}. The new circuit takes the pair in two six-bit read-only words
and L resident coin bits, where L is any positive integer. All coins
remain unchanged. They need not be random for the circuit identity.
The probability statements require fresh independent fair coins,
conditional on the input pair.

Use the original ordered product weights

```text
w = ((52-a)(52-b), (52-a)b, a(52-b), ab),
Q = 2704,                         sum(w)=Q.
```

The output has a completion bit, two label bits and
`bit_length(L+1)` depth bits. If the ordered source decision graph stops
by coin L, the circuit returns its exact label and first stopping depth.
For `(a,b)=(0,0)`, these are completion one, label zero and depth zero.
Otherwise, an unfinished draw returns completion zero, label zero and
depth L+1. The depth is a sentinel in that case, not a consumed coin.

More precisely, the circuit is the XOR oracle

```text
(a,b,coins,out,0_work) -> (a,b,coins,out XOR result,0_work).
```

The output can contain any initial bit pattern. Every history and
temporary bit is restored. All L coins are resident and may be read by
the fixed circuit, even when the source draw would stop earlier. The
reported first stopping depth does not reduce the fixed-window bill.

The exact resource counts are

```text
gates           = 3643 + 1956 L,
clean work bits = 610 + 51 L,
input bits      = 12 + L,
output bits     = 3 + bit_length(L+1).
```

The gate set is X, CNOT and Toffoli. The work count excludes the stated
inputs and output. It includes preparation, the complete retained
history and the reused temporary area. This is a Boolean circuit bill;
physical tape movement and a native caller invoice are not included.

The contract is a censored finite window. It is not an unbounded exact
sample. It resolves prefix computation and return for this stated
contract, including the first-entry collision identified by
[PR #7757](https://github.com/CrocSwap/integer-mult-bounds/pull/7757).
It does not erase that collision by substituting a cyclic predecessor.

## 2. Direct arithmetic through prefix and tail

The source graph assigns available leaf children in order 00,01,10,11.
At depth t, put `r_i=2^t w_i mod Q`. A next digit and residue are

```text
b_i = floor(2 r_i/Q),
r_i' = 2 r_i - Q b_i.
```

Each b_i is zero or one. If the current live-node index is j and the
next coin is u, form child index `2j+u`. The first `sum(b_i)` children
are leaves in label order. Otherwise subtract that count to obtain
the next live-node index. This is the source's ordered dyadic graph.

The live count is `n_t=sum(r_i)/Q`. It is an integer in {0,1,2,3},
since each residue is below Q and the weights sum to Q. The relation
`n_(t+1)=2n_t-sum(b_i)` proves that the leaf assignment never overfills
a level. Two bits suffice for j; three suffice for the child and leaf
count. The completed flag makes labels absorbing. Residues may still
advance after completion, but the retained label and flag do not change.

The circuit computes the weights from the original a,b. It forms ab
by six controlled shifted terms, then 52a and 52b by shifts 2,4,5.
The four weights follow by twelve-bit modular additions and subtractions.
Their final values lie in [0,Q], so these words represent the exact
integers. Only w_0 can equal Q, at `(0,0)`. A separate zero-input test
sets the initial completion flag and replaces that residue by zero.

For residue doubling, the circuit uses the thirteen-bit word `2r-Q`
modulo 8192. Its signed value is between -2704 and 2702. Its top bit
therefore detects a negative result. The selected twelve low bits give
`2r mod Q`, and the complementary sign bit gives the digit. All 2,704
residue inputs are checked in both directions, with all temporary wires.
The wider adders use the source Boolean gates and the standard full-adder
identity; they do not patch the source's bounded-width routines.

This calculation uses one modulus throughout. It neither prepares new
modulus-13 parameters nor converts the first prefix return to a periodic
inverse. After depth four, all residues are multiples of sixteen and
their quotient evolves modulo 169. Since `2^156=1 mod169`, depths four
through 159 give a complete period. The verifier checks that depth 160
returns to the depth-four residue tuple for all 2,704 pairs.

## 3. History, answer and exact cleanup

One state has four twelve-bit residues, a two-bit node or label and a
completion flag: 51 bits. Allocate L+1 such states, all initially zero.
A clean preparation oracle writes state zero. For each coin, a clean
draw oracle writes the next state into its own zero packet. Each oracle
computes into temporary bits, copies its output and reverses the temporary
computation. The same 559-bit temporary area suffices for every oracle.

The schedule is fixed by the circuit position. The old states remain
available until the answer is copied. The complete oracle list then runs
backwards. This clears every state and temporary wire. No inverse of a
merged prefix/tail state is required. Since the answer bits are not used
by that reversal, the result is the stated XOR oracle for arbitrary
initial output bits.

Let s_t be the completion flag in state t. These flags are monotone.
The final completion bit is s_L; label bits are the final label masked
by s_L. The depth word has the following exact bitwise formula:

```text
depth = (L+1) XOR XOR_(t=0)^L [(t XOR (t+1)) s_t].
```

If completion first occurs at d, the XOR from d through L telescopes
to `d XOR (L+1)`, so the displayed word is d. This includes d=0.
If the draw is unfinished, every s_t is zero and the result is L+1.
This formula avoids an arithmetic counter and retains the exact depth.

Write p=popcount(L+1). The increment masks contain
`2(L+1)-p` set bits in total. Indeed the mask for incrementing t has
`1+v_2(t+1)` set bits, and the sum of those valuations is `L+1-p`.
Writing the constant word takes p X gates, so depth extraction takes
exactly 2(L+1) gates. Completion and two label bits add one CNOT and
two Toffoli gates. No temporary bit is needed for answer extraction.

| Circuit component | X | CNOT | Toffoli | Total |
| --- | --- | --- | --- | --- |
| One clean preparation oracle | 130 | 1223 | 466 | 1819 |
| One clean draw oracle | 90 | 717 | 170 | 977 |
| Answer extraction | p | 2L+3-p | 2 | 2L+5 |

Preparation and all L draw oracles occur once forwards and once in
reverse. Thus the full gate-type counts are

```text
X       = 260 + 180 L + p,
CNOT    = 2449 + 1436 L - p,
Toffoli = 934 + 340 L.
```

The history costs `51(L+1)` bits, and the shared temporary area costs
559 bits. These give the stated exact total counts. The generator
recomputes them from the actual gate list; they are not estimated costs.
For L=4 the bill is 11,467 gates and 814 clean work bits. For L=64 it
is 128,827 gates and 3,874 clean work bits.

## 4. Exact censoring law

The number of length-L coin strings that have completed with label i
is exactly `floor(2^L w_i/Q)`. This follows by the source's level
recurrence, including all extensions of earlier stopping prefixes.
The circuit preserves that ordered coin function. Hence

```text
Pr(completed with label i) = floor(2^L w_i/Q)/2^L,
Pr(censored) = n_L/2^L <= 3/2^L.
```

These are unconditional masses. Conditioning on completion generally
changes the desired product law. Discarding censored results, replacing
them by a label or restarting a fresh truncated draw is not justified
by this theorem. A caller must retain and handle the censored outcome.
Extending the same retained coin sequence and recomputing a longer
window is mathematically compatible with the source function, but its
storage, access and continuation costs need a separate caller bill.

## Evidence and limits

All 21 retained source files have exact Git-blob and SHA-256 pins. The
actual mode columns give all 2,704 bounded owner witnesses. The source
fixed-pair Boolean verifier runs unchanged. New exact checks cover:

- Every runtime weight preparation and all 2,704 residue doublings,
  forwards and backwards with clean temporary bits.
- All 1,678,810 source edge visits through the four-step prefix and one
  complete period. They reduce to 107,158 distinct live edges. Together
  with every absorbed label at 28,969 residue phases, all 338,910 distinct
  transitions pass complete Boolean forward/inverse checks.
- Every coin string for every source pair at L=1,4,8: 5,408, 43,264 and
  692,224 cases. All finite output masses agree with the floor formula.
  The unchanged source prefix also agrees in all 43,264 L=4 cases.
- All stopping prefixes, with all-zero and all-one remaining suffixes,
  and all live prefixes at L=16: 153,434 distinct cases. This is not an
  exhaustive enumeration of all 2^16 strings for every pair.
- Arbitrary initial output words at L=4, separate scalar gate checks,
  ordered-label and omitted-history-cleanup circuit mutants, and changed
  input, coin, depth and work-wire controls. Exact bills also pass at
  thirteen lengths through 127.

The all-L claim is a written composition proof supported by these finite
checks. No full unbounded sampler, physical tape layout or actual caller
installation is supplied. Owner-to-residue extraction, fresh-coin delivery,
output retention and censored continuation remain unpriced. The full
source kernel fixtures, runtime/tail circuit suites, historical probability
catalogue, selected cold replay, Lean and Docker were not run. No independent
human or formal-kernel acceptance is claimed. No kappa, selected frontier
or any of the five framework assumptions changes.
