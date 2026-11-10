# Shared-wire composition and two newly enabled helper splits

This package constructs one exact native word from the frozen words of #6936 and #6937. Its canonical JSON SHA-256 is `91429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097`. The compressed artifact is `data/final.json.gz`; reproducibility compares the decompressed JSON, not gzip headers.

## Changes and attribution

1. Compose the sixteen shared helper wires in #6937's `wh` with the two additional plain splits present in #6936. The unsplit seven main wires and sixteen helper wires are predecessor work, not discoveries of this package. The composition is new here: #6937 explicitly left it open. Register renaming reserves 1459 and 1460 for #6936's tails and shifts the `wh` additions by two. The resulting word has 71,228 events and 1,477 public fields.
2. Replace a further matched pair of direct contacts at frame 709 by one shared wire, public field 1477. The contacts are `449 += 226` and `990 -= 1206`. The new wire visits frames `3, 260, 724, 246`. Its credit is rank 8. Four pairs of consecutive partner MOVEs merge; the exact paid histogram includes those mergers and the wire's three MOVEs. This produces 71,233 events and 1,478 public fields.
3. Split helper 759 at frame 660, replacing its rank-9 credit by ranks 7 and 2. Split helper 450 at frame 595, replacing its rank-9 credit by ranks 1 and 8. These two new directions are enabled by #6937's sixteen wires, and already exist in `wh`; the seventeenth wire is not necessary to enable them. Both compose with the entire preceding construction.

The final word has 71,261 events, 1,480 public fields, 1,080 helpers, 51 owned fields, 54 owned lifetimes, peak owned count 43, and the same 23 owned rises of rank mass 56 as #6936. The 1,095-frame table and 400 main fields are unchanged. Event counts are 61,180 ADD, 1 COPY, 3,662 SCALE, 6,310 MOVE, 54 INIT and 54 CLEAR.

