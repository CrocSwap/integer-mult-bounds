# Complete paid high-cube composition

This source-level composition for unchanged PR2915 closes the remaining
unit-translation and whole-swap-adapter terms in the PR2982/3265 handoff.
The predecessor inequalities below are pinned dependencies, not new results
or scientific admissions inferred from archival intake.

## Contract and currency

Let d>=1, N=d², Q=q^u with odd q>=3 and u>=0, F>=1 canonical, and
V=Q^N F. Use the actual compiled sequence with valid, distinct binary
indices. The active sequence has s factors for Q>1 and is empty for Q=1.
Let a,h,g,c count ADD, doubling/halving, negation and translation factors;
r counts ADDs whose control field exceeds their target, and t counts swap
factors plus 2r. Every binary call sees [B][Q][M][Q][S] of volume V.

All borrowed heads, complete payload extents and Count encodings are
canonical. Retain the actual outer numerical width I and high-bank role
count K. The high bank enters erased and empty. Numerical and scratch
capacity suffice. Other occupied scratch roles may contain arbitrary data;
their ownership, bytes and heads must survive. This does not allow dirty
residents in the high numerical bank. Only successful execution is claimed.

Every native B1 call preserves its complete borrowed source and spectators,
restores their heads, and returns a distinct dense V-bit owned output at
its origin. Its owned work is restored before reuse. These are inherited
all-width premises, not consequences of elementary-branch fixtures.

Count one physical Tape read, write or unit move once. Word/Lease aliases
do not add a second charge. Include all work reached between cube entry
and successful return, including probes, numerical scans, copy-out and
internal disposal. Initial context/pool provisioning, Python/finite-control
selection, compilation and final returned-output disposal remain separate.
Write A_j for each entire actual `native.run` interval, including its own
setup and cleanup. A_j is never set to zero.

## Credited same-source ingredients

* Arham Tahir's PR2877 gives plain canonical sign T<2048BQS and the
  countdown identity below. The verifier checks byte equality of its
  retained linear_sign.py with the implementation actually loaded through
  PR2915's archive chain.
* Nick Petalas's PR2951/2968 gives pooled doubling/halving T<530V.
* commdata2338's PR3233 gives complete pooled ordered ADD T<4096V,
  including arithmetic, marginal counts and acquisition probes.
* Sagar Thakrar's PR3265 gives exact setup/disposal and the bound
  `27I+10K+[373+s(3B_N+36)]V`, with `B_N=716+933J`,
  `J=2 bit_length(N)`. This excludes whole kernels and whole swap adapters.
  It already charges the three intermediate clearances of a reversed ADD.
* Nick Petalas's PR2982 bounds the complete-prefix wrapper by 265 times
  packet volume, or 277 including final output disposal.

The reached high Ring has b=bit_length(Q)+1. The two pending proof pins are
PR3233 `803f3593e8f00ed8591d5ff6fc69ce2a036a3293` and PR3265
`ac651ec18e62edf0baf3846cc4bf0a11d335c2b4`. SOURCES.json records their source
paths, Git blob IDs and SHA-256 hashes under `external_proofs`. Exact copies
in `sources/` avoid requiring unmerged Git objects in a clean checkout;
the verifier authenticates their bytes by SHA-256. The source-commit
attribution was checked during preparation, not inferred from that hash.
The PR3265 equations reproduced in bounds.py
calibrate the composition; that previously solved component is not claimed
as new.

## Counter and numerical bounds

A fully drained positive Counter of value x in e digits costs, before pooling,

    D(x,e)=15x+14e-5popcount(x)+36.

Zero costs 14e+40. Each pooled Counter adds one acquisition read. For the
separately marginal encoding e=bit_length(x)+1, `D(x,e)+1<=80x`.
Normalization occurs at construction: the encoded width is not charged
again on every decrement.

For b>=3, the literal Word/PhysicalArena loops bound zero, copy, a fitting
literal, compare, add/subtract, shift-add, zero test and free by 100(b+1)
each. For example zero is 9b+12, copy <=27b+1, add/subtract <=35b+2.
Unsigned.divmod has b iterations of at most a shift-add, comparison,
subtraction and two frees plus linear setup/teardown: <=1000(b+1)².
These deliberately loose bounds include initialization/erasure scans and
also follow from PR3233's tighter table; they are not fitted timing ratios.

Making and closing one marginal copy of a canonical positive x costs
<=100(bit_length(x)+1), by its copy/normalize/msb/append/clear scans,
including the probe. The source calls `x.marginal()` directly, not two
successive copies. Using the looser allowance 200 gives, for a pair B,S,

    marginal pair <=200(bit_length(B)+bit_length(S)+2)
                  <=800BS <=(800/3)BQS.          (1)

## Pooled sign and the missing translation tariff

The exact successful sign acquisition count is

    2+B(4Q-5)+[S>1]BQ <=5BQ <=5V.

There is one output and one outer Counter. Each row makes two move_slices
block counters and one remaining Counter, 4(Q-2) suffix movement Counters,
and Q copy_bits Counters exactly when S>1. Installing the pool changes no
tape loop; each acquisition adds one read. PhysicalWord forwards each
credited logical operation to one physical operation. The pooled sign is
therefore <2053V; with (1), kernels.negated is <4096V.

For translate_one, put P=D(Q-1,b)+D(1,b)+2 and
E=[S>1](D(S,bit_length(S)+1)+1). Its complete physical toll is at most

    200(b+1)+3 +2(D(B,bit_length(B)+1)+1)
      +2B(P+30+5QS+QE) +13V+29.                (2)

