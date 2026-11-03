# A 120N-bit complete-caller fiber from silent rounded reads

This scoped proof concerns the same-grid stochastic numerical ABI of Ali
Romman's [PR6546](https://github.com/CrocSwap/integer-mult-bounds/pull/6546)
at `ff038070b8d122a43993f2b2524154323cc6b4d7`, on the selected PR6030 word.
It builds on the complete-caller fiber argument in his
[PR6547](https://github.com/CrocSwap/integer-mult-bounds/pull/6547), exact head
`317e4a099488794c372f8a4ad1e70deef3626bbf`. That predecessor's every-seed
86N-bit family is cited, not independently verified here.

The new step permits fractional reads before erasure. One explicit seed
schedule makes 39 such reads of 17 additional fields silent. The resulting
60-field family strengthens the worst-case retained-capacity lower bound to
120N bits. The seed quantifier is weaker than the predecessor's: this proof
constructs one schedule, rather than treating every schedule.

## Contract and theorem

There are 770 arbitrary public fields, each with N complex coordinates in
`h Z[i]`, for fixed h>0 and N=512^f. Initial owned fields are zero and obey
the source INIT instructions. Work in integer coordinates in units h.
For a scalar coefficient q=p/D in lowest terms, D>0, the retained scalar
seed u belongs to {0,...,D-1}. Its component map is

```text
Q(q,x,u) = floor((p*x+u)/D).
```

ADD adds this rounded source product to the destination; SCALE replaces
its destination. COPY has the literal source/destination read set. Native
MOVE accesses only its declared field and sends the all-zero field to zero
for each fixed legal native seed. Records do not feed the forward data path.
These are hypotheses inherited from PR6546 and PR6547, not new native claims.

Fix the scalar schedule

```text
u(p,D) = 0 if p>0; D-1 if p<0.
```

The schedule depends only on the instruction coefficient, not the input,
coordinate, or a previous output. It is a legal fixed realization of the
stochastic ABI. Fix any legal native seeds satisfying the zero contract.

**Theorem.** The fixed complete map has a displayed family of
`2^(120N)` distinct public inputs with identical all-zero complete data
output. Exact recovery from that output and the unchanged seed needs at
least 120N bits of additional retained capacity. At f=1 this is 61,440 bits,
or 7,680 bytes. This exceeds the predecessor's reported worst-case floor
by 34N bits, or 2,176 bytes at f=1.

The theorem is for unrestricted public same-grid inputs. It does not assert
a new bound under an even-coordinate entrance promise, correlations imposed
by multiplication, or another word/output/seed interface.

## Silent source reads

If b is either zero or one and 0<|p|<D, then

```text
Q(p/D,b,u(p,D)) = 0.
```

For p>0, both possible numerators lie in [0,D-1]. For p<0, they are D-1 and
D-1+p, again in [0,D-1]. Also Q(q,0,u)=0 for every legal seed. Thus a
fractional read of an unmodified binary input can reveal no information
through the rounded increment, even though it is a genuine data read.
An integer source coefficient has no such guarantee and is excluded.

## The 60-field witness

Independently choose a bit for each real and imaginary coordinate of each
of these public fields; set every other public input component to zero:

```text
118 119 120 121 122 123 126 130 134 135 137 139
140 141 143 150 152 156 157 158 159 160 161 162
163 165 167 168 172 176 177 179 180 181 182 184
186 188 191 194 196 200 202 204 205 207 210 211
214 215 216 218 219 222 223 259 289 369 506 734
```

The source-bound certificate records each field's first SCALE, which is a
signed half. Before that SCALE there is no other SCALE, MOVE, COPY, INIT or
CLEAR accessing that field, and every ADD source read has 0<|q|<1. ADDs
may use the field as a destination. The per-field scan and a separate
whole-word active-label check agree on every erasure event.

There are exactly 39 ADD source reads before erasure, across 17 fields.
Their full list and all 60 erasure cuts are emitted by verify.py, bound to
the compressed source hash and verifier hash. The last erasure is event
10447, so no bit survives after cut 10448. Event indices are zero based.
No claim of a maximum fiber or an exhaustive classification is made.

## Complete chronological induction

At every cut, each not-yet-erased witness field contains only its original
independent binary coordinates. Every other live data field is zero.
This holds at entry.

- An ADD source is zero or an active witness field. A zero source gives
  zero increment. An active source has 0<|q|<1 by the certificate, so the
  silent-read identity gives zero increment for both possible bits. The
  destination is unchanged, preserving the invariant even when active.
- A SCALE on an active witness is its certified first signed half. It
  maps both bits to zero and erases that label. A SCALE on any other field
  preserves its zero value.
- A COPY, INIT or CLEAR touches no active witness. All of its data are zero.
- Every MOVE operand is zero. The stipulated native zero contract preserves
  it. No hidden read of another field is permitted by this contract.

The checker traverses all 22,803 source events, including all 3,453 MOVEs.
The last erasure occurs after native calls have begun. After cut 10448 all
data are zero, and the remaining instructions preserve zero. The induction
holds componentwise for arbitrary N; it does not enumerate 2^(120N) inputs.

## Retained capacity and a matching family code

The input bits give exactly 2^(60*2*N) distinct public inputs, since they
occupy distinct initial coordinates. The output and complete fixed seed
are identical. A b-bit retained record allows at most 2^b distinct inverse
states, hence b>=120N. Original input copies or changed seed contents that
carry these distinctions count as retained information.

An arbitrary dirty bank with Q possible initial states does not remove the
obligation if its original state must remain recoverable. Injectivity on
the product family requires 2^(120N)*Q <= 2^b*Q, giving the same bound.
This is an information-capacity result, not an initially clean hardware
storage minimum.

Packing the original 120N bits gives a matching code on this displayed
family. More concretely, each erasing signed half has residue
`(p*b+u) mod 2`, equal to b for p=1 and to 1-b for p=-1. The 60 such residue
fields therefore also encode every original bit bijectively. This uses
the literal retained residue ABI; it is not a full-input recovery schedule
or an assertion that other records are redundant on general inputs.

## Limits

The every-seed statement of PR6547 remains distinct. This new family uses
one coefficient-sign-dependent scalar schedule. A wrong seed can make a
negative fractional read nonzero, and changing an input bit to two can
survive a positive half; the checker computes both boundary witnesses.

The finite replays corroborate the written induction. They do not run
compiled native operators, establish a global fiber maximum, prove physical
randomness/routing/restoration costs, discharge the five selected assumptions,
or supply a complete multiplication theorem or a new kappa.

This contribution was produced by Nick Petalas. Credit Ali Romman for the
same-grid caller, zero-fiber method and question; DreamingOfClouds for PR6030
and its retained P104 lineage; zxv for the signed-half residue interface in
PR6066. Pigeonhole counting and chronological induction are classical.
