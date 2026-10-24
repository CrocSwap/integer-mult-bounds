# 25-paper coupled-output construction sweep

This package translates techniques from **25 primary papers into 25 executable
interface probes**, compares their combinations against the actual integer
multiplication caller, and supplies a concrete coupled boundary program.
The strongest next candidate is a history-augmented coupled transducer with an
endogenous paid observer. Its missing observation/termination bridge is stated
precisely; **no improved κ is established**.

Read [SYNTHESIS.md](SYNTHESIS.md) for the construction and next experiments,
[LITERATURE.md](LITERATURE.md) for every paper-to-code mapping, and
[PAPERS.json](PAPERS.json) for primary citations, reading locators and access
limitations. Twenty entries have accessible primary method material; five are
record/abstract-only and are labelled. These are scoped adaptations, not full
implementations of the papers or an exhaustive literature review.

## Concrete results

- A literal in-place 120-field involution H(-4,3) with 1,344 ADDs, 16 SCALEs,
  240 signed monomial maps and no new scratch. All independent input columns
  are checked. Its mode-block squared Frobenius norm is 688 versus 898 at the
  prior PR4935 gauge. The completion and three-shear method are inherited.
  A separate row-sum metric improves 69 to 50 at (-12,1), so gauge selection
  remains tied to the compiler's actual precision model. Its separately emitted
  dual program uses 1,344 ADDs, eight sign SCALEs and 240 monomial maps, with
  no odd division or new scratch.
- A catalytic main-only ADD between **different** declared coupled frames:
  `dst += H_t P H_s src`, preserving all 120 source originals. Its all-column
  free-operator-word check retains distinct chart maps. The bill is 3,712 ADDs,
  16 SCALEs and 960 monomial maps, with no new scratch or Gaussian call.
  The identical-chart specialization uses 2,360 ADDs and 480 monomial maps.
  A cross-chart thin-query wrapper also preserves all 240 originals, keeping
  its 112 paid H1 queries and explicitly paying 112 owned fields, 112 COPY,
  224 CLEAR and 112 inverse-child translations. Placement of these types
  in the full native shared-helper block remains open.
- All 112 observer columns lie in distinct right monomial cosets. All 6,216
  pair comparisons check the orientation distinction. This rejects one shared
  Gaussian after monomial aggregation in the stated architecture.
- Actual two-generation physical displacement action, with residual rank eight,
  Gram entry 2,422 and exact signed phases. This extends the previous transport
  witness into a generator-state representation; it is not a whole-field cost
  lower bound.
- An exact source-relative 0.004 moment cap against the newly selected
  PR5413 profile: the **combined new observer and extra termination** must cost
  below 50.063024… H1-equivalents per backward call, across eighteen calls.
  The frozen earlier sixteen-call comparison is retained separately. Buying 112 fresh observations
  fails; unknown bridges receive no exponent credit. Other numerical regime
  screens and precision sensitivity are recorded separately.
- Executable catalytic, interpolation, reversible-pebbling, I/O, low-rank
  inverse, nilpotent-degeneration, precision and Clifford-synthesis tests on
  pinned fixtures, with explicit controls and transfer limits.

## Reproduce

CPython 3.12+, standard library only; no network, Git executable, downloaded
paper, Lean or Docker is needed by the direct verifier.

```sh
python3 -B research/literature-coupled-synthesis/verify.py
python3 -O -B research/literature-coupled-synthesis/verify.py
```

The registered source/provenance check additionally uses Git:

```sh
python3 -B scripts/research_package.py --package research/literature-coupled-synthesis
```

The complete ADD/thin-query junction streams can also be emitted explicitly:

```sh
python3 -B research/literature-coupled-synthesis/junction.py --emit /tmp/coupled-add-junctions.json
```

The emitter refuses to overwrite an existing file. Normal verification executes
all three programs in memory and records their exact instruction hashes and bills.

`verify.py --write` deliberately regenerates `RESULT.json` and
`BALANCED-PROGRAM.json` and `ROWSUM-PROGRAM.json`; normal verification is read-only and compares every
regenerated result. `BALANCED-PROGRAM.json` specifies the physical K-frame
boundary map counts and contains the scalar program. The actual K words are
pinned in the normalizer/provider inputs.

The direct replay checks local input hashes but does not authenticate remote
Git history. `SOURCES.json` pins package-local archive bytes to a publication
ancestor; `ORIGINS.json` records exact original commits, paths, blob IDs and
byte comparisons at creation. The generic registered runner checks those
archive pins. An optional full-history ancestry audit was not run.

## Evidence and limits

See [VALIDATION.md](VALIDATION.md) for commands, environment, access/overlap
coverage and unrun obligations. Exact matrix/word checks establish only their
stated scopes. Finite physical witnesses disprove the corresponding universal
ansatz; finite positive probes alone do not establish a complete theorem.
Main now selects conditional κ=0.003027288235 (promotion `1a3ced60b`). Its
declared full price profile is independently reconstructed here; its full
admission replay is inherited, not rerun. The native endpoint and physical normalizer relations are
pinned premises. The full native implementation, full recursion precision,
ordinary BIT compiler and outer supplier admission are not replayed here.
Nothing changes `certificates/selected-result.json`.

## Open next questions

1. Can the first real backward junction supply current-version ZQY from an
   actual paid native contact while retaining or explicitly displacing its
   demanded thin Q^-1 X observation? First step: emit and check the chronological
   source/return rows. Blocker: no source-compatible joint supplier yet.
2. Can generation-tagged displacement state terminate after the second real
   contact, rather than grow indefinitely? First step: extend the exact
   two-generation input-column replay to its proposed history return. Blocker:
   an affordable restoration circuit with all originals intact.
3. Can the verified H_t P H_s and thin-query junctions be installed inside the
   full X/Y/eight-mode coupled contract? First step: place the 120-field seed
   inside the actual 232-field block, prove disjoint mode ownership, and bind
   the native FULL input/return types.
   Blocker: matching input/output type and physical volume/precision proof.
4. Does the closed bill admit a first 0.0033 milestone, then 0.004 with an
   improved ordinary compiler? First step: replace every unknown cost with an
   executable bound and rerun the shared allowance, then independent admission.
   Blocker: the previous three interfaces and full precision/tape accounting.

Prepared by zxv with substantial OpenAI Codex assistance for Dillon Amburgey.
No subagents were used for this sweep. Apache-2.0. Retain all predecessor and
paper credit in [ATTRIBUTION.md](ATTRIBUTION.md) and the frozen notices.
