# Nine downward one-bit contacts for the 111-port graph

The normalized 630-field operator of Ali Romman's [#8027](https://github.com/CrocSwap/integer-mult-bounds/pull/8027) graph needs exactly **nine downward one-bit contacts** in the fixed-schedule model below. The incumbent has 27. A 13-port information obstruction rules out eight even for arbitrary nonlinear binary messages and interacting feedback, and the retained full word attains nine with identical public endpoints and all 630 output rows. The construction keeps all 2,776 original upward contacts in order, but each new return spans eight dimensions: total paid rank rises from **4,813 to 4,822**. At the target trial exponent the conditional full-caller histogram screen also gets worse. This is a normalized communication and graph result, **not a new κ lower bound, physical supplier, or admitted multiplication theorem**.

## Model and exact statement

The source graph has 630 independent public binary input fields, 636 rational frame projectors, and fixed initial and final public chart assignments. Write `P ≤ Q` when `PQ = QP = P` for projectors; a nested contact either moves upward in this order or downward. Each counted downward contact has a **binary-valued payload**, or equivalently a channel with at most one bit of information. Schedules, contacts, timing and the set of participating charts are fixed independently of inputs; local computation, memory and decoding can be arbitrary, and messages may depend nonlinearly on earlier traffic. New charts and interacting feedback are allowed. Private state initially contains no outside-input information. A `SWAP` exchanges owner names along with their values and chart labels, without transferring a value to another chart. All non-downward communication is along nested projectors, and no uncharged information is conveyed by observing a schedule.

Under those conditions, the public output at each original output chart must agree with the graph for all inputs. The minimum number of downward contacts is **nine**. The bit capacity restriction is essential: if a paid scalar may instead be an unrestricted integer, the 111 source bits can be encoded as `Σ 2^i x_i` in one integer and decoded after a single top-to-bottom contact. Binary inputs alone do not establish one-bit capacity. Our `F₂` scalar replay uses abstract chart labels defined by rational projectors; it does not claim that the resulting word is a physical general-field program.

The full operator is explicit. Its 630 output rows are `y_i=x_i` except rows `111+i`, `0≤i<111`, which are `y_(111+i)=x_(111+i) XOR x_i`. All initial and final owner charts are retained. The verified reverse execution is the matrix transpose over `F₂` of this entire `630 × 630` operator, not a physical field-adjoint certification.

## Why eight cannot suffice

Fix the other **617** input fields. Grant every receiver the complete chronological transcript `D` of all downward bits, along with every source bit whose initial projector is below its output projector. By induction over the fixed schedule, this grants at least the available information even with arbitrary earlier feedback: local work does not import a new input, upward nested moves preserve the order by transitivity, and every downward message has been supplied as part of `D`. The source's 111 rank-one/rank-seven endpoint pairings yield an exact side-information relation.

The checked witness uses eight clique ports `0, 14, 15, 30, 31, 60, 69, 70`, none of whose bits are visible to another clique receiver. Five other ports have the following visible clique endpoints:

| Outside port | Clique endpoints |
| --- | --- |
| 78 | 0, 14 |
| 77 | 0, 15 |
| 93 | 0, 30 |
| 61 | 14, 15 |
| 110 | 14, 30 |

Two outside receivers sharing an endpoint cannot see one another's bits. Suppose `D` has at most eight bits. With the five outside bits fixed, the eight clique inputs must map injectively, hence bijectively, to the 256 transcripts. Fix any one transcript; each of the 32 outside-bit assignments has exactly one clique-input vector in its fiber. Each clique bit is therefore a Boolean function only of the outside bits incident at that vertex. For an outside edge `(u,v)`, all nuisance variables incident to `u` and `v` besides the edge bit are disjoint. The sets of possible pairs of endpoint bits for edge value 0 and 1 form two Cartesian rectangles. Correct decoding requires them disjoint, so one endpoint's Boolean function must equal that edge bit or its complement for all nuisance choices. One endpoint cannot encode two independent edge bits this way. Five edges would need five distinct endpoints, but only four are available. The contradiction establishes nine for nonlinear and interactive binary protocols, not only linear rank arguments. The complete proof, including the input-capacity counterexample and simulation details, is in [INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md).

