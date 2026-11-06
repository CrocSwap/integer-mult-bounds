# Post-seal binding of the settlement derivation

Cross-reviewed 2026-11-06 around01:00UTC, after both first drafts were sealed. This is a source-aware cross-review, not a new independent derivation. No source/new scientific program, Field constructor, DP, witness, literal minors, permutation/raw-state search, test, experiment, import, compilation or kernel was executed. Only inert source/prose and metadata hash/time operations were read. No earlier note, seal or package file was edited.

## Exact objects and verdict

Source6712 head `03caa7f6cb5bd21c834024e9d81f6b43eb325b91`, directory `research/monomial-guard-settlement/`. Relevant byte bindings read after release:

- settlement.py Git74df4fb3154fc62775850fcf54136a46faa33989, local SHA256 `2667a15111b7d0dc8c887ea2813c8340e07f7f33385f35cb3e956100f25039e4`.
- literal.py Gitbef3d242ad16109eabf27a41cf0c34b47ad76c6d, SHA256 `479b78c3f4f0ca21294d84685c0d6177acdac96ae974d29b192516ab9ecd4391`.
- monomial.py Git3b68a6d1a59b8407f4b54706eeaad78dfa397e21, SHA256 `57f870433d7cc005b875527f83c85be21ee620cb3310f61a7b557a1cbd8cbd72`.
- example_check.py Git311863c06845ac005292e25c47338dc6cde83ad6, SHA256 `9e18439050d137e8e7a6a4774e927f0f1b614a2707863fd3cac73a467a813a05`.
- Peer SETTLEMENT-CODE-DRAFT.md SHA256 `7bf994a3a42da5f0f0c5f14744b3245429c883ea9cbf2074e027c0da931bb184`.

I also read the relevant central PROOF sections and the retained exact-arithmetic helper as inert text. Later proof sections appeared in that source excerpt, but binary-dummy, ternary, complexity/orbit and other later claims are not reviewed here.

**Qualified PASS** for the zero-target settlement path and anchored full-family implication, under valid exact-field and shape/label premises. No mathematical correction to my first draft is required. Its source-proof-unexposed timestamp/hash remains accurately historical: first draft `8befc623ef765523ab9ac6ec6ec29de003f482724e1340c166e4917236d36a78` is unchanged. No new h-Z/source numeric result is claimed.

## Actual dual orientation and attainable word

The source's target=i, source=j convention is exactly `u_i+=a*u_j` and, for EVERY supplied dual row, `row_j-=a*row_i`. It is the coupled inverse right action required by my charge formula, not its transpose or a plus-sign variant. Each row's old target entry is used and copies are made, so the source's value semantics agree with the algebra.

On `witness(...,target_value=None)`, active values are precisely nonzero vector charges. There is no dummy. A block's chosen root is its last real label; it need not be the label last removed by DP backtracking. Any donor in a zero-sum block works. The actual coefficient `mul[neg[u[i]]][inv[u[root]]]` is exactly -u_i/u_j, using field inversion rather than integer division. The donor u_j stays nonzero, each unvisited target u_i stays at its original nonzero value, and different blocks have disjoint labels. Thus every emitted coefficient is legal; intermediate cancellation of the donor CHARGE does not invalidate its nonzero u component.

The code returns gates/certificate metadata, not transformed u/rows. My abstract claim was that those gates form an attaining word, not that the dictionary itself executes a header. A consumer must replay the gates on the full desired dual data, including b when appropriate. The source already has that consumer in example_check; it is not a missing step newly identified here.

## DP mask order and literal backtracking

`subset_sums` evaluates its appended list from the old list before extension; its order is the ordinary labeled binary-mask order. Every vector has the same width in this certified domain. For a mask and any present low bit, `mask^bit<mask`, so the numeric mask loop has already computed each predecessor score. The added indicator is exactly “this nonempty full subset has zero sum,” matching the zero-prefix-boundary recurrence in my abstract note.

The actual backtracker removes stored last bits from the full mask. It keeps `end` at the last zero-total boundary. Whenever the remaining mask also has zero total, `end^mask` is a NONEMPTY set difference because the masks are nested; its charge sum is zero. Repeating covers all labels by the eventual empty mask. Blocks are returned in reverse boundary order with ascending labels within each block. That differs from literally returning the whole maximizing permutation, but it is equivalent for settlement: block order and internal elimination order are arbitrary. The block count equals the optimum score, so the gates attain h-Z. No silent correction of the first draft's more abstract ordering/backtracking description is needed.

## Anchor and existing full-minor consumer

The source anchor is exactly the one in my note: b supported at c, u_c*b_c=1, W_:c=0. The carrier is absent from the active list and untouched by emitted gates. Updating the complete b/W dual data therefore preserves that anchor. A free final permutation putting c last supplies the scalar prefix condition; separation alone remains insufficient for unanchored families or proper subfamilies.

`flat_rows` enumerates the FULL field-parameter family. `literal.complement` constructs I-u*v, and the proper-minor predicates exclude order m. `literal_orders` lists actual allowed proper subsets and checks every labeled ordering. `passing_permutations` uses the corresponding subset-sum predicate and likewise exempts the full set. These are compatible interpretations of the same proper-prefix condition, not evidence that this review executed either enumerator.

The anchored examples in `example_check.collect` request a slope-only witness. `example_check.example` then replays its gates through `add_row` on BOTH scalar b and slope w, constructs all flat rows, and compares a positive literal order count to the subset order count. This is a genuine existing source consumer, separately from stored witness dictionaries. Its finite search/minimum/count outputs were not rerun or newly accepted. The universal anchor argument, rather than those few examples, establishes the all-input implication.

## Field domain, qualifications and credit

The abstract h-Z argument is field-parametric. The actual imported Field constructor supports only q in{2,3,4,5,7,8,9}, with exact lookup tables; it is not an all-prime-power software constructor. This review read its implementation but did not execute or independently certify the arithmetic tables. Valid field operations, equal vector/row widths, canonical encoded elements and valid indices remain helper preconditions. Ordinary zip/indexing and minimal local guards are not hostile-packet/negative-index admission. No arbitrary field-object or new all-q executable API claim follows.

Word/coefficient choices depend on the known input, as the source operation metric permits. All nonzero field coefficients cost one abstract paid addition; physical coefficient generation, routing, selection, precision and restoration are separate. The zero-helper component lower bound still covers arbitrary allowed words, while the upper word preserves the anchor. It does not assert unchanged original u/W/b or a physical owner-return service.

The peer's qualified PASS and scope boundaries are accurate. No first-draft contradiction or source correction was found. SHIN09-git6712 retains h-Z, its witnesses and all later source results; classical zero-sum/component/elimination methods and earlier common-image work retain credit. No source arithmetic/DP/census, later binary/ternary/complexity theorem, physical/API restoration, native/selected-framework admission, human/kernel acceptance, new κ or frontier/adoption change is established by this note.
