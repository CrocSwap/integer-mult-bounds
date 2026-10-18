# Generic dirty-connector rigidity under paid invertible frames

**Scoped exact obstruction, not a selected-supplier result or new kappa.**
Add one operation family to Ross Richardson's universal dirty connector:
`FRAME_R: z <- R z`, for fixed nonidentity invertible F2-linear R. Even with
arbitrarily many such operations, the universal five-source/all-31-output
batch cannot use only **72 A/B map calls**. Under the explicit unit-token
price (one per complete A, B or frame), its optimum remains **74**; requiring
at least one nonidentity frame makes the optimum **76**. Frames need not
commute, and may be interleaved anywhere.

The contribution is the phase-normalization argument extending the existing
paired-readout obstruction to a new alphabet, not another pairing census.
The inherited 945-word exclusion is replayed only as a source-bound control.

## Exact changed interface

All x_j, y_i, z are distinct, arbitrary dirty L-bit rows, L >= 1. Sources
remain read-only. A_i and B_j are arbitrary square F2-linear maps, possibly
singular or noncommuting. The requested final operation is

    y_i += A_i sum_j M_ij B_j x_j; x_j and z restored.

The old complete operations are `B_j: z += B_j x_j` and
`A_i: y_i += A_i z`. The sole added family is `FRAME_R`, acting only on z.
Every complete call restores private scratch and entry heads, preserves other
rows, and has a charged implementation. No extra connector, source mutation,
output mixing, direct A_i B_j call, overwrite or hidden copy is admitted.

**Quantifiers matter.** A single straight-line operation word, including its
frame matrices, is fixed independently of the entries of A_i,B_j and must
work for every choice of those maps and all inputs. It may depend on M and L.
This is not a lower bound on circuits synthesized for particular operators
or charts chosen from relations between them. For the numerical corollary,
there are five sources and one output for every nonzero five-bit mask.
For L=1 the frame family is empty; the used-frame optimum concerns L>=2.

## Proof: paired-map endpoint survives every invertible frame word

Let P_t be the chronological product of all frames up to boundary t, with
P_0=I. No commutation is assumed. In normalized coordinates u=P_t^{-1}z,
frames leave u unchanged, and a B_j call at phase H contributes
H^{-1} B_j x_j. Consequently

    z_t = P_t (z_initial + sum_(B_j events s<t) P_s^{-1} B_j x_j).

Setting all sources to zero shows that final restoration requires P_final=I.
Every active source needs at least two B_j calls: one insertion leaves a
nonzero invertible transport times arbitrary B_j x_j. Every active output
needs at least two A_i calls: a sole readout leaves A_i P_t z_initial.
This gives 2(n+r) map calls for n active sources and r active outputs.

Suppose this endpoint is attained, so every active map appears twice.
For the two B_j phases H,H', restoration for arbitrary B_j gives
H^{-1}+H'^{-1}=0, hence H=H'. This equality is **derived**, not assumed.
For the two A_i readout phases K,K', cancellation of arbitrary connector
dirt gives K+K'=0, hence K=K'. One may set A_i or B_j to identity when
extracting these necessary matrix equalities; other maps need not commute.

A source whose two insertion events both lie inside or both outside the
interval between the readouts contributes zero. If exactly one lies inside,
its coefficient in that output is

    A_i K H_j^{-1} B_j.

Since K H_j^{-1} is invertible, the coefficient cannot vanish for all A_i,B_j.
It equals the requested A_i B_j for every A_i,B_j precisely when K=H_j.
Thus the requested binary mask is exactly the set of source labels crossing
the readout interval, just as in the original alphabet. Erasing all frames
therefore gives an ordinary twice-per-source word covering every requested
mask. This holds for any number of frames, any finite L and any n,r at the
paired endpoint. Conversely, an unframed solution remains allowed, so this
endpoint's feasibility is unchanged by the extension.

For five sources and all 31 nonzero masks, such a projected word would cover
all 32 masks including zero. The pinned predecessor's complete 945-pairing
exclusion has maximum coverage 31. Hence **72 map calls are impossible**, even
if frame operations were free. The existing 74-call repair remains an upper
bound with no frames. We do not claim 74 map calls are necessary with frames:
73-map words with three or more frames are not excluded here.

