# Independent review: one source-restored physical raw dual

**PASS, with no unresolved correctness finding in the reviewed new repair.**
The frozen candidate is A's `RAWDUAL-WORD.json.gz`, SHA256
`b82a423cf4a44669d44b168dab3459e9bdb646cefd96c4e4d5f401c567eec6a2`.
Reviewed checker `8ec1616bc7336f7999e0139ef0fa1c390a61f52db40c5f87bbc325a3febd0065`,
RESULT `2fced35c17ecad163657d9ed2f05aeb3bf0ef158b06b6c9e33dbff2200fd2751`,
SOURCES `fe5ab0fc5bb76b4c88cf94df7efc1bb10c19fc8bcabe5116354f2186c014ff61`.
The checker is retained for inspection, not imported or executed by the
independent scientific replay. `CANDIDATE-HASHES.json` fixes the full bytes.

The independent derivation preceded reading A's implementation. Exact R/K/P
identities, backward sign/transpose, physical conjugation and scratch lifecycle
are recorded in DERIVATION.md/DERIVATION.json. The actual coefficient census
is 8×−12,268×−6,148×+6; the incorrect preliminary 208/208 summary was caught
independently by both agents before any erroneous receipt was frozen.

`replay_independent.py` is a separately written chronological event interpreter,
with no import from A or upstream native_core. `audit.py` confirms:

- Literal byte-structure equality of the 4929 backward prefix and every
  canonical boundary field; all 456 suffix events match the independently
  reconstructed coefficient/owner/chart sequence.
- All 632 rows of the inherited 4935 forward word, all 632 rows of the 4929
  coded backward word, and all 632 rows of the new backward word match their
  respective source-restored/raw-dual targets on arbitrary original inputs.
- All 112 original Y owners and 408 independent helper owners remain their
  prescribed pure returned jobs; only already owned C0 is copied/cleared.
  No source-mutating UNIT-TRANSFER variant or extra storage owner is used.
- All original output charts and owned-zero completion are preserved. The
  complete paid bill is {1:2209,2:412,3:510,4:127,5:40}. Backward prefix l1
  remains258, forward457; those state bounds are not rounding suffix bounds.
- Every 512 basis columns of all 8 FROZEN native lift circuits satisfy
  bar(V_j) followed by the lift =bar(F9), including global phase. These
 4,096 comparisons use a separately written sparse Gaussian-integer gate
  interpreter, not ce.zero_state or equality of compiler tableaus.
- Seven semantic controls reject a scatter-sign corruption, omitted lifts,
  absent repairs, a borrowed-owner COPY, a borrowed-owner CLEAR, missing
  transpose and a global-phase-only circuit corruption. Derivation controls
  additionally reject unconjugated and reversed-adjoint physical lifts.

Normal and optimized derivation/audit/ceiling checks pass locally on
CPython 3.12.3 using only the standard library. Source files are authenticated
before use. There is no remote mutation or caller search in this review.

The full inherited native physical warp/phase semantics remain the pinned
source contract. The independently implemented all 632 replay checks its
normalized chronological free-word identities and actual typed chart events;
it does not replace a fresh physical amplitude audit of every old source
warp. All NEW lift phases are directly checked as above. Single-word
absolute-phase equalities tensor-lift to every positive column width; scalar
owner coefficients stay outside tensor powers. The result is a physical
source-restored raw dual under those explicitly inherited source premises.
It is not obtained by formally transposing COPY/CLEAR instructions.

The finite invoice separately retains 424 weighted scatters, conservative
2,976 elementary scalar primitives,8COPY+16CLEAR and emitted monomial passes.
These are ordinary work, not extra Gaussian targets or zero-cost storage.
The bound 13^8*7^416 controls amplification from repair-suffix ADD macros in
the maximum fiber-Euclidean field norm; a future caller still needs the
inherited suffix/error bounds, actual scalar lowering and precision reserve.
No uniform compiler, outer admission or κ is funded by the local endpoint.

CEILING.md/CEILING.json separately verify the parent's requested standalone
one-bank corollary. Actual diag(F)=12D_J and F_JJ=12I; an exact two-sided
inverse witness proves G=F−12D_J invertible without assuming symmetry.
All 5,824 supported offdiagonal grades are recomputed directly. The scoped
112H2 bound and complete unrealized price relaxation lose across the stated
C interval. This does not invalidate the new repair and excludes direct coded
consumers, chronological native absorption and multibank architectures.

Reproduction from this directory:

```sh
python3 -I -W error -B derive.py
python3 -I -W error -B audit.py
python3 -I -W error -B check_ceiling.py
```

Repeat with `-O`. The scripts read the local authenticated snapshots; they do
not invoke Git or import the candidate checker. This output folder is an
independent review artifact, not a registered research package or hosted CI.
No independent human or formal proof-kernel acceptance is claimed.

Credit Dugongue #4935/#4929, Rohan Arun #1931, Ali Romman #1862,
Cinna Davis/1337isnot1337 #4694/#4698/#4470, Cao Yifan/intqwq's actual native
round-three source beyond #4610, zxv, Jacob Alan Sussman and all retained
contributors. Parent proposed the physical COPY/lift/scatter route and the
one-bank rank argument; A emitted it; this agent independently derived and
reviewed the new operator, coefficient invoice, chronology and phases.
Prepared for Chris R/Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0; source-specific notices remain authoritative.
