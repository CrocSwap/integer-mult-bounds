# A literal canonical padded-rotation switch predicate

## 1. Claim, source and credited arithmetic

Canonical base: e54523517d0f03e58352e647c403a5af3e525a57. Nick Petalas's
[#7504](https://github.com/CrocSwap/integer-mult-bounds/pull/7504), exact head
4eece58f5cebdb70a92d65447974f1c02383f60b, proves the arithmetic formulas and
child closure for Cinna Davis's #4100 canonical Beneš compiler. Its proof
and evaluator are retained byte-for-byte. The canonical compiler SHA256 is
681e2e3d71fa74c8b9b326f3860104fd9d89590a222e26ae6ee718d1fd40ff2e.
Those formulas and their canonical orientation are credited prior results.

For h>=1, N=2^h, 1<=s<=N, 0<=a<s, 0<=j<2h-1, 0<=x<N, the requested bit
is canonical row j at the **current wire address x** for rotation by a
modulo s on [0,s), fixing [s,N). It is not indexed by an original token's
entrance address. Row j flips axis min(j,2h-2-j) when its bit is one.

**Theorem.** On the supplied physical ABI below, one fixed2096-location,
14-tape graph returns exactly this Boolean in its original owned output.
It preserves all five borrowed descriptors, returns all14 heads, restores
eight private bodies and erases their newly installed guards, preserving
six permanent input/output guards and every opaque exterior. Its complete
successful bill is

```
T <=1024(h+3)^2,
K_after <=K_entry+16(h+4).
```

K counts historical visited backing on all owners; erasure never releases
history. Working storage is O(h) cells of one fixed finite alphabet. The
bill includes all validation, width production, arithmetic, guards, first
writes, output, erasure, branches and returns. Descriptor production and
transport before entry, and output consumption/retirement, remain paid
caller work.

Graph SHA256 under `digest`'s compact sorted JSON convention:
320daab199a5528d1e7c273c719b6787c01629ff6160cb01fb9c959e87c7b1d8.
No graph parameter depends on h,s,a,j,x. The optional mutation selector
constructs explicitly separate negative-control graphs only.

This supplies #7504's missing literal point-predicate/owned-return service
under an explicit ABI. It does not install a current CRT/key caller, prove
a repeated-workload speedup, discharge a foundational assumption, or improve
kappa. Prepared for @CubeJerry with substantial OpenAI assistance.

## 2. Physical ABI and exact failure boundary

The alphabet is0,1,blank B,LEFT L,private END E, represented by0,1,2,3,4.
This is a fixed symbol naming, not a runtime payload conversion. Every head
starts at its role's supplied first body cell; origins may differ.

| Ports | Role |
| --- | --- |
|0|Borrowed positive canonical LSB-first binary h, followed by blank.|
|1..4|Borrowed s,a,j,x, each exactly W=h+1 LSB-first bits, followed by blank. High zero padding is intentional.|
|5|Separate owned output: its body and next cell enter blank.|
|6|Private fixed-length binary height countdown.|
|7|Private W-one unary width guide, followed by END.|
|8..13|Private W-bit s,a,j,x,last-row and temporary records, each followed by END.|

Ports0..5 have permanent LEFT immediately before their bodies. Ports6..13
instead enter blank there; the graph installs and later erases their LEFT.
Private cells through relative h+2 are supplied blank on legal input. Those
complete windows, genuine disjoint owners and their prior backing are
premises. No count of free row labels creates erased physical storage.
Opaque exteriors are outside these windows and remain unchanged. Input
records contain no interior LEFT markers: guard corruption is outside this
framing ABI. No later tail after the first blank is consumed.

The graph never writes ports0..4. Port5 is written exactly once after the
answer is known. It remains one owned result, not productive credit. One
blank write can retire that bit at its returned head; the caller also pays
its dispatch. No input independence is assumed.

Finite binary descriptor/domain failures reject with the output unchanged,
borrowed heads returned and private bodies/guards cleared. Unexpected END
inside a borrowed body is also rejected/cleaned. This does not promise
recovery from aliasing, missing/interior LEFT, arbitrary bank corruption or
an unterminated stream. A malformed height can have more consumed bits than
a legal h; its rejection is linear in those consumed bits and requires
corresponding supplied parser capacity. For positive canonical h and bad
s/a/j/x, at most W bits of each body are consumed before rejection, so the
same O(h^2) envelope applies.

## 3. Runtime preparation and arithmetic

The finite constructor loops only over fixed role lists, three comparison
states, four bit pairs or eight parity cases. Every emitted operation is
R/W/M/J/H: scanned-symbol test, one fixed-symbol write, unit move, fixed
jump or halt. The runtime cannot consult Python integers, arrays, strides,
lengths or callback results. Interpreter heads and PC are configuration,
not numeric operands of the graph.

The graph installs its guards and checks two blank output cells. It copies
h to COUNT and rejects empty input or a final binary digit zero. COUNT keeps
its original length throughout. Starting with one WIDTH cell, it repeatedly
tests and decrements COUNT and appends one WIDTH cell. Exactly h repetitions
produce W=h+1 cells. This expands h, not N=2^h. Using WIDTH, it initializes
six numeric records and copies exactly W digits of each s,a,j,x, rejecting
short/long fields and invalid digits; all participant heads return.

Copying the unchanged height to the zero last-row record, doubling and
decrementing twice produces R=2h-2. Setting the high bit of the W-bit
temporary produces2^h without enumerating N cells. Literal comparisons
validate s>0, s<=2^h, a<s, x<2^h and j<=R before every shortcut.

Increment/decrement propagate a one-bit carry/borrow from the low end,
rejecting overflow/underflow. Right shift reads the following bit before
writing its predecessor and zeros the high cell. Left shift carries one
bit in finite control. Comparison scans low-to-high, replacing its LT/EQ/GT
state at every unequal pair; the highest unequal pair decides. All words
retain W positions and END, and every macro returns its heads through LEFT.
No arbitrary division or random-access primitive is present.

## 4. Canonical correctness for every height

At each loop entrance, define eta=R/2+1 in the proof only. The invariant is

```
R=2eta-2, 1<=eta<=h,
1<=S<=2^eta, 0<=A<S, 0<=J<=2eta-2, 0<=X<2^eta,
```

and the desired answer equals the canonical predicate at (eta,S,A,J,X).
Initial validation establishes this, on the unchanged W-bit working words.
A=0 returns0. R=0 means eta1, so a nonzero A is1 and the one-row answer is1.
For J=0 the graph returns

```
[S odd and A odd] [floor(X/2)=floor(S/2)].
```

It compares the tails after skipping the low cells. For J=R it returns

```
[A odd][X<S]        if S even;
[X<A]              if S odd, A even;
[A-1<=X<=S]        if S and A odd.
```

The last case copies/decrements A on TEMP, preserving A. These are exactly
the predecessor's first/last-row formulas, including padded wire X=S.
Otherwise0<J<R. Three low-bit reads select one of eight fixed control
branches with c=X mod2,d=S mod2,e=A mod2. Literal shifts/increments compute

```
S <- floor(S/2)+[d=1 and c=e],
A <- floor(A/2)+c*e.
```

Equality A=S is replaced by zero; A>S rejects. The credited child theorem
proves A<=S. Since this branch has prior A>0, S>=2 and the child modulus is
positive. J decreases once, R twice and X is halved. The invariant now holds
at eta-1 and the requested canonical bit is unchanged. At most h loop
entrances occur. This induction proves all-height correctness independently
of finite fixtures. No recursion stack or whole permutation is produced.

The caller still owes the current-wire payload update between queries.
This predicate does not silently advance x or convert original-token labels.

## 5. Complete instruction and historical-backing bounds

Every R/W/M/J/H costs one; labels have no action. For at most W-bit records,
direct counts of the emitted loops give these safe complete bounds:

| Macro | Instructions including returns |
| --- | ---: |
| Rewind from relative position <=W+1 |3W+6|
| Zero test including destination jump |6W+5|
| Increment/decrement |7W+5|
| Zero a number |7W+4|
| Copy a number and return both heads |11W+7|
| Right shift |9W+2|
| Left shift |7W+5|
| Compare and branch |11W+10|

For example comparison uses two reads, two moves and one jump per bit,
then two frontier reads, two full rewinds and its destination jump. Right
shift has six transitions per following-bit transfer, plus its first move,
high zero and return. These counts include scanning erased spans to return.

The canonical height has ell<=h<W bits. Height countdown and WIDTH production
cost at most `h*(13ell+13)+6ell+3W+11`. Including guard creation, output check,
height copying, six numeric initializations, four field copies, R/2^h
construction and all domain checks gives

```
T_setup <=h*(13W+13)+208W+189.
```

A nonterminal query-loop entrance costs at most109W+77, including both
child shifts, both possible increments, equality reduction, J/R updates,
X halving and all branches/returns. Endpoint paths are shorter. The uniform
bound128(W+1) covers every entrance and its answer write when terminating.
There are at most h entrances.

Cleanup rewinds all six input/output roles. On each of eight private owners
it rewinds, erases every binary/END cell up to the first blank, returns
across that erased span, and erases its LEFT. Including halt this costs at
most98W+179. Therefore

```
T <=141hW+141h+306W+368
  =141h^2+588h+674
  <=1024(h+3)^2.
```

This is a source-loop bound, not a fit to measured times. For a canonical
positive h and malformed other records, rejection occurs during setup and
uses the same cleanup, so this envelope also suffices. No host allocation
or decoded-integer instruction has been treated as a constant-cost primitive.

Private visits lie in relative[-1,h+2]. H_IN visits[-1,ell]; each other
borrowed descriptor visits[-1,W]; OUT visits[-1,1]. Their total span is at
most13h+49<16(h+4). Adding these spans to entry history counts all guards,
frontiers and first visits, conservatively including borrowed spans already
present. The private working region has at most8(h+4) cells. Fixed alphabet
encoding changes the corresponding bit count by a fixed constant only.
Erasure never frees earlier history. Reuse at the same origins takes the
actual per-owner interval union; changed origins and transport corridors
are separately charged caller work.

## 6. Repeated queries and ROM reuse

For Q supplied queries, the service bill is at most1024Q(h+3)^2, plus actual
offset production, descriptor serialization, source transport, output use
and retirement. Successful private roles can be reused, retaining history.
A ROM alternative instead pays complete build B, actual query/return costs
sum R_q, and disposal. Direct evaluation improves a complete workload only
when those totals are compared on the same query sequence. Resident or
streaming ROM queries can be cheap and reuse can win for large Q. We do not
assume unproved future reuse or infer a speedup by comparing upper bounds.

The h5,s17,j6 test covers544 separate supplied queries. Their literal service
execution totals1473152 transitions, maximum2969 for one. These totals include
every predicate's setup/cleanup but exclude the harness's host serialization.
They are not an uninterrupted544-query caller or a speedup over retaining
and scanning a544-bit ROM. A small number of queries can avoid exponentially
large table production, but no complete selected-system gain follows here.

## 7. Executed evidence and residual obligations

The primary verifier imports only the pinned original `benes`/`rotation`
definitions for expected canonical table entries; it does not use #7504's
direct evaluator as that oracle. It executes all1566 entries of49 complete
networks through h3 and all544 entries at h5,s17,j6. The latter bit-byte SHA256
is bc0ab563e6d8fdfa24ee89b50dbe3f9a3a6f23681f491e883c6b5aeef07d4104.
Every fixed-graph execution observes all reads/writes/moves, head extrema,
owner writes and guard writes, and compares whole original buffers, private
capacities and exteriors after return.

Eight extra cases cover odd endpoints, the first padded wire, equality
reduction and low-branch dependence. Thirteen malformed/domain cases reject
with full stated cleanup; a private alias is rejected by the physical binder.
Three compiled semantic mutants swap the child branch, omit its carry or
omit the padded first-row bit. The canonical oracle detects all three.
Dyadic half-turns at h7,17,65,129 execute exactly h loop entrances and return1
without constructing exponential reference networks. Repeated halving of
a dyadic half-turn proves their expected result. Finite tests corroborate
the all-height proof and do not replace it.

There is no current CRT offset producer, descriptor adapter from #7388/#7390,
consecutive physical row/payload update, full exceptional-key integration or
measured ROM-reuse comparison. Input/owner/window and consumer costs remain
explicit. All five selected assumptions and the conditional kappa remain
unchanged. Independent human or proof-kernel acceptance is unclaimed.
Original authorship and Apache-2.0 notices are retained in NOTICE.md and inputs.
