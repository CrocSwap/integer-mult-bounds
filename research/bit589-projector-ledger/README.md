# Independent exact-projector audit of the PR589 bit ledger

**Independent finite audit; no new supplier, packing bound, endpoint or κ.**
The source-to-ledger check passes for both the untuned PR555 word and the
retained PR589 word. Exact rational orthogonal projectors recover every local
paid rank. The nine-stage schedule and frozen selection recover the global
histogram without using that histogram to infer the idle capacities.

This deliberately corroborates existing results using a separate implementation.
The original `xcheck_p.py`, `wlib.py` and record exporter already check the local
word; this package does not claim discovery of its correctness or a defect in
those checkers. The additional artifact is a compact independent path from the
two source words to the selected bit invoice, with a different geometric method
and explicit failure controls.

## Result

Both words have 636 frames in **Q⁸**, 661 scalar registers over **F₂**, and one
clean, restored COPY temporary. Each forward or reverse record stream has:

| Item | Count |
|---|---:|
| MOVE records | 2,911 |
| Common-frame ADD records | 24,305 |
| COPY / ERASE records | 9 / 9 |
| Total records | 27,234 |
| Symbolic dirty-input columns | 661 |
| Local paid rank mass, including COPY | 5,129 |

The exact local profiles are:

```text
PR555: {1:1321, 2:1342, 3:80, 4:47, 5:102, 6:10, 7:18}
PR589: {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}
delta: +2 H1 - H3 - 3 H4 + H6 + H7
```

All nine copies have rank seven. Every ordinary input, including all 439 dirty
helper inputs, is represented by a distinct symbolic bit. Both orientations
restore sources and helpers and implement `y_t -> y_t + x_t` on all targets.
The COPY temporary starts and ends at zero in each lifetime.

The selected nine-stage parameters are `L=9, K=4, T=32, m=64, v=111`.
There are 288 local invocations and 28,416 live data roles. The independently
derived idle remainder per replica is
`{2:435, 4:444, 6:444, 7:666, 42:9}`. Therefore:

```text
global = 288 * local_PR589 + 32 * idle_per_replica
       = {1:381024, 2:400416, 3:22752, 4:26880,
          5:29376, 6:17376, 7:26784, 42:288}
rank mass = 1,808,352
64 * 28,416 - 1,808,352 = 10,272
```

[RESULT.json](RESULT.json) records both complete profiles, every idle window,
COPY ranks, per-phase ADD counts, exact projector and record-byte digests, and
the 16 rejected controls. It is recomputed and compared on every normal replay;
normal replay writes no package files.

## Why the projector calculation certifies each local rank

The label form is one half the standard dot product. Multiplying an inner
product by a positive scalar leaves its orthogonal projectors unchanged.
For each rational frame span F, exact Gram–Schmidt gives nonzero orthogonal
vectors `u_i`; form

`P_F = Σ_i u_i u_iᵀ / (u_iᵀ u_i)`.

The checker stores this as an integer matrix `M/d`, and checks symmetry,
`M²=dM` and `tr(M)=d dim(F)` by integer arithmetic. It also checks that the
frame lists **exactly** the live labels fixed by this projector. No modular
rank, floating point, or numerical tolerance is used.

For two orthogonal projectors P and Q, the test `PQ=P` proves nesting. Taking
transposes gives `QP=P`, so

`(Q-P)² = Q-P`, and `rank(Q-P) = tr(Q)-tr(P)`.

An idempotent over Q has eigenvalues zero or one, which justifies the last
equality. Every chronological MOVE must pass this matrix identity and have
positive rank. Reverse replay uses `I-P` and reverses the record order;
`(I-P)-(I-Q)=Q-P` preserves the charge. COPY and ERASE swap roles in reverse.
All ADDs separately require matching current frame IDs, and COPY lifetimes
require an unchanged center and clean temporary restoration.

The source and target boundary spans contribute `2v(8-1)` to the telescoping
MOVE rank mass; helpers contribute `8R`. Adding the nine COPY charges gives
`2*111*7 + 8*439 + 63 = 5129`. This identity is a cross-check, not a substitute
for reconstructing the individual ranks.

One control changes the first A gate's frame from the first source line to
the second source line. It leaves the scalar program and the **entire
dimension-only histogram** unchanged. The projector test rejects the first
non-nested transition. This delimits a weakened dimension-only check; the
retained supplier checkers are not alleged to accept this mutation.

## Independent global decomposition

The pinned `global_k.py` recipe, its `adapt9p.py` parameterization, and the
replica configuration specify the nine local calls per replica. The independent
transcription aligns pair levels before each bridge and derives the ordered
idle capacities

`14, 7, 28, 7, 42, 7, 42, 28, 14, 0`.

For each idle child, a backward scan stops at the last local/bridge touch of
its pair and records the permissible intervening stages. This is a separate
implementation of the pinned `hosting_core.py` window definition. Each positive
capacity has `2v=222` family copies. The frozen selection is checked for family
coverage, allowed stages, pattern capacity, width-eight helper inventory, and
agreement between pattern counts and stage allocations. It assigns all 439
helpers in each of the nine stages.

The pending capacity is 41,958 per replica; 3,951 hosted width-eight helpers
consume 31,608. The remaining mass is 10,350. Consequently,

