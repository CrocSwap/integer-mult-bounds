# A complete-caller zero fiber with 86N independent bits

The same-grid numerical ABI of [PR #6546](https://github.com/CrocSwap/integer-mult-bounds/pull/6546)
needs at least 86N bits of retained capacity for exact input recovery from its
public output and unchanged seed, where N=512^f. At width one this is 44,032
bits, or 5,504 bytes. The bound comes from a displayed family of actual legal
public inputs that all give the same complete output. A matching code is exact
on this family. It is not a claim that 86N bits suffice on every caller input.

This is a source-bound information result. It does not price physical clean
storage, prove a global minimum, invalidate the predecessor's error bounds,
discharge a selected assumption or improve the complete kappa calculation.
The predecessor already retains its inverse record; this result explains why
that record cannot all be recovered from only its public output and seed.

## Input, seed and data-access contract

Use the 22,803-event selected [PR #6030](https://github.com/CrocSwap/integer-mult-bounds/pull/6030) word pinned in SOURCES.json. There are
770 arbitrary public fields and 29 owned labels. Each public field has N
complex coordinates in `h*Z[i]`, for fixed h>0. Owned fields follow the source
INIT and CLEAR instructions. The argument uses the integer coordinates in
units h. There is no extra divisibility promise on the public inputs.

Fix the complete retained seed S. At a scalar instruction with q=p/D, the
forward component map is `floor((p*x+u)/D)`, with `0<=u<D`. ADD adds this rounded
increment to its destination, and SCALE overwrites its destination. A seed
can serve the whole field. Each MOVE accesses its declared data field; it
does not secretly read other public fields. Scalar operand reads and writes
are exactly those in the source word. All maps are deterministic when S is
fixed. Records do not feed back into the forward data path.

For the zero-output statement, native maps must send the zero field to zero
for every seed. This holds for the [fixed predecessor sampler](https://github.com/aliromman/integer-mult-bounds/blob/ff038070b8d122a43993f2b2524154323cc6b4d7/research/selected-absolute-stochastic-caller/sampler.py):
in its pair rule, x=y=0 gives s=d=c=0 for either sign. Gaussian-unit phases
and coordinate permutations preserve zero. Every native layer and tensor
composition therefore preserves zero. All scalar quantizers preserve zero
because floor(u/D)=0. COPY, INIT and CLEAR preserve a zero data state.

The counting lower bound only needs a common output. It remains valid for
other deterministic local native maps even if they do not preserve zero.
In that case the common output is F_S(0), which need not be zero. The stronger
zero value is not inferred without the stated zero-preserving contract.

## The complete first-access census

A field's first data access is its first read OR write. For ADD and COPY,
both destination and source count. MOVE and SCALE access their destination.
A first-write census alone would miss prior observations and is insufficient.

Two independent passes, an event scan and a separate search for each public
field, agree on every first access. Exactly 43 public fields first appear in
a signed half-SCALE. All have p=+1 or p=-1 and D=2. RESULT.json lists each
field, event, sign and frame. The fields are

```text
205,210,204,200,211,215,188,194,186,196,202,179,207,177,176,168,
167,214,216,218,222,157,161,160,172,141,140,219,135,134,152,150,
126,143,123,120,181,180,137,118,159,130,734.
```

The first is field 205 at event index 2. The last is field 734 at index 10447.
The first native MOVE is index 9896, so the proof must continue through native
calls before the last independent input is lost. It is not only a scalar-prefix
claim. Indices are zero based; the final independent label disappears at cut
10448, after that many completed events.

## A seedwise family of complete inputs

Let j(r) be the first-access half for a cohort field r. Its sign is p_r and
its retained seed is u_r in {0,1}. For each real and imaginary coordinate k,
choose an independent bit b_(r,k), and set the initial input to

```text
x_(r,k) = p_r*(b_(r,k)-u_r).
```

Set every other public component to zero. Every component has absolute value
at most one, so the physical inputs use only -h, 0 and h. There are exactly
`43*2*N` independent bits, and different bit arrays give different complete
public inputs. The all-zero input belongs to this family: choose b_(r,k)=u_r.

Before event j(r), no instruction reads or writes field r. It therefore still
contains its original coordinates. At that event,

```text
floor((p_r*x_(r,k)+u_r)/2) = floor(b_(r,k)/2) = 0,
(p_r*x_(r,k)+u_r) mod 2 = b_(r,k).
```

Use induction over every source event. Unconsumed family bits occur only in
their untouched input fields. All other live fields have values independent
of those bits. An instruction before the relevant first access cannot read
one of these fields. A certified half removes that field's bits from the data
state. Every other instruction acts on bit-independent data. Thus after cut
10448 the complete data state is independent of all bits, and the remainder
of the word has the same complete public output for every member of the family.

With zero-preserving native maps, strengthen the induction: every field apart
from those untouched inputs is exactly zero. A half maps its secret input to
zero. Every remaining instruction preserves zero. Consequently

```text
F_S(x) = 0 for all 2^(86*N) inputs in the displayed family,
for every fixed legal complete seed S.
```

The native interface and the source read set are explicit hypotheses. Hidden
reads of an untouched field could export its bits before the half and defeat
this proof. The executable causal checker rejects such a prior read. It also
checks the entire frame/ownership ledger and all 3,453 native zero operands.

## Retained capacity, dirty storage and the exact family code

An exact inverse from the public output, unchanged seed and b retained bits
must distinguish all members of the zero fiber. It therefore requires

```text
2^b >= 2^(86*N), hence b >= 86*N.
```

This is additional information besides the declared public output and seed.
Original input copies, changed seed contents, hidden tags or other output
metadata count as retained information if they carry the distinction.

A finite arbitrary dirty bank with Q possible initial states cannot reduce
the bound while its information remains recoverable. The input slice has
`2^(86*N)*Q` possibilities. The public output and unchanged seed are fixed,
so a b-bit record and a Q-state output bank have at most `2^b*Q` states.
Injectivity again gives b>=86N. This is a capacity count, not an initially
clean register lower bound or a proof about infinite auxiliary storage.

On the displayed family the bound is attained. Read the residue bit of each
of the 43 first-access halves in event order, with real/imaginary coordinates
in fixed order, and pack them. Given the unchanged 43 half seeds, reconstruct
x by the formula above and set the other public inputs to zero. Exactly 86N
bits suffice. Byte padding is zero; for N=512^f no padding is needed. The
codec rejects inputs outside this family. It is not a general inverse for
all inputs of the complete stochastic caller.

These bits are present literally in the predecessor's division record. On
this family every other division residue is determined by its seed, and all
old COPY/CLEAR values are zero. Thus the 86N-bit variation is an actual joint
record distinction; it is not obtained by adding unrelated local lower bounds.
No claim is made that the other records are recoverable on general inputs.

## A fixed input pair and fresh randomness

The seedwise family is a worst-case exact-recovery argument. It does not
require that an application choose its data after seeing the seed. There is
also a fixed, seed-independent pair: the zero input and the input with real
coordinate zero of field 205 equal to one, with every other component zero.
The first two events do not read field 205. If the seed of event 2 is zero,
its half maps either input to zero and every subsequent data field is zero.

Under the predecessor's fresh uniform sampling law, this event has probability
one half, regardless of later seeds. Thus this fixed pair has identical
complete public outputs with probability AT LEAST one half. No exact claim
is made about the final output for the other half seed. This is information
loss on a positive-probability event, not a failure of the stated numerical
error tolerance. Exact retained-state inversion still works as designed.

## Scope boundaries and verification

The lower bound is for unrestricted public h-grid inputs of this numerical
ABI. If all public coordinates are promised to be even in these units, each
pair `p*(b-u)` has only its zero member left. The displayed family then collapses
to one input. The bound does not transfer automatically to the finer exact
scalar entrance grids in [PR #6499](https://github.com/CrocSwap/integer-mult-bounds/pull/6499)
or to correlated public inputs reached by an actual multiplication encoding.
It also does not prohibit compute/copy/uncompute while the original input
remains available, or changes to the forward word, output encoding or seed ABI.

The verifier authenticates the word, performs both first-access censuses,
and proves the full causal label invariant. It checks every signed-half coin
and bit, 86 individual label positions, and the exact packed family code.
Fifty-three complete scalar/zero-contract replays cover 1,208,559 source
events, including two width-one 512-coordinate cases. Smaller one- and
four-coordinate cases test the dimension-independent contract. At each MOVE,
the verifier checks that its input is exactly zero and applies only the
proved zero contract. It does NOT run a compiled native implementation.

Nine semantic/domain controls cover prior reads, first-write confusion,
restricted grids, a biased zero map, nonzero padding, a truncated label, outside-family
inputs and a wrong retained seed. Source corruption is rejected. The large
fiber is proved by independent parameters and induction, not enumerated.
The pair sampler's zero behavior is read from its pinned implementation;
its complete native/scientific suite is not replayed here. No independent
human or proof-kernel acceptance, physical circuit/tape bill, full selected
cold replay or global maximum-fiber calculation is claimed.

The retained-bit and zero-fiber method is classical and has prior local
source-bound instances in [PR #6066](https://github.com/CrocSwap/integer-mult-bounds/pull/6066),
[PR #5323](https://github.com/CrocSwap/integer-mult-bounds/pull/5323) and
[PR #6540](https://github.com/CrocSwap/integer-mult-bounds/pull/6540).
The new contribution is the complete selected-caller causal fiber, its
independent 43-field census, the 86N-bit joint bound and its exact scope.