The checker extracts the relation from the graph; it does not assume an E8 label mask. It verifies all 636 rational projectors, 2,803 original nested moves and the 13-port witness. The nine native return fields restricted to the 111 head inputs have rank nine; an independently checked table supplies a nine-bit linear broadcast decoder for each of the 111 ports. That relaxed code supports the lower-bound analysis; the actual upper bound is the literal causal word below.

## Literal causal construction

[NINE-WORD.json.gz](NINE-WORD.json.gz) contains the complete modified program and its original frames and endpoints. [nine_word.py](nine_word.py) reconstructs it from the authenticated source with `--top-first`. The default zero-first construction is retained as the independently reproducible [first-pass receipt](FIRST-PASS-RESULT.json). For each of nine original three-contact return chains, it forms the required scalar as an XOR of live owners at chart 1 and chart 0, sends its chart-1 component **1 → 0** in one rank-eight MOVE, and adds the chart-0 component. The original live state outside the two eliminated intermediate owners is restored at each replacement boundary. The exact owner lists, source-clock triples, replacement clocks and feedback-field hashes are in [NINE-WORD-RESULT.json](NINE-WORD-RESULT.json).

| Native MOVE clocks, zero-based | Return owner | New MOVE clock |
| --- | ---: | ---: |
| 10997, 11002, 11013 | 3150 | 11004 |
| 11017, 11022, 11026 | 3153 | 11011 |
| 11030, 11035, 11039 | 3156 | 11025 |
| 11043, 11048, 11052 | 3159 | 11032 |
| 11056, 11061, 11065 | 3162 | 11040 |
| 11069, 11074, 11078 | 3165 | 11054 |
| 11082, 11087, 11091 | 3168 | 11063 |
| 11095, 11100, 11104 | 3171 | 11072 |
| 18866, 18871, 18875 | 3284 | 18837 |

Eight returns use only chart-1 donors; the fifth adds chart-0 owner 351 after delivery. The native and lean words contain 39,600 and 39,544 instructions, with 29,301 and 29,299 local XORs respectively. The first-pass nine-contact construction used 30,890 XORs, so top-first stock selection removes 1,591 XORs without changing its paid histogram. The independent replayer checks every public forward row and every transposed row, the unchanged ordered upward MOVEs and the complete clear accounting. Deleting one actual chart-1 donor ADD spoils **55** outputs while preserving instruction placement legality; the independent receipt records the first failed rows. This is an all-column symbolic test, not sampled inputs.

The native word has 3,433 symbolically nonzero private CLEAR values. The candidate removes the 18 intermediate owners from the nine chains and retains 3,415 CLEARs at exactly their former charts and with exactly their former symbolic values. Peak live owners fall from 4,063 to 4,045. Those retained values are **dirty**, and equal normalized traces do not prove their disposal, register restoration, lifetime legality, uncomputation or physical erasure cost. These requirements, general-field and compiler correctness, and the actual physical caller remain open.

## Frozen-upward direct price

A separate restricted theorem fixes the original upward receipt set, values, charts and clocks, forbids extra cross-chart traffic, and requires the first eight and then all nine native return forms by logical native boundaries 11104 and 18875 (inserted local operations do not consume communication ticks). Among nine direct-to-zero one-bit contacts, each sender must be chart 1; the minimum downward tariff in this class is exactly `9·8^t`. Independent high- and low-pivot audits check both 636-chart stock intersections, with a mutated-target control. This does not cover altered upstream traffic or other destinations. [Proof and precise contract](DIRECT-PRICE.md).

## Price and caller scope

Upward histograms are unchanged. Downward native counts at grades `(1,2,4,5)` are `(17,1,1,8)`; the candidate has nine grade-eight moves. Thus the local rank sum increases by 9. At trial `κ = 0.00389046`, the change in the single-invocation powered paid sum is

```
9·8^(1−κ) − 17 − 2^(1−κ) − 4^(1−κ) − 8·5^(1−κ)
  ∈ [8.696447871129279893, 8.696447871129279894].
```