The first term prices subtract_exact(Q,1) and free; three probes acquire
left/right/output. Two outer countdowns cover split and merge. Each row
per traversal calls copy_blocks twice: P prices their countdowns, 30 their
suffix probes, 5QS the opaque copies, and QE the nontrivial suffix counters.
The last term includes source/bucket rewinds, consumption probes, the two
bucket clearances starting at their consumed ends, and the output rewind.

Since b<=Q, P<=80Q, 30<=10Q, E<=80S, and b+1<=4Q/3, (2) is at most

    (350+160/3+800/3+13+32/3)V <1024V.

Both S=1 and S>1 are covered. The replay checks (2) at each actually
reached translation, separately from the enclosing kernel.

A positive carry k<=4 makes k unit translations. A negative carry makes
2k pooled signs and k unit translations. At most 3k-1<=11 intermediate
outputs are cleared inside the kernel, each at 5V+7<=12V. One marginal
pair serves the whole kernel. Hence kernels.translated costs less than

    [8*2053+4*1024+11*12+800/3]V <32768V.

This includes all intermediate work for the compiler's nonzero carries
between -4 and +4.

## Whole swap adapter with a paid native interval

Adapter.swap creates width zero and three canonical extent copies, derives
u by radix_power, calls B1, copies its returned output to a fresh outer
lease, clears the native output, and closes all four counts. B1 costs A_j.

There are u<=bit_length(Q)<b divisions. The numerical bounds above price
the radix scan at <=2000(b+1)³. Width construction, increments and disposal
cost <=200(b+1)². For Q>=3,

    (bit_length(Q)+2)³ <=8Q².                  (3)

Check Q=3 directly. For bit length k>=3 use Q>=2^(k-1), base
5³<=8*4², and induction: increasing k multiplies (k+2)³ by less than four
and 2^(2k) by four. Thus radix plus width costs <=17600Q²<=17600V.

For P=BMS, the three extent lengths plus three unit allowances total <=6P.
At 100 per digit for each copy and close, their cost is <=1200P<400V,
because V=PQ² and Q²>=9. Acquisition, output copying/rewinding and native
output disposal scan exactly V symbols. Even 2000(V+1)<=2223V covers these
paths. Suspend/re-enable installation performs no physical tape work;
the ready marker belongs to the stated outer entry contract.

Therefore the whole adapter, conservatively, costs

    A_j+100000V.                              (4)

Its exact complete-output and ownership premises are necessary. An opaque
routine returning a larger tape does not satisfy (4) merely by sharing B1's
exponent. The native all-width tariff is not proved here.

## Complete cube and linear prefix lift

The direct kernels are disjoint intervals. A reversed ADD contains two
whole adapters and one ordered ADD; PR3265 already charges its three
clearances. Combining the preceding bounds gives

    T_cube <= sum_j A_j +27I+10K
      +[373+s(3B_N+36)+4096a+530h+4096g+32768c+100000t]V. (5)

For Q=1, all factor/native counts vanish; the credited copy/setup bound
still applies. Final returned-cube disposal adds 5V+7<=12V, outside (5).
For C old prefixes, sum (5) once over actual cubes and add PR2982's 265CV
wrapper (277CV with output disposal). There is no second factor C on a
complete-packet charge. Distinct per-cube I,K or words can instead be
retained and summed explicitly.

If actual fitted B1 calls additionally satisfy their inherited same-domain
tariff A_j<=C_B V u^p, then (5)'s native term is t C_B V u^p. For fixed
q,d,K and compiled word, the source relation
I=bit_length(q^(u+1))+1<=bit_length(Q)+bit_length(q)+1 absorbs I into the
linear term. This establishes the conditional local
O_q,d,K,word(V(1+u^p)) bound and its linear prefix lift. It does not prove
the native premise, enclosing recursion, stock, supplier admission or kappa.

## Evidence and limits

The source argument supplies the all-parameter implication. The replay
checks 14 complete reduced packets (9,654 Boolean coordinates), all six
kinds, nonidentity low rows with carries -4 and +3, both ADD orientations,
Q=1/3/5/9, fibres 1/3, repeated prefixes, occupied dirty scratch roles and
48 actual elementary B1 calls. Exact paid partitions agree with raw meters
and the separate observer. Six additional radix scans reach 268-bit words
without exponential payloads; these are not field/admission tests.

Controls reject a wrong coefficient, missing native charges, a one-swap
reversed-ADD invoice, corrupted source hashes and changed receipt types.
A real extra adapter read preserves the endpoint and legitimately passes
the loose bound, but changes the exact receipt and is detected there.
All gates also run with assertions disabled.

No fitted or GL64 payload, full selected cold replay, formal theorem,
interrupted-call recovery, total physical backing, finite-control cost,
root stock or inherited C0/native admission is established. The selected
record is unchanged.

Krzysztof Wójt with substantial OpenAI Codex assistance. Luna supplied
read-only inventories and separate bounded source counts, checked and
integrated by the primary agent. This is author-checked automated evidence,
not independent human/formal review. Credit Jose Manuel/jmbarrancoml,
David Arias, Nick Petalas, commdata2338, Sagar Thakrar, Arham Tahir, ywz65,
Ross Richardson and the retained PR2157/PR589/source lineage. Apache-2.0.
