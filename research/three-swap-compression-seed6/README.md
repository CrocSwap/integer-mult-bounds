# Three swaps with arbitrary restored dirty registers cost nine calls

**Scoped computer-assisted negative theorem; no new κ.** In the formal
`F2[GL_2(F2)]` coordinate-CNOT register model, three coordinate-SWAP targets
require exactly **nine paid calls**, for any finite number of restored dirty
registers, even with arbitrary free scalar mixing. The explicit nine-call
word uses only the three active registers and restores the full boundary.

The new arbitrary-register step is a general compression lemma: a q-call word
for t swaps compresses to at most q−t registers. For three targets, parity and
address-representation rank leave only seven-call improvements; they compress
to four registers. Normalizing one label's three image vectors gives exactly
35 cases. Every case has a supplied UNSAT proof checked by two implementations.
The result rules out shared work in this specific optimistic alphabet. It is
not a lower bound for physical bit suppliers or other operation alphabets.

This addresses the arbitrary-workspace question in commdata2338's
[#1414](https://github.com/CrocSwap/integer-mult-bounds/pull/1414), pinned at
`9e1640094f649ba6db9742796825a8d6c238989b`, and extends the register-count scope
of their [#1491](https://github.com/CrocSwap/integer-mult-bounds/pull/1491), pinned
at `69638b36c691d3e1b8463526fd68c849e8d1aef9`. #1491 proves nine for exactly
three registers by a different Cayley census. Our proof does not import its
finite enumeration or rely on its lower-bound conclusion. No priority claim
is made for the formal model, sign quotient or the nine-call upper bound.

## Exact scope and complete paid comparison

The [proof](PROOF.md) defines every operation. A paid factor is
`I+([g]+1)uv^T`, with `g=a or b` and `v^T u=1` over F2. Each occurrence,
including an inverse, costs one. Extra registers start arbitrarily dirty and
must return identically, with no leakage to active outputs. Scalar register
basis changes are free in the lower-bound relaxation; no address operations,
COPY/ERASE, clean rows, overwrites or data-dependent choices are free.

Baseline: three calls `b,a,b` on each active coordinate projector, nine total.
The proposed seven-call shared alternative would save two in this optimistic
model. The exact certificates exclude it, including the fourth dirty row.
The attaining word needs no scalar preparation, helper allocation or deferred
restoration. A physical compiler would still price every complete address
call, coefficient/source access, frames, tape, precision and hosting. Such a
compiler or supplier recurrence is not provided; no multiplication endpoint
is inferred from unit paid-call counts.

## New proof mechanism

Apply the natural two-coordinate representation only as a necessary condition.
Let U_a and U_b span the paid projector image vectors for the two labels.
The target's top-right and bottom-left blocks both have image im(P), of
dimension t, so `im(P) <= U_a intersect U_b`. Therefore

```
dim(U_a+U_b) <= q−t.
```

Every paid projector and P preserves this subspace. Restriction retains
rank-one idempotence and exactly the same formal target on t active roles
plus restored dirty extras. This proves compression for arbitrary finite
workspace. At q=7,t=3, the smaller label count is three, and those three image
vectors form a basis of im(P). One scalar basis change fixes them at e0,e1,e2.
Exchanging address coordinates covers the reverse label counts. There are
`binomial(7,3)=35` remaining seven-letter patterns; none is omitted by a
heuristic or cyclic quotient.

For each pattern, all normalized projector choices are covered: eight choices
per fixed-image a projector and 120 choices per b projector. The constraint
proof covers the resulting Boolean domain; it is not a brute-force enumeration
of the corresponding 106,168,320,000 tuples per pattern.

## Evidence and verification

[CERTIFICATES.json.gz](CERTIFICATES.json.gz) contains all 35 exact CNFs and
DRUP proof logs. The decompressed payload SHA256 is
`90a23d6b20de8329e3db9e7555d1fb81a8c99edf5a4a76f9cd0ac1058b0b7ffa`.
Container bytes need not match across gzip versions: proof-relevant content
and rebuilt clauses are checked exactly.

- `cnf.py` builds a left-product formal group-algebra encoding, including all
  96 output coefficient bits and every fourth-register leakage coefficient.
- `verify.py` rebuilds every CNF and checks every proof by reverse unit
  propagation. All 161,432 original clauses and 3,836 validated additions are
  covered. Deletions are safely ignored because retained validated clauses
  remain consequences of the original formula.
- `independent.py` imports no encoder or watched checker. It checks all proof
  additions again with a separate scanning propagation engine, and the
  complete 24-column faithful regular boundary for one/two/three-swap words.
- `search.py` independently encodes right products using Boolean Z3 state
  variables and explicit 2x2 address matrices. It returns UNSAT on all 35
  patterns, with no timeouts. [SEARCH.json](SEARCH.json) records that completed
  bounded run; it is corroboration, not the proof trusted by replay.
- Controls reject invalid or unfinished proofs and an incorrect paid label.
  Exact truth tables check both directions of Tseitin equivalence. Watched
  and scanning unit propagation agree on all 2,304 two-variable cases. An
  explicit satisfying assignment checks the actual nine-call CNF. A natural
  representation kernel fixture demonstrates why that representation alone
  does not certify a formal endpoint.

Proof generation used python-sat 1.8.dev24 / Glucose3's
[DRUP interface](https://pysathq.github.io/docs/html/api/solvers.html).
The optional independent SMT run used z3-solver 4.13.4.0. Neither dependency
is needed to verify the committed certificates. No Lean or human review is
claimed. The written compression argument supplies the unbounded-register
step; finite solver output alone would not establish that step.

## Reproduce

From repository root, Python 3.12 and the standard library:

```sh
python3.12 scripts/research_package.py --package research/three-swap-compression-seed6
```

Expected: `PASS_THREE_SWAP_COMPRESSION`,
`PASS_INDEPENDENT_THREE_SWAP_COMPRESSION`, and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=negative-result`.
The development host took about two seconds for the watched replay and
35 seconds for the independent scanning replay. Wall times are observations,
not performance guarantees. Both checks also pass with Python assertions off.

Optional regeneration of this package's certificates and the independent SMT
run, using the pinned [build dependencies](requirements-build.txt):

```sh
python3.12 -m venv /tmp/three-swap-build
/tmp/three-swap-build/bin/pip install -r research/three-swap-compression-seed6/requirements-build.txt
/tmp/three-swap-build/bin/python research/three-swap-compression-seed6/generate.py
/tmp/three-swap-build/bin/python research/three-swap-compression-seed6/search.py --output /tmp/three-swap-search.json
```

A newly generated proof need not have the same clause sequence; it must be
validated and retain the complete 35-case domain. Regeneration touches only
this package. Immutable predecessor sources are not changed.

## Assignment, sources and limits

OS seed **6**, bit-supplier track. Exact base:
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. The seed rotates the solver processing
order starting at case six. The new question is the restored extra register
and rank compression, not a different optimizer seed. [TASK.json](TASK.json)
records the three candidate scopes, overlap, stopping rule and next questions;
[SOURCES.json](SOURCES.json) pins the model predecessors and historical state.
The [claim](CLAIM.md) is Discussion #1514.

The selected #1094 frontier, selected PR589 bit supplier and `upstream/` are
unchanged. Full selected cold replay and repository-wide artifact regeneration
were not run for this isolated proof package. Physical/all-size compiler,
common-label, hosting, precision/tape, analytic and bit H1–H5 obligations
remain inherited. The theorem concerns formal group-algebra equality for
arbitrary modules; a different physical address representation or paid
alphabet needs its own argument.

## Open next questions

For four active swaps, an eight-call counterexample can be padded with a
canceling paid pair to ten calls; compression bounds a ten-call counterexample
to at most six registers. First separate the 4/6 and 5/5 label-count cases: only the former
has a full fixed-image basis normalization. An exact encoding and checked
proof or witness would decide the next instance; no larger-target conclusion
is implied here. Separately, a physical compiler must price free scalar work
before any formal-model witness could imply a supplier gain. Structured first
steps and blockers are in TASK.json.

## Credit and license

Prepared by Cinna Davis (`1337isnot1337`) with substantial OpenAI Codex
assistance in proof, implementation, verification and writing. New work is
Apache-2.0. Credit commdata2338 for #1414/#1491's formal nonabelian model,
normalization, sign parity, earlier finite results and questions; Gareth
Davidson's #1333 for the scalar-mixing paid-call relaxation; and Ali Romman's
[three-register abelian obstruction](../bit-three-register-lower-bound/README.md)
as the task's model-change starting point. The selected bit lineage remains
credited to DreamingOfClouds/eumemic and its supplier/review contributors.
No predecessor executable implementation is imported. PySAT/Glucose and Z3
are optional proof-generation tools and retain their respective licenses.