[NINE-PRICE.json](NINE-PRICE.json) records outward rational intervals, using the retained #8041 arithmetic source. It reconstructs the original 36-local-call paired BIT caller histogram from its pinned event data, then substitutes the candidate histogram in 0, 1 or all 36 invocations, keeping other target, productive and inherited profile terms fixed. At the trial exponent, the raw target-minus-paid interval changes from approximately `−0.132405` at zero substitutions to `−8.828853` at one and `−313.204528` at 36. The corresponding **raw histogram crossing** intervals are `[0.00389011528659446, 0.00389011528659447]`, `[0.00386747070641162, 0.00386747070641163]`, and `[0.00307042508293270, 0.00307042508293271]`. The 268-factor screen also remains negative in all three cases. These are conditional arithmetic substitutions, not proof that the changed program is legal in one or 36 physical calls, and the raw crossing is not an independently established κ bound. The inherited #8035 conditional lower figure concerns its own native word and assumptions, not this candidate.

[#7829](https://github.com/CrocSwap/integer-mult-bounds/pull/7829), by DreamingOfClouds with Claude Opus 5.5, supplies CERTKIT/PRICEKIT and Lean certificates for specific different words under the **17-call #7113 caller**. Its packed caller record gives a pricing projection; it is not a full physical encoding of the caller. Neither the #7829 Lean proof nor its word-specific crossing is a certificate for this 36-call candidate. No #7829 Lean build is run here.

## Sources, replay and controls

The sole vendored raw graph is #8027 at head `fb9b6a7b0d27da1cf98430893a3016bf811e2aa4`; #8041 at `05f6172d4d9487090fa24c75137a7c60e6fcd67e` retained the same bytes. Their graph Git blob is `16f8cafb1c4d139a99a62e46eb40c118e6176c34`. The `pinned` directory also holds a small caller-data file and pricing code for the conditional arithmetic screen. [SOURCES.json](SOURCES.json) records Git blob IDs, compressed and expanded SHA-256s, provenance, and every checked script and receipt. Authenticating vendored bytes does not establish that external PR heads are reachable in a clean checkout.

Using Python 3.12 and its standard library from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/p104-nine-downward-contacts --check-only
python3.12 -I -B scripts/research_package.py --package research/p104-nine-downward-contacts
```

The registered command authenticates all checked bytes and three upstream Git blobs, checks independently implemented lower and direct-price replays, regenerates both the first-pass receipt and full lean candidate, checks an independent forward/transpose interpreter and its clear accounting, and reprices the local and caller histograms. Controls reject a corrupted source, a corrupted candidate, a wrong witness edge, a repeated clique port, an altered direct-price target, an eight-signal reduction and a deleted actual donor. Receipts are deterministic; regenerated gzip bytes may differ between zlib versions, so reconstruction is compared on canonical uncompressed bytes while the retained gzip itself is hash-pinned. The separate implementations and AI review are author-side evidence, not independent human or proof-kernel acceptance.

## Relation to earlier work

DreamingOfClouds's [E8 rank-8 closure](../p104-e8-rank8-closure/README.md) proves a related five-edge/13-line Hall obstruction for **linear** forced-zero factorizations under an assumed complex label pattern. Here the incidences are derived from the specific #8027 frames, and the fixed-transcript fiber argument addresses arbitrary nonlinear **binary** messages and feedback. It does not import that linear hypothesis as a theorem of the physical word. #8041 identifies a relay and a chart-1 cut; this coordinated rewrite changes all nine return chains. The separate local five-file CI prerequisite `0618e75a22cec54d1651394ef83d088551b7f026`, based on canonical `e54523517d0f03e58352e647c403a5af3e525a57`, is not part of the mathematics.

## Open next questions

- Can the changed graph satisfy the physical field, stock, register-lifetime and erasure contracts? Compile the concrete operations and audit all 3,415 retained dirty clears and the 18 eliminated allocations. A physical correctness proof is missing.
- Can any fully priced, legal alternative yield a favorable complete caller rather than just fewer contacts? Bind every change to the actual paired caller, include all paid and productive terms and the positive supplier, and certify the signed outer application. A favorable invoice and physical candidate are missing.
- Does a related lower bound hold for a larger scalar alphabet or input-dependent schedules when their full capacity is charged? Specify that model's communication and timing costs, then establish an appropriate information lower bound. The binary transcript proof does not cover it.

Ali Romman supplied the #8027 graph and physical supplier. DreamingOfClouds supplied the E8 closure and #7829, and the contributors in [PARENT-NOTICE](PARENT-NOTICE) supplied the predecessor chain. Clear1nsight prepared this work with substantial OpenAI Codex assistance, including the separate computational review. See [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE).
