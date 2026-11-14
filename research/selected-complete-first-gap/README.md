# Complete the selected first gap with literal half-source ADD and owner return

This package executes the actual five consecutive source events28037–28041
in one fixed45-tape graph: owned INIT, public half-source ADD, productive
frame137 MOVE, public ADD, and first owned SUB. It replaces the two external
ADD continuations left by the [published first-donor producer](https://github.com/CubeJerry/integer-mult-bounds/tree/a94e3f2ee0360202943b577ff8cd76245f6aa9ed/research/selected-first-donor-producer).

For initial public values A at212, B at449, C at124 and X at1349, the returned
values are `212=A+B/2`, `124=C+A+B/2`, `449=B`,
`1349=T137^(tensor f)X` and `1526=-T137^(tensor f)X`. No host intermediate
value is injected. The complete positive fixture makes one literal call
from INIT to HALT and checks all four public outputs and owned1526.

**No new kappa.** This is a uniform, local physical source-prefix theorem
under supplied initial-packet and same-width numerical conditions. The
selected complete bound remains conditional on its five assumptions.
Earlier packet production, the remaining lifetime and the full caller
are not executed here.

## Exact contribution and boundary

The source records are28037 `INIT1526`,28038 `ADD212<-449` with exterior1/2,
28039 `MOVE1349,3->601,false`,28040 `ADD124<-212` with+1, and28041
`SUB1526<-1349`. Frame3 is `[]`; frame601 is `[137]`. A full source typing
walk through28042 records confirms the initial and final owners/frames.
Source typing does not establish earlier numerical values.

The only new arithmetic is an even signed half-copy on the actual complete
Gamma6 working field. It physically parses every header, constructs unary
width from the fifth Gamma code, sign-extends every component, checks its
original least significant bit, pays every guide reset and retires all
private digits. It halves only a private copy of449. The original+1 ADD
then produces212; the later+1 ADD consumes that updated212.

The graph has71793 reachable states. All71524 predecessor states remain;
only the INIT and producer return targets change. The new269 states add
the half-copy and two paid bank contacts. Old bank43 retains its exact
five fields; new bank44 holds fixed public124,212,449. Successful execution
returns all45 heads, preserves the same physical owner arrays and clears
all40 reused private bodies.

All fields share the genuine frame/grid and complete header
`Gamma(f)Gamma(r)Gamma(P)Gamma(S)Gamma(w)Gamma(cutoff)`, w>=2.
Every B component must be even, and A+B/2 and C+A+B/2 must fit the signed
width. The actual frame137 producer separately retains its f<=cutoff,
phase and all-prefix integrality/range conditions. Successful first-gap
execution does not imply the later rank-two admission.

The prefix is not a global transaction. A later MOVE rejection leaves the
earlier public212 update committed. Each added ADD scatters only after its
own success, but failure cleanup, head return and retry are not claimed.

## Complete local bill

Set `V=2PSr2^(9f)w`, `E=|header|`, `F=E+V`. Each complete three-field bank
gather/scatter costs exactly7F+12 transitions. Two ADDs, the half-copy,
all new delivery, retirement and return edges add at most

`12334F+12370`.

Including the frozen zero constructor and actual137 producer, one convenient
whole-prefix bound is

`T <= 2^20(V_old+E_old+1) + 2^24(fV+E+1) + 32768(F+1) + 128`.

Added historical footprint is bounded by

`Delta K <= 64(V_old+E_old+3) + 4096(F+2)`.

Initial live-source acquisition, initial bank installation, earlier history
and any caller setup remain explicit additional costs. Erasure never refunds
history; the fV term is a paid leaf-order term, with no accelerated nonleaf
rate or complete multiplication improvement inferred.

## Reproduce

From the repository root, using Python3.12 and no third-party dependencies:

```sh
python3.12 -I -W error -B research/selected-complete-first-gap/verify.py --archive research/selected-complete-first-gap/inputs/selected-native.json.gz
python3.12 -I -O -W error -B research/selected-complete-first-gap/verify.py --archive research/selected-complete-first-gap/inputs/selected-native.json.gz
```

Both commands report `status: PASS` and produce identical JSON. The complete
positive run uses21,858,749 transitions with historical increment143240.
The graph digest is
`dbe04f2f719bf7c48ce02477871944a6c8ee1a6e1e73c331dc6c06d2de84ace7`.
VERIFY.json registers the commands. The ordinary verifier can omit `--archive`
to use the authenticated compact source witness; the registered runs also
re-extract the complete source archive.

Five complete half-packet cases cover widths2,3,6,17,129, with a2049-bit cutoff
in the last case. Twenty-four tiny bank cases check every position and the
exact7F+12 cost. Returning zero-fill and missing-guide-erasure mutations
distinguish arithmetic from cleanup. Odd, short, mismatched-header and alias
controls reject. The full returning skipped28038 control still gives the
correct1349 and1526 but fails the public-output oracle. A later-MOVE failure
checks that earlier INIT and ADD effects remain committed.

PROOF.md supplies the all-width/all-component argument and precise limits;
finite tests alone are not that proof. `--half-only` is a small diagnostic
subrun and does not constitute a full-prefix check.


Independent model-assisted review passes within the explicit ABI. A separate
sparse interpreter executes six complete arithmetic seam packets (2,962,252
transitions), eight controls and a 536,257-transition original native failure
join. Static comparison preserves all 71,524 old states except the two
declared return edges and checks both exact ADD embeddings. This avoids
relabeling a duplicate heavy positive native replay as independent evidence.
The uniform half/parity, complete public endpoint and cost proofs were
independently derived. See `REVIEW.md`, `RESULT.json` and `FREEZE.json`.

```sh
python3 -I -W error -B research/selected-complete-first-gap/independent_check.py research/selected-complete-first-gap
python3 -I -W error -B -O research/selected-complete-first-gap/independent_check.py research/selected-complete-first-gap
```

## Files and provenance

- `gap.py`: literal source-prefix compiler and exact input authentication.
- `cpu.py`: the unchanged C4 literal run method under fixed45-tape inventory;
  AST equivalence is checked, and no numerical payload oracle is used.
- `verify.py`: initial packet fixtures, direct source/scalar endpoint oracles,
  full literal execution and meaningful failure controls.
- `PROOF.md`: uniform correctness, exact chronology, restoration, full cost
  and history bounds, failure semantics, scope and predecessor credit.
- `SOURCE-PREFIX.json`, `SOURCE-PINS.json`, `SOURCES.json`: exact source,
  predecessor and canonical-main bindings. Forty-two retained dependency
  files preserve their original bytes; the small original source archive is
  supplied separately for complete re-extraction.
- `VERIFY-NORMAL.json`, `VERIFY-OPTIMIZED.json`, `VALIDATION.json`: executed
  primary evidence. Independent review is recorded with its own files.

Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`; immediate
predecessor is `a94e3f2ee0360202943b577ff8cd76245f6aa9ed`.
Credit @CubeJerry, the published first-donor/lifetime/OLD23-zero packages,
[the signed-contact primitive](https://github.com/CrocSwap/integer-mult-bounds/pull/7567),
its native/phase/linear/C predecessors, the older signed-half and rational
arithmetic work, and all retained notices. Substantial OpenAI assistance was
used for implementation, proof, testing and cross-review.

## Open next questions

1. Produce or acquire the actual initial124,212,449,1349 packets at the
   pre28037 boundary, proving their common grid/frame, evenness/range and
   all source-access, transport and earlier-history costs.
2. Compose subsequent productive donors and the later owned rank-two MOVE
   under one actual caller invariant; first-gap success gives neither its
   stronger cutoff nor its correlated-prefix integrality.
3. Extend a fixed chronological fragment only when each additional source
   and complete physical bill is established. This result supplies no
   generic native dispatcher, global assumption discharge or new kappa.
