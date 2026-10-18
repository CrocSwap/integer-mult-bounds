# Two mutable snapshots in the selected bit supplier's exact stream model

**Source-bound physical address construction, not supplier admission; no new κ.**
This supplies the physical-stream boundary left open by Ross Richardson's
[PR1704](https://github.com/CrocSwap/integer-mult-bounds/pull/1704) and the
[PR1943 record interpreter](https://github.com/CrocSwap/integer-mult-bounds/pull/1943).
It does not claim their 120-ADD saving or repeat their formal bank replay.

The fixed partition is `(0,3), (1), (2,4), (5,7), (6,8)` of retained totals
472–480. The exact selected owner template has 28,416 persistent families and
nine reserved private families. Allocate private families **28,416 and 28,417**,
with class **d** for the current common cover class d. They are different
physical streams from every persistent owner and from each other, even when
persistent values are correlated. Both are restored to zero before the next
invocation. The remaining seven reserved private families are untouched.

The nine COPY maps are the actual, distinct rank-seven partial swaps, not a
full swap and not a scalar identity. The verifier executes every MOVE as an
exact rational address pullback, checks every transported ERASE, and compares
all 661 arbitrary physical input functions in both complete local words and
both orientations. The recorded operator equality is stronger than equality
of frame labels, ranks, scalar coefficients, or a finite address sample.

## Exact contract and proof

### 1. Domain and actual owners

Use the ideal exact-stream model of
[PR1627](https://github.com/CrocSwap/integer-mult-bounds/pull/1627), specifically
its [physical hosting proof](../pr589-five-helper-hosting/PROOF.md). Let K be a
field of characteristic other than two. A physical memory location is a pair
`(family,g)` with `g` in the orthogonal cover group on K^64; its contents are an
arbitrary Boolean function on `K^64 × K^64`. Different locations need not have
independent contents. The local address operations below act on these actual
functions, not on finite role-column values.

For a hosted role in physical port family q, the source chart is
`σ = A_q π_S`, where `A_q = diag([q/2 | U_q],I_56)` and π_S sends local axes
0–7 to the eight listed pending axes, then unused axes in increasing order.
Its owner at common class d is `(F,d σ^-1)`. The original data chart is retained.
The checker reconstructs these chart descriptors from the actual hosting slots,
checks every `A_q` for exact orthogonality, and checks all 190,368 persistent
owner occurrences in the 288 stage/replica descriptors. It is not a census of
cover classes. For roles of one family, distinct π_S are distinct matrices:
apply them to a basis vector. Hence cancellation of the invertible d and A_q
proves that their owners are distinct for **every d over every such K**.
Persistent data and hosted helper families are separated by the source's
active/inactive-pair assignment.

For the two private roles use σ=I, owners `(28416,d)` and `(28417,d)`. Every
persistent family is in `[0,28416)`, while the selected reserved range is
`[28416,28425)`. Thus no choice of d, no chart coincidence, and no correlation
of values can alias a private role with a persistent one or with the other
private role. This argument is by family tags, not by an unproved inequality
between hashes or names of routes. Since `gσ=d` for private and persistent
roles, their chart-routed ADDs use the same common native address.

The reserve in this **exact stream model** is allocated work storage: the two
chosen private streams start blank, and the other seven are not accessed.
There is no reset of a dirty persistent input or of a previously used private
stream. COPY below is the ideal source-preserving transported injection; it
uses only its specified source and destination. This proof does not assert
that an implemented recursive COPY child's additional scratch fits in the
remaining seven families. That compiler obligation is separate from the
explicit stream allocation and is not discharged by the number nine.

### 2. Native address maps, including MOVE

For an exact symmetric idempotent P, let

`D_P(x,y) = ((I-P)x + Py, Px + (I-P)y)`.

It satisfies `D_P^2=I`. The frame projectors are reconstructed over Q from the
pinned root vectors. All resulting entries are dyadic; hence the displayed
matrix identities specialize to every K of characteristic other than two.
For stage s, the common exterior projector E_s is orthogonal to the local
8-dimensional block. Forward gauges are `Γ_f = D_(P_f+E_s)`; reflected gauges
are `Γ_f = D_(I_8-P_f+E_s)`. In both orientations the relative address map is

`Γ_a Γ_b^-1 = D_(P_a) D_(P_b)` on the local block,

with the identity on exterior coordinates. The common exterior factors cancel;
in the reflected case the two full local swaps cancel too. This establishes
why the verified 16×16 local maps are the actual restrictions of the ambient
128×128 maps, in all nine stages, rather than an address-size experiment.

MOVE from a to b changes the native function `f` to
`f ∘ (Γ_a Γ_b^-1)`. The interpreter **multiplies that rational matrix into every
function atom** at each MOVE. It does not skip MOVEs or merely check their labels.
The emitted record still pays its exact positive dimension increment. ADD is
XOR at the common native address; its operands must have the same frame.

In particular, retained total i is at its actual frame f_i, of rank seven,
and its copied slot is at frame 0. Its native copied function is

`c_i = f_i ∘ D_(P_f_i)`.

This formula is the same in the forward and reflected call. The nine operators
are recorded explicitly, along with an address basis column distinguishing
each from a rank-eight full swap. Distinct rank-seven frames are not identified.

### 3. Mutable snapshots, guard and contextual substitution

For two centers with arbitrary native functions f and h, first create
`p = f ∘ D_P` and `q = h ∘ D_Q` in the two distinct private locations. P and Q
may differ. They are never equated. After COPY, both slots and all scatter
targets are in the same common zero-frame module. The pair block is the literal
PR1704 word: exclusive target reads, `p += q`, common-target reads, `p -= q`,
then the two ERASEs. The signs agree for Boolean functions.

Pointwise, this returns `p=f∘D_P` and `q=h∘D_Q`; every target receives exactly
the same functions as the old separate-copy scatter. Each ERASE checks equality
against its **own current center transported by its own D_P or D_Q** before
removing the copied value. Equivalently it XORs that transported center into
the private stream, leaving zero. No other location is written. This is a
uniform function identity and uses no independence assumption on f, h or targets.

The new and old scatter therefore agree on all persistent physical functions,
all frames, and private zero at the cut. Their literal surrounding D/A/B/C
records are identical. Contextual substitution gives equality of the two
complete local calls. Reversing the events exchanges COPY with its guarded
ERASE inverse, reverses MOVEs, and negates ADD coefficients; the same pointwise
proof applies. The physical interpreter checks both orientations directly.
Because a complete call leaves both private streams blank, induction over the
source's sequential invocation order proves safe reuse for every replica,
stage and cover class. A cover sweep is not assumed to access previously unused
persistent streams; arbitrary current inputs are permitted on each call.

This adds the two-private physical substitution to PR1627's existing generic
frame and chronological hosting argument. It does **not** reproclaim that
argument or assert a new all-size construction from finite certificates.

## Complete price and relevance

All values below are measured or checked against the pinned words. No scalar
search or alternate partition is performed.

| Per local call | Single copied slot | Two private slots |
|---|---:|---:|
| Arbitrary persistent input functions |661|661|
| Peak live copied streams |1|2|
| COPY / ERASE |9 /9|9 /9|
| COPY rank sum |63|63|
| Peak live COPY rank |7|14|
| Persistent MOVEs |2,911|2,911|
| Scatter ADDs, including preparation/restoration |527|407|
| Complete ADDs |11,500|11,380|
| Local recursive rank mass |5,129|5,129|
| Retained physical families, including reserve |28,425|28,425|

Each COPY has one charged rank-seven child; its paired ERASE is the guarded
inverse under the inherited paired COPY/ERASE convention. There is no unpriced
extra rank-eight transfer, frame descent, or temporary. All MOVE charges are
retained. The profile is unchanged:
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`.
The complete source profile, idle children and outer normalization are not
reoptimized. Even granting spare private storage and scalar work for free
leaves the recursive moment unchanged. This is a concrete physical interface
completion for the bit mechanism, **not** a κ-improving result; the selected
complex-binding κ remains 0.001672660197076918.

The replay measures `F=25,717`, `B=6,248,884`; the inherited
`64 F^3 B^2` and `2^18 F^5 B^4` expressions occupy 96 and 182 bits, below the
104/192-bit caps. Address permutations preserve a function's coefficient norm;
every scalar addition, including restoration, is counted. These finite
algebraic guards are not a tape/routing/precision or child-scratch invoice.

## Reproduce and evidence

Standard-library CPython 3.12, from the repository root:

```sh
uv run --python 3.12 --no-project python -I -B research/bit-two-copy-physical/verify.py
uv run --python 3.12 --no-project python -I -B scripts/research_package.py --package research/bit-two-copy-physical
```

`RESULT.json` contains canonical exact physical endpoints' hashes, explicit
COPY matrices, complete bills and semantic controls. The ordinary replay
recomputes the entire payload and compares parsed values, not gzip headers.
`--emit NEW_PATH` is the explicit receipt-generation command and refuses overwrite.
All external scientific inputs are authenticated before reading their contents;
no predecessor executable code is imported. No whole-repository suite is needed.

The controls address omitted restoration hidden by blind deletion, wrong full
or equal-rank COPY maps, omitted COPY transport, a dirty fresh destination,
aliased private families, a one-family reserve, and a mispriced MOVE. A separate
control keeps all MOVE labels and charges but omits its actual address action;
the physical endpoint then fails. In the
blind-deletion control the persistent physical functions still agree, while the
actual chronological ERASE rejects. The checks remain enabled under `-O`.
Exact exercised commands/environment and output are in `VALIDATION.json`.

## Sources and scope

Scientific base: `564148b82ae9df72163f22106f15e73efca8aff2`, priority revision 4.
The submission checkpoint also read main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`: workflow guidance changed, but
scientific inputs, catalogue revision and selected record did not.
`SELECTION.json` preserves the independent nonce
`d275591f5a4f5d59e9e8231c8f6aad53` and both emitted bit cards. `TASK.json` records
the scope change before computation. `SOURCES.json` pins every consumed file by
Git blob and SHA256. The source/local/merged overlap check is not a novelty proof.
No discussion post is required to interpret this package.

Predecessors: Ross Richardson, PR1704 at
`7f14aa7285cf10a7be350472fab25a25ef898484` (fixed scalar scatter and bill);
Adam Gall, PR1943 at `60e0d6d37b857a30c2db032255892f7e2f6465ce`
(record lifecycle, explicitly projecting out MOVE addresses); alephnan, PR1627 at
`7943acd4b430dd4286e32954237136ee9657be3b` (exact stream model, selected owner
charts and one-private whole-call proof). Credit Sagar Thakrar PR1062 and the
PR967 helper-star/PR1015/PR923 block lineage, DreamingOfClouds PR589 and eumemic
PR555, and the hosting/geometry/formal lineage retained by PR1627, especially
cheesegrader PR540, DaysSky, Zhihao Chen, chafreaky, commdata2338 and Cinna Davis.

## Open next questions

Can an all-size compiler lower the two distinct private
owners and both guarded transports while preserving recursive-child scratch,
common-grid routing, tape and precision contracts? First bind these exact two
locations to its workspace allocator and price simultaneous child output plus
child scratch. The ideal-stream existence result does not answer that question.
In particular, `private_centre_reserve=9` is not by itself a child-scratch theorem.
A formal-kernel port, native compiled supplier replay, hosted finite invoice and
outer assembly are not supplied, and no hosted CI success is claimed.
The structured question is in `TASK.json`.

Prepared for Adam Gall with substantial OpenAI Codex assistance in proof,
implementation and writing. Apache-2.0. No independent human review is claimed.