## The 74 / 76 token theorem and complete bill

Let N be the number of A/B calls and f the number of nonidentity frame calls.
The preceding proof gives N>=73 whenever f>0. Restoration of arbitrary dirt
requires f>=2. With exactly two frames, their product is I, so all cumulative
phases are I or one invertible R. If N=73, precisely one active map occurs
three times and every other map twice. For a triply used B_j, restoration
would require a sum of three members of {I,R^{-1}} to vanish. For a triply
used A_i, dirt cancellation requires a sum of three members of {I,R} to
vanish. Both are impossible: after pair cancellation one invertible matrix
remains. Therefore N=73 requires f>=3. If N>=74, f>=2 already suffices for
the lower bound. In all cases with frames, **N+f>=76**.

Without frames the original even-count parity and 72 exclusion give N>=74.
A predecessor 74-call word attains the overall bound. For L>=2, prepend an
explicit shear and its inverse to that word to attain 76 with frames. This
attainment intentionally contains a redundant frame pair: the theorem is a
sharp lower bound on *any* frame use, not a claim that a useful frame achieves
76. It includes identity-product frame words and their complete cleanup.

**Do not extend even-call parity to arbitrary frame words.** Over F2 let
T have rows (2,3). Then T^3=I and I+T+T^2=0. The chronological word
`B,T,B,T,B,T` restores z for every B,x,z despite three B calls. This is an
explicit semantic control for why the two-phase restriction above is needed.
It is a restoration identity, not a construction of the 31 requested outputs.

For an actual implementation price the entire word W by

    C(W) = I(W) + P(W) + D(W)
           + sum_i n_i c_Ai + sum_j n_j c_Bj + sum_frames c_R.

I pays input admission, layout and reserved-row initialization; P pays any
coefficient preparation and frame synthesis; D pays root instruction storage,
scheduling and dispatch. Each c includes coefficient/source access, arithmetic,
target updates, internal child dispatch, private scratch and head restoration.
No part of a frame is free. The unit-token theorem sets each call token to
one and excludes variable I/P/D: it is not a physical runtime optimum.
For positive lower prices c_* on A/B and f_* on frames, the map/frame portion
of every frame-using generic implementation is at least

    2 sum_i c_Ai + 2 sum_j c_Bj
      + min(c_* + 3 f_*, 2 c_* + 2 f_*).

Actual I/P/D must still be added. This is a necessary cost screen, not an
attainable unequal-price frontier. Cheap frames and expensive maps are not
universally ruled out; in particular the 73-map case remains unresolved.

## Smallest dirty-input instance and fully priced operation

A nonidentity invertible binary frame first exists at L=2. Use the single
shear R=(3,2), meaning `z_0 ^= z_1`, which is its own inverse and costs one
scalar XOR. With one source and one output, the chronological word

    R; B; A; B; A; R

implements `(x,z,y) -> (x,z,y+A B x)` for arbitrary two-by-two A,B and every
dirty x,z,y. The frame surrounds the echo; neither its entry nor its exit is
free. The verifier checks all 16*16*64=**16,384** map/input combinations,
including singular and noncommuting maps, lowers every operation into scalar
XORs, and replays every inverse.

The tempting word `B; R; A; R; B; A` is wrong without conjugating its maps.
For A=B=I, x=(0,0), z=(0,1), y=(0,0), it restores z but changes y to (1,0)
instead of leaving it zero. Thus checking only clean connectors misses the
failure. This is the smallest positive row dimension and source/output count
where the added operation and that dirty failure can occur.

For the explicit noncommuting price fixture A=(3,2), B=(1,3), each additive
map costs three source-to-target XORs. The old echo costs **12 scalar XORs**;
the framed echo costs **14**, including both frame operations. Number the
bits x,z,y as 0..5, with home one cell before bit zero. Under the explicit
fixed-port tariff `2*(max(source,target)+1)+5` per complete XOR (round-trip
movement, dispatch, two reads, one write and XOR), totals are **168 vs 194**.
No clean bit or full row is required in this scalar-XOR primitive model.
This tariff fully prices the fixed pilot's gates; external input preparation
is shared and excluded from both totals. It is not native supplier admission.

