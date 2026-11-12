# Independent review of the selected four-tape controller

**Outcome: PASS for the stated literal control interface.** The independent
interpreter found no correctness, restoration, transition-envelope or
historical-interval defect in the tested cases. The code and written loop/
stack invariants support the universal control claim; finite execution is
corroboration, not a replacement for that proof. No new kappa or complete
foundational-assumption discharge follows.

Prepared for Jerry Chen / @CubeJerry by the compiler/source-index worker,
independently of the controller author, with substantial OpenAI assistance.
Canonical source base: `e54523517d0f03e58352e647c403a5af3e525a57`.

## Exact reviewed source

Read `SOURCE-BINDING.md`, `GENERAL-CONTROL-PROOF.md`, all of
`selected_control.py`, and the Builder/instruction definitions in
`controller_reference.py`. Reviewed SHA256 values:

- `selected_control.py`:
  `1c977e9f4864d338f874aa4943d9f3422d964c3ab0cc2f877d9bc4c2d9e20237`.
- `controller_reference.py`:
  `e664a748e6b6797d4b60f60a7a7dd68b59a5608acf56b9c5d8b466f363755f73`.
- `SOURCE-BINDING.md`:
  `48ba45eb71df262db7384aa7a8003d9cd2801348c486948cab431528363bf6e5`.

No author file was edited. This review checks execution against the stated
rank-one law and supplied-cutoff contract; it does not independently certify
the selected final compiler word or its payload interfaces.

## Independent method

The checker calls only the subject's compile-time Builder/program generator.
It translates the resulting instructions to a separate six-opcode CPU with
integer symbol codes, dense read-dispatch tables and four dense tape arrays.
The author's Machine, Tape and initial_tapes names are replaced by rejecting
functions before the subject is imported. No author verifier or input helper
is imported or called.

The oracle first materializes the entire mathematical address tree breadth
first, using direct integer division and the predicate `e>=max(N,L)`. It then
assigns phase-order keys to each node's entry, pre-hook, child descent/return,
post-hook and exit events, and sorts those keys to obtain the contour. This
is independent of the subject's finite remainder machine and stack control.
At every emitted edge it compares the label **and the actual unary WIDTH**.
It also compares the complete active stack with the explicit ancestor list.

Dense buffers, event lists, trees, metrics and observers belong to the
verifier. They are not used to select a CPU instruction and are not claimed
as the controller's workspace representation.

## Results and adversarial coverage

Reproduce from this package directory:

```sh
python3 -I -W error -B independent_check.py . > evidence/independent.json
```

Observed result: **125 cases, 837 nodes, 3,654 emitted events and 488,423
literal transitions: PASS.** Every event matched its independently computed
width and chronological address. The cases use N in {2,3,5,7}, one through
four paid sites, widths through 4,097, supplied cutoffs through 100,003,
three independently shifted sets of tape origins, and repeated equal-rank
paid sites. They include e<N, exact cutoff equality, e=L-1, zero and positive
remainders, deep branching, and L much larger than e.

The observer checks:

- WIDTH, CHILD and CUTOFF heads at their required origins at every emit;
  actual parent restoration before U_i and A_r; exact positive child width
  before D_i.
- Entire CHILD and unused WIDTH histories blank at every emit, active STACK
  equal to the explicit ancestor record, and its retired suffix blank.
- All four tapes and heads restored on halt; no CUTOFF writes; no access below
  an entry marker. Hostile symbols below markers and beyond each active
  window remain unchanged, including on the source and scratch tapes.
- Exact program and alphabet census for every unchanged tested program:
  `30N+42+P(69+3N)` instruction locations and P+4 symbols.
- Total transitions, including HALT, below
  `200(P+1)*sum_v e_v`; the largest measured ratio to this bound is below 0.181.
- The comparison envelope `11*min(e,L)+10`, and **all 556 pre/post remainder
  scans** having the exact measured edge-to-edge duration `6e+7`.
- Historical visited intervals below
  `2(e+2)+e/(1-1/N)+D+2+min(e,L)+2`, and below its stated linear relaxation.
  Adding arbitrary entry backing K0 preserves the published bound.

For e=4,097 and L=100,001, the cutoff tape visits only 4,099 cells, while
its supplied unary input itself occupies 100,003 framed cells. Thus the
observed prefix bound does not conceal the cost of storing the supplied L;
the theorem must retain K0 as stated. Hostile exterior tests strengthen
the observed locality but do not remove the requirement for a valid blank
active scratch window.

Three semantic negative controls are rejected at the expected independent
comparison: changing A_1 to A_0; doubling the quotient's emitted unary
symbols; and treating cutoff equality as a leaf. The second fails on actual
WIDTH, not merely on its event label. The receipt records all cases and pins.

## Proof assessment and limits

The early N-probe enforces positive strictly smaller children. The later
comparator reads CUTOFF first, so equality enters; neither finite probe
requires traversing a larger cutoff. The remainder states advance modulo N
once per parent token and rewind before their hooks. The parent-width push,
site tag, transfer, child erasure and pop preserve the exact active ancestor
record, accounting for chronology and sibling reuse. Post-hook scans occur
only after the final U_i has restored the parent.

Rank one is essential to this source binding: `1*floor(e/N)=floor(e/N)`.
This check does not extend raw mixed-rank control to a different integer
rounding law. B_0/A_0 are finite hooks; their consumers must skip a zero-size
payload remainder. The supplied cutoff, chronological scalar/frame segments,
actual row grants, remainder consumers and leaf routine retain their own
construction, preservation and cost obligations. Emits are control edges,
not a free materialized event transcript. The selected enormous N/P template
and the complete multiplication machine remain unmaterialized.

## Root proof and integration review

The orchestrator separately checked the general and source-bound proofs, actual child-width law, cutoff equality, remainder hooks, restored-parent chronology, complete transition invoice and historical intervals. This identified the exact remainder-scan count correction to 6e+7 before the frozen snapshot; the conservative global bound is unchanged. The separate CPU confirms that corrected exact count. Source pins and the declared scope were rechecked before publication. Packaging changes only checker paths and review metadata; scientific controller and proof bytes are unchanged.
