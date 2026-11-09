# Literal total rounded scalars on the retained lifecycle ABI

Prepared for **@CubeJerry**, with substantial OpenAI assistance. Canonical
base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. This is a physical scalar
service lemma and current finite-source binding. **No new kappa, no full
caller admission, and no unconditional multiplication theorem.**

## 1. Exact scope and predecessor boundary

The unchanged predecessor scalar compiler is published at
[`13193a22b1070a74a8580c5d3ea27470443f815a`](https://github.com/CubeJerry/integer-mult-bounds/tree/13193a22b1070a74a8580c5d3ea27470443f815a/research/current-scalar-flat-tables).
The unchanged lifecycle `Controller.primitive`, `execute_table`, CodedPort
and retirement code are published at
[`ab239cb6ee884e7a900dd9101c34448077fad0b0`](https://github.com/CubeJerry/integer-mult-bounds/tree/ab239cb6ee884e7a900dd9101c34448077fad0b0/research/compiled-owned-bank-lifecycle).
The old scalar divider is checked **exact** division. Its finite-state
builder is reused unmodified; its quotient transition is replaced, not
relabelled as rounding.

The concrete word is DreamingOfClouds'
[CrocSwap/integer-mult-bounds#6936](https://github.com/CrocSwap/integer-mult-bounds/pull/6936),
head `03626137d0bd57f09b0bf9597376183ce6fa9683`, 71,144 events.
Its 3,660 SCALE occurrences use 52 fixed rational coefficients. All 52
tables are constructed and registered under the exact local token
`(local, pc, original_event)`, retaining source position, coefficient,
register and frame. The caller must supply that instruction's ordered
numeric field and the premises below; an entire caller/recursive source
exporter is not installed here.

DreamingOfClouds' `ROUNDED-DIVISION.md` in
[CrocSwap/integer-mult-bounds#6937](https://github.com/CrocSwap/integer-mult-bounds/pull/6937),
head `a98df73ddae1d1ea85a62b6bdf2714b28cb7b359`, defines nearest-up RDiv,
gives an abstract LSF multiply/MSF odd division construction, and reports
285,870 small automaton cases. It explicitly leaves tape-level recounting
and physical services open. Its sole shipped `check.py`, blob
`cebc2062a3939e5b2e415fe5aa6d3d8ce1d6cdac`, does not contain that
automaton or lifecycle join. Here a signed residue prepass is followed by
an LSF exact odd quotient and low-bit discard, using the existing two work
banks and no new reversal buffer.

The preceding precision package at
[`56bc9383594a3efc303148e00bb746851abd1ed5`](https://github.com/CubeJerry/integer-mult-bounds/tree/56bc9383594a3efc303148e00bb746851abd1ed5/research/query-only-precision-envelope)
locates a permitted one-grid defect before SCALE37480 by -2/3 that the
exact service rejects. This package closes that arithmetic seam and
constructs the whole current SCALE class. The remaining 4,079 odd ADD
occurrences are not instantiated here.

Six unchanged files have exact commit/path/blob/SHA-256 pins in
`DEPENDENCIES.json`. Runtime tables contain only branch, write, unit move,
goto, halt and reject. Python arithmetic occurs only in fixed table
construction; there is no runtime payload callback or host division.
These are the proposed RDiv numerical semantics, not the source's
exact-child mode or an unannounced change to the selected rule.

## 2. All-size theorem and domain

Fix `a/b` in lowest terms, a integer and b>0, before runtime sizes vary.
Write `b=2^d o`, o odd, and `c=floor(b/2)`.
Define `Round(m)=floor((a*m+c)/b)`. SCALE sends m to Round(m); ADD sends
target x and source y to `x+Round(y)` and preserves the source. ADD shares
the proof; only small ADD coefficients are physically instantiated here.

The tape premises are:

* A field has a finite, nonempty even number R of signed components, each
  with positive width w_i, LSF two's-complement bits and delimiter2. The
  current format specializes to common W. ADD has matching shapes and a
  common grid on distinct tapes. Equal values are permitted; physical
  target/source alias is outside this contract.
* Numeric symbols0,1,2 use canonical three-nonblank-bit physical codes,
  followed by a **physical** BLANK frontier. Encoded virtual4 cannot
  masquerade as a frontier. CodedPort identifies those two cases, so this
  table is not a validator of arbitrary noncanonical encodings.
* Public and borrowed context heads start at their protected local origins.
  Each work head is inside its old contiguous binary body or at its
  frontier. All field/work tapes are distinct and mutation is sequential.
* Work may initially be dirty and longer than the new field. Historically
  allocated cells beyond its contiguous body must already be blank.
  Hidden dirt after a blank is outside the retirement invariant. Protected
  parent/ancestor segments stay live and are not scratch.
* The unchanged lifecycle retires both work banks on entry, executes the
  table, resets successful heads and retires both banks on success.

**Theorem.** Every such input terminates and succeeds iff every rounded
output fits its original signed width. Success installs the exact rounded
result, preserves source/context data, restores all heads and blanks both
work bodies, including previously written tails. A detected pre-installation
grammar error or overflow leaves the entire public target unchanged,
including earlier staged components. On rejection, work and heads may be
dirty/unrestored; no automatic rollback or successful continuation is claimed.

This is total rounding subject to representable output, not an assertion
that every coefficient/input pair fits a fixed output width.

## 3. Signed residue prepass

For a w-bit component with bits x_j and sign s, write
`U=sum x_j 2^j`, `m=U-s 2^w`. The prepass keeps finite states

    rho = c + a sum_(j<k) x_j 2^j  (mod o),
    power = 2^k (mod o).

At the delimiter it computes

    r=(rho-a*s*power) mod o=(a*m+c) mod o,   0<=r<o.

The terminal sign correction is essential; a compiled mutant omitting it
fails a representable negative-input case. For ADD, its numerator is
`b*x+a*y+c`. Since b*x vanishes modulo o, the prepass uses source y for
the residue and its terminal sign correction, while checking both public
streams in lockstep. No independence of their values is assumed.

When o=1 the prepass is absent: r=0. Otherwise it scans the current
component and writes guide marker6 for its first bit and guide1 for the
remaining bits. Walking the guide backwards moves each public head back
once per bit until marker6, exactly to the component start, without crossing
its protected origin. No width is stored in host memory. The arithmetic
pass overwrites marker6 with ordinary guide1, leaving the original global
marker5 and one mark per consumed input bit/delimiter. No additional bank
or persistent residue word is allocated. Residue and power range below o
and are part of the fixed finite controller.

## 4. Odd quotient and arithmetic low-bit discard

For SCALE put `(p,t)=(a,0)`; for ADD put `(p,t)=(b,a)`. Start carry at
`c_0=c-r`. For LSF input bits x_j,y_j use

    v_j=p*x_j+t*y_j+c_j,
    z_j=v_j mod 2 in {0,1},
    c_(j+1)=(v_j-o*z_j)/2.

Oddness of o makes this integral. The service first divides by o and
discards the first d quotient bits; it never requires discarded bits to
be zero. After w actual bits it processes d further copies of the input
sign bits without moving the public heads. It therefore processes L=w+d
positions and emits exactly w bits, including when w<d.

Let `C=abs(p)+abs(t)+o+c`. Initially `abs(c-r)<=c+o-1<=C`, and induction
gives `abs(c_(j+1)) <= (abs(p)+abs(t)+C+o)/2 <= C`. All these arithmetic
transitions are compiled into a finite graph. No temporary negation of a
most-negative input is formed in its original signed width.

If Z_L is the unsigned quotient word, telescoping yields

    p*X_L+t*Y_L+c-r = o*Z_L + 2^L c_L.               (1)

Sign extension gives `X_L=x+s_x 2^L`, `Y_L=y+s_y 2^L`. With final quotient
bit s_z, its signed value is `Q=Z_L-s_z 2^L`. The final guard is

    c_L=p*s_x+t*s_y-o*s_z.                           (2)

Together these assert exactly `o Q=p*x+t*y+c-r`. The numerator is divisible
by o. Since o is odd, each successive quotient bit is uniquely determined
modulo the next power of two. The emitted L-bit word is consequently the
exact integer quotient modulo 2^L. Guard (2) succeeds iff that exact
quotient fits signed L bits. This proves necessity and sufficiency for
negative, zero and most-negative inputs, rather than only eventual carry
stability. A wrong-sign guard mutant is physically rejected by the oracle.

Low-bit discard implements mathematical floor. Write uniquely
`Q=2^d R+ell`, `0<=ell<2^d`, also for negative Q. Q fits signed L=w+d bits
iff R fits signed w bits, and the retained word represents R. For
`N=p*x+t*y+c=o Q+r`,

    N/(o*2^d)=R+(ell+r/o)/2^d,
    0 <= (ell+r/o)/2^d < 1.

Thus the output is `floor(N/b)`, equal to Round(x) for SCALE and
`x+Round(y)` for ADD. There is no divisibility rejection. This is not
truncation toward zero. Even ties go upward: Round_(1/2)(1)=1 whereas
Round_(1/2)(-1)=0.

If `a*m+c=b R+u`, `0<=u<b`, the residual is `(c-u)/b`, whose absolute
value is at most 1/2. Hence a grid-Delta component has error at most Delta/2;
a complete X-fibre of complex entries has error at most
`2^((X-1)/2)*Delta`, matching the preceding precision contract.

## 5. Actual -2/3 seam: every signed input fits for W>=2

For q=-2/3, `Round(m)=floor((-2m+1)/3)`. Put A=2^(W-1). At input -A,
the largest output is `floor((2A+1)/3)`. If W>=2 then A>=2 and
`2A+1<3A`, so this is at most A-1. At the largest input A-1, the result is
`floor((-2A+3)/3)>=-A`. Monotonicity covers every intermediate input.
Thus the table succeeds on every signed W-bit input for every W>=2 and
every finite complete field in the theorem's domain.

At source SCALE37480 on register697, numerator1 maps to -1, with residual
-1/3 quantum; the old exact table rejected it. W=1 is correctly exceptional:
input -1 would round to +1, outside [-1,0]. Grid precision does not change
this integer statement.

## 6. Whole-field staging, preservation and history

No public write occurs during residue measurement, quotient generation,
shape checking or per-component range checks. Candidate components go to
the output bank. A parity state requires a positive even component count
at the frontier; ADD checks input bits, delimiters and frontiers in lockstep.
Only after every component passes does the global unary guide rewind the
inputs and protected output. Installation then copies the validated whole
field to the target.

Under the geometry premises this installation cannot encounter a new
arithmetic/shape failure: the work streams were generated by the table and
have the consumed target's length. The ADD source is never written. No
table row addresses extra borrowed contexts; the executor only resets their
already-origin heads. Every ancestor remains behind its protected marker.

Fixtures execute the unchanged `Controller.primitive` method, supplying
the exact attributes it reads. They do not claim a full recursive
Controller constructor, row provider or stack execution. Tables are immutable
tuples, and integer oracles inspect outputs only outside runtime.
Three separate cost fixtures wrap only table lookup in a transparent
counter that returns the unchanged immutable row. It receives no tape or
numerical payload and cannot influence the instruction stream; it counts
control steps alongside the physical Tape observer.

The executor resets success heads; unchanged retirement erases both
contiguous work bodies. Guide marker6 is encoded as three nonblank physical
bits and cannot hide a suffix from retirement. Older longer tails were
erased at entry and remain blank. Shorter reuse therefore preserves all
historical cells. A rejected run can leave contiguous dirt and an interior
head; a subsequent explicitly started primitive retires it. Rejected public
heads are not automatically restored.

## 7. Complete positive primitive cost and storage

Let R be the component count and `S=sum_i(w_i+1)` the numeric virtual
extent of a public field, delimiters included. Let A_0,A_1 be the old
contiguous physical work-body lengths, with heads inside those bodies or
at their frontiers. Let Q_c count untouched borrowed binary contexts at
their origins. Count each physical read, write, unit head move and each
executed flat-table row as one finite-control action. A conservative
complete successful primitive bound is

    512(S+1) + 64 d R + 7(A_0+A_1) + 16 Q_c.          (3)

Detected pre-installation failures use only a prefix of these phases, for
their scanned extents. This is a bound in stated physical/finite-control
units, not a conversion into the supplier's raw tariff.

A valid CodedPort nonblank read costs at most 10 physical actions, a write9
and a unit move4. Every forward move is from a written/data symbol: the
table does not allocate an extra virtual word by moving from a blank
frontier. Including the control row, each instruction costs at most 11.

| Table phase | Upper bound on executed rows |
|---|---:|
| Arithmetic and delimiter checks | 10 S + 3 d R |
| Odd residue scan and component rewind | 13 S |
| Global guide rewind | 7 S |
| Validated installation | 7 S |
| Fixed entry/frontier/marker branches | 32 |

The residue phase is absent when o=1. The table therefore costs at most
`407S+33dR+352` including its physical actions. Executor head resets cost
at most `18S+18`. Entry retirement of work bank i costs
`5A_i+2h_i+7<=7A_i+7`, where h_i is its initial displacement. Final
retirement of physical lengths 3S and3(S+1) costs `30S+29`. Their sum is
at most `455S+33dR+413+7(A_0+A_1)`. The remaining allowance in (3) covers
the fixed two-bank/at-most-two-public-port wrapper bookkeeping (at most 64
control steps under this convention) and context resets. The latter cost 3
physical actions each plus linear bookkeeping; 16 Q_c is positive slack.
Since R>=2 and w_i>=1, S>=4, so this slack is sufficient. Every source
read, copy, rewind, head return and retirement remains in the bill.

Runtime output uses at most3S physical cells and guide 3(S+1). No multiply
or reversal array is allocated. The carry is bounded by C and residue/power
by o; those are fixed finite controller states. The generic W+26 numerator
budget from the precision package is compatible but is not a hidden third
array here. If a coefficient or d is itself a runtime variable, this fixed
template theorem does not provide a uniform variable-divisor service.

If prior backing capacities are H_0,H_1, resident private storage remains

    max(H_0,3S) + max(H_1,3(S+1)),

in addition to public fields, all borrowed metadata, protected ancestors
and fixed controller storage. For repeated calls i, sum (3) with actual
S_i,R_i and initial dirty lengths A_(j,i). After success these dirty lengths
are zero on the next use; resident capacities still retain historical
maxima. This charges initial dirt/failure leftovers and does not pretend
that an erased longer tail ceases to occupy backing.

**Construction.** There are at most 2C+1 carry values, finite residue/power
states and phase counters bounded by d. A coarse finite graph bound is a
fixed constant times `(d+1)^2(C+1)+(o+1)^2`, with positive coefficient-bit
arithmetic and label-resolution cost. Authentication, source reading, token
registration, graph construction and storage contribute C_setup independent
of runtime field sizes. They are not priced as zero.

The instantiated 52-SCALE catalogue has 92,113 rows, at most 20,401 in one
table, with d<=8, o<=15 and C<=278. Only 64 occurrences per local word use
the residue prepass, hence 1,152 in an 18-call raw caller. `SOURCE.json`
records every coefficient and occurrence count. No additional bank is
introduced.

The previous precision package's optimistic extra-scan margin is not an
admitted exchange rate between (3) and the inherited 10^9 raw tariff.
The complete current ADD class, source/row exporter, other providers,
recursive children, setup and normalization interfaces still need a common
physical invoice. This package makes no tariff-cap or kappa conclusion.

## 8. Verification and remaining obligations

The physical oracle computes mathematical integer floor and final signed
range directly, without replaying table transitions. Bounded coverage is:

* all 52 current SCALE coefficients, all signed inputs at widths 1..5:
  3,224 cases, 1,998 accepts and1,226 correct overflow rejections;
* seven small ADD coefficients, all input pairs at widths 1..4:
  2,380 cases, 1,706 accepts and 674 correct overflow rejections;
* every -2/3 input at widths 2..9:1,020 successes;
* work initially dirty for 1,800 and 2,400 cells, arbitrary interior/frontier
  heads, long-to-short reuse, late-component overflow, explicit retirement
  after failure including a live residue marker6, three borrowed contexts,
  detected malformed grammars and combined table/physical cost samples;
* separately compiled mutants omitting signed residue correction, omitting
  the upward rounding offset, and changing the final signed guard.

Physical attempts have a 120-second cap. The proof, rather than finite
width coverage, establishes universality. Tests do not monkey-patch the
executor/CodedPort or use numerical payload callbacks. The primitive
fixture is not a recursive tape computation or independent human review.

Open next questions: construct and price uninstantiated current ADD
tables; bind recursive occurrence/row formats; establish the remaining
native/Lambda/error/ownership contracts; and assemble the full physical
tariff and rounded outer recovery. The source precision implication at
56bc938 remains conditional on those interfaces. No selected certificate
or predecessor source is changed here.