## Reproduction, scope and provenance

    uv run --python 3.12 --no-project python scripts/research_package.py --package research/connector-frame-rigidity
    uv run --python 3.12 --no-project python -I -O -B research/connector-frame-rigidity/verify.py

Initial commands passed on CPython 3.12.12 / Darwin arm64: the registered replay
in 0.24 seconds and the direct isolated optimized replay in 0.14 seconds
(single local timings, not benchmarks). They emitted
`PASS_CONNECTOR_FRAME_RIGIDITY` with the counts below; the wrapper also emitted
`PASS_REGISTERED_RESEARCH_PACKAGE`. No full repository suite or selected
frontier replay was run. The default Python 3.9 could not run the predecessor's
`int.bit_count` code or the package generator's `write_text(newline=...)`;
both prerequisites succeeded under the already-installed Python 3.12.

The registered check binds the three predecessor inputs in SOURCES.json.
The finite verifier separately checks all GL(2,2) phase pairs and all 9,216
phase/map coefficient combinations against direct vector composition, the
40 two-phase triples, the 256 odd-count
restoration cases, all 16,384 dirty pilot cases and inverses, five failing
mutations, and exact scalar/tariff totals. Checks do not rely on Python assert.
The arbitrary-dimension theorem is the written algebra above; these finite
checks are not formal verification of it or of integer multiplication.

Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Ross Richardson receives credit
for [the original connector contract, paired-prefix criterion and sharp
five-source obstruction](../universal-connector-boundary/README.md) (PR943 /
PR934 lineage). The new proof does not import predecessor executable code.
The historical selected record is provenance only; no frontier files change.

Closest live overlap is woklerx's [PR1858](https://github.com/CrocSwap/integer-mult-bounds/pull/1858),
head `4b650a8471c38f87519da497019dde24228c7f8a`, whose complete README was read.
It constructs chart transport **for structured fixed maps B1=R B0** with a
24-vs-32 scalar-XOR pilot. Our operator-independent generic theorem neither
refutes that construction nor claims priority for adding connector frames.
It supplies a different implication: frames cannot cure the generic paired
endpoint, and generic unit-token costs cannot improve. PR1518 (atomic triple
sums), the merged mutable-source/shear packages and the two-connector transfer
package change other operations and are not reimplemented here.

The initial overlap snapshot covered 539 open PRs including drafts and 524
discussion records, completely paginated at 2026-10-14 13:09-13:10 UTC.
The final refresh covered 541 open PRs at 13:20:07 UTC and 528 discussion
records at 13:21:27 UTC, again completely paginated; PR1858 retained the
same head. A new two-row frame proposal in discussion1167 comment18924276
adds a second dirty connector, outside this package's one-row contract.
Searches included connector frame, invertible connector, connector rotation
and order-three; relevant complete PR text was inspected. This does not cover
all code diffs, PR comments or all closed work and is not a novelty certificate.
Before publication, an offline search reused 558 PRs fetched at 13:42:39 UTC
and 529 discussion records fetched at 13:25:07 UTC, with explicit stale-cache
warnings. A targeted live query confirmed PR1858 open at its pinned head.
This scope is coordinated in the
[batch discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/1884).

## Open next questions

* Is a generic 73-map-call five-source construction possible with at least
  three invertible frames? It could matter only when frame costs are sufficiently
  low relative to map costs. Start with L=2 and its order-three phase relation,
  retaining all arbitrary-map coefficient constraints, rather than testing only
  identity maps. No such construction or impossibility proof is supplied here.
* Can structured chart transport be admitted at an actual selected-supplier
  boundary? First identify explicit related source maps, connector lifetime and
  complete native frame prices. Our generic quantifier deliberately excludes
  that relation-dependent synthesis; no admitted instance is known here.

Prepared for Adam Gall with substantial OpenAI Codex assistance in the proof,
implementation, experiments and writing. Apache-2.0 under repository terms.
