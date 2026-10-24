# Scoped all-width charging implication for selected4470

## Statement and inherited interface

Fix the selected source closure at `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`, its complex p16/a7 controller and any positive column multiplicity `f`. The claim concerns only its 15 `QUERY_SHEAR` sites and 15 nonempty `IDLE` sites. It does not reprice full native calls, boundary scalars, the root, completion or the outer ledger.

Use the following named source premises. They are hypotheses, not results of this package.

1. **Complete child ABI.** A whole rank-`r*f` Gaussian child, including both exact rank-zero normalizers, acts on the specified complete field with every inactive/spectator coordinate retained. All borrowed caller and recursive helper state outside that field returns unchanged. The normalizers have the retained finite nonrecursive movement/scalar implementation. Exact absolute phase is part of the ABI.
2. **Private stream ABI.** A private full-volume stream can be allocated/cleared, copied to, added from and erased under the retained owned-stream and fixed-tape/precision contracts. Only private storage may be cleared. The relevant operation is a bulk record on the complete field; its physical cost is covered by that ABI, not declared zero here.
3. **Caller separation.** Source, destination, borrowed helpers and this invocation's private stream occupy distinct physical slots. If several parent instances are suspended, each retains its own stream until return. The finite compiler's global allocation/lifetime proof remains outside this local lemma.

The selected record explicitly retains `native_all_columns`, `owned_erasure`, `compiler` and `precision_tape`. PR4440 `PROOF.md` sections 1 and 5 already state the copied-query algorithm, rank-`f` request and finite nonrecursive allowance. PR4470 `PROOF.md` sections 4 and 6 retain that interface and enlarge the local reserve. The new implication below binds that protocol to every actual p16 site, distinguishes a whole multi-column request from factorwise requests, and derives the arbitrary-state endpoint and charge map.

**Conditional conclusion.** Under these premises, every expanded thin site has exactly one paid rank-`f` child and seven explicit nonrecursive logical records; every expanded idle site has exactly one paid rank-`8|S|f` child and two exact rank-zero normalizer records. No borrowed helper or spectator is erased. There is no additional recursive COPY, ADD or ERASE job in this specified protocol. This statement discharges the local charging implication under the admitted ABI; it does not establish that ABI on a concrete tape machine.

## Thin shear: direct proof at arbitrary width

For one source port let `T_q` be translation by its norm-one direction `q` and put

```text
a = (1+i)/2,  b = (1-i)/2,
Q = a I + b T_q,  Q^2 = T_q,  Q^-1 = T_q Q.
```

For `f` address columns use the completed operator `Q_f = Q tensor ... tensor Q` on those columns and identity on every spectator. Define `T_f` as translation by `q` in **all** `f` columns. Then `Q_f^-1 = T_f Q_f` exactly, including phase. Any fixed spectator space can be included; the proof is an equality of operators tensor identity, not a clean-state assumption.

Let `X,Y,H` be arbitrary independent full fields, with `H` standing for any number of borrowed helpers/spectators; let `Z0` be arbitrary old private contents. Execute this literal trace:

| Position | Operation | State after operation | Charge |
| --- | --- | --- | --- |
| 0 | `OWNED_CLEAR Z` | `(X,Y,0,H)` | Nonrecursive private-stream record |
| 1 | `COPY X -> Z` | `(X,Y,X,H)` | Nonrecursive complete-field record |
| 2 | Right monomial on `Z` | Input chart for the complete child | Nonrecursive normalizer record |
| 3 | One whole Gaussian child on `Z` | Normalized positive query result | Exactly one rank-`f` paid job |
| 4 | Left monomial on `Z` | `(X,Y,Q_f X,H)` | Nonrecursive normalizer record |
| 5 | `T_f` on `Z` | `(X,Y,Q_f^-1 X,H)` | Nonrecursive translation record |
| 6 | `ADD Z -> Y` | `(X,Y+Q_f^-1 X,Q_f^-1 X,H)` | Nonrecursive complete-field record |
| 7 | `OWNED_ERASE Z` | `(X,Y+Q_f^-1 X,0,H)` | Nonrecursive private-stream record |