`288*5129 + 32*10350 = 1808352`,

and the deficit also equals `32*(2*4*111 - 9*63)=10272`.
Only **after** reconstruction are the published local/global histograms read
as expected values. The selected assembly's immutable input digest, PR589
identity and COPY deficit bind this comparison to its retained bit source.
The global result is a fixed-selection accounting audit: it does not construct
or replay the physical owners.

## Reproduce and controls

Python 3.12, standard library, no network or dependency installation:

```sh
python3 -I -B research/bit589-projector-ledger/verify.py
python3 -I -B research/bit589-projector-ledger/test_verify.py
python3 -B scripts/research_package.py --package research/bit589-projector-ledger --check-only
python3 -B scripts/research_package.py --package research/bit589-projector-ledger
```

Expected audit output:

```text
PASS_BIT589_PROJECTOR_LEDGER local_mass=5129 global_mass=1808352 deficit=10272 controls=16
```

The seven tests cover six explicit exact-projector fixtures and a differential
check of both full literal record exports and all exported basis/annihilator
operators. The latter invokes the pinned predecessor exporter only as a
secondary compatibility check; `verify.py` does not import or execute it.
Temporary differential outputs are removed on test completion.

The 16 controls reject non-nesting with equal dimensions, the same-histogram
gate mutation, wrong MOVE/COPY/ERASE charges, omitted dirty restoration or
compensation, wrong scatter frames, missing temporary erasure, idle overfill,
missing families/helpers, an illegal stage window, wrong replica multiplicity,
a rank-mass-preserving histogram change, and a corrupt source pin. Exact
rejection reasons are checked. The verifier uses explicit exceptions, so its
checks remain active with `python3 -O`.

## Sources, scope and overlap

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
Retained PR589: `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.
Selected PR1094: `0fc329d0bec93ca7cd288eaea1295172e8789810`.
Exact SHA256 and Git-blob pins are in [SOURCES.json](SOURCES.json). Catalogue
and selected-record pins are historical provenance; implementation inputs are
checked against their working bytes. The source-aware package runner needs
the base commit in Git history. Frozen sources are unchanged.

The chooser's `independent-moment` card is refined to this source ledger, as
recorded in [TASK.json](TASK.json). Coordination is in discussion #1166.
No pending implementation is imported. Nearby work is explicitly credited:

- PR1262 independently reconstructs the **complex** emitted ledger.
- PR1293 audits published supplier histograms, endpoint arithmetic and D/E.
  PR1405 separately audits that pending package's logarithm enclosure; no
  numerical engine or conclusion from either package is used here.
- PR1329 supplies the retained-bit identity guard. Here identity checks only
  bind the distinct chronological ledger calculation.
- This account's PR1307 checks cross-child physical pending projectors. The
  present selection recount is corroboration, not another physical audit.
- Cinna Davis's PR1351/1371 check one physical family's address operators,
  using complete matrix replay and projector algebra respectively. Here the
  projectors describe local eight-dimensional label frames and their complete
  chronological rank invoice, not that physical family map.
- PR1344 checks the scalar matrix of a particular frame-509 replacement;
  PR1345 prices a transport census from per-register frame paths. Those local
  arithmetic/path checks are predecessors, not new findings claimed here.
- The incorporated `bit589-width-packing` package already proves the no-bank
  packing optimum. This package makes no new packing-ceiling claim.

Unchecked obligations: complete selected cold replay; native cohort checkers;
the generator's recovery of these frozen compact words; full E8 lattice
classification; every H1–H5 implication; physical owner/chart realization and
global emitted-program equivalence; finite precision; all-size compilation;
moment/surcharge/outer analytic transfer; Lean or a complete multiplication
theorem. The schedule rules are a pinned, reviewed-source transcription,
not a proof of the Python compiler for all parameters. Source hashes establish
identity, not mathematical correctness of these inherited obligations.

## Open next questions

The structured questions are in [TASK.json](TASK.json).

1. Connect this independently derived invoice to each call and remainder of a
   source-bound emitted physical program. First pin a complete PR589 replay
   capsule and compare its call expansion against this receipt, using PR1307's
   separate pending-axis audit. The blocker is the capsule and the full
   physical realization contract; matching accounting alone cannot discharge it.
2. Apply this check to one distinct changed bit word before pricing its saving.
   This can separate scalar ADD reductions from changes to paid children. A
   candidate still needs its own H1–H5 or replacement-interface proof, hosting
   and precision evidence; none is supplied by this audit.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Assistance covered research, implementation, proof explanation, checks and
writing; no independent human review is claimed. New material is Apache-2.0.

DreamingOfClouds: PR589 tuning and PR545/510/463 geometry and templates.
eumemic: PR555/543/493 scalar words and interface lineage. DaysSky: PR442
hosting. Dylan Crow: record format/exporter. Zhihao Chen, chafreaky, Jacob
Sussman, Dugongue, Rohan Arun and the retained source authors: preceding
geometry, circuits and transports. Sagar Thakrar: nearby ledger/packing audits;
Navinor: PR1293. Cinna Davis: the nearby local-matrix and physical-family audits.
Original source notices and licenses remain untouched.