The construction builds on DreamingOfClouds' #6936/#6937 words and handoff, Ali Romman's helper-split lemma (#5599), CubeJerry's helper-split native-word applications (#6916), CubeJerry's caller blocks and owned-rise work (#6912/#6914), unpaidmoon's phase test (#6930), and icekylinx's odd-grid precedent (#104). Original authors and notices remain attached to frozen sources. New construction and checks were developed with substantial OpenAI assistance.

## Causal composition

Each event has, for every touched register, one of three access classes: source-read R, ADD destination A, or exclusive M. MOVE, SCALE, INIT, CLEAR and COPY destination are exclusive. Consecutive R accesses commute with each other; consecutive A accesses commute with each other. Every pair across consecutive unlike runs is ordered. `compose.py` forms the union of these dependency edges from the two source words after exact register renaming and event selection, then finds a topological order. No access is moved through an incompatible access.

The sixteen-wire branch's noncommon retained events and the two-split branch's noncommon retained events have disjoint register footprints. All common literal events retain the same multiplicity. Independent cross-review checked those facts separately. The generated word is then replayed over exact fractions on every independent public input, so all new helper inputs, not merely zero helper initializations, are tested.

For the seventeenth wire, write Y=449, X=226, U=990, V=1206, H=1477. At the four rests, its ADDs are:

| Rest | ADDs in order |
|---|---|
| 3 | Y += H; H += V |
| 260 | U -= H; H -= X |
| 724 | H -= V; Y -= H |
| 246 | H += X; U += H |

The exact transfer is Y += X, U -= V, H unchanged. The generator places each partner access inside its uninterrupted compatible access run and preserves every remaining access dependency. It merges only the four partner MOVE pairs whose intervening direct contacts disappear.

## Split identity and exact witnesses

Let P be the prefix map and S the suffix map at a common cut frame. Suppose aP=c and Sb=d, where c and d are supported on helpers sharing the same entry and exit frames, with a·b=c·d=1. Choose boundary B0 and cut BC with pivot row c and a, respectively, and inverse pivot column d and b, respectively. The normalized prefix BC P B0^-1 has pivot row equal to the original independent pivot input. The normalized suffix B0 S BC^-1 has pivot column equal to the corresponding independent pivot output. Terminating that pivot at the cut and replacing subsequent uses by a fresh independent tail therefore yields two independent identity helpers. No MOVE is added; the target rank splits additively.

`basis(c,d,p,f)` constructs these elementary changes of basis. After an optional same-frame swap, its pivot row becomes c; each other row j is changed to e_j−d_j c. Thus B d=e_p. The coefficient at the chosen pivot is a unit for both concrete witnesses. The generator recomputes c and d from exact prefix and reverse suffix maps rather than accepting the certificate vectors on trust.

For helper 759, immediately after event 42531 of the 71,233-event word:

- cut frame 660, rank 7;
- a=e759, b=e759−e758;
- c=e759−e1472, d=−e758−e1472.

For helper 450, immediately after event 37192 of the first-split word:

- cut frame 595, rank 1;
- a=e450, b=e450−e1207;
- c=e1050+2e1070+e1466;
- d=4e1075−e1053+e1466.

Both have a·b=c·d=1 exactly. All cut supports are public. No zero scratch extension or new owned CLEAR is used. The complete vectors and emitted changes of basis are in `data/*proof.json`.

## Exact native invoice delta

Relative to #6936, per native call:

| Rank | Helper-credit change | Paid-MOVE change |
|---:|---:|---:|
| 1 | +1 | −34 |
| 2 | +1 | −50 |
| 3 | 0 | +30 |
| 4 | 0 | +23 |
| 5 | 0 | +16 |
| 6 | +1 | +2 |
| 7 | +4 | 0 |
| 8 | +5 | 0 |
| 9 | +7 | 0 |

Both rank masses increase by 140 per call; the complete 18-call surplus remains 1520. The complete kernel moment D falls from 422226.7185002353… to 421882.370033337478… on the original caller. The QUERY-only E-free caller of #6980 removes 192 rank-1 targets and 192 rank-1 paid jobs together, leaving the crossing unchanged. Independent full caller/invoice/interval/precision review gives crossing `0.00363005817468836708593357676489689967…`, conservative ordinary total 826790496, and proposed claimed/tested prices `.00363005817` / `.00363005817007`. These complete caller and outer checks are included in this package; `native-accounting.json` explicitly retains the original-caller comparison for attribution.

## Reproduction and limits

Run `python -B verify.py`. This cold-reconstructs all four stages from the two frozen input words, checks exact cut vectors, compares final canonical payloads, and runs the predecessor's exact odd verifier with S=1125. `python -B chart_delta.py data/final.json.gz` lowers all 73 newly introduced native chart pairs (71 MOVE pairs and two helper endpoints), checking exact rank, signed operator and global phase at width 1; 61 old pairs retire. The same-frame scalar proof and exact symbolic endpoint do not constitute an all-width native-provider admission.

The construction inherits odd native scalars with exact child returns and prefix grid S=1125, owned ascent A6 and peak 43, owned erasure, per-port/reducible roots, helper accounting, LAMBDA ordinary pricing, the compiler, precision tape, analytic recovery, and native-all-columns obligations. It does not discharge these assumptions or update the selected result. The final caller integration removes the empty-root-field credit premise; the paired QUERY-only BIT dependency is pinned at commit `d777f3a0aa2878bea0478918923dabcf86b9878b` in `INDEPENDENT-SOURCES.json`.

## Open next questions

1. Can further causal changes expose additional pure prefix/suffix pairings after these two splits? The remaining chronological search described in the handoff is finite and scoped, not a universal obstruction.
2. Can a generalized split with nontrivial a·b be realized with ordinary zero cleanup and a complete native invoice? No such witness is used here.
3. Can combs with more than four rests exceed the one-wire opportunities while retaining exact independent helper restoration? Fixed four-rest sharing bounds do not exclude that changed itinerary.