The two query charts are actual address maps taking the line `q` to one coordinate in each column, followed by their inverses. They realize `Q_f` with one rank-`f` child. Translation `T_f` is a rank-zero address permutation, not another Gaussian child. The final erase is legal precisely because `Z` is private, even though its contents depend on an arbitrary borrowed source. Erasing the source, destination or helper instead is invalid. Private old contents `Z0` are intentionally discarded, while every borrowed initial symbol remains correctly represented.

The stream is one pre-reserved full-volume physical field, not an extra scalar and not an independently productive input. Its reservation belongs to the retained fixed-template storage envelope. There is no dynamic allocation/deallocation instruction inside the literal query trace; any concrete implementation that introduces those instructions must charge them under the same private-stream ABI. Between queries the stream is reusable only after the complete return/erase, and the checker rejects erasing only one spectator slice.

This argument holds for arbitrary inputs because every displayed equality is linear over the entire field space. It permits correlated values between distinct slots after COPY. It does not infer independent productive input credit for the copy. At no point does it tensor a two-owner shear matrix: `S(Q) tensor ... tensor S(Q)` is not the asserted multi-column shear. First form the complete `Q_f`, then perform the same COPY/query/ADD protocol on the complete arrays. Replacing `Q_f` with `Q tensor I` fails the width-two symbolic control.

All actual thin events are forward. The source general backward protocol would subtract `Q_f Y` from `X`, but it is unnecessary to admit a backward event at any of these 15 sites.

## Whole IDLE: one child, retaining the full spectator space

For each actual port, `DATA-PHASES.json` supplies `q` and eight old-space vectors `b_1,...,b_8`. The checker independently verifies that `(q,b_1,...,b_8)` is an orthonormal basis of the nine-dimensional old block. In particular `q.q=1`. Its phase-polynomial reconstruction checks that

```text
D_0 = F_9 Q^-1 = (source translation) product_j C_(b_j)
```

with the exact source translation; this is stronger than comparing only ranks or binary symplectic matrices. Each noninitial retained `D_s` acts on its own fresh eight-axis block. Consequently, for any actual idle set `S`, the completed product `product_(s in S) D_s` has an orthonormal active basis of exactly `8|S|` vectors. Stage zero contributes its old-eight complement, each other stage its own disjoint fresh-eight block, and every other coordinate remains a spectator. No set repeats a stage.

For completeness, a binary character is `parity(sum x_i) = sum x_i - 2 sum_(i<j) x_i*x_j (mod 4)`: terms of degree at least three vanish modulo four. The independent phase checker can therefore recover the complete phase polynomial from its values on weight-one and weight-two vectors. Matching those coefficients and the recorded even-linear translation proves the displayed absolute-phase equality for all addresses, rather than only the sampled addresses.

At width `f`, repeat that actual chart in each column. Its active dimension is `8|S|f`. The product, including any stage-zero translation, therefore has a whole-job normal form

```text
left rank-zero monomial ; one rank-(8|S|f) Gaussian child ; right rank-zero monomial.
```

Execution order is right monomial, child, left monomial. Translations are absorbed in the left normalizer. This is the source whole-job/Clifford ABI from `notes/general-clifford-frames.tex`; no new recursive job is required for a translation. The child acts on the entire original field, including every inactive column/axis and retained spectator. It may be applied to arbitrary dirty data; it does not allocate or erase a productive field.

An idle event applies this complete operator once to each of its two owners at each port. The jobs are not `|S|` independent rank-eight requests, nor is an old-nine central rank added. The exact stage sets below exclude all removed thin stages. This is a source-bound whole-idle rank argument, not an assumption that arbitrary Gaussian products have additive rank.

## Complete chronological charge map

`RESULT.json` contains all 30 relevant source events with their zero-based index in the unchanged 154-event word, actual pair/stage sets, destination/source roles, operation sequence and paid multiplicity. Its event indices are:

```text
thin:  5,12,19,26,33,40,47,53,59,65,71,77,83,89,95
idle:  2,9,16,23,30,37,44,100,101,102,103,104,105,106,107
```

Equivalently, thin stage `2j+2` acts from role `2j` to role `2j+1` for `j=0,...,14`. Initial idles have pair `j=1,...,7` and set `{0,1,3,...,2j-1}`; terminal idles have pair `j=7,...,14` and set `{2j+3,2j+5,...,31,32}`. These formulas are reconstructed independently from the source constructor and compared to the literal selected event word. Full event and phase bytes are authenticated first.

Associate a thin child with key `(event_index,port,Z)` and an idle child with `(event_index,port,physical_role)`. Keys are injective: different source events have different first component, ports are `0,...,111`, and the two idle roles are distinct. The private stream may be sequentially reused only after its erase. No recursive child is identified merely by equal rank, and no helper target is introduced by these sites.

Thus 15 thin sites expand to 1,680 distinct rank-one-coefficient jobs. This is calibration against PR4951, not a new invoice. The 15 whole idles expand to 3,360 jobs: rank coefficients `16,24,...,64` each occur 448 times and coefficient `72` occurs 224 times. At multiplicity `f` these coefficients multiply `f`; neither the number of jobs nor the spectator volume is divided by `f`.

The scoped nonrecursive logical-record list has `7*1680 + 2*3360 = 18,480` records. Existing source allowance terms are `16*1680` for query records and `32*112*len(physical_events)` for controller records. Allocate seven of each query's sixteen reserved records to its table entries and two per idle owner/port to that idle event's controller reserve. Each idle uses 448 records, below its per-event reserve of 3,584. No boundary or full-call reserve is consumed by this mapping. This uses a subset of the already stated allowance and changes no source numerical bound.

These are **logical bulk records**, not a newly proved count of scalar instructions or tape steps. The finite-template movement/precision contract must lower each exact monomial and each full-field operation with its stated allowance. An implementation that needs more physical work cannot be justified solely by `18,480 <= allowance`; it must satisfy the named ABI. In particular this package does not turn a fixed record count into an all-size tape theorem.

## Verification and remaining boundary

`verify.py` imports no predecessor verifier or operator implementation. It authenticates sources, checks all 112 actual old-nine phase charts, reconstructs every selected site and uses exact rational complex coefficients with independent symbolic input symbols at widths 1, 2 and 3, with one dirty spectator bit. A direct subset-convolution oracle for `Q_f^-1` is independent of the executed per-column positive query plus translation. The all-width conclusion follows from the written operator identity and direct-sum chart construction, not induction from three tests.

The semantic controls actually execute omission of initial clear, query, tensor translation and final erase; clearing borrowed data; overwriting the arbitrary destination; skipping the final active column; collapsing the spectator coordinate; and erasing only its first slice. Source controls drop/reorient a thin event and remove/replace an idle stage. Every rejection must survive optimized Python; no acceptance condition uses `assert`.

The unclosed physical implication is explicit: instantiate the private-stream and complete-child normalizer ABIs on a concrete fixed-tape layout with the stated precision, complete-volume scans and suspended-parent allocation. This is the existing inherited premise, not evidence that the selected conditional result has an omitted job. No claim about the 18 full calls, stage-zero full-call local invoice, global compiler ownership, full multiplication theorem or a new kappa is made.

## Credit

Cinna Davis / 1337isnot1337 supplied PR4440/4441/4447/4470; zxv supplied the native/controller lineage; Mihir Srivastava supplied PR4504's frame audit; Ryanson Jonathan supplied PR4478 and the controller replay; JoyboyBrian supplied PR4951's invoice join. The retained frame note credits icekylinx and OpenAI GPT-6 Astra; native phase, Clifford, scalar, geometry, ownership, precision and outer-framework contributors retain their source notices. This scoped implication and independent checker were prepared by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
